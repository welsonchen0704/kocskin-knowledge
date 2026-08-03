---
name: kocskin-post-writer
description: 為 KOCSKIN 克麗詩黛品牌官方帳號撰寫 Facebook／Instagram 貼文（預設兩版），含品牌語氣、內容類型範本、自動配圖候選與獨立合規審查。寫 FB 貼文、IG 貼文、粉絲頁貼文時觸發。Threads／脆請改用 kocskin-threads-writer。
---

# KOCSKIN 社群貼文生成器（FB / IG）

為 KOCSKIN 品牌官方帳號的社群貼文把關品質與合規。丟主題或商品，這個 skill 把流程串好。

## 範圍邊界

**這支 skill 只用於 KOCSKIN 品牌官方帳號的 Facebook 與 Instagram。**

不適用：
- **Threads／脆（@koc_skin）→ `kocskin-threads-writer`**
- Welson 個人 FB（短 3–5 行、自嘲、無 hashtag — 風格完全不同）
- 露營瘋／瘋大叔粉絲頁（戶外社群調性，未在此 skill 範圍）
- LP 文案、廣告素材、Email、新聞稿

碰到上列情境，提醒使用者改用對應 skill 或另行處理，不要硬寫。

### FB/IG 與 Threads 是兩條獨立內容線

Welson 2026-07-25 裁定：兩線各自規劃、各自排程、各自配比。**禁止把 FB/IG 文案搬去 Threads，或同一則文同時排兩邊。** 要在 Threads 講同一支商品，必須用 `kocskin-threads-writer` 另寫一版。

（規則全文見專案文件 `claude/發文渠道分流規範.md`。）

## 模式（先確認，再動手）

| 模式 | 行為 |
| --- | --- |
| **草稿（預設）** | 產文 + 跑合規審查；不寫 Notion |
| **正式** | 產文 + 跑合規審查 + 寫入 Notion 📅 社群貼文管理 DB（`04b770fc-b2fa-4185-85e4-b6245777557d`），狀態一律 `待審`、`啟用自動發文` 不勾。**只寫 Notion，排程不碰 Buffer**（見〈發佈關卡・鐵律〉） |
| **快線** | 臨時議題即時發布，不進 Buffer 佇列。見〈唯一例外：快線〉 |
| **研究** | 不產文，只給內容類型建議與資料蒐集；不跑 compliance |

未指定 → 預設草稿。使用者說「正式」「上稿」「寫進 Notion」「同步社群 DB」→ 切正式模式。使用者說「馬上發」「現在就發」「不要排程」→ 快線。

## 發佈關卡・鐵律（最重要，違反＝搶跑）

KOCSKIN 排程貼文的發佈流程是一條**單向管道**，每一關的核准點都在指定位置，AI 不得跳關：

```
AI 寫文＋獨立審查  →  寫入 Notion（狀態＝待審）  →  【Welson 在 Notion 按「核准」＋勾「啟用自動發文」】  →  自動發文引擎掃描  →  引擎寫入 Buffer  →  Buffer 自動發佈
```

- **核准這一關只在 Notion 按**。使用者在對話裡說「OK／定稿／可以發」＝同意這份文案內容，**不等於** Notion 的「核准」，更不是授權你去送 Buffer。
- **排程貼文，AI 不得直接呼叫 Buffer**（`create_post` 等）。送 Buffer 是「自動發文引擎」在 Welson 於 Notion 核准後的**專責動作**。
- 正式模式寫 Notion 時：`文案狀態＝待審`、`啟用自動發文` 留空（`__NO__`）、**不要**填 `Buffer貼文ID`、`發文狀態＝待發`。核准與啟用一律留給 Welson 在 Notion 手動完成。
- 使用者就算明講「幫我排到 X 點自動發」，正確做法仍是：寫成 Notion 待審＋設好 `發文日期`，然後告訴他「請到 Notion 核准＋勾啟用，引擎會自動送 Buffer」。**不是**自己動手排 Buffer。
- 引擎排程：`trig_01DgE6EUokjbzYxWMjeREBnD`「KOCSKIN 自動發文引擎（核可→Buffer）v2」，cron `36 */5 * * *`（**每 5 小時的第 36 分**掃描一次）。送 Buffer 需距發文 ≥30 分鐘，且下一次掃描最長可能要等 5 小時——提醒 Welson **提早半天核准**，不要壓線。

