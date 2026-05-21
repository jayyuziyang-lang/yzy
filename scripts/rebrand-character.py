#!/usr/bin/env python3
"""
扬说财经 · 角色形象全面重建
根据用户提供的阿扬设计图，重制所有角色SVG
"""

import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from character_svg import generate_character_svg

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_full_avatar() -> str:
    """生成300x300圆形头像"""
    s = 1.0
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1A56DB"/>
      <stop offset="100%" style="stop-color:#1E3A7A"/>
    </linearGradient>
    <linearGradient id="shirt-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2A6BE0"/>
      <stop offset="100%" style="stop-color:#153E9E"/>
    </linearGradient>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#1E293B" flood-opacity="0.15"/>
    </filter>
  </defs>
  <circle cx="150" cy="150" r="150" fill="url(#bg)"/>
''' + generate_character_svg(150, 140, 1.0, 'character/ayang-portrait.jpg') + '''
  <rect x="50" y="265" width="200" height="26" rx="13" fill="rgba(255,255,255,0.12)"/>
  <text x="150" y="283" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="14" font-weight="bold" fill="white">扬说财经</text>
</svg>'''


def generate_header() -> str:
    """生成1080x405公众号头图"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 405">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1A56DB"/>
      <stop offset="50%" style="stop-color:#1E3A7A"/>
      <stop offset="100%" style="stop-color:#0F2557"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#D4A017"/>
      <stop offset="100%" style="stop-color:#B8860B"/>
    </linearGradient>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" flood-opacity="0.2"/>
    </filter>
  </defs>
  <rect width="1080" height="405" fill="url(#bg)"/>
  <g stroke="rgba(255,255,255,0.03)" stroke-width="1">
    <line x1="0" y1="100" x2="1080" y2="100"/>
    <line x1="0" y1="200" x2="1080" y2="200"/>
    <line x1="0" y1="300" x2="1080" y2="300"/>
    <line x1="270" y1="0" x2="270" y2="405"/>
    <line x1="540" y1="0" x2="540" y2="405"/>
    <line x1="810" y1="0" x2="810" y2="405"/>
  </g>
  <circle cx="900" cy="50" r="120" fill="rgba(255,255,255,0.03)"/>
  <circle cx="950" cy="30" r="80" fill="rgba(255,255,255,0.02)"/>
  <circle cx="200" cy="350" r="100" fill="rgba(255,255,255,0.02)"/>
  <text x="100" y="140" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="52" font-weight="bold" fill="white">扬说财经</text>
  <rect x="100" y="155" width="120" height="4" rx="2" fill="url(#gold)"/>
  <text x="100" y="195" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="22" fill="rgba(255,255,255,0.7)">用漫画看懂财经 — 你好，我是阿扬</text>
  <rect x="100" y="215" width="72" height="26" rx="13" fill="rgba(212,160,23,0.3)" stroke="#D4A017" stroke-width="1"/>
  <text x="136" y="232" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="12" fill="#D4A017">扬说·早报</text>
  <rect x="182" y="215" width="72" height="26" rx="13" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
  <text x="218" y="232" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="12" fill="rgba(255,255,255,0.8)">扬说·夜读</text>
''' + generate_character_svg(800, 210, 1.35, 'character/ayang-portrait.jpg') + '''
  <rect x="0" y="400" width="1080" height="5" fill="url(#gold)"/>
</svg>'''


