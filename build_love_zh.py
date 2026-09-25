#!/usr/bin/env python3
"""Translate love/career fields to 繁中 for all 78 cards via GLM (resume-safe)."""
import json, os, subprocess, time, sys

GLM_KEY = os.environ.get("GLM_API_KEY")
BASE = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

en = json.load(open("/home/ubuntu/tarot-site/data/en.json"))
OUT = "/home/ubuntu/tarot-site/data/zh_love_partial.json"

def call_llm(chunk):
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content":
             "你是專業塔羅牌譯者。把英文塔羅牌愛情/事業解讀翻譯成繁體中文（香港慣用語），保持塔羅專業用語。只輸出 JSON，不要任何其他文字。格式：JSON 陣列，每個元素 {\"id\":數字,\"love_zh\":一句15-25字,\"love_rev_zh\":一句15-25字,\"career_zh\":一句15-25字,\"career_rev_zh\":一句15-25字}。id 與輸入一致，一個不漏。"},
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
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            out = json.loads(content)
            return out if isinstance(out, list) else out.get("cards", [])
        except Exception:
            err = (r.stdout[:150] if 'r' in dir() and r.stdout else "no response")
            print(f"  attempt {attempt+1} failed: {err}")
            time.sleep(4)
    return None

def payload(c):
    return {"id": c["id"], "name": c["name_en"],
            "love_en": c["love_en"], "love_rev_en": c["love_rev_en"],
            "career_en": c["career_en"], "career_rev_en": c["career_rev_en"]}

zh = {}
if os.path.exists(OUT):
    zh = {int(k): v for k, v in json.load(open(OUT)).items()}

chunks = [en[0:20], en[20:40], en[40:60], en[60:78]]
for i, ch in enumerate(chunks):
    todo = [c for c in ch if c["id"] not in zh]
    if not todo:
        print(f"chunk {i+1}/4 done"); continue
    print(f"chunk {i+1}/4 ({len(todo)} cards)...")
    res = call_llm([payload(c) for c in todo])
    if res is None:
        print("FATAL"); sys.exit(1)
    got = {r["id"]: r for r in res}
    for mid in [c["id"] for c in todo if c["id"] not in got]:
        c = next(x for x in todo if x["id"] == mid)
        r2 = call_llm([payload(c)])
        if r2: got[mid] = r2[0]
    zh.update(got)
    json.dump({str(k): v for k, v in zh.items()}, open(OUT, "w"), ensure_ascii=False)

print("translated love/career:", len(zh))
json.dump({str(k): v for k, v in zh.items()}, open(OUT, "w"), ensure_ascii=False)
print("sample id0:", json.dumps(zh.get(0), ensure_ascii=False))
