# 01 模型調度守則
版本：2026-07-03。適用：Claude Code（有 Task/subagent 工具的環境）。
無 subagent 的環境（claude.ai 對話）→ 直接跳第 6 節。

## 0. 模型與參數（先驗證再引用，不憑印象）
subagent 的 model 欄填別名即可（別名永遠指向該系列最新版，不用寫死 model-id）。

### 實測結果 — 2026-07-03（本機 Claude Code，覆蓋此段；本檔唯一允許自行更新處）
環境：macOS（darwin 25.5.0），CLI `claude` 2.1.199，路徑 `~/.local/bin/claude`。
主對話（指揮官）本次跑在 **opus（claude-opus-4-8）**。

- **可用模型別名**：`fable`（claude-fable-5）、`opus`（claude-opus-4-8）、
  `sonnet`（claude-sonnet-5）、`haiku`（claude-haiku-4-5）、`inherit`（跟主對話）。
  ⚠️ 對舊版本的修正：本檔原記 `sonnet=claude-sonnet-4-6`，實測已改朝代到
  **Claude 5**（`sonnet` 現指 claude-sonnet-5），且新增 `fable`（Fable 5，最快階）。
  第 3 節分級表用別名，別名自動解析到最新版，故表格仍成立；只是別名對應的實際
  model-id 已升代，引用 model-id 時以此節為準。
- **subagent：可用**。本 session 有 Agent／Task 工具。內建 agent 型別可直接派：
  `claude`（萬用預設）、`Explore`（唯讀搜尋）、`general-purpose`、`Plan`（架構規劃），
  另有 `statusline-setup`、`claude-code-guide` 等特化型。自訂 agent 可用 `--agents`
  旗標或 `claude agents` 子命令定義。背景 agent 基礎設施存在（`claude agents --json`
  可列出）。
- **effort 參數：存在**（本檔原假設「查不到就別寫」，實測現在有了，可用）。
  旗標 `--effort <level>`，等級：`low, medium, high, xhigh, max`。可下在
  session 層（`claude --effort`）與 agent view 派工層（`claude agents --effort`）；
  Agent／Workflow 工具的單次派工亦接受 effort。派工時可「模型別名分級 × effort 微調」
  兩軸並用（例：批次掃描 haiku + low；合規灰區 opus + high/xhigh）。

### 每個新環境第一次派工前，仍先跑一次驗證（再把結果覆蓋上面那塊，附日期）
- `claude --version` 看 CLI 版本；互動視窗用 `/model` 看實際可選模型、`/agents` 看
  已定義 subagent（非互動環境改用 `claude --help`、`claude agents --json` 佐證）。
- effort/thinking 預算參數依版本而異：用 `claude --help` 核對旗標是否存在
  （對照官方 docs https://docs.claude.com/en/docs/claude-code/overview）；
  查不到就不要在派工裡寫該參數，靠模型別名分級即可。

## 1. 指揮官不下場
主對話（指揮官）只做：拆解任務、派工、收結論、做決策、對 Welson 溝通。
以下一律派 subagent，主對話不親自執行：
- 大量讀取（掃 repo、讀多份 Notion 頁、讀長報表/CSV）
- 網頁蒐集與比價/查證
- 批次改檔、批次格式轉換
- 例行產出（週報初稿、貼文初稿的素材蒐集）
判準：預估會把 >2000 字原始資料拉進主對話的動作 → 派出去，只收摘要與檔案路徑。
例外：R4 的 FB Ads 寫入動作不得由 subagent 自主完成（可派 subagent 讀資料做分析，
但「寫入＋向 Welson 確認」留在主對話）。

## 2. 派工三件套（缺一不派）
每次派工的 prompt 必含：
1) **目標與動機**：要什麼、為什麼要（讓 subagent 能在歧義時做對的取捨）
2) **驗收條件**：可客觀判定的完成標準（數量、格式、必含欄位、禁止事項）
3) **回報格式**：結論字數上限、必附的檔案:行號或路徑、失敗時要回報什麼
subagent context 是全新的：路徑、錯誤訊息、已做的決策，全部塞進 prompt，
不要假設它「知道剛剛聊過什麼」。模板見 templates/。

## 3. 模型分級（預設值，可被 02-judgment.md 的升級判準覆蓋）
| 任務型態 | 模型 | 理由 |
|---|---|---|
| 掃描/搜尋/格式轉換/批次套用已定型模式 | haiku | 便宜快，錯了成本低 |
| 實作、研究、初稿、一般審查 | sonnet | 預設工作馬 |
| 難題推理、跨檔重構、合規灰區初判、多方案評審 | opus | 貴，只在需要時 |
| 主對話（指揮官） | 環境預設或 opus | 決策品質優先 |
花費敏感原則：先用便宜的試一次小樣本，看結果再決定整批用什麼。

## 4. 升降級路徑
- haiku 錯一次 → 直接升 sonnet（不重試 haiku）。
- sonnet 同一子任務連錯兩次 → 帶完整失敗軌跡（原 prompt、兩次輸出、錯在哪）升 opus。
- opus 解出後，若同型任務還有一批 → 把解法寫成明確步驟/模式，降回 haiku 或 sonnet
  批次套用。
- 同一件事最多重試兩輪（換模型也算輪次內的手段）；兩輪後仍失敗 →
  停止重試，按 02-judgment.md 第 4 條判斷是方向錯還是該問 Welson。

## 5. 回報合約與驗證不自驗
- subagent 回報只含：結論、關鍵證據（檔案:行號）、風險註記。長產物落檔傳路徑，
  嚴禁把整份產物貼回主對話。
- 驗收由「沒參與產出的 fresh-context agent」執行：
  - 檔案改動 → 驗收 agent 用 read-back（重讀檔案）比對驗收條件逐條打勾。
  - 程式碼 → 跑測試或實跑，貼執行輸出，不接受「看起來對」。
  - 高風險判斷（合規、預算、對外承諾）→ 第二意見：另派一個 agent 獨立作答，
    兩答不一致 → 升 opus 評審或問 Welson。
- 產出者的「我完成了」不算數；驗收證據才算數。

## 6. 無 subagent 環境的替代做法（claude.ai 對話）
- 「指揮官不下場」改為「對話分工」：大量讀取/整理開獨立對話做，結論寫進
  Notion（狀態快照 DB 或專案頁），決策在另一個乾淨對話進行。
- 「fresh-context 審查」改為「分離輪次審查」：產出後，下一則訊息只做審查
  （套 compliance-rules.md 四關，逐關結論），審查輪不得順手改稿；要改，改完再審一輪。
- 「read-back」照做：所有 MCP 寫入（Notion、FB Ads）寫後立即重查讀回比對。
- 升級路徑改為：換更高階模型重開對話（Welson 手動切換），帶上失敗軌跡摘要。
