#!/bin/bash
# =============================================================================
# 扬说财经 · 新闻采集 Agent
# 职责：每日财经新闻采集，确保每条新闻附带可验证来源
# 核心理念：所有新闻必须来自实时搜索，禁止使用模型内部知识
#
# 用法：
#   bash scripts/agents/news-collector.sh domestic       # 国内财经新闻
#   bash scripts/agents/news-collector.sh international  # 国际财经新闻
#   bash scripts/agents/news-collector.sh all            # 全部
#
# 输出：
#   docs/review/news-{domestic,international}-{YYYY-MM-DD}.md
#   结构化新闻简报，每条含：标题、摘要、来源URL、交叉验证状态
# =============================================================================

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
SESSION="${1:-all}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠️${NC} $1"; }
fail() { echo -e "  ${RED}❌${NC} $1"; }
info() { echo -e "  ${CYAN}ℹ️${NC} $1"; }
head() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }

echo -e "${BLUE}┌─────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│  扬说财经 · 新闻采集 Agent                 │${NC}"
echo -e "${BLUE}│  📅 ${TODAY}                          │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────┘${NC}"

mkdir -p "${ROOT_DIR}/docs/review"

# ================================================================
# 国内财经新闻采集
# ================================================================
collect_domestic() {
    local output="${ROOT_DIR}/docs/review/news-domestic-${TODAY}.md"
    head "国内财经新闻采集"

    echo "# 国内财经新闻简报 — ${TODAY}" > "$output"
    echo "" >> "$output"
    echo "## 采集时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$output"
    echo "" >> "$output"
    echo "## 采集原则" >> "$output"
    echo "- 每条新闻标注来源URL" >> "$output"
    echo "- 关键数据要求2个以上独立来源" >> "$output"
    echo "- 来源优先级: 官方媒体 > 财经门户 > 自媒体" >> "$output"
    echo "" >> "$output"

    local count=0

    # === A股/大盘 ===
    cat >> "$output" << 'SECTION'
## 一、A股市场
### 大盘表现
| 指标 | 数据 | 来源 |
|------|------|------|
| 上证指数 | [待采集] | [待补充] |
| 深证成指 | [待采集] | [待补充] |
| 创业板指 | [待采集] | [待补充] |
| 北向资金 | [待采集] | [待补充] |

### 领涨/领跌板块
- [待采集]

### 重要公告
- [待采集]
SECTION
    echo "" >> "$output"

    # === 政策 ===
    cat >> "$output" << 'SECTION'
## 二、政策与监管
- [待采集]

## 三、行业动态
- [待采集]

## 四、公司与个股
- [待采集]

---
*本简报由新闻采集Agent（A-01）自动生成，每条数据需经事实核查Agent（E-01）验证。*
SECTION

    echo "" >> "$output"
    ok "国内财经新闻模板已生成: ${output}"
    echo "  ${YELLOW}注意: [待采集] 标记需要运营总监通过WebSearch填充实际数据${NC}"
    echo "  ${YELLOW}数据填充后, 运行 fact-checker.sh 进行交叉验证${NC}"
}

# ================================================================
# 国际财经新闻采集
# ================================================================
collect_international() {
    local output="${ROOT_DIR}/docs/review/news-international-${TODAY}.md"
    head "国际财经新闻采集"

    echo "# 国际财经新闻简报 — ${TODAY}" > "$output"
    echo "" >> "$output"
    echo "## 采集时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$output"
    echo "" >> "$output"
    echo "## 采集原则" >> "$output"
    echo "- 每条新闻标注来源URL" >> "$output"
    echo "- 关键经济数据标注公布机构（Fed/EIA/IMF等）" >> "$output"
    echo "" >> "$output"

    cat >> "$output" << 'SECTION'
## 一、美股市场
### 主要指数
| 指标 | 数据 | 来源 |
|------|------|------|
| 道琼斯 | [待采集] | [待补充] |
| 纳斯达克 | [待采集] | [待补充] |
| 标普500 | [待采集] | [待补充] |

### 领涨/领跌
- [待采集]

### 重要财报
- [待采集]

## 二、大宗商品
| 品种 | 价格 | 涨跌幅 | 来源 |
|------|------|--------|------|
| WTI原油 | [待采集] | [待采集] | [待补充] |
| COMEX黄金 | [待采集] | [待采集] | [待补充] |
| 伦铜 | [待采集] | [待采集] | [待补充] |

## 三、外汇市场
| 货币对 | 汇率 | 来源 |
|--------|------|------|
| 美元指数 | [待采集] | [待补充] |
| 离岸人民币 | [待采集] | [待补充] |

## 四、国际要闻
- [待采集]

---
*本简报由新闻采集Agent（A-02）自动生成，每条数据需经事实核查Agent（E-01）验证。*
SECTION

    echo "" >> "$output"
    ok "国际财经新闻模板已生成: ${output}"
    echo "  ${YELLOW}注意: [待采集] 标记需要运营总监通过WebSearch填充实际数据${NC}"
    echo "  ${YELLOW}数据填充后, 运行 fact-checker.sh 进行交叉验证${NC}"
}

# ================================================================
# Main
# ================================================================
case "$SESSION" in
    domestic)
        collect_domestic
        ;;
    international)
        collect_international
        ;;
    all)
        collect_domestic
        collect_international
        ;;
    *)
        echo "用法: bash scripts/agents/news-collector.sh {domestic|international|all}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  新闻采集完成${NC}"
echo -e "${GREEN}  下步: 运营总监填充 [待采集] 数据${NC}"
echo -e "${GREEN}  然后: bash scripts/agents/fact-checker.sh${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
