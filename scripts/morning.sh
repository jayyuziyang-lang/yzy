#!/bin/bash
# =============================================================================
# 扬说财经 · 早报生产入口
# 用法：bash scripts/morning.sh
# =============================================================================
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TODAY=$(date +%Y-%m-%d)
TODAY_DIR="${ROOT_DIR}/${TODAY}"
PASS=0
FAIL=0

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
ok()   { echo -e "${GREEN}[✓]${NC} $1"; PASS=$((PASS+1)); }
fail() { echo -e "${RED}[✗]${NC} $1"; FAIL=$((FAIL+1)); }

echo -e "${BLUE}=========================================="
echo "  扬说财经 · 早报生产管线"
echo "  📅 ${TODAY}"
echo -e "==========================================${NC}"
echo ""

# === 阶段0：新闻源验证（AI团队协作）===
log "📰 阶段0：新闻源验证..."
cd "${ROOT_DIR}"
if [ -f "${ROOT_DIR}/docs/review/factcheck-${TODAY}.md" ]; then
  ok "新闻简报已核查（来源已验证）"
else
  warn "新闻简报未经过事实核查"
  warn "  建议先运行: bash scripts/agents/news-collector.sh all"
  warn "  再运行:     bash scripts/agents/fact-checker.sh"
  echo -e "${YELLOW}  是否继续? (Ctrl+C 取消, 等待5秒自动继续)${NC}"
  sleep 5
  warn "继续执行生产管线..."
fi
echo ""

# === 环境准备 ===
log "📁 检查生产环境..."
if [ ! -d "${TODAY_DIR}/wechat-publish/morning/comic" ]; then
  mkdir -p "${TODAY_DIR}/wechat-publish/morning/comic"
  mkdir -p "${TODAY_DIR}/archive"
  ok "今日目录已创建"
fi
for f in "${TODAY_DIR}/wechat-publish/morning/storyboard.json" \
         "${TODAY_DIR}/wechat-publish/morning/article.md" \
         "${TODAY_DIR}/wechat-publish/morning/article.html"; do
  if [ ! -f "$f" ]; then
    fail "内容文件缺失: $(basename $f) —— 请先准备早报内容"
  fi
done
[ $FAIL -gt 0 ] && exit 1
ok "生产环境就绪"
echo ""

# === 阶段1：数据图表 ===
log "📊 阶段1：数据图表..."
cd "${ROOT_DIR}"
PYTHONIOENCODING=utf-8 python scripts/generate-charts.py && ok "图表生成完成" || fail "图表生成失败"
PYTHONIOENCODING=utf-8 python scripts/quality-check.py charts && ok "图表质量检查通过" || fail "图表质量检查不通过"
echo ""

# === 阶段2：品牌资产 ===
log "🎭 阶段2：品牌资产..."
cd "${ROOT_DIR}"
PYTHONIOENCODING=utf-8 python scripts/rebrand-character.py && ok "品牌资产生成完成" || fail "品牌资产生成失败"
PYTHONIOENCODING=utf-8 python scripts/quality-check.py brand && ok "品牌资产检查通过" || fail "品牌资产检查不通过"
echo ""

# === 阶段3：漫画升级 ===
log "🎨 阶段3：漫画分镜..."
cd "${ROOT_DIR}"
PYTHONIOENCODING=utf-8 python scripts/upgrade-comic.py && ok "漫画升级完成" || fail "漫画升级失败"
PYTHONIOENCODING=utf-8 python scripts/quality-check.py comics && ok "漫画质量检查通过" || fail "漫画质量检查不通过"

# 人物图像嵌入（使SVG在img标签中正确显示照片）
PYTHONIOENCODING=utf-8 python scripts/embed-character.py && ok "人物图像嵌入完成" || fail "人物图像嵌入失败"
echo ""

# === 阶段4：口播脚本（仅出文本，待审核）===
log "📝 阶段4：口播脚本生成..."
cd "${ROOT_DIR}"
PYTHONIOENCODING=utf-8 python scripts/upgrade-audio.py --script-only morning && ok "口播脚本已保存" || fail "口播脚本生成失败"
echo ""

SCRIPT_PATH="${TODAY_DIR}/wechat-publish/morning/script.txt"
echo -e "${YELLOW}══════════════════════════════════════════${NC}"
echo -e "${YELLOW}   ⏸  人工审核环节${NC}"
echo -e "${YELLOW}  请打开以下文件审核脚本文本：${NC}"
echo -e "${YELLOW}  ${SCRIPT_PATH}${NC}"
echo -e "${YELLOW}  确认无误后运行：${NC}"
echo -e "${YELLOW}  python scripts/upgrade-audio.py --from-script morning${NC}"
echo -e "${YELLOW}  然后运行：python scripts/quality-check.py${NC}"
echo -e "${YELLOW}══════════════════════════════════════════${NC}"
echo ""

log "📋 早报生产预览..."
echo ""
echo "  文章:    ${TODAY_DIR}/wechat-publish/morning/article.html"
echo "  漫画:    ${TODAY_DIR}/wechat-publish/morning/comic/"
ls -1 "${TODAY_DIR}/wechat-publish/morning/comic/"*.svg 2>/dev/null | wc -l | xargs echo "    SVG数量:"
echo "  脚本:    ${SCRIPT_PATH}"
[ -f "${TODAY_DIR}/wechat-publish/morning/audio.mp3" ] && \
  echo "  音频:    ${TODAY_DIR}/wechat-publish/morning/audio.mp3" || \
  echo "  音频:    待审核脚本后生成"
echo ""

if [ $FAIL -eq 0 ]; then
  # 自动更新站点索引
  log "📊 自动更新站点索引..."
  PYTHONIOENCODING=utf-8 python scripts/update-index.py && ok "索引已更新"
  ok "早报生产管线执行完毕"
else
  fail "存在 ${FAIL} 个问题需要处理"
fi
