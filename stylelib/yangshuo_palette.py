"""
扬说财经 · 品牌配色工具 v2.0
配合 yangshuo.mplstyle v2.0 使用 — 专业财经媒体风格

v2.0 新增:
  - 面板/卡片配色（CARD_BG, FIGURE_BG, FOOTNOTE）
  - Economist 风格标注框配色
  - chart_titles() 统一标题层级

用法：
    from stylelib.yangshuo_palette import *

    # 获取涨跌颜色
    color = get_price_color(2.5)  # 返回红色 #DC2626
    color = get_price_color(-1.2) # 返回绿色 #16A34A

    # 获取资金流向颜色
    color = get_flow_color(50.7)   # 流入 → 红
    color = get_flow_color(-388.1) # 流出 → 绿
"""

# ============================================================
# 品牌核心色
# ============================================================
BRAND_RED    = '#DC2626'   # 涨 / 流入
BRAND_GREEN  = '#16A34A'   # 跌 / 流出
BRAND_BLUE   = '#1A56DB'   # 信息 / 科技 / 指数
BRAND_GOLD   = '#D4A017'   # 黄金 / 贵金属
BRAND_PURPLE = '#7C3AED'   # 半导体 / 前沿科技
BRAND_ORANGE = '#EA580C'   # 商品 / 能源
BRAND_DARK   = '#1E293B'   # 主要文本
BRAND_GRAY   = '#64748B'   # 次要文本
BRAND_LIGHT  = '#94A3B8'   # 辅助信息
BRAND_BG     = '#F8FAFC'   # 卡片背景（旧版兼容）
BRAND_LINE   = '#E2E8F0'  # 边框/网格线
WHITE        = '#FFFFFF'

# ============================================================
# v2.0 新增：专业图表布局配色
# ============================================================
FIGURE_BG  = '#F0F2F5'  # 图表整体容器背景（暖灰）
CARD_BG    = '#FFFFFF'  # 图表卡片/面板背景（纯白）
CARD_BORDER = '#E2E8F0' # 卡片边框
FOOTNOTE   = '#94A3B8'  # 脚注（数据来源）文字颜色
SUBTTITLE   = '#64748B'  # 副标题文字颜色
ACCENT_LINE = '#334155'  # 强调线/零轴线

# Economist 风格标注框
ECON_BG    = '#F8F9FA'  # 标注框背景
ECON_BORDER = '#DC2626' # 标注框红色边框

# ============================================================
# 涨跌幅色阶（红涨绿跌）
# ============================================================
# 红色系（越涨越深）
RED_50  = '#FEF2F2'
RED_100 = '#FEE2E2'
RED_200 = '#FECACA'
RED_300 = '#FCA5A5'
RED_400 = '#F87171'
RED_500 = '#EF4444'
RED_600 = '#DC2626'   # BRAND_RED
RED_700 = '#B91C1C'
RED_800 = '#991B1B'

# 绿色系（越跌越深）
GREEN_50  = '#F0FDF4'
GREEN_100 = '#DCFCE7'
GREEN_200 = '#BBF7D0'
GREEN_300 = '#86EFAC'
GREEN_400 = '#4ADE80'
GREEN_500 = '#22C55E'
GREEN_600 = '#16A34A'  # BRAND_GREEN
GREEN_700 = '#15803D'
GREEN_800 = '#166534'

# 蓝色系
BLUE_50  = '#EFF6FF'
BLUE_100 = '#DBEAFE'
BLUE_200 = '#BFDBFE'
BLUE_300 = '#93C5FD'
BLUE_400 = '#60A5FA'
BLUE_500 = '#3B82F6'
BLUE_600 = '#2563EB'
BLUE_700 = '#1D4ED8'

# 紫色系（半导体）
PURPLE_50  = '#F5F3FF'
PURPLE_100 = '#EDE9FE'
PURPLE_200 = '#DDD6FE'
PURPLE_300 = '#C4B5FD'
PURPLE_400 = '#A78BFA'
PURPLE_500 = '#8B5CF6'
PURPLE_600 = '#7C3AED'
PURPLE_700 = '#6D28D9'

# 金色系
GOLD_50  = '#FFFBEB'
GOLD_100 = '#FEF3C7'
GOLD_200 = '#FDE68A'
GOLD_300 = '#FCD34D'
GOLD_400 = '#FBBF24'
GOLD_500 = '#F59E0B'
GOLD_600 = '#D97706'
GOLD_700 = '#B45309'

# ============================================================
# 色板列表（用于多系列对比）
# ============================================================
# 扬说财经主色板（按优先级排序）
BRAND_PALETTE = [
    BRAND_RED,      # #1 涨
    BRAND_BLUE,     # #2 科技/指数
    BRAND_GOLD,     # #3 黄金
    BRAND_PURPLE,   # #4 半导体
    BRAND_ORANGE,   # #5 商品
    BRAND_GREEN,    # #6 跌
]

