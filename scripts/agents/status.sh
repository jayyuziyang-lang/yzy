#!/bin/bash
# =============================================================================
# 扬说财经 · 生产状态检查 Agent
# 快速查看今日所有产出的完整性状态
# 用法：bash scripts/agents/status.sh
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
TODAY_DIR="${ROOT_DIR}/${TODAY}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()    { echo -e "  ${GREEN}✅${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠️${NC} $1"; }
fail()  { echo -e "  ${RED}❌${NC} $1"; }
info()  { echo -e "  ${CYAN}ℹ️${NC} $1"; }

echo -e "${BLUE}=========================================="
echo "  扬说财经 · 生产状态报告"
echo "  📅 ${TODAY}"
echo -e "=========================================="
echo ""

# === 目录检查 ===
echo -e "${CYAN}📁 项目结构${NC}"
if [ -d "$ROOT_DIR" ]; then ok "项目根目录"; else fail "项目根目录"; fi
echo ""

# === 早报检查 ===
echo -e "${CYAN}🌅 早报 (Morning)${NC}"
M_DIR="${TODAY_DIR}/wechat-publish/morning"
if [ ! -d "$M_DIR" ]; then
  fail "目录不存在"
else
  # storyboard
  [ -f "$M_DIR/storyboard.json" ] && ok "storyboard.json" || fail "storyboard.json 缺失"
  # article
  [ -f "$M_DIR/article.html" ]    && ok "article.html"   || fail "article.html 缺失"
  [ -f "$M_DIR/article.md" ]      && ok "article.md"     || fail "article.md 缺失"
  # SVGs
  SVG_COUNT=$(ls "$M_DIR/comic/"*.svg 2>/dev/null | wc -l)
  if [ "$SVG_COUNT" -gt 0 ]; then
    ok "漫画 SVG: ${SVG_COUNT} 幅"
  else
    fail "漫画 SVG 缺失"
  fi
  # 脚本
  if [ -f "$M_DIR/script.txt" ]; then
    SC=$(wc -c < "$M_DIR/script.txt" 2>/dev/null || echo 0)
    ok "口播脚本 ($(echo $SC) chars)"
  else
    warn "口播脚本 待生成"
  fi
  # 音频
  if [ -f "$M_DIR/audio.mp3" ]; then
    SZ=$(stat -c%s "$M_DIR/audio.mp3" 2>/dev/null || stat -f%z "$M_DIR/audio.mp3" 2>/dev/null)
    SZ_KB=$((SZ / 1024))
    ok "音频 ($SZ_KB KB)"
  else
    warn "音频 待生成"
  fi
fi
echo ""

# === 晚报检查 ===
echo -e "${CYAN}🌙 晚报 (Evening)${NC}"
E_DIR="${TODAY_DIR}/wechat-publish/evening"
if [ ! -d "$E_DIR" ]; then
  fail "目录不存在"
else
  [ -f "$E_DIR/storyboard.json" ] && ok "storyboard.json" || fail "storyboard.json 缺失"
  [ -f "$E_DIR/article.html" ]    && ok "article.html"   || fail "article.html 缺失"
  [ -f "$E_DIR/article.md" ]      && ok "article.md"     || fail "article.md 缺失"
  SVG_COUNT=$(ls "$E_DIR/comic/"*.svg 2>/dev/null | wc -l)
  if [ "$SVG_COUNT" -gt 0 ]; then
    ok "漫画 SVG: ${SVG_COUNT} 幅"
  else
    fail "漫画 SVG 缺失"
  fi
  if [ -f "$E_DIR/script.txt" ]; then
    SC=$(wc -c < "$E_DIR/script.txt" 2>/dev/null || echo 0)
    ok "口播脚本 ($(echo $SC) chars)"
  else
    warn "口播脚本 待生成"
  fi
  if [ -f "$E_DIR/audio.mp3" ]; then
    SZ=$(stat -c%s "$E_DIR/audio.mp3" 2>/dev/null || stat -f%z "$E_DIR/audio.mp3" 2>/dev/null)
    SZ_KB=$((SZ / 1024))
    ok "音频 ($SZ_KB KB)"
  else
    warn "音频 待生成"
  fi
fi
echo ""

# === 品牌资产 ===
echo -e "${CYAN}🎭 品牌资产${NC}"
ASSETS_DIR="${ROOT_DIR}/docs/assets"
if [ -d "$ASSETS_DIR/character" ]; then
  ok "人物图片已就位"
else
  fail "人物图片缺失"
fi
for svg in avatar.svg header.svg cover-morning.svg cover-evening.svg; do
  [ -f "$ASSETS_DIR/$svg" ] && ok "$svg" || fail "$svg 缺失"
done
echo ""

# === 数据图表 ===
echo -e "${CYAN}📊 数据图表${NC}"
CHART_DIR="${ROOT_DIR}/docs/charts"
if [ -d "$CHART_DIR" ]; then
  C_COUNT=$(ls "$CHART_DIR"/*.svg 2>/dev/null | wc -l)
  ok "${C_COUNT} 张图表"
else
  fail "charts 目录缺失"
fi
echo ""

# === 质量检查状态 ===
echo -e "${CYAN}🔎 质量检查${NC}"
QC_SCRIPT="${ROOT_DIR}/scripts/quality-check.py"
if [ -f "$QC_SCRIPT" ]; then
  PASS_COUNT=$(PYTHONIOENCODING=utf-8 python "$QC_SCRIPT" 2>&1 | grep -c "\[PASS\]")
  FAIL_COUNT=$(PYTHONIOENCODING=utf-8 python "$QC_SCRIPT" 2>&1 | grep -c "\[FAIL\]")
  if [ "$FAIL_COUNT" -eq 0 ]; then
    ok "全部 ${PASS_COUNT} 项检查通过"
  else
    warn "通过 ${PASS_COUNT} 项，失败 ${FAIL_COUNT} 项"
  fi
fi
echo ""

# === 快捷操作 ===
echo -e "${CYAN}⚡ 快捷操作${NC}"
echo -e "  早报全流程:    ${GREEN}bash scripts/morning.sh${NC}"
echo -e "  晚报全流程:    ${GREEN}bash scripts/evening.sh${NC}"
echo -e "  仅出脚本:      ${GREEN}python scripts/upgrade-audio.py --script-only morning${NC}"
echo -e "  从脚本生成音频:${GREEN}python scripts/upgrade-audio.py --from-script morning${NC}"
echo -e "  完整质量检查:  ${GREEN}python scripts/quality-check.py${NC}"
echo ""
