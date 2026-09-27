---
name: kocskin-visual-generator
description: "用 Cloudinary Image Generation（nano-banana / flux / recraft / gpt-image / ideogram 等模型）規劃並產出 KOCSKIN／KOC 貼文或廣告用的 AI 視覺素材，主路徑為 Cloudinary MCP 連接器，無連接器時才退回 python 腳本。當 Welson 說「幫我生成素材」「AI 產一張廣告圖」「用商品照生情境圖」「幫我出幾版視覺概念」「re-stage 商品」時觸發。只負責「規劃視覺概念 + 產圖」，文案由 kocskin-post-writer／kocskin-threads-writer 負責，商品事實由 kocskin-product-lookup 負責，對外文字內容一律仍要過 kocskin-compliance-check。"
---

# KOCSKIN AI 視覺素材生成器

版本：2026-09-14 v1.1（Welson 同意主路徑改走 Cloudinary MCP；2026-08-25 v1.0 建立）

## 0. 這個 Skill 做什麼 / 不做什麼

做：規劃 2-3 組視覺概念（構圖、風格、對應 prompt），呼叫 Cloudinary Image
Generation 產出實際圖片，交給 Welson 挑選，並記錄每張圖的 prompt/model
方便回溯或重新生成。

不做：不生成貼文文案本身（找 kocskin-post-writer / kocskin-threads-writer）、
不查商品資料（找 kocskin-product-lookup）、不做語意合規審查（找
kocskin-compliance-check）、不負責 FB Ads 素材上架與投放設定（那是
01-dispatch.md R4 的範圍，AI 生的圖只是素材來源之一）。

## 1. 產圖路徑（先判斷用哪一條）

| 路徑 | 條件 | 憑證 | 網域白名單 |
|---|---|---|---|
| **A. Cloudinary MCP（主路徑，預設）** | session 內有 `Cloudinary` 連接器（工具後綴 `generate-image`、`generate-image-from-images`；`mcp__` 前綴依環境而異，認後綴即可） | 不需要——連接器已授權 | 不需要 |
| B. python 腳本（備援） | 沒有 Cloudinary 連接器，但有 Bash | 每次向 Welson 索取，用完即丟（見第 2 節） | 需要 `api.cloudinary.com`＋`res.cloudinary.com` |
| C. 只出 prompt | 兩者皆無（純 claude.ai 對話且無連接器） | — | — |

**判斷順序：先找連接器 → 有就走 A，不要問 Welson 要憑證。** 只有 A 不可用才走 B；走 B 前先跟 Welson 說明「本 session 沒有 Cloudinary 連接器，改走腳本，需要憑證」。

### 路徑 A：MCP 工具用法

**純文字生圖** `generate-image`：

```json
{"request": {
  "prompt": "A minimalist skincare serum bottle on wet marble surface, soft morning window light, editorial product photography, shallow depth of field",
  "model": {"family": "nano-banana", "tier": "premium"},
  "image_size": {"aspect_ratio": "1:1", "resolution": "1K"},
  "format": "jpeg",
  "target": {"target_type": "managed_asset", "public_id": "koc_gen/KOCxxx_concept1_20260914"}
}}
```

**參考圖生圖** `generate-image-from-images`（有實拍商品照時優先）：

```json
{"request": {
  "prompt": "Place the product from [1] on a marble kitchen counter with soft morning light, lifestyle photography style. Keep the bottle, label and colors exactly as in [1].",
  "reference_images": [{"source_type": "url", "url": "https://res.cloudinary.com/s55rhpbr/image/upload/<真實商品照 public_id>.jpg"}],
  "model": {"family": "nano-banana", "tier": "premium"},
  "image_size": {"aspect_ratio": "1:1", "resolution": "1K"},
  "format": "jpeg",
  "target": {"target_type": "managed_asset", "public_id": "koc_gen/KOCxxx_restage1_20260914"}
}}
```

