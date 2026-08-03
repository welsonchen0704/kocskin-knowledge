---
name: kocskin-product-lookup
description: 查詢 KOCSKIN 克麗詩黛商品資料庫 V2（Notion），回答商品成分、售價、系列、定位、適用膚質、主打賣點等資訊。當使用者提到 KOCSKIN 任一商品名稱、系列（3D全能、極光美白、玫瑰抗老、敏肌修護、基礎清潔等）、或問「哪些商品適合 X 膚質」「XX 多少錢」「XX 的主要成分」時就要觸發。撰寫 KOCSKIN 文案、客服應答、廣告素材前也要先用這個 skill 查商品真實資料，避免憑空捏造。不要生成文案（交給 marketing:draft-content），只負責「查資料」。
---

# KOCSKIN 商品資料庫查詢（v1.3，2026-07-25 本機／雲端合併版）

這個 skill 封裝 KOCSKIN 克麗詩黛商品資料庫 V2 的查詢邏輯，讓使用者不用手動開 Notion 就能取得精準、結構化的商品資料。**主路徑是 SQL 查詢**（`notion-query-data-sources`），search + fetch 為語意模糊時的兜底路徑。

## 核心資訊

- **Notion Data Source ID**：`16d640a9-9f0b-441f-a670-821c6b4189ac`
- **Collection URL**（給 search 用）：`collection://16d640a9-9f0b-441f-a670-821c6b4189ac`
- **Database URL**：`https://www.notion.so/6e20bfbc8a9c4f1bb89f23f4b32b11ec`
- **總 SKU 數**：不寫死，一律用 SQL 即時計數（見下方範例）
- **欄位定義**：見 references/schema.md（2026-07-11 稽核快照，含裁定摘要；以 Notion 即時 schema 為準）

## 已知限制（非常重要，不遵守查詢會失敗）

目前環境中的 Notion MCP 工具分兩組，**只有其中一組可用**：

**✅ 可用**（使用這組；`mcp__` 前綴的連接器 ID 依環境而異，認工具後綴名即可）
- `mcp__a98ccb2c-079e-4bb9-b75c-cdea11c97c70__notion-query-data-sources`（SQL 全表查詢；2026-07-11 實測可用，**多條件篩選、清單、全庫查詢首選**）
- `mcp__a98ccb2c-079e-4bb9-b75c-cdea11c97c70__notion-search`
- `mcp__a98ccb2c-079e-4bb9-b75c-cdea11c97c70__notion-fetch`
- `mcp__a98ccb2c-079e-4bb9-b75c-cdea11c97c70__notion-create-pages`
- `mcp__a98ccb2c-079e-4bb9-b75c-cdea11c97c70__notion-update-page`

**❌ 不要用**（會回 400 `invalid_request_url`）
- `mcp__notion__API-query-data-source`
- `mcp__notion__API-retrieve-a-data-source`

為什麼：`mcp__notion__` server 的 route 表沒升級到 Notion 2025-09-03 新版 API，所有 `/v1/data_sources/*` 端點都壞了。這是已知問題，不是你的參數錯。

**查詢方式選擇**：多條件／清單／全表需求優先用 `notion-query-data-sources` 下 SQL（表名＝`"collection://16d640a9-9f0b-441f-a670-821c6b4189ac"`；multi-select 是 JSON 陣列字串、checkbox 用 `__YES__`／`__NO__`、`問答覆蓋數` 查不到、`最後審核日期` 用 `date:最後審核日期:start`）。語意模糊查詢再用 `notion-search` + `notion-fetch` 組合，見下方〈執行流程〉。

即時總數／狀態分佈（回答「共幾個 SKU」時用這個，不要背數字）：

```sql
SELECT "SKU狀態", COUNT(*) FROM "collection://16d640a9-9f0b-441f-a670-821c6b4189ac" GROUP BY "SKU狀態"
```

## 使用原則

### 1. 自動排除停售商品

**預設只回傳 `SKU狀態 = 在售` 的商品**。V2 **已存在停售列**（2026-07-13／14 起），在售／停售分佈一律用上方 SQL 即時查，不要引用歷史快照數字。

紅線品「氣墊粉餅補充蕊」「益生守護者 7 日體驗包」為**未開發未販售、根本不在 V2**（補充蕊在「Kocskin 商品成本表」DB），查不到是正常的。使用者問起時照實說明「未販售」即可；**任何對外輸出（貼文、LP、客服、廣告）都不得提及這兩支**。

`SKU狀態 = 停售` 的列只在使用者明確要求時納入，並清楚標示「已停售」；名單細節與「暫時停賣」特例（如 KOCS001）以 `kocskin-compliance-check/references/brand-rules.md`〈一、停售商品〉為正本。

為什麼：Welson 的品牌規範明令禁止對外提及停售商品，無意中帶出停售品可能導致行銷文案或客服回覆出問題。

### 2. 只讀不寫

本 skill **絕對不修改 Notion 資料**。如果使用者想更新商品資料，請他直接在 Notion 改，或另外明確請求修改。

### 3. 不生成文案

查完資料就報告資料。若使用者需要文案，提示他用 `marketing:draft-content` 或 `marketing:content-creation`，並把查到的商品資料當作素材。

為什麼：職責單一才容易穩定。把「事實查詢」和「創意生成」分開，避免資料錯了卻包在漂亮文案裡難以察覺。

## 執行流程（Search + Fetch 驗證 pattern）

多條件／清單／全表需求**優先用 `notion-query-data-sources` 下 SQL**（一次拿齊全欄位、不會漏召回）。語意模糊、只記得片段關鍵字時，才走傳統流程：**先 search 擴召回，再 fetch 驗證屬性**。

