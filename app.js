/* 星語塔羅 Tarot of the Stars — app logic */
(function () {
"use strict";

const T = {
  zh: {
    "setup.title": "靜下心，在心中默想一個問題",
    "setup.hint": "問題越具體，牌面越有方向。不輸入問題也可以。",
    "setup.qPlaceholder": "你現在最想了解的是…？",
    "setup.spread": "選擇牌陣",
    "setup.reversed": "允許逆位（部分牌會倒轉）",
    "setup.start": "✦ 開始洗牌",
    "shuffle.title": "專注於你的問題，洗牌中…",
    "shuffle.stop": "停止洗牌",
    "shuffle.hint": "準備好就按「停止洗牌」，牌會自動抽出。",
    "draw.title": "請逐張翻開你的牌",
    "draw.reading": "查看完整解讀",
    "draw.again": "✦ 再占一次",
    "spread.1.name": "單張指引", "spread.1.desc": "每日一牌，聚焦當下",
    "spread.3.name": "三張牌陣", "spread.3.desc": "過去 · 現在 · 未來",
    "spread.5.name": "五張十字", "spread.5.desc": "現況 · 挑戰 · 根基 · 發展 · 建議",
    "pos.1": ["今日指引"],
    "pos.3": ["過去", "現在", "未來"],
    "pos.5": ["現況", "挑戰", "根基", "發展", "建議"],
    "posctx.1": ["指出你今天最值得留意的事"],
    "posctx.3": ["交代了推動現在的過往動力", "呈現你當下的真實狀態", "描繪可望走向的未來"],
    "posctx.5": ["描繪你當下的局勢", "指出你必須跨越的關卡", "揭示支撐局勢的底層力量", "預示事情可能的走向", "給出具體的行動方向"],
    "badge.up": "正位", "badge.rev": "逆位",
    "sec.mean": "牌義解讀",
    "sec.love": "💗 愛情",
    "sec.career": "💼 事業",
    "ov.title": "牌陣總覽",
    "ov.kw": "本次牌陣聚焦：",
    "ov.q": "你的問題：",
    "ov.nq": "（心中默想的問題）",
    "ov.narr": "整體而言，這副牌陣傳遞的核心訊息是：",
    "deep.btn": "✦ AI 深度解讀",
    "deep.hint": "由 AI 綜合整副牌陣撰寫更長的解讀（可選）",
    "deep.loading": "占卜師凝神解讀中…",
    "deep.fail": "AI 暫時未能回應，請稍後再試（詳細解讀仍在下方）。",
    "footer.credit": "牌面：Rider-Waite 塔羅牌（公有領域）· 解讀：參考 Tarotoo 開源資料集及《Pictorial Key to the Tarot》",
    "footer.disclaimer": "占卜結果僅供娛樂參考，不構成任何專業建議。",
  },
  en: {
    "setup.title": "Take a deep breath and hold your question in mind",
    "setup.hint": "A clear question gives clearer answers. You may also shuffle without one.",
    "setup.qPlaceholder": "What would you like to know right now…？",
    "setup.spread": "Choose a Spread",
    "setup.reversed": "Allow reversed cards (some cards will appear upside down)",
    "setup.start": "✦ Shuffle the Deck",
    "shuffle.title": "Focus on your question while shuffling…",
    "shuffle.stop": "Stop Shuffling",
    "shuffle.hint": "Tap stop when you feel ready — your cards are drawn automatically.",
    "draw.title": "Tap each card to reveal it",
    "draw.reading": "View Full Reading",
    "draw.again": "✦ Read Again",
    "spread.1.name": "Single Card", "spread.1.desc": "Daily guidance for today",
    "spread.3.name": "Three Cards", "spread.3.desc": "Past · Present · Future",
    "spread.5.name": "Five-Star Cross", "spread.5.desc": "Situation · Challenge · Foundation · Development · Advice",
    "pos.1": ["Today's Guidance"],
    "pos.3": ["Past", "Present", "Future"],
    "pos.5": ["Situation", "Challenge", "Foundation", "Development", "Advice"],
    "posctx.1": ["what deserves your attention today"],
    "posctx.3": ["the force that shaped where you are now", "your true state in the present", "where things are likely heading"],
    "posctx.5": ["the situation you stand in", "the hurdle you must cross", "the hidden foundation beneath it all", "the direction things may take", "the action this reading advises"],
    "badge.up": "Upright", "badge.rev": "Reversed",
    "sec.mean": "Card Meaning",
    "sec.love": "💗 Love",
    "sec.career": "💼 Career",
    "ov.title": "Reading Overview",
    "ov.kw": "Focus keywords of this spread: ",
    "ov.q": "Your question: ",
    "ov.nq": "(your unspoken question)",
    "ov.narr": "Overall, the core message of this spread is: ",
    "deep.btn": "✦ AI Deep Reading",
    "deep.hint": "Let AI weave a longer reading from your whole spread (optional)",
    "deep.loading": "The reader is consulting the cards…",
    "deep.fail": "AI is unavailable right now — please try again later (the detailed reading remains below).",
    "footer.credit": "Cards: Rider-Waite Tarot (public domain) · Interpretations: Tarotoo open dataset & The Pictorial Key to the Tarot",
    "footer.disclaimer": "For entertainment purposes only — not professional advice.",
  },
};

let lang = localStorage.getItem("tstars-lang") ||
  (navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en");
let deck = null;
let state = { spread: 3, reversed: true, question: "", shuffled: [], drawn: [], flipped: 0, shuffleTimer: null };

const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
const t = (k) => (T[lang] && T[lang][k]) || k;

function switchLang(to) {
  lang = to;
  localStorage.setItem("tstars-lang", lang);
  renderI18n();
  renderStateLabels();
  if (state.drawn.length) renderReadings();
}
function renderI18n() {
  $$("[data-i18n]").forEach((el) => {
    const k = el.dataset.i18n;
    if (T[lang][k]) el.textContent = T[lang][k];
  });
  $$("[data-i18n-placeholder]").forEach((el) => {
    const k = el.dataset.i18nPlaceholder;
    if (T[lang][k]) el.placeholder = T[lang][k];
  });
  $("#lang-btn").textContent = lang === "zh" ? "EN" : "繁中";
}
function renderStateLabels() {
  $$(".pos-label").forEach((el) => {
    el.textContent = posLabel(+el.dataset.idx);
  });
}

function posLabel(i) {
  const ps = T[lang]["pos." + state.spread] || [];
  return ps[i] || "";
}

/* ------- deck ------- */
function shuffleDeck() {
  const a = deck.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/* ------- setup ------- */
function bindSetup() {
  $$(".spread-opt").forEach((b) =>
    b.addEventListener("click", () => {
      $$(".spread-opt").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      state.spread = +b.dataset.spread;
    })
  );
  $("#start-btn").addEventListener("click", () => {
    state.question = $("#question").value.trim();
    state.reversed = $("#rev-toggle").checked;
    state.shuffled = shuffleDeck();
    state.drawn = [];
    state.flipped = 0;
    $("#reading-list").innerHTML = "";
    $("#reading-footer").hidden = true;
    $("#draw-cta").hidden = true;
    showStep("step-shuffle");
    startShuffleAnim();
  });
}

/* ------- shuffle ------- */
function startShuffleAnim() {
  const stage = $("#shuffle-stage");
  stage.innerHTML = "";
  const n = 5;
  const cards = [];
  for (let i = 0; i < n; i++) {
    const d = document.createElement("div");
    d.className = "sh-card";
    d.innerHTML = `<img src="./cards/back.jpg" alt="" loading="lazy" />`;
    stage.appendChild(d);
    cards.push(d);
  }
  const styles = [
    { transform: "translateX(-168px) rotate(-14deg)", delay: "0s" },
    { transform: "translateX(-84px) rotate(-7deg)", delay: ".15s" },
    { transform: "translateX(0) rotate(0deg)", delay: ".3s" },
    { transform: "translateX(84px) rotate(7deg)", delay: ".45s" },
    { transform: "translateX(168px) rotate(14deg)", delay: ".6s" },
  ];
  let tick = 0;
  state.shuffleTimer = setInterval(() => {
    tick++;
    cards.forEach((c, i) => {
      const s = styles[(tick + i) % 5];
      c.style.animationDelay = s.delay;
      c.animate(
        [
          { transform: s.transform, opacity: tick % 2 ? 0.85 : 1 },
          { transform: s.transform + " translateY(6px) rotate((" + ((tick % 3) - 1) * 4 + "deg))", opacity: 1 },
          { transform: s.transform, opacity: tick % 2 ? 0.85 : 1 },
        ],
        { duration: 260, easing: "ease-in-out" }
      );
      const dy = (i - 2) * 2;
      c.style.transform = `translateY(${dy}px)`;
    });
  }, 420);
  $("#stop-btn").onclick = () => {
    clearInterval(state.shuffleTimer);
    deal();
  };
}

/* ------- deal & draw ------- */
function deal() {
  const n = state.spread;
  for (let i = 0; i < n; i++) {
    const card = state.shuffled[i];
    const rev = state.reversed && Math.random() < 0.3;
    state.drawn.push({ id: card.id, rev, flipped: false });
  }
  showStep("step-draw");
  const grid = $("#draw-grid");
  grid.innerHTML = "";
  state.drawn.forEach((d, i) => {
    const w = document.createElement("div");
    w.className = "card-wrap";
    w.dataset.idx = i;
    w.innerHTML = `
      <div class="card-inner">
        <div class="card-face card-front"><img src="./cards/back.jpg" alt="card back" loading="lazy" /></div>
        <div class="card-face card-back"><img src="" alt="" loading="lazy" /></div>
      </div>
      <div class="pos-label" data-idx="${i}"></div>`;
    grid.appendChild(w);
    const frontImg = w.querySelector(".card-back img");
    frontImg.src = cardUrl(cardById(d.id));
    w.addEventListener("click", () => flipCard(i, w), { once: true });
  });
  renderStateLabels();
  $("#draw-title").textContent = t("draw.title");
}

function cardUrl(card) {
  return "./cards/" + card.img;
}
function cardById(id) {
  return deck.find((c) => c.id === id);
}

function flipCard(i, wrap) {
  state.drawn[i].flipped = true;
  state.flipped++;
  wrap.classList.add("flipped");
  if (state.drawn[i].rev) wrap.classList.add("rev");
  wrap.style.cursor = "default";
  addReadingCard(i);
  if (state.flipped === state.drawn.length) {
    $("#draw-cta").hidden = false;
    $("#reading-footer").hidden = false;
    buildOverview();
  }
}

/* ------- reading ------- */
function addReadingCard(i) {
  const d = state.drawn[i];
  const c = cardById(d.id);
  const list = $("#reading-list");
  const rev = d.rev;
  const f = (zhKey, enKey) => (lang === "zh" ? c[zhKey] : c[enKey]);
  const posCtx = (T[lang]["posctx." + state.spread] || [])[i] || "";
  const rc = document.createElement("div");
  rc.className = "reading-card";
  rc.innerHTML = `
    <div class="rc-img"><img src="${cardUrl(c)}" alt="${c.name_en}" loading="lazy" /></div>
    <div class="rc-body">
      <div class="rc-head">
        <span class="rc-pos">${posLabel(i)}</span>
        <span class="rc-name">${lang === "zh" ? c.name_zh : c.name_en}</span>
        <span class="el-badge" title="${c.element}">${lang === "zh" ? c.element_zh : c.element}</span>
        <span class="badge ${rev ? "reversed" : "upright"}">${rev ? t("badge.rev") : t("badge.up")}</span>
      </div>
      <p class="rc-ctx"><em>${posCtx} —</em></p>
      <div class="rc-keywords">
        ${(rev ? (f("kw_rev_zh", "kw_rev_en") || []) : (f("kw_zh", "kw_en") || []))
          .map((k) => `<span class="kw">${k}</span>`).join("")}
      </div>
      <p class="rc-mean"><b>${t("sec.mean")} ·</b> ${rev ? (f("mean_rev_zh", "mean_rev_en") || "") : (f("mean_zh", "mean_en") || "")}</p>
      <div class="rc-aspect"><span class="aspect-label">${t("sec.love")}</span>
        <span class="aspect-txt">${rev ? (f("love_rev_zh", "love_rev_en") || "") : (f("love_zh", "love_en") || "")}</span></div>
      <div class="rc-aspect"><span class="aspect-label">${t("sec.career")}</span>
        <span class="aspect-txt">${rev ? (f("career_rev_zh", "career_rev_en") || "") : (f("career_zh", "career_en") || "")}</span></div>
    </div>`;
  list.appendChild(rc);
  setTimeout(() => rc.scrollIntoView({ behavior: "smooth", block: "nearest" }), 120);
}

function renderReadings() {
  // re-render reading cards after lang switch
  const list = $("#reading-list");
  list.innerHTML = "";
  state.drawn.forEach((d, i) => addReadingCard(i));
  if (state.flipped === state.drawn.length) buildOverview();
}

/* ------- overview ------- */
function buildOverview() {
  const names = state.drawn.map((d) => {
    const c = cardById(d.id);
    return lang === "zh" ? c.name_zh : c.name_en;
  });
  const narr = state.drawn.map((d, i) => {
    const c = cardById(d.id);
    const name = lang === "zh" ? c.name_zh : c.name_en;
    const kws = d.rev ? f(d.id, "kw_rev", "kw_rev_en") : f(d.id, "kw", "kw_en");
    const k2 = (kws || []).slice(0, 2).join(lang === "zh" ? "、" : ", ");
    const role = (T[lang]["posctx." + state.spread] || [])[i] || "";
    const orient = d.rev ? t("badge.rev") : t("badge.up");
    return lang === "zh"
      ? `「${posLabel(i)}」是〈${name}〉（${orient}），以${k2}的特質，${role}。`
      : `${name} (${orient}) in the ${posLabel(i)} position — ${k2} — ${role}.`;
  }).join("");
  const div = document.createElement("div");
  div.className = "overview";
  const qLine = state.question ? t("ov.q") + state.question : t("ov.nq");
  div.innerHTML = `<h3>${t("ov.title")}</h3><p>${qLine}</p>
    <p style="margin-top:6px">${t("ov.narr")}${narr}</p>
    <p style="margin-top:6px">${t("ov.kw")}${names.join("、")}</p>`;
  $("#reading-list").prepend(div);
}

/* ------- AI deep reading ------- */
function f(id, zhKey, enKey) {
  const c = cardById(id);
  return lang === "zh" ? c[zhKey + "_zh"] : c[enKey];
}
async function runDeepReading() {
  const out = $("#deep-out");
  const btn = $("#deep-btn");
  out.hidden = false;
  out.className = "deep-out loading";
  out.textContent = t("deep.loading");
  btn.disabled = true;
  const payload = {
    lang,
    question: state.question,
    spread: state.spread,
    cards: state.drawn.map((d, i) => ({
      pos: posLabel(i),
      name: lang === "zh" ? cardById(d.id).name_zh : cardById(d.id).name_en,
      rev: d.rev,
      kw: f(d.id, d.rev ? "kw_rev" : "kw", d.rev ? "kw_rev_en" : "kw_en") || [],
      mean: f(d.id, d.rev ? "mean_rev" : "mean", d.rev ? "mean_rev_en" : "mean_en"),
      love: f(d.id, d.rev ? "love_rev" : "love", d.rev ? "love_rev_en" : "love_en"),
      career: f(d.id, d.rev ? "career_rev" : "career", d.rev ? "career_rev_en" : "career_en"),
    })),
  };
  try {
    const r = await fetch("/api/deep-reading", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (!r.ok || !data.text) throw new Error(data.error || "fail");
    out.className = "deep-out";
    out.textContent = data.text;
  } catch (e) {
    console.error(e);
    out.className = "deep-out error";
    out.textContent = t("deep.fail");
  } finally {
    btn.disabled = false;
  }
}

/* ------- steps ------- */
function showStep(id) {
  ["step-setup", "step-shuffle", "step-draw"].forEach((s) => ($("#" + s).hidden = s !== id));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function bindActions() {
  $("#lang-btn").addEventListener("click", () => switchLang(lang === "zh" ? "en" : "zh"));
  $("#deep-btn").addEventListener("click", runDeepReading);
  $("#view-reading-btn").addEventListener("click", () => {
    $("#reading-footer").hidden = false;
    $("#reading-list").scrollIntoView({ behavior: "smooth" });
  });
  $("#again-btn").addEventListener("click", () => {
    clearInterval(state.shuffleTimer);
    state.drawn = []; state.flipped = 0;
    $("#reading-list").innerHTML = "";
    $("#draw-grid").innerHTML = "";
    $("#draw-cta").hidden = true;
    $("#reading-footer").hidden = true;
    $("#deep-out").hidden = true; $("#deep-out").textContent = "";
    $("#question").value = "";
    showStep("step-setup");
  });
}

/* ------- boot ------- */
async function init() {
  try {
    const r = await fetch("./deck.json?v=1");
    deck = await r.json();
    if (!Array.isArray(deck) || deck.length !== 78) throw new Error("deck json invalid");
  } catch (e) {
    console.error(e);
    $("#start-btn").disabled = true;
    return;
  }
  renderI18n();
  bindSetup();
  bindActions();
}
init();
})();