#!/bin/bash
# =============================================================
# 扬说财经 · git hooks 安装脚本
# =============================================================
# 自动安装 pre-push 钩子到 .git/hooks/
# 防止手动 git push 绕过 deploy.sh 验证
# =============================================================

set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cp "$ROOT_DIR/scripts/install-hooks.sh" "$ROOT_DIR/.git/hooks/pre-push"
chmod +x "$ROOT_DIR/.git/hooks/pre-push"
echo "✅ pre-push 钩子已安装"
echo "   现在所有 git push 将通过 deploy.sh 强制验证"