- `reference_images` 最多 4 張；可用 `{"source_type":"managed_asset","asset_id":"..."}` 指 Cloudinary 內既有素材（asset_id 用 `search-assets` 或 `get-asset-details` 查）。
- `model.family`：`nano-banana`（通用，預設）／`flux`（寫實）／`recraft`（向量插畫，只收 1 張參考圖）／`gpt-image`（行銷主視覺）／`ideogram`（文字渲染，僅 text_to_image）。`tier` 預設 `standard`，正式素材用 `premium`。
- `image_size` 只收 `1:1`／`16:9`／`9:16`／`4:3`／`3:4`；FB/IG 直式 4:5 或其他比例，先生 1:1 或 3:4，再用 Cloudinary URL 參數 `c_fill,g_auto,w_1080,h_1350` 動態裁（見 post-writer〈依平台切尺寸〉）。
- `target.public_id` 一律命名 `koc_gen/<SKU或主題>_<用途>_<YYYYMMDD>`，方便日後在素材庫索引與追溯。**不要用 `temporary`**——會過期，Welson 挑完圖就找不到。
- 回傳的 `secure_url` 即可直接填進 Notion 素材圖庫或貼文列；同時記下 `seed` 供重生。
- 每次呼叫後回報 `limits.addons_quota`（若回傳有），接近上限主動提醒。

### 路徑 B：python 腳本（備援）

只在無連接器時使用。用法、憑證規則、白名單見第 2、4 節，與 v1.0 相同。

## 2. 憑證處理（僅路徑 B 適用；硬性規定，不得偷懶簡化）

- Cloudinary API 憑證（API Key / API Secret / Cloud name）**不得**寫死在
  這個 Skill 的任何檔案、任何程式碼、任何暫存設定裡。
- 走腳本產圖前，先跟 Welson 要這次要用的 Key / Secret / Cloud name，用環境
  變數帶入 `scripts/generate_image.py`，用完即丟，不落地保存、不寫進對話
  紀錄以外的任何檔案。
- 這是 Welson 2026-08-25 明確拍板的處理方式，非經 Welson 同意不得改成「寫死
  憑證方便之後不用要」這種簡化版本。
- 路徑 A 走連接器授權，不經手憑證，因此不適用本節——這是 Welson 2026-09-14
  同意的例外。

```bash
export CLOUDINARY_API_KEY="Welson 這次提供的值"
export CLOUDINARY_API_SECRET="Welson 這次提供的值"
export CLOUDINARY_CLOUD_NAME="s55rhpbr"   # 沒有另外說明就用這個
```

路徑 B 的網域白名單（Cowork 雲端環境）：若跑腳本出現 `Tunnel connection
failed: 403 Forbidden`，確認 Welson 帳號 **Settings → Capabilities → Code
execution and file creation → Domain allowlist** 有 `api.cloudinary.com`
（呼叫 API）與 `res.cloudinary.com`（下載圖片）兩個網域，缺一不可。

## 3. 觸發後的標準流程

1. **判斷路徑**：依第 1 節找連接器；有就走 A，不索取憑證。
2. **商品事實查核（若素材涉及特定 SKU）**：依 CLAUDE.md R1，先用
   kocskin-product-lookup 查 Notion 商品資料庫 V2 該 SKU 頁面的合規卡，取得
   真實品名、賣點、外觀特徵、以及 ❌禁用／✅可用 清單。**不得**憑記憶或推測
   捏造商品外觀或賣點去寫 prompt。若素材是純氛圍/情境圖（不涉及特定商品外觀
   或功效主張），可跳過這步。
3. **停售品檢查**：依 R5，氣墊粉餅補充蕊、益生守護者7日體驗包絕不生成任何
   相關素材；注意易混淆的在售品「KOC 益生守護者益生菌」「晶燦白皙氣墊粉餅」
   不要誤判成停售品。完整停售名單以 compliance-check brand-rules〈一〉＋V2
   `SKU狀態` 即時值為準。
4. **找實拍參考圖**：查素材圖庫 `collection://a924b6bd-c492-4328-93ea-3d036229301f`
   該 SKU 的「實拍」或「白底」圖網址，作為 image_to_image 的 reference。
5. **規劃視覺概念**：依用途（FB/IG 貼文 vs 廣告素材 vs LP 圖）產出 2-3 組
   概念，每組寫清楚：
   - 構圖與氛圍描述（給人看的）
   - 對應的 prompt（英文，具體描述構圖/光線/材質/情緒，避免抽象形容詞堆疊）
   - 建議模型與 aspect_ratio（見第 1 節對照）
   - **有實拍商品照可用時，優先用 image_to_image + reference_images**，
     只指示「換場景/換背景/換光線」，並在 prompt 明寫「keep the product,
     label and colors exactly as in [1]」，不要求 AI 改變商品本身外觀，避免
     產出跟真實商品不符的圖（對應 CLAUDE.md「不得竄改商品資訊」原則）。沒有
     實拍照才用 text_to_image 純生成情境圖，且要讓 Welson 知道這是「AI 想像
     的情境，非商品實拍」。
