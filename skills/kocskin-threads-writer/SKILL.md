---
name: kocskin-threads-writer
description: "為 KOCSKIN 品牌 Threads 帳號 @koc_skin 撰寫貼文，內建 K編人設、三條硬規則（不放設計圖卡／hashtag≤1／連結放留言）、台灣發文時段、鉤子句型庫與四關合規審查。寫 Threads、脆、@koc_skin 貼文時觸發。FB／IG 請改用 kocskin-post-writer。"
---

# KOCSKIN Threads 貼文生成器（@koc_skin）

依據《KOCSKIN_Threads貼文撰寫SOP_v1.md》與《KOCSKIN_Threads經營策略研究報告_20260725.md》。本 skill 說「怎麼做」，有爭議時回去看研究報告。

## 三十秒版本

寫給人看，不是寫給客戶看。第一行要讓人停下來，最後一行要讓人想回話。純文字為主，不放設計圖卡，不堆 hashtag，連結放留言區。寫商品前先查 V2 合規卡，寫完再由獨立的一方審一次。

## 範圍邊界

**只用於 KOCSKIN 品牌 Threads 帳號 @koc_skin。**

不適用：FB／IG 貼文（→ `kocskin-post-writer`）、Welson 個人 FB、露營瘋（瘋大叔）、小燕個人帳號、LP 文案、廣告素材。

**FB/IG 與 Threads 是兩條獨立內容線**（Welson 2026-07-25 裁定）。禁止把 FB/IG 文案搬來 Threads，或同一則文同時排兩邊。要講同一支商品時必須另寫一版。

## 模式

| 模式 | 行為 |
| --- | --- |
| **草稿（預設）** | 產文 ＋ 獨立審查；不寫 Notion |
| **正式** | 產文 ＋ 獨立審查 ＋ Welson 定稿後寫入 Notion 社群貼文 DB |
| **快線** | 臨時議題即時發布，見〈快線〉一節 |

未指定 → 草稿。使用者說「正式」「上稿」「寫進 Notion」→ 正式模式。

## 流程（六步）

```
1. 查 V2 合規卡（有商品才需要）
   ↓
2. 依配比與時段規劃篇數與日期
   ↓
3. 寫稿（結構公式 + 鉤子庫 + K編語氣）
   ↓
4. 獨立審查 —— 派 fresh subagent 跑四關，只審不改
   ↓
5. 依審查結果修正 → 修正版再審一次
   ↓
6. Welson 定稿 → 寫入 Notion（文案狀態＝待審）→ 讀回比對
```

### Step 1：查 V2 合規卡

提及任何商品前，先查 Notion 商品資料庫 V2（`collection://16d640a9-9f0b-441f-a670-821c6b4189ac`）該 SKU 頁面頂端的「合規卡」。也可直接呼叫 `kocskin-product-lookup`。

合規卡的「❌ 禁用／✅ 可用／📌 已核定決議」**優先於本檔與一切記憶**。V2 查不到 → 明講「需進一步確認」。Notion 連不上 → 明講「未連 V2、無法核對合規卡」，**不產出商品文案**。

> ⚠️ 合規卡會被更新，且會來回翻轉。例：7/11 曾裁定「傳明酸品項可訴求美白」，**8/8 已更正推翻**——美白須該產品本身有特定用途化粧品許可證，含核可成分不等於有宣稱資格，目前極光線只能寫「亮白／透亮」（正本見 kocskin-compliance-check〈美白宣稱規則〉）。**永遠以當下讀到的卡與 compliance-check 為準，不要用記憶中的結論。**

### Step 2：規劃

配比以 14 篇為一循環：教育型 5、商品價值型 5、見證品牌型 4、促銷導購型 0–2。原則 **70% 人味／教育，30% 產品**。

時段（台灣時間，勿改）與五大支柱見 [references/threads-rules.md](references/threads-rules.md)。**絕對避開早上 8–9 點。**

### Step 3：寫稿

結構公式、鉤子句型庫、K編語氣特徵見 [references/persona-and-hooks.md](references/persona-and-hooks.md)。

100–250 字，emoji 0–1 個。

### Step 4：獨立審查（分開執行，不等下一輪）

