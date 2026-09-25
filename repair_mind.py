#!/usr/bin/env python3
"""Repair missing mind_rev_en fields in deck.json + source partial (inferai deepseek-v4-pro)."""
import json, os, subprocess, time, sys

API = os.environ.get("INFERAI_API_KEY")
if not API:
    sys.exit("INFERAI_API_KEY not set — source ~/.hermes/.env first")

DECK = "/home/ubuntu/tarot-site/deck.json"
PART = "/home/ubuntu/tarot-site/data/zh_theme_mind.json"
d = json.load(open(DECK))
part = json.load(open(PART))
missing = [c for c in d if not (c.get("mind_rev_en") or "").strip()]
if not missing:
    print("nothing to repair"); sys.exit(0)
ids = {str(c["id"]) for c in missing}
print("repairing", len(missing), "cards:", sorted(ids))

payload = [{"id": c["id"], "name": c["name_en"], "reversed_meaning": c["mean_rev_en"]} for c in missing]
body = {
    "model": "deepseek-v4-pro",
    "messages": [
        {"role": "system", "content":
         "You are an experienced tarot reader. For each tarot card given, write ONLY the reversed-card reading for the theme 心情／心靈 (mind, mood and inner state) — in English, 40-70 words, specific and practical, no padding. Output ONLY a JSON array [{\"id\":number,\"rev_en\":\"...\"}]. No preamble, no markdown, no code fences."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ],
    "temperature": 0.7,
    "max_tokens": 4000,
}

got = {}
for attempt in range(4):
    r = subprocess.run(["curl", "-s", "-m", "300", "-X", "POST",
                        "https://inferaiapi.com/v1/chat/completions",
                        "-H", f"Authorization: Bearer {API}",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps(body)], capture_output=True, text=True)
    try:
        content = json.loads(r.stdout)["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        got = {str(x["id"]): x for x in json.loads(content) if str(x["id"]) in ids and x.get("rev_en")}
        print(f"attempt {attempt+1}: got {len(got)}/{len(ids)}")
        if len(got) >= len(ids):
            break
    except Exception as e:
        print(f"attempt {attempt+1} failed: {str(e)[:120]}")
        print("  raw:", r.stdout[:200])
        time.sleep(4)

fixed = 0
for c in d:
    k = str(c["id"])
    if not (c.get("mind_rev_en") or "").strip() and got.get(k, {}).get("rev_en"):
        c["mind_rev_en"] = got[k]["rev_en"]
        if k in part:
            part[k]["rev_en"] = got[k]["rev_en"]
        fixed += 1
json.dump(d, open(DECK, "w"), ensure_ascii=False, indent=1)
json.dump(part, open(PART, "w"), ensure_ascii=False)
still = [c["id"] for c in d if not (c.get("mind_rev_en") or "").strip()]
print("fixed:", fixed, "| still missing:", still)
if fixed:
    print("sample id6:", [c for c in d if c["id"] == 6][0]["mind_rev_en"][:140])