#!/bin/bash
# =============================================================================
# 扬说财经 · 每日复盘 Agent (F-01)
# 职责：
#   每日工作总结，问题追踪，改进日志
#       记录当天所有产出环节的问题和优化点
#       追踪未解决问题的状态
#       生成可执行的明日改进清单
#
# 用法：
#   bash scripts/agents/daily-review.sh          # 完整复盘（早晚报都生产后）
#   bash scripts/agents/daily-review.sh quick    # 快速检查
#   bash scripts/agents/daily-review.sh history  # 查看历史趋势
#
# 输出：
#   docs/review/daily-{YYYY-MM-DD}.md (每日复盘记录)
#   docs/review/improvement-log.md (持续改进日志)
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
MODE="${1:-full}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} $1"; }
fail() { echo -e "  ${RED}❌${NC} $1"; }
info() { echo -e "  ${CYAN}ℹ️${NC} $1"; }
head() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

echo -e "${BLUE}┌─────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  扬说财经 · 每日复盘 Agent (F-01)          │${NC}"
echo -e "${BLUE}│  📅 ${TODAY}                          │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────┘${NC}"

mkdir -p "${ROOT_DIR}/docs/review"

PASS=0
FAIL=0
WARN=0
ISSUES=()

# ================================================================
# 1. 产出完整性检查
# ================================================================
check_completeness() {
    head "产出完整性"

    for session in morning evening; do
        local dir="${ROOT_DIR}/${TODAY}/wechat-publish/${session}"
        if [ ! -d "$dir" ]; then
            warn "${session}: 目录不存在"
            ISSUES+=("${session}: 产出目录缺失")
            continue
        fi

        local all_ok=true
        for f in storyboard.json article.md article.html; do
            if [ ! -f "${dir}/${f}" ]; then
                fail "${session}: ${f} 缺失"
                ISSUES+=("${session}: ${f} 缺失")
                all_ok=false
            fi
        done

        # 漫画
        local comic_dir="${dir}/comic"
        if [ -d "$comic_dir" ]; then
            local svg_count=$(ls "$comic_dir"/*.svg 2>/dev/null | wc -l)
            if [ "$svg_count" -gt 0 ]; then
                ok "${session}: ${svg_count}幅漫画"
            else
                warn "${session}: 漫画SVG为空"
                ISSUES+=("${session}: 漫画SVG未生成")
            fi
        fi

        # 脚本
        if [ -f "${dir}/script.txt" ]; then
            local sc=$(wc -c < "${dir}/script.txt" 2>/dev/null || echo 0)
            ok "${session}: 口播脚本 (${sc} chars)"
        else
            warn "${session}: 口播脚本未生成"
            ISSUES+=("${session}: 口播脚本待生成")
        fi

        # 音频
        if [ -f "${dir}/audio.mp3" ]; then
            local sz=$(stat -c%s "${dir}/audio.mp3" 2>/dev/null || stat -f%z "${dir}/audio.mp3" 2>/dev/null || echo 0)
            local sz_kb=$((sz / 1024))
            ok "${session}: 音频 (${sz_kb} KB)"
        else
            warn "${session}: 音频未生成"
            ISSUES+=("${session}: 音频待生成")
        fi

        if $all_ok; then
            PASS=$((PASS+1))
        else
            FAIL=$((FAIL+1))
        fi
    done
}

# ================================================================
# 2. 质量检查结果汇总
# ================================================================
check_quality() {
    head "质量检查结果"

    if [ -f "${ROOT_DIR}/scripts/quality-check.py" ]; then
        local result=$(PYTHONIOENCODING=utf-8 python "${ROOT_DIR}/scripts/quality-check.py" 2>&1)
        local pass_count=$(echo "$result" | grep -c "\[PASS\]")
        local fail_count=$(echo "$result" | grep -c "\[FAIL\]")

        if [ "$fail_count" -eq 0 ]; then
            ok "全部 ${pass_count} 项检查通过"
        else
            warn "通过 ${pass_count} 项，失败 ${fail_count} 项"
            ISSUES+=("质量检查: ${fail_count} 项失败")
            # 提取失败项
            echo "$result" | grep "\[FAIL\]" | while read line; do
                warn "  -> $line"
            done
        fi
    else
        warn "quality-check.py 不存在"
        ISSUES+=("质量检查脚本缺失")
    fi
}

# ================================================================
# 3. 今日改进记录
# ================================================================
generate_review() {
    head "生成复盘报告"

    local output="${ROOT_DIR}/docs/review/daily-${TODAY}.md"

    cat > "$output" << SECTION
# 每日复盘 — ${TODAY}

## 基本信息
| 项目 | 内容 |
|------|------|
| 日期 | ${TODAY} |
| 复盘时间 | $(date '+%Y-%m-%d %H:%M:%S') |
| 复盘Agent | F-01 每日复盘员 |

## 今日产出
- 早报: $( [ -d "${ROOT_DIR}/${TODAY}/wechat-publish/morning" ] && echo "✅" || echo "❌")
- 晚报: $( [ -d "${ROOT_DIR}/${TODAY}/wechat-publish/evening" ] && echo "✅" || echo "❌")

## 质量检查
- [待补充: 运行 python scripts/quality-check.py 获取结果]

## 发现问题
SECTION

    if [ ${#ISSUES[@]} -eq 0 ]; then
        echo "暂无发现问题" >> "$output"
        ok "今日无待解决问题"
    else
        for issue in "${ISSUES[@]}"; do
            echo "- ${issue}" >> "$output"
        done
        echo "" >> "$output"
        warn "发现 ${#ISSUES[@]} 个问题"
    fi

    cat >> "$output" << SECTION

## 改进建议
1. [待运营总监补充]

## 明日重点
1. [待运营总监补充]

## 学到的经验
- [待补充]

---
*本报告由每日复盘Agent（F-01）自动生成。*
SECTION

    ok "复盘报告已保存: ${output}"

    # 更新改进日志
    local improvement_log="${ROOT_DIR}/docs/review/improvement-log.md"
    if [ ! -f "$improvement_log" ]; then
        cat > "$improvement_log" << 'LOG'
# 扬说财经 · 持续改进日志

> 记录每日发现的问题和改进措施
> 目标：问题不过夜，每天都在进步

## 格式
| 日期 | 问题 | 影响 | 解决方案 | 状态 |
|------|------|------|---------|------|
| YYYY-MM-DD | 问题描述 | 影响范围 | 如何处理 | ✅/🔄/❌ |

---
LOG
    fi

    # 追加今日条目
    if [ ${#ISSUES[@]} -gt 0 ]; then
        echo "" >> "$improvement_log"
        for issue in "${ISSUES[@]}"; do
            echo "| ${TODAY} | ${issue} | 产出质量 | [待解决] | 🔄 |" >> "$improvement_log"
        done
        ok "改进日志已更新"
    fi
}

# ================================================================
# 4. 历史趋势（快速查看最近复盘）
# ================================================================
show_history() {
    head "历史复盘概览"

    local review_dir="${ROOT_DIR}/docs/review"
    local files=($(ls -t "$review_dir"/daily-*.md 2>/dev/null))

    if [ ${#files[@]} -eq 0 ]; then
        info "暂无历史复盘记录"
        return
    fi

    info "最近的复盘记录:"
    for f in "${files[@]:0:7}"; do
        local date_part=$(basename "$f" | sed 's/daily-//;s/\.md//')
        if grep -q "发现问题" "$f" 2>/dev/null; then
            local issues=$(grep -c "^- " "$f" 2>/dev/null || echo 0)
            if [ "$issues" -gt 1 ]; then
                warn "  ${date_part}: ${issues} 个问题"
            else
                ok "  ${date_part}: 无问题"
            fi
        fi
    done

    echo ""
    # 改进日志摘要
    if [ -f "$review_dir/improvement-log.md" ]; then
        local open_items=$(grep -c "🔄" "$review_dir/improvement-log.md" 2>/dev/null || echo 0)
        local resolved_items=$(grep -c "✅" "$review_dir/improvement-log.md" 2>/dev/null || echo 0)
        info "改进追踪: ${open_items} 进行中 / ${resolved_items} 已完成"
    fi
}

# ================================================================
# Main
# ================================================================

case "$MODE" in
    quick)
        check_completeness
        check_quality
        echo ""
        info "快速复盘完成"
        ;;
    full)
        check_completeness
        check_quality
        generate_review
        ;;
    history)
        show_history
        ;;
    *)
        echo "用法: bash scripts/agents/daily-review.sh {full|quick|history}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  每日复盘完成${NC}"
echo -e "${GREEN}  详情: ${ROOT_DIR}/docs/review/${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
