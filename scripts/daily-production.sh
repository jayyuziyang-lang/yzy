#!/bin/bash
# ============================================================
# 扬说财经 · 每日生产综合工作流 v2.0
#
# 新的6阶段生产流水线，带质量门控：
#   Phase 1: 新闻采集与事实核查 (必须通过)
#   Phase 2: 数据可视化 (失败则警告不阻塞)
#   Phase 3: 内容生产 (文章 + 漫画 + 音频，并行)
#   Phase 4: 质量审查 (必须通过)
#   Phase 5: 索引更新
#   Phase 6: 发布部署
#
# 用法:
#   bash scripts/daily-production.sh              # 完整流程
#   bash scripts/daily-production.sh --skip-factcheck  # 跳过事实核查
#   bash scripts/daily-production.sh --edition evening  # 只做晚报
#   bash scripts/daily-production.sh --deploy-only      # 只做部署
# ============================================================

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DATE=$(date +%Y-%m-%d)
START_TIME=$(date +%s)

PASS=0
FAIL=0
WARN=0

# ============================================================
# 颜色定义
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { printf "${BLUE}[INFO]${NC}  %s\n" "$1"; }
ok()    { printf "${GREEN}[PASS]${NC}  %s\n" "$1"; ((PASS++)); }
fail()  { printf "${RED}[FAIL]${NC}  %s\n" "$1"; ((FAIL++)); }
warn()  { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; ((WARN++)); }

# ============================================================
# Phase 1: 新闻采集与事实核查
# ============================================================
phase1_factcheck() {
    echo ""
    echo "═══════════════════════════════════════════════"
    info "Phase 1/6: 新闻采集与事实核查"
    echo "═══════════════════════════════════════════════"

    if [ ! -f "scripts/factcheck-news.py" ]; then
        fail "factcheck-news.py 不存在，请先创建"
        return 1
    fi

    # 事实核查所有版次
    python scripts/factcheck-news.py --check-script --output
    local result=$?

    if [ $result -eq 0 ]; then
        ok "事实核查全部通过"
    else
        fail "事实核查发现问题，请修复后重试"
        echo ""
        echo "  📄 查看报告: cat wechat-publish/factcheck-report.md"
        echo "  🔧 修复后重新运行: bash scripts/daily-production.sh --skip-factcheck"
        return 1
    fi
}

# ============================================================
# Phase 2: 数据可视化
# ============================================================
phase2_charts() {
    echo ""
    echo "═══════════════════════════════════════════════"
    info "Phase 2/6: 数据可视化"
    echo "═══════════════════════════════════════════════"

    if [ ! -f "scripts/generate-charts.py" ]; then
        warn "generate-charts.py 不存在，跳过"
        return 0
    fi

    python scripts/generate-charts.py
    local result=$?

    if [ $result -eq 0 ]; then
        ok "8张数据图表生成成功"
    else
        warn "图表生成失败（不阻塞流程）"
    fi
}

# ============================================================
# Phase 3: 内容生产（占位 — 由人工创作）
# ============================================================
phase3_content() {
    echo ""
    echo "═══════════════════════════════════════════════"
    info "Phase 3/6: 内容生产"
    echo "═══════════════════════════════════════════════"

    local edition=$1
    local dir="$ROOT/$DATE/wechat-publish/$edition"

    if [ -f "$dir/article.html" ]; then
        ok "$edition/article.html 已存在"
    else
        fail "$edition/article.html 缺失，请在 $dir 创建"
        return 1
    fi

    if [ -f "$dir/script.txt" ]; then
        ok "$edition/script.txt 已存在"
    else
        warn "$edition/script.txt 缺失"
    fi

    # 检查音频（如有口播稿但无音频，自动生成）
    if [ -f "$dir/script.txt" ] && [ ! -f "$dir/audio.mp3" ]; then
        info "检测到script.txt但无audio.mp3，自动生成..."
        if [ -f "scripts/upgrade-audio.py" ]; then
            python scripts/upgrade-audio.py --edition "$edition" --date "$DATE" 2>/dev/null && \
                ok "audio.mp3 已自动生成" || \
                warn "音频生成失败"
        else
            warn "upgrade-audio.py 不存在，请手动生成音频"
        fi
    fi
}

