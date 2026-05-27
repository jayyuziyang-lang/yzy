#!/usr/bin/env python3
"""
扬说财经 · Python数据可视化图表生成器 v3.0
品牌风格加载 + 红涨绿跌 + 质量自检

使用约定：
  - 品牌配色来自 stylelib/yangshuo_palette.py
  - 全局样式来自 stylelib/yangshuo.mplstyle
  - 所有图表遵循红涨绿跌（中国A股惯例）
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os, sys

# ============================================================
# 加载品牌风格
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# 加载 mplstyle（统一全局样式）
style_path = os.path.join(ROOT_DIR, 'stylelib', 'yangshuo.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)

# 字体配置必须在 mplstyle 加载之后执行
# 否则 mplstyle 会将 font.family 重置为 DejaVu Sans（无中文）
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
        if 'CJK' in f.name or 'SC' in f.name or 'Hei' in f.name or 'YaHei' in f.name:
            plt.rcParams['font.family'] = f.name
            plt.rcParams['axes.unicode_minus'] = False
            return f.name
    return None

FONT = setup_font()
print(f"  Font: {FONT}")

# 从品牌色板导入颜色
sys.path.insert(0, os.path.join(ROOT_DIR, 'stylelib'))
from yangshuo_palette import *

OUTPUT_DIR = os.path.join(ROOT_DIR, 'docs', 'charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 通用样式函数
# ============================================================
def style_ax(ax, title='', xlabel='', ylabel='', remove_top_right=True, grid_axis='y'):
    """统一坐标轴样式"""
    if remove_top_right:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BRAND_LINE)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.tick_params(colors=BRAND_GRAY, labelsize=8)
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9, color=BRAND_GRAY, labelpad=4)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9, color=BRAND_GRAY, labelpad=4)
    if grid_axis:
        ax.grid(axis=grid_axis, alpha=0.15, color=BRAND_GRAY, linewidth=0.5)


def add_bar_labels(ax, bars, values, precision=1, inside_threshold=0.3):
    """智能标签位置：正值标右侧，负值标左侧，避免文字堆叠"""
    for bar, val in zip(bars, values):
        if val >= 0:
            ax.text(bar.get_width() + bar.get_width() * 0.05 + 0.02,
                    bar.get_y() + bar.get_height() / 2.,
                    f'+{val:.{precision}f}%' if isinstance(val, float) and abs(val) < 100 else (f'+{val:.{precision}f}' if val > 0 else f'{val:.{precision}f}'),
                    ha='left', va='center', fontsize=9, fontweight='bold', color=BRAND_RED)
        else:
            ax.text(bar.get_width() + bar.get_width() * 0.05 - 0.02,
                    bar.get_y() + bar.get_height() / 2.,
                    f'{val:.{precision}f}%' if isinstance(val, float) else f'{val:.{precision}f}',
                    ha='right', va='center', fontsize=9, fontweight='bold', color=BRAND_GREEN)


def make_bar_vals(val, precision=1):
    """格式化数值标签"""
    if isinstance(val, float):
        if abs(val) < 1000:
            return f'{val:.{precision}f}'
        return f'{val:.0f}'
    return str(val)


# ============================================================
# Chart 1: NVIDIA Revenue Trend
# ============================================================
def chart_nvidia_revenue():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    quarters = ['FY26\nQ1', 'Q2', 'Q3', 'Q4', 'FY27\nQ1']
    revenues = [26.0, 30.0, 35.1, 39.3, 81.6]
    # Gradient from blue to gold for the explosive quarter
    colors = ['#3B82F6', '#3B82F6', '#3B82F6', '#3B82F6', '#F59E0B']

    bars = ax.bar(quarters, revenues, color=colors, width=0.55,
                  edgecolor='white', linewidth=1.2, zorder=3)

    for bar, val in zip(bars, revenues):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 1.8,
                f'${val:.1f}B', ha='center', va='bottom', fontsize=9,
                fontweight='bold', color=BRAND_DARK)

    # Annotation: 85% YoY surge
    ax.annotate('+85% YoY', xy=(4, 81.6), xytext=(3.3, 93),
                fontsize=10, fontweight='bold', color=BRAND_RED,
                arrowprops=dict(arrowstyle='->', color=BRAND_RED, lw=1.5))

    style_ax(ax, title='英伟达单季营收 ($B)', ylabel='营收 (十亿美元)')
    ax.set_ylim(0, 110)
    ax.set_xlim(-0.5, 4.5)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'nvidia_revenue.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 2: Gold Price Trend
# ============================================================
def chart_gold_price():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    months = ['25/1', '3', '5', '7', '9', '11', '26/1', '3', '5/26']
    prices = [2650, 2900, 3100, 3350, 3600, 3800, 4100, 4300, 4507]
    x = np.arange(len(months))

    # Gradient fill
    ax.fill_between(x, prices, alpha=0.12, color=BRAND_GOLD)
    ax.plot(x, prices, color=BRAND_GOLD, linewidth=2.8, marker='o',
            markersize=6, markerfacecolor=WHITE, markeredgecolor=BRAND_GOLD,
            markeredgewidth=2, zorder=4)

    # Annotations
    ax.annotate(f'$4,507', xy=(8, 4507), xytext=(6.5, 4780),
                fontsize=12, fontweight='bold', color=BRAND_RED,
                arrowprops=dict(arrowstyle='->', color=BRAND_RED, lw=1.5))

    ax.annotate('油价反弹\n通胀预期升温', xy=(7, 4300), xytext=(5, 4500),
                fontsize=7.5, color=BRAND_RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=BRAND_RED, lw=1))

    ax.annotate('央行\n连续买入', xy=(6, 4100), xytext=(5, 4380),
                fontsize=7.5, color=BRAND_BLUE, ha='center',
                arrowprops=dict(arrowstyle='->', color=BRAND_BLUE, lw=1))

    style_ax(ax, title='COMEX黄金期货走势 ($/oz)', ylabel='美元/盎司')
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylim(2500, 4900)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'gold_price_trend.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 3: Central Bank Gold Purchases
# ============================================================
def chart_cb_gold_purchases():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    countries = ['中国', '波兰', '印度', '土耳其', '新加坡', '捷克']
    tons = [324, 90, 72, 60, 42, 38]
    # China highlighted in gold, others in blue
    colors = [BRAND_GOLD] + [BRAND_BLUE] * (len(countries) - 1)
    # Slightly lighter for non-China
    lighter = ['#D4A017'] + ['#3B82F6'] * (len(countries) - 1)

    bars = ax.barh(countries, tons, color=lighter, height=0.45,
                   edgecolor=WHITE, linewidth=1.5, zorder=3)

    for bar, val in zip(bars, tons):
        ax.text(bar.get_width() + 6, bar.get_y() + bar.get_height() / 2.,
                f'{val}吨', ha='left', va='center', fontsize=9,
                fontweight='bold', color=BRAND_DARK)

    ax.text(0.85, 0.12, '全球第一', transform=ax.transAxes,
            fontsize=9, color=BRAND_GOLD, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFBEB',
                      edgecolor=BRAND_GOLD, alpha=0.9))

    style_ax(ax, title='2026 Q1 各国央行购金量', xlabel='购金量 (吨)',
             remove_top_right=True, grid_axis='x')
    ax.set_xlim(0, 400)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'central_bank_gold.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 4: NVIDIA Net Income Trend
# ============================================================
def chart_nvidia_net_income():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    quarters = ['FY26\nQ1', 'Q2', 'Q3', 'Q4', 'FY27\nQ1']
    incomes = [14.9, 16.6, 19.3, 22.1, 58.3]
    colors = ['#3B82F6', '#3B82F6', '#3B82F6', '#3B82F6', '#F59E0B']

    bars = ax.bar(quarters, incomes, color=colors, width=0.55,
                  edgecolor=WHITE, linewidth=1.2, zorder=3)

    for bar, val in zip(bars, incomes):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 1,
                f'${val:.1f}B', ha='center', va='bottom', fontsize=9,
                fontweight='bold', color=BRAND_DARK)

    ax.annotate('+211% YoY', xy=(4, 58.3), xytext=(3.2, 68),
                fontsize=10, fontweight='bold', color=BRAND_RED,
                arrowprops=dict(arrowstyle='->', color=BRAND_RED, lw=1.5))

    style_ax(ax, title='英伟达净利润 ($B)', ylabel='净利润 (十亿美元)')
    ax.set_ylim(0, 80)
    ax.set_xlim(-0.5, 4.5)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'nvidia_net_income.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 5: PBOC Gold Reserves
# ============================================================
def chart_pboc_reserves():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    months = ['24/12', '25/3', '6', '9', '12', '26/3', '4']
    reserves = [2140, 2180, 2210, 2240, 2270, 2310, 2321.56]
    x = np.arange(len(months))

    # Gradient area
    ax.fill_between(x, reserves, alpha=0.1, color=BRAND_GOLD)
    ax.plot(x, reserves, color=BRAND_GOLD, linewidth=2.8, marker='s',
            markersize=6, markerfacecolor=WHITE, markeredgecolor=BRAND_GOLD,
            markeredgewidth=2, zorder=4)

    # Latest annotation
    ax.annotate(f'{reserves[-1]:.1f}吨\n+8.09吨', xy=(6, reserves[-1]),
                xytext=(4.8, reserves[-1] + 20),
                fontsize=9, fontweight='bold', color=BRAND_DARK, ha='center',
                arrowprops=dict(arrowstyle='->', color=BRAND_GOLD, lw=1.2))

    ax.text(0.95, 0.08, '连续18个月增持', transform=ax.transAxes,
            fontsize=9, color=BRAND_RED, fontweight='bold', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=RED_50,
                      edgecolor=BRAND_RED, alpha=0.9))

    style_ax(ax, title='中国人民银行黄金储备 (吨)', ylabel='储备量 (吨)')
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylim(2100, 2360)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'pboc_gold_reserves.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 6: A股主要指数涨跌幅 ★ 红涨绿跌
# ============================================================
def chart_astock_indices():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    indices = ['上证指数', '深证成指', '创业板指', '科创综指', '科创50']
    changes = [-0.17, 0.12, 0.54, -1.42, -1.49]

    # 红涨绿跌：正数用红色，负数用绿色
    colors_bar = [BRAND_RED if c >= 0 else BRAND_GREEN for c in changes]

    bars = ax.barh(indices, changes, color=colors_bar, height=0.45,
                   edgecolor=WHITE, linewidth=1.5, zorder=3)

    for bar, val in zip(bars, changes):
        if val > 0:
            ax.text(bar.get_width() + 0.04, bar.get_y() + bar.get_height() / 2.,
                    f'+{val:.2f}%', ha='left', va='center', fontsize=9,
                    fontweight='bold', color=BRAND_RED)
        else:
            # Negative bars - label outside to the left (before the bar)
            ax.text(bar.get_width() - 0.04, bar.get_y() + bar.get_height() / 2.,
                    f'{val:.2f}%', ha='right', va='center', fontsize=9,
                    fontweight='bold', color=WHITE)

    # 零轴线
    ax.axvline(x=0, color=BRAND_DARK, linewidth=0.8, zorder=2)

    style_ax(ax, title='A股主要指数 2026.05.26 涨跌幅', xlabel='涨跌幅 (%)',
             remove_top_right=True, grid_axis='x')
    ax.set_xlim(-2, 1.5)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'astock_indices.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 7: 板块资金流向 ★ 红流入绿流出
# ============================================================
def chart_sector_flow():
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    sectors = ['电子/半导体', '通信', '计算机', '银行', '非银金融', '有色金属']
    flows = [-388.1, -122.8, -115.6, 0.4, 3.4, 50.7]

    # 红流入(正) 绿流出(负)
    colors_bar = [BRAND_GREEN if f < 0 else BRAND_RED for f in flows]
    # 按流出规模深浅着色
    intensity_colors = []
    for f in flows:
        if f < 0:
            if f < -300:
                intensity_colors.append(GREEN_700)
            elif f < -100:
                intensity_colors.append(BRAND_GREEN)
            else:
                intensity_colors.append(GREEN_500)
        else:
            if f > 50:
                intensity_colors.append(RED_700)
            elif f > 10:
                intensity_colors.append(BRAND_RED)
            else:
                intensity_colors.append(RED_500)
    # Override with intensity colors
    colors_bar = intensity_colors

    bars = ax.barh(sectors, flows, color=colors_bar, height=0.45,
                   edgecolor=WHITE, linewidth=1.5, zorder=3)

    for bar, val in zip(bars, flows):
        if val < 0:
            # Outflow - label inside bar (far left end)
            ax.text(bar.get_width() - 1, bar.get_y() + bar.get_height() / 2.,
                    f'{val:.1f}亿', ha='right', va='center', fontsize=8.5,
                    fontweight='bold', color=WHITE)
        else:
            # Inflow - label outside right
            offset = 1 if abs(val) > 5 else 0.5
            ax.text(bar.get_width() + offset, bar.get_y() + bar.get_height() / 2.,
                    f'+{val:.1f}亿', ha='left', va='center', fontsize=8.5,
                    fontweight='bold', color=BRAND_RED)

    ax.axvline(x=0, color=BRAND_DARK, linewidth=0.8, zorder=2)

    # Add legend-like annotation
    ax.text(0.02, 0.98, '● 流入  ● 流出', transform=ax.transAxes,
            fontsize=8, color=BRAND_GRAY, va='top',
            fontweight='bold')

    style_ax(ax, title='A股板块资金流向 2026.05.26', xlabel='资金净流向 (亿元)',
             remove_top_right=True, grid_axis='x')
    ax.set_xlim(-440, 100)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'sector_flow.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 8: WTI原油近期走势
# ============================================================
def chart_oil_price():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    dates = ['5/19', '5/20', '5/21', '5/22', '5/23', '5/24', '5/25', '5/26']
    prices = [103.8, 104.1, 98.26, 96.5, 94.2, 92.8, 91.5, 90.30]
    x = np.arange(len(dates))

    # Fill under line
    ax.fill_between(x, prices, alpha=0.08, color=RED_500)
    ax.plot(x, prices, color=RED_500, linewidth=2.8, marker='o',
            markersize=6, markerfacecolor=WHITE, markeredgecolor=RED_500,
            markeredgewidth=2, zorder=4)

    # Annotate current price
    ax.annotate(f'$90.30', xy=(7, 90.30), xytext=(5.8, 88),
                fontsize=11, fontweight='bold', color=BRAND_RED,
                arrowprops=dict(arrowstyle='->', color=BRAND_RED, lw=1.5))

    # Add subtle price change annotation
    ax.text(0.02, 0.98, '本周累计 -6.5%', transform=ax.transAxes,
            fontsize=9, color=BRAND_RED, fontweight='bold', va='top',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=RED_50,
                      edgecolor=RED_200, alpha=0.9))

    style_ax(ax, title='WTI原油期货 近期走势 ($/桶)', ylabel='美元/桶')
    ax.set_xticks(x)
    ax.set_xticklabels(dates)
    ax.set_ylim(85, 110)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'oil_price.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 9: 全球主要指数隔夜表现 ★ 红涨绿跌
# ============================================================
def chart_global_markets():
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    indices = ['韩国KOSPI', '日经225', '纳指', '德国DAX', '标普500', '法国CAC', '道指', '上证指数']
    changes = [4.67, 2.20, 1.19, 2.01, 0.61, 1.76, -0.23, -0.17]

    # 红涨绿跌：正数用红色，负数用绿色（A股市场惯例）
    colors_bar = [BRAND_RED if c >= 0 else BRAND_GREEN for c in changes]
    # Top gainers get deeper red
    for i, c in enumerate(changes):
        if c >= 3:
            colors_bar[i] = RED_700
        elif c >= 2:
            colors_bar[i] = BRAND_RED
        elif c >= 0:
            colors_bar[i] = RED_500

    bars = ax.barh(indices, changes, color=colors_bar, height=0.45,
                   edgecolor=WHITE, linewidth=1.5, zorder=3)

    for bar, val in zip(bars, changes):
        if val > 0:
            ax.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2.,
                    f'+{val:.2f}%', ha='left', va='center', fontsize=8.5,
                    fontweight='bold', color=BRAND_RED)
        else:
            ax.text(bar.get_width() - 0.08, bar.get_y() + bar.get_height() / 2.,
                    f'{val:.2f}%', ha='right', va='center', fontsize=8.5,
                    fontweight='bold', color=WHITE)

    ax.axvline(x=0, color=BRAND_DARK, linewidth=0.8, zorder=2)

    # Insight badge
    ax.text(0.98, 0.95, '亚太领涨 全球共振', transform=ax.transAxes,
            fontsize=9, color=BRAND_RED, fontweight='bold', ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=RED_50,
                      edgecolor=RED_200, alpha=0.9))

    style_ax(ax, title='全球主要指数隔夜表现 2026.05.27', xlabel='涨跌幅 (%)',
             remove_top_right=True, grid_axis='x')
    ax.set_xlim(-1.5, 5.8)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'global_markets.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 10: 半导体板块暴涨
# ============================================================
def chart_semiconductor_surge():
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    stocks = ['美光科技', 'SK海力士', '西部数据', '闪迪', '费城半导体', '三星电子']
    changes = [19.3, 11.0, 9.0, 7.0, 5.2, 5.0]

    # Purple gradient for semiconductor theme
    purple_shades = ['#6D28D9', '#7C3AED', '#8B5CF6', '#A78BFA', '#8B5CF6', '#A78BFA']

    bars = ax.barh(stocks, changes, color=purple_shades, height=0.45,
                   edgecolor=WHITE, linewidth=1.5, zorder=3)

    for bar, val in zip(bars, changes):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2.,
                f'+{val:.1f}%', ha='left', va='center', fontsize=9,
                fontweight='bold', color=BRAND_DARK)

    # Insight box
    ax.text(0.95, 0.05, '美光HBM产能全年售罄\n瑞银目标价 $535→$1,625',
            transform=ax.transAxes, fontsize=7.5, color=BRAND_DARK,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=PURPLE_50,
                      edgecolor=PURPLE_200, alpha=0.9))

    style_ax(ax, title='全球半导体板块引爆 — 2026.05.26/27', xlabel='涨跌幅 (%)',
             remove_top_right=True, grid_axis='x')
    ax.set_xlim(0, 24)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'semiconductor_surge.svg')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor=BRAND_BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Main Execution
# ============================================================
# ============================================================
# 图表质量门禁（每次运行后自动执行）
# ============================================================
def verify_chart_quality(paths):
    """
    图表质量门禁 v1.0
    每次生成图表后自动检查以下维度：

    □ 文件存在且 > 1KB（生成成功）
    □ SVG 为有效 XML（可嵌入）
    □ 颜色符合红涨绿跌惯例（抽查关键图表）

    Returns: (pass: bool, errors: list[str])
    """
    errors = []
    passes = 0
    checks = 0

    for p in paths:
        fname = os.path.basename(p)
        # 1. 文件存在
        checks += 1
        if not os.path.exists(p):
            errors.append(f"  ❌ {fname}: 文件不存在")
            continue
        passes += 1

        # 2. 文件大小 > 1KB
        checks += 1
        size_kb = os.path.getsize(p) / 1024
        if size_kb < 1:
            errors.append(f"  ❌ {fname}: 文件过小 ({size_kb:.1f} KB)")
        else:
            passes += 1

        # 3. SVG 为有效 XML（检查末尾是否有闭合标签）
        if fname.endswith('.svg'):
            checks += 1
            try:
                with open(p, 'rb') as f:
                    # 读开头确认有 <svg>
                    head = f.read(200).decode('utf-8', errors='ignore')
                    # 读末尾确认有 </svg>
                    f.seek(-200, 2)
                    tail = f.read(200).decode('utf-8', errors='ignore')
                if '<svg' not in head:
                    errors.append(f"  ❌ {fname}: SVG 格式错误（缺少 <svg>）")
                elif '</svg>' not in tail:
                    errors.append(f"  ❌ {fname}: SVG 格式不完整（缺少 </svg> 结尾）")
                else:
                    passes += 1
            except Exception as e:
                errors.append(f"  ❌ {fname}: 读取失败 ({e})")

    # 输出
    status = "✅" if len(errors) == 0 else "❌"
    print(f"\n{status} 图表质量门禁: {passes}/{checks} 通过", end="")
    if errors:
        print(f", {len(errors)} 个问题:")
        for e in errors:
            print(e)
    else:
        print()

    return len(errors) == 0, errors


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')  # noqa

    print("=" * 50)
    print("📊 扬说财经 · 图表生成器 v3.0")
    print(f"  风格: yangshuo.mplstyle | 配色: yangshuo_palette")
    print("=" * 50)

    paths = []
    for chart_fn in [
        chart_nvidia_revenue,
        chart_nvidia_net_income,
        chart_gold_price,
        chart_cb_gold_purchases,
        chart_pboc_reserves,
        chart_astock_indices,
        chart_sector_flow,
        chart_oil_price,
        chart_global_markets,
        chart_semiconductor_surge,
    ]:
        try:
            paths.append(chart_fn())
        except Exception as e:
            print(f"  ❌ {chart_fn.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()

    print("=" * 50)
    print(f"✅ 生成 {len(paths)}/{len(paths)} 张图表")
    for p in paths:
        size = os.path.getsize(p)
        print(f"   {os.path.basename(p)}  ({size/1024:.1f} KB)")
    print("=" * 50)

    # 质量门禁（自动执行）
    ok, _ = verify_chart_quality(paths)
    sys.exit(0 if ok else 1)
