#!/bin/bash
# =============================================================
# 扬说财经 · pre-push 钩子
# 强制使用 deploy.sh 部署，禁止手动 git push
#
# 安装: bash scripts/install-hooks.sh
# 强制推送: GIT_PUSH_USING_DEPLOY=1 git push
# =============================================================

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'
BLUE='\033[0;34m'

# 检测是否通过 deploy.sh 调用
PPID_CHECK=$(ps -o comm= -p $PPID 2>/dev/null | grep deploy || echo "")
if [ -n "$PPID_CHECK" ]; then
    exit 0
fi

# 检测调用栈中是否有 deploy.sh
if pstree -s $$ 2>/dev/null | grep -q deploy; then
    exit 0
fi

# 环境变量方式（用于特殊情况）
if [ "$GIT_PUSH_USING_DEPLOY" = "1" ]; then
    exit 0
fi

echo ""
echo -e "${RED}============================================================${NC}"
echo -e "${RED}  ❌ 禁止手动 git push！${NC}"
echo -e "${RED}============================================================${NC}"
echo ""
echo -e "  所有部署必须通过 ${BLUE}deploy.sh${NC}："
echo ""
echo -e "    ${YELLOW}bash deploy.sh \"提交信息\"${NC}"
echo ""
echo -e "  deploy.sh 自动执行："
echo -e "    1. update-index.py — 刷新数据索引"
echo -e "    2. pre-deploy-check.sh — 6项验证"
echo -e "    3. 验证通过 → 自动 git add / commit / push"
echo -e "    4. CDN 预热 + 部署后验证"
echo ""
echo -e "  手动 push 会绕过所有验证环节。"
echo -e "  如需强制 push，设置环境变量："
echo ""
echo -e "    ${YELLOW}GIT_PUSH_USING_DEPLOY=1 git push${NC}"
echo ""
echo -e "${RED}============================================================${NC}"
echo ""
exit 1
