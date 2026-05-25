#!/usr/bin/env python3
"""
扬说财经 · xkcd 素描风格图表生成器
使用 chart.xkcd 库生成手绘/素描风格 SVG 图表
通过 Playwright (headless browser) 渲染并导出独立 SVG 文件

用法：
  python scripts/generate-xkcd-charts.py --chart line --data "[1,2,3,4,5]" --labels "['周一','周二','周三','周四','周五']" --title "本周走势"

图表类型：
  line   — 折线图（趋势展示）
  bar    — 柱状图（对比展示）
  pie    — 饼图（占比展示）
  radar  — 雷达图（多维度对比）

降级方案：
  如果 headless browser 不可用，输出 HTML 片段嵌入文章中。
"""

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, 'docs', 'charts')
TEMPLATE_PATH = os.path.join(ROOT, 'scripts', 'xkcd-charts-template.html')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 品牌色系
BLUE = '#1A56DB'
GOLD = '#D4A017'
RED = '#EF4444'
GREEN = '#10B981'
PURPLE = '#8B5CF6'
ORANGE = '#F59E0B'
GREY = '#CBD5E1'
STROKE = '#1E293B'
BG = '#FFFFFF'

# 中文字体栈
FONT = '"xkcd", "PingFang SC", "Microsoft YaHei", sans-serif'


def _parse_data(value):
    """解析命令行传入的数据参数（JSON 数组格式）"""
    if isinstance(value, list):
        return value
    return json.loads(value)


def _parse_labels(value):
    """解析命令行传入的标签参数"""
    if isinstance(value, list):
        return value
    return json.loads(value)


def _safe_name(text):
    """将标题转换为安全的文件名片段"""
    import re
    text = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:30]


def _build_config(chart_type, title, x_label, y_label, labels, data, datasets=None):
    """构建 chart.xkcd 配置对象"""
    config = {
        'title': title,
        'data': {
            'labels': labels,
            'datasets': datasets or [{'label': title, 'data': data}]
        },
        'options': {
            'dataColors': [BLUE, GOLD, RED, GREEN, PURPLE, ORANGE],
            'fontFamily': FONT,
            'strokeColor': STROKE,
            'backgroundColor': BG
        }
    }

    if chart_type in ('line', 'xy'):
        config['xLabel'] = x_label or ''
        config['yLabel'] = y_label or ''
    elif chart_type == 'bar':
        config['xLabel'] = x_label or ''
        config['yLabel'] = y_label or ''
    elif chart_type == 'pie':
        config['options']['innerRadius'] = 0.4
    elif chart_type == 'radar':
        config['options']['showLabels'] = True
        config['options']['ticksCount'] = 4

    return config


def generate_html_fragment(chart_type, title, config):
    """降级方案：输出 HTML 片段，可嵌入文章中"""
    chart_class_map = {
        'line': 'Line',
        'bar': 'Bar',
        'pie': 'Pie',
        'radar': 'Radar',
    }
    chart_class = chart_class_map.get(chart_type, 'Bar')
    config_json = json.dumps(config, ensure_ascii=False)

    import time
    chart_id = f"xkcd-{chart_type}-{int(time.time() * 1000)}"

    html = f'''<!-- xkcd 素描图表：{title} -->
<div class="xkcd-chart-wrapper" style="background:{BG};border-radius:10px;padding:10px;margin:14px 0;border:1px solid #E2E8F0;text-align:center;">
  <svg id="{chart_id}" style="width:100%;max-width:600px;height:auto;min-height:350px;"></svg>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.xkcd@1/dist/chart.xkcd.min.js"></script>
<script>
(function() {{
  var svg = document.getElementById('{chart_id}');
  if (svg && window.chartXkcd) {{
    new chartXkcd.{chart_class}(svg, {config_json});
  }}
}})();
</script>'''
    return html


