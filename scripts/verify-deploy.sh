#!/bin/bash
# =============================================================
# 部署后验证脚本
# 部署完成后，模拟用户访问验证所有关键页面
# =============================================================
# 用法: bash scripts/verify-deploy.sh
# =============================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ERRORS=0

check_url() {
    local url="$1" name="$2"
    local code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    if [ "$code" = "200" ]; then
        echo -e "  ${GREEN}✅${NC} $code $name"
    else
        echo -e "  ${RED}❌${NC} $code $name"
        ERRORS=$((ERRORS+1))
    fi
}

check_content() {
    local url="$1" name="$2" keyword="$3"
    local body=$(curl -s "$url" 2>/dev/null || echo "")
    if echo "$body" | grep -q "$keyword"; then
        echo -e "  ${GREEN}✅${NC} 内容验证通过: $name (含\"$keyword\")"
    else
        echo -e "  ${RED}❌${NC} 内容验证失败: $name (缺少\"$keyword\")"
        ERRORS=$((ERRORS+1))
    fi
}

# 获取站点URL
OWNER="jayyuziyang-lang"
REPO="yzy"
SITE_URL="https://${OWNER}.github.io/${REPO}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  扬说财经 · 部署验证${NC}"
echo -e "${BLUE}========================================${NC}"

# ── 1. 等待部署 ──
echo -e "\n⏳ 等待部署完成..."
for i in $(seq 1 36); do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}/" 2>/dev/null || echo "000")
    if [ "$CODE" = "200" ]; then
        echo -e "  ${GREEN}✅${NC} 部署完成 ($((i*5))秒)"
        break
    fi
    if [ "$i" -eq 36 ]; then
        echo -e "  ${RED}❌${NC} 部署超时！"
        exit 1
    fi
    sleep 5
done

# ── 2. 验证关键 URL ──
echo -e "\n🔗 关键 URL 检查..."
check_url "${SITE_URL}/" "首页"
check_url "${SITE_URL}/data/articles.js" "数据文件 articles.js"
check_url "${SITE_URL}/data/articles.json" "数据文件 articles.json"

# ── 3. 验证文章页 ──
echo -e "\n📝 文章页检查..."
TODAY=$(date +%Y-%m-%d)
if curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}/${TODAY}/wechat-publish/morning/article.html" 2>/dev/null | grep -q 200; then
    echo -e "  ${GREEN}✅${NC} 200 早报: ${TODAY}/morning/article.html"
else
    echo -e "  ${YELLOW}⚠️${NC} ${TODAY} 早报不可用，检查最近日期..."
    # 从 articles.json 找最新日期
    LATEST=$(curl -s "${SITE_URL}/data/articles.json" 2>/dev/null | grep -o '"latest_date":"[^"]*"' | cut -d'"' -f4 || echo "")
    if [ -n "$LATEST" ]; then
        echo "  使用最新日期: $LATEST"
        check_url "${SITE_URL}/${LATEST}/wechat-publish/morning/article.html" "早报 ($LATEST)"
        check_url "${SITE_URL}/${LATEST}/wechat-publish/evening/article.html" "晚报 ($LATEST)"
    fi
fi

# ── 4. 内容完整性验证 ──
echo -e "\n✅ 内容完整性验证..."
# 首页必须包含预渲染的文章链接
check_content "${SITE_URL}/" "首页预渲染" "edition-morning"
check_content "${SITE_URL}/" "首页预渲染" "edition-evening"
# 数据文件必须包含有效 JSON/JS
check_content "${SITE_URL}/data/articles.json" "articles.json" "articles"
check_content "${SITE_URL}/data/articles.js" "articles.js" "ARTICLES_BY_DATE"

# ── 5. 预热CDN ──
echo -e "\n🌐 预热 CDN..."
for url in \
    "${SITE_URL}/" \
    "${SITE_URL}/data/articles.js" \
    "${SITE_URL}/data/articles.json"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    echo -e "  $CODE  $url"
done

# ── 汇总 ──
echo ""
echo -e "${BLUE}========================================${NC}"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "  ${GREEN}✅ 全部验证通过！${NC}"
    echo -e "  ${GREEN}  访问地址: $SITE_URL${NC}"
else
    echo -e "  ${RED}❌ $ERRORS 个验证失败，请排查${NC}"
fi
echo -e "${BLUE}========================================${NC}"
exit $ERRORS
