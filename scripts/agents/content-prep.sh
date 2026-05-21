#!/bin/bash
# =============================================================================
# 扬说财经 · 内容准备辅助 Agent
# 用法：bash scripts/agents/content-prep.sh morning
#       bash scripts/agents/content-prep.sh evening
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
SESSION="${1:-morning}"
EDITION_DIR="${ROOT_DIR}/${TODAY}/wechat-publish/${SESSION}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} $1"; }
fail() { echo -e "  ${RED}❌${NC} $1"; }

LABEL="早报" && [ "$SESSION" = "evening" ] && LABEL="晚报"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  内容结构验证 — ${LABEL}${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# === storyboard.json ===
SB_PATH="${EDITION_DIR}/storyboard.json"
PANEL_COUNT=0
SB_TITLE=""
if [ -f "$SB_PATH" ]; then
  PANEL_COUNT=$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1], 'r', encoding='utf-8'))
    print(len(d.get('panels', [])))
except: print(0)
" "$SB_PATH" 2>/dev/null || echo 0)
  SB_TITLE=$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1], 'r', encoding='utf-8'))
    print(d.get('articleTitle', ''))
except: print('')
" "$SB_PATH" 2>/dev/null)
  if [ "$PANEL_COUNT" -gt 0 ]; then
    ok "storyboard.json: ${PANEL_COUNT} 个分镜 · ${SB_TITLE}"
  else
    fail "storyboard.json 面板数为空"
  fi
else
  fail "storyboard.json 缺失"
fi
echo ""

# === article.md ===
MD_PATH="${EDITION_DIR}/article.md"
if [ -f "$MD_PATH" ]; then
  MC=$(wc -m < "$MD_PATH" 2>/dev/null | tr -d ' ')
  [ "$MC" -gt 500 ] && ok "article.md: ${MC} 字" || warn "article.md 较短 (${MC}字)"
else
  fail "article.md 缺失"
fi
echo ""

# === article.html ===
HTML_PATH="${EDITION_DIR}/article.html"
HTML_PANEL_COUNT=0
if [ -f "$HTML_PATH" ]; then
  ok "article.html 存在"
  HTML_CONTENT=$(cat "$HTML_PATH")
  L1=false; L2=false; L3=false
  echo "$HTML_CONTENT" | grep -q "layer1\|热点速览" && L1=true
  echo "$HTML_CONTENT" | grep -q "layer2\|深度" && L2=true
  echo "$HTML_CONTENT" | grep -q "layer3\|数据" && L3=true
  $L1 && ok "  Layer1 (速览) ✓" || warn "  Layer1 可能缺失"
  $L2 && ok "  Layer2 (深度) ✓" || warn "  Layer2 可能缺失"
  $L3 && ok "  Layer3 (数据) ✓" || warn "  Layer3 可能缺失"
  HTML_PANEL_COUNT=$(grep -c 'panel-[0-9]*\.svg' "$HTML_PATH" 2>/dev/null || echo 0)
else
  fail "article.html 缺失"
fi
echo ""

# === storyboard vs HTML 面板数一致 ===
SCRATCH_COUNT=$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1], 'r', encoding='utf-8'))
    print(len(d.get('panels', [])))
except: print(0)
" "$SB_PATH" 2>/dev/null || echo 0)
if [ "$SCRATCH_COUNT" -eq "$HTML_PANEL_COUNT" ] && [ "$SCRATCH_COUNT" -gt 0 ]; then
  ok "Storyboard(${SCRATCH_COUNT}) vs HTML(${HTML_PANEL_COUNT}) 面板数一致"
else
  [ "$SCRATCH_COUNT" -gt 0 ] && [ "$HTML_PANEL_COUNT" -gt 0 ] && \
    warn "Storyboard(${SCRATCH_COUNT}) vs HTML(${HTML_PANEL_COUNT}) 不一致" || true
fi
echo ""

# === 新增：推荐下一步Agent操作 ===
echo -e "${CYAN}🤖 Agent团队推荐操作${NC}"
echo "  1. 新闻采集: bash scripts/agents/news-collector.sh all"
echo "  2. 事实核查: bash scripts/agents/fact-checker.sh"
echo "  3. 生产管线: bash scripts/${SESSION}.sh"
echo "  4. 质量检查: python scripts/quality-check.py"
echo "  5. 每日复盘: bash scripts/agents/daily-review.sh"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  验证完成 — 由内容验证Agent (A-03) 执行${NC}"
echo -e "${GREEN}  下一步: bash scripts/${SESSION}.sh${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
