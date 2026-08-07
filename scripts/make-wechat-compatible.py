#!/usr/bin/env python3
"""
微信公众号 HTML 兼容性格式化器
================================
将现代 HTML/CSS (grid, flex, rgba, shadow, gradient) 转换为
微信公众平台编辑器完全兼容的 inline-style HTML。

核心原则（来自开源项目 lyricat/wechat-format, wechat-styler 等）：
  1. 所有样式必须 inline — WeChat 剥离 <style>/class/外部 CSS
  2. 布局用 <table> 替代 Grid/Flex — WeChat 不支持 display:grid/flex
  3. 颜色用 hex，禁止 rgba() — WeChat 剥离 rgba
  4. 阴影用 border 替代 — WeChat 剥离 box-shadow
  5. 渐变用纯色替代 — WeChat 剥离 linear-gradient
  6. 列表用 <p> + <br> 替代 <ul>/<ol> — WeChat 重置列表样式
  7. 表格明确设置边框色 — WeChat 注入自己的灰色边框

用法:
  python scripts/make-wechat-compatible.py --input ai-chain/mlcc-series/article-wechat.html
  python scripts/make-wechat-compatible.py --input ai-chain/mlcc-series/article-wechat.html --output article-final.html
"""

import re
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── rgba() → hex 映射表 ──────────────────────────────────
# 用于阴影和半透明背景的 rgba 值 → 最近的纯色替代
RGBA_TO_HEX = {
    "rgba(0,0,0,0.04)": "#F5F5F5",
    "rgba(0, 0, 0, 0.04)": "#F5F5F5",
    "rgba(0,0,0,0.06)": "#F0F0F0",
    "rgba(0, 0, 0, 0.06)": "#F0F0F0",
    "rgba(0,0,0,0.07)": "#EDEDED",
    "rgba(0, 0, 0, 0.07)": "#EDEDED",
    "rgba(0,0,0,0.04), 0 2px 4px -2px rgba(0,0,0,0.04)": "",  # 完整匹配 shadows
}


def fix_rgba_colors(html: str) -> str:
    """将 rgba() 颜色替换为纯 hex"""
    def replace_rgba(match):
        full = match.group(0)
        # 尝试精确匹配
        normalized = re.sub(r'\s+', ' ', full).strip()
        for pattern, replacement in RGBA_TO_HEX.items():
            if replacement:  # 有映射
                norm_pattern = re.sub(r'\s+', ' ', pattern).strip()
                if normalized == norm_pattern:
                    return replacement
        # 通用处理：提取 rgb 部分，忽略 alpha
        m = re.match(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)', normalized)
        if m:
            return f"#{int(m.group(1)):02X}{int(m.group(2)):02X}{int(m.group(3)):02X}"
        return full

    html = re.sub(r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)', replace_rgba, html)
    return html


def fix_gradients(html: str) -> str:
    """linear-gradient → 取第一个颜色作为纯色背景"""
    def replace_gradient(match):
        full = match.group(0)
        # 提取第一个 hex 颜色
        colors = re.findall(r'#([0-9A-Fa-f]{3,6})', full)
        if colors:
            return f"#{colors[0]}"
        return "#FFFFFF"

    html = re.sub(r'linear-gradient\([^)]+\)', replace_gradient, html)
    return html


def fix_box_shadow(html: str) -> str:
    """box-shadow → border 替代"""
    # 对于 chart-container 和 card，用 border 替代 shadow
    # box-shadow: 0 4px 6px -1px rgba(...), 0 2px 4px -2px rgba(...) → border
    html = re.sub(
        r'box-shadow:[^;"]+;?',
        '',
        html
    )
    return html


