---
name: kocskin-post-writer
description: 為 KOCSKIN 克麗詩黛撰寫 Facebook、Instagram、Threads 三大社群平台的貼文，內建品牌語氣（親切、專業、有溫度、不誇大、不焦慮）、4 種內容類型比例（商品價值 40% / 教育 30% / 見證品牌 20% / 促銷導購 10%）、週一三五日發文節奏、合規審查。當使用者要寫 / 撰寫 / 產出 / 生成 / 草擬 FB 貼文、IG 貼文、Threads 貼文、脆、社群貼文、粉絲頁貼文、限時動態，或說「來寫一篇」「推 XX 商品」「本週還缺貼文」時就要觸發。預設同時產出 FB + IG + Threads 三版，除非使用者指定只要某個平台。負責完整流程：查商品資料 → 套內容範本 → 產文 → 自動合規審查。不要用於 LP 文案、廣告素材、Email、新聞稿（這些目前無對應 skill，需手動產出後過 kocskin-compliance-check）。
---

# KOCSKIN Facebook / Instagram 貼文生成器

為 KOCSKIN 社群貼文把關品質、速度、合規、品牌一致性。你（或團隊的行銷專員）只要丟主題，這個 skill 把後面的流程都串好。

## 核心流程（5 步）

使用者丟需求後，依序執行：

### Step 1：釐清需求

問使用者（或從對話猜測）：
1. **主推商品**（或主題）— 例如「玫瑰超導安瓶」「保濕保養概念」
2. **目標平台** — FB / IG / Threads，**預設同時產三版**，除非使用者明說只要某個
3. **今天是週幾 / 要發哪天** — 影響節奏判斷（見 [references/weekly-rhythm.md](references/weekly-rhythm.md)）
4. **本週已發哪幾篇、什麼類型** — 影響類型比例平衡
5. **是否有特定檔期 / 活動**（母親節、週年慶等）

若使用者沒給完整資訊，**先給預設建議再讓他調整**，不要把所有問題拋給他。

### Step 2：決定內容類型

依照 40/30/20/10 比例，從下列四類挑一：

| 類型 | 占比 | 目標 | 範例切入 |
| --- | --- | --- | --- |
| **商品價值型** | 40% | 傳達商品核心賣點、成分、適用族群 | 「這支精華為什麼特別？成分拆解給你看」 |
| **教育型** | 30% | 保養知識、使用教學、膚質判別 | 「敏感肌到底是什麼？3 種常見誤解」 |
| **見證品牌型** | 20% | 使用者見證、品牌故事、幕後 | 「消費者分享｜小雅的 14 天紀錄」「我們為什麼做 MIT」 |
| **促銷導購型** | 10% | 檔期活動、折扣、新品 | 「週年慶滿千折百」（這是最常過度使用的類型，嚴格控制在 10%） |

**智能判斷**：若本週促銷型已 > 10%，即使使用者要求促銷，要主動建議「先補教育型或見證型平衡」。

### Step 3：查商品真實資料

若主題有特定商品，**一定用 `kocskin-product-lookup` 查 Notion**，取得：
- 產品名稱、售價、容量規格
- 核心成分、主打賣點、主推訴求句
- 適用膚質、目標客群
- **合規備注**（非常重要，直接影響文案用字）

**不要憑記憶或推測商品資料**。記憶會錯、資料會過時。

### Step 4：撰寫文案

依照選定的內容類型，參考 [references/content-types.md](references/content-types.md) 的結構範本：

1. **標題 / 第一行**（FB 頭 3 行決定開展率、IG 第一行決定滑掉率、Threads 第一行決定是否引發討論）
2. **主文**（核心訊息 + 3-5 個賣點或論述）
3. **CTA**（行動呼籲：連結、優惠碼、私訊詢問、看留言、引發討論）
4. **Hashtag**（FB 3-5 個，IG 15-30 個，Threads 3-8 個）

平台差異見 [references/platform-specs.md](references/platform-specs.md)。**三個平台不能一貼三用**，第一行、斷行、hashtag 都有各自套法。

**必守品牌語氣**：
- ✅ 親切、專業、有溫度（像懂成分的閨蜜分享）
- ✅ 具體、可證據化（成分、實驗、消費者 N 字樣的見證）
- ❌ 焦慮行銷（「再不用你就完了」「皮膚已經壞光光」）
- ❌ 誇大神化（「神級」「逆天」「奇蹟」）
- ❌ 過度口語（「姊妹們快衝」「真的 TM 好用」）
- ❌ 過度正式（「本公司隆重推出」）

好 / 壞語氣範例見 [references/voice-examples.md](references/voice-examples.md)。

### Step 5：合規自動審查（必做，不可省略）

**文案產出後，自動呼叫 `kocskin-compliance-check`** 跑一次審查。

