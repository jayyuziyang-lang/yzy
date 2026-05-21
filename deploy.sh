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
    echo "    git remote add origin https://github.com/你的用户名/你的仓库名.git"
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
    echo "    git remote add origin https://github.com/你的用户名/你的仓库名.git"
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
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo -e "  📡 Pages 地址（等待 1-2 分钟生效）:"
git remote -v | head -1 | awk '{print $2}' | sed 's/.*github.com[:\/]//;s/\.git//' | xargs -I{} echo "  https://{}.github.io/{}"
echo ""
echo -e "  ⏳ 部署进度:"
git remote -v | head -1 | awk '{print $2}' | sed 's/.*github.com[:\/]//;s/\.git//' | xargs -I{} echo "  https://github.com/{}/actions"
