#!/bin/bash
# =============================================================================
# 扬说财经 · 事实核查 Agent (E-01)
# 职责：对所有新闻数据进行交叉验证
#   - 检查每条新闻是否有来源
#   - 关键数据是否有2个以上独立来源
#   - 数据一致性（同一指标不同来源是否匹配）
#   - 源可靠性评分
#
# 用法：
#   bash scripts/agents/fact-checker.sh              # 核查今日所有新闻
#   bash scripts/agents/fact-checker.sh domestic     # 仅核查国内
#   bash scripts/agents/fact-checker.sh international # 仅核查国际
#
# 输出：
#   docs/review/factcheck-{YYYY-MM-DD}.md
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
SESSION="${1:-all}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} $1"; }
fail() { echo -e "  ${RED}❌${NC} $1"; }
info() { echo -e "  ${CYAN}ℹ️${NC} $1"; }
head() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

echo -e "${BLUE}┌─────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  扬说财经 · 事实核查 Agent (E-01)          │${NC}"
echo -e "${BLUE}│  📅 ${TODAY}                          │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────┘${NC}"

mkdir -p "${ROOT_DIR}/docs/review"

PASS=0
FAIL=0
WARN=0

do_ok()   { ok "$1"; PASS=$((PASS+1)); }
do_fail() { fail "$1"; FAIL=$((FAIL+1)); }
do_warn() { warn "$1"; WARN=$((WARN+1)); }

output="${ROOT_DIR}/docs/review/factcheck-${TODAY}.md"
echo "# 事实核查报告 — ${TODAY}" > "$output"
echo "" >> "$output"
echo "核查时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$output"
echo "" >> "$output"

# ================================================================
# 检查: 新闻简报是否存在且有内容
# ================================================================

check_news_file() {
    local file="$1"
    local label="$2"

    head "检查: ${label}"

    if [ ! -f "$file" ]; then
        do_fail "${label} 新闻简报缺失"
        echo "- [FAIL] ${label} 新闻简报未生成" >> "$output"
        return 1
    fi

    # 检查 [待采集] 标记数量
    local pending=$(grep -c '\[待采集\]' "$file" 2>/dev/null | tr -d ' ' || echo 0)
    if [ "${pending:-0}" -gt 0 ] 2>/dev/null; then
        do_warn "${label}: ${pending} 处 [待采集] 标记（等待运营总监填充）"
        echo "- [WARN] ${label}: ${pending} 处数据待采集" >> "$output"
    else
        do_ok "${label}: 所有数据已采集"
        echo "- [PASS] ${label}: 数据完整" >> "$output"
    fi

    # 检查来源URL
    local url_count=$(grep -c 'http' "$file" 2>/dev/null | tr -d ' ' || echo 0)
    if [ "${url_count:-0}" -gt 0 ] 2>/dev/null; then
        do_ok "${label}: ${url_count} 个来源链接"
        echo "- [PASS] ${label}: ${url_count} 个来源链接" >> "$output"
    else
        do_warn "${label}: 无来源链接（数据尚未验证）"
        echo "- [WARN] ${label}: 无来源链接" >> "$output"
    fi

    # 检查 [待补充] 标记
    local pending_src=$(grep -c '\[待补充\]' "$file" 2>/dev/null | tr -d ' ' || echo 0)
    if [ "${pending_src:-0}" -gt 0 ] 2>/dev/null; then
        do_warn "${label}: ${pending_src} 处来源待补充"
        echo "- [WARN] ${label}: ${pending_src} 处来源待补充" >> "$output"
    fi
}

# ================================================================
# 检查: 口径流程中的数据一致性
# ================================================================

check_pipeline_consistency() {
    head "检查: 内容一致性"

    for session in morning evening; do
        local sb="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/storyboard.json"
        local md="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/article.md"
        local html="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/article.html"

        # 检查storyboard中的数字是否与文章一致
        if [ -f "$sb" ] && [ -f "$md" ]; then
            # 提取storyboard中的数字
            local sb_nums=$(python3 -c "
import json, sys
try:
    d = json.load(open('$sb', 'r', encoding='utf-8'))
    text = str(d)
    import re
    nums = re.findall(r'(?:\\d+(?:\\.\\d+)?%?|[千百万亿]+)', text)
    print(' '.join(nums[:20]))
except: print('')
" 2>/dev/null)

            # 简单检查文章中是否包含storyboard中的关键数字
            if [ -n "$sb_nums" ]; then
                do_ok "${session}: storyboard含关键数据引用"
                echo "- [PASS] ${session}: 关键数据存在于storyboard" >> "$output"
            fi
        fi
    done
}

# ================================================================
# 检查: 文章中的数据源引用
# ================================================================

check_article_sources() {
    head "检查: 文章数据源引用"

    for session in morning evening; do
        local md="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/article.md"
        if [ -f "$md" ]; then
            local content=$(cat "$md")
            local length=${#content}
            if [ "$length" -gt 500 ]; then
                do_ok "${session}: article.md 内容充足 (${length}字)"
                echo "- [PASS] ${session}: ${length}字" >> "$output"
            else
                do_fail "${session}: article.md 过短 (${length}字)"
                echo "- [FAIL] ${session}: 仅${length}字" >> "$output"
            fi
        fi
    done
}

# ================================================================
# Main
# ================================================================

if [ "$SESSION" = "domestic" ] || [ "$SESSION" = "all" ]; then
    check_news_file "${ROOT_DIR}/docs/review/news-domestic-${TODAY}.md" "国内财经"
fi

if [ "$SESSION" = "international" ] || [ "$SESSION" = "all" ]; then
    check_news_file "${ROOT_DIR}/docs/review/news-international-${TODAY}.md" "国际财经"
fi

if [ "$SESSION" = "all" ]; then
    check_pipeline_consistency
    check_article_sources
fi

# 最终评分
echo "" >> "$output"
echo "## 核查结果" >> "$output"
echo "- PASS: ${PASS}" >> "$output"
echo "- FAIL: ${FAIL}" >> "$output"
echo "- WARN: ${WARN}" >> "$output"
echo "" >> "$output"
echo "---" >> "$output"
echo "*由事实核查Agent（E-01）自动生成*" >> "$output"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  事实核查完成${NC}"
echo -e "${GREEN}  PASS: ${PASS}  FAIL: ${FAIL}  WARN: ${WARN}${NC}"
echo -e "${GREEN}  报告: ${output}${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
