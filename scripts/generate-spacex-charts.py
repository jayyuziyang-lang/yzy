#!/usr/bin/env python3
"""
扬说财经 · SpaceX专题 数据可视化图表
专题: SpaceX虹吸效应——万亿估值如何吸走全球资本？
生成: 4张专业数据图表（matplotlib SVG）
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os, sys, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# 加载品牌风格
style_path = os.path.join(ROOT_DIR, 'stylelib', 'yangshuo.mplstyle')
if os.path.exists(style_path):
    plt.style.use(style_path)

def setup_font():
    chinese_fonts = [
        'Noto Sans SC Medium', 'Noto Sans SC Regular',
        'PingFang SC Semibold', 'PingFang SC Medium', 'PingFang SC',
        'Microsoft YaHei UI', 'Microsoft YaHei',
        'SimHei', 'Droid Sans Fallback'
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in chinese_fonts:
        if font in available:
            plt.rcParams['font.family'] = font
            plt.rcParams['font.weight'] = 'bold'
            plt.rcParams['axes.unicode_minus'] = False
            return font
    for f in fm.fontManager.ttflist:
        if 'CJK' in f.name or 'SC' in f.name or 'Hei' in f.name or 'YaHei' in f.name:
            plt.rcParams['font.family'] = f.name
            plt.rcParams['font.weight'] = 'bold'
            plt.rcParams['axes.unicode_minus'] = False
            return f.name
    return None

FONT = setup_font()
print(f"  Font: {FONT}")

sys.path.insert(0, os.path.join(ROOT_DIR, 'stylelib'))
from yangshuo_palette import *

OUTPUT_DIR = os.path.join(ROOT_DIR, 'special', 'SpaceX虹吸效应', 'comic')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 图表 1: 史上最大IPO对比（水平柱状图）
# ============================================================
def chart_ipo_comparison():
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    companies = ['SpaceX\n(2026)', '沙特阿美\n(2019)', '阿里巴巴\n(2014)', 'NTT Mobile\n(1998)', 'Uber\n(2019)']
    values = [75.0, 25.6, 25.0, 18.4, 8.1]
    colors = [BLUE_500, GOLD_600, RED_500, PURPLE_500, BRAND_LIGHT]

    bars = ax.barh(companies, values, height=0.55, color=colors, edgecolor='white', linewidth=0.5)

    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height()/2,
                f'${v}B', va='center', ha='left', fontsize=11, fontweight='bold',
                color=BRAND_DARK)

    ax.set_xlim(0, 95)
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(left=False)
    ax.tick_params(axis='y', labelsize=10, colors=BRAND_GRAY)

    # Title
    fig.text(0.12, 0.92, '史上最大IPO：SpaceX $750亿 vs 所有对手',
             fontsize=14, fontweight='bold', color=BRAND_DARK, va='bottom')
    fig.text(0.12, 0.88, '首发规模接近沙特阿美的3倍，超过全球所有科技IPO年度总和',
             fontsize=8.5, color=SUBTTITLE, va='top')
    fig.text(0.12, 0.03, '来源: Bloomberg / SEC Filing — 2026年6月',
             fontsize=7, color=FOOTNOTE, va='bottom')
    fig.text(0.88, 0.03, 'SpaceX虹吸效应 · 扬说深度',
             fontsize=7, color=FOOTNOTE, va='bottom', ha='right')

    plt.subplots_adjust(left=0.18, right=0.88, top=0.82, bottom=0.10)
    path = os.path.join(OUTPUT_DIR, 'chart-ipo-comparison.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {path}')

# ============================================================
# 图表 2: 空间板块冲击全景（水平柱状图，负值）
# ============================================================
def chart_sector_impact():
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    stocks = ['维珍银河\n(SPCE)', 'Redwire\n(RDW)', 'Rocket Lab\n(RKLB)', 'EchoStar\n(SATS)',
              'AST SpaceMobile\n(ASTS)', 'Intuitive Machines\n(LUNR)', 'Planet Labs\n(PL)',
              'UFO太空ETF']
    declines = [-37, -13, -13, -14, -16, -10, -9, -7.9]
    colors_deep = [GREEN_700, GREEN_600, GREEN_600, GREEN_600,
                   GREEN_600, GREEN_500, GREEN_500, GREEN_500]

    bars = ax.barh(stocks, declines, height=0.5, color=colors_deep, edgecolor='white', linewidth=0.5)

    for bar, v in zip(bars, declines):
        ax.text(-0.5, bar.get_y() + bar.get_height()/2,
                f'{v}%', va='center', ha='right', fontsize=11, fontweight='bold',
                color=BRAND_DARK)

    ax.set_xlim(-42, 5)
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.axvline(0, color='#CBD5E1', linewidth=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(left=False)
    ax.tick_params(axis='y', labelsize=9.5, colors=BRAND_GRAY)

    # Annotations
    ax.annotate('SpaceX上市日\n资金大面积流出',
                xy=(-37, 0), xytext=(-39, 1.5),
                fontsize=8, color=BRAND_GRAY, ha='left',
                arrowprops=dict(arrowstyle='->', color=BRAND_GRAY, lw=0.8))

    # Title
    fig.text(0.12, 0.92, 'SpaceX上市日：周边概念股集体暴跌',
             fontsize=14, fontweight='bold', color=BRAND_DARK, va='bottom')
    fig.text(0.12, 0.88, '"SpaceX替代品"的逻辑一夜崩塌，资金全部流向正品',
             fontsize=8.5, color=SUBTTITLE, va='top')
    fig.text(0.12, 0.03, '来源: Yahoo Finance / Bloomberg — 2026年6月12日',
             fontsize=7, color=FOOTNOTE, va='bottom')
    fig.text(0.88, 0.03, 'SpaceX虹吸效应 · 扬说深度',
             fontsize=7, color=FOOTNOTE, va='bottom', ha='right')

    plt.subplots_adjust(left=0.22, right=0.88, top=0.82, bottom=0.10)
    path = os.path.join(OUTPUT_DIR, 'chart-sector-impact.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {path}')


# ============================================================
# 图表 3: 估值对比——市场价 vs DCF模型（组合柱状图+数据标签）
# ============================================================
def chart_valuation_gap():
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    labels = ['SpaceX\n市场估值', 'SpaceX\nDCF估值', '波音\n市场估值', 'Lockheed Martin\n市场估值']
    values = [2.1, 0.78, 0.95, 1.3]
    colors = [BLUE_500, BLUE_200, BRAND_LIGHT, BRAND_LIGHT]

    bars = ax.bar(labels, values, width=0.5, color=colors, edgecolor='white', linewidth=0.5)

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'${v:.2f}T', va='bottom', ha='center', fontsize=12, fontweight='bold',
                color=BRAND_DARK)

    # Gap arrow
    ax.annotate('',
                xy=(1.2, 0.78), xytext=(1.2, 2.1),
                arrowprops=dict(arrowstyle='<->', color=RED_500, lw=1.5))
    ax.text(1.6, 1.55, '$1.32T\n差距', fontsize=9, fontweight='bold',
            color=RED_600, va='center')

    ax.set_ylim(0, 2.5)
    ax.set_ylabel('万亿美元', fontsize=9, color=BRAND_GRAY, labelpad=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(BRAND_LINE)
    ax.spines['bottom'].set_color(BRAND_LINE)
    ax.tick_params(axis='y', labelsize=9, colors=BRAND_GRAY)
    ax.tick_params(axis='x', labelsize=9, colors=BRAND_GRAY)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.1f}T'))

    # Title
    fig.text(0.12, 0.92, '估值鸿沟：市场定价 vs 基本面',
             fontsize=14, fontweight='bold', color=BRAND_DARK, va='bottom')
    fig.text(0.12, 0.88, 'Morningstar DCF模型算出$0.78T——仅为市场价的37%',
             fontsize=8.5, color=SUBTTITLE, va='top')
    fig.text(0.12, 0.03, '来源: Morningstar / Bloomberg / Yahoo Finance — 2026年6月',
             fontsize=7, color=FOOTNOTE, va='bottom')
    fig.text(0.88, 0.03, 'SpaceX虹吸效应 · 扬说深度',
             fontsize=7, color=FOOTNOTE, va='bottom', ha='right')

    plt.subplots_adjust(left=0.12, right=0.88, top=0.82, bottom=0.12)
    path = os.path.join(OUTPUT_DIR, 'chart-valuation-gap.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {path}')


# ============================================================
# 图表 4: 未来时间线——虹吸效应演进（事件时间线图）
# ============================================================
def chart_timeline():
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Define events: (date, label, impact_level, y_pos, detail)
    events = [
        ('2026-06-12', 'SpaceX上市\n$750亿融资', 3.0, '首日+19%\n市值$2.1T'),
        ('2026-07', '纳指100\n正式纳入', 2.0, '被动基金强制买入\n再平衡压力加剧'),
        ('2026-09', 'Anthropic\nIPO预期', 2.5, '估值~$9650亿\n预计再抽血$500亿+'),
        ('2026-10', 'OpenAI\nIPO预期', 2.5, '估值>$1万亿\n虹吸效应第二波'),
        ('2026-12', '锁定180天\n期到期', 3.5, '内部人90%股份解锁\n潜在卖压$2000亿+'),
    ]

    # Draw horizontal timeline
    for i, (date, label, impact, detail) in enumerate(events):
        x = i * 1.3 + 0.2
        y = 0

        # Impact circle (size = impact level)
        size = 80 + impact * 60
        color = BLUE_500 if impact < 2.5 else (GOLD_500 if impact < 3.0 else RED_500)
        ax.scatter([x], [y], s=size, c=color, zorder=5, edgecolors='white', linewidth=2)

        # Date label above
        date_clean = date.replace('2026-', '')
        ax.text(x, y + 0.15, date_clean, ha='center', va='bottom',
                fontsize=8, fontweight='bold', color=BRAND_GRAY)

        # Event name above
        ax.text(x, y + 0.6, label, ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=BRAND_DARK, linespacing=1.3)

        # Detail below
        ax.text(x, y - 0.5, detail, ha='center', va='top',
                fontsize=7.5, color=SUBTTITLE, linespacing=1.3)

    # Timeline line
    for i in range(len(events)):
        x1 = i * 1.3 + 0.2
        x2 = (i + 1) * 1.3 + 0.2
        if i < len(events) - 1:
            ax.plot([x1 + 0.1, x2 - 0.1], [0, 0], color=BRAND_LINE, linewidth=2, zorder=1)

    # "现在" marker
    ax.annotate('▲ 现在',
                xy=(0.2, 0.15), xytext=(0.2, 0.35),
                fontsize=8, fontweight='bold', color=RED_600, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED_600, lw=1.5))

    # Warning zone: right side after Sep
    ax.axvspan(2.5, 6.0, ymin=0.4, ymax=0.6, alpha=0.06, color=RED_500)
    ax.text(5.5, 0, '虹吸效应\n高峰区', fontsize=8, color=RED_300,
            ha='center', va='center', fontweight='bold')

    ax.set_ylim(-1.8, 2.0)
    ax.set_xlim(-0.4, 6.0)
    ax.axis('off')

    # Title
    fig.text(0.12, 0.92, '虹吸效应演进时间线：接下来会发生什么？',
             fontsize=14, fontweight='bold', color=BRAND_DARK, va='bottom')
    fig.text(0.12, 0.88, '2026下半年是虹吸效应的关键冲击窗口——锁定期到期将决定最终影响',
             fontsize=8.5, color=SUBTTITLE, va='top')
    fig.text(0.12, 0.03, '来源: SEC Filing / Bloomberg / Nasdaq — 2026年6月 | 时间线为预期，实际可能存在变动',
             fontsize=7, color=FOOTNOTE, va='bottom')
    fig.text(0.88, 0.03, 'SpaceX虹吸效应 · 扬说深度',
             fontsize=7, color=FOOTNOTE, va='bottom', ha='right')

    plt.subplots_adjust(left=0.08, right=0.92, top=0.82, bottom=0.10)
    path = os.path.join(OUTPUT_DIR, 'chart-timeline.svg')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {path}')


# ============================================================
# 执行
# ============================================================
if __name__ == '__main__':
    print('[SpaceX专题] 数据可视化图表生成')
    print('=' * 50)
    chart_ipo_comparison()
    chart_sector_impact()
    chart_valuation_gap()
    chart_timeline()
    print('=' * 50)
    print(f'  [OK] 全部4张图表生成完成')