### 唯一例外：快線（臨時議題即時發布）

Welson 2026-07-25 開放：他丟一個臨時想法要「馬上發」時，可走 `create_post` 的 `mode: shareNow` 直接發布，不進 Buffer 佇列。條件全部成立才可執行：

1. 是 Welson 本人在這一輪明確提出的臨時發文需求；
2. 提及商品的話仍**必須查 V2 合規卡**（這關省不掉）；
3. 我先做一次內審並附結論，**Critical 等級問題（醫療效能宣稱、無文號美白、停售品、真實名人虛構引述）必須明確標紅呈報**；
4. **臨時發文由 Welson 自審把關**，最終判斷權在他；
5. **他明確說「發」之後**才執行 `create_post`，AI 不自行按送出。

快線適用純觀點、時事承接、輕量互動。要完整推商品、要配圖排版的貼文不走快線。

## 流程（3 步）

### Step 1：查商品（僅在指定商品時）

若使用者指定具體商品（例：「玫瑰超導安瓶」「青春美妍膠原飲」），**必須呼叫 `kocskin-product-lookup`** 取得：
- 產品名稱、售價、容量規格
- 核心成分、主打賣點
- 適用膚質、目標客群
- **合規備注**（直接決定文案用字邊界，必須完整帶入 Step 2）

若使用者只給「教育型主題」（例：「敏感肌保養知識」「換季膚況」）沒指定商品 → 跳過此步。

**禁止憑記憶寫商品資料。** 記憶會錯，也會過時。

### Step 2：寫文案

選一個內容類型（單篇選擇，不做比例追蹤）：

| 類型 | 適用情境 |
| --- | --- |
| **商品價值型** | 主推單一商品的賣點、成分、適用族群 |
| **教育型** | 保養知識、使用教學、膚質判別 |
| **見證品牌型** | 使用者見證、品牌故事、幕後 |
| **促銷導購型** | 檔期活動、折扣、新品發表 |

四種類型的詳細結構範本見 [references/content-types.md](references/content-types.md)。

依選定平台（FB / IG，**預設兩平台同產**）撰寫，平台差異見 [references/platform-specs.md](references/platform-specs.md)。兩個平台不能一貼二用，第一行、斷行、hashtag 各自有套法。

**字數**（Welson 2026-07-25 裁定，取代舊的「FB/IG 一律 150 字內」合併規格；2026-08-02 Welson 確認以《發文渠道分流規範》為準）：

- **FB：不設字數上限**，依內容需要決定長短（前 3 行仍是決定展開的關鍵）。
- **IG：150 字內。**

**品牌語氣**：
- ✅ 親切、專業、有溫度（懂成分的閨蜜分享）
- ✅ 具體、可證據化（成分、實驗、見證）
- ❌ 焦慮行銷（「再不用就完了」）
- ❌ 誇大神化（「神級」「逆天」「奇蹟」）
- ❌ 過度口語（「姊妹們快衝」）
- ❌ 過度正式（「本公司隆重推出」）

語氣對照範例見 [references/voice-examples.md](references/voice-examples.md)。

### Step 3：獨立合規審查（分開執行，不等下一輪）

**產出與審查必須由不同的一方做**（憲章 R2）。Welson 2026-07-25 裁定：取消「停一輪」的等待，但**不取消分開審查**。

做法：寫完後在同一輪內**派 fresh subagent** 跑四關，只審不改，回傳逐關結論。也可直接呼叫 `kocskin-compliance-check`。

- **Critical / High** → 修正後再送審一次
- **Medium / Low** → 輸出並附審查摘要，由使用者決定是否微調

審查通過的證據是**逐關結論**，不是一句「已檢查」。

