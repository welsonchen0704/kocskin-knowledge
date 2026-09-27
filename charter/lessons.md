# lessons.md 踩坑紀錄（格式見 04-maintenance.md 第 2 節）

### L-001｜2026-Q2（追溯）｜FB Ads 預算幣別單位事故
情境：更新每日預算時把台幣元誤當「分」處理。
錯誤：寫入值放大 100 倍。
規則：帳號 2053421094961197 API 預算單位＝台幣元；NT$1,200/日 寫 1200。寫前讀當前值、寫後讀回比對、金額以 NT$ 明碼向 Welson 確認。
落點：已升級進 CLAUDE.md R4。

### L-002｜2026-Q2（追溯）｜預算更新觸發自動 PAUSED
情境：預算寫入成功但廣告停止投放。
錯誤：未注意此帳號預算更新會自動轉 PAUSED。
規則：預算寫入後必接 ads_activate_entity 並讀回 status=ACTIVE。
落點：已升級進 CLAUDE.md R4。

### L-003｜2026（追溯）｜特定用途無文號宣稱
情境：無美白文號的 SKU 文案使用「美白」措辭。
錯誤：把「含美白成分」當成「可宣稱美白」。
規則：成分可如實列，宣稱需文號；無文號一律走 C 案只寫透亮。
落點：已升級進 ref/compliance-rules.md 第三關。

### L-004｜2026-07-03｜dash shell 無 brace expansion
情境：本包建置時 mkdir dir/{a,b,c} 建出名為 {a,b,c} 的目錄；中文檔名經 heredoc 重導向在 /bin/sh 下失敗。
錯誤：假設 bash 語法在 /bin/sh (dash) 可用。
規則：本環境 bash_tool 底層是 dash——目錄逐一 mkdir；輸出檔名優先用 ASCII。
落點：留在 lessons（環境怪癖）。

### L-005｜2026-07-03｜停售品同名陷阱（回購星系「益生守護者」）
情境：fresh-context 審查發現 ref/brand-and-content.md 回購星系列出在售品「益生守護者」，與 R5 停售品「益生守護者7日體驗包」僅差四字。
錯誤：兩者同名前綴，弱模型寫回購線文案時可能提及「益生守護者」而越過 R5，或把本體與停售體驗包混為一談。
規則：該品保留加註「（非7日體驗包；體驗包已停售見R5，在售狀態以V2為準）」；凡與停售品同名前綴的在售品，一律就地標注區分。
落點：已修 ref/brand-and-content.md:22；規則留 lessons（防同類再發）。

### L-006｜2026-07-03｜社群內容比例三處漂移（含裁定）
情境：社群內容比例在三處不一致——ref/brand-and-content.md 教育40/商品25/見證20/促銷15；使用者全域與 Downloads 專案 CLAUDE.md 及 kocskin-post-writer skill 皆寫商品價值40/教育30/見證20/促銷10，連「誰佔40%」都相反。
錯誤：同一規格散在 ≥3 處各自維護，違反單一來源；下游 post-writer 必然分歧。
規則：Welson 2026-07-03 裁定正確比例＝【教育40 / 商品25 / 見證20 / 促銷15】，單一來源＝ref/brand-and-content.md，ref 不動；其餘位置一律對齊或改為指向 ref 的指標，不各自寫死（04-maintenance 同步義務第 49 條）。
落點：2026-07-03 已完成對齊——偏好檔（全域＋Downloads CLAUDE.md）比例行改為指向 ref 單一來源；post-writer skill（SKILL.md＋content-types.md＋weekly-rhythm.md）數字與門檻同步為 教育40/商品25/見證20/促銷15、促銷門檻>15%。規則留 lessons + 既有同步義務。

### L-007｜2026-07-03｜檔案索引跳號無說明
情境：CLAUDE.md 檔案索引列 00/01/02/04/05，跳過 03 且無註記，接手模型易誤判缺檔。
錯誤：編號斷點未說明，README 自稱修過但成品仍留裸跳號。
規則：刻意的編號斷點須就地一行說明「已併入／刻意保留斷號」，不留無註記裸跳號。
落點：已修 CLAUDE.md 索引段；規則留 lessons。

### L-008｜2026-07-03｜派工模板填空占位未給預設值
情境：dispatch-prompts.md 通用尾段〔300〕字、各型〔N〕為裸填空占位，弱模型可能連〔〕一起送進 subagent prompt。
錯誤：占位符未附預設實值，遺漏填空即污染派工指令。
規則：模板占位一律附「預設值＋可調」字樣（回報上限預設300字、N 預設2）；派工時填實值勿連〔〕送出。
落點：已修 templates/dispatch-prompts.md 尾段；規則留 lessons。

