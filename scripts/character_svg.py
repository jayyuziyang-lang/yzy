#!/usr/bin/env python3
"""
扬说财经 · 共享角色模块（v6.0）
直接使用用户提供的真实人物图片，不做SVG绘画
"""

# 用户提供的真人写真照路径（统一在此定义，所有模块引用此变量）
# 实际使用时通过 img_rel 参数传入相对路径
CHAR_IMG_REL = '../assets/character/ayang-portrait.jpg'

def generate_character_svg(cx: float, cy: float, scale: float,
                           img_rel: str) -> str:
    """
    在(cx,cy)位置生成角色SVG组——直接嵌入真实人物图片
    img_rel: 从SVG文件到人物肖像的相对路径
    """
    s = scale
    return f'''<g transform="translate({cx:.0f}, {cy:.0f})">
  <!-- ===== 真实人物肖像 ===== -->
  <defs>
    <clipPath id="char-clip-{cx:.0f}-{cy:.0f}">
      <ellipse cx="0" cy="{-7*s}" rx="{16*s}" ry="{22*s}"/>
    </clipPath>
  </defs>
  <image href="{img_rel}" x="{-16*s}" y="{-30*s}" width="{32*s}" height="{48*s}"
         preserveAspectRatio="xMidYMin slice" clip-path="url(#char-clip-{cx:.0f}-{cy:.0f})"
         filter="url(#drop-shadow)"/>
  <!-- ===== 下半身简约处理 ===== -->
  <rect x="{-19*s}" y="{12*s}" width="{38*s}" height="{34*s}" rx="{11*s}" fill="#1A56DB" opacity="0.85" filter="url(#drop-shadow)"/>
  <polygon points="{-7*s},{12*s} 0,{-2*s} {7*s},{12*s}" fill="#FFFFFF" opacity="0.9"/>
  <polygon points="{-2.5*s},{8*s} 0,{0*s} {2.5*s},{8*s}" fill="#D4A017"/>
  <rect x="{-2*s}" y="{9*s}" width="{4*s}" height="{8*s}" rx="{1*s}" fill="#D4A017"/>
</g>'''

def character_image_tag(img_rel: str, width: int, height: int,
                        portrait: str = 'ayang-portrait.jpg') -> str:
    """生成可直接嵌入SVG的人物图片标签（用于cover/banner等大图）"""
    return f'<image href="{img_rel}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice"/>'