**產出與審查必須由不同的一方做**（憲章 R2）。Welson 2026-07-25 裁定：取消「停一輪」的等待，但**不取消分開審查**。

做法：寫完後在同一輪內派 **fresh subagent** 跑四關，只審不改，回傳逐關結論。審查通過的證據是逐關結論，不是一句「已檢查」。

審查格式與必查的兩類敘述（幕後型陳述、代真人陳述）見 [references/threads-rules.md](references/threads-rules.md)。也可直接呼叫 `kocskin-compliance-check`。

### Step 6：寫入 Notion

**預設草稿模式不寫 Notion。** 只有 Welson 明確確認為發布版（定稿）後才寫入——這是草稿模式的唯一例外。

欄位對照表與技術踩雷紀錄見 [references/notion-and-images.md](references/notion-and-images.md)。寫入後必須讀回全文比對（R7）。

## 發佈關卡

排程貼文是單向管道，AI 不得跳關：

```
AI 寫文＋獨立審查 → 寫入 Notion（文案狀態＝待審、啟用自動發文＝__NO__）
  → 【Welson 在 Notion 按「核准」＋勾「啟用自動發文」】
  → 自動發文引擎掃描（trig_01DgE6EUokjbzYxWMjeREBnD，每 5 小時第 36 分）
  → 引擎寫入 Buffer → 自動發佈
```

- Threads **進自動發文引擎，但需 Welson 核准後才排**。2026-08-03 裁定：**與 FB/IG 統一**——AI 寫入 `文案狀態＝待審`、`啟用自動發文＝__NO__`，「核准」與「啟用」一律由 Welson 在 Notion 完成（7/25「定稿即核准」做法廢止）。
- 對話裡的「OK／可以發」＝同意文案內容，**不等於**授權排程。
- **排程貼文不得由 AI 直接呼叫 Buffer。** 唯一例外是下面的〈快線〉。

## 快線（臨時議題即時發布）

Threads 最適合即時承接議題——研究報告指出第一小時的互動速度是演算法最強訊號。不提商品的純觀點型貼文特別適合走這條。

```
Welson 丟想法 → （有商品才查 V2）→ 寫 → 我內審一次並附結論
  → 交給 Welson，由他自審把關 → 他明確說「發」→ create_post mode=shareNow
```

- **臨時發文由 Welson 自審**（2026-07-25 裁定）。我仍會做一次內審並主動標出禁語、簡體字、商品事實問題，但最終判斷權在他。
- 若內審發現 **Critical 等級**問題（醫療效能宣稱、無文號美白、停售品、真實名人虛構引述），**必須明確標紅呈報**，不得只附在結論裡帶過。
- **發布動作只在 Welson 明確說「發」之後執行**，AI 不自行按送出。
- 快線適用純觀點、時事承接、幕後碎念。要推商品的貼文不走快線——省不掉 V2 查核。

## 配圖（半自動）

Threads 多數貼文純文字。要配圖時走半自動：**系統挑 2–3 張候選，由人選一張。**

理由：規則挑得出正確 SKU，挑不出「這張圖看起來像不像真人隨手拍」——而那正是 Threads 圖片唯一的判準。

選圖邏輯（類型優先序：實拍 > AI實景；白底／設計卡不用）、素材庫欄位與 Cloudinary 尺寸切換見 [references/notion-and-images.md](references/notion-and-images.md)。

> ⚠️ **notion-and-images.md §3 的「去重」小節（比對貼文 DB 圖片網址字串）與「45 個在售 SKU／26 有實拍／19 缺」等寫死數字已作廢**（2026-09-14 修訂，對齊 post-writer 2026-08-07 裁定）。去重一律以下方本節為準。

### 去重（正本，2026-09-14 起）

素材圖庫 `collection://a924b6bd-c492-4328-93ea-3d036229301f` 已有 **`最近使用日期`（date）** 欄位。挑候選時先排除 30 天內用過的：

```sql
SELECT "圖名", "SKU", "類型", "場景", "圖片網址", "date:最近使用日期:start"
FROM "collection://a924b6bd-c492-4328-93ea-3d036229301f"
WHERE "SKU"='KOCxxx' AND "狀態"='可用' AND "類型" IN ('實拍','AI實景')
  AND ("date:最近使用日期:start" IS NULL
       OR date("date:最近使用日期:start") < date('now','-30 day'))
```