def render_with_playwright(chart_type, title, x_label, y_label, labels, data, datasets=None):
    """使用 Playwright 渲染 xkcd 图表并导出 SVG 文件"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright 未安装。使用降级方案输出 HTML 片段。")
        return None

    config = _build_config(chart_type, title, x_label, y_label, labels, data, datasets)
    chart_class_map = {
        'line': 'Line',
        'bar': 'Bar',
        'pie': 'Pie',
        'radar': 'Radar',
    }
    chart_class = chart_class_map.get(chart_type, 'Bar')
    config_json = json.dumps(config, ensure_ascii=False)

    # 构建最小 HTML 页面用于渲染
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    background: {BG};
    width: 700px;
    margin: 0;
    padding: 10px;
  }}
  svg {{ display: block; }}
</style>
</head>
<body>
  <svg id="xkcd-target" width="680" height="420"></svg>
  <script src="https://cdn.jsdelivr.net/npm/chart.xkcd@1/dist/chart.xkcd.min.js"></script>
  <script>
    var svgEl = document.getElementById('xkcd-target');
    try {{
      new chartXkcd.{chart_class}(svgEl, {config_json});
    }} catch(e) {{
      document.body.setAttribute('data-error', e.message);
    }}
  </script>
</body>
</html>'''

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 720, 'height': 500})
        page.set_content(html_content, wait_until='networkidle')

        # 等待 SVG 渲染完成（chart.xkcd 动态添加子元素到 svg）
        try:
            page.wait_for_selector('#xkcd-target > *', timeout=10000)
        except Exception:
            pass

        # 检查是否有渲染错误
        error = page.evaluate("() => document.body.getAttribute('data-error')")
        if error:
            print(f"  警告：chart.xkcd 渲染可能出错: {error}")
            browser.close()
            return None

        # 提取 SVG outerHTML
        svg_html = page.evaluate('''() => {
          var svg = document.getElementById('xkcd-target');
          if (!svg) return null;
          // 确保 SVG 有正确的命名空间和 viewBox
          svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
          if (!svg.getAttribute('viewBox')) {
            var w = svg.getAttribute('width') || 680;
            var h = svg.getAttribute('height') || 420;
            svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
          }
          return svg.outerHTML;
        }''')

        browser.close()

        if not svg_html:
            print("  错误：无法提取 SVG 内容")
            return None

        return svg_html


def main():
    parser = argparse.ArgumentParser(
        description='扬说财经 · xkcd 素描风格图表生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  python scripts/generate-xkcd-charts.py --chart line --data "[1,2,3,4,5]" --labels "['周一','周二','周三','周四','周五']" --title "本周走势"
  python scripts/generate-xkcd-charts.py --chart bar --data "[287,96,78,-42,320]" --labels "['半导体','通信','计算机','白酒','银行']" --title "资金流向"
  python scripts/generate-xkcd-charts.py --chart pie --data "[324,90,72,60]" --labels "['中国','波兰','印度','土耳其']" --title "全球央行购金"
  python scripts/generate-xkcd-charts.py --chart radar --title "宏观评估" --labels "['GDP','CPI','PMI']" --data "[70,60,55]"
        '''
    )
    parser.add_argument('--chart', required=True, choices=['line', 'bar', 'pie', 'radar'],
                        help='图表类型')
    parser.add_argument('--title', required=True, help='图表标题')
    parser.add_argument('--data', required=True, help='数据数组 (JSON格式)，如 "[1,2,3,4,5]"')
    parser.add_argument('--labels', required=True, help='标签数组 (JSON格式)')
    parser.add_argument('--x-label', default='', help='X轴标签')
    parser.add_argument('--y-label', default='', help='Y轴标签')
    parser.add_argument('--output', default='', help='输出文件名 (不含扩展名)，默认自动生成')
    parser.add_argument('--fallback', action='store_true', help='强制使用降级方案 (输出HTML片段)')

    args = parser.parse_args()

    data = _parse_data(args.data)
    labels = _parse_labels(args.labels)

    # 自动生成输出文件名
    output_name = args.output or f"xkcd-{args.chart}-{_safe_name(args.title)}"
    svg_path = os.path.join(OUTPUT_DIR, f"{output_name}.svg")

    print(f"生成 xkcd 素描图表: {args.chart}")
    print(f"  标题: {args.title}")
    print(f"  数据: {data}")
    print(f"  标签: {labels}")

    svg_content = None

    if args.fallback:
        print("  使用降级方案...")
        config = _build_config(args.chart, args.title, args.x_label, args.y_label, labels, data)
        html_fragment = generate_html_fragment(args.chart, args.title, config)
        html_path = os.path.join(OUTPUT_DIR, f"{output_name}-embed.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_fragment)
        print(f"  HTML 片段已保存: {html_path}")
        print(f"  (降级方案: 嵌入文章时需要加载 chart.xkcd CDN)")
        return

    # 尝试 Playwright 渲染
    print("  使用 Playwright 渲染...")
    svg_content = render_with_playwright(args.chart, args.title, args.x_label, args.y_label,
                                         labels, data)

    if svg_content:
        # 包装成完整的 SVG 文件（添加 XML 声明和命名空间）
        full_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
{svg_content}'''

        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(full_svg)

        size = os.path.getsize(svg_path)
        print(f"  SVG 已保存: {svg_path} ({size / 1024:.1f} KB)")

        # 同时生成嵌入 HTML 片段
        config = _build_config(args.chart, args.title, args.x_label, args.y_label, labels, data)
        html_fragment = generate_html_fragment(args.chart, args.title, config)
        html_path = os.path.join(OUTPUT_DIR, f"{output_name}-embed.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_fragment)
        print(f"  嵌入片段已保存: {html_path}")
    else:
        # 降级方案
        print("  Playwright 渲染失败，使用降级方案...")
        config = _build_config(args.chart, args.title, args.x_label, args.y_label, labels, data)
        html_fragment = generate_html_fragment(args.chart, args.title, config)
        html_path = os.path.join(OUTPUT_DIR, f"{output_name}-embed.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_fragment)
        print(f"  HTML 片段已保存: {html_path}")
        print(f"  (降级方案: 嵌入文章时需要加载 chart.xkcd CDN)")


if __name__ == '__main__':
    main()