合規檢查涵蓋化粧品／保健食品法規、停售商品、PDRN 線歸屬、簡體字、執行長稱呼、虛構名人引述等。**所有合規規則交給 compliance skill 統一維護**，這支不重複列。

## 輸出格式

純文字、無裝飾分隔線。範本：

```
KOCSKIN｜[主題或商品]｜[類型]

【Facebook】
（正文段落式，長度依內容需要；FB 不設上限）

#hashtag1 #hashtag2 #hashtag3（3–5 個，含 #KOCSKIN）

【Instagram】
（第一行 hook）

（主文 150 字內，斷行較多）

#hashtag1 #hashtag2 ...（3–5 個，含 #KOCSKIN）

——
配圖候選：1. [圖名／類型] 2. [圖名／類型] 3. [圖名／類型] → 請挑一張
合規審查：🟢 通過 ／ 🟡 建議調整 — [逐關結論]
備注：[是否需小燕出鏡／檔期搭配，1–3 點]
```

**正式模式額外動作**：呼叫 Notion API 寫入 📅 社群貼文管理 DB（`04b770fc-b2fa-4185-85e4-b6245777557d`）。每個平台一列，欄位包含：貼文標題、發文平台、主角商品、內容類型、貼文文案、Hashtag、圖片網址、導購連結、發文日期（datetime，用展開鍵 `date:發文日期:start`＋`date:發文日期:is_datetime`）。**狀態欄位固定**：`文案狀態＝待審`、`發文狀態＝待發`、`啟用自動發文＝__NO__`、不填 `Buffer貼文ID`（checkbox 欄位值用字串 `__YES__`／`__NO__`，不是布林）。**寫入前先顯示摘要，等使用者確認後再寫**。寫入失敗則輸出純文字供手動建立。**寫完就結束——不呼叫 Buffer、不改核准狀態**；接著提示 Welson 到 Notion 核准＋勾啟用即可。

## 配圖（自動跳候選 ＋ 依平台切尺寸）

Welson 2026-07-25 裁定：FB/IG **自動從素材圖庫跳候選圖，並依平台自動切換尺寸**。

### Step A：從素材庫查候選

**素材圖庫索引：** `collection://a924b6bd-c492-4328-93ea-3d036229301f`
欄位：圖名／SKU／商品(relation)／商品名／場景／類型／狀態／圖片網址／尺寸／備註

```sql
SELECT "圖名", "SKU", "類型", "場景", "圖片網址"
FROM "collection://a924b6bd-c492-4328-93ea-3d036229301f"
WHERE "SKU"='KOCxxx' AND "狀態"='可用'
```

FB/IG 的類型優先序：**白底／設計卡／AI實景／實拍皆可用**（品牌帳號本來就是經營過的視覺），依內容類型挑：商品價值型優先白底或設計卡，教育型與見證品牌型優先實拍或 AI實景。

輸出 2–3 張候選（附圖名與類型）讓 Welson 挑，挑定再填 Notion。純教育文無主角商品時可略過。

**去重**：素材庫沒有「最近使用」欄位。查社群貼文 DB 近期已用的圖片網址，從候選中排除。

```sql
SELECT "圖片網址" FROM "collection://04b770fc-b2fa-4185-85e4-b6245777557d"
WHERE "發文平台" IN ('Facebook','Instagram') ORDER BY "date:發文日期:start" DESC
```

### Step B：依平台切尺寸（Cloudinary 動態裁切）

一張原圖可衍生所有比例——在 `upload/` 後面插參數即可，不必重複上傳。

| 平台／版位 | 參數 |
|---|---|
| FB 連結圖 | `c_fill,g_auto,w_1200,h_630` |
| FB 一般貼文 | `c_fill,g_auto,w_1200,h_1200` |
| IG 方形 | `c_fill,g_auto,w_1080,h_1080` |
| IG 直式 | `c_fill,g_auto,w_1080,h_1350` |
| IG 限動 | `c_fill,g_auto,w_1080,h_1920` |

範例：`https://res.cloudinary.com/s55rhpbr/image/upload/c_fill,g_auto,w_1080,h_1350/koc_xxx.jpg`

