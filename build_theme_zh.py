#!/usr/bin/env python3
"""Bulk pre-generate theme readings (health/wealth/study/family) for all 78 cards × upright/reversed, zh+en."""
import json, os, subprocess, time, sys

GLM_KEY = os.environ.get("GLM_API_KEY")
BASE = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

en = json.load(open("/home/ubuntu/tarot-site/data/en.json"))
THEMES = ["health", "wealth", "study", "family"]
THEME_ZH = {"health": "健康", "wealth": "財富", "study": "學業", "family": "家庭"}
OUT = "/home/ubuntu/tarot-site/data/zh_theme_partial.json"

def call_llm(theme, chunk):
    tzh = THEME_ZH[theme]
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content":
             "你是資深塔羅師兼專業譯者。每張牌用 40-70 字繁體中文（香港慣用語）寫一句主題解讀，另用 40-70 字英文寫一句。要具體、有畫面、可實踐，唔好空泛。只輸出 JSON 陣列，每個元素 {\"id\":數字,\"zh\":\"正位解讀\",\"rev_zh\":\"逆位解讀\",\"en\":\"upright reading\",\"rev_en\":\"reversed reading\"}。id 與輸入一致，一個不漏。"},
            {"role": "user", "content":
             f"主題：{tzh}（{theme}）。為以下每張塔羅牌寫該主題下的正位同逆位解讀（正位係主題能量正面顯現，逆位係受阻/反轉/提醒）。輸入：\n"
             + json.dumps([{"id": c["id"], "name": c["name_en"], "mean": c["mean_en"], "mean_rev": c["mean_rev_en"], "love": c["love_en"], "career": c["career_en"]} for c in chunk], ensure_ascii=False)}
        ],
        "temperature": 0.7,
        "max_tokens": 6000
    }
    for attempt in range(4):
        try:
            r = subprocess.run(["curl", "-s", "-m", "240", "-X", "POST", BASE,
                                "-H", f"Authorization: Bearer {GLM_KEY}",
                                "-H", "Content-Type: application/json",
                                "-d", json.dumps(body)],
                               capture_output=True, text=True)
            data = json.loads(r.stdout)
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            out = json.loads(content)
            if isinstance(out, dict) and "cards" in out:
                out = out["cards"]
            return out
        except Exception:
            err = (r.stdout[:160] if 'r' in dir() and r.stdout else "no response")
            print(f"  attempt {attempt+1} failed: {err}")
            time.sleep(5)
    return None

store = {}
if os.path.exists(OUT):
    store = {tuple(k.split(":")): v for k, v in json.load(open(OUT)).items()}

for theme in THEMES:
    for si in range(6):
        ch = en[si*13:(si+1)*13] or en[65:78]
        todo = [c for c in ch if (theme, str(c["id"])) not in store]
        if not todo:
            print(f"{theme} chunk {si+1}/6 done"); continue
        print(f"{theme} chunk {si+1}/6 ({len(todo)} cards)...")
        res = call_llm(theme, todo)
        if res is None:
            print("FATAL"); sys.exit(1)
        got = {str(r["id"]): r for r in res}
        for c in todo:
            if str(c["id"]) not in got:
                r2 = call_llm(theme, [c])
                if r2: got[str(c["id"])] = r2[0]
        for cid, r in got.items():
            store[(theme, cid)] = r
        json.dump({":".join(k): v for k, v in store.items()}, open(OUT, "w"), ensure_ascii=False)
        print(f"  stored {len(store)}")

json.dump({":".join(k): v for k, v in store.items()}, open(OUT, "w"), ensure_ascii=False)
print("TOTAL:", len(store), "expected:", 4*78)
print("sample health Fool:", json.dumps(store.get(("health","0")), ensure_ascii=False))