#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOCSKIN 知識庫一致性驗收腳本（唯讀）
====================================
用途：在「裁定更新 → 正本修改 → 各處同步」之後跑一次，機器驗證規則沒有再度分岔。
本腳本只讀檔、只輸出報告，不修改任何檔案。

用法：
  python3 06-verify.py                          # 用預設路徑（雲端 session）
  python3 06-verify.py --skills ~/.claude/skills --ai-studio ~/code/kocskin-ai-studio
  python3 06-verify.py --wordlist-diff          # 額外輸出禁用詞正本 vs 程式檔差異（資訊性）

結束碼：0＝全部 PASS（WARN 不擋）；1＝有 FAIL。
無法離線驗證的活資料（Notion V2 / 憲章鏡像）列在結尾的「人工檢查清單」。
"""
import argparse
import datetime as dt
import glob
import os
import re
import sys

# ---------------------------------------------------------------- 設定

DEFAULT_SKILLS_ROOT = os.path.expanduser("~/.claude/skills")
KOCSKIN_SKILLS = [
    "kocskin-compliance-check",
    "kocskin-product-lookup",
    "kocskin-post-writer",
    "kocskin-threads-writer",
    "kocskin-live-lineup-planner",
    "kocskin-script-trend-updater",
]

# 檢查 1｜過期斷言墓碑：這些字串一旦重新出現＝有人又把快照寫死了
# 格式：(字串, 允許持有的檔案片段清單)——例如 platform-specs.md 的「15–30」是
# 已標「待決事項、未開放」的合法記載，不是規格本身。
STALE_CLAIMS = [
    ("筆全為在售", []),            # 「45 筆全為在售」及其變體
    ("沒有任何停售列", []),
    ("V2 目前沒有停售列", []),
    ("43 SKU", []),
    ("SKU 數：45", []),
    ("15-30 個分層", ["platform-specs.md"]),   # IG hashtag 舊規格
    ("15–30 個分層", ["platform-specs.md"]),
]
# 允許出現墓碑字串的檔案（討論歷史用，不是規則本身）
STALE_ALLOWED = ["knowledge-audit", "lessons", "更新紀錄"]

# 檢查 2｜執行長本名：出現的那一行必須帶「禁令/錯誤示範」標記才放行
CEO_REAL_NAME = "李燕"
CEO_BAN_CONTEXT = ["❌", "🔴", "不用", "不得", "不使用", "錯誤", "壞範例", "→"]
CEO_ALLOWED_FILES = [
    "kocskin-compliance-check/references/brand-rules.md",     # 禁令正本
    "kocskin-compliance-check/references/replacements.md",    # 替代字典（錯誤示範欄）
    "kocskin-compliance-check/SKILL.md",                      # 審查規則描述
]

# 檢查 3｜停售/紅線品名單唯一正本：品名只准出現在正本；其他檔案要用引用
STOPSALE_CANONICAL = "kocskin-compliance-check/references/brand-rules.md"
STOPSALE_NAMES = [
    "氣墊粉餅補充蕊",
    "益生守護者 7 日體驗包",
    "益生守護者7日體驗包",
    "雪絨花緊緻賦活面膜",
    "北歐之森香氛蠟燭",
    "角質煥膚發光液",
    # 「收斂水」為通名易誤報，僅在 wordlist-diff 模式提示人工看
]
# 防混淆的相似名在售品，出現不算違規
STOPSALE_FALSE_POSITIVES = ["益生守護者益生菌", "晶燦白皙氣墊粉餅"]

# 檢查 4｜快照時效：抓「同步日期／比對日／核對日」型日期，過期提醒
SNAPSHOT_PATTERNS = [
    r"同步日期[:：]\s*(\d{4}-\d{2}-\d{2})",
    r"最後與正本比對日[:：]\s*(\d{4}-\d{2}-\d{2})",
    r"法規內容最後核對日[:：]\s*(\d{4}-\d{2})",
]
SNAPSHOT_WARN_DAYS = 45
LEGAL_RECHECK_MONTHS = 6   # compliance-rules.md 自訂規則

# 檢查 5｜受驗快照等值：threads-rules 的全域禁語行必須與正本一字不差
# （正本＝brand-rules/compliance-rules 所載、憲章 R3 同文；改正本時要同步改快照）
R3_COSMETIC_LINE = "**化粧品：** 療效、根治、修復受損細胞、第一、最、唯一、保證、無副作用、立即見效、除皺、活化細胞、抗發炎、修復DNA、治療、幹細胞療效、PDRN 修復再生"
R3_SUPPLEMENT_LINE = "**保健食品：** 治療、預防（疾病）、改善（疾病）、療效、降血糖、調節血糖"

# 檢查 6（--wordlist-diff）｜forbidden-words.ts vs 正本詞集（資訊性）
R3_CANONICAL_WORDS = [
    "療效", "根治", "修復受損細胞", "第一", "最", "唯一", "保證", "無副作用",
    "立即見效", "除皺", "活化細胞", "抗發炎", "修復DNA", "治療", "幹細胞療效",
    "PDRN 修復再生",
]

# ---------------------------------------------------------------- 工具

RESULTS = []

def record(status, name, detail=""):
    RESULTS.append((status, name, detail))
    mark = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ "}[status]
    print(f"{mark} [{status}] {name}" + (f"\n     {detail}" if detail else ""))

def iter_files(roots, exts=(".md", ".ts")):
    for root in roots:
        if not root or not os.path.isdir(root):
            continue
        for path in glob.glob(os.path.join(root, "**", "*"), recursive=True):
            if os.path.isfile(path) and path.endswith(exts) and "node_modules" not in path:
                yield path

def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""

def rel(path, roots):
    for r in roots:
        if r and path.startswith(r):
            return os.path.relpath(path, r)
    return path

# ---------------------------------------------------------------- 檢查

def check_stale_claims(files, roots):
    hits = []
    for p in files:
        text = read(p)
        for claim, allowed in STALE_CLAIMS:
            if claim in text \
               and not any(a in p for a in STALE_ALLOWED) \
               and not any(a in p for a in allowed):
                hits.append(f"{rel(p, roots)} ← 「{claim}」")
    if hits:
        record("FAIL", "過期斷言墓碑（快照數字/舊規格不得寫死）", "；".join(hits))
    else:
        record("PASS", "過期斷言墓碑：無復發")

def check_ceo_name(files, roots):
    hits = []
    for p in files:
        if any(p.endswith(a) or a in p for a in CEO_ALLOWED_FILES):
            continue
        if "knowledge-audit" in p:
            continue
        for i, line in enumerate(read(p).splitlines(), 1):
            if CEO_REAL_NAME in line and not any(m in line for m in CEO_BAN_CONTEXT):
                hits.append(f"{rel(p, roots)}:{i}")
    if hits:
        record("FAIL", f"執行長本名「{CEO_REAL_NAME}」出現在無禁令標記的行", "、".join(hits))
    else:
        record("PASS", "執行長稱謂：非禁令記載處無本名")

def check_stopsale_single_source(files, roots):
    """品名出現於正本以外的檔案 → 違反「引用不複製」。
    例外：product-lookup 家族與 AGENTS.md 對『兩支未販售紅線品』的技術性說明
    （它們解釋『V2 查不到是正常的』，屬查詢行為說明，經 Welson 於第二階段確認去留）。"""
    tech_exception_files = [
        "kocskin-product-lookup/SKILL.md",
        "kocskin-product-lookup/references/schema.md",
        "kocskin-product-lookup/references/query-patterns.md",
        "kocskin-compliance-check/references/replacements.md",  # 替代表的「（刪除整句）」列＝禁令記載
        "AGENTS.md",
        "docs/CLAUDE_kocskin_ai_studio_v2.md",  # 歷史 spec：「已知停售（提示用）」＝禁令記載（2026-08-03 入庫）
    ]
    tech_exception_names = {"氣墊粉餅補充蕊", "益生守護者 7 日體驗包", "益生守護者7日體驗包"}
    hits = []
    for p in files:
        if p.endswith(STOPSALE_CANONICAL) or STOPSALE_CANONICAL in p or "knowledge-audit" in p:
            continue
        text = read(p)
        for name in STOPSALE_NAMES:
            if name not in text:
                continue
            # 相似名在售品（晶燦白皙氣墊粉餅／益生守護者益生菌）與紅線品名無子字串
            # 重疊，直接比對品名即可，無需額外防誤判。
            if name in tech_exception_names and any(t in p for t in tech_exception_files):
                continue
            hits.append(f"{rel(p, roots)} ← 「{name}」")
    if hits:
        record("FAIL", "停售/紅線品名出現在正本（brand-rules.md〈一〉）以外", "；".join(sorted(set(hits))))
    else:
        record("PASS", "停售/紅線品名單：僅正本（含核可的技術性例外）持有")

def check_snapshot_freshness(files, roots):
    today = dt.date.today()
    warns = []
    for p in files:
        text = read(p)
        for pat in SNAPSHOT_PATTERNS:
            for m in re.finditer(pat, text):
                raw = m.group(1)
                try:
                    if len(raw) == 7:  # YYYY-MM（法規核對日）
                        d = dt.date(int(raw[:4]), int(raw[5:7]), 1)
                        limit = LEGAL_RECHECK_MONTHS * 31
                    else:
                        d = dt.date.fromisoformat(raw)
                        limit = SNAPSHOT_WARN_DAYS
                    if (today - d).days > limit:
                        warns.append(f"{rel(p, roots)}：{raw}（{(today - d).days} 天前）")
                except ValueError:
                    pass
    if warns:
        record("WARN", "快照/核對日過期提醒（不擋，請安排重核）", "；".join(warns))
    else:
        record("PASS", "快照時效：皆在期限內")

def check_verified_snapshot_equality(skills_root):
    p = os.path.join(skills_root, "kocskin-threads-writer/references/threads-rules.md")
    text = read(p)
    if not text:
        record("WARN", "受驗快照等值：threads-rules.md 不存在（略過）")
        return
    missing = [ln for ln in (R3_COSMETIC_LINE, R3_SUPPLEMENT_LINE) if ln not in text]
    if missing:
        record("FAIL", "threads-rules.md 全域禁語快照與正本（R3 詞列）不一致",
               "缺/異動行數：" + str(len(missing)) + "——改了正本詞列時必須同步此快照，或反之查明誰動了快照")
    else:
        record("PASS", "threads-rules.md 全域禁語快照＝正本詞列")

def wordlist_diff(ai_studio_root):
    p = os.path.join(ai_studio_root, "lib/compliance/forbidden-words.ts")
    text = read(p)
    if not text:
        record("WARN", "wordlist-diff：找不到 forbidden-words.ts（略過）")
        return
    code_words = set(re.findall(r'word:\s*"([^"]+)"', text))
    canon = set(R3_CANONICAL_WORDS)
    only_canon = sorted(canon - code_words)
    only_code = sorted(code_words - canon)
    print("\n── 禁用詞差異（資訊性，僅供 Welson 裁定，不算 FAIL）──")
    print(f"  正本（R3 詞列）有、程式檔無：{ '、'.join(only_canon) or '（無）'}")
    print(f"  程式檔有、R3 詞列未明列：{ '、'.join(only_code) or '（無）'}")
    wl = re.findall(r'BRAND_SIGNATURE_WHITELIST[^\]]*\]', text)
    if wl and ("最" in wl[0]):
        print("  ⚖️ 白名單仍含「最」字 phrase（衝突矩陣 C4，待裁定）")

# ---------------------------------------------------------------- 主程式

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default=DEFAULT_SKILLS_ROOT)
    ap.add_argument("--ai-studio", default="/workspace/kocskin-ai-studio")
    ap.add_argument("--wordlist-diff", action="store_true")
    args = ap.parse_args()

    skill_dirs = [os.path.join(args.skills, s) for s in KOCSKIN_SKILLS]
    roots = skill_dirs + [args.ai_studio]
    files = list(iter_files(roots))
    print(f"掃描 {len(files)} 個檔案（skills root: {args.skills}；ai-studio: {args.ai_studio}）\n")

    check_stale_claims(files, roots)
    check_ceo_name(files, roots)
    check_stopsale_single_source(files, roots)
    check_snapshot_freshness(files, roots)
    check_verified_snapshot_equality(args.skills)
    if args.wordlist_diff:
        wordlist_diff(args.ai_studio)

    print("\n── 人工檢查清單（活資料，腳本無法離線驗證）──")
    print("  1. Notion V2：SELECT \"SKU狀態\", COUNT(*) ... GROUP BY——分佈與 brand-rules.md〈一〉是否相符")
    print("  2. 憲章 Notion 鏡像最後編輯日 vs 本機 CLAUDE.md 版本行——落差要走 D13 合併")
    print("  3. 《發文渠道分流規範》正本 vs claude 專案副本——抽查字數/配比/hashtag 三格")
    print("  4. claude.ai skills 重新上傳後，用 manifest updatedAt 確認六支皆為新版")

    fails = [r for r in RESULTS if r[0] == "FAIL"]
    print(f"\n結果：{len([r for r in RESULTS if r[0]=='PASS'])} PASS / "
          f"{len([r for r in RESULTS if r[0]=='WARN'])} WARN / {len(fails)} FAIL")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
