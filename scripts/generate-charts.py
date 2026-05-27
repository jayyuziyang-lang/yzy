#!/usr/bin/env python3
"""
扬说财经 · Python数据可视化图表生成器
生成可嵌入文章的SVG图表
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# ============================================================
# 字体配置（优先使用中文字体）
# ============================================================
def setup_font():
    """Setup Chinese font for matplotlib"""
    # Try common Chinese fonts
    chinese_fonts = [
        'Noto Sans SC', 'Noto Sans CJK SC', 'Source Han Sans SC',
        'PingFang SC', 'Microsoft YaHei', 'SimHei',
        'WenQuanYi Micro Hei', 'Droid Sans Fallback'
    ]

    # Check available fonts
    available = {f.name for f in fm.fontManager.ttflist}
    for font in chinese_fonts:
        if font in available:
            plt.rcParams['font.family'] = font
            plt.rcParams['axes.unicode_minus'] = False
            return font

    # Fallback - try to find any CJK font
    for f in fm.fontManager.ttflist:
        if 'CJK' in f.name or 'SC' in f.name or 'Hei' in f.name or 'YaHei' in f.name:
            plt.rcParams['font.family'] = f.name
            plt.rcParams['axes.unicode_minus'] = False
            return f.name

    return None

FONT = setup_font()
print(f"Using font: {FONT}")

# Brand colors
BLUE = '#1A56DB'
DARK_BLUE = '#1E3A7A'
GOLD = '#D4A017'
RED = '#EF4444'
GREEN = '#10B981'
BG = '#F5F7FA'
WHITE = '#FFFFFF'
DARK = '#1E293B'
GRAY = '#64748B'

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# Chart 1: NVIDIA Revenue Trend (Bar chart)
# ============================================================
def chart_nvidia_revenue():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    quarters = ['FY26\nQ1', 'Q2', 'Q3', 'Q4', 'FY27\nQ1']
    revenues = [26.0, 30.0, 35.1, 39.3, 81.6]  # in billions
    colors = [BLUE, BLUE, BLUE, BLUE, GOLD]

    bars = ax.bar(quarters, revenues, color=colors, width=0.6, edgecolor='white', linewidth=0.5)

    # Add value labels on bars
    for bar, val in zip(bars, revenues):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5,
                f'${val}B', ha='center', va='bottom', fontsize=9, fontweight='bold', color=DARK)

    # Add "+85%" annotation on last bar
    ax.annotate('+85% YoY', xy=(4, 81.6), xytext=(3.5, 92),
                fontsize=10, fontweight='bold', color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

    ax.set_title('英伟达单季营收 ($B)', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('营收 (十亿美元)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.2, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'nvidia_revenue.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 2: Gold Price Trend (Line chart)
# ============================================================
def chart_gold_price():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    months = ['2025\n1月', '3月', '5月', '7月', '9月', '11月', '2026\n1月', '3月', '5/26']
    prices = [2650, 2900, 3100, 3350, 3600, 3800, 4100, 4300, 4507]

    ax.plot(months, prices, color=GOLD, linewidth=2.5, marker='o', markersize=5, zorder=3)
    ax.fill_between(range(len(months)), prices, alpha=0.1, color=GOLD)

    # Annotate latest price
    ax.annotate(f'$4,507', xy=(8, 4507), xytext=(6.5, 4750),
                fontsize=11, fontweight='bold', color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

    # Add annotation for recent drop
    ax.annotate('油价反弹\n通胀预期升温', xy=(7, 4300), xytext=(5, 4450),
                fontsize=7, color=RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1))

    # Add key event annotations
    ax.annotate('央行\n连续买入', xy=(6, 4100), xytext=(5, 4400),
                fontsize=7, color=BLUE, ha='center',
                arrowprops=dict(arrowstyle='->', color=BLUE, lw=1))

    ax.set_title('COMEX黄金期货走势 ($/oz)', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('美元/盎司', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=7)
    ax.grid(axis='y', alpha=0.2, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'gold_price_trend.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 3: Central Bank Gold Purchases (Bar chart)
# ============================================================
def chart_cb_gold_purchases():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    countries = ['中国', '波兰', '印度', '土耳其', '新加坡', '捷克']
    tons = [324, 90, 72, 60, 42, 38]
    colors_bar = [GOLD, BLUE, BLUE, BLUE, BLUE, BLUE]

    bars = ax.barh(countries, tons, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, tons):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2.,
                f'{val}吨', ha='left', va='center', fontsize=9, fontweight='bold', color=DARK)

    # Highlight China bar
    ax.text(280, 0, '全球第一', fontsize=8, color=GOLD, fontweight='bold', va='center')

    ax.set_title('2026 Q1 各国央行购金量', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('购金量 (吨)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_xlim(0, 450)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'central_bank_gold.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 4: NVIDIA Net Income Trend
# ============================================================
def chart_nvidia_net_income():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    quarters = ['FY26\nQ1', 'Q2', 'Q3', 'Q4', 'FY27\nQ1']
    incomes = [14.9, 16.6, 19.3, 22.1, 58.3]  # in billions
    colors_bar = [BLUE, BLUE, BLUE, BLUE, GOLD]

    bars = ax.bar(quarters, incomes, color=colors_bar, width=0.6, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, incomes):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'${val}B', ha='center', va='bottom', fontsize=9, fontweight='bold', color=DARK)

    ax.annotate('+211% YoY', xy=(4, 58.3), xytext=(3.2, 68),
                fontsize=10, fontweight='bold', color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

    ax.set_title('英伟达净利润 ($B)', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('净利润 (十亿美元)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_ylim(0, 78)
    ax.grid(axis='y', alpha=0.2, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'nvidia_net_income.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 5: PBOC Gold Reserves (Bar chart - monthly)
# ============================================================
def chart_pboc_reserves():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    months = ['2024\n12月', '2025\n3月', '6月', '9月', '12月', '2026\n3月', '4月']
    reserves = [2140, 2180, 2210, 2240, 2270, 2310, 2321.56]

    # Gradient area under line
    ax.fill_between(range(len(months)), reserves, alpha=0.12, color=GOLD)
    ax.plot(months, reserves, color=GOLD, linewidth=2.5, marker='s', markersize=5, zorder=3)

    # Annotate latest
    ax.annotate(f'{reserves[-1]:.1f}吨\n+8.09吨', xy=(6, reserves[-1]),
                xytext=(5, reserves[-1] + 20),
                fontsize=9, fontweight='bold', color=DARK, ha='center',
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.2))

    # Add "连续18个月" text
    ax.text(0.95, 0.05, '连续18个月增持', transform=ax.transAxes,
            fontsize=9, color=RED, fontweight='bold', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF0F0', edgecolor=RED, alpha=0.8))

    ax.set_title('中国人民银行黄金储备 (吨)', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('储备量 (吨)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=7)
    ax.grid(axis='y', alpha=0.2, color=GRAY)
    ax.set_ylim(2080, 2360)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'pboc_gold_reserves.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 6: A股主要指数涨跌幅 (Bar chart)
# ============================================================
def chart_astock_indices():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    indices = ['上证指数', '深证成指', '创业板指', '科创综指', '科创50']
    changes = [-0.17, 0.12, 0.54, -1.42, -1.49]
    colors_bar = [GREEN if c >= 0 else RED for c in changes]
    colors_bar[4] = RED  # 科创50跌幅最大

    bars = ax.barh(indices, changes, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, changes):
        if val > 0:
            ax.text(bar.get_width() + 0.03, bar.get_y() + bar.get_height()/2.,
                    f'+{val:.2f}%', ha='left', va='center', fontsize=9, fontweight='bold', color=GREEN)
        else:
            ax.text(bar.get_width() - 0.03, bar.get_y() + bar.get_height()/2.,
                    f'{val:.2f}%', ha='right', va='center', fontsize=9, fontweight='bold', color='white')

    ax.set_title('A股主要指数 2026.05.26 涨跌幅', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_xlim(-2, 2)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    # Add vertical line at 0
    ax.axvline(x=0, color=DARK, linewidth=0.8)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'astock_indices.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 7: 板块资金流向 (Horizontal bar chart)
# ============================================================
def chart_sector_flow():
    fig, ax = plt.subplots(figsize=(5, 3.2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    sectors = ['电子/半导体', '通信', '计算机', '银行', '非银金融', '有色金属']
    flows = [-388.1, -122.8, -115.6, 0.4, 3.4, 50.7]
    colors_bar = ['#DC2626', '#EF4444', '#F87171', GREEN, GREEN, '#059669']

    bars = ax.barh(sectors, flows, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, flows):
        if val < 0:
            ax.text(bar.get_width() - 5, bar.get_y() + bar.get_height()/2.,
                    f'{val:.1f}亿', ha='right', va='center', fontsize=8, fontweight='bold', color='white')
        else:
            ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2.,
                    f'+{val:.1f}亿', ha='left', va='center', fontsize=8, fontweight='bold', color=GREEN)

    ax.set_title('A股板块资金流向 2026.05.26', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('资金净流向 (亿元)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.set_xlim(-440, 80)
    ax.axvline(x=0, color=DARK, linewidth=0.8)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'sector_flow.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 8: WTI原油近期走势 (Line chart)
# ============================================================
def chart_oil_price():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    months = ['5/19', '5/20', '5/21', '5/22', '5/23', '5/24', '5/25', '5/26']
    prices = [103.8, 104.1, 98.26, 96.5, 94.2, 92.8, 91.5, 90.30]

    ax.fill_between(range(len(months)), prices, alpha=0.12, color=RED)
    ax.plot(months, prices, color=RED, linewidth=2.5, marker='o', markersize=6, zorder=3)

    # Annotate the crash
    ax.annotate(f'-6.52%\n$90.30', xy=(7, 90.30), xytext=(5.5, 88),
                fontsize=11, fontweight='bold', color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

    ax.set_title('WTI原油期货 近期走势 ($/桶)', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('美元/桶', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.grid(axis='y', alpha=0.2, color=GRAY)
    ax.set_ylim(85, 108)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'oil_price.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 9: 全球主要指数隔夜表现 (Comparison bar chart)
# ============================================================
def chart_global_markets():
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    indices = ['韩国KOSPI', '日经225', '纳指', '德国DAX', '标普500', '法国CAC', '道指', '上证指数']
    changes = [4.67, 2.20, 1.19, 2.01, 0.61, 1.76, -0.23, -0.17]
    colors_bar = [GREEN if c >= 0 else RED for c in changes]
    # Highlight top performers
    colors_bar[0] = '#059669'
    colors_bar[1] = '#059669'

    bars = ax.barh(indices, changes, color=colors_bar, height=0.55, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, changes):
        if val > 0:
            ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height()/2.,
                    f'+{val:.2f}%', ha='left', va='center', fontsize=8, fontweight='bold', color=GREEN)
        else:
            ax.text(bar.get_width() - 0.08, bar.get_y() + bar.get_height()/2.,
                    f'{val:.2f}%', ha='right', va='center', fontsize=8, fontweight='bold', color='white')

    # Add vertical zones
    ax.axvline(x=0, color=DARK, linewidth=0.8)
    ax.axvspan(0, 5, alpha=0.03, color=GREEN)
    ax.axvspan(-1, 0, alpha=0.03, color=RED)

    # Annotate key insight
    ax.text(0.98, 0.95, '亚太领涨 全球共振', transform=ax.transAxes,
            fontsize=9, color='#059669', fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0FDF4', edgecolor=GREEN, alpha=0.8))

    ax.set_title('全球主要指数隔夜表现 2026.05.27', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_xlim(-1.5, 5.7)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'global_markets.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 10: 半导体板块 — 美光引爆全球 (Grouped bar with annotation)
# ============================================================
def chart_semiconductor_surge():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    stocks = ['美光科技', 'SK海力士', '三星电子', '西部数据', '闪迪', '费城半导体']
    changes = [19.3, 11.0, 5.0, 9.0, 7.0, 5.2]
    colors_bar = ['#7C3AED', '#8B5CF6', '#A78BFA', '#8B5CF6', '#A78BFA', '#7C3AED']

    bars = ax.barh(stocks, changes, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, changes):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2.,
                f'+{val:.1f}%', ha='left', va='center', fontsize=9, fontweight='bold', color=DARK)

    # Revenue breakdown inset box
    ax.text(0.95, 0.05, '美光HBM产能全年售罄\n瑞银目标价 $535→$1,625',
            transform=ax.transAxes, fontsize=7.5, color=DARK, ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#F5F3FF', edgecolor='#C4B5FD', alpha=0.9))

    ax.set_title('全球半导体板块引爆 — 2026.05.26/27', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_xlim(0, 24)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'semiconductor_surge.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')  # noqa

    print("=" * 50)
    print("Chart Generator for 扬说财经")
    print("=" * 50)

    paths = []
    paths.append(chart_nvidia_revenue())
    paths.append(chart_nvidia_net_income())
    paths.append(chart_gold_price())
    paths.append(chart_cb_gold_purchases())
    paths.append(chart_pboc_reserves())
    paths.append(chart_astock_indices())
    paths.append(chart_sector_flow())
    paths.append(chart_oil_price())
    paths.append(chart_global_markets())
    paths.append(chart_semiconductor_surge())

    print("=" * 50)
    print(f"Generated {len(paths)} charts")
    for p in paths:
        size = os.path.getsize(p)
        print(f"   {os.path.basename(p)}  ({size/1024:.1f} KB)")
    print("=" * 50)
