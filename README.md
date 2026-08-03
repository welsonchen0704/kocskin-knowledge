# kocskin-knowledge（種子包）

KOCSKIN AI 知識系統的**唯一版本正本**。claude.ai 上傳與本機拷貝一律從本 repo 出；改規則＝改這裡 → commit → 傳播 → 跑 `tools/verify.py`。


## 結構

```
skills/     六個 KOCSKIN skills 的正本（2026-08-02 知識審計 P2 修訂版）
            ├── kocskin-compliance-check/   ← L1 法律通則（compliance-rules/replacements）
            │                                  ＋ L2 品牌紅線（brand-rules）正本所在
            ├── kocskin-product-lookup/
            ├── kocskin-post-writer/
            ├── kocskin-threads-writer/
            ├── kocskin-live-lineup-planner/
            └── kocskin-script-trend-updater/
charter/    憲章與附件（待 Welson 提供本機 ~/.claude/CLAUDE.md、ref/、01-dispatch 等後入庫）
tools/      verify.py — 一致性驗收腳本（--skills 指向 skills/ 即可跑）
```

## 同步流程（每次裁定更新後）

1. 改正本（分層規則見審計報告 `knowledge-audit/README.md`〈三〉〈四〉）→ commit＋更新紀錄。
2. 上傳 claude.ai：對應 skill 目錄壓 zip → claude.ai 設定→Skills 重新上傳 → 用 manifest updatedAt 確認。
3. 同步本機拷貝（`~/kocskin-work/kocskin-ai-system/` 由 repo pull／複製，不再手改）。
4. ai-studio 受驗快照（forbidden-words.ts／platform-rules.ts）如受影響 → 開 PR。
5. `python3 tools/verify.py --skills skills/ --ai-studio <ai-studio路徑>` → 0 FAIL 才算同步完成。

單品裁定不在本 repo——正本永遠是 Notion V2 合規卡（憲章 R1）。
