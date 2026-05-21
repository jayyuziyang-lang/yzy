#!/bin/bash
# =============================================================
# 每日自动化升级脚本
# 每天生产任务结束后自动执行：
#   1. 质量检查   2. 索引校验   3. 版本标记   4. 问题入库
# =============================================================
# 用法: bash scripts/daily-upgrade.sh [--date YYYY-MM-DD]
# =============================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
DATE="${1:-$(date +%Y-%m-%d)}"
LOGFILE="${ROOT_DIR}/logs/upgrade-${DATE}.log"
mkdir -p "${ROOT_DIR}/logs"

log()  { echo -e "[$(date '+%H:%M:%S')] $1" | tee -a "$LOGFILE"; }
ok()   { log "${GREEN}✅ $1${NC}"; }
warn() { log "${YELLOW}⚠️  $1${NC}"; }
fail() { log "${RED}❌ $1${NC}"; }

echo "" | tee -a "$LOGFILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$LOGFILE"
echo -e "${BLUE}  扬说财经 · 每日自动化升级${NC}" | tee -a "$LOGFILE"
echo -e "${BLUE}  日期: ${DATE}${NC}" | tee -a "$LOGFILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$LOGFILE"

ISSUES=0

# ── Step 1: 运行数据索引更新 ──
echo -e "\n📊 数据索引更新..." | tee -a "$LOGFILE"
if python scripts/update-index.py; then
    ok "数据索引更新成功"
else
    fail "数据索引更新失败"
    ISSUES=$((ISSUES+1))
fi

# ── Step 2: 运行部署前检查 ──
echo -e "\n🔍 部署前检查..." | tee -a "$LOGFILE"
if bash scripts/pre-deploy-check.sh; then
    ok "部署前检查通过"
elif [ $? -eq 1 ]; then
    warn "部署前检查有警告，继续执行"
else
    fail "部署前检查未通过"
    ISSUES=$((ISSUES+1))
fi

# ── Step 3: 运行质量检查 ──
echo -e "\n🏥 质量检查..." | tee -a "$LOGFILE"
if python scripts/site-health.py; then
    ok "质量检查通过"
else
    warn "质量检查有异常（非阻塞）"
fi

# ── Step 4: 验证文章文件完整性 ──
echo -e "\n📝 文章完整性检查..." | tee -a "$LOGFILE"
MORNING="${DATE}/wechat-publish/morning/article.html"
EVENING="${DATE}/wechat-publish/evening/article.html"
if [ -f "$MORNING" ]; then
    ok "早报文件存在 ($MORNING)"
else
    warn "早报文件缺失 ($MORNING)"
fi
if [ -f "$EVENING" ]; then
    ok "晚报文件存在 ($EVENING)"
else
    warn "晚报文件缺失 ($EVENING)"
fi

# ── Step 5: 检查 index.html 预渲染是否包含当天内容 ──
echo -e "\n🏠 首页预渲染检查..." | tee -a "$LOGFILE"
PRERENDER_DATE=$(grep -o 'data-date="[^"]*"' index.html 2>/dev/null | cut -d'"' -f2 || echo "")
if [ "$PRERENDER_DATE" = "$DATE" ]; then
    ok "首页预渲染日期为当天 ($DATE)"
else
    warn "首页预渲染日期 ($PRERENDER_DATE) 与当天 ($DATE) 不一致"
    warn "  → 需要手动更新 index.html 中的 data-date 属性"
fi

# ── Step 6: 索引文件比对 ──
echo -e "\n📋 数据一致性检查..." | tee -a "$LOGFILE"
if [ -f "data/articles.json" ]; then
    ARTICLE_COUNT=$(python3 -c "import json; d=json.load(open('data/articles.json')); print(len(d['articles']))" 2>/dev/null || echo "0")
    if [ "$ARTICLE_COUNT" -gt 0 ]; then
        ok "articles.json 包含 $ARTICLE_COUNT 篇文章"
    else
        warn "articles.json 为空"
    fi
fi

# ── Step 7: 部署触发 ──
echo -e "\n🚀 触发部署..." | tee -a "$LOGFILE"
COMMIT_MSG="${DATE} 每日财经内容更新"
if bash deploy.sh "$COMMIT_MSG" 2>&1 | tail -10 | tee -a "$LOGFILE"; then
    ok "部署触发成功"
else
    fail "部署触发失败"
    ISSUES=$((ISSUES+1))
fi

# ── Step 8: 部署后验证 ──
echo -e "\n✅ 部署后验证..." | tee -a "$LOGFILE"
if bash scripts/verify-deploy.sh 2>&1 | tail -15 | tee -a "$LOGFILE"; then
    ok "部署后验证通过"
else
    fail "部署后验证有异常"
    ISSUES=$((ISSUES+1))
fi

# ── Step 9: Git 版本标记 ──
echo -e "\n📌 版本标记..." | tee -a "$LOGFILE"
TAG="v$(echo $DATE | tr -d '-').1"
# 如果今天已有 tag 则递增
EXISTING=$(git tag -l "${DATE//-/}*" 2>/dev/null | wc -l)
if [ "$EXISTING" -gt 0 ]; then
    TAG="v$(echo $DATE | tr -d '-').$((EXISTING+1))"
fi
if git tag "$TAG" -m "每日发布: $DATE" 2>/dev/null; then
    git push origin "$TAG" 2>/dev/null
    ok "版本标记: $TAG"
else
    warn "版本标记失败（可能已存在），跳过"
fi

# ── Step 10: 写入问题日志 ──
echo -e "\n📝 写入日常记录..." | tee -a "$LOGFILE"
if [ "$ISSUES" -gt 0 ]; then
    warn "今天有 $ISSUES 个问题待处理"
else
    ok "今天无问题"
fi

# ── 汇总 ──
echo "" | tee -a "$LOGFILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$LOGFILE"
if [ "$ISSUES" -eq 0 ]; then
    echo -e "  ${GREEN}✅ 每日升级全部完成！${NC}" | tee -a "$LOGFILE"
else
    echo -e "  ${YELLOW}⚠️  升级完成，$ISSUES 个问题需关注${NC}" | tee -a "$LOGFILE"
    log "  查看日志: $LOGFILE"
fi
echo -e "${BLUE}========================================${NC}" | tee -a "$LOGFILE"

exit $ISSUES
