# KOCSKIN Skills — ChatGPT 移轉包（2026-09-15）

來源：Claude 帳號 skill 現行版（= `~/kocskin-knowledge/skills`，含 8/8 美白更正、9/14–15 修訂）。
格式：Agent Skills 開放標準（`SKILL.md` + `references/` + `scripts/`），ChatGPT 直接相容。

## 上傳方式（ChatGPT Business／Enterprise／Edu）

ChatGPT 網頁或桌面版 → **Skills → Create → Upload from your computer**，一次上傳一個 skill。
用 `zips/` 裡的檔（每支一個 ZIP，skill 資料夾在 ZIP 根層）。免費／Plus／Pro 目前未開放 skills 上傳。

上傳後 ChatGPT 會掃描，可能標「Needs Review」；本包無可執行的網路呼叫（visual-generator 的 python 腳本只在有憑證時才會連 Cloudinary），若被擋請先傳其他 8 支。

## 建議順序

1. `kocskin-compliance-check`（無工具依賴，先傳先用）
2. `kocskin-product-lookup`（需先在 ChatGPT 連接 Notion connector 並授權「商品資料庫 V2」）
3. `kocskin-post-writer`、`kocskin-threads-writer`
4. 其餘依需要

## 每支 SKILL.md 開頭都加了「⚠️ ChatGPT 版平台對照」區塊

規則、紅線、憲章 R1–R7 全部照舊，只換「工具怎麼叫」。重點差異：

| Claude 環境 | ChatGPT 對應 |
|---|---|
| Notion MCP SQL 查詢（`notion-query-data-sources`） | Notion connector 搜尋＋逐頁讀取；**無 SQL**，計數以實際讀到為準 |
| fresh subagent 獨立審查 | 開新對話跑 compliance-check，只審不改 |
| Buffer／Cloudinary／Notion 寫入 | 無對應 connector → 不寫、不排程，輸出操作清單給 Welson |
| Claude in Chrome 瀏覽器（91app） | ChatGPT Agent 模式，未實跑驗證 |
| Cloudinary MCP 產圖（visual-generator） | 只出 prompt（路徑 C），正式圖由 Welson 到 console 產 |
| pptxgenjs（ad-wireframe） | python-pptx |
| 本機資料夾路徑 | 上傳檔案到對話 |

## 維護原則

兩邊都改會分岔。建議：**只改 Claude 帳號版／本機 repo**，要更新 ChatGPT 時重跑打包（保留「平台對照」區塊）再重傳。
