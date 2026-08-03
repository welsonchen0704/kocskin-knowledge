---
name: kocskin-product-lookup
description: 查詢 KOCSKIN 克麗詩黛商品資料庫 V2（Notion），回答商品成分、售價、系列、定位、適用膚質、主打賣點等資訊。當使用者提到 KOCSKIN 任一商品名稱、系列（3D全能、極光美白、玫瑰抗老、敏肌修護、基礎清潔等）、或問「哪些商品適合 X 膚質」「XX 多少錢」「XX 的主要成分」時就要觸發。撰寫 KOCSKIN 文案、客服應答、廣告素材前也要先用這個 skill 查商品真實資料，避免憑空捏造。不要生成文案（社群貼文交給 kocskin-post-writer；LP／廣告素材／Email／新聞稿目前無對應 skill），只負責「查資料」。
---

# KOCSKIN 商品資料庫查詢（v1.1）

這個 skill 封裝 KOCSKIN 克麗詩黛商品資料庫 V2 的查詢邏輯，讓使用者不用手動開 Notion 就能取得精準、結構化的商品資料。

## 核心資訊

- **Notion Data Source ID**：`16d640a9-9f0b-441f-a670-821c6b4189ac`
- **Collection URL**（給 search 用）：`collection://16d640a9-9f0b-441f-a670-821c6b4189ac`
- **Database URL**：`https://www.notion.so/6e20bfbc8a9c4f1bb89f23f4b32b11ec`
- **總 SKU 數**：43 個（其中部分為「開發中」狀態）

## 已知限制（非常重要，不遵守查詢會失敗）

目前環境中的 Notion MCP 工具有兩組，**只有一組可用**：

**✅ 可用**（使用這組）
- `notion-search`
- `notion-fetch`
- `notion-create-pages`
- `notion-update-page`
- `notion-create-view`

**❌ 不要用**（會回 400）
- `API-query-data-source`（Route 表沒升級到 Notion 2025-09-03 新版 API，回 `invalid_request_url`）
- `API-retrieve-a-data-source`（同上）
- `notion-fetch` on `view://...` URL（回 `URL type view not currently supported for fetch tool.`）

### 為什麼有兩組

原本以為新版的 query-data-source 會修，但 2026-05-10 實測仍壞。後來嘗試用 view（先建 view 帶 filter，再 fetch view 拿過濾結果），實測也行不通：view 給人在 UI 看可以，但 API 不支援 fetch。

**結論**：目前唯一能用的查詢路徑是 `notion-search`（語意搜尋）+ `notion-fetch`（單頁讀取）。任何結構化過濾都必須在程式層做。

## 預建 View 清單（給人類用，不是給 AI 用）

以下 8 個 view 已建立在 V2 資料庫上，**供使用者在 Notion UI 直接點擊瀏覽**，AI 不要嘗試 fetch 它們。

| 名稱 | 類型 | 等同條件 | View ID |
|---|---|---|---|
| 📋 在售總覽 | Table | SKU狀態 = 在售 | `35cb9aa8-e77e-8100-9802-000c77ab0c97` |
| 🚪 引流商品 | Table | 在售 + 引流商品 | `35cb9aa8-e77e-8189-8370-000c10aa6bc9` |
| 🎯 主力商品 | Table | 在售 + 主力商品 | `35cb9aa8-e77e-81b8-a28b-000ce8c3f98b` |
| 💎 高單價商品 | Table | 在售 + 高單價商品 | `35cb9aa8-e77e-81a0-8e41-000c43df010e` |
| 🔄 回購商品 | Table | 在售 + 回購商品 | `35cb9aa8-e77e-8124-8c47-000c35696f5b` |
| 🌸 敏感肌可用 | Table | 在售 + 適用膚質含敏感肌 | `35cb9aa8-e77e-81c7-9fec-000cca2c02c8` |
| 📊 按系列分類 | Board | Board view，按系列分類分組 | `35cb9aa8-e77e-81e4-87bd-000c802c385a` |
| ⚠️ 開發中商品 | Table | SKU狀態 = 開發中 | `35cb9aa8-e77e-8113-bd05-000cfec5ed33` |

**AI 使用方式**：當使用者請求的查詢條件剛好等同某個 view，**告訴他「你也可以直接到 Notion 開 [view 名稱] 看」**，但 AI 自己要查資料時，仍走 search + fetch 流程。

## 使用原則

### 1. 自動排除停售與開發中商品

**預設只回傳 `SKU狀態 == 在售` 的商品**。

- 停售商品：氣墊粉餅補充蕊、益生守護者 7 日體驗包等
- 開發中商品：已建檔但尚未上架（在 ⚠️ 開發中商品 view 可見）

**例外**：使用者明確要求看停售/開發中商品（例如「停售的商品有哪些」「pipeline 上有什麼新品」）才納入，並清楚標示狀態。