> `g_auto` 會自動抓主體置中，但**商品瓶身照仍需人眼確認沒被裁到標籤**。

> ⚠️ Threads 的配圖規則完全不同（只限寬不裁切、禁設計圖卡、半自動由人選），見 `kocskin-threads-writer`。

## 配圖託管（Cloudinary MCP，2026-07-22 起）

配圖上傳走 Cloudinary MCP（連接器名 `Cloudinary`，帳號 cloud name `s55rhpbr`）。工具 `mcp__Cloudinary__upload-asset`：

- **可靠上傳法**：`file` 帶「公開 HTTPS 網址」→ Cloudinary 抓圖入庫，任何大小都穩。
- **小圖**：`file` 可帶 base64 data URI（`data:image/...;base64,...`）。⚠️ 大圖（數十 KB 以上）**不要**用 inline base64——超長字串在工具層不穩、會 `Could not decode base64`；大圖一律走公開 URL。
- 上傳成功回傳 `secure_url`（`https://res.cloudinary.com/s55rhpbr/...`），把它填進 Notion 貼文列的「圖片網址」。
- 沙盒生成的卡片要上 Cloudinary：壓成精簡 JPEG 走 data URI（單張、體積小時可行），或先讓圖取得公開 URL 再讓 Cloudinary 以 URL 抓取。
- 不必再手動拖 Supabase；Supabase 公開 bucket 仍可作備援。
- 一律「先產文＋合規＋寫 Notion 待審」，配圖網址可同批填入；此步不改發佈關卡（送 Buffer 仍只由引擎在 Notion 核准後執行）。

## 觸發 vs 不觸發

**觸發**：KOCSKIN 品牌官方帳號的 FB／IG 貼文需求。

**不觸發**：
- **Threads／脆／@koc_skin → `kocskin-threads-writer`**
- LP 文案、廣告素材、Email、新聞稿 → `marketing:draft-content`
- Welson 個人 FB、露營瘋（瘋大叔）帳號 → 各自風格不同
- 純文案審查無生成需求 → `kocskin-compliance-check` 直接跑

## 依賴 skill

- `kocskin-product-lookup` — 指定商品時必呼叫
- `kocskin-compliance-check` — 產出後自動審查

兩者組成內容生產鏈：查 → 寫 → 審。

## 不要做的事

- ❌ 憑記憶寫商品資料（Step 1 用 product-lookup）
- ❌ 跳過合規審查（Step 3 必跑，且必須派獨立的一方，自己寫完自己審不算）
- ❌ 一貼二用（FB / IG 各自版型）
- ❌ **用這支寫 Threads 貼文，或把 FB/IG 文案搬去 Threads**（兩條獨立內容線）
- ❌ 誤用此 skill 寫個人 FB 或露營瘋貼文
- ❌ 正式模式未經確認直接寫入 Notion
- ❌ **排程貼文直接呼叫 Buffer（create_post 等）**——送 Buffer 是引擎在 Notion 核准後的專責，AI 不碰。唯一例外是〈快線〉，且必須等 Welson 明確說「發」
- ❌ **把對話裡的「OK／定稿」當成 Notion 核准**——那只是同意文案內容，不是發佈授權
- ❌ 正式模式寫 Notion 時把狀態設成「核准」或勾「啟用自動發文」——一律留 `待審`／不勾，交給 Welson
- ❌ **文案內已放導購連結、又把同一條填進 Notion「導購連結」欄位**——引擎 v2 會在 FB 文末自動接一次，結果連結重複。規則：填了「導購連結」欄位，文案內就**不要**再放同一條連結（二擇一）。IG 不受影響（走 bio）

## 內部參考檔

- [references/content-types.md](references/content-types.md) — 4 種內容類型結構範本
- [references/platform-specs.md](references/platform-specs.md) — FB / IG 格式規範
- [references/voice-examples.md](references/voice-examples.md) — 好／壞語氣對照
- [references/weekly-rhythm.md](references/weekly-rhythm.md) — 週節奏（背景參考；主流程已不做比例追蹤）