def generate_cover_morning() -> str:
    """生成900x383早报封面"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 383">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1A56DB"/>
      <stop offset="100%" style="stop-color:#1E3A7A"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#D4A017"/>
      <stop offset="100%" style="stop-color:#B8860B"/>
    </linearGradient>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000" flood-opacity="0.2"/>
    </filter>
  </defs>
  <rect width="900" height="383" fill="url(#bg)"/>
  <circle cx="750" cy="50" r="150" fill="rgba(255,255,255,0.03)"/>
  <circle cx="50" cy="350" r="80" fill="rgba(255,255,255,0.02)"/>
  <text x="40" y="50" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="16" fill="rgba(255,255,255,0.6)">扬说财经 · 2026.05.21</text>
  <rect x="770" y="35" width="90" height="24" rx="12" fill="rgba(255,255,255,0.1)"/>
  <text x="815" y="51" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="11" fill="rgba(255,255,255,0.7)">扬说·早报</text>
  <text x="40" y="110" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="38" font-weight="bold" fill="white">一天狂赚6.4亿美元</text>
  <text x="40" y="160" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="32" font-weight="bold" fill="#D4A017">英伟达印钞机还在加速</text>
  <rect x="40" y="185" width="60" height="3" rx="1.5" fill="url(#gold)"/>
  <text x="40" y="218" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="17" fill="rgba(255,255,255,0.65)">Q1营收$816亿 +85% · 净利$583亿 +211%</text>
  <rect x="40" y="240" width="56" height="24" rx="12" fill="rgba(239,68,68,0.25)"/>
  <text x="68" y="256" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="11" fill="#EF4444">AI硬件</text>
  <rect x="104" y="240" width="56" height="24" rx="12" fill="rgba(16,185,129,0.25)"/>
  <text x="132" y="256" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="11" fill="#10B981">美股</text>
''' + generate_character_svg(780, 290, 0.9, 'character/ayang-portrait.jpg') + '''
  <rect x="0" y="378" width="900" height="5" fill="url(#gold)"/>
</svg>'''


def generate_cover_evening() -> str:
    """生成900x383晚报封面"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 383">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#D4A017"/>
      <stop offset="50%" style="stop-color:#B8860B"/>
      <stop offset="100%" style="stop-color:#8B6914"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FFF3D6"/>
      <stop offset="100%" style="stop-color:#FFE4A0"/>
    </linearGradient>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000" flood-opacity="0.2"/>
    </filter>
  </defs>
  <rect width="900" height="383" fill="url(#bg)"/>
  <circle cx="750" cy="50" r="150" fill="rgba(255,255,255,0.05)"/>
  <circle cx="50" cy="350" r="80" fill="rgba(255,255,255,0.03)"/>
  <text x="40" y="50" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="16" fill="rgba(255,255,255,0.6)">扬说财经 · 2026.05.21</text>
  <rect x="770" y="35" width="90" height="24" rx="12" fill="rgba(255,255,255,0.15)"/>
  <text x="815" y="51" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="11" fill="rgba(255,255,255,0.85)">扬说·夜读</text>
  <text x="40" y="110" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="38" font-weight="bold" fill="white">金价冲破4500美元</text>
  <text x="40" y="160" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="32" font-weight="bold" fill="#FFE4A0">央行连买18个月买金</text>
  <rect x="40" y="185" width="60" height="3" rx="1.5" fill="url(#gold)"/>
  <text x="40" y="218" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="17" fill="rgba(255,255,255,0.65)">COMEX $4,546/oz · 沪金 ¥999.70/克</text>
  <rect x="40" y="240" width="56" height="24" rx="12" fill="rgba(255,255,255,0.2)"/>
  <text x="68" y="256" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="11" fill="#FFE4A0">黄金</text>
  <rect x="104" y="240" width="56" height="24" rx="12" fill="rgba(255,255,255,0.15)"/>
  <text x="132" y="256" text-anchor="middle" font-family="'PingFang SC','Noto Sans SC',sans-serif" font-size="11" fill="rgba(255,255,255,0.85)">宏观</text>
''' + generate_character_svg(780, 290, 0.9, 'character/ayang-portrait.jpg') + '''
  <rect x="0" y="378" width="900" height="5" fill="url(#gold)"/>
</svg>'''


def generate_character_component(size: int = 100) -> str:
    """生成可复用角色组件"""
    s = size / 100
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
  <defs>
    <filter id="drop-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
    <linearGradient id="suit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2A6BE0"/>
      <stop offset="100%" stop-color="#153E9E"/>
    </linearGradient>
  </defs>
  <rect x="{-5*s}" y="{10*s}" width="{10*s}" height="{5*s}" opacity="0"/>  <!-- dummy to maintain size -->'''.replace('{-5*s}', f'{size*0.05:.0f}').replace('{10*s}', f'{size*0.1:.0f}').replace('{5*s}', f'{size*0.05:.0f}') + f'''
{generate_character_svg(size/2, size*0.52, size/80, '../assets/character/ayang-portrait.jpg')}
</svg>'''


# ================================================================
# 替换SVG文件中角色部分的函数
# ================================================================

