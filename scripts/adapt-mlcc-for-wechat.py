#!/usr/bin/env python3
"""
MLCC产业链文章 → 微信兼容版本 专用适配器
=============================================
处理特殊问题：
  1. CSS 变量 (var(--primary) 等) → 解析为实际值
  2. iframe 交互图表 → <img> 引用已有 PNG
  3. <video> 元素 → 移除（保留说明文字）
  4. 导航栏/浮动目录/JS → 移除
  5. 输出为 publish-to-wechat.py 可处理的格式
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ARTICLE = PROJECT_ROOT / "ai-chain/mlcc-series/article.html"
CSS_FILE = PROJECT_ROOT / "ai-chain/mlcc-series/css/style.css"
CHARTS_DIR = PROJECT_ROOT / "ai-chain/mlcc-series/charts"
OUTPUT_DIR = PROJECT_ROOT / "ai-chain/mlcc-series"

# CSS 变量 → 实际值
CSS_VARS = {
    "--primary": "#1A56DB",
    "--primary-light": "#EFF6FF",
    "--primary-dark": "#1E40AF",
    "--accent-green": "#0F766E",
    "--accent-green-light": "#ECFDF5",
    "--accent-amber": "#D4A017",
    "--accent-amber-light": "#FFFBE6",
    "--bg": "#FFFFFF",
    "--bg-card": "#F8FAFC",
    "--text": "#1E293B",
    "--text-secondary": "#475569",
    "--text-muted": "#94A3B8",
    "--border": "#E2E8F0",
    "--border-light": "#F1F5F9",
    "--shadow-sm": "0 1px 2px rgba(0,0,0,0.04)",
    "--shadow": "0 4px 6px -1px rgba(0,0,0,0.06), 0 2px 4px -2px rgba(0,0,0,0.04)",
    "--shadow-md": "0 10px 15px -3px rgba(0,0,0,0.07), 0 4px 6px -4px rgba(0,0,0,0.04)",
    "--radius": "8px",
    "--radius-lg": "12px",
    "--max-width": "960px",
    "--nav-width": "200px",
    "--scroll-offset": "72px",
}

# iframe 图表 → PNG 静态图映射
IFRAME_TO_IMG = {
    "ai_position_sankey.html": "ai_position_sankey.png",
    "usage_per_device.html": "usage_per_device.png",
    "market_share.html": "market_share.png",
    "supply_chain_d3.html": "supply_chain.png",
    "market_size.html": "market_size.png",
    "price_cycle.html": "price_cycle.png",
    "tech_evolution.html": "tech_evolution.png",
}


def resolve_css_vars(css_content: str) -> str:
    """将 CSS 中的 var(--xxx) 替换为实际值"""
    for var_name, value in CSS_VARS.items():
        css_content = css_content.replace(f"var({var_name})", value)
    return css_content


def convert_iframe_to_img(html: str) -> str:
    """将 <iframe> 图表替换为 <img> 静态图"""
    def replace_iframe(match):
        iframe_tag = match.group(0)
        # 提取 src 中的文件名
        src_match = re.search(r'src="[^"]*?([^/"]+\.html)"', iframe_tag)
        if not src_match:
            return match.group(0)

        html_file = src_match.group(1)
        if html_file not in IFRAME_TO_IMG:
            return match.group(0)

        img_file = IFRAME_TO_IMG[html_file]
        # 提取 title/alt
        title_match = re.search(r'title="([^"]+)"', iframe_tag)
        alt_text = title_match.group(1) if title_match else "图表"

        return f'<img src="charts/{img_file}" alt="{alt_text}" style="width:100%;height:auto;display:block;" loading="lazy">'

    # 匹配 iframe 及其周围的 chart-container div
    # 方案：替换 iframe 标签本身，保留外层容器
    html = re.sub(
        r'<iframe[^>]*src="[^"]*\.html"[^>]*>.*?</iframe>',
        replace_iframe,
        html,
        flags=re.DOTALL,
    )
    return html


def remove_unsupported_elements(html: str) -> str:
    """移除微信不支持的元素"""
    removals = [
        # 导航栏
        (r'<nav[^>]*class="[^"]*top-nav[^"]*"[^>]*>.*?</nav>', ""),
        # 侧边目录
        (r'<aside[^>]*class="[^"]*side-toc[^"]*"[^>]*>.*?</aside>', ""),
        # 回到顶部按钮
        (r'<button[^>]*id="back-to-top"[^>]*>.*?</button>', ""),
        # JavaScript
        (r'<script[^>]*src="[^"]*"[^>]*>.*?</script>', ""),
        # video 容器（保留说明文字）
        (r'<div[^>]*class="[^"]*video-container[^"]*"[^>]*>.*?</div>\s*<p[^>]*class="chart-caption"[^>]*>.*?</p>', ""),
    ]
    for pattern, replacement in removals:
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    # 单独处理 video 标签
    html = re.sub(r'<video[^>]*>.*?</video>', '', html, flags=re.DOTALL)

    return html


def main():
    print("=" * 60)
    print("  MLCC产业链文章 → 微信兼容版本")
    print("=" * 60)

    # 读取原始文章
    print("\n1. 读取原始文章和 CSS...")
    html = SRC_ARTICLE.read_text(encoding="utf-8")
    css = CSS_FILE.read_text(encoding="utf-8")

    # 解析 CSS 变量
    print("2. 解析 CSS 变量...")
    css = resolve_css_vars(css)
    # 也解析 HTML 中的内联 var()
    for var_name, value in CSS_VARS.items():
        html = html.replace(f"var({var_name})", value)

    # 替换 <link> 为内联 <style>
    print("3. 内联 CSS...")
    html = html.replace(
        '<link rel="stylesheet" href="css/style.css">',
        f"<style>\n{css}\n</style>"
    )

    # 替换 iframe 图表为 img
    print("4. 替换 iframe 图表为静态图片...")
    html = convert_iframe_to_img(html)

    # 移除不支持的导航/JS/video
    print("5. 移除微信不支持的元素...")
    html = remove_unsupported_elements(html)

    # 清理空白残留
    html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)

    # 保存
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "article-wechat.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"\n  已保存: {output_path}")

    # 统计
    img_count = len(re.findall(r'<img[^>]+src="([^"]+)"', html))
    iframe_count = len(re.findall(r'<iframe', html))
    video_count = len(re.findall(r'<video', html))
    print(f"\n  图片: {img_count} 张")
    print(f"  残留 iframe: {iframe_count} 个")
    print(f"  残留 video: {video_count} 个")

    print("\n" + "=" * 60)
    print("  下一步:")
    print(f"  python scripts/publish-to-wechat.py --path {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