# ============================================================
# Phase 4: 质量审查
# ============================================================
phase4_quality() {
    echo ""
    echo "═══════════════════════════════════════════════"
    info "Phase 4/6: 质量审查"
    echo "═══════════════════════════════════════════════"

    if [ ! -f "scripts/quality-check.py" ]; then
        fail "quality-check.py 不存在"
        return 1
    fi

    python scripts/quality-check.py
    local result=$?

    if [ $result -eq 0 ]; then
        ok "质量检查全部通过"
    else
        fail "质量检查发现问题，请修复后重试"
        return 1
    fi
}

# ============================================================
# Phase 5: 索引更新
# ============================================================
phase5_index() {
    echo ""
    echo "═══════════════════════════════════════════════"
    info "Phase 5/6: 索引更新"
    echo "═══════════════════════════════════════════════"

    if [ ! -f "scripts/update-index.py" ]; then
        fail "update-index.py 不存在"
        return 1
    fi

    python scripts/update-index.py
    local result=$?

    if [ $result -eq 0 ]; then
        ok "索引更新完成"
    else
        fail "索引更新失败"
        return 1
    fi
}

# ============================================================
# Phase 6: 发布部署
# ============================================================
phase6_deploy() {
    echo ""
    echo "═══════════════════════════════════════════════"
    info "Phase 6/6: 发布部署"
    echo "═══════════════════════════════════════════════"

    # 检查是否有 git 仓库
    if [ ! -d ".git" ]; then
        fail "不是 git 仓库，跳过部署"
        return 1
    fi

    # 检查是否有变更
    if git diff --quiet && git diff --cached --quiet; then
        info "无变更，跳过部署"
        return 0
    fi

    # 查看变更
    git status --short
    echo ""

    info "准备提交并推送..."
    echo ""
    echo "  执行以下命令手动部署："
    echo "    git add ."
    echo "    git commit -m \"扬说财经日报 $DATE\""
    echo "    git push origin main"
    echo ""
    warn "自动部署功能需确认，请手动执行以上命令"
}

# ============================================================
# 打印报告
# ============================================================
print_report() {
    local duration=$(( $(date +%s) - START_TIME ))
    echo ""
    echo "═══════════════════════════════════════════════"
    info "每日生产报告"
    echo "═══════════════════════════════════════════════"
    echo "  日期:     $DATE"
    echo "  耗时:     ${duration}s"
    echo "  结果:     $(ok_count)/$(total_count) 通过"
    echo ""
    echo "  PASS: $PASS   FAIL: $FAIL   WARN: $WARN"
    echo "═══════════════════════════════════════════════"

    if [ $FAIL -gt 0 ]; then
        echo ""
        warn "存在 $FAIL 个失败项，请修复后重新运行"
        return 1
    fi

    echo ""
    ok "生产流程全部完成!"
    return 0
}

ok_count() { echo "$PASS"; }
total_count() { echo $((PASS + FAIL + WARN)); }

# ============================================================
# Main
# ============================================================
main() {
    local skip_factcheck=false
    local edition=""
    local deploy_only=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-factcheck) skip_factcheck=true; shift ;;
            --edition) edition="$2"; shift 2 ;;
            --deploy-only) deploy_only=true; shift ;;
            *) echo "未知参数: $1"; exit 1 ;;
        esac
    done

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│   扬说财经 · 每日生产流水线                       │"
    echo "│   日期: $DATE                              │"
    echo "└─────────────────────────────────────────────────┘"

    if [ "$deploy_only" = true ]; then
        phase5_index || true
        phase6_deploy
        print_report
        return $?
    fi

    # Phase 1: 事实核查（除非跳过）
    if [ "$skip_factcheck" = false ]; then
        phase1_factcheck || { print_report; return 1; }
    else
        info "Phase 1/6: 新闻采集 (已跳过事实核查)"
    fi

    # Phase 2: 数据可视化
    phase2_charts

    # Phase 3: 内容生产
    if [ -n "$edition" ]; then
        phase3_content "$edition" || { print_report; return 1; }
    else
        phase3_content "morning" || { print_report; return 1; }
        phase3_content "evening" || { print_report; return 1; }
    fi

    # Phase 4: 质量审查（门控）
    phase4_quality || { print_report; return 1; }

    # Phase 5: 索引更新
    phase5_index || { print_report; return 1; }

    # Phase 6: 部署
    phase6_deploy

    print_report
}

main "$@"