6. **產圖**：每組概念產一張；記錄 public_id／secure_url／model／seed／prompt
   （路徑 A 記在回覆裡；路徑 B 由 manifest.json 自動記）。
7. **文字/主張把關**：若生成的素材上有疊加文字或隱含功效主張（例如「美白」
   「修復」等字樣），這段文字內容要另外過 kocskin-compliance-check 四關，
   絕不能因為「只是圖」就跳過 R2 的審查管道。純視覺氛圍圖（無文字主張）
   仍需 Welson 本人確認是否符合品牌調性再使用。
8. **交付**：把生成圖片的 secure_url＋對應 prompt/model/seed 一起給 Welson，
   方便他選圖或要求微調重生。Welson 選定後，若要進素材圖庫，另建一列（類型
   填「AI實景」、狀態「可用」）。

## 4. 技術細節：python 腳本（路徑 B）

Base URL：`https://api.cloudinary.com/v2`，Basic Auth（API Key:Secret）。

- 純文字生圖：`POST /generate/{cloud_name}/text_to_image`
- 參考圖生圖：`POST /generate/{cloud_name}/image_to_image`（reference_images
  最多4張，可用 `managed_asset`(asset_id) 或外部 `url`）

用本包的 `scripts/generate_image.py` 執行，範例：

```bash
# 純文字生圖
python3 scripts/generate_image.py \
  --prompt "A minimalist skincare serum bottle on wet marble surface, soft morning window light, editorial product photography, shallow depth of field" \
  --model-family nano-banana --model-tier premium \
  --aspect-ratio 1:1 --resolution 1K \
  --out ./output/concept_1.png

# 參考圖生圖（用真實商品照換場景）
python3 scripts/generate_image.py \
  --prompt "Place the product from [1] on a marble kitchen counter with soft morning light, lifestyle photography style" \
  --ref-url "https://res.cloudinary.com/.../真實商品照.jpg" \
  --aspect-ratio 1:1 \
  --out ./output/concept_2.png
```

回應會包含 `limits.addons_quota`（本次用量與剩餘額度）——**接近額度上限時
要主動提醒 Welson**，不要悶著頭一直生到爆額度。

## 5. 環境分支

- **有 Cloudinary 連接器（Cowork／claude.ai／Claude Code 皆可能）**：路徑 A。
- **無連接器但有 Bash（Claude Code 本機、部分 Cowork）**：路徑 B。
- **無連接器也無 Bash（純 claude.ai 對話）**：路徑 C——只做「規劃視覺概念」，
  把 prompt 整理好給 Welson，由 Welson 自己到 Cloudinary console
  （`console.cloudinary.com` → Image Generation）貼上執行。

## 6. 常見錯誤（照踩坑經驗，避免重蹈覆轍）

- 有連接器卻還跟 Welson 要 API Key → 多此一舉，先找連接器。
- 路徑 A 用 `target_type: temporary` → 圖會過期，一律 `managed_asset` 並命名 public_id。
- 路徑 A 要求 4:5 或非支援比例 → 400；先生支援比例再用 URL 參數裁。
- `recraft` 給超過 1 張參考圖 → 400。
- 路徑 B 被 `Tunnel connection failed: 403` 卡住 → 查第 2 節兩個網域是否都已加入白名單；只加 `api.cloudinary.com` 沒加 `res.cloudinary.com` 會 API 成功但下載失敗（2026-08-25 實測）。
- 沒讀商品合規卡就自己編商品賣點寫進 prompt → 違反 R1，禁止。
- 路徑 B 為了方便把憑證寫進腳本或設定檔存起來 → 違反 Welson 拍板的憑證處理原則，禁止。
- 生成圖上有文字/主張卻略過 compliance-check 直接發布 → 違反 R2，禁止。
- 對停售品（R5）生成素材 → 禁止，發現要立刻停止並告知 Welson。
- 額度用完才發現 → 每次呼叫後檢查用量並主動回報。

## 更新紀錄

- 2026-08-25 v1.0：建立，python 腳本＋每次索取憑證。
- 2026-09-14 v1.1：Welson 同意主路徑改走 Cloudinary MCP 連接器（`generate-image`／`generate-image-from-images`），不經手憑證、不需網域白名單；腳本降為備援，憑證規則僅適用備援路徑。新增 public_id 命名慣例、比例限制與 reference 用法。