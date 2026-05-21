#!/bin/bash
# =============================================================
# 扬说财经 · 一键部署脚本
# 提交每日内容并推送到 GitHub，自动触发 Pages 部署
#
# 用法:
#   bash deploy.sh "2026-05-21 晚报"    # 提交并推送
#   bash deploy.sh --status              # 查看部署状态
#   bash deploy.sh --url                 # 查看 Pages 地址
# =============================================================

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  扬说财经 · 部署工具${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查是否在 git 仓库中
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}[!] 尚未初始化 git 仓库${NC}"
    echo "  请先运行以下命令:"
    echo "    git init"
    echo "    git add ."
    echo "    git commit -m '初始提交'"
    echo "    git remote add origin git@github.com:jayyuziyang-lang/yzy.git"
    echo "    git push -u origin main"
    echo ""
    echo "  然后在 GitHub 上启用 Pages:"
    echo "    仓库 → Settings → Pages → Source: GitHub Actions"
    exit 1
fi

# 检查远程仓库
REMOTE=$(git remote -v 2>/dev/null | head -1 || true)
if [ -z "$REMOTE" ]; then
    echo -e "${YELLOW}[!] 未配置远程仓库${NC}"
    echo "  请添加远程仓库:"
    echo "    git remote add origin git@github.com:jayyuziyang-lang/yzy.git"
    exit 1
fi

# --status: 查看部署状态
if [ "$1" = "--status" ]; then
    echo -e "\n最近提交:"
    git log --oneline -5
    echo -e "\n远程仓库:"
    echo "  $REMOTE"
    echo -e "\n部署状态: https://github.com/$(git remote -v | head -1 | awk '{print $2}' | sed 's/.*github.com[:\/]//;s/\.git//')/actions"
    exit 0
fi

# --url: 查看 Pages 地址
if [ "$1" = "--url" ]; then
    REPO=$(git remote -v | head -1 | awk '{print $2}' | sed 's/.*github.com[:\/]//;s/\.git//')
    echo "https://$(echo $REPO | cut -d/ -f1).github.io/$(echo $REPO | cut -d/ -f2)/"
    exit 0
fi

# 提交信息
COMMIT_MSG="${1:-每日财经内容更新 $(date +%Y-%m-%d)}"

# 更新文章索引
echo -e "\n📊 更新文章索引..."
python scripts/update-index.py || {
    echo -e "${YELLOW}[!] 索引更新失败!${NC}"
    echo "  python scripts/update-index.py 出错，请检查脚本"
    echo "  跳过索引更新，继续部署..."
}

# 健康检查
echo -e "\n🏥 站点健康检查..."
python scripts/site-health.py 2>/dev/null || echo "  (skip — 非阻塞)"

# 部署前自动检查
echo -e "\n🔍 运行部署前检查..."
if [ -f "scripts/pre-deploy-check.sh" ]; then
    bash scripts/pre-deploy-check.sh || true  # 仅提示，不阻断部署
else
    echo "  (pre-deploy-check.sh 不存在，跳过)"
fi

echo -e "\n📦 提交信息: $COMMIT_MSG"
echo ""

# 添加并提交
git add .
git status --short | head -20
echo ""

echo -e "📤 提交中..."
git commit -m "$COMMIT_MSG" 2>/dev/null || echo "  无新变更"

echo -e "📤 推送到远程..."
git push 2>&1 || {
    echo -e "${YELLOW}[!] 推送失败，尝试设置 upstream${NC}"
    git push -u origin main 2>&1
}

echo ""
echo -e "${GREEN}✅ 推送成功，等待部署...${NC}"
echo ""

# 等待 GitHub Actions 部署完成 + 预热 CDN
echo -e "⏳ 等待 GitHub Actions 部署..."
REPO=$(git remote -v | head -1 | awk '{print $2}' | sed 's/.*github.com[:\/]//;s/\.git//')
OWNER=$(echo "$REPO" | cut -d/ -f1)
REPO_NAME=$(echo "$REPO" | cut -d/ -f2)
SITE_URL="https://${OWNER}.github.io/${REPO_NAME}"

# 轮询等待部署完成（最多等 3 分钟）
for i in $(seq 1 36); do
    sleep 5
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}/" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "\r${GREEN}✅ 部署完成！${NC} ($((i*5))秒)"
        break
    fi
    echo -ne "\r  ⏳ 第 $((i*5)) 秒... (HTTP $HTTP_CODE)"
done

# 预热 CDN：强制刷新所有关键页面的缓存
echo -e "\n🌐 预热 CDN 缓存..."
LATEST_DATE=$(curl -s "${SITE_URL}/data/articles.json" 2>/dev/null | grep -o '"latest_date":"[^"]*"' | cut -d'"' -f4 || echo "")
for url in \
    "${SITE_URL}/" \
    "${SITE_URL}/data/articles.js" \
    "${SITE_URL}/data/articles.json"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    echo -e "  $CODE  $url"
done

# 自动预热最新日期的文章
if [ -n "$LATEST_DATE" ]; then
    echo "  (最新日期: $LATEST_DATE)"
    for url in \
        "${SITE_URL}/${LATEST_DATE}/wechat-publish/morning/article.html" \
        "${SITE_URL}/${LATEST_DATE}/wechat-publish/evening/article.html"; do
        CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        echo -e "  $CODE  $url"
    done
fi

# 部署后验证
echo -e "\n✅ 运行部署后验证..."
if [ -f "scripts/verify-deploy.sh" ]; then
    bash scripts/verify-deploy.sh
else
    # 简易验证
    echo "  验证首页..."
    curl -s -o /dev/null -w "  %{http_code}  $SITE_URL/\n" "$SITE_URL/"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 全部完成！立即访问:${NC}"
echo -e "${GREEN}  $SITE_URL${NC}"
echo -e "${GREEN}========================================${NC}"