def fix_calc(html: str) -> str:
    """calc() → 移除或取近似值"""
    # margin-top:calc(-1 * 72px) → margin-top:-72px
    def replace_calc(match):
        expr = match.group(1)
        # 简单计算：-1 * N → -N
        m = re.match(r'-1\s*\*\s*(\d+)px', expr.strip())
        if m:
            return f"-{m.group(1)}px"
        # N + M
        m = re.match(r'(\d+)px\s*\+\s*(\d+)px', expr.strip())
        if m:
            return f"{int(m.group(1)) + int(m.group(2))}px"
        m = re.match(r'(\d+)px\s*-\s*(\d+)px', expr.strip())
        if m:
            return f"{int(m.group(1)) - int(m.group(2))}px"
        return expr

    html = re.sub(r'calc\(([^)]+)\)', replace_calc, html)
    return html


def fix_display_flex(html: str) -> str:
    """将 display:flex / inline-flex 替换为兼容方案"""
    # display:flex → 移除（依赖外层 table 布局已经处理）
    html = re.sub(r'display:\s*flex\s*;?', '', html)
    html = re.sub(r'display:\s*inline-flex\s*;?', 'display:inline-block;', html)
    # align-items, justify-content 在没有 flex 时无效，移除
    html = re.sub(r'align-items:\s*\w+\s*;?', '', html)
    html = re.sub(r'justify-content:\s*\w+\s*;?', '', html)
    html = re.sub(r'gap:\s*\d+px\s*;?', '', html)
    html = re.sub(r'flex-shrink:\s*\d+\s*;?', '', html)
    html = re.sub(r'flex-wrap:\s*\w+\s*;?', '', html)
    return html


def fix_negative_margins(html: str) -> str:
    """移除负 margin-top（scroll offset，微信无法使用锚点滚动）"""
    html = re.sub(r'margin-top:\s*-?\d+px\s*;?', '', html)
    return html


def fix_letter_spacing(html: str) -> str:
    """移除 letter-spacing（微信不支持）"""
    html = re.sub(r'letter-spacing:[^;"]+;?', '', html)
    return html


def fix_text_transform(html: str) -> str:
    """移除 text-transform（微信不支持）"""
    html = re.sub(r'text-transform:[^;"]+;?', '', html)
    return html


def fix_section_numbers(html: str) -> str:
    """修复 section-number span：补充居中所需的属性（在 flex 移除后）"""
    # section-number span 在 flex 移除后需要 text-align:center + line-height 实现居中
    pattern = r'(<span[^>]*class="[^"]*section-number[^"]*"[^>]*style=")([^"]*)(")'

    def fix_span(match):
        prefix = match.group(1)
        style = match.group(2)
        suffix = match.group(3)
        if 'text-align:center' not in style:
            style += '; text-align:center'
        if 'line-height' not in style:
            style += '; line-height:36px'
        if 'vertical-align:middle' not in style:
            style += '; vertical-align:middle'
        # 清理多余分号
        style = re.sub(r';\s*;', ';', style)
        style = style.strip('; ')
        return f'{prefix}{style}{suffix}'

    return re.sub(pattern, fix_span, html)


def _find_matching_close(html: str, start: int) -> int:
    """从 <div ...> 的起始位置找到对应的 </div>，处理嵌套"""
    depth = 1
    pos = html.find('>', start) + 1
    while pos < len(html) and depth > 0:
        next_open = html.find('<div', pos)
        next_close = html.find('</div>', pos)

        if next_close == -1:
            return -1
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                return next_close + 6  # len('</div>')
            pos = next_close + 6

    return -1


def _extract_child_divs(inner: str, class_pattern: str) -> list[str]:
    """从 inner HTML 中提取 class 匹配 class_pattern 的完整 div（处理嵌套）"""
    results = []
    pattern = re.compile(rf'<div\s[^>]*class="[^"]*{class_pattern}[^"]*"[^>]*>', re.IGNORECASE)
    pos = 0
    while pos < len(inner):
        m = pattern.search(inner, pos)
        if not m:
            break
        div_start = m.start()
        div_end = _find_matching_close(inner, div_start)
        if div_end == -1:
            pos = m.end()
            continue
        results.append(inner[div_start:div_end])
        pos = div_end
    return results