### L-009｜2026-07-03｜社群貼文入庫寫入護欄較 R4 軟
情境：CLAUDE.md 路由表允許「定稿後寫入社群貼文DB」為草稿模式唯一例外，原判準僅自然語言「Welson 明確確認」，無 read-back 硬綁定，較 R4（FB Ads）四步協議寬。
錯誤：正式 Notion 寫入未一致綁定寫後讀回，存在靜默失敗/漂移空間。
規則：所有 Notion 正式寫入一律接 R7 讀回該筆比對，社群貼文DB 亦同。
落點：已於路由表該格補「寫入後讀回該筆比對（R7）」；規則留 lessons。

### L-010｜2026-09-27｜R3 美白禁令新增極光美白系列例外（制度變更）
情境：Welson 2026-09-27 拍板——極光美白系列 KOC022 極光美白精華／KOC042 極光美白神仙水／KOC030 極光美白乳霜，傳明酸添加比例足以支撐美白宣稱，「美白」訴求即日解鎖；依 2026-09-26 D2 裁定之解鎖條件（PIF 完備＋產品登錄完成＋法規窗口確認）達成。Notion V2 三品合規卡已於 claude.ai 對話同步更新。
錯誤：非踩坑。但同時修正一處長期分岔——CLAUDE_v2.1.md R3 末句自 07-11 起仍寫「無文號禁美白」，ref/compliance-rules.md 第三關卻已放寬為「含衛福部核可美白成分可訴求美白」，兩處規則不一致達 80 天；且「衛福部核可美白成分」一語本身即暗示官方核准（現行制度已無核准機制），不宜再作為判準依據。
規則：美白宣稱僅限 KOC022／KOC042／KOC030 三品可用「美白、美白肌膚、亮白、白皙、淨白、嫩白、皙白」等通常詞句；淡斑／淡化斑點／調節、抑制或阻斷黑色素／防止色斑形成等機轉宣稱、「衛福部核准／核可美白成分」表述、KOC030 獲獎／專利／TranEX-1／胜肽 維持禁用；其餘 SKU 照 R3 原規則。KOC050 未在本次裁定範圍，以 V2 合規卡為準。同日追加裁定：「調節黑色素」原為 compliance-check skill 的淡斑替代語（replacements.md、compliance-rules.md 兩處），屬機轉宣稱，一併改列禁用。
落點：已寫入 CLAUDE_v2.1.md R3 例外條款（正本）；ref/compliance-rules.md 依 08-08 架構為指向 skill 正本的 symlink（四關版已退役，存 .bak），規則本體改在 kocskin-compliance-check/references/compliance-rules.md 與 SKILL.md〈美白宣稱規則〉；skill 內建 references（kocskin-compliance-check/compliance-rules.md 第 32 行、kocskin-product-lookup/schema.md 裁定摘要第 1–2 條、kocskin-threads-writer/SKILL.md 第 54 行舉例）已於同日經 Welson 核准同步；KOC050 經 Welson 確認維持以 V2 為準。待辦：六支 skill 重新上傳 claude.ai、claude.ai 個人偏好檔 R3 手動貼入例外條款。

### L-011｜2026-09-27｜本機 clone 五十天未入庫，GitHub 正本落後、上傳的 skill 被退版
情境：執行 R3 例外條款同步時發現 `~/kocskin-knowledge` 停在 08-03 commit，之後的 08-08 美白判準更正、09-14／09-15 六支 skill 修訂、三支新 skill（91app-report-export／ad-wireframe／visual-generator）全部只在本機、未 commit 未 push。README 自稱「repo 是唯一版本正本」，實際正本在本機。
錯誤：當日先依 GitHub 版打包三支 skill 上傳 claude.ai，等於把 compliance-check 從 09-15 版（13.4KB，含四關格式與美白宣稱規則）退回 08-03 版（7.3KB）；charter/ref/compliance-rules.md 在 GitHub 仍是四關版，本機早已改成指向 skill 的 symlink，兩邊對「正本是誰」認知不同。
規則：①改 skill 或憲章的當個 session 內必 commit＋push，本機 `git status` 不得留過夜的 modified；②打包上傳 claude.ai 前先 `git status` 確認乾淨、且 `git log origin/main..HEAD` 為空，zip 一律從 main 打；③合規規則正本＝skills/kocskin-compliance-check/references/（08-08 架構），charter/ref/compliance-rules.md 只作 symlink，不再各自維護。
落點：本條規則 ①② 建議升級進 04-maintenance.md 第 4 節同步義務（待 Welson 核准）；③ 已於本日合併時落實（repo 內改為相對路徑 symlink，charter/README.md 同步註記）。
