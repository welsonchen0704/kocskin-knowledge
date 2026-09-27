#!/bin/bash
# 規則正本同步腳本｜symlink 失效時使用
CANON=~/kocskin-knowledge/skills/kocskin-compliance-check/references
[ -d "$CANON" ] || { echo "❌ 正本目錄不存在：$CANON"; exit 1; }

TARGETS=(
  ~/.claude/skills/kocskin-compliance-check/references
  ~/.codex/skills/kocskin-compliance-check/references
)
for D in "${TARGETS[@]}"; do
  [ -d "$D" ] || continue
  for F in compliance-rules.md brand-rules.md replacements.md; do
    [ -L "$D/$F" ] && continue   # 已是連結就跳過
    cp "$CANON/$F" "$D/$F" && echo "SYNCED $D/$F"
  done
done

for P in \
  ~/kocskin-work/kocskin-ai-system/ref/compliance-rules.md \
  ~/kocskin-knowledge/charter/ref/compliance-rules.md \
  ~/Desktop/05_程式專案/kocskin-ssot/compliance-rules.md ; do
  [ -L "$P" ] && continue
  [ -e "$P" ] && cp "$CANON/compliance-rules.md" "$P" && echo "SYNCED $P"
done
echo "✅ 同步完成"
