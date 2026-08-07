#!/usr/bin/env python3
"""
扬说财经 · 2026-08-07 早报专项图表
基于8月6日6故事内容生成SVG数据图表

主轴：ADP爆冷(9月加息预期降温) + 霍尔木兹谈判破冰 → 油价回落 → 通胀担忧缓解
→ 黄金四连涨破$4,300(七周新高) → 道指终结五连涨 → 今夜非农裁决

所有数据点均来自8月7日凌晨的多来源交叉验证：
- 美股/金价/油价/ADP: Reuters · CNBC · Investing.com · 东方财富
- A股: 证券时报 · 东方财富 · 金融界
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os, sys

# ============================================================
# 字体配置
# ============================================================
def setup_font():
    chinese_fonts = [
        'Noto Sans SC', 'Noto Sans CJK SC', 'Source Han Sans SC',
        'PingFang SC', 'Microsoft YaHei', 'SimHei',
        'WenQuanYi Micro Hei', 'Droid Sans Fallback'
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in chinese_fonts:
        if font in available:
            plt.rcParams['font.family'] = font
            plt.rcParams['axes.unicode_minus'] = False
            return font
    for f in fm.fontManager.ttflist:
        if 'CJK' in f.name or 'SC' in f.name:
            plt.rcParams['font.family'] = f.name
            plt.rcParams['axes.unicode_minus'] = False
            return f.name
    return None

FONT = setup_font()
print(f"Using font: {FONT}")

# 品牌色（早报蓝色系）
BLUE = '#1A56DB'
DARK_BLUE = '#1E3A7A'
GOLD = '#D4A017'
RED = '#EF4444'
GREEN = '#10B981'
BG = '#F5F7FA'
DARK = '#1E293B'
GRAY = '#64748B'
ORANGE = '#EA580C'
PURPLE = '#8B5CF6'

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Chart 1: 布伦特原油一周走势 — 霍尔木兹博弈
# 对应 主轴传导链 + 故事六（商品/黄金）
# 数据：7/31≈$88 → 8/3 -7% $83.77(特朗普取消打击) → 8/4 -5.3% $79.36
#       → 8/5 $79.45 → 8/6 -0.5% $79.08(伊阿坐标达成+库存增加)
# ============================================================
def chart_brent_hormuz():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    days = ['7/31\n(周五)', '8/3\n(周一)', '8/4\n(周二)', '8/5\n(周三)', '8/6\n(周四)']
    prices = [88.0, 83.77, 79.36, 79.45, 79.08]
    x = np.arange(len(days))

    ax.plot(x, prices, color=DARK_BLUE, linewidth=2.5, marker='o', markersize=7, zorder=3)
    ax.fill_between(x, prices, alpha=0.08, color=DARK_BLUE)

    # 数据标签
    for xi, pi in zip(x, prices):
        va = 'top' if xi < 4 else 'bottom'
        ax.text(xi, pi + 0.9 if xi < 4 else pi - 1.8, f'${pi:.2f}',
                ha='center', va=va, fontsize=8, fontweight='bold', color=DARK_BLUE)

    # 事件标注
    ax.annotate('特朗普取消\n对伊打击\n油价单日-7%',
                xy=(1, 83.77), xytext=(1.05, 87.5),
                fontsize=7, color=RED, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
    ax.annotate('美伊-阿曼\n谈判破冰\n临时航线达成',
                xy=(4, 79.08), xytext=(3.1, 83.0),
                fontsize=7, color=GREEN, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.2))

    ax.set_title('布伦特原油：霍尔木兹风险溢价快速消退', fontsize=12, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('美元/桶', fontsize=9, color=GRAY)
    ax.set_xticks(x)
    ax.set_xticklabels(days, fontsize=8, color=GRAY)
    ax.set_ylim(75, 92)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.grid(axis='y', alpha=0.15, color=GRAY)

    ax.text(0.5, -0.16, '一周累计-10% · 数据来源：ICE · Reuters · 路透财经', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'brent_hormuz_aug7.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 2: 黄金破$4,300 — 四连涨/七周新高
# 对应 故事六（商品/黄金）核心图
# 数据：6/30年内低点$3,942.43 → 7/22阶段高点$4,131.09
#       → 8月初回踩(约$3,960-4,000) → 8/5 +4% → 8/6 +4.2%收$4,308
# ============================================================
def chart_gold_rally():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    labels = ['6/30\n年内低点', '7月上旬\n关口拉锯', '7/22\n阶段高点', '8/4\n回踩蓄势', '8/5\n+4%', '8/6\n$4,308']
    prices = [3942.43, 4000, 4131.09, 3965, 4134, 4308]
    x = np.arange(len(labels))

    ax.plot(x, prices, color=GOLD, linewidth=2.5, marker='o', markersize=7, zorder=3)
    ax.fill_between(x, prices, alpha=0.08, color=GOLD)

    # 数据标签
    for xi, pi in zip(x, prices):
        ax.text(xi, pi + 70, f'${pi:,.0f}', ha='center', va='bottom',
                fontsize=7.5, fontweight='bold', color='#B8860B')

    # 关键点标注
    ax.annotate('六周下降三角\n形整理后突破',
                xy=(5, 4308), xytext=(3.4, 4500),
                fontsize=7, color=RED, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

    ax.annotate('ADP爆冷+谈判破冰\n双重驱动',
                xy=(4, 4134), xytext=(0.2, 4550),
                fontsize=7, color=PURPLE, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=PURPLE, lw=1.2))

    ax.set_title('现货黄金：四连涨突破$4,300，创七周新高', fontsize=12, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('美元/盎司', fontsize=9, color=GRAY)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.5, color=GRAY)
    ax.set_ylim(3800, 4750)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.grid(axis='y', alpha=0.15, color=GRAY)

    ax.text(0.5, -0.18, '周涨近6% · 年内低点累计反弹超$350 · 数据来源：COMEX · 东方财富 · Investing.com',
            transform=ax.transAxes, fontsize=7.5, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'gold_rally_aug7.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 3: A股8月6日指数分化 + 煤炭领涨
# 对应 故事一（A股）
# 数据：沪指+0.57% 深成指-0.24% 创业板-0.55% 科创50+0.45% 北证50+0.31%
#       煤炭开采+4.88%领涨(涨停潮近10股)
# ============================================================
def chart_astock_index():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    indexes = ['沪指', '深成指', '创业板', '科创50', '北证50']
    changes = [0.57, -0.24, -0.55, 0.45, 0.31]
    # A股：红涨绿跌
    colors_bar = [RED if v >= 0 else GREEN for v in changes]

    bars = ax.bar(indexes, changes, color=colors_bar, width=0.55, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, changes):
        label = f'{val:+.2f}%'
        y_pos = bar.get_height() + 0.06 if val >= 0 else bar.get_height() - 0.11
        va = 'bottom' if val >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2., y_pos, label,
                ha='center', va=va, fontsize=8.5, fontweight='bold',
                color=RED if val >= 0 else GREEN)

    ax.set_title('A股8月6日：沪指重回3900点，指数分化', fontsize=12, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_ylim(-0.85, 0.95)
    ax.axhline(y=0, color=DARK, linewidth=0.8)
    ax.grid(axis='y', alpha=0.15, color=GRAY)

    # 煤炭亮点标注
    ax.annotate('煤炭开采 +4.88%\n近10股涨停(昊华能源/潞安环能等)',
                xy=(0, 0.57), xytext=(1.15, 0.72),
                fontsize=7.5, color=RED, ha='left', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.1))
    ax.text(0.5, 0.62, '超2700股上涨 · 成交2.55万亿(缩量约1300亿)', transform=ax.transAxes,
            fontsize=7.5, color=GRAY, ha='center', va='center')

    ax.text(0.5, -0.18, '数据来源：上交所 · 深交所 · 证券时报 · 东方财富', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'astock_index_aug7.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 4: 美股三大指数 — 道指终结五连涨
# 对应 故事二（美股）
# 数据：8/5道指54,349.12 +0.49%创新高 → 8/6道指-464.05(-0.85%)收53,885.10
#       标普-0.18% 纳指-0.06% · 10Y美债~4.66% · VIX 15.15(-4.17%)
# ============================================================
def chart_us_markets():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    indexes = ['道指', '标普500', '纳指']
    changes = [-0.85, -0.18, -0.06]
    closes = ['53,885.10', '7,709.96', '26,348.35']
    # 全市场统一：红涨绿跌
    colors_bar = [RED if v >= 0 else GREEN for v in changes]

    bars = ax.bar(indexes, changes, color=colors_bar, width=0.5, edgecolor='white', linewidth=0.8)

    for bar, val, close in zip(bars, changes, closes):
        label = f'{val:.2f}%'
        y_pos = bar.get_height() + 0.03 if val >= 0 else bar.get_height() - 0.1
        va = 'bottom' if val >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2., y_pos, label,
                ha='center', va=va, fontsize=9, fontweight='bold',
                color=RED if val >= 0 else GREEN)
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() - 0.15, close,
                ha='center', va='top', fontsize=7, color=GRAY)

    ax.set_title('美股8月6日：道指-0.85%终结五连涨，高位回落', fontsize=11.5, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_ylim(-1.3, 0.4)
    ax.axhline(y=0, color=DARK, linewidth=0.8)
    ax.grid(axis='y', alpha=0.15, color=GRAY)

    ax.text(0.5, 0.78, '前日(8/5)道指54,349.12创历史新高，隔日回落464点',
            transform=ax.transAxes, fontsize=7.5, color=GRAY, ha='center', va='center')
    ax.text(0.5, -0.18, '数据来源：Reuters · CNBC · 东方财富 · 10Y美债~4.66% · VIX 15.81',
            transform=ax.transAxes, fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'us_markets_aug7.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 50)
    print("扬说财经 · 2026-08-07 早报专项图表")
    print("=" * 50)

    paths = []
    paths.append(chart_brent_hormuz())
    paths.append(chart_gold_rally())
    paths.append(chart_astock_index())
    paths.append(chart_us_markets())

    print("=" * 50)
    print(f"Generated {len(paths)} charts")
    for p in paths:
        size = os.path.getsize(p)
        print(f"   {os.path.basename(p)}  ({size/1024:.1f} KB)")
    print("=" * 50)