### Step 1：判斷查詢類型

| 類型 | 範例 | 建議策略 |
| --- | --- | --- |
| **單品查詢** | 「玫瑰精華的成分是什麼」 | Step 2→3 走一次 |
| **多條件篩選** | 「所有敏感肌可用的主力商品」 | Step 2 跑多組關鍵字 → Step 3 合併驗證 |
| **系列/分類清單** | 「極光美白系列有哪些」 | Step 2 用系列名 + 典型成分關鍵字 → Step 3 驗證 `系列分類` |
| **商品比較** | 「A 和 B 的差異」 | 直接 fetch 兩支商品 |
| **組合推薦** | 「乾性肌 1500 元預算的保養組合」 | Step 2 篩符合條件 → Step 3 驗證 → 再主動組合建議 |

### Step 2：用 `notion-search` 擴召回

挑 2-4 個關鍵字，分別呼叫 `notion-search`：

```
notion-search(
  query: "<關鍵字>",
  data_source_url: "collection://16d640a9-9f0b-441f-a670-821c6b4189ac",
  page_size: 25,
  filters: {}
)
```

關鍵字怎麼挑：
- **系列查詢** → 用系列名稱（如「玫瑰抗老」）、**系列定位句內的特色詞**（如「玫瑰幹細胞」「PDRN」）、**典型核心成分**
- **膚質/需求** → 用膚質名（如「敏感肌」「乾性肌」）、需求詞（如「保濕」「美白」「抗老」）
- **商品名稱** → 直接用名稱片段

為什麼要多組：`notion-search` 是 **semantic search**，單一關鍵字可能漏掉部分商品。多組關鍵字聯集才有完整召回。詳見 [references/query-patterns.md](references/query-patterns.md)。

### Step 3：用 `notion-fetch` 驗證屬性

對 Step 2 的每個候選 page id 呼叫：

```
notion-fetch(id: "<page_id>")
```

取得完整 properties 後，**在程式層面**驗證下列條件：
- `SKU狀態 == "在售"`（預設必要）
- 任務指定的過濾條件（如 `系列分類 == "玫瑰抗老系列"`、`適用膚質 contains "敏感肌"`、`售價 <= 1500`）

篩掉不符合的，保留符合的。

### Step 4：整理輸出

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

### Step 5：召回不完整的兜底

若 Step 3 驗證後符合條件的商品 **< 3 筆**，而使用者問的是整個系列或寬鬆條件，很可能是 search 召回不全。此時：

1. 主動再跑 1-2 組新關鍵字（從 references/query-patterns.md 附錄找）
2. 若仍不夠，在輸出末尾加一句：「本次以 semantic search 召回，可能有遺漏，建議到 Notion [📋 系列清單總覽 view](https://www.notion.so/6e20bfbc8a9c4f1bb89f23f4b32b11ec) 核對。」

### Step 6：主動提醒

查完後視情況補一句：
- 若使用者接下來可能要寫文案 → 提示「要產文案的話可以接著用 `marketing:draft-content`」
- 若合規備注有內容 → 把它拉到顯眼處，這對法規敏感的美妝/保健品很重要

## 資料庫欄位速查

完整欄位定義在 [references/schema.md](references/schema.md)。常用欄位：

| 欄位 | 類型 | 主要值 |
| --- | --- | --- |
| `SKU狀態` | select | 在售 / 停售 / 開發中 |
| `商品定位角色` | select | 引流商品 / 主力商品 / 高單價商品 / 回購商品 |
| `產品系列` | select（功能分類） | 保濕 / 美白淡斑 / 抗老 / 清潔 / 防曬 / 面膜 / 保健食品 / 髮體護理 / 美妝配件 / 香氛／生活 / 精華（2026-07-11 新增）。「極光系列」選項已退役——極光三品已歸「美白淡斑」 |
| `系列分類` | select（品牌線） | 3D全能系列 / 極光美白系列 / 玫瑰抗老系列 / 敏肌修護系列 / 基礎清潔系列 / 沐浴洗髮系列 / 彩妝系列 / KOC保健食品 / 贈品／加價購 / 夜間儀式系列 |
| `AI是否可推薦` | checkbox | AI 導購白名單開關 |
| `宣稱風險等級` | select | Low / Medium / High |
| `合規可用說法`、`禁用說法` | text | 產文案前必查的白名單／黑名單 |
| `AI可引用商品摘要` | text | AI 可直接引用的安全摘要 |
| `適用膚質` | multi-select | 全膚質 / 乾性肌 / 油性肌 / 混合肌 / 敏感肌 / 熟齡肌 / 一般肌 |
| `核心購買動機` | multi-select | 乾燥修護 / 暗沉亮白 / 抗老緊緻 / 懶人簡化 / 信任品牌 / 促購活動 / 成分研究 / 控油清潔 / 健康保養 / 防曬彩妝 |
| `售價` | number | 新台幣 |

## 不要做的事

- ❌ 不要呼叫 `mcp__notion__API-query-data-source` 或 `API-retrieve-a-data-source`（壞掉，見〈已知限制〉）
- ❌ 不要憑記憶回答商品資料（永遠以 Notion 即時資料為準）
- ❌ 不要寫入 Notion（本 skill 是唯讀查詢工具）
- ❌ 不要生成文案、slogan、廣告素材（交給 marketing 系列 skill）
- ❌ 不要在輸出中提及停售商品，除非使用者明確要求
- ❌ 不要使用簡體字（Welson 偏好繁體中文）
- ❌ 保健食品資料回傳時不要腦補「治療/預防疾病」類效能描述，這違反台灣法規
