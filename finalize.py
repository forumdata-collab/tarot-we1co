#!/usr/bin/env python3
"""Finalize enriched deck.json: element + love/career zh (majors curated override minors GLM), s2t cleanup."""
import json, os, opencc

en = json.load(open("/home/ubuntu/tarot-site/data/en.json"))
names = {int(k): v for k, v in json.load(open("/home/ubuntu/tarot-site/data/name_zh.json")).items()}

base = {int(k): v for k, v in json.load(open("/home/ubuntu/tarot-site/data/zh_partial.json")).items()}
base.update({int(k): v for k, v in json.load(open("/home/ubuntu/tarot-site/data/majors_zh.json")).items()})

love = {}
if os.path.exists("/home/ubuntu/tarot-site/data/zh_love_partial.json"):
    love = {int(k): v for k, v in json.load(open("/home/ubuntu/tarot-site/data/zh_love_partial.json")).items()}
love.update({int(k): v for k, v in json.load(open("/home/ubuntu/tarot-site/data/majors_love_zh.json")).items()})

ELEMENT_ZH = {"Fire": "火", "Water": "水", "Air": "風", "Earth": "土"}

final, missing = [], []
for c in en:
    b = base.get(c["id"]) or {}
    lv = love.get(c["id"]) or {}
    if not b.get("kw_zh"): missing.append((c["id"], "kw"))
    if not lv.get("love_zh"): missing.append((c["id"], "love"))
    final.append({**c, "name_zh": names[c["id"]],
        "element_zh": ELEMENT_ZH.get(c["element"], c["element"]),
        "kw_zh": b.get("kw_zh"), "kw_rev_zh": b.get("kw_rev_zh"),
        "mean_zh": b.get("mean_zh"), "mean_rev_zh": b.get("mean_rev_zh"),
        "love_zh": lv.get("love_zh"), "love_rev_zh": lv.get("love_rev_zh"),
        "career_zh": lv.get("career_zh"), "career_rev_zh": lv.get("career_rev_zh")})
print("missing:", missing if missing else "NONE")

cc = opencc.OpenCC('s2t')
for c in final:
    for k in ("name_zh","kw_zh","kw_rev_zh","mean_zh","mean_rev_zh","love_zh","love_rev_zh","career_zh","career_rev_zh"):
        v = c.get(k)
        if isinstance(v, list): c[k] = [cc.convert(x) for x in v]
        elif isinstance(v, str): c[k] = cc.convert(v)

json.dump(final, open("/home/ubuntu/tarot-site/data/deck.json", "w"), ensure_ascii=False, indent=1)
json.dump(final, open("/home/ubuntu/tarot-site/deck.json", "w"), ensure_ascii=False, indent=1)
print("deck.json:", len(final), "cards,", os.path.getsize("/home/ubuntu/tarot-site/deck.json"), "bytes")
print("id0 love:", final[0]["love_zh"], "| career:", final[0]["career_zh"])
print("id6 love:", final[6]["love_zh"])