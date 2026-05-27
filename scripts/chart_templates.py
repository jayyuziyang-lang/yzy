"""
扬说财经 · 高级图表模板库 v1.0
六大进阶图表类型 + 品牌配色 + 红涨绿跌

用法：
    from chart_templates import *

    # 1. 棒棒糖图（涨跌幅排名）
    fig, ax = lollipop_chart(labels, values, title='板块涨跌幅排名')

    # 2. 瀑布图（利润拆解）
    fig, ax = waterfall_chart(items, amounts, title='净利润构成')

    # 3. 斜率图（两期对比）
    fig, ax = slope_chart(labels, start, end, title='QoQ对比')

    # 4. 哑铃图（范围展示）
    fig, ax = dumbbell_chart(labels, lows, highs, title='估值区间')

    # 5. 华夫饼图（占比展示）
    fig, ax = waffle_chart(percentage, label='上涨家数占比')

    # 6. 带置信区间的趋势图
    fig, ax = trend_with_band(months, mid, upper, lower)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os


# ============================================================
# 字体配置（优先中文字体）
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
        if 'CJK' in f.name or 'SC' in f.name or 'Hei' in f.name or 'YaHei' in f.name:
            plt.rcParams['font.family'] = f.name
            plt.rcParams['axes.unicode_minus'] = False
            return f.name
    return None

setup_font()

# ============================================================
# 品牌配色（与 yangshuo_palette.py 同步）
# ============================================================
BRAND_RED    = '#DC2626'
BRAND_GREEN  = '#16A34A'
BRAND_BLUE   = '#1A56DB'
BRAND_GOLD   = '#D4A017'
BRAND_PURPLE = '#7C3AED'
BRAND_ORANGE = '#EA580C'
BRAND_DARK   = '#1E293B'
BRAND_GRAY   = '#64748B'
BRAND_BG     = '#F8FAFC'
BRAND_LINE   = '#E2E8F0'
WHITE        = '#FFFFFF'

RED_500 = '#EF4444'
RED_600 = '#DC2626'
RED_700 = '#B91C1C'
GREEN_500 = '#22C55E'
GREEN_600 = '#16A34A'
GREEN_700 = '#15803D'


# ============================================================
# 样式工具
# ============================================================

def _style_ax(ax, title='', xlabel='', ylabel='', grid_axis='y'):
    """统一坐标轴样式"""
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color(BRAND_LINE)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9, color=BRAND_GRAY, labelpad=4)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9, color=BRAND_GRAY, labelpad=4)
    if grid_axis:
        ax.grid(axis=grid_axis, alpha=0.15, color=BRAND_GRAY, linewidth=0.5)
    ax.set_axisbelow(True)


# ============================================================
# 模板 1：棒棒糖图（涨跌幅排名）
# ============================================================

def lollipop_chart(labels, values, title='', xlabel='',
                   color_positive=BRAND_RED, color_negative=BRAND_GREEN,
                   precision=2):
    """
    棒棒糖图 — 适合展示涨跌幅排名
    比条形图更简洁，视觉冲击力更强

    Parameters
    ----------
    labels : list[str]
    values : list[float]
    title : str
    xlabel : str
    color_positive : str — 正值颜色（默认红）
    color_negative : str — 负值颜色（默认绿）
    precision : int — 数值精度
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    # 排序
    sorted_idx = np.argsort(values)
    labels_sorted = [labels[i] for i in sorted_idx]
    values_sorted = [values[i] for i in sorted_idx]
    y = np.arange(len(labels_sorted))

    # 画竖线
    for i, val in enumerate(values_sorted):
        color = color_positive if val >= 0 else color_negative
        intensity = min(abs(val) / max(abs(v) for v in values_sorted if v != 0), 1.0) if any(values_sorted) else 0
        alpha = 0.6 + 0.4 * intensity
        ax.plot([0, val], [i, i], color=color, linewidth=1.5, alpha=alpha, zorder=2)
        ax.plot(val, i, 'o', color=color, markersize=8,
                markeredgecolor=WHITE, markeredgewidth=1.5, zorder=3)

        # 标签
        fmt = f'+{{:.{precision}f}}%' if isinstance(val, float) else None
        label = fmt.format(val) if fmt else f'{val:.{precision}f}'
        if val >= 0:
            ax.text(val + max(values_sorted) * 0.02, i, label,
                    ha='left', va='center', fontsize=9, fontweight='bold', color=color)
        else:
            ax.text(val - max(abs(v) for v in values_sorted) * 0.02, i, label,
                    ha='right', va='center', fontsize=9, fontweight='bold', color=color)

    ax.set_yticks(y)
    ax.set_yticklabels(labels_sorted)
    ax.axvline(x=0, color=BRAND_DARK, linewidth=0.8, zorder=1)
    _style_ax(ax, title=title, xlabel=xlabel, grid_axis='x')
    # Auto-scale
    max_abs = max(abs(v) for v in values_sorted) * 1.3
    ax.set_xlim(-max_abs if min(values_sorted) < 0 else 0, max_abs)

    plt.tight_layout()
    return fig, ax


