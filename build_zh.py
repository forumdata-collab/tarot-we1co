#!/usr/bin/env python3
"""Build 繁中 tarot dataset: hardcoded card names + GLM translation of keywords/meanings."""
import json, os, subprocess, time, sys

GLM_KEY = os.environ.get("GLM_API_KEY")
BASE = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

en = json.load(open("/home/ubuntu/tarot-site/data/en.json"))

MAJOR_ZH = ["愚者","魔術師","女祭司","皇后","皇帝","教皇","戀人","戰車","力量","隱士",
            "命運之輪","正義","倒吊人","死神","節制","惡魔","高塔","星星","月亮","太陽","審判","世界"]
SUIT_ZH = {"wands":"權杖","cups":"聖杯","swords":"寶劍","pentacles":"錢幣"}
COURT_ZH = {11:"侍從",12:"騎士",13:"王后",14:"國王"}
NUM_ZH = {1:"王牌",2:"二",3:"三",4:"四",5:"五",6:"六",7:"七",8:"八",9:"九",10:"十"}

def zh_name(c):
    if c["suit"] is None:
        return MAJOR_ZH[c["num"]]
    s = SUIT_ZH[c["suit"]]
    return f"{s}{COURT_ZH[c['num']]}" if c["num"] >= 11 else f"{s}{NUM_ZH[c['num']]}"

names = {c["id"]: zh_name(c) for c in en}
json.dump(names, open("/home/ubuntu/tarot-site/data/name_zh.json", "w"), ensure_ascii=False, indent=1)
print("names:", len(names))

def call_llm(chunk):
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content":
             "你是專業塔羅牌譯者。把英文塔羅牌資料翻譯成繁體中文（台灣／香港慣用語），保持塔羅專業用語。只輸出 JSON，不要任何其他文字。格式：JSON 陣列，每個元素 {\"id\":數字,\"kw_zh\":[4-5個詞],\"kw_rev_zh\":[4-5個詞],\"mean_zh\":一句20-35字,\"mean_rev_zh\":一句20-35字}。id 與輸入一致，一個不漏。"},
            {"role": "user", "content": "翻譯以下塔羅牌資料：\n" + json.dumps(chunk, ensure_ascii=False)}
        ],
        "temperature": 0.3,
        "max_tokens": 5000
    }
    for attempt in range(4):
        try:
            r = subprocess.run(["curl", "-s", "-m", "180", "-X", "POST", BASE,
                                "-H", f"Authorization: Bearer {GLM_KEY}",
                                "-H", "Content-Type: application/json",
                                "-d", json.dumps(body)],
                               capture_output=True, text=True)
            data = json.loads(r.stdout)
            content = data["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            out = json.loads(content)
            if isinstance(out, dict) and "cards" in out:
                out = out["cards"]
            return out
        except Exception:
            err = (r.stdout[:200] if 'r' in dir() and r.stdout else "no response")
            print(f"  attempt {attempt+1} failed: {err}")
            time.sleep(4)
    return None

def payload(c):
    return {"id": c["id"], "name": c["name_en"],
            "kw_en": c["kw_en"], "kw_rev_en": c["kw_rev_en"],
            "mean_en": c["mean_en"], "mean_rev_en": c["mean_rev_en"]}

chunks = [en[0:20], en[20:40], en[40:60], en[60:78]]
zh_by_id = {}
if os.path.exists("/home/ubuntu/tarot-site/data/zh_partial.json"):
    zh_by_id = {int(k): v for k, v in json.load(open("/home/ubuntu/tarot-site/data/zh_partial.json")).items()}
for i, ch in enumerate(chunks):
    done_ids = {str(x) for x in zh_by_id.keys()}
    todo = [c for c in ch if str(c["id"]) not in done_ids]
    if not todo:
        print(f"chunk {i+1}/4 already done"); continue
    print(f"chunk {i+1}/4 ({len(todo)} cards)...")
    res = call_llm([payload(c) for c in todo])
    if res is None:
        print("FATAL chunk failed"); sys.exit(1)
    got = {r["id"]: r for r in res}
    missing = [c["id"] for c in todo if c["id"] not in got]
    print(f"  got {len(got)}, missing {missing}")
    for mid in missing:
        c = next(x for x in todo if x["id"] == mid)
        r2 = call_llm([payload(c)])
        if r2:
            got[mid] = r2[0]
    zh_by_id.update(got)
    json.dump(zh_by_id, open("/home/ubuntu/tarot-site/data/zh_partial.json","w"), ensure_ascii=False)

print("translated:", len(zh_by_id))

# Curated 繁中 for the 22 Major Arcana (hand-written, overrides GLM output)
majors = json.load(open("/home/ubuntu/tarot-site/data/majors_zh.json"))
for k, v in majors.items():
    zh_by_id[int(k)] = v          # keys "0".."21" -> int id

final = []
for c in en:
    z = zh_by_id.get(c["id"])
    final.append({**c, "name_zh": names[c["id"]],
        **({k: z[k] for k in ("kw_zh","kw_rev_zh","mean_zh","mean_rev_zh")} if z else {})})
json.dump(final, open("/home/ubuntu/tarot-site/data/deck.json","w"), ensure_ascii=False, indent=1)
print("deck.json bytes:", os.path.getsize("/home/ubuntu/tarot-site/data/deck.json"))
print("sample:", json.dumps(final[0], ensure_ascii=False)[:300])
