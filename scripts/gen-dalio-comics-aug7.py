#!/usr/bin/env python3
"""
扬说财经 · 2026-08-07 早报 Dalio 简笔科普漫画生成
遵循 DALIO_SVG_COMIC_STANDARD：
- 768x512, viewBox="0 0 768 512", 背景 #FAFBFC
- 品牌蓝 #1A56DB, 红涨 #DC2626, 绿跌 #16A34A
- font-family="Microsoft YaHei, SimHei, sans-serif"
- 具体物件隐喻, 3秒可懂, 简笔画小人, 文件<10KB
"""
import os
import xml.etree.ElementTree as ET

# ---- 颜色 ----
BG = '#FAFBFC'
BLUE = '#1A56DB'
DARK_BLUE = '#1E3A7A'
RED = '#DC2626'
GREEN = '#16A34A'
GRAY = '#64748B'
LIGHT_GRAY = '#94A3B8'
SLATE = '#475569'
GOLD = '#D4A017'
DARK_GREEN = '#14532D'
DARK_RED = '#991B1B'

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       '2026-08-07', 'wechat-publish', 'morning', 'comic')
os.makedirs(OUT_DIR, exist_ok=True)


def head(font='Microsoft YaHei, SimHei, sans-serif'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 512" width="768" height="512" font-family="{font}">'


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=0, opacity=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if opacity:
        s += f' opacity="{opacity}"'
    return s + '/>'


def text(x, y, txt, size, fill, weight=None, anchor='middle', opacity=None):
    s = f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}"'
    if weight:
        s += f' font-weight="{weight}"'
    if opacity:
        s += f' opacity="{opacity}"'
    return s + f'>{txt}</text>'


def line(x1, y1, x2, y2, stroke, w=2, cap='round'):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="{cap}"/>'


def circle(cx, cy, r, fill, stroke=None, sw=0):
    s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + '/>'


def polygon(points, fill, stroke=None, sw=0):
    s = f'<polygon points="{points}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + '/>'


def polyline(points, stroke, w=2):
    return f'<polyline points="{points}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'


def stick_figure(x, y, scale=1.0, arm='up', color=SLATE, skin=None):
    """简笔画小人: (x,y)=脚部中心。arm: up=举手 / mid=平举 / down=垂手"""
    r = 10 * scale
    body_top = y - 36 * scale
    shoulder = body_top + 10 * scale
    hip = y - 12 * scale
    el = []
    el.append(circle(x, body_top, r, color))  # 头
    el.append(line(x, shoulder, x, hip, color, w=3 * scale))  # 身体
    if arm == 'up':  # 右手向上举
        el.append(line(x, shoulder, x + 16 * scale, body_top - 6 * scale, color, w=3 * scale))
        el.append(line(x, shoulder, x - 12 * scale, shoulder + 4 * scale, color, w=3 * scale))
    elif arm == 'mid':  # 平举
        el.append(line(x, shoulder, x + 18 * scale, shoulder, color, w=3 * scale))
        el.append(line(x, shoulder, x - 18 * scale, shoulder, color, w=3 * scale))
    else:  # 垂手
        el.append(line(x, shoulder, x + 8 * scale, hip, color, w=3 * scale))
        el.append(line(x, shoulder, x - 8 * scale, hip, color, w=3 * scale))
    el.append(line(x, hip, x - 9 * scale, y, color, w=3 * scale))  # 左腿
    el.append(line(x, hip, x + 9 * scale, y, color, w=3 * scale))  # 右腿
    return '\n'.join(el)


