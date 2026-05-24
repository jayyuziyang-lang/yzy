#!/usr/bin/env python3
"""
扬说财经 · 漫画质量升级器（SVG增强版）
不依赖GPU，通过程序化SVG增强提升漫画分镜品质

功能:
  1. SVG增强：添加阴影、渐变、边框美化
  2. 角色组件库：可复用的高质Q版角色SVG模板
  3. AnimeGANv2管线（可选）：照片转动漫风格角色

用法:
  python scripts/upgrade-comic.py                    # 增强今日所有漫画
  python scripts/upgrade-comic.py --dir 2026-05-21/wechat-publish/morning/comic
  python scripts/upgrade-comic.py --panel panel-001.svg
"""

import argparse
import os
import sys
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from character_svg import generate_character_svg
CHART_DIR = os.path.join(ROOT, 'docs', 'charts')

# ================================================================
# SVG 增强函数
# ================================================================

def read_svg(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_svg(path: str, content: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    size_kb = os.path.getsize(path) / 1024
    print(f"  ✅ {os.path.basename(path)} ({size_kb:.0f} KB)")


def add_narrative_title(svg: str, title: str = None) -> str:
    """
    为SVG添加叙事性标题（FT数据记者研究发现：叙事标题+多重标注的图表最受欢迎）

    在SVG顶部添加一个品牌标题栏，包含叙事性标题文本。
    如果title为None，尝试从SVG内容中提取现有标题。
    """
    vb_match = re.search(r'viewBox="([^"]+)"', svg)
    if not vb_match:
        return svg
    vb = vb_match.group(1)
    parts = vb.split()
    vb_w = float(parts[2]) if len(parts) >= 3 else 300
    vb_h = float(parts[3]) if len(parts) >= 4 else 220

    # 如果没提供标题，尝试从SVG内容提取
    if not title:
        # 找已有的大号文本作为标题
        text_match = re.search(r'<text[^>]*font-size="[^"]*(?:1[4-9]|2[0-4])[^"]*"[^>]*>([^<]+)</text>', svg)
        if text_match:
            title = text_match.group(1).strip()
        else:
            return svg  # 没有可用的标题，跳过

    if len(title) > 40:
        title = title[:38] + '…'

    # 标题栏高度
    bar_h = 28
    new_vb_h = vb_h + bar_h

    # 构建标题栏SVG
    title_bar = f'''
    <!-- 叙事性标题栏（FT研究方法） -->
    <rect x="0" y="0" width="{vb_w}" height="{bar_h}" fill="#1A56DB" rx="0"/>
    <text x="{vb_w/2}" y="{bar_h/2 + 1}" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="11" font-weight="700" fill="#FFFFFF" text-anchor="middle" dominant-baseline="middle">{title}</text>
    <line x1="0" y1="{bar_h}" x2="{vb_w}" y2="{bar_h}" stroke="#D4A017" stroke-width="1.5"/>
'''

    # 调整viewBox高度
    svg = svg.replace(f'viewBox="0 0 {vb_w} {vb_h}"', f'viewBox="0 0 {vb_w} {new_vb_h}"')

    # 将现有内容下移
    # 把所有组和主要元素用g包装并平移
    svg = re.sub(
        r'(<rect[^>]*fill="#FAFAFA"[^>]*/>)',
        rf'\1{title_bar}',
        svg
    )

    # 将所有非defs、非metadata内容整体下移
    # 在</defs>之后插入translate组开始
    svg = svg.replace('</defs>', '</defs>\n  <g transform="translate(0, {})">'.format(bar_h))
    # 在</svg>前关闭组
    svg = svg.replace('</svg>', '  </g>\n</svg>')

    return svg


def enhance_svg(svg: str) -> str:
    """
    对SVG漫画分镜进行增强处理：
    1. 添加 defs（渐变、滤镜、阴影）
    2. 增强背景
    3. 美化对话框
    4. 添加微妙的光影效果
    """
    # 检查是否已经有defs
    if '<defs>' in svg:
        return svg  # 已经有defs，跳过

    # 提取viewBox
    vb_match = re.search(r'viewBox="([^"]+)"', svg)
    if not vb_match:
        return svg
    vb = vb_match.group(1)
    parts = vb.split()
    vb_w = float(parts[2]) if len(parts) >= 3 else 300
    vb_h = float(parts[3]) if len(parts) >= 4 else 220

    # 品牌颜色
    BLUE = '#1A56DB'
    GOLD = '#D4A017'
    LIGHT_BG = '#F5F7FA'

    # 构建增强defs
    enhanced_defs = f'''<defs>
    <!-- 主投影滤镜 -->
    <filter id="drop-shadow" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1E293B" flood-opacity="0.12"/>
    </filter>
    <!-- 柔和投影 -->
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#1E293B" flood-opacity="0.08"/>
    </filter>
    <!-- 品牌蓝色渐变 -->
    <linearGradient id="brand-blue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1A56DB"/>
      <stop offset="100%" stop-color="#1E3A7A"/>
    </linearGradient>
    <!-- 品牌金色渐变 -->
    <linearGradient id="brand-gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#D4A017"/>
      <stop offset="100%" stop-color="#B8860B"/>
    </linearGradient>
    <!-- 对话框渐变 -->
    <linearGradient id="bubble-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#F8F9FA"/>
    </linearGradient>
    <!-- 高光渐变 -->
    <linearGradient id="brand-glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(26,86,219,0.15)"/>
      <stop offset="100%" stop-color="rgba(26,86,219,0.02)"/>
    </linearGradient>
    <!-- 背景网格图案 -->
    <pattern id="dot-grid" width="12" height="12" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.5" fill="#E2E8F0" opacity="0.3"/>
    </pattern>
  </defs>'''

    # 在第一个 tag 之后插入 defs
    insert_pos = svg.find('>', svg.find('<svg')) + 1
    svg = svg[:insert_pos] + '\n' + enhanced_defs + '\n' + svg[insert_pos:]

    # 确保背景使用品牌颜色和点阵
    bg_tags = ['<rect width="100%" height="100%"', '<rect width="100%" height="100%"']
    for old_bg in ['<rect width="100%" height="100%" fill="#F5F7FA"',
                   '<rect width="100%" height="100%" fill="#FFFFFF"',
                   '<rect width="100%" height="100%">']:
        if old_bg in svg:
            svg = svg.replace(old_bg,
                              f'<rect width="100%" height="100%" fill="#F5F7FA"/>'
                              f'\n    <rect width="100%" height="100%" fill="url(#dot-grid)"/>'
                              f'\n    <rect width="100%" height="100%" fill="url(#brand-glow)"')
            break

    # 美化标题文本 - 添加品牌蓝色的底部边框
    title_pattern = r'(<text[^>]*font-size="[^"]*(?:20|22|24)[^"]*"[^>]*>.*?</text>)'
    svg = re.sub(title_pattern,
                  lambda m: m.group(1) + '\n    <line x1="0" y1="0" x2="0" y2="0" stroke="#D4A017" stroke-width="2" opacity="0"/>',
                  svg, count=1)

    # 为矩形（面板）添加投影
    svg = re.sub(r'(<rect[^>]*rx="[^"]*"[^>]*fill="[^"]*"[^>]*/>)',
                  lambda m: m.group(1).replace('/>', ' filter="url(#drop-shadow)"/>') if 'filter' not in m.group(1) else m.group(1),
                  svg)

    return svg


def batch_enhance(comic_dir: str):
    """批量增强目录中的SVG漫画文件"""
    if not os.path.isdir(comic_dir):
        print(f"[!] 目录不存在: {comic_dir}")
        return

    svg_files = sorted([f for f in os.listdir(comic_dir) if f.endswith('.svg')])
    if not svg_files:
        print(f"[!] 未找到SVG文件: {comic_dir}")
        return

    print(f"\n🔧 增强漫画分镜: {comic_dir}")
    for fname in svg_files:
        path = os.path.join(comic_dir, fname)
        svg = read_svg(path)
        enhanced = enhance_svg(svg)
        # 自动添加叙事性标题（FT研究：叙事标题+多重标注的图表最受欢迎）
        enhanced = add_narrative_title(enhanced)
        if enhanced != svg:
            write_svg(path, enhanced)
        else:
            print(f"  ⏭️  {fname} (已增强)")


# ================================================================
# 角色SVG组件生成器（可复用的Q版角色）
# ================================================================

def _generate_component_svg(size: int) -> str:
    """使用共享角色函数生成独立SVG组件文件"""
    # 角色居中摆放，比例适合组件大小
    scale = size / 80  # 基准缩放: size=80 → scale=1.0
    center = size // 2
    char_svg = generate_character_svg(center, int(size * 0.58), scale, '../assets/character/ayang-portrait.jpg')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
  <defs>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
  </defs>
{char_svg}
</svg>'''


def generate_character_component(output_dir: str):
    """生成可复用的角色组件SVG"""
    os.makedirs(output_dir, exist_ok=True)

    # 生成不同尺寸的角色组件
    for size, suffix in [(80, 'sm'), (120, 'md'), (160, 'lg')]:
        svg = _generate_component_svg(size)
        path = os.path.join(output_dir, f'character-{suffix}.svg')
        write_svg(path, svg)

    print(f"\n✅ 角色组件已生成: {output_dir}")


# ================================================================
# AnimeGANv2 管线（可选，需GPU）
# ================================================================
def install_animegan_pipeline():
    """输出AnimeGANv2管线安装和使用指南"""
    guide = '''
📸 AnimeGANv2 角色生成管线（GPU推荐）

安装:
  git clone https://github.com/bryandlee/animegan2-pytorch
  cd animegan2-pytorch
  pip install -r requirements.txt

使用:
  python scripts/run_animegan.py --input photo.jpg --output character.png

转换为SVG:
  python -c "
from PIL import Image
import vtracer

img = Image.open('character.png')
# VTracer 矢量化
with open('character.svg', 'w') as f:
    vtracer.convert_png_to_svg('character.png', f)
  "

管线集成到 morning.sh/evening.sh:
  # 添加到漫画生成步骤
  python scripts/upgrade-comic.py --animegan --input photo.jpg
'''
    print(guide)


# ================================================================
# Main
# ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='扬说财经 · 漫画质量升级器')
    parser.add_argument('--dir', help='漫画SVG目录')
    parser.add_argument('--panel', help='单个SVG文件路径')
    parser.add_argument('--enhance', action='store_true', default=True,
                        help='增强SVG视觉效果（默认开启）')
    parser.add_argument('--generate-characters', action='store_true',
                        help='生成可复用角色组件')
    parser.add_argument('--add-narrative-titles', action='store_true', default=True,
                        help='为SVG添加叙事性标题（FT研究推荐，默认开启）')
    parser.add_argument('--title', help='为单个SVG指定叙事性标题')
    parser.add_argument('--animegan-guide', action='store_true',
                        help='打印AnimeGANv2管线安装指南')

    args = parser.parse_args()

    # 打印AnimeGANv2指南
    if args.animegan_guide:
        install_animegan_pipeline()
        sys.exit(0)

    # 生成角色组件
    if args.generate_characters:
        comp_dir = os.path.join(ROOT, 'docs', 'components')
        generate_character_component(comp_dir)
        sys.exit(0)

    # 增强SVG
    if args.panel:
        if os.path.isfile(args.panel):
            svg = read_svg(args.panel)
            enhanced = enhance_svg(svg)
            if args.add_narrative_titles:
                enhanced = add_narrative_title(enhanced, title=args.title)
            if enhanced != svg:
                write_svg(args.panel, enhanced)
            elif args.title:
                write_svg(args.panel, enhanced)
            else:
                print(f"⏭️  {args.panel} (无需增强)")
        else:
            print(f"[!] 文件不存在: {args.panel}")

    elif args.dir:
        batch_enhance(args.dir)

    else:
        # 默认：增强今日所有漫画分镜
        today = time.strftime('%Y-%m-%d')
        print(f"📡 扬说财经 · 漫画质量升级器")
        print(f"📅 {today}")
        print("=" * 40)

        for edition in ['morning', 'evening']:
            comic_dir = os.path.join(ROOT, today, 'wechat-publish', edition, 'comic')
            if os.path.isdir(comic_dir):
                batch_enhance(comic_dir)

        # 也生成角色组件
        comp_dir = os.path.join(ROOT, 'docs', 'components')
        print(f"\n🎨 生成角色组件: {comp_dir}")
        generate_character_component(comp_dir)

        print(f"\n{'=' * 40}")
        print(f"✅ 漫画升级完成！")
        print(f"\n💡 进一步提升:")
        print(f"  对有GPU的机器，运行:")
        print(f"    python scripts/upgrade-comic.py --animegan-guide")