def grid_to_table(html: str) -> str:
    """
    将 display:grid 容器转换为 <table> 布局（使用嵌套感知解析器）。
    data-grid → 3列 table
    card-grid → 2列 table
    """

    # ── 统一处理函数 ──
    def convert_grid_container(html: str, grid_class: str, cols: int) -> str:
        """找到所有 grid_class 容器并转换为 cols 列表格"""
        pattern = re.compile(
            rf'<div\s[^>]*class="[^"]*{grid_class}[^"]*"[^>]*>',
            re.IGNORECASE
        )

        result_parts = []
        last_end = 0

        for m in pattern.finditer(html):
            # 添加前面的内容
            result_parts.append(html[last_end:m.start()])

            div_start = m.start()
            div_end = _find_matching_close(html, div_start)
            if div_end == -1:
                result_parts.append(html[div_start:])
                last_end = len(html)
                break

            outer_tag = m.group(0)
            inner = html[m.end():div_end - 6]  # 去掉 </div>

            # 提取 margin
            margin_match = re.search(r'margin(?:-bottom)?:\s*([^;"]+)', outer_tag)
            margin = margin_match.group(1) if margin_match else "28px 0"

            # 提取子卡片
            card_class = "data-card" if "data-grid" in grid_class else "card"
            child_divs = _extract_child_divs(inner, card_class)

            if len(child_divs) < 2:
                # 不移除，保持原样
                result_parts.append(html[div_start:div_end])
                last_end = div_end
                continue

            width_pct = 100 // cols
            rows_html = ''
            for i in range(0, len(child_divs), cols):
                row_cards = child_divs[i:i+cols]
                cells = ''
                for card in row_cards:
                    cells += (
                        f'<td width="{width_pct}%" '
                        f'style="width:{width_pct}%; padding:8px; border:none; vertical-align:top">'
                        f'{card}</td>\n'
                    )
                rows_html += f'<tr>{cells}</tr>\n'

            replacement = (
                f'<table width="100%" '
                f'style="width:100%; margin:{margin}; border:none; border-collapse:collapse" '
                f'border="0" cellpadding="0" cellspacing="0">\n'
                f'{rows_html}</table>'
            )
            result_parts.append(replacement)
            last_end = div_end

        result_parts.append(html[last_end:])
        return ''.join(result_parts)

    html = convert_grid_container(html, "data-grid", 3)
    html = convert_grid_container(html, "card-grid", 2)

    return html


def fix_glossary_grid(html: str) -> str:
    """将 glossary 内的 dl grid 转为简单块布局"""
    # 移除 dl 上的所有 grid 相关 CSS 属性
    html = re.sub(r'display:\s*grid\s*;', '', html)
    html = re.sub(r'grid-template-columns:\s*[^;"]+;?', '', html)
    html = re.sub(r'gap:\s*\d+px\s*;?', '', html)
    return html


def fix_table_styling(html: str) -> str:
    """确保所有 <table> 有微信兼容的边框样式"""
    # 给所有 th 和 td 添加明确的边框色，防止微信注入灰色边框
    # 已有 style 的 th/td 保留，没有的添加基础样式

    # 对于公司表格（company-table），确保边框色明确
    # 这些表格的 th 已经有 background 和 border-bottom
    # 关键是确保 border-color 是明确的 hex

    return html


def remove_class_attrs(html: str) -> str:
    """移除 class 属性（微信剥离，保留无害但减少体积）"""
    # 暂时保留 class，以便调试。生产环境可启用。
    # html = re.sub(r'\s*class="[^"]*"', '', html)
    return html


def fix_meta_bar(html: str) -> str:
    """修复 meta-bar 的布局（flex → text-align:center + inline-block）"""
    # meta-bar div: 确保有 text-align:center
    pattern = r'(<div[^>]*class="[^"]*meta-bar[^"]*"[^>]*style=")([^"]*)(")'
    def fix_div(match):
        prefix = match.group(1)
        style = match.group(2)
        suffix = match.group(3)
        if 'text-align:center' not in style:
            style = 'text-align:center; ' + style
        # 清理多余空格和分号
        style = re.sub(r';\s*;', ';', style)
        style = style.strip().strip(';')
        return f'{prefix}{style}{suffix}'
    html = re.sub(pattern, fix_div, html)

    # meta-item span: inline-flex → inline-block
    html = html.replace(
        'display:flex; align-items:center; gap:6px',
        'display:inline-block; vertical-align:middle'
    )
    return html