- **指派圖片後，必須回寫該素材列的 `最近使用日期`**（填該則貼文的發文日期；同一張排多天時填最晚那天）。不回寫，下一批必重複。
- **跨渠道共用同一個欄位。** FB/IG 與 Threads 內容線獨立，但素材共用；`最近使用日期` 是三渠道共用的，所以只要每條線都回寫，一次查詢就涵蓋跨渠道。
- ❌ **不要再用「比對社群貼文 DB 的圖片網址字串」去重**——同一張圖在三個渠道的 Cloudinary transform 片段不同（Threads `c_limit,w_1080`、FB `c_fill…`），字串比對抓不到。2026-08-19 三渠道同時撞圖 `KOC073_ceo02_scene` 就是這樣漏的。
- **實拍缺口不寫死數字。** 需要時即時查：`SELECT "SKU", COUNT(*) FROM "collection://a924b6bd-…" WHERE "類型"='實拍' AND "狀態"='可用' GROUP BY "SKU"`，再對照 V2 在售清單找缺實拍的 SKU。若該 SKU 沒有實拍，明講「Threads 建議走純文字」，不硬塞白底圖。

**需要照片的貼文，圖沒備妥前 `啟用自動發文` 一律 `__NO__`**，否則會發出空殼貼文。

## 海巡（不能自動化，但價值最高）

排程可以自動，留言不能。貼文的價值有一半在留言區。

| 動作 | 頻率 |
| --- | --- |
| 回覆自己貼文的第一批留言 | 發文後 30–60 分鐘（黃金窗口，過了不會回頭重評） |
| 海巡別人的熱門貼文 | 每天 5–10 次（早期留言權重最高，觸及可能比自己發文高 10 倍） |

留言要有料：觀點／幽默吐槽／延伸問題。**不要**「好棒」「推推」這類複製貼上式讚美——engagement bait 有降權風險。

這一段是**提醒人去做**，不是 AI 代做。

## 依賴 skill

- `kocskin-product-lookup` — 提及商品時查 V2 合規卡
- `kocskin-compliance-check` — Step 4 四關審查

## 不要做的事

- ❌ 從 IG／FB 一鍵同步或搬運文案
- ❌ 放設計圖卡（有商品名／賣點／售價排版的圖）
- ❌ 堆 hashtag（≤1 個，Notion Hashtag 欄留空）
- ❌ 主文放購買連結（連結放第一則留言，Notion 導購連結欄留空）
- ❌ 用「症狀描述 → 商品」結構（暗示改善症狀＝違規）
- ❌ 憑記憶寫商品資料或引用記憶中的合規結論
- ❌ 自己寫完自己審就當審查完成（Step 4 必須派獨立的一方）
- ❌ 排程貼文直接呼叫 Buffer（只有快線且 Welson 說「發」才可）
- ❌ 未經 Welson 定稿就寫入 Notion
- ❌ 用小燕第一人稱寫 @koc_skin 的貼文（K編不是小燕）
- ❌ **挑圖不查 `最近使用日期` 就指派，或指派後不回寫該欄位**
- ❌ **用貼文 DB 圖片網址字串比對去重**（已作廢）
- ❌ 在文案或報告裡引用寫死的 SKU 數／實拍張數（一律 SQL 即時查）

## 內部參考檔

- [references/persona-and-hooks.md](references/persona-and-hooks.md) — K編語氣、結構公式、鉤子句型庫
- [references/threads-rules.md](references/threads-rules.md) — 三條硬規則、時段、配比、禁止事項、審查格式、指標、檢查表
- [references/notion-and-images.md](references/notion-and-images.md) — Notion 欄位對照、技術坑、選圖類型優先序、尺寸切換（§3 去重小節已作廢，以本檔〈去重〉為準）

## 更新紀錄

- 2026-09-15：Step 1 範例改為 8/8 美白更正版（原引 7/11 舊裁定，已被推翻）。
- 2026-09-14：去重改以素材庫 `最近使用日期` 為準（對齊 post-writer 8/7 裁定），作廢 URL 字串比對法；移除寫死的在售／實拍數字，改即時查。