#!/bin/bash
# =============================================================================
# [已弃用] 每日财经 旧版自动化流水线
# 已被 morning.sh + evening.sh 替代
# 保留此文件仅用于历史参考和 quality-check.py 检查
# 新用法:
#   bash scripts/morning.sh   # 早报生产
#   bash scripts/evening.sh   # 晚报生产
# =============================================================================
# 使用方法（旧版）：
#   bash scripts/daily-pipeline.sh            # 完整生产流程
#   bash scripts/daily-pipeline.sh --morning  # 仅早报
#   bash scripts/daily-pipeline.sh --evening  # 仅晚报
#   bash scripts/daily-pipeline.sh --preview  # 预览现有产出
#   bash scripts/daily-pipeline.sh --full     # 全量生产（图表+漫画+音频+文章）
# =============================================================================

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TODAY=$(date +%Y-%m-%d)
TODAY_DIR="${ROOT_DIR}/${TODAY}"
DATE_FORMATTED=$(date +%Y.%m.%d)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
ok()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn(){ echo -e "${YELLOW}[!]${NC} $1"; }
err() { echo -e "${RED}[✗]${NC} $1"; }

# =============================================================================
# 阶段 1：环境检查
# =============================================================================
phase_check_env() {
  log "🔍 检查运行环境..."

  # 检查目录
  if [ ! -d "${ROOT_DIR}" ]; then
    err "项目目录不存在: ${ROOT_DIR}"
    exit 1
  fi
  ok "项目目录: ${ROOT_DIR}"

  # 检查日期目录
  if [ ! -d "${TODAY_DIR}" ]; then
    warn "今日目录不存在: ${TODAY_DIR}"
    log "  创建今日目录..."
    mkdir -p "${TODAY_DIR}/archive"
    mkdir -p "${TODAY_DIR}/wechat-publish/morning/comic"
    mkdir -p "${TODAY_DIR}/wechat-publish/evening/comic"
    ok "今日目录已创建"
  fi

  # 检查必要工具
  command -v python &>/dev/null || warn "python 未安装（音频生成需要 edge-tts）"
  command -v node  &>/dev/null || warn "node 未安装"

  ok "环境检查完成"
}

# =============================================================================
# 阶段 2：生成早报
# =============================================================================
phase_morning() {
  log "🌅 开始生成早报..."

  MORNING_DIR="${TODAY_DIR}/wechat-publish/morning"

  # 检查关键文件
  if [ -f "${MORNING_DIR}/article.html" ] && [ -f "${MORNING_DIR}/audio.mp3" ]; then
    ok "早报文章和音频已存在"
    local SVG_COUNT=$(ls "${MORNING_DIR}/comic/"*.svg 2>/dev/null | wc -l)
    ok "漫画 SVG: ${SVG_COUNT} 幅"
  else
    warn "早报文件不完整，请手动创建以下文件："
    warn "  - ${MORNING_DIR}/article.html"
    warn "  - ${MORNING_DIR}/audio.mp3"
    warn "  - ${MORNING_DIR}/comic/panel-000.svg ~ panel-005.svg"
  fi
}

# =============================================================================
# 阶段 3：生成晚报
# =============================================================================
phase_evening() {
  log "🌙 开始生成晚报..."

  EVENING_DIR="${TODAY_DIR}/wechat-publish/evening"

  if [ -f "${EVENING_DIR}/article.html" ] && [ -f "${EVENING_DIR}/audio.mp3" ]; then
    ok "晚报文章和音频已存在"
    local SVG_COUNT=$(ls "${EVENING_DIR}/comic/"*.svg 2>/dev/null | wc -l)
    ok "漫画 SVG: ${SVG_COUNT} 幅"
  else
    warn "晚报文件不完整，请手动创建以下文件："
    warn "  - ${EVENING_DIR}/article.html"
    warn "  - ${EVENING_DIR}/audio.mp3"
    warn "  - ${EVENING_DIR}/comic/panel-000.svg ~ panel-008.svg"
  fi
}