def bubble(x, y, w, h, txt, fill='#FFFFFF', stroke=BLUE, txt_color=DARK_BLUE, size=13):
    """对话框: (x,y)=框左上角"""
    el = []
    el.append(rect(x, y, w, h, fill, rx=10, stroke=stroke, sw=1.5))
    # 尾巴三角
    el.append(polygon(f'{x+w//2-7},{y+h} {x+w//2+7},{y+h} {x+w//2},{y+h+12}', fill, stroke, 1.5))
    el.append(text(x + w // 2, y + h // 2 + 5, txt, size, txt_color, weight='700'))
    return '\n'.join(el)


# ============================================================
# Panel 001: 同一个引擎 — 天平隐喻
# 核心矛盾: 黄金涨6% vs 油价跌10%, 出自同一个引擎(宽松预期)
# ============================================================
def panel_001():
    el = []
    el.append(rect(0, 0, 768, 512, BG))

    # 标题条
    el.append(rect(24, 18, 720, 42, BLUE, rx=6, opacity=0.1))
    el.append(text(384, 46, '同一个引擎：ADP爆冷 + 谈判破冰 → 黄金涨、油价跌', 18, BLUE, weight='700'))
    el.append(text(384, 78, '黄金周涨6% vs 油价周跌10% —— 不是两件事，是同一件事', 12, GRAY))

    # ---- 天平（右高左低）----
    # 支点三角 + 底座
    el.append(polygon('384,430 344,392 424,392', SLATE))
    el.append(rect(356, 430, 56, 8, SLATE, rx=2))
    # 横梁: 左低右高
    el.append(line(150, 320, 618, 225, BLUE, w=9))
    # 悬挂绳
    el.append(line(150, 320, 180, 352, GRAY, w=2))
    el.append(line(618, 225, 588, 262, GRAY, w=2))
    # 左托盘（低位，油桶）
    el.append(rect(132, 352, 96, 20, '#E2E8F0', rx=6, stroke=GRAY, sw=1.5))
    # 油桶
    el.append(rect(146, 320, 36, 30, SLATE, rx=5))
    el.append(rect(140, 332, 48, 8, BLUE))
    el.append(line(164, 322, 164, 348, BG, w=2))
    el.append(text(180, 394, '油价 $79.08', 12, SLATE, weight='700'))
    el.append(text(180, 410, '地缘溢价消退 · 一周-10%', 10, GREEN, weight='700'))

    # 右托盘（高位，金砖）
    el.append(rect(544, 262, 88, 18, '#E2E8F0', rx=6, stroke=GRAY, sw=1.5))
    # 金砖
    el.append(rect(560, 240, 40, 20, GOLD, rx=4))
    el.append(rect(560, 240, 40, 8, '#F5D988', rx=4))
    el.append(text(588, 232, '黄金 $4,308', 12, '#B8860B', weight='700'))
    el.append(text(588, 210, '+4.2% · 七周新高', 11, RED, weight='700'))

    # 右侧两个推力砝码（向上箭头顶住右端）
    el.append(line(470, 320, 470, 285, RED, w=2))
    el.append(polygon('470,278 464,288 476,288', RED))
    el.append(rect(418, 322, 104, 40, '#EFF6FF', rx=8, stroke=BLUE, sw=1.5))
    el.append(text(470, 337, '小非农爆冷', 12, DARK_BLUE, weight='700'))
    el.append(text(470, 353, 'ADP仅 +4.4万', 10, GRAY))

    el.append(line(470, 408, 470, 368, RED, w=2))
    el.append(polygon('470,360 464,370 476,370', RED))
    el.append(rect(418, 410, 104, 40, '#F0FDF4', rx=8, stroke=GREEN, sw=1.5))
    el.append(text(470, 425, '谈判破冰', 12, DARK_GREEN, weight='700'))
    el.append(text(470, 441, '通胀担忧缓解', 10, GRAY))

    # 支点上的小人（裁判），举牌
    el.append(stick_figure(300, 396, scale=1.0, arm='up'))
    el.append(bubble(204, 322, 172, 44, '今夜非农\n= 最后一块砝码？', fill='#FFFFFF', stroke=BLUE, size=11))

    # 底部洞察条
    el.append(rect(24, 466, 720, 40, '#F0F4FF', rx=6, stroke=BLUE, sw=1.5))
    el.append(text(384, 491, '市场交易的是“宽松预期”，不是“通胀”——黄金是利率预期资产，不是避险资产', 13, DARK_BLUE, weight='700'))

    # 品牌线
    el.append(line(24, 506, 744, 506, BLUE, w=2, cap='round'))
    return head() + '\n' + '\n'.join(el) + '\n' + text(384, 510, '扬说财经早报 · 2026.08.07', 9, LIGHT_GRAY) + '\n</svg>'


# ============================================================
# Panel 002: AI"验真"时代 — 电子秤隐喻
# 核心矛盾: 市场只信业绩+确定性 → 英伟达+3% vs AMD-7%/AppLovin-19.7%
# ============================================================
def panel_002():
    el = []
    el.append(rect(0, 0, 768, 512, BG))

    # 标题条
    el.append(rect(24, 18, 720, 42, BLUE, rx=6, opacity=0.1))
    el.append(text(384, 46, 'AI进入“验真”时代：故事轻如纸，业绩重如铁', 18, BLUE, weight='700'))
    el.append(text(384, 78, '英伟达+3%逼近$5.8万亿 vs AMD-7%、AppLovin-19.7% —— 资金只奖确定性', 11, GRAY))

    # ---- 电子秤 ----
    # 秤盘支柱
    el.append(rect(380, 220, 8, 170, SLATE))
    el.append(rect(332, 390, 104, 10, SLATE, rx=3))  # 底座
    # 横杆
    el.append(line(170, 230, 598, 230, SLATE, w=8))
    # 左盘悬绳 + 左盘
    el.append(line(200, 230, 200, 258, GRAY, w=2))
    el.append(rect(152, 258, 96, 18, '#E2E8F0', rx=6, stroke=GRAY, sw=1.5))
    # 左盘上的"故事/PPT"轻纸盒（被弹起，虚线箭头向上）
    el.append(rect(172, 224, 40, 26, '#FFFFFF', rx=4, stroke=RED, sw=1.5))
    el.append(text(192, 242, '故事', 12, RED, weight='700'))
    el.append(polyline('192,222 192,196 216,180', RED, w=2))
    el.append(circle(220, 178, 3, RED))
    el.append(text(238, 200, '被弹飞', 10, RED, weight='700'))
    el.append(text(200, 300, '讲故事 → 出清', 11, DARK_RED, weight='700'))
    el.append(text(200, 316, 'AppLovin -19.7%', 10, GRAY))
    el.append(text(200, 332, 'AMD -7% · 西数 -13%', 10, GRAY))

    # 右盘悬绳 + 右盘
    el.append(line(568, 230, 568, 258, GRAY, w=2))
    el.append(rect(520, 258, 96, 18, '#E2E8F0', rx=6, stroke=GRAY, sw=1.5))
    # 右盘上的"业绩"重铁块（稳稳压住）
    el.append(rect(544, 200, 44, 40, BLUE, rx=4))
    el.append(text(566, 228, '业绩', 14, '#FFFFFF', weight='700'))
    el.append(text(568, 300, '有业绩 → 领跑', 11, DARK_GREEN, weight='700'))
    el.append(text(568, 316, '英伟达 +3%', 10, GREEN, weight='700'))
    el.append(text(568, 332, '美光 重返万亿', 10, GREEN))

    # 立柱上的裁判小人（举旗/举牌）
    el.append(stick_figure(296, 400, scale=0.95, arm='up'))
    el.append(bubble(288, 252, 144, 40, '财报说了算！', fill='#FFFFFF', stroke=BLUE, size=12))
    el.append(text(360, 382, '裁判：财报季', 10, GRAY))

    # 底部洞察条
    el.append(rect(24, 424, 720, 40, '#F0F4FF', rx=6, stroke=BLUE, sw=1.5))
    el.append(text(384, 449, '市场已经不信“故事”，只信“业绩+绑定确定性”——AI投资进入下半场', 13, DARK_BLUE, weight='700'))

    # 品牌线
    el.append(line(24, 476, 744, 476, BLUE, w=2, cap='round'))
    return head() + '\n' + '\n'.join(el) + '\n' + text(384, 480, '扬说财经早报 · 2026.08.07', 9, LIGHT_GRAY) + '\n</svg>'


def validate(svg_str, path):
    """SVG 6项自检: XML语法 / font-family / &转义 / 尺寸 / 颜色 / 文件大小"""
    checks = []
    try:
        ET.fromstring(svg_str)
        checks.append(('XML语法', True))
    except Exception as e:
        checks.append(('XML语法', False, str(e)))
    checks.append(('font-family', 'font-family="Microsoft YaHei, SimHei, sans-serif"' in svg_str))
    checks.append(('&转义', ' & ' not in svg_str.replace('&amp;', '')))
    checks.append(('尺寸', 'viewBox="0 0 768 512"' in svg_str and 'width="768"' in svg_str))
    checks.append(('颜色', BG in svg_str and '#DC2626' in svg_str and '#16A34A' in svg_str))
    size = len(svg_str.encode('utf-8'))
    checks.append(('大小', size < 10 * 1024, f'{size/1024:.1f}KB'))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg_str)
    ok = all(c[1] for c in checks)
    print(f"  {'PASS' if ok else 'FAIL'} {path}")
    for c in checks:
        tag = c[0]
        passed = c[1]
        extra = f' ({c[2]})' if len(c) > 2 else ''
        print(f"    [{chr(10004) if passed else chr(10007)}] {tag}{extra}")
    return ok


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print('=' * 50)
    print('扬说财经 · 2026-08-07 Dalio漫画生成')
    print('=' * 50)
    all_ok = True
    all_ok &= validate(panel_001(), os.path.join(OUT_DIR, 'panel-001.svg'))
    all_ok &= validate(panel_002(), os.path.join(OUT_DIR, 'panel-002.svg'))
    print('=' * 50)
    print('ALL PASS' if all_ok else 'HAS FAILURES')
