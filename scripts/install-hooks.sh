#!/bin/bash
# =============================================================
# 扬说财经 · git hooks 安装脚本
# =============================================================
# 安装 pre-push 钩子到 .git/hooks/
# 防止手动 git push 绕过 deploy.sh 验证
#
# 用法: bash scripts/install-hooks.sh
# =============================================================

set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_SRC="$ROOT_DIR/scripts/pre-push.sh"
HOOK_DST="$ROOT_DIR/.git/hooks/pre-push"

if [ ! -f "$HOOK_SRC" ]; then
    echo "❌ $HOOK_SRC 不存在"
    exit 1
fi

cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "✅ pre-push 钩子已安装"
echo "   来源: scripts/pre-push.sh"
echo "   位置: .git/hooks/pre-push"
echo ""
echo "   所有 git push 将检查是否通过 deploy.sh 调用"
echo "   强制推送: GIT_PUSH_USING_DEPLOY=1 git push"
