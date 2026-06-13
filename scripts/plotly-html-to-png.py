"""
从 Plotly HTML 文件中提取图表数据，使用 kaleido 渲染为静态 PNG。
用于解决 Plotly CDN 被墙 + 自托管 JS 在 GitHub Pages 上 404 的问题。
"""
import json
import re
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CHARTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ai-chain', 'mlcc-series', 'charts')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'ai-chain', 'mlcc-series', 'charts')

CHART_FILES = [
    ('ai_position_sankey.html', 'ai_position_sankey.png', 1200, 700),
    ('usage_per_device.html', 'usage_per_device.png', 800, 500),
    ('market_share.html', 'market_share.png', 1000, 600),
    ('supply_chain_d3.html', None, None, None),  # D3.js - special handling
    ('market_size.html', 'market_size.png', 900, 550),
    ('price_cycle.html', 'price_cycle.png', 900, 600),
    ('tech_evolution.html', 'tech_evolution.png', 1000, 650),
]

def extract_figure_from_html(filepath):
    """从 Plotly HTML 文件中提取 traces 和 layout 数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 找到 Plotly.newPlot( 调用
    match = re.search(r'Plotly\.newPlot\s*\(\s*"[^"]*"\s*,\s*(\[.*?\])\s*,\s*(\{.*\})\s*,\s*(\{.*\})\s*\)', html, re.DOTALL)
    if not match:
        # 尝试单引号版本
        match = re.search(r"Plotly\.newPlot\s*\(\s*'[^']*'\s*,\s*(\[.*?\])\s*,\s*(\{.*\})\s*,\s*(\{.*\})\s*\)", html, re.DOTALL)

    if not match:
        print(f"  FAIL: 未能从 {os.path.basename(filepath)} 中提取 Plotly 数据")
        return None, None

    traces_str = match.group(1)
    layout_str = match.group(2)

    try:
        traces = json.loads(traces_str)
        layout = json.loads(layout_str)
        return traces, layout
    except json.JSONDecodeError as e:
        print(f"  FAIL: JSON parse error: {e}")
        print(f"  trying repair...")
        # 尝试修复常见 JSON 问题
        for s in [traces_str, layout_str]:
            s = s.replace("'", '"')
            s = re.sub(r'(\w+):', r'"\1":', s)
        try:
            traces = json.loads(traces_str)
            layout = json.loads(layout_str)
            return traces, layout
        except:
            return None, None

def render_static(traces, layout, output_path, width=1000, height=600):
    """使用 plotly + kaleido 渲染静态图片"""
    fig = go.Figure(data=traces, layout=layout)

    try:
        fig.write_image(output_path, width=width, height=height, scale=2)
        size_kb = os.path.getsize(output_path) / 1024
        print(f"  OK {os.path.basename(output_path)} ({size_kb:.0f} KB)")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

def main():
    print("=" * 60)
    print("  Plotly HTML → 静态 PNG 渲染")
    print("=" * 60)

    for html_file, png_file, width, height in CHART_FILES:
        if png_file is None:
            print(f"\n⏭️  {html_file} (D3.js, 跳过)")
            continue

        html_path = os.path.join(CHARTS_DIR, html_file)
        png_path = os.path.join(OUTPUT_DIR, png_file)

        if not os.path.exists(html_path):
            print(f"\n❌ {html_file} 不存在")
            continue

        print(f"\n>>> {html_file} -> {png_file}")
        traces, layout = extract_figure_from_html(html_path)

        if traces is None:
            continue

        render_static(traces, layout, png_path, width, height)

    print("\n" + "=" * 60)
    print("  完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