# ============================================================
# 模板 2：瀑布图（累积拆解）
# ============================================================

def waterfall_chart(categories, values, title='', ylabel='', fmt='{:.1f}', unit=''):
    """
    瀑布图 — 追踪从起点到终点的累积变化

    Parameters
    ----------
    categories : list[str] — 各项目名称（首项为起点，末项为总计）
    values : list[float] — 各项目增减值
    title : str
    ylabel : str
    fmt : str — 数字格式，如 '{:.1f}' 或 '${:.1f}B'
    unit : str — 单位后缀
    """
    n = len(categories)
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    # 计算累积基线
    running = np.zeros(n + 1)
    running[1] = values[0]
    for i in range(1, n):
        running[i + 1] = running[i] + values[i]

    x = np.arange(n)
    bar_width = 0.55

    for i in range(n):
        if i == 0:  # 起点
            bottom = 0
            height = values[0]
            color = BRAND_BLUE
        elif i == n - 1:  # 终点（总计）
            bottom = 0
            height = running[-1]
            color = BRAND_BLUE
        elif values[i] >= 0:  # 增加项
            bottom = running[i]
            height = values[i]
            color = BRAND_RED
        else:  # 减少项
            bottom = running[i + 1]
            height = abs(values[i])
            color = BRAND_GREEN

        bar = ax.bar(i, height, bottom=bottom, width=bar_width,
                     color=color, edgecolor=WHITE, linewidth=1.5, zorder=3)

        # 数值标签
        label_val = fmt.format(values[0] if i == 0 else (running[-1] if i == n - 1 else abs(values[i])))
        label_y = bottom + height + (max(running) * 0.02 if i > 0 else max(running) * 0.02)
        ax.text(i, label_y, label_val + unit, ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=BRAND_DARK)

    # 连接虚线
    for i in range(1, n):
        prev_top = running[i]
        ax.plot([i - 1 + bar_width / 2, i - bar_width / 2],
                [prev_top, prev_top],
                color='#94A3B8', linewidth=0.8, linestyle='--', zorder=1)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    _style_ax(ax, title=title, ylabel=ylabel, grid_axis='y')
    ax.set_ylim(0, max(running) * 1.15)

    plt.tight_layout()
    return fig, ax


# ============================================================
# 模板 3：斜率图（两期对比）
# ============================================================