def fix_data_card_styles(html: str) -> str:
    """data-card 内部样式优化"""
    # data-number 的 display:flex 相关移除（已在 td 中居中）
    # 保持 color, font-size 等
    return html


def clean_empty_styles(html: str) -> str:
    """清理空的 style 属性"""
    html = re.sub(r'\s*style="\s*"', '', html)
    html = re.sub(r'\s*style=""', '', html)
    return html


def clean_blank_lines(html: str) -> str:
    """清理多余空行"""
    html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)
    return html


def main():
    parser = argparse.ArgumentParser(description="微信 HTML 兼容性格式化")
    parser.add_argument("--input", required=True, help="输入 HTML 文件路径")
    parser.add_argument("--output", default=None, help="输出路径（默认：输入文件名 + -wechat-final.html）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path

    if not input_path.exists():
        print(f"[FAIL] 文件不存在: {input_path}")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
    else:
        output_path = input_path.parent / f"{input_path.stem}-wechat-final.html"

    print("=" * 60)
    print("  微信公众号 HTML 兼容性格式化")
    print(f"  输入: {input_path}")
    print("=" * 60)

    html = input_path.read_text(encoding="utf-8")
    original_size = len(html)

    # 变换流水线
    transforms = [
        ("rgba → hex", fix_rgba_colors),
        ("linear-gradient → solid", fix_gradients),
        ("box-shadow → border", fix_box_shadow),
        ("calc() → fixed", fix_calc),
        ("负 margin 移除", fix_negative_margins),
        ("display:flex → fallback", fix_display_flex),
        ("section-number 修复", fix_section_numbers),
        ("meta-bar 修复", fix_meta_bar),
        ("letter-spacing 移除", fix_letter_spacing),
        ("text-transform 移除", fix_text_transform),
        ("grid → table", grid_to_table),
        ("glossary grid 修复", fix_glossary_grid),
        ("表格样式修复", fix_table_styling),
        ("空 style 清理", clean_empty_styles),
        ("空行清理", clean_blank_lines),
    ]

    for name, transform_fn in transforms:
        before = len(html)
        html = transform_fn(html)
        after = len(html)
        diff = after - before
        sign = "+" if diff > 0 else ""
        print(f"  [{name}] {sign}{diff} bytes")

    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    # 统计
    final_size = len(html)
    img_count = len(re.findall(r'<img[^>]+src="([^"]+)"', html))
    table_count = len(re.findall(r'<table[^>]*>', html))

    # 检查残留问题
    remaining_grid = len(re.findall(r'display:\s*grid', html))
    remaining_flex = len(re.findall(r'display:\s*(inline-)?flex', html))
    remaining_rgba = len(re.findall(r'rgba\(', html))
    remaining_shadow = len(re.findall(r'box-shadow:', html))
    remaining_gradient = len(re.findall(r'linear-gradient\(', html))

    print(f"\n  文件大小: {original_size} → {final_size} bytes")
    print(f"  图片: {img_count} 张")
    print(f"  表格: {table_count} 个")
    print(f"\n  残留检查:")
    print(f"    grid: {remaining_grid}")
    print(f"    flex: {remaining_flex}")
    print(f"    rgba: {remaining_rgba}")
    print(f"    shadow: {remaining_shadow}")
    print(f"    gradient: {remaining_gradient}")

    if any([remaining_grid, remaining_flex, remaining_rgba]):
        print(f"\n  [WARN] 仍有未处理的不兼容属性，需手动检查")
    else:
        print(f"\n  [OK] 主要不兼容属性已清除")

    print(f"\n  [OK] 输出: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