- 若出現 **Critical** 或 **High** 問題 → 修正後再輸出給使用者
- 若只有 **Medium** 或 **Low** → 輸出給使用者並附審查結果，讓他決定要不要微調

為什麼自動串接：人的自檢率會下降，但 skill 不會累。這是守門機制。

## 輸出格式

```
📱 KOCSKIN [主推商品 / 主題] 貼文草稿

━━━━━━━━━━━━━━━━━━
🎯 類型：[商品價值 / 教育 / 見證品牌 / 促銷導購]
📅 建議發佈：[週X 2026-XX-XX]
📊 本週內容比例追蹤：商品價值 X / 教育 X / 見證 X / 促銷 X

━━━━━━━━━━━━━━━━━━
## Facebook 版本（250-500 字）

[正文，段落式]

[Hashtag 3-5 個]

━━━━━━━━━━━━━━━━━━
## Instagram 版本（80-200 字）

[第一行 hook]
.
.
.
[主文，較短、大方斷行]

[Hashtag 15-30 個]

━━━━━━━━━━━━━━━━━━
## Threads 版本（50-150 字）

[引發討論的第一行 hook：問題、觀點或反差]

[主文，口語感、不用太正式結構]

[CTA：邀請回覆 / 分享經驗，不是導購]

[Hashtag 3-8 個]

━━━━━━━━━━━━━━━━━━
## ⚖️ 合規審查結果

[compliance-check 輸出摘要]
總體評級：🟢 通過 / 🟡 建議調整

━━━━━━━━━━━━━━━━━━
## 💡 給使用者的備注

- 搭配哪張商品圖 / 情境圖
- 要不要加到哪個活動 / 限動
- 是否需要小燕出鏡（見證品牌型常用）
- Threads 發布後 1-2 小時可回覆留言延伸討論（這個平台吃互動）
```

## 觸發情境

下列對話都要觸發本 skill：

- 「幫我寫玫瑰超導安瓶的 FB 貼文」
- 「來一篇關於敏感肌保養的教育文」
- 「本週還缺一篇，你決定主題」
- 「週三要發什麼？」
- 「IG 貼文推 B5 面膜」
- 「寫一個見證型的貼文」

不觸發的情境（目前的處理方式）：
- LP 文案 → **無對應 skill**，手動寫 → 過 `kocskin-compliance-check`
- 廣告素材（Meta / Google） → **無對應 skill**，手動寫 → 過 `kocskin-compliance-check`（廣告審查特別嚴，務必跑）
- Email 電子報 → **無對應 skill**，手動寫 → 過 `kocskin-compliance-check`
- 新聞稿 → **無對應 skill**，手動寫 → 過 `kocskin-compliance-check`
- 只審查文案沒要生成 → `kocskin-compliance-check` 直接跑

## 依賴的其他 skill

- **`kocskin-product-lookup`** — 查商品真實資料（售價、成分、合規備注）
- **`kocskin-compliance-check`** — 產出後守門

這三個 skill 組成 KOCSKIN 內容生產鏈：查 → 寫 → 審。任何一環斷掉都會影響品質。

## 內部參考檔

- [references/content-types.md](references/content-types.md) — 4 種內容類型的詳細結構範本與範例
- [references/platform-specs.md](references/platform-specs.md) — FB vs IG 格式規範、字數建議、hashtag 策略
- [references/voice-examples.md](references/voice-examples.md) — KOCSKIN 好 / 壞語氣對照，避免抽象指令靠具體例子對齊
- [references/weekly-rhythm.md](references/weekly-rhythm.md) — 週一三五日節奏、類型比例追蹤、檔期搭配邏輯

## 不要做的事

- ❌ 不要憑記憶寫商品成分 / 售價（先查 `kocskin-product-lookup`）
- ❌ 不要跳過合規審查（每篇都要跑 `kocskin-compliance-check`）
- ❌ 不要一次產出多篇卻沒控制類型比例
- ❌ 不要讓促銷導購型超過 10%
- ❌ 不要寫進停售商品（氣墊粉餅補充蕊、益生守護者 7 日體驗包）
- ❌ 不要把玫瑰超導全能安瓶歸入 PDRN 線（它是山茶花外泌體）
- ❌ 不要使用「李燕」稱呼執行長，用「小燕」或「執行長小燕」
- ❌ 不要用簡體字
- ❌ 不要擅自產出 LP、Email、廣告素材、新聞稿文案（這些 skill 目前不存在；告訴使用者「post-writer 只負責社群貼文，這類長文案請開新對話手動處理，產出後務必過 kocskin-compliance-check」）

## 變更歷史

- **v1.1 (2026-05-10)**：移除 4 處對不存在 skill 的引用（`marketing:draft-content`、`marketing:email-sequence`），改為明確標註「目前無對應 skill，手動產出後務必過 `kocskin-compliance-check`」。修正 frontmatter description、不觸發情境列表、不要做的事三個區段。
- v1.0：初版。