def slope_chart(labels, start_vals, end_vals,
                start_label='上期', end_label='本期',
                title='', precision=1):
    """
    斜率图 — 对比两个时间点的变化
    适合：QoQ对比、前后变化、排名变化

    Parameters
    ----------
    labels : list[str]
    start_vals : list[float] — 起始值
    end_vals : list[float] — 结束值
    start_label : str
    end_label : str
    title : str
    precision : int
    """
    n = len(labels)
    fig, ax = plt.subplots(figsize=(6, 0.45 * n + 2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    x = [0, 1]
    changes = [e - s for s, e in zip(start_vals, end_vals)]
    max_abs = max(max(start_vals), max(end_vals))

    for i in range(n):
        color = BRAND_RED if changes[i] > 0 else (BRAND_GREEN if changes[i] < 0 else BRAND_GRAY)
        intensity = min(abs(changes[i]) / (max(abs(c) for c in changes) + 0.01), 1.0) if any(changes) else 0
        alpha = 0.4 + 0.6 * intensity

        ax.plot(x, [start_vals[i], end_vals[i]], color=color,
                linewidth=2 if intensity > 0.7 else 1.2,
                alpha=alpha, zorder=2,
                marker='o', markersize=6, markerfacecolor=WHITE,
                markeredgecolor=color, markeredgewidth=1.5)

        # 左标签
        ax.text(-0.02, start_vals[i], f'{labels[i]} {start_vals[i]:.{precision}f}',
                ha='right', va='center', fontsize=9, color=BRAND_DARK)
        # 右标签（带变化方向）
        change_sign = '+' if changes[i] > 0 else ''
        ax.text(1.02, end_vals[i],
                f'{end_vals[i]:.{precision}f} ({change_sign}{changes[i]:.{precision}f})',
                ha='left', va='center', fontsize=9,
                fontweight='bold' if abs(changes[i]) > 0 else 'normal',
                color=color if changes[i] != 0 else BRAND_GRAY)

    # 轴标签
    ax.text(0, max(start_vals) * 1.15, start_label, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=BRAND_GRAY)
    ax.text(1, max(end_vals) * 1.15, end_label, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=BRAND_GRAY)

    ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    ax.set_xlim(-0.5, 1.6)
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    plt.tight_layout()
    return fig, ax


# ============================================================
# 模板 4：哑铃图（范围展示）
# ============================================================

def dumbbell_chart(labels, low_vals, high_vals, title='',
                   xlabel='', low_label='低', high_label='高',
                   low_color=BRAND_BLUE, high_color=BRAND_RED):
    """
    哑铃图 — 显示两个端点之间的范围
    适合：估值区间、涨跌幅范围、预测区间、高低点

    Parameters
    ----------
    labels : list[str]
    low_vals : list[float]
    high_vals : list[float]
    title : str
    xlabel : str
    low_label : str
    high_label : str
    low_color : str
    high_color : str
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    y = np.arange(len(labels))

    # 连接线
    for i in range(len(labels)):
        ax.plot([low_vals[i], high_vals[i]], [i, i],
                color='#CBD5E1', linewidth=2.5, zorder=1)

    # 低点
    ax.scatter(low_vals, y, color=low_color, s=100, zorder=3,
               edgecolors=WHITE, linewidth=1.5, label=low_label)
    # 高点
    ax.scatter(high_vals, y, color=high_color, s=100, zorder=3,
               edgecolors=WHITE, linewidth=1.5, label=high_label)

    # 值标签
    for i in range(len(labels)):
        range_pct = (high_vals[i] - low_vals[i]) / low_vals[i] * 100 if low_vals[i] != 0 else 0
        ax.text(low_vals[i], i, f'{low_vals[i]:.1f}',
                ha='right', va='center', fontsize=8, color=low_color, fontweight='bold')
        ax.text(high_vals[i], i, f'{high_vals[i]:.1f}',
                ha='left', va='center', fontsize=8, color=high_color, fontweight='bold')
        ax.text((low_vals[i] + high_vals[i]) / 2, i,
                f'+{range_pct:.0f}%' if range_pct > 0 else f'{range_pct:.0f}%',
                ha='center', va='center', fontsize=7, color=BRAND_GRAY)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    _style_ax(ax, title=title, xlabel=xlabel, grid_axis='x')
    ax.legend(fontsize=9, loc='lower right')

    plt.tight_layout()
    return fig, ax


# ============================================================
# 模板 5：华夫饼图（占比展示）
# ============================================================

def waffle_chart(percentage, label='', title='', color=BRAND_RED, bg_color='#E2E8F0'):
    """
    华夫饼图 — 10x10 网格展示百分比
    比饼图精确 10 倍

    Parameters
    ----------
    percentage : float — 0~100
    label : str — 下方的说明文字
    title : str — 上方的标题
    color : str — 填充色
    bg_color : str — 背景色
    """
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    n_filled = int(round(percentage))
    grid_size = 10
    cell_size = 0.85

    for i in range(grid_size):
        for j in range(grid_size):
            idx = i * grid_size + j
            square_color = color if idx < n_filled else bg_color
            rect = plt.Rectangle((j, grid_size - i - 1), cell_size, cell_size,
                                 facecolor=square_color, edgecolor=WHITE,
                                 linewidth=1.5, zorder=2)
            ax.add_patch(rect)

    # 中心大百分比
    ax.text(5, 5, f'{percentage:.1f}%', ha='center', va='center',
            fontsize=28, fontweight='bold', color=color, zorder=3)
    if title:
        ax.text(5, 11, title, ha='center', va='bottom',
                fontsize=13, fontweight='bold', color=BRAND_DARK)
    if label:
        ax.text(5, -0.5, label, ha='center', va='top',
                fontsize=10, color=BRAND_GRAY)

    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 11)
    ax.set_aspect('equal')
    ax.spines[:].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    plt.tight_layout()
    return fig, ax


# ============================================================
# 模板 6：带置信区间的趋势图
# ============================================================

def trend_with_band(months, mid, upper, lower, title='',
                    ylabel='', fill_color=BRAND_BLUE,
                    annotate_last=True, unit=''):
    """
    带置信区间的趋势折线图

    Parameters
    ----------
    months : list[str] — X轴标签
    mid : list[float] — 中心值（趋势线）
    upper : list[float] — 上界
    lower : list[float] — 下界
    title : str
    ylabel : str
    fill_color : str — 填充和线条颜色
    annotate_last : bool — 是否标注最新值
    unit : str — 单位
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    x = np.arange(len(months))

    # 置信区间填充
    ax.fill_between(x, lower, upper, alpha=0.12, color=fill_color)

    # 主趋势线
    ax.plot(x, mid, color=fill_color, linewidth=2.8, zorder=4,
            marker='o', markersize=5, markerfacecolor=WHITE,
            markeredgecolor=fill_color, markeredgewidth=2)

    # 上下界虚线
    ax.plot(x, upper, color=fill_color, linewidth=0.8,
            linestyle='--', alpha=0.4, zorder=1)
    ax.plot(x, lower, color=fill_color, linewidth=0.8,
            linestyle='--', alpha=0.4, zorder=1)

    if annotate_last and len(mid) > 0:
        last_val = mid[-1]
        ax.annotate(f'{last_val:.1f}{unit}', xy=(len(months) - 1, last_val),
                    xytext=(len(months) - 1.5, last_val + (max(mid) - min(mid)) * 0.1),
                    fontsize=11, fontweight='bold', color=BRAND_RED,
                    arrowprops=dict(arrowstyle='->', color=BRAND_RED, lw=1.5))

    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=8)
    _style_ax(ax, title=title, ylabel=ylabel, grid_axis='y')

    plt.tight_layout()
    return fig, ax


# ============================================================
# 工具：红涨绿跌颜色生成
# ============================================================

def up_down_colors(values):
    """红涨绿跌"""
    return [BRAND_RED if v >= 0 else BRAND_GREEN for v in values]

def flow_colors(values):
    """红流入绿流出"""
    return [BRAND_RED if v >= 0 else BRAND_GREEN for v in values]


# ============================================================
# 演示
# ============================================================

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print('=' * 50)
    print('扬说财经 · 高级图表模板演示')
    print('=' * 50)

    # 生成所有模板示例
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'charts', 'templates')
    os.makedirs(output_dir, exist_ok=True)

    # 1. 棒棒糖图
    fig, ax = lollipop_chart(
        ['韩国KOSPI', '日经225', '纳指', '德国DAX', '标普500', '法国CAC', '道指', '上证指数'],
        [4.67, 2.20, 1.19, 2.01, 0.61, 1.76, -0.23, -0.17],
        title='全球主要指数涨跌幅 — 棒棒糖图',
        xlabel='涨跌幅 (%)'
    )
    fig.savefig(os.path.join(output_dir, 'lollipop_demo.svg'), bbox_inches='tight')
    plt.close()
    print('  OK: lollipop')

    # 2. 瀑布图
    fig, ax = waterfall_chart(
        ['营业收入', '营业成本', '研发费用', '销售费用', '投资收益', '税费', '净利润'],
        [1000, -600, -100, -50, 20, -30, 240],
        title='净利润构成 — 瀑布图',
        ylabel='金额 (亿元)',
        fmt='{:.0f}',
        unit='亿'
    )
    fig.savefig(os.path.join(output_dir, 'waterfall_demo.svg'), bbox_inches='tight')
    plt.close()
    print('  OK: waterfall')

    # 3. 斜率图
    fig, ax = slope_chart(
        ['上证指数', '深证成指', '创业板指', '科创50'],
        [-0.17, 0.12, 0.54, -1.49],
        [0.30, 0.50, -0.20, 1.10],
        start_label='昨日收盘',
        end_label='今日开盘',
        title='主要指数隔夜变化 — 斜率图'
    )
    fig.savefig(os.path.join(output_dir, 'slope_demo.svg'), bbox_inches='tight')
    plt.close()
    print('  OK: slope')

    # 4. 哑铃图
    fig, ax = dumbbell_chart(
        ['上证指数', '深证成指', '创业板指', '科创50'],
        [3000, 9800, 1800, 950],
        [3400, 11000, 2200, 1050],
        title='主要指数年内区间 — 哑铃图',
        xlabel='点位'
    )
    fig.savefig(os.path.join(output_dir, 'dumbbell_demo.svg'), bbox_inches='tight')
    plt.close()
    print('  OK: dumbbell')

    # 5. 华夫饼图
    fig, ax = waffle_chart(
        68.5,
        label='上涨家数占比',
        title='A股昨日涨跌家数'
    )
    fig.savefig(os.path.join(output_dir, 'waffle_demo.svg'), bbox_inches='tight')
    plt.close()
    print('  OK: waffle')

    # 6. 带置信区间趋势图
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    mid = [100, 105, 103, 108, 112, 110]
    upper = [102, 108, 106, 111, 116, 114]
    lower = [98, 102, 100, 105, 108, 106]
    fig, ax = trend_with_band(
        months, mid, upper, lower,
        title='营收预测趋势（含置信区间）',
        ylabel='营收 (亿)',
        fill_color=BRAND_BLUE
    )
    fig.savefig(os.path.join(output_dir, 'band_demo.svg'), bbox_inches='tight')
    plt.close()
    print('  OK: trend with band')

    print()
    print(f'所有模板已生成: {output_dir}')
