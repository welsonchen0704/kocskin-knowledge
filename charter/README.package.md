# README：KOCSKIN AI 制度包 v2.0（2026-07-03）

## 這包是什麼
一次 Fable 5 session 產出的長期制度，目標：讓之後每個較弱模型的 session
自動變強。核心設計：把「模型自覺」換成「結構強制」——順序不可重排的合規管道、
寫後必讀回、驗收換人做、事實只有一個家（V2）。

## 安裝（Welson 三步，約 10 分鐘）
1. **Claude Code**：整個 `kocskin-ai-system/` 資料夾放進專案根目錄，
   把 `CLAUDE.md` 放到專案根（或 `~/.claude/CLAUDE.md` 全域生效）。
   其餘檔案保持相對路徑（ref/、templates/ 與 CLAUDE.md 同層）。
2. **claude.ai**：設定 > 個人偏好 → 把現行 2026-06-28 版**先自行留存一份**，
   再以本包 `CLAUDE.md` 全文取代（貼上時把「本包檔案索引」段落保留，
   claude.ai 環境讀不到 ref/ 檔案時，模型會依第 6 節優先序退回既有 skills）。
   ⚠️ 已知限制：claude.ai 讀不到 ref/ 引用檔——合規細節靠 kocskin-compliance-check
   skill 補位（該 skill 與 ref/compliance-rules.md 的同步核對列在待辦）。
3. **第一個 Claude Code session 先跑**：01-dispatch.md 第 0 節的環境驗證
   （模型清單、subagent、effort 參數），把結果寫回該節。

## 改了什麼、為什麼（一頁總結）
| 交付 | 檔案 | 一句話 |
|---|---|---|
| A 診斷 | 00-diagnosis.md | 三大病灶：事實混進常駐檔（過期最危險）、驗證自驗（幣別事故的根因）、單人樞紐無 runbook |
| B 新憲章 | CLAUDE.md + ref/×2 | 舊 claude.md 拆三份：硬紅線 R1–R7＋路由表常駐；合規四關、品牌格式抽成引用檔。新增：數字保鮮（>14天需重查）、管道順序不可重排、驗證不自驗 |
| C 調度 | 01-dispatch.md | 指揮官不下場、派工三件套、模型分級與升降級、回報合約；含無 subagent 環境（claude.ai）替代做法 |
| D 判斷 | 02-judgment.md | 五組 rubric（升級/完成/問人/換路/驗底線）各附正反例＋制度補不了的事的處置法 |
| E 模板 | templates/dispatch-prompts.md | 搜尋/實作/重構/研究/審查五型派工模板，填空即用 |
| F 維護 | 04-maintenance.md + lessons.md | 權限分級（可自改/先問/絕不做）、教訓格式、精簡觸發線、同步義務 |
| G 信 | 05-letter.md | 三件沒被問的事（合規=生存線、季節性 vs 記憶、單人風險）＋四種退化模式與金絲雀測試 |

## 明天開始怎麼用
- 任何 session 開場：模型讀 CLAUDE.md → 按路由表找細則，不用你重複交代。
- 出貼文/文案：管道自動變成 查V2 → 產 → 分離審查 → 交付；審查會逐關給結論。
- 動廣告預算：R4 流程強制——讀現值、NT$ 明碼跟你確認、寫後讀回、重啟 ACTIVE。
- 踩到坑：要求模型「按 04 格式寫進 lessons.md」，同類第二次它會提議升級成正式規則。
- 覺得規則變囉嗦：等模型自己提議精簡（觸發線已設），或你說一聲即可。

## 誠實標註（本 session 的極限）
- 在 claude.ai App 產出，未實測 Claude Code 參數（驗證步驟已留在 01 第 0 節）。
- 「fresh-context 對抗審查」以分離輪次自審替代，抓出並修了 3 個真問題
  （幽靈檔號、草稿模式與貼文入庫規則打架、章節引用錯位）；嚴謹度低於真 subagent
  審查，建議第一個 Claude Code session 用 T5 模板對本包再派審一次。
- 品味與模糊題制度補不了：處置法在 02-judgment.md 第 6 條，別刪它。
