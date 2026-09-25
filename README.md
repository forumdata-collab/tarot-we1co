# 星語塔羅 · Tarot of the Stars

互動塔羅占卜網站，部署於 Cloudflare Pages + R2（圖片）。

## 功能
- **互動占卜**：默想問題 → 洗牌（可自行按「停止」）→ 逐張翻牌 → 完整牌陣解讀
- **三種牌陣**：單張指引 / 三張（過去·現在·未來）/ 五張十字（現況·挑戰·根基·發展·建議）
- **逆位支援**：可開關，翻牌時隨機出現逆位並顯示逆位解讀
- **雙語**：繁體中文 / English
- **78 張牌完整解讀**：關鍵詞 + 正逆位解說，牌面圖片存於 Cloudflare R2

## 技術
- 純靜態前端（HTML/CSS/JS，無框架）
- Pages Function `functions/cards.js` 從 R2 bucket `tarot-cards` 讀取牌面圖片（`deck/<file>.jpg`）
- 牌面：**Rider-Waite Tarot**（公有領域，來源 [mixvlad/TarotCards](https://github.com/mixvlad/TarotCards)）
- 解讀資料：[Tarotoo 開源資料集](https://github.com/Tarotoo-com/tarotoo-tarot-dataset)（參考 A.E. Waite《The Pictorial Key to the Tarot》），繁中翻譯由本項目整理

## 部署
```bash
wrangler pages deploy . --project-name=tarot-we1co --branch=main
# R2 binding: TAROT_CARDS → tarot-cards（需先在 Pages 專案註冊 binding）
```

## 目錄
- `index.html` / `app.css` / `app.js` — 前端
- `deck.json` — 78 張牌資料（雙語）
- `functions/cards.js` — R2 圖片代理
- `build_zh.py` — 繁中資料建構腳本

## 聲明
占卜結果僅供娛樂參考。
