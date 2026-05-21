#!/usr/bin/env python3
"""
扬说财经 · 人物图像嵌入工具
将漫画 SVG 中引用的外部人物照片嵌入为 base64 数据 URI。

问题背景：
- 漫画 SVG 通过 <image href="...ayang-portrait.jpg"> 引用人物照片
- 当 SVG 被 <img> 标签嵌入 HTML 时，浏览器禁止加载外部文件
- 导致人物照片无法显示，只渲染出几何体（蓝色身体）

解决方案：
- 将人物照片读取为 base64 数据 URI，直接嵌入 SVG
- 这样 SVG 成为自包含文件，<img> 标签也能正确渲染

用法:
  python scripts/embed-character.py                    # 嵌入今日所有漫画
  python scripts/embed-character.py --dir <path>       # 指定目录
"""

import argparse
import base64
import io
import os
import re
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR_PORTRAIT = os.path.join(ROOT, 'docs', 'assets', 'character', 'ayang-portrait.jpg')


def image_to_data_uri(image_path: str, max_width: int = 60) -> str:
    """
    将图片文件转为 base64 数据 URI，并缩放到指定宽度。
    SVG 漫画中人物图像渲染尺寸约 30x45px，这里缩放到 60px 宽以保证清晰度。
    """
    if not os.path.exists(image_path):
        print(f'[!] 人物图片不存在: {image_path}')
        return None

    img = Image.open(image_path)

    # 缩放图片
    w_percent = max_width / float(img.size[0])
    h_size = int(float(img.size[1]) * float(w_percent))
    img = img.resize((max_width, h_size), Image.LANCZOS)

    # 转为 JPEG base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)
    b64 = base64.b64encode(buffer.getvalue()).decode('ascii')

    return f'data:image/jpeg;base64,{b64}'


def embed_character_in_svg(svg_path: str, data_uri: str) -> bool:
    """
    替换 SVG 中的人物图片引用为 data URI。
    返回 True 表示有修改，False 表示无需修改。
    """
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 <image href="...ayang-portrait.jpg" ...>
    pattern = re.compile(
        r'(<image\s+href=")[^"]*(ayang-portrait\.jpg)[^"]*("[^>]*>)',
        re.IGNORECASE
    )

    if not pattern.search(content):
        # 检查是否已经是 data URI
        if 'data:image/jpeg;base64' in content and 'char-clip' in content:
            return False  # 已经嵌入过了
        # 尝试查找任何指向外部文件的 image 标签
        ext_pattern = re.compile(r'<image\s+href="[^"]+\.jpg"[^>]*>')
        if not ext_pattern.search(content):
            print(f'  [!] 未找到人物图片引用: {os.path.basename(svg_path)}')
            return False

    new_content = pattern.sub(
        lambda m: f'{m.group(1)}{data_uri}{m.group(3)}',
        content
    )

    if new_content != content:
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        size_kb = os.path.getsize(svg_path) / 1024
        print(f'  [OK] {os.path.basename(svg_path)} ({size_kb:.0f} KB)')
        return True
    else:
        print(f'  [--] {os.path.basename(svg_path)} (无变化)')
        return False


def process_directory(comic_dir: str, data_uri: str):
    """处理目录中所有 SVG 文件"""
    if not os.path.isdir(comic_dir):
        print(f'[!] 目录不存在: {comic_dir}')
        return

    svg_files = sorted(f for f in os.listdir(comic_dir) if f.endswith('.svg'))
    if not svg_files:
        print(f'[!] 未找到 SVG 文件: {comic_dir}')
        return

    print(f'\n📁 {comic_dir}')
    count = 0
    for fname in svg_files:
        path = os.path.join(comic_dir, fname)
        if embed_character_in_svg(path, data_uri):
            count += 1
    print(f'   修改了 {count}/{len(svg_files)} 个文件')


def main():
    parser = argparse.ArgumentParser(description='扬说财经 · 人物图像嵌入工具')
    parser.add_argument('--dir', help='SVG 目录路径')
    parser.add_argument('--portrait',
                        default=CHAR_PORTRAIT,
                        help='人物照片路径')
    args = parser.parse_args()

    print('=' * 50)
    print('  扬说财经 · 人物图像嵌入工具')
    print('  将人物照片嵌入 SVG 为 data URI')
    print('=' * 50)

    # 生成 data URI
    data_uri = image_to_data_uri(args.portrait)
    if not data_uri:
        print('[FAIL] 无法生成 data URI')
        sys.exit(1)
    print(f'\n📷 人物照片: {args.portrait}')
    print(f'📦 Data URI: {len(data_uri)} 字符')

    if args.dir:
        # 处理指定目录
        process_directory(args.dir, data_uri)
    else:
        # 处理今日所有漫画
        today = '2026-05-21'
        for edition in ['morning', 'evening']:
            comic_dir = os.path.join(ROOT, today, 'wechat-publish', edition, 'comic')
            process_directory(comic_dir, data_uri)

    print('\n' + '=' * 50)
    print('✅ 嵌入完成！')
    print('=' * 50)


if __name__ == '__main__':
    main()
