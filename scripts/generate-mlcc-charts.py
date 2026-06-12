#!/usr/bin/env python3
"""Generate static SVG chart versions for MLCC article, replacing Plotly iframes."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART_DIR = os.path.join(ROOT, 'ai-chain', 'mlcc-series', 'charts')

BLUE = '#1A56DB'
DARK = '#1E293B'
GRAY = '#94A3B8'

# Chinese font
chinese_fonts = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'Noto Sans SC', 'WenQuanYi Micro Hei']
for font in chinese_fonts:
    try:
        plt.rcParams['font.family'] = font
        plt.rcParams['axes.unicode_minus'] = False
        break
    except:
        continue

os.makedirs(CHART_DIR, exist_ok=True)


def save_chart(fig, name):
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'  [OK] {name}')


# ========== Chart 1: usage_per_device ==========
fig, ax = plt.subplots(figsize=(7, 4.2))
fig.patch.set_facecolor('white')
categories = ['AI服务器节点\n(GB200/GB300, 8GPU)', '电动车\n(EV/NEV)', '普通服务器\n(单台双路)', '燃油车\n(ICE)', '智能手机\n(5G旗舰)']
values = [30000, 18000, 4000, 5000, 1200]
colors_bar = ['#2563EB', '#F59E0B', '#60A5FA', '#9CA3AF', '#9CA3AF']
bars = ax.barh(categories, values, color=colors_bar, height=0.6)
for bar, v in zip(bars, values):
    ax.text(v + 600, bar.get_y() + bar.get_height()/2, f'{v:,}颗', va='center', fontsize=10, fontweight='bold', color=DARK)
ax.set_xlim(0, 40000)
ax.set_xlabel('MLCC用量（颗/台或颗/节点）', fontsize=10, color=DARK)
ax.set_title('单设备MLCC用量对比 (2024-2025)\nAI服务器单节点用量是普通服务器的10-15倍', fontsize=13, fontweight='bold', color=DARK, loc='left')
ax.spines[['top', 'right']].set_visible(False)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.tick_params(colors=GRAY, labelsize=9)
fig.text(0.5, 0.02, '数据来源：村田/TDK公开技术资料 | 中时电子报(2025.10) | 微信行业研究', ha='center', fontsize=7, color=GRAY)
plt.tight_layout(pad=2.0)
save_chart(fig, 'usage_per_device.svg')

# ========== Chart 2: market_share ==========
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5))
fig.patch.set_facecolor('white')
labels1 = ['Murata村田', '三星电机', '国巨Yageo', '太阳诱电', 'TDK', '中国厂商']
sizes1 = [35, 23, 15, 10, 7, 10]
colors_pie = ['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#F59E0B']
wedges1, _, autotexts1 = ax1.pie(sizes1, labels=labels1, autopct='%1.0f%%', colors=colors_pie, startangle=90, textprops={'fontsize': 8})
for t in autotexts1: t.set_fontweight('bold'); t.set_fontsize(9)
ax1.set_title('整体市场', fontsize=12, fontweight='bold', color=DARK)

labels2 = ['Murata村田', '三星电机', '太阳诱电', 'TDK', '国巨Yageo', '中国厂商']
sizes2 = [42, 26, 12, 8, 7, 5]
colors_pie2 = ['#1D4ED8', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#F59E0B']
wedges2, _, autotexts2 = ax2.pie(sizes2, labels=labels2, autopct='%1.0f%%', colors=colors_pie2, startangle=90, textprops={'fontsize': 8})
for t in autotexts2: t.set_fontweight('bold'); t.set_fontsize(9)
ax2.set_title('高端市场\n(01005/008004等微型规格)', fontsize=12, fontweight='bold', color=DARK)
fig.text(0.5, 0.01, '数据来源：TrendForce集邦咨询、各公司公开财报 | 中国厂商市占率为行业共识区间', ha='center', fontsize=7, color=GRAY)
plt.tight_layout(pad=2.0)
save_chart(fig, 'market_share.svg')

# ========== Chart 3: market_size ==========
fig, ax = plt.subplots(figsize=(7, 3.5))
fig.patch.set_facecolor('white')
years = ['2020', '2021', '2022', '2023', '2024', '2025E', '2026E', '2027E', '2028E']
vals = [38, 46, 42, 38, 44, 52, 61, 72, 85]
ax.fill_between(range(len(years)), vals, alpha=0.12, color=BLUE)
ax.plot(range(len(years)), vals, color=BLUE, linewidth=2.5, marker='o', markersize=6, zorder=3)
for i, v in enumerate(vals):
    ax.annotate(f'{v}', (i, v), textcoords='offset points', xytext=(0, 10), ha='center', fontsize=9, fontweight='bold', color=BLUE)
ax.set_xticks(range(len(years)))
ax.set_xticklabels(years, fontsize=9)
ax.set_ylabel('市场规模（亿美元）', fontsize=10, color=DARK)
ax.set_title('全球MLCC市场规模趋势 (2020-2028E)\n高端化+AI驱动下，2028年预计突破850亿美元', fontsize=13, fontweight='bold', color=DARK, loc='left')
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(colors=GRAY, labelsize=9)
ax.grid(axis='y', alpha=0.15, color=GRAY)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
fig.text(0.5, 0.02, '数据来源：ECIA、华经产业研究院、中国电子元件行业协会 | E=预测值', ha='center', fontsize=7, color=GRAY)
plt.tight_layout(pad=2.0)
save_chart(fig, 'market_size.svg')

# ========== Chart 4: price_cycle ==========
fig, ax = plt.subplots(figsize=(7, 3.5))
fig.patch.set_facecolor('white')
cats = ['通用0402\n(1uF/6.3V)', '通用0603\n(10uF/10V)', '车规0805\n(47uF/25V)', '高端1005\n(100uF/6.3V)', 'AI服务器\n专用大容量']
p1 = [0.5, 2, 15, 80, 200]
p2 = [2, 8, 50, 250, 800]
x = np.arange(len(cats))
width = 0.35
ax.bar(x - width/2, p1, width, label='标准品', color='#93C5FD', edgecolor='white', linewidth=0.5)
ax.bar(x + width/2, p2, width, label='高端品', color='#2563EB', edgecolor='white', linewidth=0.5)
ax.set_xticks(x)
ax.set_xticklabels(cats, fontsize=8)
ax.set_ylabel('单价（美分/颗）', fontsize=10, color=DARK)
ax.set_title('MLCC标准品 vs 高端品单价对比\n高端品价格是标准品的3-10倍，AI服务器规格是普通100倍', fontsize=13, fontweight='bold', color=DARK, loc='left')
ax.legend(fontsize=9)
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(colors=GRAY, labelsize=9)
ax.grid(axis='y', alpha=0.15, color=GRAY)
for i, (s, h) in enumerate(zip(p1, p2)):
    ax.annotate(f'{h/s:.0f}x', (i, max(s, h) + 50), ha='center', fontsize=9, fontweight='bold', color='#D97706')
fig.text(0.5, 0.02, '数据来源：国巨/村田官网报价、DigiKey分销商公开价格、行业研究报告（2024-2025年均价）', ha='center', fontsize=7, color=GRAY)
plt.tight_layout(pad=2.0)
save_chart(fig, 'price_cycle.svg')

# ========== Chart 5: tech_evolution ==========
fig, ax = plt.subplots(figsize=(7, 3.5))
fig.patch.set_facecolor('white')
techs = ['1990s\n通用型', '2000s\n高容型', '2010s\n超薄型', '2020s\n车规型', '2025+\nAI专用']
layers = [50, 200, 500, 800, 1000]
thickness = [50, 10, 3, 0.5, 0.3]
ax2 = ax.twinx()
bars = ax.bar(range(len(techs)), layers, color=['#BFDBFE', '#93C5FD', '#60A5FA', '#3B82F6', '#1D4ED8'], width=0.6, zorder=3)
line = ax2.plot(range(len(techs)), thickness, color='#DC2626', marker='D', markersize=6, linewidth=2, zorder=5, label='介质厚度(um)')
ax2.legend(loc='upper right', fontsize=9)
ax.set_xticks(range(len(techs)))
ax.set_xticklabels(techs, fontsize=8)
ax.set_ylabel('堆叠层数', fontsize=10, color=BLUE)
ax2.set_ylabel('介质厚度 (um)', fontsize=10, color='#DC2626')
ax.set_title('MLCC技术演进：更薄介质 + 更多层数\n从50层到1000层，介质厚度从50um降至0.3um', fontsize=13, fontweight='bold', color=DARK, loc='left')
ax.spines[['top', 'right']].set_visible(False)
ax2.spines[['top']].set_visible(False)
for bar, l in zip(bars, layers):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15, f'{l}层', ha='center', fontsize=9, fontweight='bold', color=BLUE)
ax.tick_params(colors=GRAY, labelsize=9)
ax2.tick_params(colors=GRAY, labelsize=9)
fig.text(0.5, 0.02, '数据来源：村田、TDK、三星电机技术白皮书 | 车规MLCC需AEC-Q200认证', ha='center', fontsize=7, color=GRAY)
plt.tight_layout(pad=2.0)
save_chart(fig, 'tech_evolution.svg')

# ========== Chart 6: ai_position_sankey (simplified as flow blocks) ==========
fig, ax = plt.subplots(figsize=(7, 3.5))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')
stages = [
    (0.5, 1.5, 3.5, 3.0, 'GPU功耗↑', '#DC2626', 0),
    (2.5, 1.0, 3.5, 3.5, '电流需求↑', '#D97706', 0),
    (4.5, 0.5, 3.5, 4.0, '电压纹波↑\n需要更多电容', '#2563EB', 0),
    (6.5, 1.0, 3.5, 3.5, 'MLCC用量↑\n(稳压/滤波)', '#7C3AED', 0),
]
for x, y, w, h, label, color, _ in stages:
    from matplotlib.patches import FancyBboxPatch
    rect = FancyBboxPatch((x, y), w, h, facecolor=color, alpha=0.15, edgecolor=color, linewidth=2, boxstyle="round,pad=0.02")
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=11, fontweight='bold', color=color)
# Arrows between blocks
ax.annotate('', xy=(4.5, 2.5), xytext=(4.0, 2.5), arrowprops=dict(arrowstyle='->', color=GRAY, lw=2))
ax.annotate('', xy=(6.5, 2.5), xytext=(6.0, 2.5), arrowprops=dict(arrowstyle='->', color=GRAY, lw=2))
ax.annotate('', xy=(2.5, 2.5), xytext=(2.0, 2.5), arrowprops=dict(arrowstyle='->', color=GRAY, lw=2))
ax.set_title('AI算力 → MLCC需求 传导链\nGPU功耗↑ → 电流↑ → 纹波↑ → 电容需求↑', fontsize=13, fontweight='bold', color=DARK, loc='left')
plt.tight_layout(pad=1.5)
save_chart(fig, 'ai_position_sankey.svg')

# ========== Chart 7: supply_chain (simplified network) ==========
fig, ax = plt.subplots(figsize=(7, 3.5))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')

# Supply chain nodes
nodes = [
    (1, 3.0, '陶瓷粉末\n(钛酸钡)', '#1A56DB'),
    (1, 1.5, '电极材料\n(镍粉)', '#1A56DB'),
    (3, 2.2, 'MLCC制造\n(村田/三星/国巨)', '#2563EB'),
    (5, 3.0, 'PCB组装\n(富士康/伟创力)', '#0F766E'),
    (5, 1.5, '模组厂\n(安费诺/泰科)', '#0F766E'),
    (7, 2.2, '服务器OEM\n(戴尔/惠普/超微)', '#D4A017'),
    (9, 2.2, '云厂商\n(AWS/GCP/Azure)', '#DC2626'),
]
for x, y, label, color in nodes:
    ax.plot(x, y, 'o', markersize=28, markerfacecolor=color, markeredgecolor='white', markeredgewidth=2, alpha=0.8)
    ax.text(x, y, label, ha='center', va='center', fontsize=6, fontweight='bold', color='white')

# Connection lines
edges = [((1, 3.0), (3, 2.2)), ((1, 1.5), (3, 2.2)), ((3, 2.2), (5, 3.0)), ((3, 2.2), (5, 1.5)),
         ((5, 3.0), (7, 2.2)), ((5, 1.5), (7, 2.2)), ((7, 2.2), (9, 2.2))]
for (x1, y1), (x2, y2) in edges:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.5, alpha=0.5))

ax.set_title('MLCC供应链全景：从原材料到云厂商', fontsize=13, fontweight='bold', color=DARK, loc='left')
plt.tight_layout(pad=1.5)
save_chart(fig, 'supply_chain.svg')

print(f'\nAll 7 static SVG charts generated in {CHART_DIR}')
