#!/usr/bin/env python3
"""
扬说财经 · 2026-06-02 早报专项图表
基于今日6故事内容生成SVG数据图表
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
PURPLE = '#8B5CF6'

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'charts')
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Chart 1: A股6月1日资金行业内部分化
# 对应 故事一（A股）：结构切换
# ============================================================
def chart_astock_flow():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    sectors = ['电子', '机械设备', '通信', '有色金属', '国防军工', '银行', '传媒', '计算机']
    values = [-240.5, -59.9, -42.7, -32.1, -30.2, 4.0, 39.6, 41.6]
    colors_bar = []
    for v in values:
        if v >= 0:
            colors_bar.append(RED if v > 30 else GREEN)
        else:
            colors_bar.append(RED if v < -100 else '#F87171')

    bars = ax.barh(sectors, values, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, values):
        label = f'{val:+.1f}亿'
        if val < 0:
            ax.text(bar.get_width() - 3, bar.get_y() + bar.get_height()/2.,
                    label, ha='right', va='center', fontsize=9, fontweight='bold', color='white')
        else:
            ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2.,
                    label, ha='left', va='center', fontsize=9, fontweight='bold',
                    color=GREEN if val < 30 else RED)

    ax.set_title('6月1日A股主力资金流向（亿元）', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('净流入/出（亿元）', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_xlim(-300, 80)
    ax.axvline(x=0, color=DARK, linewidth=0.8)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    ax.text(0.5, -0.18, '数据来源：Wind · 证券时报 · 东方财富', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'astock_flow_june2.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 2: 芯片板块隔夜分化（NVIDIA PC宣战）
# 对应 故事二（美股）+ 头号焦点
# ============================================================
def chart_chip_divergence():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    stocks = ['ARM', 'Cadence', 'NVIDIA', '戴尔', '美光', 'IBM', 'AMD', '高通', '英特尔']
    changes = [16.1, 10.5, 6.3, 10.5, 6.6, 7.6, -1.2, -5.6, -4.7]
    colors_bar = []
    for v in changes:
        colors_bar.append(GREEN if v >= 0 else RED)

    bars = ax.bar(stocks, changes, color=colors_bar, width=0.6, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, changes):
        label = f'+{val:.1f}%' if val > 0 else f'{val:.1f}%'
        color_label = GREEN if val >= 0 else RED
        y_pos = bar.get_height() + 0.6 if val >= 0 else bar.get_height() - 1.2
        va = 'bottom' if val >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2., y_pos, label,
                ha='center', va=va, fontsize=8, fontweight='bold', color=color_label)

    ax.set_title('芯片板块隔夜涨跌幅 — GTC Taipei后', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_ylim(-10, 22)
    ax.axhline(y=0, color=DARK, linewidth=0.8)
    ax.grid(axis='y', alpha=0.2, color=GRAY)
    ax.set_xticklabels(stocks, rotation=20, ha='right', fontsize=8)

    ax.text(0.5, -0.18, '数据来源：CNBC · 各公司公告 · 高盛研报', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'chip_divergence_june2.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 3: 油价暴涨+黄金回落（跷跷板）
# 对应 故事六（商品/黄金）
# ============================================================
def chart_oil_gold_see_saw():
    fig, ax1 = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax1.set_facecolor(BG)

    months = ['2025/11', '12', '2026/1', '2', '3', '4', '5', '6/1']
    x = np.arange(len(months))

    # WTI油价
    oil = [68, 72, 78, 105, 98, 92, 87, 92]
    # 黄金
    gold = [3800, 3950, 4200, 5600, 4700, 4520, 4530, 4485]

    color_oil = DARK_BLUE
    color_gold = GOLD

    ax1.plot(x, oil, color=color_oil, linewidth=2.5, marker='^', markersize=6,
             label='WTI原油 ($/桶)', zorder=3)
    ax1.fill_between(x, oil, alpha=0.08, color=color_oil)

    ax2 = ax1.twinx()
    ax2.plot(x, gold, color=color_gold, linewidth=2.5, marker='s', markersize=6,
             label='现货黄金 ($/oz)', zorder=3)
    ax2.fill_between(x, gold, alpha=0.08, color=color_gold)

    # 标注关键点
    ax1.annotate('伊朗局势\n油价暴跌16%',
                 xy=(5, 87), xytext=(3.5, 75),
                 fontsize=7, color=GRAY, ha='center',
                 arrowprops=dict(arrowstyle='->', color=GRAY, lw=1))

    ax1.annotate('霍尔木兹威胁\n油价+5.5%',
                 xy=(6.5, 92), xytext=(5, 110),
                 fontsize=7, color=ORANGE, ha='center', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.2))

    ax2.annotate('金价历史峰值\n$5,600',
                 xy=(3, 5600), xytext=(1.5, 5850),
                 fontsize=7, color=RED, ha='center', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

    ax1.set_xlabel('时间', fontsize=9, color=GRAY)
    ax1.set_ylabel('WTI原油 ($/桶)', fontsize=9, color=color_oil)
    ax2.set_ylabel('黄金 ($/oz)', fontsize=9, color=color_gold)
    ax1.set_xticks(x)
    ax1.set_xticklabels(months, fontsize=7, color=GRAY)
    ax1.set_ylim(50, 120)
    ax2.set_ylim(3000, 6200)

    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_color('#E2E8F0')
    ax2.spines['right'].set_color('#E2E8F0')
    ax1.tick_params(colors=GRAY, labelsize=8)
    ax2.tick_params(colors=GRAY, labelsize=8)
    ax1.grid(axis='y', alpha=0.15, color=GRAY)

    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               fontsize=7, framealpha=0.85, edgecolor='#E2E8F0')

    ax1.set_title('油金跷跷板：伊朗威胁推油价，紧缩预期压金价', fontsize=12, fontweight='bold', color=DARK, pad=12)

    ax1.text(0.5, -0.18, '数据来源：COMEX · 新华财经 · LME', transform=ax1.transAxes,
             fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'oil_gold_seesaw_june2.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 4: 全球市场表现对比
# 对应 综合：如何看待三大指数同步新高
# ============================================================
def chart_global_markets_june2():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    markets = ['费城半导体', '纳斯达克', 'ARM', '标普500', '日经225', 'A股科创50', '欧洲STOXX', '恒生指数', '韩国KOSPI']
    changes = [5.12, 0.42, 16.1, 0.26, -1.5, -5.0, -0.8, -1.2, 0.3]
    colors_bar = [GREEN if v >= 0 else RED for v in changes]

    bars = ax.barh(markets, changes, color=colors_bar, height=0.5, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, changes):
        label = f'+{val:.1f}%' if val > 0 else f'{val:.1f}%'
        color_label = GREEN if val >= 0 else RED
        x_pos = bar.get_width() + 0.4 if val >= 0 else bar.get_width() - 0.4
        ha = 'left' if val >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2., label,
                ha=ha, va='center', fontsize=8, fontweight='bold', color=color_label)

    ax.set_title('隔夜全球核心市场表现', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_xlabel('涨跌幅 (%)', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=8)
    ax.set_xlim(-8, 22)
    ax.axvline(x=0, color=DARK, linewidth=0.8)
    ax.grid(axis='x', alpha=0.2, color=GRAY)

    ax.text(0.5, -0.18, '数据来源：各市场收盘数据 · CNBC · 东方财富', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'global_markets_june2.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"✅ {path}")
    return path


# ============================================================
# Chart 5: Anthropic估值飞跃 vs OpenAI对比
# 对应 故事三（科技/AI）
# ============================================================
def chart_ai_valuations():
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    companies = ['Anthropic\n(2024)', 'Anthropic\n(2025)', 'Anthropic\n(今夏IPO)', 'OpenAI\n(今夏)', 'SpaceX\n(今夏)']
    valuations = [180, 380, 965, 852, 1750]

    colors_bar = [PURPLE, PURPLE, '#7C3AED', '#6366F1,', '#8B5CF6']
    colors_fill = [PURPLE, PURPLE, '#7C3AED', '#6366F1', '#8B5CF6']

    bars = ax.bar(companies, valuations, color=colors_fill, width=0.55, edgecolor='white', linewidth=0.8)

    for bar, val in zip(bars, valuations):
        label = f'${val}B'
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 25, label,
                ha='center', va='bottom', fontsize=9, fontweight='bold', color=DARK)

    ax.set_title('AI巨头估值飞跃（十亿美元）', fontsize=13, fontweight='bold', color=DARK, pad=12)
    ax.set_ylabel('估值（十亿美元）', fontsize=9, color=GRAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(colors=GRAY, labelsize=7)
    ax.set_ylim(0, 2000)
    ax.grid(axis='y', alpha=0.15, color=GRAY)

    # 加箭头标注
    ax.annotate('近万亿估值\n超OpenAI',
                xy=(2, 965), xytext=(1, 1200),
                fontsize=8, color=PURPLE, fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', color=PURPLE, lw=1.5))

    ax.text(0.5, -0.18, '数据来源：SEC文件 · 华尔街日报 · Yahoo Finance', transform=ax.transAxes,
            fontsize=8, color=GRAY, ha='center', va='top')

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'ai_valuations_june2.svg')
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
    print("扬说财经 · 2026-06-02 早报专项图表")
    print("=" * 50)

    paths = []
    paths.append(chart_astock_flow())
    paths.append(chart_chip_divergence())
    paths.append(chart_oil_gold_see_saw())
    paths.append(chart_global_markets_june2())
    paths.append(chart_ai_valuations())

    print("=" * 50)
    print(f"Generated {len(paths)} charts")
    for p in paths:
        size = os.path.getsize(p)
        print(f"   {os.path.basename(p)}  ({size/1024:.1f} KB)")
    print("=" * 50)