# 扩展色板（6色以上使用）
EXTENDED_PALETTE = [
    BRAND_RED, BRAND_BLUE, BRAND_GOLD, BRAND_PURPLE,
    BRAND_ORANGE, BRAND_GREEN,
    '#0891B2', '#BE185D', '#65A30D', '#4F46E5',
]

# 色盲友好色板
COLORBLIND_FRIENDLY = [
    '#1A56DB', '#D4A017', '#7C3AED', '#EA580C',
    '#059669', '#0891B2', '#BE185D', '#4F46E5',
]

# ============================================================
# 专业图表标题布局
# ============================================================

def chart_titles(ax, title, subtitle=None, source=None):
    """
    在图表 axes 上方绘制专业标题层级（Economist/FT风格）：
      - 标题（大号粗体，左对齐）
      - 副标题（小号，灰色）
      - 数据来源（最小号，灰色，底部）

    注意：这是通过 fig.text 绘制在 figure 层面的布局函数。
    需要在 savefig 前调用。

    Args:
        ax: matplotlib.axes.Axes — 图表坐标轴
        title: str — 主标题
        subtitle: str | None — 副标题（可选）
        source: str | None — 数据来源（可选）
    """
    fig = ax.figure

    # === 主标题（figure 顶部左侧） ===
    fig.text(0.105, 0.92, title,
             fontsize=14, fontweight='bold',
             color=BRAND_DARK,
             va='bottom', ha='left',
             transform=fig.transFigure)

    # === 副标题（紧接主标题下方） ===
    if subtitle:
        fig.text(0.105, 0.88, subtitle,
                 fontsize=9, fontweight='normal',
                 color=SUBTTITLE,
                 va='top', ha='left',
                 transform=fig.transFigure)

    # === 数据来源（图表底部左侧） ===
    if source:
        fig.text(0.105, 0.02, f'来源: {source}',
                 fontsize=7, fontweight='normal',
                 color=FOOTNOTE,
                 va='bottom', ha='left',
                 transform=fig.transFigure)


# ============================================================
# 配色工具函数
# ============================================================

def get_price_color(value):
    """
    红涨绿跌 — 基于涨跌幅返回对应颜色

    Args:
        value: float — 涨跌幅（%）

    Returns:
        str — hex color
    """
    if value >= 5:   return RED_700       # 暴涨
    if value >= 2:   return RED_600       # 大涨
    if value >= 0.5: return RED_500       # 中涨
    if value > 0:    return '#F87171'     # 微涨
    if value <= -5:  return GREEN_700     # 暴跌
    if value <= -2:  return GREEN_600     # 大跌
    if value <= -0.5: return GREEN_500    # 中跌
    return '#4ADE80'                       # 微跌


def get_flow_color(value):
    """
    资金流向颜色 — 红流入绿流出

    Args:
        value: float — 资金净流向（亿元）

    Returns:
        str — hex color
    """
    if value > 300:  return RED_700       # 大幅流入
    if value > 100:  return RED_600       # 中等流入
    if value > 10:   return RED_500       # 小幅流入
    if value > 0:    return '#F87171'     # 微幅流入
    if value < -300: return GREEN_700     # 大幅流出
    if value < -100: return GREEN_600     # 中等流出
    if value < -10:  return GREEN_500     # 小幅流出
    return '#4ADE80'                       # 微幅流出


def get_bar_colors(values, color_positive=BRAND_RED, color_negative=BRAND_GREEN):
    """
    根据数值正负返回柱状图颜色列表

    Args:
        values: list[float]
        color_positive: str — 正值颜色（默认红）
        color_negative: str — 负值颜色（默认绿）

    Returns:
        list[str] — 每个柱子对应的颜色
    """
    return [color_positive if v >= 0 else color_negative for v in values]


def get_intensity_colors(values, positive_deep=RED_700, positive_mid=BRAND_RED,
                         positive_light=RED_500, negative_light=GREEN_500,
                         negative_mid=BRAND_GREEN, negative_deep=GREEN_700):
    """
    根据数值大小返回深浅渐变色

    Args:
        values: list[float]

    Returns:
        list[str] — 每个柱子对应的颜色
    """
    import numpy as np
    arr = np.abs(values)
    if len(arr) == 0:
        return []
    mean = np.mean(arr)
    std = np.std(arr)

    colors = []
    for v in values:
        if v >= 0:
            if v > mean + std:
                colors.append(positive_deep)
            elif v > mean * 0.5:
                colors.append(positive_mid)
            else:
                colors.append(positive_light)
        else:
            abs_v = abs(v)
            if abs_v > mean + std:
                colors.append(negative_deep)
            elif abs_v > mean * 0.5:
                colors.append(negative_mid)
            else:
                colors.append(negative_light)
    return colors