⚠️ 注意：實務上有些商品 SKU狀態 是「在售」，但內頁 metadata 表格寫「開發中」，這是欄位不同步問題。以 SKU狀態 為準。

### 2. 只讀不寫

本 skill **絕對不修改 Notion 資料**。如果使用者想更新商品資料，請他直接在 Notion 改，或另外明確請求修改。

### 3. 不生成文案

查完資料就報告資料。若使用者需要文案：

- **FB / IG / Threads 貼文** → 用 `kocskin-post-writer`，把 lookup 結果當素材傳入
- **LP 文案 / Meta 廣告素材 / Email / 新聞稿** → 目前無對應 skill，直接讓 Claude 手動寫，並提醒最後要過 `kocskin-compliance-check`

## 執行流程（Search + Fetch + Code-Filter pattern）

### Step 1：判斷查詢類型，決定策略

| 類型 | 範例 | 策略 |
| --- | --- | --- |
| **單品查詢** | 「玫瑰精華的成分是什麼」 | 直接走 Step 2（targeted search）→ Step 3 |
| **多條件篩選** | 「所有敏感肌可用的主力商品」 | 走 Step 2（targeted search）多組關鍵字 → Step 3 → Step 4 程式過濾 |
| **系列/分類清單** | 「極光美白系列有哪些」 | 走 Step 2（用系列名 + 典型成分）→ Step 3 → Step 4 過濾系列 |
| **全品項枚舉** | 「目前在售有哪些商品」 | 走 Step 2A（loose search 枚舉）→ Step 3 |
| **商品比較** | 「A 和 B 的差異」 | 直接 fetch 兩支商品 |
| **組合推薦** | 「乾性肌 1500 元預算的保養組合」 | 走 Step 2 多組關鍵字 → Step 3 → Step 4 過濾條件後組合建議 |

### Step 2：targeted search（精準關鍵字）

挑 2-4 個關鍵字，分別呼叫 `notion-search`：

```
notion-search(
  query: "<關鍵字>",
  data_source_url: "collection://16d640a9-9f0b-441f-a670-821c6b4189ac",
  page_size: 25,
  filters: {},
  max_highlight_length: 0
)
```

關鍵字怎麼挑：
- **系列查詢** → 用系列名稱（如「玫瑰抗老」）、**系列定位句內的特色詞**（如「玫瑰幹細胞」「PDRN」）、**典型核心成分**
- **膚質/需求** → 用膚質名（如「敏感肌」「乾性肌」）、需求詞（如「保濕」「美白」「抗老」）
- **商品名稱** → 直接用名稱片段

為什麼要多組：`notion-search` 是 **semantic search**，單一關鍵字可能漏掉部分商品。多組關鍵字聯集才有完整召回。

### Step 2A：loose search 枚舉（用於全品項列表）

當使用者要「所有商品」「在售清單」「現在賣什麼」這類枚舉需求時：

跑 2-3 組通用關鍵字，去重合併：

```
搜 1：query="商品", page_size=25
搜 2：query="KOCSKIN", page_size=25
搜 3（如還不夠）：query="保養", page_size=25
```

合併去重（用 page id 為 key）→ 對每筆 fetch 驗證 SKU狀態。

⚠️ 警告：此方法在 43 SKU 規模下還能 cover；若未來 SKU 數成長到超過 50，可能需要更多組關鍵字、或者改用其他策略（例如直接告訴使用者去開 📋 在售總覽 view）。

### Step 3：用 `notion-fetch` 取得完整 properties

對 Step 2 / Step 2A 的每個候選 page id 呼叫：

```
notion-fetch(id: "<page_id>")
```

### Step 4：在程式層過濾

取得完整 properties 後，在程式層驗證下列條件：
- `SKU狀態 == "在售"`（預設必要，除非使用者明示）
- 任務指定的過濾條件（如 `系列分類 == "玫瑰抗老系列"`、`適用膚質 contains "敏感肌"`、`售價 <= 1500`）

篩掉不符合的，保留符合的。

### Step 5：整理輸出

**單品輸出格式**（繁體中文）：

```
📦 [產品名稱]（[系列分類]）
━━━━━━━━━━━━━━━━━━
💰 售價：NT$ [售價] / [容量規格]
🎯 定位：[商品定位角色]
✨ 主打賣點：[主打賣點]
💬 主推訴求句：「[主推訴求句]」
🧪 核心成分：[核心成分]
👤 適用膚質：[適用膚質]
🎁 核心購買動機：[核心購買動機]
📝 使用方式：[使用方式]
⚠️ 合規備注：[合規備注]（若有）
🔗 Notion：[連結]
```

**列表輸出格式**：表格呈現，欄位至少包含「產品名稱、系列分類、售價、商品定位角色、適用膚質」，並附每筆 Notion 連結。

