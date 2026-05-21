#!/bin/bash
# =============================================================
# 部署前自动检查脚本
# 每次 push 前运行，拦截常见问题
# =============================================================
# 用法: bash scripts/pre-deploy-check.sh
# 返回值: 0 = 通过, 1 = 有警告, 2 = 有错误
# =============================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ERRORS=0; WARNINGS=0

check_pass() { echo -e "  ${GREEN}✅${NC} $1"; }
check_warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; WARNINGS=$((WARNINGS+1)); }
check_fail() { echo -e "  ${RED}❌ $1${NC}"; ERRORS=$((ERRORS+1)); }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  扬说财经 · 部署前自动检查${NC}"
echo -e "${BLUE}========================================${NC}"

# ── 1. 检查 data/articles.js 有今天的日期 ──
echo -e "\n📄 数据文件检查..."
TODAY=$(date +%Y-%m-%d)
if grep -q "$TODAY" data/articles.js 2>/dev/null; then
    check_pass "articles.js 包含今天 ($TODAY) 的数据"
else
    check_warn "articles.js 未包含今天的日期 — 确认是否需要更新"
fi

# ── 2. articles.json 生成时间戳检查 ──
echo -e "\n⏰ 时间戳检查..."
if grep -q "$TODAY" data/articles.json 2>/dev/null; then
    check_pass "articles.json 生成时间为今天"
else
    check_warn "articles.json 生成时间不是今天，可能未刷新"
fi

# ── 3. index.html 预渲染日期检查 ──
echo -e "\n🏠 首页预渲染检查..."
PRERENDER_DATE=$(grep -o 'data-date="[^"]*"' index.html 2>/dev/null | cut -d'"' -f2 || echo "")
if [ -n "$PRERENDER_DATE" ]; then
    if [ "$PRERENDER_DATE" = "$TODAY" ]; then
        check_pass "首页预渲染日期 = $PRERENDER_DATE ✓"
    else
        check_warn "首页预渲染日期为 $PRERENDER_DATE，不是今天 $TODAY"
    fi
else
    check_warn "未找到 data-date 属性，确认首页是否有预渲染内容"
fi

# ── 4. 检查文章 HTML 文件是否存在 ──
echo -e "\n📝 文章文件检查..."
MORNING_HTML="${TODAY}/wechat-publish/morning/article.html"
EVENING_HTML="${TODAY}/wechat-publish/evening/article.html"
if [ -f "$MORNING_HTML" ]; then
    check_pass "早报文件存在: $MORNING_HTML"
else
    check_warn "早报文件不存在: $MORNING_HTML"
fi
if [ -f "$EVENING_HTML" ]; then
    check_pass "晚报文件存在: $EVENING_HTML"
else
    check_warn "晚报文件不存在: $EVENING_HTML"
fi

# ── 5. 对比 index.html 中的链接与实际文件 ──
echo -e "\n🔗 链接一致性检查..."
MORNING_IN_HTML=$(grep -c "morning/article.html" index.html 2>/dev/null || echo 0)
EVENING_IN_HTML=$(grep -c "evening/article.html" index.html 2>/dev/null || echo 0)
if [ "$MORNING_IN_HTML" -gt 0 ]; then
    check_pass "首页包含早报链接 ($MORNING_IN_HTML 处)"
else
    check_fail "首页缺少早报链接！"
fi
if [ "$EVENING_IN_HTML" -gt 0 ]; then
    check_pass "首页包含晚报链接 ($EVENING_IN_HTML 处)"
else
    check_fail "首页缺少晚报链接！"
fi

# ── 6. 检查 deploy.sh 关键函数 ──
echo -e "\n🚀 部署脚本检查..."
if grep -q "CDN.*预热\|cdn.*warm" deploy.sh 2>/dev/null; then
    check_pass "deploy.sh 包含 CDN 预热步骤"
else
    check_fail "deploy.sh 缺少 CDN 预热！"
fi

# ── 7. 检查部署版本描述文件 ──
echo -e "\n📌 版本标记检查..."
if [ -f "deploy-version.txt" ]; then
    check_pass "部署版本文件存在"
else
    check_warn "无 deploy-version.txt（GitHub Actions 会自动生成）"
fi

# ── 8. 检查未跟踪的文件 ──
echo -e "\n📦 Git 状态检查..."
UNTRACKED=$(git status --porcelain 2>/dev/null | grep '^??' | wc -l)
MODIFIED=$(git status --porcelain 2>/dev/null | grep -v '^??' | wc -l)
echo "  未跟踪: $UNTRACKED 个文件 | 已修改: $MODIFIED 个文件"

# ── 汇总 ──
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "  错误: ${ERRORS}  警告: ${WARNINGS}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}❌ 存在 $ERRORS 个错误，请修复后再部署！${NC}"
    exit 2
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  存在 $WARNINGS 个警告，建议检查后部署${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 全部检查通过，可以部署！${NC}"
    exit 0
fi
