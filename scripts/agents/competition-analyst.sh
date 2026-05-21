#!/bin/bash
# =============================================================================
# 扬说财经 · 竞争分析 Agent (F-02)
# 职责：
#   研究顶尖财经媒体/自媒体，学习优秀作品
#   输出对标分析报告，推动团队持续迭代
#
# 用法：
#   bash scripts/agents/competition-analyst.sh           # 完全分析
#   bash scripts/agents/competition-analyst.sh quick     # 快速简报
#   bash scripts/agents/competition-analyst.sh deep      # 深度分析
#
# 输出：
#   docs/competition/report-{YYYY-MM-DD}.md
#   docs/competition/benchmarks.md (持续更新)
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
MODE="${1:-full}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} $1"; }
head() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

echo -e "${BLUE}┌─────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  扬说财经 · 竞争分析 Agent (F-02)          │${NC}"
echo -e "${BLUE}│  📅 ${TODAY}                          │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────┘${NC}"

mkdir -p "${ROOT_DIR}/docs/competition"

output="${ROOT_DIR}/docs/competition/report-${TODAY}.md"
benchmark="${ROOT_DIR}/docs/competition/benchmarks.md"

# ================================================================
# 比较管道：现有产出 vs 行业标准
# ================================================================
compare_outputs() {
    head "当前产出对标分析"

    local issues=0

    # 检查音频时长
    for session in morning evening; do
        local audio="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/audio.mp3"
        if [ -f "$audio" ]; then
            local size_kb=$(stat -c%s "$audio" 2>/dev/null | awk '{printf "%.0f", $1/1024}' || echo 0)
            ok "${session} 音频: ${size_kb} KB"

            # 估算时长（约16KB/秒 for MP3)
            local est_sec=$((size_kb / 16))
            local est_min=$((est_sec / 60))
            local est_rem=$((est_sec % 60))
            ok "${session} 估算时长: ${est_min}分${est_rem}秒"
        else
            warn "${session} 音频未生成"
            issues=$((issues + 1))
        fi
    done

    # 检查文章长度
    for session in morning evening; do
        local md="${ROOT_DIR}/${TODAY}/wechat-publish/${session}/article.md"
        if [ -f "$md" ]; then
            local chars=$(wc -m < "$md" 2>/dev/null | tr -d ' ')
            ok "${session} 文章: ${chars}字"
        fi
    done

    return $issues
}

# ================================================================
# 生成分析报告
# ================================================================
generate_report() {
    head "生成竞争分析报告"

    cat > "$output" << SECTION
# 竞争分析报告 — ${TODAY}

## 分析范围
- 同类型财经公众号/自媒体
- 头部财经媒体
- 海外优秀财经内容创作者

## 对标维度

### 1. 内容质量
| 维度 | 行业基准 | 我们当前 | 差距 | 改进方向 |
|------|---------|---------|------|---------|
| 新闻时效性 | 实时/当日 | [待评估] | [待评估] | [待填充] |
| 数据准确性 | 可追溯来源 | [待评估] | [待评估] | [待填充] |
| 分析深度 | 有独立观点 | [待评估] | [待评估] | [待填充] |
| 可读性 | 口语化+专业 | [待评估] | [待评估] | [待填充] |

### 2. 视觉呈现
| 维度 | 行业基准 | 我们当前 | 差距 | 改进方向 |
|------|---------|---------|------|---------|
| 漫画/插图质量 | [待研究] | [待评估] | [待评估] | [待填充] |
| 数据可视化 | [待研究] | SVG图表 | [待评估] | [待填充] |
| 品牌一致性 | 高 | 有品牌色 | [待评估] | [待填充] |

### 3. 音频/播客
| 维度 | 行业基准 | 我们当前 | 差距 | 改进方向 |
|------|---------|---------|------|---------|
| 音色 | 专业播音 | YunyangNeural | [待评估] | [待填充] |
| 语速节奏 | 自然 | -5% | [待评估] | [待填充] |
| 内容长度 | [待研究] | [待统计] | [待评估] | [待填充] |

## 行业优秀案例
*需运营总监通过WebSearch研究后填充*
1. [案例1: 名称+地址+亮点]
2. [案例2: 名称+地址+亮点]
3. [案例3: 名称+地址+亮点]

## 本周改进建议
1. [待填充]
2. [待填充]
3. [待填充]

---
*本报告由竞争分析Agent（F-02）生成。*
*[待填充]/[待研究] 标记需运营总监通过WebSearch调研后补充。*
SECTION

    ok "竞争分析报告已生成: ${output}"

    # 更新基准文档
    if [ ! -f "$benchmark" ]; then
        cat > "$benchmark" << 'BM'
# 扬说财经 · 行业基准追踪

> 持续更新的对标文档，记录行业优秀标准

## 内容基准（持续更新）
- 音频最佳时长: [待研究]
- 文章最佳字数: [待研究]
- 最佳发布频率: [待研究]

## 视觉基准（持续更新）
- 漫画风格参考: [待研究]
- 配色方案参考: [待研究]
- 信息图标准: [待研究]

## 竞品列表（持续更新）
| 名称 | 类型 | 优势 | 可借鉴 |
|------|------|------|--------|
| [待补充] | [待补充] | [待补充] | [待补充] |

---
*由竞争分析Agent（F-02）维护，每次分析后更新。*
BM
        ok "行业基准文档已创建"
    fi
}

# ================================================================
# 快速简报
# ================================================================
quick_brief() {
    head "快速简报"

    compare_outputs

    echo ""
    ok "快速简报完成"
    echo "  完整分析请运行: bash scripts/agents/competition-analyst.sh deep"
}

# ================================================================
# Main
# ================================================================

case "$MODE" in
    quick)
        quick_brief
        ;;
    deep|full)
        compare_outputs
        generate_report
        ;;
    *)
        echo "用法: bash scripts/agents/competition-analyst.sh {quick|deep|full}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  竞争分析完成${NC}"
echo -e "${GREEN}  报告: ${output}${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
