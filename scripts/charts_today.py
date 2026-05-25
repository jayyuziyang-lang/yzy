#!/usr/bin/env python3
"""
扬说财经 · 2026-05-25 早报专项图表
基于今日文章内容生成SVG图表
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

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

# 品牌色
BLUE = '#1A56DB'
DARK_BLUE = '#1E3A7A'
GOLD = '#D4A017'
RED = '#EF4444'
GREEN = '#10B981'
BG = '#F5F7FA'
DARK = '#1E293B'
GRAY = '#64748B'
ORANGE = '#EA580C'

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Chart 1: 美债收益率当前水平 (US Treasury Yields)
# 对应 故事五（宏观）：Warsh缩表预期推升长端利率
# ============================================================
def chart_treasury_yields():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    labels = ['2年期', '5年期', '10年期', '30年期']
    yields = [4.02, 4.28, 4.56, 5.064]
    colors_bar = [GREEN, BLUE, ORANGE, RED]

    bars = ax.barh(labels, yields, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, yields):
        label = f'{val:.3f}%'
        if val == 5.064:
            label += ' ⬆ 2007年以来最高'
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2.,
                label, ha='left', va='center', fontsize=9, fontweight='bold', color=DARK)

    # 30年期高亮标注
    ax.annotate('Warsh缩表预期\n推升长端利率',
                xy=(5.064, 0), xytext=(5.5, 0.5),
                fontsize=8, color=RED, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

    ax.set_title('美国国债收益率 — 2026.05.22收盘', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('收益率 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_xlim(0, 7.5)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    # 添加参考线 - 中美利差标注
    ax.axvline(x=2.3, color=GOLD, linewidth=1, linestyle='--', alpha=0.6)
    ax.text(2.3, 3.5, '中国10年期 2.3%', rotation=90, fontsize=7, color=GOLD, alpha=0.7)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'treasury_yields.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 2: 金油比趋势 (Gold-Oil Ratio)
# 对应 故事六（商品/黄金）：市场逻辑从避险→滞胀交易
# ============================================================
def chart_gold_oil_ratio():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    months = ['2025\n11月', '12月', '2026\n1月', '2月', '3月', '4月', '5月']
    gold_prices = [3800, 3950, 4200, 4700, 4500, 4600, 4523]   # 黄金价格
    oil_prices = [72, 74, 78, 110, 108, 105, 102]               # 布伦特原油
    ratios = [52.8, 53.4, 53.8, 70.6, 41.7, 43.8, 44.4]        # 金油比

    # 双轴图
    color_gold = GOLD
    color_oil = DARK_BLUE
    color_ratio = RED

    ax_twin = ax.twinx()

    # 金价线
    ax.plot(months, gold_prices, color=color_gold, linewidth=2, marker='s', markersize=4,
            label='黄金 ($/oz)', zorder=3)
    # 油价线
    ax.plot(months, oil_prices, color=color_oil, linewidth=2, marker='^', markersize=4,
            label='布伦特原油 ($/桶)', zorder=3)

    # 金油比（柱状图）
    ax_twin.bar(months, ratios, color=color_ratio, alpha=0.15, width=0.5, label='金油比')

    # 标注关键转折点
    # 2月峰值70.6
    ax_twin.annotate('峰值 70.6\n恐慌避险',
                     xy=(3, 70.6), xytext=(1.5, 78),
                     fontsize=8, fontweight='bold', color=RED, ha='center',
                     arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

    # 当前45
    ax_twin.annotate('当前 ~45\n滞胀交易',
                     xy=(6, 44.4), xytext=(4.5, 52),
                     fontsize=8, fontweight='bold', color=RED, ha='center',
                     arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

    # 主Y轴：价格
    ax.set_ylabel('价格 (美元)', fontsize=9, color=GRAY)
    ax.set_ylim(0, 5200)

    # 次Y轴：金油比
    ax_twin.set_ylabel('金油比', fontsize=9, color=RED)
    ax_twin.set_ylim(0, 90)
    ax_twin.spines['right'].set_color(RED)
    ax_twin.tick_params(colors=RED, labelsize=8)

    # 图例
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax_twin.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
              fontsize=7, framealpha=0.8)

    ax.set_title('金油比趋势：从恐慌避险到滞胀交易', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=7)
    ax.grid(axis='y', alpha=0.15, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'gold_oil_ratio.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 3: A股板块资金切换 (Sector Rotation)
# 对应 故事一（A股）：资金从AI算力链向低估值高股息迁移
# ============================================================
def chart_sector_rotation():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    sectors = ['AI算力(通信/电子)', '半导体', '计算机软件', '军工', '银行', '高股息红利']
    changes = [-4.8, -3.2, -2.1, 0.8, 1.5, 1.8]
    colors_bar = [RED, '#EF4444', '#F87171', BLUE, GREEN, '#059669']

    bars = ax.barh(sectors, changes, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, changes):
        if val < 0:
            ax.text(bar.get_width() - 0.15, bar.get_y() + bar.get_height()/2.,
                    f'{val:.1f}%', ha='right', va='center', fontsize=9, fontweight='bold', color='white')
        else:
            ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height()/2.,
                    f'+{val:.1f}%', ha='left', va='center', fontsize=9, fontweight='bold', color=GREEN)

    ax.set_title('A股板块轮动 — 资金从高估值向低估值迁移', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('周涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_xlim(-6.5, 3.5)
    ax.axvline(x=0, color=DARK, linewidth=0.8)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    # 添加注解
    ax.text(0.5, -0.15, 'AI交易拥挤度触顶 → 资金高低切换', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'sector_rotation.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 50)
    print("扬说财经 · 今日专项图表")
    print(f"主题: 2026-05-25 早报")
    print("=" * 50)

    paths = []
    paths.append(chart_treasury_yields())
    paths.append(chart_gold_oil_ratio())
    paths.append(chart_sector_rotation())

    print("=" * 50)
    print(f"Generated {len(paths)} charts")
    for p in paths:
        size = os.path.getsize(p)
        print(f"   {os.path.basename(p)}  ({size/1024:.1f} KB)")
    print("=" * 50)
