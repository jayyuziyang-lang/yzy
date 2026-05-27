# 扬说财经 · 数据可视化质量升级培训手册

> 目标：让团队具备生产 Bloomberg/FT 级别图表的能力
> 更新日期：2026-05-27

---

## 目录

1. [核心认知：先思考，再制图](#1-核心认知先思考再制图)
2. [Matplotlib 架构深度解析](#2-matplotlib-架构深度解析)
3. [专业颜色系统](#3-专业颜色系统)
4. [图表类型选择指南](#4-图表类型选择指南)
5. [风格工厂：创建专属 mplstyle](#5-风格工厂创建专属-mplstyle)
6. [六大进阶图表模板](#6-六大进阶图表模板)
7. [商业级精度：FT/WSJ/Economist 风格拆解](#7-商业级精度ftwsjeconomist-风格拆解)
8. [工作流与质量门禁](#8-工作流与质量门禁)
9. [实战作业](#9-实战作业)
10. [学习资源](#10-学习资源)

---

## 1. 核心认知：先思考，再制图

### 1.1 一个图表的黄金标准

| 维度 | 差 | 好 | 卓越 |
|------|-----|-----|------|
| 准确 | 有色差、刻度误导 | 数据正确 | 数据可追溯、刻度有意 |
| 清晰 | 文字堆叠、颜色杂乱 | 一目了然 | 一眼抓住核心信息 |
| 美观 | 默认配色、无排版 | 配色协调 | 有品牌感、像出版物 |
| 有洞察 | 只有数字 | 有注释说明 | 标题就是结论 |

### 1.2 制图五问

在写任何 `plt.subplots()` 之前，先回答：

```
1. 这张图要传达什么核心信息？（一句话）
2. 谁在看？（普通读者 / 投资者 / 同行）
3. 哪种图表最适合传递这个信息？（不是每个数据都需要柱状图）
4. 哪个数据点最重要？如何强调它？
5. 如果只能保留一个视觉元素，应该是什么？
```

### 1.3 反模式（我们的常见错误）

```
❌ "所有柱子不同颜色" — 除了强调色，其他用灰色
❌ "以图例代替标注" — 直接标在图上，不要让人来回看
❌ "旋转X轴标签" — 改为水平条形图
❌ "Y轴不从0开始"（柱状图）— 柱状图Y轴必须从0
❌ "所有元素同等重要" — 视觉层次要分明
❌ "依赖默认配色" — 主动选择色板
```

---

## 2. Matplotlib 架构深度解析

### 2.1 三层定制体系

```
运行时 rcParams（最高优先级）
    ↑
MPL 样式文件 (.mplstyle)（可组合、可复用）
    ↑
matplotlibrc 启动配置（用户级）
    ↑
matplotlib 内置默认值（最低优先级）
```

### 2.2 rcParams：一切的核心

`matplotlib.rcParams` 是一个全局字典，存储约 **300 多个**配置参数。理解它是高质量定制的关键。

#### 核心参数分组

```python
# ========== 字体 ==========
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10.0
plt.rcParams['font.weight'] = 'normal'

# ========== 图形 ==========
plt.rcParams['figure.figsize'] = (6.4, 4.8)
plt.rcParams['figure.dpi'] = 100.0
plt.rcParams['figure.facecolor'] = 'white'

# ========== 坐标轴 ==========
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['axes.edgecolor'] = '#E2E8F0'
plt.rcParams['axes.labelcolor'] = '#1E293B'
plt.rcParams['axes.grid'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.prop_cycle'] = 'color'  # 配色循环

# ========== 网格 ==========
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.alpha'] = 0.15
plt.rcParams['grid.linewidth'] = 0.5

# ========== 线条 ==========
plt.rcParams['lines.linewidth'] = 2.5
plt.rcParams['lines.markersize'] = 6.0
plt.rcParams['lines.markeredgewidth'] = 0.0

# ========== 图例 ==========
plt.rcParams['legend.frameon'] = False
plt.rcParams['legend.fontsize'] = 9.0
plt.rcParams['legend.loc'] = 'best'

# ========== 保存 ==========
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.transparent'] = False

# ========== 刻度 ==========
plt.rcParams['xtick.color'] = '#64748B'
plt.rcParams['ytick.color'] = '#64748B'
plt.rcParams['xtick.labelsize'] = 9.0
plt.rcParams['ytick.labelsize'] = 9.0
```

### 2.3 .mplstyle 文件格式

创建一个 `yangshuo.mplstyle` 文件：

```ini
# 扬说财经 · 品牌风格
# 文件路径：stylelib/yangshuo.mplstyle

# 图形
figure.figsize : 5.5, 3.2
figure.dpi : 200
figure.facecolor : F8FAFC

# 坐标轴
axes.facecolor : F8FAFC
axes.edgecolor : E2E8F0
axes.spines.top : False
axes.spines.right : False
axes.labelcolor : 1E293B
axes.grid : True
axes.grid.axis : y
axisbelow : True

# 网格
grid.color : E2E8F0
grid.alpha : 0.15
grid.linewidth : 0.5

# 字体
font.family : sans-serif
font.size : 10

# 线条
lines.linewidth : 2.5
lines.markersize : 6
lines.markeredgewidth : 1.5

# 图例
legend.frameon : False
legend.fontsize : 9
legend.loc : best

# 保存
savefig.dpi : 200
savefig.facecolor : F8FAFC
savefig.bbox : tight

# 刻度
xtick.color : 64748B
ytick.color : 64748B
xtick.labelsize : 9
ytick.labelsize : 9
```

### 2.4 使用方式

```python
# 方式一：全局使用
import matplotlib.pyplot as plt
plt.style.use('yangshuo')

# 方式二：上下文管理器（推荐）
with plt.style.context('yangshuo'):
    fig, ax = plt.subplots()
    ax.plot(data)
    ...

# 方式三：叠加风格
plt.style.use(['yangshuo', 'presentation'])  # 后者覆盖前者

# 方式四：运行时覆盖
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 16,
})
```

### 2.5 内置风格一览

matplotlib 自带的风格文件位于 `lib/matplotlib/mpl-data/stylelib/`：

| 风格名 | 特点 | 适用场景 |
|--------|------|---------|
| `default` | matplotlib 默认 | 快速验证 |
| `ggplot` | R ggplot2 风格，灰底白线 | 数据分析 |
| `seaborn-v0_8` | 暗网格、浅色背景 | 通用美观 |
| `fivethirtyeight` | 数据新闻，粗线条 | 新闻图表 |
| `dark_background` | 深色背景 | 演示/深色模式 |
| `bmh` | Bayesian Methods for Hackers | 学术感 |
| `classic` | 旧版 matplotlib 风格 | 兼容 |
| `Solarize_Light2` | 暖色系 | 柔和展示 |
| `_mpl-gallery` | 画廊示例 | 学习参考 |
| `tableau-colorblind10` | 色盲友好 10 色调色板 | 无障碍 |
| `fast` | 简化渲染，更快 | 大数据 |

---

## 3. 专业颜色系统

### 3.1 核心原则：从灰色开始

```
1. 先用纯灰色设计图表
2. 再只对最关键的数据点使用强调色
3. 不要给每个柱子不同颜色
```

### 3.2 扬说财经品牌色板

```python
# ========== 品牌核心色 ==========
# 红涨绿跌（中国A股惯例）
BRAND_RED    = '#DC2626'   # 涨 / 流入
BRAND_GREEN  = '#16A34A'   # 跌 / 流出
BRAND_BLUE   = '#1A56DB'   # 信息 / 科技
BRAND_GOLD   = '#D4A017'   # 黄金 / 贵金属
BRAND_PURPLE = '#7C3AED'   # 半导体 / 前沿科技
BRAND_ORANGE = '#EA580C'   # 商品 / 能源

# ========== 文本色系 ==========
DARK    = '#1E293B'   # 主标题
GRAY    = '#64748B'   # 次要文本 / 注释
LIGHT   = '#94A3B8'   # 辅助信息

# ========== 背景色系 ==========
BG_CARD  = '#F8FAFC'  # 卡片背景
BG_PAGE  = '#F5F7FA'  # 页面背景
WHITE    = '#FFFFFF'  # 纯白

# ========== 边框/网格 ==========
BORDER   = '#E2E8F0'  # 线条、边框、网格

# ========== 涨跌幅深浅渐变 ==========
# 涨幅越大 → 颜色越深
RED_50  = '#FEF2F2'   # 极浅（微涨）
RED_100 = '#FEE2E2'
RED_200 = '#FECACA'
RED_500 = '#EF4444'   # 中等（中涨）
RED_600 = '#DC2626'   # 深（大涨）
RED_700 = '#B91C1C'   # 极深（暴涨）

# 跌幅越大 → 颜色越深
GREEN_50  = '#F0FDF4'
GREEN_100 = '#DCFCE7'
GREEN_200 = '#BBF7D0'
GREEN_500 = '#22C55E'
GREEN_600 = '#16A34A'
GREEN_700 = '#15803D'

# ========== 半导体渐变（紫色系）==========
PURPLE_50  = '#F5F3FF'
PURPLE_100 = '#EDE9FE'
PURPLE_200 = '#DDD6FE'
PURPLE_500 = '#8B5CF6'
PURPLE_600 = '#7C3AED'
PURPLE_700 = '#6D28D9'
```

### 3.3 色盲友好注意事项

```python
# 不要仅靠颜色区分数据系列
# ❌ 不同颜色线条 + 图例
# ✅ 不同颜色 + 不同线型 + 直接标注

# 红绿搭配时注意
# 红绿色盲（8%男性）无法区分红色和绿色
# 解决方案：添加符号标记（o, s, ^）+ 线型（-, --, -.）
```

### 3.4 配色方案决策树

```
需要显示正负值？
  ├── A股涨跌幅 → 红绿配色（红涨绿跌）
  ├── 资金流向 → 红绿配色（红流入绿流出）
  └── 其他正负 → 红蓝发散（RdBu）

需要比较类别？
  ├── 有重点类别 → 灰色+一个强调色
  └── 多类别平等 → 单色渐变或调色板

需要时间趋势？
  └── 品牌色系折线
```

---

## 4. 图表类型选择指南

### 4.1 决策树

```
需要展示什么？
│
├── 类别比较 → 水平条形图（优先）或柱状图
│   ├── 数据量大（>10项）→ 水平条形图（barh）
│   └── 数据量小 → 柱状图
│
├── 时间趋势 → 折线图
│   ├── 单条线 → 折线+填充
│   └── 多条线 → 分面子图，每条加标注
│
├── 分布 → 箱线图或核密度图
│
├── 两个时间点变化 → 斜率图（slope chart）
│   ├── 涨跌幅排名 → 棒棒糖图（lollipop）
│   └── 各板块变化 → 哑铃图（dumbbell）
│
├── 累积效应 → 瀑布图（waterfall）
│   └── 利润拆解、市值变化
│
├── 相关性 → 散点图
│
└── 占比 → 条形图（不要用饼图！）
```

### 4.2 金融场景专属推荐

| 数据类型 | 推荐图表 | 替代方案 | 注意事项 |
|----------|---------|---------|---------|
| 指数日涨跌 | 水平条形图（排序后） | 柱状图 | 红涨绿跌，标签直接在柱上 |
| 多市场对比 | 水平条形图 | 雷达图（别用） | 排序，突出最高最低 |
| 时间序列价格 | 折线图+填充 | 蜡烛图（太复杂） | 标注关键事件 |
| 板块资金流 | 水平条形图 | 饼图（别用） | 红流入绿流出 |
| 利润拆解 | 瀑布图 | 堆积柱状图 | 从营收→净利润 |
| 权重变化 | 百分比堆积条形图 | 饼图（别用） | 显示构成变化 |
| 历史分位数 | 箱线图+当前点 | 简单折线 | 标注当前分位 |
| 两期对比 | 斜率图 / 棒棒糖图 | 分组柱状图 | 直观显示"谁涨谁跌" |

### 4.3 必避开坑

```
❌ 饼图 — 人眼无法比较角度和面积
❌ 雷达图 — 面积比较有误导性
❌ 3D 图表 — 遮挡数据，无信息增量
❌ 堆积面积图（超过3个系列）— 互相遮挡
❌ 双 Y 轴 — 99%情况下是错误做法
```

---

## 5. 风格工厂：创建专属 mplstyle

### 5.1 创建扬说财经品牌风格

在项目根目录创建 `stylelib/` 文件夹，放入 `yangshuo.mplstyle`：

```ini
# stylelib/yangshuo.mplstyle
# 扬说财经 · 品牌视觉风格 v1.0

# === FIGURE ===
figure.figsize : 5.5, 3.2
figure.dpi : 200
figure.facecolor : F8FAFC
figure.titlesize : 14
figure.titleweight : bold

# === AXES ===
axes.facecolor : F8FAFC
axes.edgecolor : E2E8F0
axes.linewidth : 0.5
axes.spines.top : False
axes.spines.right : False
axes.spines.left : True
axes.spines.bottom : True
axes.labelcolor : 1E293B
axes.labelsize : 10
axes.labelweight : normal
axes.titlesize : 13
axes.titleweight : bold
axes.titlelocation : center
axes.titlepad : 14
axes.grid : True
axes.grid.axis : y
axisbelow : True

# === GRID ===
grid.color : E2E8F0
grid.alpha : 0.15
grid.linewidth : 0.5
grid.linestyle : -

# === LINES ===
lines.linewidth : 2.8
lines.linestyle : -
lines.color : 1A56DB
lines.marker : o
lines.markersize : 6
lines.markeredgewidth : 1.5
lines.markeredgecolor : auto
lines.dash_capstyle : round

# === PATCHES (bars, boxes) ===
patch.facecolor : 1A56DB
patch.edgecolor : FFFFFF
patch.linewidth : 1.5
patch.force_edgecolor : True

# === FONT ===
font.family : sans-serif
font.size : 10
font.weight : normal

# === TEXT ===
text.color : 1E293B

# === LEGEND ===
legend.frameon : False
legend.fontsize : 9
legend.loc : best
legend.handlelength : 1.5
legend.handletextpad : 0.5

# === TICKS ===
xtick.color : 64748B
ytick.color : 64748B
xtick.labelsize : 9
ytick.labelsize : 9
xtick.major.size : 3
ytick.major.size : 3
xtick.major.width : 0.5
ytick.major.width : 0.5

# === SAVEFIG ===
savefig.dpi : 200
savefig.facecolor : F8FAFC
savefig.bbox : tight
savefig.pad_inches : 0.1
savefig.transparent : False
savefig.format : svg
```

### 5.2 创建扬说财经专属配色表

```python
# yangshuo_palette.py
"""
扬说财经 · 品牌配色工具
配合 mplstyle 使用
"""

# 品牌色
BRAND_RED    = '#DC2626'
BRAND_GREEN  = '#16A34A'
BRAND_BLUE   = '#1A56DB'
BRAND_GOLD   = '#D4A017'
BRAND_PURPLE = '#7C3AED'
BRAND_ORANGE = '#EA580C'
BRAND_DARK   = '#1E293B'
BRAND_GRAY   = '#64748B'
BRAND_BG     = '#F8FAFC'

# 涨跌幅深浅（红涨绿跌）
RED_UP = [BRAND_RED, '#EF4444', '#F87171']
GREEN_DOWN = [BRAND_GREEN, '#22C55E', '#4ADE80']

# 色盲友好的补充配色
COLORBLIND_FRIENDLY = ['#1A56DB', '#D4A017', '#7C3AED', '#EA580C', '#059669']

# 配色工具函数
def get_up_down_color(value):
    """
    红涨绿跌：正数返回红色，负数返回绿色
    value: float — 涨跌幅数值
    returns: str — hex color
    """
    if value >= 3: return '#B91C1C'     # 暴涨
    if value >= 1: return BRAND_RED      # 涨
    if value > 0:  return '#EF4444'     # 微涨
    if value <= -3: return '#15803D'    # 暴跌
    if value <= -1: return BRAND_GREEN   # 跌
    return '#22C55E'                     # 微跌

def get_flow_color(value):
    """
    资金流向：正（流入）红色，负（流出）绿色
    """
    if value > 100:  return '#B91C1C'
    if value > 10:   return BRAND_RED
    if value > 0:    return '#EF4444'
    if value < -300: return '#15803D'
    if value < -100: return BRAND_GREEN
    return '#22C55E'
```

### 5.3 使用方法

```python
# 方式一：直接从文件加载
import matplotlib.pyplot as plt
plt.style.use('path/to/stylelib/yangshuo.mplstyle')

# 方式二：注册到 matplotlib（推荐）
import matplotlib.style as mplstyle
mplstyle.register([
    'path/to/stylelib/yangshuo.mplstyle'
])
# 之后可以直接 plt.style.use('yangshuo')

# 方式三：上下文局部使用
with plt.style.context('yangshuo'):
    fig, ax = plt.subplots()
    ...
```

---

## 6. 六大进阶图表模板

### 6.1 棒棒糖图（Lollipop Chart）

**用途**：涨跌幅排名，比条形图更简洁

```python
def lollipop_chart(labels, values, title='', xlabel='', color_brand='#DC2626'):
    """棒棒糖图 — 适合涨跌幅排名展示"""
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    # 排序
    sorted_idx = np.argsort(values)
    labels = [labels[i] for i in sorted_idx]
    values = [values[i] for i in sorted_idx]

    y = np.arange(len(labels))

    # 画竖线（茎）
    markerline, stemlines, baseline = ax.stem(
        values, y,
        linefmt='#CBD5E1', markerfmt='o', basefmt=''
    )

    # 自定义每个点的颜色
    for i, (val, stem) in enumerate(zip(values, stemlines)):
        stem.set_color('#94A3B8')
        stem.set_linewidth(1.5)

    # 自定义每个标记
    for i, val in enumerate(values):
        color = BRAND_RED if val >= 0 else BRAND_GREEN
        ax.plot(val, i, 'o', color=color, markersize=8,
                markeredgecolor='white', markeredgewidth=1.5, zorder=4)
        ax.text(val + (0.5 if val >= 0 else -0.5), i,
                f'{val:.2f}%', ha='left' if val >= 0 else 'right',
                va='center', fontsize=9, fontweight='bold', color=color)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel, fontsize=9, color=BRAND_GRAY)
    ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)
    ax.grid(axis='x', alpha=0.15, color=BRAND_GRAY, linewidth=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    return fig, ax
```

### 6.2 瀑布图（Waterfall Chart）

**用途**：从营收 → 净利润的拆解，或总市值的增减分解

```python
def waterfall_chart(categories, values, title='', ylabel='', fmt='${:.1f}B'):
    """
    瀑布图 — 从起点到终点的累积拆解
    categories: list[str] — 各项目名称
    values: list[float] — 各项目增减值（最后一个为总计）
    """
    import numpy as np
    n = len(categories)
    assert n == len(values)

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    # 计算累积基线
    cumulative = np.zeros(n)
    cumulative[0] = values[0]
    for i in range(1, n):
        cumulative[i] = cumulative[i-1] + values[i]

    # 绘制柱子
    x = np.arange(n)
    for i in range(n):
        if i == 0:  # 起点
            bottom = 0
            color = BRAND_BLUE
        elif i == n - 1:  # 终点（总计）
            bottom = 0
            color = BRAND_BLUE
        elif values[i] >= 0:  # 增加项
            bottom = cumulative[i-1]
            color = BRAND_RED
        else:  # 减少项
            bottom = cumulative[i]
            color = BRAND_GREEN
            values[i] = abs(values[i])

        height = abs(values[i])
        bar = ax.bar(i, height, bottom=bottom, width=0.5,
                     color=color, edgecolor='white', linewidth=1.5, zorder=3)

        # 值标签
        val = values[i] if i != 0 else cumulative[i]
        ax.text(i, bottom + height + 0.5,
                fmt.format(val), ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=BRAND_DARK)

    # 连接线
    for i in range(n - 1):
        curr_top = cumulative[i]
        ax.plot([i + 0.25, (i + 1) - 0.25],
                [curr_top, curr_top],
                color='#94A3B8', linewidth=0.8, linestyle='--')

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    ax.set_ylabel(ylabel, fontsize=9, color=BRAND_GRAY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color(BRAND_LINE)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)
    ax.grid(axis='y', alpha=0.15, color=BRAND_GRAY, linewidth=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    return fig, ax
```

### 6.3 斜率图（Slope Chart）

**用途**：两期数据的对比变化，例如 "上季度 vs 本季度各板块涨跌幅"

```python
def slope_chart(labels, start_vals, end_vals,
                start_label='上期', end_label='本期',
                title=''):
    """
    斜率图 — 对比两个时间点的数据变化
    """
    n = len(labels)
    x = [0, 1]

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    # 判断每个项目的涨跌
    changes = [end - start for start, end in zip(start_vals, end_vals)]

    for i in range(n):
        color = BRAND_RED if changes[i] > 0 else (BRAND_GREEN if changes[i] < 0 else BRAND_GRAY)
        alpha = min(1.0, 0.3 + 0.7 * abs(changes[i]) / max(abs(c) for c in changes))

        ax.plot(x, [start_vals[i], end_vals[i]], color=color,
                linewidth=1.5, alpha=alpha, zorder=2, marker='o',
                markersize=6, markerfacecolor='white',
                markeredgecolor=color, markeredgewidth=1.5)

        # 左标签
        ax.text(0 - 0.02, start_vals[i], labels[i], ha='right', va='center',
                fontsize=9, color=BRAND_DARK, fontweight='bold')
        # 右标签
        ax.text(1 + 0.02, end_vals[i],
                f'{end_vals[i]:.1f}', ha='left', va='center',
                fontsize=9, color=color, fontweight='bold')

    # 轴标签
    ax.text(0, max(start_vals) + 2, start_label, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=BRAND_GRAY)
    ax.text(1, max(end_vals) + 2, end_label, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=BRAND_GRAY)

    ax.set_xlim(-0.5, 1.5)
    ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)
    ax.set_xticks([])
    ax.set_yticks([])

    plt.tight_layout()
    return fig, ax
```

### 6.4 哑铃图（Dumbbell Chart）

**用途**：各指数高低点范围，或各行业估值分位数

```python
def dumbbell_chart(labels, low_vals, high_vals, title='',
                   xlabel='', low_label='低', high_label='高'):
    """
    哑铃图 — 显示两个端点之间的范围
    适合：估值区间、涨跌幅范围、预测区间
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    y = np.arange(len(labels))

    # 连接线
    for i in range(len(labels)):
        ax.plot([low_vals[i], high_vals[i]], [i, i],
                color='#CBD5E1', linewidth=2.5, zorder=1)

    # 低点（蓝色圆点）
    ax.scatter(low_vals, y, color=BRAND_BLUE, s=80, zorder=3,
               edgecolors='white', linewidth=1.5, label=low_label)
    # 高点（红色圆点）
    ax.scatter(high_vals, y, color=BRAND_RED, s=80, zorder=3,
               edgecolors='white', linewidth=1.5, label=high_label)

    # 标签
    for i in range(len(labels)):
        ax.text(low_vals[i] - 0.5, i, f'{low_vals[i]:.1f}',
                ha='right', va='center', fontsize=8, color=BRAND_BLUE)
        ax.text(high_vals[i] + 0.5, i, f'{high_vals[i]:.1f}',
                ha='left', va='center', fontsize=8, color=BRAND_RED)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel, fontsize=9, color=BRAND_GRAY)
    ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color(BRAND_LINE)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)
    ax.grid(axis='x', alpha=0.15, color=BRAND_GRAY)
    ax.legend(fontsize=9, loc='lower right')

    plt.tight_layout()
    return fig, ax
```

### 6.5 华夫饼图（Waffle Chart）

**用途**：展示占比（如「95% 的个股上涨」），比饼图精确 10 倍

```python
def waffle_chart(percentage, label='', title='', color=BRAND_RED):
    """
    华夫饼图 — 10x10 网格展示比例
    percentage: float 0~100
    """
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    n_filled = int(percentage)
    grid_size = 10
    bg_color = '#E2E8F0'

    for i in range(grid_size):
        for j in range(grid_size):
            idx = i * grid_size + j
            square_color = color if idx < n_filled else bg_color
            ax.add_patch(plt.Rectangle((j, grid_size - i - 1), 0.85, 0.85,
                                       facecolor=square_color, edgecolor='white',
                                       linewidth=1.5, zorder=2))

    ax.text(5, 10.5, title, ha='center', va='bottom',
            fontsize=13, fontweight='bold', color=BRAND_DARK)
    ax.text(5, 5, f'{percentage:.1f}%', ha='center', va='center',
            fontsize=28, fontweight='bold', color=color, zorder=3)
    if label:
        ax.text(5, -0.5, label, ha='center', va='top',
                fontsize=10, color=BRAND_GRAY)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.spines[:].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    plt.tight_layout()
    return fig, ax
```

### 6.6 带置信区间的趋势图

**用途**：显示不确定性范围 / 预测区间

```python
def trend_with_band(months, mid, upper, lower, title='',
                    ylabel='', fill_color='#1A56DB'):
    """
    带置信区间的趋势折线图
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    x = np.arange(len(months))

    # 置信区间填充
    ax.fill_between(x, lower, upper, alpha=0.12, color=fill_color)

    # 主趋势线
    ax.plot(x, mid, color=fill_color, linewidth=2.8, marker='o',
            markersize=5, markerfacecolor='white',
            markeredgecolor=fill_color, markeredgewidth=2, zorder=4)

    # 上下界虚线
    ax.plot(x, upper, color=fill_color, linewidth=0.8,
            linestyle='--', alpha=0.5)
    ax.plot(x, lower, color=fill_color, linewidth=0.8,
            linestyle='--', alpha=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_title(title, fontsize=13, fontweight='bold', color=BRAND_DARK, pad=14)
    ax.set_ylabel(ylabel, fontsize=9, color=BRAND_GRAY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color(BRAND_LINE)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.tick_params(colors=BRAND_GRAY, labelsize=9)
    ax.grid(axis='y', alpha=0.15, color=BRAND_GRAY)

    plt.tight_layout()
    return fig, ax
```

---

## 7. 商业级精度：FT/WSJ/Economist 风格拆解

### 7.1 Financial Times 风格

**特点**：橙色品牌色、白底、极简网格、左对齐标题、直接标注

```python
with plt.style.context('fivethirtyeight'):
    # 近似 FT 风格的 rcParams 调整
    plt.rcParams.update({
        'axes.facecolor': '#FFF1E5',     # FT 暖白底
        'figure.facecolor': '#FFF1E5',
        'axes.grid': True,
        'grid.alpha': 0.15,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'font.family': 'sans-serif',
        'figure.dpi': 200,
    })
```

**关键视觉元素**：
- 背景色：`#FFF1E5`（暖白）
- 强调色：橙色 `#FF8000`、蓝色 `#005FFF`
- 图表标题左对齐，加粗
- 数据直接标注，不使用图例
- 来源标注在右下角

### 7.2 Wall Street Journal 风格

**特点**：米色底、轻柔网格、金/蓝色调、庄重感

```python
WSJ_STYLE = {
    'axes.facecolor': '#F8F2E4',       # WSJ 米色背景
    'figure.facecolor': '#F8F2E4',
    'axes.grid': True,
    'grid.color': '#BFBFC0',
    'grid.linestyle': 'dotted',
    'axes.spines.right': False,
    'axes.spines.top': False,
}

# 色板
WSJ_COLORS = ['#E3122B', '#1A56DB', '#D4A017', '#059669', '#7C3AED']
```

### 7.3 The Economist 风格

**特点**：浅蓝灰背景、白色网格线、左上角红色条、Y轴在右侧

```python
ECONOMIST_STYLE = {
    'axes.facecolor': '#CFDBE7',       # 浅蓝灰
    'figure.facecolor': '#CFDBE7',
    'axes.grid': True,
    'grid.color': '#FFFFFF',            # 白色网格线
    'grid.linewidth': 1.2,
    'axes.spines.right': True,          # Y轴在右侧
    'axes.spines.top': False,
    'axes.spines.left': False,
}

# 左上角红色标志条
ax.plot([0, 0.08], [1.08, 1.08], transform=ax.transAxes,
        color='#E3122B', linewidth=12, clip_on=False)

# Ecnomist 品牌红
ECONOMIST_RED = '#E3122B'
```

### 7.4 一键切换：morethemes 包

```bash
pip install morethemes
```

```python
import morethemes as mt
import matplotlib.pyplot as plt

# 一键切换主题
mt.set_theme("ft")         # Financial Times
mt.set_theme("wsj")        # Wall Street Journal
mt.set_theme("economist")  # The Economist

# 预览当前主题
mt.preview_theme()
```

---

## 8. 工作流与质量门禁

### 8.1 生产流程

```
┌─────────────────────────────────────────┐
│ Step 1: 需求分析                          │
│   - 这个图表回答什么问题？                 │
│   - 谁是读者？                           │
│   - 选什么图表类型？                      │
├─────────────────────────────────────────┤
│ Step 2: 数据准备                          │
│   - 数据来源可追溯                        │
│   - 数据排序（如有必要）                   │
│   - 单位统一                             │
├─────────────────────────────────────────┤
│ Step 3: 草图                              │
│   - 先手画或用 Excel 快速验证布局          │
│   - 确定核心信息点                        │
├─────────────────────────────────────────┤
│ Step 4: 代码实现                          │
│   - 使用团队 mplstyle                     │
│   - 品牌配色                              │
│   - 有注释 + 标题即结论                   │
├─────────────────────────────────────────┤
│ Step 5: 渲染 → 检查 → 修复（关键步骤）    │
│   - 临时 PNG 输出                        │
│   - 检查：标签重叠？截断？强调得当？       │
│   - 修复后再次渲染确认                    │
├─────────────────────────────────────────┤
│ Step 6: 最终输出                          │
│   - SVG 用于 Web（矢量可缩放）            │
│   - PNG/PDF 用于印刷（300dpi）            │
│   - 小尺寸压缩版本（如需）                 │
└─────────────────────────────────────────┘
```

### 8.2 检查清单

每个图表生成后，逐项检查：

```
□ 标题是否传达了结论？（不是描述数据，而是揭示含义）
□ 颜色是否正确？（红涨绿跌）
□ 是否有重叠的文字？
□ 最重要的数据点是否一眼可见？
□ 是否有需要标注的事件/异常点？
□ 图例是否可以替换为直接标注？
□ 坐标标签是否清晰？
□ 是否有不必要的装饰（3D、阴影、渐变过度）？
□ 数据来源是否可追溯？
□ 输出格式是否正确（SVG for Web / 高DPI for print）？
```

### 8.3 修复示例

```
问题：柱状图文字重叠
方案：
  1. 增大 figsize（临时的）
  2. 水平条形图替代（根本解决方案）
  3. 调整标签位置避开（offset 计算）

问题：颜色误导
方案：
  1. 确认正负含义（涨跌 / 流入流出）
  2. 使用色盲友好的备选方案（符号+颜色）

问题：默认风格太丑
方案：
  1. 加载团队 mplstyle
  2. 自定义 rcParams
  3. （终极方案）安装 morethemes
```

---

## 9. 实战作业

### 练习 1：风格迁移

将以下代码改造成扬说财经品牌风格：

```python
import matplotlib.pyplot as plt
import numpy as np

# 原始代码（丑！）
months = ['1月', '2月', '3月', '4月', '5月', '6月']
revenue = [120, 135, 128, 145, 160, 158]

plt.bar(months, revenue, color=['red', 'blue', 'green', 'yellow', 'purple', 'orange'])
plt.title('Monthly Revenue')
plt.show()

# 你的任务：
# 1. 使用水平条形图
# 2. 灰色+一个强调色
# 3. 直接标注数据
# 4. 标题即结论
```

### 练习 2：红涨绿跌应用

给定数据：

```python
indices = ['上证指数', '深证成指', '创业板指', '科创50', '沪深300']
changes = [-0.15, 0.32, 0.78, -1.23, 0.05]
```

1. 正确应用红涨绿跌配色
2. 按涨跌幅排序
3. 用棒棒糖图替代柱状图

### 练习 3：FT 风格迁移

1. 安装 `morethemes` 包
2. 用 `mt.set_theme("ft")` + 我们的品牌颜色覆写关键元素
3. 生成一张 半导体板块涨跌幅 的 FT 风格图

### 练习 4：瀑布图

将以下利润拆解用瀑布图展示：

```
营收: 1000亿
- 营业成本: -600亿
- 研发费用: -100亿
- 销售费用: -50亿
+ 投资收益: +20亿
- 税费: -30亿
= 净利润: 240亿
```

---

## 10. 学习资源

### 官方文档

- [Matplotlib Customizing](https://matplotlib.org/stable/users/explain/customizing.html) — rcParams 完整参考
- [Matplotlib Style Sheet Reference](https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html) — 内置风格预览
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html) — 官方画廊

### 专业工具包

- [morethemes](https://pypi.org/project/morethemes/) — FT/WSJ/Economist 一键切换
- [highlight_text](https://pypi.org/project/highlight-text/) — 出版物级文字标注
- [matplotlib-label-lines](https://github.com/cphyc/matplotlib-label-lines) — 自动标注折线

### 进阶阅读

- [《Python数据可视化之美》](http://www.broadview.com.cn/file/samplefile/092052216175048000140171020241185039239002110234) — 商业图表绘制完整指南（中文）
- [From Data to Viz](https://www.data-to-viz.com/) — 图表类型选择决策树
- [Financial Times Visual Vocabulary](https://ft.com/vocabulary) — FT 可视化词汇表
- [Matplotlib 源码](https://github.com/matplotlib/matplotlib) — 核心架构在 `lib/matplotlib/`
  - `lib/matplotlib/rcsetup.py` — 默认参数定义+验证器
  - `lib/matplotlib/style/core.py` — `use()` / `context()` 实现
  - `lib/matplotlib/mpl-data/stylelib/` — 内置风格文件

### 设计原则

- [数据可视化五大黄金原则](https://xie.infoq.cn/article/cac87c215562e765bd56e21f9) — 中文精讲
- [Python 从"能看"到"好看"的 10 个实用技巧](http://mp.weixin.qq.com/s?__biz=MzcwNzI0MDkyNg==&mid=2247483729&idx=1&sn=602793e70f096bff1924608a9bde4d5f)

---

> **最后提醒**：一个卓越的图表 = 正确的数据 × 清晰的信息 × 精良的制作。
> 每张图都是一个产品，用心对待每一次渲染。