**比較輸出格式**：並列比較表，只呈現差異欄位，相同的欄位合併說明。

### Step 6：召回不完整的兜底

若 Step 4 過濾後符合條件的商品 **< 3 筆**，而使用者問的是整個系列或寬鬆條件，很可能是 search 召回不全。此時：

1. 主動再跑 1-2 組新關鍵字
2. 若仍不夠，在輸出末尾加一句：「以 semantic search 召回，可能有遺漏。建議到 Notion 對應的 view 直接核對：[最相關的 view 名稱與連結]」

### Step 7：主動提醒

查完後視情況補一句：
- 若使用者接下來可能要寫文案 → 若是社群貼文，提示「可以接著用 `kocskin-post-writer`」；若是其他長文案，提示「目前沒有對應 skill，可以直接告訴 Claude 你要的格式，產出後記得用 `kocskin-compliance-check` 過稿」
- 若合規備注有內容 → 把它拉到顯眼處，這對法規敏感的美妝/保健品很重要
- 若使用者問的條件剛好等同某個預建 view → 告訴他可以直接到 Notion UI 看

## 資料庫欄位速查

### Select 類欄位（單選）

| 欄位 | 選項 |
| --- | --- |
| `SKU狀態` | 在售 / 停售 / 開發中 |
| `商品定位角色` | 引流商品 / 主力商品 / 高單價商品 / 回購商品 |
| `產品系列` | 保濕 / 美白淡斑 / 抗老 / 清潔 / 防曬 / 面膜 / 保健食品 / 髮體護理 / 美妝配件 / 極光系列 / 香氛／生活 |
| `系列分類` | 3D全能系列 / 極光美白系列 / 玫瑰抗老系列 / 敏肌修護系列 / 基礎清潔系列 / 沐浴洗髮系列 / 彩妝系列 / KOC保健食品 / 贈品／加價購 / 夜間儀式系列 |

### Multi-select 類欄位（多選）

| 欄位 | 選項 |
| --- | --- |
| `適用膚質` | 全膚質 / 乾性肌 / 油性肌 / 混合肌 / 敏感肌 / 熟齡肌 / 一般肌 |
| `核心購買動機` | 乾燥修護 / 暗沉亮白 / 抗老緊緻 / 懶人簡化 / 信任品牌 / 促購活動 / 成分研究 / 控油清潔 / 健康保養 / 防曬彩妝 |

### Text / Number 類欄位

| 欄位 | 類型 | 說明 |
| --- | --- | --- |
| `產品名稱` | Title | 主鍵 |
| `售價` | Number | 新台幣 |
| `容量規格` | Text | 例：30ml、60顆、5片 |
| `主打賣點` | Text | 商品力長描述 |
| `主推訴求句` | Text | 一句話訴求 |
| `核心成分` | Text | 主要成分清單 |
| `目標客群` | Text | TA 圖像描述 |
| `使用方式` | Text | SOP |
| `廣告關鍵字` | Text | 含可用詞與避用詞 |
| `合規備注` | Text | 合規風險與替代用詞 |
| `系列定位句` | Text | 系列形象描述 |
| `備注` | Text | 其他補充 |
| `最後更新` | Last edited time | 自動 |

## 不要做的事

- ❌ 不要呼叫 `API-query-data-source` 或 `API-retrieve-a-data-source`（壞掉，見〈已知限制〉）
- ❌ 不要嘗試 `notion-fetch` 一個 `view://...` URL（不支援）
- ❌ 不要憑記憶回答商品資料（永遠以 Notion 即時資料為準）
- ❌ 不要寫入 Notion（本 skill 是唯讀查詢工具）
- ❌ 不要生成文案、slogan、廣告素材（社群貼文交給 `kocskin-post-writer`；其他長文案需手動產出，不要在這個 skill 內處理）
- ❌ 不要在輸出中提及停售商品，除非使用者明確要求
- ❌ 不要使用簡體字（Welson 偏好繁體中文）
- ❌ 保健食品資料回傳時不要腦補「治療/預防疾病」類效能描述，這違反台灣法規

## 變更歷史

- **v1.2 (2026-05-10)**：修正 v1.1 內 4 處對不存在的 `marketing:draft-content` / `marketing:content-creation` skill 的引用，改成 `kocskin-post-writer`（社群貼文）；明確標註 LP／廣告／Email／新聞稿目前無對應 skill 需手動處理；補上「手動產出後必過 `kocskin-compliance-check`」的提醒。
- **v1.1 (2026-05-10)**：實測確認 view fetch 不支援，新增 Step 2A loose search 枚舉策略；補上 8 個預建 view 清單作為 UI 導引；補上 5 月初發現的 SKU狀態 vs 內頁狀態欄位不同步問題提醒。
- v1.0：初版。