# =============================================================================
# 阶段 4：质量检查
# =============================================================================
phase_quality() {
  log "🔎 质量检查..."
  local ERRORS=0

  # 检查各层结构
  for edition in "morning" "evening"; do
    local FILE="${TODAY_DIR}/wechat-publish/${edition}/article.html"
    if [ ! -f "$FILE" ]; then
      err "${edition}: article.html 缺失"
      ERRORS=$((ERRORS + 1))
      continue
    fi

    # Layer 1: 热点速览
    if grep -q "layer1\|l1-grid\|l1-title" "$FILE" 2>/dev/null; then
      ok "${edition}: Layer 1 (热点速览) ✅"
    else
      warn "${edition}: Layer 1 未找到"
    fi

    # Layer 2: 深度解读
    if grep -q "layer2\|l2-title\|h2" "$FILE" 2>/dev/null; then
      ok "${edition}: Layer 2 (深度解读) ✅"
    else
      warn "${edition}: Layer 2 未找到"
    fi

    # Layer 3: 数据
    if grep -q "layer3\|l3-title\|table" "$FILE" 2>/dev/null; then
      ok "${edition}: Layer 3 (数据一览) ✅"
    else
      warn "${edition}: Layer 3 未找到"
    fi

    # SVG 漫画
    local SVG_DIR="${TODAY_DIR}/wechat-publish/${edition}/comic"
    if [ -d "$SVG_DIR" ]; then
      local SC=$(ls "${SVG_DIR}"/*.svg 2>/dev/null | wc -l)
      ok "${edition}: SVG漫画 ${SC} 幅"
    else
      warn "${edition}: SVG目录不存在"
      ERRORS=$((ERRORS + 1))
    fi
  done

  # 音频检查
  for edition in "morning" "evening"; do
    local AUDIO="${TODAY_DIR}/wechat-publish/${edition}/audio.mp3"
    if [ -f "$AUDIO" ]; then
      local SIZE=$(stat -c%s "$AUDIO" 2>/dev/null || stat -f%z "$AUDIO" 2>/dev/null)
      local SIZE_KB=$((SIZE / 1024))
      ok "${edition}: 音频 ${SIZE_KB}KB"
    else
      warn "${edition}: audio.mp3 缺失"
      ERRORS=$((ERRORS + 1))
    fi
  done

  if [ $ERRORS -eq 0 ]; then
    ok "🎉 质量检查全部通过！"
  else
    warn "存在 ${ERRORS} 个问题"
  fi
}

# =============================================================================
# 阶段 4b：生成数据图表
# =============================================================================
phase_charts() {
  log "📊 生成Python数据可视化图表..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/generate-charts.py
  ok "数据图表生成完成"
}

# =============================================================================
# 阶段 4c：漫画质量升级
# =============================================================================
phase_comic_upgrade() {
  log "🎨 升级漫画分镜质量..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/upgrade-comic.py --enhance
  ok "漫画质量升级完成"
}

# =============================================================================
# 阶段 4d：口播音频生成（v2.0 - 自然对话风格）
# =============================================================================
phase_audio_upgrade() {
  log "🎵 生成口播音频（自然对话风格）..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/upgrade-audio.py
  ok "口播音频生成完成"
}

# =============================================================================
# 阶段 4e：角色重建（真实人物图片）
# =============================================================================
phase_rebrand_character() {
  log "🎭 重建角色形象（使用真实人物图片）..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/rebrand-character.py
  ok "角色重建完成"
}

# =============================================================================
# 质量检查
# =============================================================================
phase_q_brand() {
  log "🔎 品牌资产质量检查..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/quality-check.py brand && ok "品牌资产检查通过" || err "品牌资产检查不通过"
}

phase_q_comics() {
  log "🔎 漫画分镜质量检查..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/quality-check.py comics && ok "漫画分镜检查通过" || err "漫画分镜检查不通过"
}

phase_q_articles() {
  log "🔎 文章质量检查..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/quality-check.py articles && ok "文章检查通过" || err "文章检查不通过"
}

phase_q_charts() {
  log "🔎 图表质量检查..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/quality-check.py charts && ok "图表检查通过" || err "图表检查不通过"
}

phase_q_audio() {
  log "🔎 音频质量检查..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/quality-check.py audio && ok "音频检查通过" || err "音频检查不通过"
}

phase_verify() {
  log "🔎 最终全量验证..."
  cd "${ROOT_DIR}"
  PYTHONIOENCODING=utf-8 python scripts/quality-check.py && ok "全量验证通过" || err "全量验证发现问题"
}

# =============================================================================
# 阶段 5：预览
# =============================================================================
phase_preview() {
  log "📋 ${DATE_FORMATTED} 产出预览"
  echo ""
  echo "  🌅 早报：${TODAY_DIR}/wechat-publish/morning/"
  ls -lh "${TODAY_DIR}/wechat-publish/morning/" 2>/dev/null | grep -v "^total" | awk '{print "    " $0}'
  echo ""
  echo "  🌙 晚报：${TODAY_DIR}/wechat-publish/evening/"
  ls -lh "${TODAY_DIR}/wechat-publish/evening/" 2>/dev/null | grep -v "^total" | awk '{print "    " $0}'
  echo ""
  echo "  📁 归档：${TODAY_DIR}/archive/"
  ls -lh "${TODAY_DIR}/archive/" 2>/dev/null | grep -v "^total" | awk '{print "    " $0}'
  echo ""
  echo "  📐 品牌VI:"
  echo "    - 命名方案:  docs/naming-scheme.md"
  echo "    - 品牌指南:  docs/brand-guidelines.md"
  echo "    - 注册指南:  docs/wechat-registration-guide.md"
  echo "    - 头像:      docs/assets/avatar.svg"
  echo "    - 头图:      docs/assets/header.svg"
  echo "    - 封面(早):  docs/assets/cover-morning.svg"
  echo "    - 封面(晚):  docs/assets/cover-evening.svg"
}

# =============================================================================
# 执行入口
# =============================================================================
case "${1:-}" in
  --morning)
    phase_check_env
    phase_morning
    ;;
  --evening)
    phase_check_env
    phase_evening
    ;;
  --preview)
    phase_preview
    ;;
  --quality)
    phase_verify
    ;;
  --verify)
    phase_verify
    ;;
  --full)
    log "=========================================="
    log "📡 扬说财经 · 全量生产流水线（含质量检查）"
    log "📅 ${DATE_FORMATTED}"
    log "=========================================="
    echo ""
    phase_check_env
    echo ""
    log "📊 阶段1：数据图表"
    phase_charts
    phase_q_charts
    echo ""
    log "🎭 阶段2：角色重建"
    phase_rebrand_character
    phase_q_brand
    echo ""
    log "🎨 阶段3：漫画升级"
    phase_comic_upgrade
    phase_q_comics
    echo ""
    log "📝 阶段4：文章"
    phase_morning
    phase_evening
    phase_q_articles
    echo ""
    log "🎵 阶段5：口播音频"
    phase_audio_upgrade
    phase_q_audio
    echo ""
    log "🏁 阶段6：最终验证"
    phase_verify
    echo ""
    phase_preview
    log "=========================================="
    ok "全量流水线执行完毕"
    log "=========================================="
    ;;
  "")
    log "=========================================="
    log "📡 扬说财经 · 日更流水线"
    log "📅 ${DATE_FORMATTED}"
    log "=========================================="
    echo ""
    phase_check_env
    echo ""
    phase_morning
    echo ""
    phase_evening
    echo ""
    phase_quality
    echo ""
    phase_preview
    log "=========================================="
    ok "流水线执行完毕"
    log "=========================================="
    ;;
  *)
    echo "用法: $0 [--morning|--evening|--preview|--quality|--full]"
    exit 1
    ;;
esac
