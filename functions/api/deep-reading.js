// AI deep reading: POST /api/deep-reading -> GLM narrative from the user's spread
// Reads GLM_API_KEY from Pages secret. Returns {text} or {error} with 4xx/5xx.
export async function onRequestPost({ request, env }) {
  const key = env.GLM_API_KEY;
  if (!key) {
    return json({ error: "AI not configured" }, 503);
  }
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "bad json" }, 400);
  }
  const { lang, question, cards } = body;
  if (!Array.isArray(cards) || cards.length < 1 || cards.length > 10) {
    return json({ error: "invalid cards" }, 400);
  }
  const zh = lang !== "en";
  const list = cards
    .map((c, i) =>
      zh
        ? `${i + 1}. 位置「${c.pos}」：${c.name}（${c.rev ? "逆位" : "正位"}）。關鍵詞：${(c.kw || []).join("、")}。一般解讀：${c.mean || ""}；愛情：${c.love || ""}；事業：${c.career || ""}`
        : `${i + 1}. Position "${c.pos}": ${c.name} (${c.rev ? "reversed" : "upright"}). Keywords: ${(c.kw || []).join(", ")}. Meaning: ${c.mean || ""}; Love: ${c.love || ""}; Career: ${c.career || ""}`
    )
    .join("\n");

  const system = zh
    ? "你是資深而溫暖的塔羅師，擅長把牌陣串成連貫、具體、可行動的解讀。用繁體中文（香港慣用語）作答，只輸出解讀文字，不要任何前言或標題。"
    : "You are an experienced, warm tarot reader who weaves spreads into coherent, specific, actionable readings. Answer in fluent English prose only — no preamble, no headings.";
  const user = zh
    ? `求問者問題：${question || "（未提出具體問題）"}\n牌陣位置與牌面：\n${list}\n\n請按以下結構寫一段 250-400 字（繁體中文）的深度解讀：1) 整副牌的整體盤勢與核心情緒；2) 逐張牌結合位置與正逆位的意義；3) 最後給出 2-3 個具體、溫柔的行動建議。`
    : `Question: ${question || "(no specific question asked)"}\nSpread:\n${list}\n\nWrite a 220-350 word deep reading: 1) the overall arc and core emotion of the spread; 2) each card in its position, including upright/reversed meaning; 3) end with 2-3 specific, gentle action steps.`;

  const res = await fetch("https://open.bigmodel.cn/api/paas/v4/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
    body: JSON.stringify({
      model: "glm-4-flash",
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
      temperature: 0.8,
      max_tokens: 2200,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    return json({ error: "upstream " + res.status + ": " + text.slice(0, 160) }, 502);
  }
  const data = await res.json();
  const text = data?.choices?.[0]?.message?.content;
  if (!text) return json({ error: "empty upstream reply" }, 502);
  return json({ text });
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}