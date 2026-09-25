#!/usr/bin/env python3
"""Pre-generate theme readings via inferai deepseek-v4-pro. Usage: build_theme_ds.py <theme>
Theme: health|wealth|study|family. Resume-safe per-theme partial file."""
import json, os, subprocess, sys, time

API = os.environ.get("INFERAI_API_KEY")
BASE = "https://inferaiapi.com/v1/chat/completions"
MODEL = "deepseek-v4-pro"
THEMES = {"health": "健康", "wealth": "財富", "study": "學業", "family": "家庭"}

theme = sys.argv[1]
tzh = THEMES[theme]
en = json.load(open("/home/ubuntu/tarot-site/data/en.json"))
OUT = f"/home/ubuntu/tarot-site/data/zh_theme_{theme}.json"

def call_llm(chunk):
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content":
             "你是資深塔羅師兼專業譯者。每張牌寫一句繁體中文（香港用語）主題解讀，另寫一句英文解讀。要具體、有畫面、可實踐。只輸出 JSON 陣列，每個元素 {\"id\":數字,\"zh\":\"正位解讀\",\"rev_zh\":\"逆位解讀\",\"en\":\"upright reading\",\"rev_en\":\"reversed reading\"}。id 與輸入一致，一個不漏。直接輸出 JSON，唔好加任何前言或 markdown。"},
            {"role": "user", "content":
             f"主題：{tzh}（{theme}）。為以下每張塔羅牌寫該主題下嘅正位同逆位解讀（正位＝主題能量正面顯現，逆位＝受阻／反轉／提醒）。輸入：\n"
             + json.dumps([{"id": c["id"], "name": c["name_en"], "mean": c["mean_en"], "mean_rev": c["mean_rev_en"], "love": c["love_en"], "career": c["career_en"]} for c in chunk], ensure_ascii=False)}
        ],
        "temperature": 0.7,
        "max_tokens": 6000
    }
    for attempt in range(5):
        try:
            r = subprocess.run(["curl", "-s", "-m", "300", "-X", "POST", BASE,
                                "-H", f"Authorization: Bearer {API}",
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
            print(f"  {MODEL} attempt {attempt+1} failed: {err}", flush=True)
            time.sleep(4)
    return None

store = {}
if os.path.exists(OUT):
    store = json.load(open(OUT))

for si in range(6):
    ch = en[si*13:(si+1)*13] or en[65:78]
    todo = [c for c in ch if str(c["id"]) not in store]
    if not todo:
        print(f"{theme} chunk {si+1}/6 done", flush=True); continue
    print(f"{theme} chunk {si+1}/6 ({len(todo)} cards)...", flush=True)
    res = call_llm(todo)
    if res is None:
        print("FATAL"); sys.exit(1)
    got = {str(r["id"]): r for r in res}
    for c in todo:
        if str(c["id"]) not in got:
            r2 = call_llm([c])
            if r2: got[str(c["id"])] = r2[0]
    store.update(got)
    json.dump(store, open(OUT, "w"), ensure_ascii=False)
    print(f"{theme}: stored {len(store)}/78", flush=True)

json.dump(store, open(OUT, "w"), ensure_ascii=False)
print(f"DONE {theme}: {len(store)} cards")
print("sample:", json.dumps(store.get("0"), ensure_ascii=False)[:220])