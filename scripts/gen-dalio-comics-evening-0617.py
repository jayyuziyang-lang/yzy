"""
6.17 晚报 Dalio SVG 漫画 v2.0 — 金色系
对标 DALIO_SVG_COMIC_STANDARD.md v2.0
6张漫画: 1张Layer1全景 + 5张Layer2故事
"""
import math, os, xml.etree.ElementTree as ET

OUT = "D:/Desktop/每日财经/2026-06-17/wechat-publish/evening/comic"
os.makedirs(OUT, exist_ok=True)

W, H = 768, 512
GOLD = "#D4A017"
GOLD_DARK = "#B8860B"
GOLD_LIGHT = "#F59E0B"

def svg_header():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Microsoft YaHei, SimHei, PingFang SC, sans-serif">\n  <rect width="{W}" height="{H}" fill="#FAFBFC"/>\n'

ARROW_DEFS = '''  <defs>
    <marker id="agold" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#D4A017"/></marker>
    <marker id="ar" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#DC2626"/></marker>
    <marker id="ag" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#16A34A"/></marker>
    <marker id="apurple" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#7C3AED"/></marker>
  </defs>\n'''

def svg_footer():
    return '</svg>'

def geo_person(x, y, h=44, color=GOLD, role="stand"):
    parts = []
    head_r, body_top_w, body_bot_w = 10, 16, 20
    body_h = h * 0.45
    cx = x
    head_cy = y - body_h - head_r + 2
    parts.append(f'<circle cx="{cx}" cy="{head_cy}" r="{head_r}" fill="#E2E8F0" stroke="{color}" stroke-width="2"/>')
    bx, by = cx - body_top_w, head_cy + head_r
    bw_top, bw_bot = body_top_w * 2, body_bot_w * 2
    parts.append(f'<polygon points="{cx-bw_top/2},{by} {cx+bw_top/2},{by} {cx+bw_bot/2},{by+body_h} {cx-bw_bot/2},{by+body_h}" fill="#FFF8E7" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>')
    leg_y = by + body_h
    leg_len = h * 0.35
    parts.append(f'<line x1="{cx-7}" y1="{leg_y}" x2="{cx-9}" y2="{leg_y+leg_len}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
    parts.append(f'<line x1="{cx+7}" y1="{leg_y}" x2="{cx+9}" y2="{leg_y+leg_len}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
    arm_y = by + body_h * 0.25
    if role == "arms_up":
        parts.append(f'<line x1="{cx-bw_top/2}" y1="{arm_y}" x2="{cx-bw_top/2-16}" y2="{arm_y-22}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx+bw_top/2}" y1="{arm_y}" x2="{cx+bw_top/2+16}" y2="{arm_y-22}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
    elif role == "look_up":
        parts.append(f'<line x1="{cx-bw_top/2}" y1="{arm_y}" x2="{cx-bw_top/2-10}" y2="{arm_y+8}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx+bw_top/2}" y1="{arm_y}" x2="{cx+bw_top/2+10}" y2="{arm_y+8}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
    elif role == "point":
        parts.append(f'<line x1="{cx-bw_top/2}" y1="{arm_y}" x2="{cx-bw_top/2-10}" y2="{arm_y+6}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx+bw_top/2}" y1="{arm_y}" x2="{cx+bw_top/2+22}" y2="{arm_y-10}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
    elif role == "carry":
        parts.append(f'<line x1="{cx-bw_top/2}" y1="{arm_y}" x2="{cx-bw_top/2-8}" y2="{arm_y-10}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx+bw_top/2}" y1="{arm_y}" x2="{cx+bw_top/2+8}" y2="{arm_y-10}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
    else:
        parts.append(f'<line x1="{cx-bw_top/2}" y1="{arm_y}" x2="{cx-bw_top/2-10}" y2="{arm_y+12}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx+bw_top/2}" y1="{arm_y}" x2="{cx+bw_top/2+10}" y2="{arm_y+12}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
    return '\n  '.join(parts)

def label(x, y, text, size=13, color="#334155", anchor="middle", bold=False, bg=None):
    out = ''
    if bg:
        tw = len(text) * size * 0.65
        out += f'<rect x="{x-tw/2-4}" y="{y-size+2}" width="{tw+8}" height="{size+4}" rx="3" fill="{bg}" opacity="0.85"/>\n  '
    w = "bold" if bold else "normal"
    out += f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{w}">{text}</text>'
    return out

def title_bar(text, color=GOLD):
    return (f'<rect x="0" y="0" width="{W}" height="44" fill="{color}" opacity="0.08"/>\n'
            f'  <text x="{W/2}" y="30" font-size="18" fill="{color}" text-anchor="middle" font-weight="bold">{text}</text>')

def footnote(text, y=500):
    return f'<text x="{W/2}" y="{y}" font-size="11" fill="#94A3B8" text-anchor="middle">{text}</text>'

def dashed_line(x1, y1, x2, y2, color="#CBD5E1"):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,4"/>'

def arrow(x1, y1, x2, y2, color=GOLD, marker="agold", sw=2.5):
    mid = f' marker-end="url(#{marker})"' if marker else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{mid}/>'

def clock_face(cx, cy, r, hour_angle=0):
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="#475569" stroke-width="2.5"/>',
             f'<circle cx="{cx}" cy="{cy}" r="3" fill="#475569"/>']
    for i in range(12):
        a = -math.pi/2 + i * math.pi/6
        ix, iy = cx + (r-6)*math.cos(a), cy + (r-6)*math.sin(a)
        ox, oy = cx + (r-2)*math.cos(a), cy + (r-2)*math.sin(a)
        parts.append(f'<line x1="{ix}" y1="{iy}" x2="{ox}" y2="{oy}" stroke="#475569" stroke-width="1.5"/>')
    ha = -math.pi/2 + hour_angle * math.pi/180
    hx, hy = cx + r*0.55*math.cos(ha), cy + r*0.55*math.sin(ha)
    parts.append(f'<line x1="{cx}" y1="{cy}" x2="{hx}" y2="{hy}" stroke="#D4A017" stroke-width="2.5" stroke-linecap="round"/>')
    return '\n  '.join(parts)

def gear(cx, cy, r, color=GOLD, teeth=8):
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="3"/>',
             f'<circle cx="{cx}" cy="{cy}" r="{r*0.55}" fill="none" stroke="{color}" stroke-width="1.5"/>',
             f'<circle cx="{cx}" cy="{cy}" r="{r*0.2}" fill="{color}"/>']
    for i in range(teeth):
        angle = 2 * math.pi * i / teeth
        tx, ty = cx + r * math.cos(angle), cy + r * math.sin(angle)
        parts.append(f'<rect x="{tx-3}" y="{ty-3}" width="6" height="6" rx="1" fill="{color}" transform="rotate({angle*180/math.pi},{tx},{ty})"/>')
    return '\n  '.join(parts)

def knob(cx, cy, r, angle=0, color=GOLD):
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="{color}" stroke-width="2.5"/>']
    for i in range(8):
        a = -math.pi*0.6 + i * math.pi*1.2/7
        ix, iy = cx + (r-4)*math.cos(a), cy + (r-4)*math.sin(a)
        ox, oy = cx + (r+3)*math.cos(a), cy + (r+3)*math.sin(a)
        parts.append(f'<line x1="{ix}" y1="{iy}" x2="{ox}" y2="{oy}" stroke="{color}" stroke-width="1"/>')
    pa = -math.pi*0.6 + angle * math.pi*1.2/100
    px, py = cx + (r-8)*math.cos(pa), cy + (r-8)*math.sin(pa)
    parts.append(f'<line x1="{cx}" y1="{cy}" x2="{px}" y2="{py}" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#DC2626"/>')
    return '\n  '.join(parts)

def pool(x, y, w, h, fill_level, color, label_text="", sub_text=""):
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="white" stroke="{color}" stroke-width="2.5"/>']
    water_h = h * fill_level / 100
    water_y = y + h - water_h
    parts.append(f'<rect x="{x+3}" y="{water_y}" width="{w-6}" height="{water_h}" rx="3" fill="{color}" opacity="0.2"/>')
    parts.append(f'<path d="M{x+3},{water_y+4} Q{x+w/2},{water_y-8} {x+w-3},{water_y+4}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6"/>')
    if label_text:
        parts.append(f'<text x="{x+w/2}" y="{y-12}" font-size="13" fill="{color}" text-anchor="middle" font-weight="bold">{label_text}</text>')
    if sub_text:
        parts.append(f'<text x="{x+w/2}" y="{y+h/2+5}" font-size="22" fill="{color}" text-anchor="middle" font-weight="800">{sub_text}</text>')
    return '\n  '.join(parts)

def scale(cx, cy, tilt_deg=0, l_text="", r_text="", l_color="#DC2626", r_color="#16A34A"):
    """天平——多空/利弊平衡"""
    rad = tilt_deg * math.pi / 180
    bw = 200
    parts = []
    # 底座
    parts.append(f'<rect x="{cx-12}" y="{cy+30}" width="24" height="30" rx="3" fill="#F1F5F9" stroke="#475569" stroke-width="2"/>')
    parts.append(f'<rect x="{cx-30}" y="{cy+52}" width="60" height="8" rx="3" fill="#E2E8F0" stroke="#475569" stroke-width="1.5"/>')
    # 支柱
    parts.append(f'<line x1="{cx}" y1="{cy+30}" x2="{cx}" y2="{cy-40}" stroke="#475569" stroke-width="2.5"/>')
    # 横梁
    lx = cx - bw/2 * math.cos(rad)
    ly = cy - 40 - bw/2 * math.sin(rad)
    rx = cx + bw/2 * math.cos(rad)
    ry = cy - 40 + bw/2 * math.sin(rad)
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="#475569" stroke-width="3" stroke-linecap="round"/>')
    # 左托盘
    parts.append(f'<ellipse cx="{lx}" cy="{ly+18}" rx="45" ry="12" fill="{l_color}" opacity="0.15" stroke="{l_color}" stroke-width="1.5"/>')
    # 右托盘
    parts.append(f'<ellipse cx="{rx}" cy="{ry+18}" rx="45" ry="12" fill="{r_color}" opacity="0.15" stroke="{r_color}" stroke-width="1.5"/>')
    # 连接线
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx}" y2="{ly+12}" stroke="#475569" stroke-width="1.5"/>')
    parts.append(f'<line x1="{rx}" y1="{ry}" x2="{rx}" y2="{ry+12}" stroke="#475569" stroke-width="1.5"/>')
    if l_text:
        parts.append(f'<text x="{lx}" y="{ly+38}" font-size="10" fill="{l_color}" text-anchor="middle" font-weight="bold">{l_text}</text>')
    if r_text:
        parts.append(f'<text x="{rx}" y="{ry+38}" font-size="10" fill="{r_color}" text-anchor="middle" font-weight="bold">{r_text}</text>')
    return '\n  '.join(parts)


# ============================================================
# 6张漫画
# ============================================================

def comic_001_summary():
    """Layer 1 全景: 指数繁荣·半导体独秀·FOMC倒计时"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("6.17 晚报速览：科创50暴涨·一九分化·全球等FOMC", GOLD)

    # 左侧——科创50火箭冲天
    rkt_cx, rkt_top = 160, 100
    # 火箭身体
    svg += f'<ellipse cx="{rkt_cx}" cy="230" rx="28" ry="85" fill="#FFF8E7" stroke="#DC2626" stroke-width="3"/>'
    svg += f'<polygon points="{rkt_cx-28},140 {rkt_cx},95 {rkt_cx+28},140" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.5" stroke-linejoin="round"/>'
    # 火焰
    svg += f'<polygon points="{rkt_cx-16},310 {rkt_cx},345 {rkt_cx+16},310" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>'
    svg += f'<polygon points="{rkt_cx-10},325 {rkt_cx},350 {rkt_cx+10},325" fill="#DC2626" opacity="0.6"/>'
    svg += label(rkt_cx, 365, "科创50 +4.69%", 14, "#DC2626", "middle", True)
    svg += label(rkt_cx, 383, "半导体净流入154亿", 10, "#991B1B")

    # 右侧——下沉的小船(3700个股)
    for i, (sx, sy) in enumerate([(560, 280), (610, 295), (520, 305), (590, 320), (550, 340), (630, 315)]):
        svg += f'<path d="M{sx-14},{sy} Q{sx-6},{sy-10} {sx},{sy-10} Q{sx+6},{sy-10} {sx+14},{sy} Z" fill="#F1F5F9" stroke="#16A34A" stroke-width="1.5"/>'
    svg += label(570, 370, "3734只个股下跌", 13, "#16A34A", "middle", True)
    svg += label(570, 388, "中位数 -1.19%", 11, "#64748B")

    # 中间——天平(一九分化)
    svg += scale(384, 420, -8, "指数↑", "个股↓", "#DC2626", "#16A34A")
    svg += label(384, 350, "一九分化", 14, "#DC2626", "middle", True)

    # 左上——FOMC时钟
    svg += clock_face(384, 120, 26, 315)
    svg += label(430, 118, "FOMC倒计时", 13, GOLD, "start", True)
    svg += label(430, 138, "凌晨2:00 沃什首秀", 10, "#64748B", "start")

    # 底部传导链
    chain_y = 460
    for gx, gc, gn in [(60, "#D4A017", "陆家嘴论坛"), (190, GOLD, "硬科技政策"), (330, "#DC2626", "半导体涨停"), (470, "#16A34A", "3700股下跌"), (610, GOLD, "FOMC")]:
        svg += gear(gx, chain_y, 11, gc, 6)
        svg += label(gx, chain_y+22, gn, 9, gc)
    svg += footnote("指数上涨但亏钱效应显著——这不是全面牛市，是极致抱团", 498)

    svg += svg_footer()
    return svg


def comic_002_ashare():
    """01 A股: 一九分化——半导体火箭冲天 vs 个股小船沉没"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("A股：科创50暴涨4.69% vs 3700只个股下跌", GOLD)

    # 中央裂谷
    svg += f'<path d="M200,80 Q384,150 568,80" fill="none" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="6,4"/>'

    # 左侧——半导体火箭区
    svg += f'<rect x="30" y="95" width="310" height="100" rx="10" fill="#FFF8E7" stroke="#D4A017" stroke-width="2"/>'
    svg += label(185, 125, "半导体板块", 14, GOLD, "middle", True)
    # 火箭
    svg += f'<ellipse cx="100" cy="170" rx="22" ry="65" fill="#FEF3C7" stroke="#DC2626" stroke-width="2.5"/>'
    svg += f'<polygon points="78,115 100,75 122,115" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>'
    svg += f'<polygon points="85,230 100,260 115,230" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>'
    svg += label(100, 275, "+6.91%", 14, "#DC2626", "middle", True)

    # 涨停标的
    stocks = [("盛美上海 20CM", 240, 155), ("普冉股份 20CM", 240, 173), ("兆易创新 涨停", 240, 191)]
    for nm, sx, sy in stocks:
        svg += label(sx, sy, nm, 10, "#DC2626")

    # 右侧——下沉个股
    svg += f'<rect x="430" y="95" width="310" height="100" rx="10" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>'
    svg += label(585, 125, "白酒/汽车/煤炭/商贸", 13, "#16A34A", "middle", True)

    for i, (sx, sy) in enumerate([(480, 160), (520, 175), (560, 165), (600, 180), (530, 195), (570, 200), (490, 190)]):
        svg += f'<path d="M{sx-10},{sy} Q{sx-4},{sy-8} {sx},{sy-8} Q{sx+4},{sy-8} {sx+10},{sy} Z" fill="#F1F5F9" stroke="#16A34A" stroke-width="1.5"/>'

    svg += label(585, 225, "资金净流出", 11, "#16A34A", "middle", True)
    svg += label(585, 243, "3734只个股下跌 中位数-1.19%", 11, "#64748B")

    # 中间裂谷标注
    svg += label(384, 75, "一九分化裂谷", 12, "#DC2626", "middle", True)
    svg += arrow(250, 65, 384, 65, "#DC2626", "ar", 2)
    svg += arrow(518, 65, 384, 65, "#16A34A", "ag", 2)

    # 底部——政策牌
    svg += f'<rect x="80" y="310" width="610" height="80" rx="10" fill="#FFF8E7" stroke="#D4A017" stroke-width="2"/>'
    svg += label(384, 338, "陆家嘴论坛 政策催化剂", 14, GOLD_DARK, "middle", True)
    svg += label(200, 362, "科创板第五套标准", 11, "#92400E")
    svg += label(200, 380, "扩至AI大模型", 11, "#92400E")
    svg += label(400, 362, "央行中长期资金", 11, "#92400E")
    svg += label(400, 380, "非银流动性工具", 11, "#92400E")
    svg += label(560, 362, '"硬科技"成', 11, "#92400E")
    svg += label(560, 380, "政策意志", 11, "#92400E")
    svg += arrow(384, 310, 384, 200, GOLD, "agold", 2)

    # 小人——左边半导体区举手，右边观望
    svg += geo_person(140, 270, 30, "#DC2626", "arms_up")
    svg += geo_person(610, 280, 30, "#16A34A", "stand")

    svg += footnote("一九分化≠健康牛市。上涨广度越窄，抱团松动时回调越剧烈", 498)
    svg += svg_footer()
    return svg


def comic_003_spacex():
    """03 科技: SpaceX一枝独秀 vs 科技股下沉 + 科创板制度红利"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("科技：SpaceX火箭一枝独秀·A股硬科技制度红利", GOLD)

    # 地面线
    svg += f'<line x1="30" y1="380" x2="738" y2="380" stroke="#CBD5E1" stroke-width="2"/>'

    # SpaceX火箭(中央冲天)
    svg += f'<ellipse cx="384" cy="230" rx="35" ry="95" fill="#FFF8E7" stroke="#DC2626" stroke-width="3"/>'
    svg += f'<polygon points="349,145 384,85 419,145" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.5" stroke-linejoin="round"/>'
    svg += f'<polygon points="358,320 384,370 410,320" fill="#FEE2E2" stroke="#DC2626" stroke-width="2"/>'
    svg += f'<polygon points="364,340 384,380 404,340" fill="#DC2626" opacity="0.5"/>'
    svg += label(384, 395, "SpaceX $2.66万亿", 13, "#DC2626", "middle", True)
    svg += label(384, 413, "四日累涨+50%·超越亚马逊", 10, "#991B1B")

    # 估值皮筋
    svg += f'<path d="M384,85 Q200,40 150,200" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="8,4"/>'
    svg += label(220, 60, "估值皮筋：暴涨后与基本面距离", 10, "#F59E0B")
    svg += label(220, 76, "合理区间 vs 当前市值", 10, "#D4A017")

    # 周围下沉科技股
    sinking = [("费半-5.7%", 120, 375, "#DC2626"), ("英伟达-2%", 230, 375, "#DC2626"),
               ("Meta-2.8%", 540, 375, "#DC2626"), ("AMD-7.3%", 650, 375, "#DC2626")]
    for txt, sx, sy, sc in sinking:
        svg += f'<ellipse cx="{sx}" cy="{sy}" rx="42" ry="14" fill="#FEF2F2" stroke="{sc}" stroke-width="1.5"/>'
        svg += label(sx, sy+2, txt, 10, sc)

    # 底部——科创板制度红利
    svg += f'<rect x="80" y="430" width="610" height="65" rx="8" fill="#FFF8E7" stroke="#D4A017" stroke-width="2" stroke-dasharray="6,3"/>'
    svg += label(384, 455, "科创板第五套标准扩至AI大模型", 13, GOLD_DARK, "middle", True)
    svg += label(250, 480, '"卖铲子给淘金者"', 12, "#B8860B", "middle", True)
    svg += label(500, 480, "硬科技=制度红利+政策意志", 12, "#B8860B", "middle", True)

    svg += geo_person(100, 348, 28, "#7C3AED", "look_up")
    svg += geo_person(660, 348, 28, "#7C3AED", "look_up")

    svg += footnote("一边是SpaceX估值皮筋越拉越紧，一边是A股硬科技制度红利刚刚开始", 502)
    svg += svg_footer()
    return svg


def comic_004_fomc():
    """05 宏观: FOMC三岔路——鸽/鹰/中性 + 沃什首秀时钟"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("FOMC：沃什首秀·三岔路口·全球屏息等待", GOLD)

    # 美联储大楼(中央)
    svg += f'<rect x="334" y="100" width="100" height="110" rx="4" fill="#FFF8E7" stroke="#D4A017" stroke-width="2.5"/>'
    svg += f'<rect x="354" y="120" width="60" height="20" rx="2" fill="#FEF3C7" stroke="#D4A017" stroke-width="1"/>'
    svg += label(384, 134, "FOMC", 12, GOLD_DARK, "middle", True)
    svg += f'<rect x="354" y="148" width="25" height="18" rx="1" fill="#FFF8E7" stroke="#D4A017" stroke-width="1"/>'
    svg += f'<rect x="384" y="148" width="25" height="18" rx="1" fill="#FFF8E7" stroke="#D4A017" stroke-width="1"/>'
    svg += f'<rect x="354" y="172" width="25" height="18" rx="1" fill="#FFF8E7" stroke="#D4A017" stroke-width="1"/>'
    svg += f'<rect x="384" y="172" width="25" height="18" rx="1" fill="#FFF8E7" stroke="#D4A017" stroke-width="1"/>'
    # 门
    svg += f'<rect x="369" y="190" width="30" height="20" rx="3" fill="#F1F5F9" stroke="#D4A017" stroke-width="1.5"/>'

    # 时钟(右上)
    svg += clock_face(480, 130, 30, 315)
    svg += label(530, 128, "北京时间", 11, "#475569", "start", True)
    svg += label(530, 146, "凌晨2:00", 11, "#DC2626", "start", True)

    # 三岔路——从大楼出发分三条
    split_x, split_y = 384, 230
    svg += f'<circle cx="{split_x}" cy="{split_y}" r="6" fill="#D4A017"/>'

    # 路径A——向上/左：鸽派
    svg += arrow(split_x, split_y, 170, 310, "#16A34A", "ag", 3)
    svg += f'<rect x="80" y="290" width="180" height="75" rx="10" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>'
    svg += label(170, 318, "🕊️ 鸽派", 15, "#16A34A", "middle", True)
    svg += label(170, 338, "沃什留白+宽松保留", 11, "#166534")
    svg += label(170, 355, "→ 美元弱·A股高开", 11, "#166534")

    # 路径B——向下：鹰派
    svg += arrow(split_x, split_y, 384, 440, "#DC2626", "ar", 3)
    svg += f'<rect x="294" y="430" width="180" height="65" rx="10" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>'
    svg += label(384, 458, "🦅 鹰派", 15, "#DC2626", "middle", True)
    svg += label(384, 478, "删除宽松倾向·暗示加息", 11, "#991B1B")
    svg += label(384, 493, "→ A股低开·半导体回吐", 10, "#991B1B")

    # 路径C——向右：中性
    svg += arrow(split_x, split_y, 610, 310, GOLD, "agold", 3)
    svg += f'<rect x="520" y="290" width="180" height="75" rx="10" fill="#FFF8E7" stroke="#D4A017" stroke-width="2"/>'
    svg += label(610, 318, "⚖️ 中性", 15, GOLD_DARK, "middle", True)
    svg += label(610, 338, "措辞微调方向不明", 11, "#92400E")
    svg += label(610, 355, "→ 窄幅震荡·等催化剂", 11, "#92400E")

    # 沃什小人(站大楼前)
    svg += geo_person(384, 230, 36, GOLD, "point")

    # 点阵图标注
    svg += f'<rect x="75" y="140" width="155" height="60" rx="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.5"/>'
    svg += label(152, 160, "三大悬念", 12, "#475569", "middle", True)
    svg += label(152, 178, "点阵图·留白·声明措辞", 10, "#64748B")

    svg += footnote("今晚最佳策略不是预测结果——而是准备好应对三种结果", 502)
    svg += svg_footer()
    return svg


def comic_005_commodity():
    """06 商品: 油价瀑布下跌 vs 黄金横盘等FOMC"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("商品：油价三日暴跌·黄金横盘等FOMC选方向", GOLD)

    # 左侧——油价瀑布
    svg += f'<rect x="30" y="70" width="340" height="220" rx="10" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>'
    svg += label(200, 98, "WTI原油 三日暴跌", 14, "#EA580C", "middle", True)

    # 油价阶梯下跌
    levels = [(200, 130, "$81+", "#EA580C"), (200, 170, "$77", "#EA580C"), (200, 210, "$74.80", "#DC2626")]
    prev_x, prev_y = 200, 115
    for cx, cy, txt, clr in levels:
        svg += f'<circle cx="{cx}" cy="{cy}" r="8" fill="white" stroke="{clr}" stroke-width="2.5"/>'
        svg += label(cx, cy+24, txt, 12, clr, "middle", True)
    # 下跌箭头
    for i in range(3):
        svg += arrow(170 + i*10, 145 + i*38, 170 + i*10, 160 + i*38, "#EA580C", "ar", 2)
    # 下跌百分比
    svg += label(200, 255, "从$95跌超20%·技术性熊市", 12, "#DC2626", "middle", True)
    svg += label(200, 275, "美伊协议挤出战争溢价", 10, "#991B1B")

    # 下跌油桶
    svg += f'<ellipse cx="130" cy="265" rx="22" ry="14" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>'
    svg += f'<rect x="108" y="242" width="44" height="23" rx="3" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>'
    svg += label(130, 255, "油", 14, "#EA580C", "middle", True)

    # 右侧——黄金横盘
    svg += f'<rect x="400" y="70" width="340" height="180" rx="10" fill="#FFFBEB" stroke="#D4A017" stroke-width="2"/>'
    svg += label(570, 98, "现货黄金 横盘等待", 14, GOLD, "middle", True)

    # 黄金平台线
    svg += f'<line x1="420" y1="160" x2="720" y2="160" stroke="#D4A017" stroke-width="3" stroke-dasharray="2,0"/>'
    svg += label(440, 148, "$4,320", 16, GOLD_DARK, "start", True)

    # 三力拉扯标注
    forces = [("\u6cb9\u4ef7\u66b4\u8dcc\u2193", "#EA580C", 440, 195), ("DXY&lt;100\u2191", "#16A34A", 530, 195), ("FOMC?", GOLD, 620, 195)]
    for txt, clr, fx, fy in forces:
        svg += label(fx, fy, txt, 10, clr)

    # 黄金小人
    svg += geo_person(570, 185, 30, GOLD, "stand")
    svg += label(570, 220, "三重均衡", 10, "#B8860B")

    # 底部——FOMC时钟决定方向
    svg += f'<rect x="120" y="330" width="530" height="70" rx="10" fill="#FFF8E7" stroke="#D4A017" stroke-width="2"/>'
    svg += clock_face(180, 365, 24, 315)
    svg += label(260, 360, "FOMC后方向选择", 15, GOLD_DARK, "start", True)
    svg += arrow(430, 350, 430, 330, "#16A34A", "ag", 2)
    svg += label(430, 325, "鸽派→黄金$4,400", 10, "#16A34A")
    svg += arrow(550, 380, 550, 400, "#DC2626", "ar", 2)
    svg += label(550, 410, "鹰派→黄金$4,200", 10, "#DC2626")

    svg += footnote("横盘越久，突破后的趋势越强。FOMC打破三重均衡", 498)
    svg += svg_footer()
    return svg


def comic_006_boj():
    """04 国际: BOJ加息至1%但日元不涨——利率升了货币不跟的悖论"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("国际：BOJ加息至1%·日元为何不涨反疲？", GOLD)

    # 左侧——BOJ旋钮(上调)
    svg += knob(180, 180, 55, 70, "#1A56DB")
    svg += label(180, 115, "BOJ 利率旋钮", 14, "#1A56DB", "middle", True)
    svg += label(180, 135, "上调至1% (31年最高)", 10, "#1E40AF")
    svg += label(180, 265, "加息=利多日元? → 理论上", 11, "#475569")

    # 旋钮向右的箭头(预期日元升)
    svg += arrow(245, 170, 310, 140, "#1A56DB", "agold", 2.5)
    svg += label(290, 128, "预期", 10, "#1A56DB")

    # 但日元实际走势(向下)
    svg += f'<rect x="320" y="200" width="180" height="80" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>'
    svg += label(410, 228, "实际: 美元/日元", 12, "#DC2626", "middle", True)
    svg += label(410, 252, "160.40 仍在疲软", 18, "#DC2626", "middle", True)
    svg += label(410, 272, "日元没涨!", 11, "#991B1B")

    # 交叉箭头——预期vs实际
    svg += arrow(410, 198, 410, 160, "#DC2626", "ar", 2)

    # 底部解释——实际利率仍为负
    svg += f'<rect x="80" y="310" width="610" height="90" rx="10" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2"/>'
    svg += label(384, 340, "为什么加息了日元还不涨？", 14, "#475569", "middle", True)

    # 公式
    svg += label(200, 370, "日本实际利率", 12, "#475569", "middle", True)
    svg += label(200, 390, "1% – 2%通胀 = -1%", 14, "#DC2626", "middle", True)
    svg += label(500, 370, "日美利差", 12, "#475569", "middle", True)
    svg += label(500, 390, "约250bp+ 仍巨大", 14, "#DC2626", "middle", True)

    # 套利交易说明
    svg += label(384, 420, "\u201c借日元买全球\u201d套利成本从0.75%\u21921%\u2014\u2014结构完全没变", 11, "#64748B")

    # 日元小人
    svg += geo_person(570, 295, 32, "#DC2626", "look_up")
    svg += label(570, 330, "日元", 11, "#DC2626")

    # BOJ大楼
    svg += f'<rect x="50" y="240" width="50" height="60" rx="3" fill="#EFF6FF" stroke="#1A56DB" stroke-width="1.5"/>'
    svg += label(75, 275, "BOJ", 11, "#1A56DB", "middle", True)

    svg += footnote("加息≠货币走强——实际利率和利差才是真正的驱动力", 500)
    svg += svg_footer()
    return svg


# ============================================================
# 生成全部
# ============================================================
comics = [
    ("panel-001", comic_001_summary, "Layer1全景速览"),
    ("panel-002", comic_002_ashare, "01 A股一九分化"),
    ("panel-003", comic_003_spacex, "03 科技SpaceX"),
    ("panel-004", comic_004_fomc, "05 宏观FOMC三岔路"),
    ("panel-005", comic_005_commodity, "06 商品油价黄金"),
    ("panel-006", comic_006_boj, "04 国际BOJ悖论"),
]

for fname, fn, desc in comics:
    svg = fn()
    path = os.path.join(OUT, f"{fname}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = len(svg.encode("utf-8")) / 1024
    print(f"  {fname}.svg ({desc}): {size_kb:.1f}KB")

print(f"\n全部 {len(comics)} 张漫画已生成到 {OUT}")