def replace_character_in_svg(filepath: str, cx: float, cy: float, scale: float):
    """替换SVG文件中的角色定义"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Compute relative path to character image from SVG file location
    svg_dir = os.path.dirname(os.path.abspath(filepath))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    char_img = os.path.join('docs', 'assets', 'character', 'ayang-portrait.jpg')
    try:
        img_rel = os.path.relpath(os.path.join(root, char_img), svg_dir).replace('\\', '/')
    except ValueError:
        img_rel = char_img

    new_character = generate_character_svg(cx, cy, scale, img_rel)

    # 使用正则替换角色块
    # 匹配模式：一个g标签及其内部所有子g标签，这个g的transform匹配目标位置
    old_pattern = re.compile(
        r'<!--\s*阿扬角色\s*-->\s*<g[^>]*transform="[^"]*"[^>]*>[\s\S]*?</g>',
        re.MULTILINE
    )

    if old_pattern.search(content):
        content = old_pattern.sub(f'<!-- 阿扬角色 -->\n{new_character}', content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def replace_comic_character(svg_content: str) -> str:
    """替换漫画分镜中的角色——保留原始位置"""
    # 找到角色块并提取其transform位置
    char_patterns = [
        r'<!--[^>]*阿扬[^>]*-->\s*<g[^>]*transform="([^"]*)"[^>]*>[\s\S]*?</g>',
        r'<!--[^>]*角色[^>]*-->\s*<g[^>]*transform="([^"]*)"[^>]*>[\s\S]*?</g>',
        r'<g[^>]*transform="([^"]*)"[^>]*>\s*<!--[^>]*身体-蓝色外套[^>]*-->[\s\S]*?</g>',
    ]

    for pattern in char_patterns:
        match = re.search(pattern, svg_content)
        if match:
            transform = match.group(1)  # preserve original position like "150, 170" or "245, 138"
            comment_match = re.search(r'<!--[^>]*-->', match.group())
            comment = comment_match.group() if comment_match else '<!-- 阿扬角色 -->'

            # Parse transform to get cx, cy, and determine scale
            coords = re.findall(r'[\d.]+', transform)
            if len(coords) >= 2:
                cx, cy = float(coords[0]), float(coords[1])
            else:
                cx, cy = 150, 170

            # Determine scale based on position
            # Panel-000 type (right side, smaller): cx is ~245
            # Normal panels (bottom center): cx is ~150
            if cx > 200:
                scale = 0.65  # smaller for right-side character
            else:
                scale = 0.9  # normal size for bottom center

            new_char = generate_character_svg(cx, cy, scale,
                '../../../../docs/assets/character/ayang-portrait.jpg')
            replacement = f'{comment}\n{new_char}'
            return re.sub(pattern, replacement, svg_content)

    return svg_content


# ================================================================
# 批量更新函数
# ================================================================

def update_avatar():
    path = os.path.join(ROOT, 'docs', 'assets', 'avatar.svg')
    content = generate_full_avatar()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ avatar.svg ({os.path.getsize(path)/1024:.0f} KB)")


def update_header():
    path = os.path.join(ROOT, 'docs', 'assets', 'header.svg')
    content = generate_header()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ header.svg ({os.path.getsize(path)/1024:.0f} KB)")


def update_covers():
    for name, gen_fn in [('cover-morning.svg', generate_cover_morning),
                          ('cover-evening.svg', generate_cover_evening)]:
        path = os.path.join(ROOT, 'docs', 'assets', name)
        content = gen_fn()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {name} ({os.path.getsize(path)/1024:.0f} KB)")


def update_components():
    comp_dir = os.path.join(ROOT, 'docs', 'components')
    os.makedirs(comp_dir, exist_ok=True)
    for size, suffix in [(80, 'sm'), (120, 'md'), (160, 'lg')]:
        content = generate_character_component(size)
        path = os.path.join(comp_dir, f'character-{suffix}.svg')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ character-{suffix}.svg ({os.path.getsize(path)/1024:.0f} KB)")


def update_comic_panels():
    for edition in ['morning', 'evening']:
        comic_dir = os.path.join(ROOT, '2026-05-21', 'wechat-publish', edition, 'comic')
        if not os.path.isdir(comic_dir):
            continue
        files = sorted(f for f in os.listdir(comic_dir) if f.endswith('.svg'))
        for fname in files:
            path = os.path.join(comic_dir, fname)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = replace_comic_character(content)
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  ✅ {edition}/{fname}")
            else:
                # 直接替换整个文件中的旧角色定义
                # 找到旧的角色绘制代码块并替换
                print(f"  ⏭️  {edition}/{fname} (需要手动检查)")


# ================================================================
# Main
# ================================================================
if __name__ == '__main__':
    print("=" * 50)
    print("📡 扬说财经 · 角色形象全面重建")
    print(f"   基于用户设计图重制阿扬角色")
    print("=" * 50)

    print("\n📁 品牌资产:")
    update_avatar()
    update_header()
    update_covers()

    print("\n🎨 角色组件:")
    update_components()

    print("\n🖼️ 漫画分镜:")
    update_comic_panels()

    print("\n" + "=" * 50)
    print("✅ 角色重建完成！")
    print("=" * 50)
