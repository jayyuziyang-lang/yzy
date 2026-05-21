#!/bin/bash
# =============================================================================
# 扬说财经 · 漫画风格迭代 Agent (C-02)
# 职责：研究当前漫画/视觉趋势，提出风格改进建议
#   - 分析当前SVG漫画质量
#   - 研究行业优秀视觉作品
#   - 提出具体风格迭代方案
#
# 用法：
#   bash scripts/agents/comic-stylist.sh          # 全面评估+建议
#   bash scripts/agents/comic-stylist.sh analyze  # 仅分析当前风格
#   bash scripts/agents/comic-stylist.sh research # 仅输出研究建议
#
# 输出：
#   docs/review/comic-style-{YYYY-MM-DD}.md
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
SESSION="${1:-full}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} $1"; }
fail() { echo -e "  ${RED}❌${NC} $1"; }
head() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

echo -e "${BLUE}┌─────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  扬说财经 · 漫画风格迭代 Agent (C-02)      │${NC}"
echo -e "${BLUE}│  📅 ${TODAY}                          │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────┘${NC}"

mkdir -p "${ROOT_DIR}/docs/review"

output="${ROOT_DIR}/docs/review/comic-style-${TODAY}.md"

# ================================================================
# 分析：当前SVG质量评估
# ================================================================
analyze_current() {
    head "分析当前漫画风格"

    local total_svgs=0
    local total_size=0
    local has_defs=0
    local has_shadow=0
    local has_gradient=0

    for session in morning evening; do
        local comic_dir="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/comic"
        if [ -d "$comic_dir" ]; then
            for f in "$comic_dir"/*.svg; do
                [ -f "$f" ] || continue
                total_svgs=$((total_svgs + 1))
                local sz=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
                total_size=$((total_size + sz))
                local content=$(cat "$f")
                echo "$content" | grep -q '<defs>' && has_defs=$((has_defs + 1))
                echo "$content" | grep -q 'drop-shadow' && has_shadow=$((has_shadow + 1))
                echo "$content" | grep -q 'linearGradient' && has_gradient=$((has_gradient + 1))
            done
        fi
    done

    local avg_size=0
    [ "$total_svgs" -gt 0 ] && avg_size=$((total_size / total_svgs / 1024))

    ok "共 ${total_svgs} 个SVG漫画面板"
    ok "平均大小: ${avg_size} KB"
    ok "含deifs定义: ${has_defs}/${total_svgs}"
    ok "含投影效果: ${has_shadow}/${total_svgs}"
    ok "含渐变色: ${has_gradient}/${total_svgs}"
}

# ================================================================
# 风格迭代建议
# ================================================================
generate_suggestions() {
    head "风格迭代建议"

    cat > "$output" << SECTION
# 漫画风格评估报告 — ${TODAY}

## 当前状态
- 面板数: [待统计]
- 平均大小: [待统计]
- 角色表现: SVG矢量角色
- 色彩方案: 蓝色系+金色点缀（品牌色）

## 行业趋势研究
*以下内容需运营总监通过WebSearch研究后填充*

### 当前财经漫画/信息图趋势
| 维度 | 行业顶尖水平 | 我们当前 | 差距 | 改进建议 |
|------|-------------|---------|------|---------|
| 角色表情 | [待研究] | 静态/有限 | [待评估] | [待填充] |
| 配色方案 | [待研究] | 蓝金品牌色 | [待评估] | [待填充] |
| 信息密度 | [待研究] | [待评估] | [待评估] | [待填充] |
| 动效/交互 | [待研究] | 静态SVG | [待评估] | [待填充] |

### 参考案例
1. [待研究: 同类型头部账号视觉分析]
2. [待研究: 华尔街见闻/财新视觉风格]
3. [待研究: 海外财经媒体信息图趋势]

## 具体改进方案

### 短期（本周内可落地）
- [待填充：小幅改进]

### 中期（1-2周）
- [待填充：中等复杂度改进]

### 长期（1个月以上）
- [待填充：重大风格升级]

## 资源需求
- [待评估：是否需要新的设计工具或人员]

---
*本报告由漫画风格迭代Agent（C-02）生成，趋势数据需运营总监配合研究。*
SECTION

    ok "风格迭代报告已生成: ${output}"
}

# ================================================================
# Main
# ================================================================

echo "" > "$output"

case "$SESSION" in
    analyze)
        analyze_current
        ;;
    research)
        generate_suggestions
        ;;
    full)
        analyze_current
        generate_suggestions
        ;;
    *)
        echo "用法: bash scripts/agents/comic-stylist.sh {analyze|research|full}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  漫画风格评估完成${NC}"
echo -e "${GREEN}  报告: ${output}${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
