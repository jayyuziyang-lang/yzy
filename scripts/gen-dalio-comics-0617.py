"""
6.17 早报 Dalio SVG 漫画 v2.0
对标「金融科普视觉风格指南」— 几何人物+视觉隐喻+极简信息图
7张漫画: 1张Layer1全景 + 6张Layer2故事
"""
import math, os

OUT = "D:/Desktop/每日财经/2026-06-17/wechat-publish/morning/comic"
os.makedirs(OUT, exist_ok=True)

W, H = 768, 512

# ============================================================
# 共用组件
# ============================================================

def svg_header():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Microsoft YaHei, SimHei, PingFang SC, sans-serif">\n  <rect width="{W}" height="{H}" fill="#FAFBFC"/>\n'

ARROW_DEFS = '''  <defs>
    <marker id="ab" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#1A56DB"/></marker>
    <marker id="ar" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#DC2626"/></marker>
    <marker id="ag" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#16A34A"/></marker>
    <marker id="ao" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#D4A017"/></marker>
  </defs>\n'''

def svg_footer():
    return '</svg>'

def geo_person(x, y, h=44, color="#1A56DB", role="stand"):
    """几何人物 v2.0 — 圆头+梯形身体"""
    parts = []
    head_r, body_top_w, body_bot_w = 10, 16, 20
    body_h = h * 0.45
    cx = x
    head_cy = y - body_h - head_r + 2
    parts.append(f'<circle cx="{cx}" cy="{head_cy}" r="{head_r}" fill="#E2E8F0" stroke="{color}" stroke-width="2"/>')
    bx, by = cx - body_top_w, head_cy + head_r
    bw_top, bw_bot = body_top_w * 2, body_bot_w * 2
    parts.append(f'<polygon points="{cx-bw_top/2},{by} {cx+bw_top/2},{by} {cx+bw_bot/2},{by+body_h} {cx-bw_bot/2},{by+body_h}" fill="#EFF6FF" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>')
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

def title_bar(text, color="#1A56DB"):
    return (f'<rect x="0" y="0" width="{W}" height="44" fill="{color}" opacity="0.08"/>\n'
            f'  <text x="{W/2}" y="30" font-size="18" fill="{color}" text-anchor="middle" font-weight="bold">{text}</text>')

def footnote(text, y=500):
    return f'<text x="{W/2}" y="{y}" font-size="11" fill="#94A3B8" text-anchor="middle">{text}</text>'

def dashed_line(x1, y1, x2, y2, color="#CBD5E1"):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,4"/>'

def arrow(x1, y1, x2, y2, color="#1A56DB", marker="ab", sw=2.5):
    mid = f' marker-end="url(#{marker})"' if marker else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{mid}/>'

def curved_arrow(x1, y1, x2, y2, color="#1A56DB", curve=40, marker="ab"):
    cy = (y1 + y2) / 2
    cx = (x1 + x2) / 2 + (curve if x2 > x1 else -curve)
    return f'<path d="M{x1},{y1} Q{cx},{cy} {x2},{y2}" fill="none" stroke="{color}" stroke-width="2.5" marker-end="url(#{marker})"/>'

def gear(cx, cy, r, color="#1A56DB", teeth=8):
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="3"/>',
             f'<circle cx="{cx}" cy="{cy}" r="{r*0.55}" fill="none" stroke="{color}" stroke-width="1.5"/>',
             f'<circle cx="{cx}" cy="{cy}" r="{r*0.2}" fill="{color}"/>']
    for i in range(teeth):
        angle = 2 * math.pi * i / teeth
        tx, ty = cx + r * math.cos(angle), cy + r * math.sin(angle)
        parts.append(f'<rect x="{tx-3}" y="{ty-3}" width="6" height="6" rx="1" fill="{color}" transform="rotate({angle*180/math.pi},{tx},{ty})"/>')
    return '\n  '.join(parts)

def knob(cx, cy, r, angle=0, color="#1A56DB"):
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

def thermometer(cx, cy, h, temp_pct, color="#DC2626"):
    w = 28
    bulb_r = 18
    parts = [f'<rect x="{cx-w/2}" y="{cy-h}" width="{w}" height="{h}" rx="{w/2}" fill="white" stroke="#64748B" stroke-width="2"/>',
             f'<circle cx="{cx}" cy="{cy+bulb_r-14}" r="{bulb_r}" fill="white" stroke="#64748B" stroke-width="2"/>']
    liquid_h = h * temp_pct / 100
    liquid_top = cy - liquid_h
    if liquid_h > 0:
        parts.append(f'<rect x="{cx-w/2+4}" y="{liquid_top}" width="{w-8}" height="{liquid_h+bulb_r-10}" rx="10" fill="{color}" opacity="0.85"/>')
        parts.append(f'<circle cx="{cx}" cy="{liquid_top}" r="{w/2-4}" fill="{color}" opacity="0.85"/>')
    return '\n  '.join(parts)

def clock_face(cx, cy, r, hour_angle=0):
    """简单时钟面"""
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="#475569" stroke-width="2.5"/>',
             f'<circle cx="{cx}" cy="{cy}" r="3" fill="#475569"/>']
    for i in range(12):
        a = -math.pi/2 + i * math.pi/6
        ix, iy = cx + (r-6)*math.cos(a), cy + (r-6)*math.sin(a)
        ox, oy = cx + (r-2)*math.cos(a), cy + (r-2)*math.sin(a)
        parts.append(f'<line x1="{ix}" y1="{iy}" x2="{ox}" y2="{oy}" stroke="#475569" stroke-width="1.5"/>')
    ha = -math.pi/2 + hour_angle * math.pi/180
    hx, hy = cx + r*0.55*math.cos(ha), cy + r*0.55*math.sin(ha)
    parts.append(f'<line x1="{cx}" y1="{cy}" x2="{hx}" y2="{hy}" stroke="#1A56DB" stroke-width="2.5" stroke-linecap="round"/>')
    return '\n  '.join(parts)

def pool(x, y, w, h, fill_level, color, label_text="", sub_text=""):
    """水池——fill_level 0-100"""
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

def valve_pipe(cx, cy, w, h, color="#1A56DB", open_valve=True):
    """管道+阀门"""
    parts = [f'<rect x="{cx-w/2}" y="{cy-h/4}" width="{w}" height="{h/2}" rx="4" fill="#E2E8F0" stroke="{color}" stroke-width="2"/>']
    vx = cx
    vy = cy - h/4 - 10
    parts.append(f'<rect x="{vx-5}" y="{vy-14}" width="10" height="28" rx="3" fill="#F1F5F9" stroke="{color}" stroke-width="2.5"/>')
    valve_color = "#16A34A" if open_valve else "#DC2626"
    parts.append(f'<circle cx="{vx}" cy="{vy-14}" r="9" fill="white" stroke="{valve_color}" stroke-width="2.5"/>')
    if open_valve:
        parts.append(f'<line x1="{vx}" y1="{vy-20}" x2="{vx}" y2="{vy-8}" stroke="{valve_color}" stroke-width="2"/>')
    else:
        parts.append(f'<line x1="{vx-5}" y1="{vy-19}" x2="{vx+5}" y2="{vy-9}" stroke="{valve_color}" stroke-width="2"/>')
    return '\n  '.join(parts)


# ============================================================
# 7张漫画
# ============================================================

def comic_01_summary():
    """Layer 1 全景: 大轮动——资金从科技池涌向周期池"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("大轮动：资金如何从科技奔涌向周期？")

    # 顶部传导链（小齿轮）
    chain_y = 78
    svg += gear(90, chain_y, 14, "#D4A017")
    svg += label(90, chain_y+28, "美伊协议", 10, "#D4A017")
    svg += arrow(108, chain_y, 136, chain_y, "#D4A017", "ao", 2)
    svg += gear(155, chain_y, 14, "#EA580C")
    svg += label(155, chain_y+28, "油价暴跌", 10, "#EA580C")
    svg += arrow(173, chain_y, 201, chain_y, "#EA580C", "ao", 2)
    svg += gear(218, chain_y, 12, "#D4A017")
    svg += label(218, chain_y+28, "通胀预期降", 10, "#D4A017")
    svg += arrow(235, chain_y, 500, chain_y, "#D4A017", "ao", 2)

    # 左侧——科技水池（水位下降）
    tech_pool_x, tech_pool_y, tech_pool_w, tech_pool_h = 50, 140, 200, 180
    svg += pool(tech_pool_x, tech_pool_y, tech_pool_w, tech_pool_h, 65, "#7C3AED", "科技/AI 资金池", "费半-5.7%")

    # 科技池上方图标
    for i, (ix, txt) in enumerate([(85, "Marvell"), (125, "Intel"), (165, "AMD"), (205, "NVDA")]):
        svg += f'<text x="{ix}" y="{tech_pool_y+tech_pool_h-25+i*14}" font-size="9" fill="#7C3AED" text-anchor="middle">{txt}</text>'

    # 右侧——周期水池（水位上升）
    cycl_pool_x, cycl_pool_y, cycl_pool_w, cycl_pool_h = 518, 140, 200, 180
    svg += pool(cycl_pool_x, cycl_pool_y, cycl_pool_w, cycl_pool_h, 75, "#16A34A", "银行/工业 资金池", "道指+0.64%")

    for i, (ix, txt) in enumerate([(553, "JPM"), (593, "Visa"), (633, "高盛"), (673, "CAT")]):
        svg += f'<text x="{ix}" y="{cycl_pool_y+cycl_pool_h-25+i*14}" font-size="9" fill="#16A34A" text-anchor="middle">{txt}</text>'

    # 中间——管道+阀门（打开状态）
    pipe_y = tech_pool_y + tech_pool_h/2
    svg += valve_pipe(384, pipe_y, 180, 24, "#1A56DB", True)

    # 管道水流方向
    svg += arrow(290, pipe_y-8, 310, pipe_y-8, "#1A56DB", "ab", 2)
    svg += arrow(458, pipe_y-8, 478, pipe_y-8, "#1A56DB", "ab", 2)

    # 管道上方标注
    svg += label(384, pipe_y-30, "资金迁徙通道", 11, "#1A56DB", "middle", True)
    svg += label(384, pipe_y-16, "2026年最大单日轮动", 10, "#DC2626", "middle", True)

    # 科技→周期 水流标记
    svg += f'<text x="220" y="{tech_pool_y+tech_pool_h+30}" font-size="10" fill="#7C3AED" text-anchor="middle">水位↓</text>'
    svg += f'<text x="548" y="{cycl_pool_y+cycl_pool_h+30}" font-size="10" fill="#16A34A" text-anchor="middle">水位↑</text>'

    # 底部FOMC时钟
    svg += clock_face(384, 435, 28, 315)
    svg += label(440, 435, "FOMC Day2", 13, "#1A56DB", "start", True)
    svg += label(440, 453, "沃什首秀倒计时...", 11, "#64748B", "start")

    svg += footnote("轮动的本质：宏观条件变了，钱换了地方")
    svg += svg_footer()
    return svg


def comic_02_ashare():
    """01 A股: 外部冲击波 vs 内部缓冲垫"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("A股：外部冲击波袭来，但有缓冲垫在托底")

    # 左侧——冲击源：费半暴跌
    svg += f'<rect x="30" y="80" width="160" height="100" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>'
    svg += label(110, 110, "费城半导体", 13, "#DC2626", "middle", True)
    svg += label(110, 134, "−5.7%", 30, "#DC2626", "middle", True)
    svg += label(110, 158, "年内最大单日跌幅", 10, "#991B1B")

    # 冲击波箭头
    for i in range(3):
        svg += arrow(195 + i*28, 110 + i*8, 235 + i*28, 110 + i*8, "#DC2626", "ar", 2.5)

    svg += label(260, 95, "冲击传导", 10, "#DC2626", "middle", True)

    # 中间——A股芯片（被冲击）
    svg += f'<rect x="290" y="80" width="180" height="100" rx="8" fill="#FFF5F5" stroke="#EF4444" stroke-width="2"/>'
    svg += label(380, 110, "A股芯片板块", 13, "#EF4444", "middle", True)

    chips = [("中芯国际", "-1.7%", 130), ("华虹宏力", "-2.7%", 148), ("寒武纪", "-1.3%", 166)]
    for nm, val, yy in chips:
        svg += label(380, yy, f"{nm} {val}", 10, "#DC2626")

    # 冲击波到达
    svg += arrow(470, 130, 500, 130, "#DC2626", "ar", 2)

    # 右侧——A股大盘
    svg += f'<rect x="510" y="80" width="220" height="100" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>'
    svg += label(620, 110, "A股大盘", 13, "#334155", "middle", True)
    svg += label(620, 135, "沪指 4074 -0.43%", 13, "#16A34A", "middle", True)
    svg += label(620, 155, "3605家下跌", 11, "#64748B")
    svg += label(620, 170, "等待FOMC方向", 10, "#94A3B8")

    # 底部——缓冲垫
    buf_y = 240
    svg += f'<rect x="60" y="{buf_y}" width="650" height="80" rx="10" fill="#F0FDF4" stroke="#16A34A" stroke-width="2" stroke-dasharray="8,3"/>'
    svg += label(384, buf_y+22, "内生缓冲垫", 14, "#16A34A", "middle", True)

    buffers = [("央行净投放", "2,613亿元", 130), ("融资余额", "+263亿→2.89万亿", 300), ("陆家嘴论坛", "今日开幕·政策信号", 500), ("光伏/航运", "逆势走强接力", 660)]
    for txt, val, bx in buffers:
        svg += f'<text x="{bx}" y="{buf_y+46}" font-size="11" fill="#166534" text-anchor="middle" font-weight="bold">{txt}</text>'
        svg += f'<text x="{bx}" y="{buf_y+64}" font-size="10" fill="#16A34A" text-anchor="middle">{val}</text>'

    # 缓冲垫向上托举
    svg += arrow(384, buf_y, 384, 195, "#16A34A", "ag", 2.5)

    svg += footnote("A股今天的关键词：等待。外部冲击是事实，内部缓冲也是事实——FOMC后见分晓")
    svg += svg_footer()
    return svg


def comic_03_us():
    """02 美股: 跷跷板——道指向上·纳指向下"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("美股：跷跷板的两端——道指新高vs费半暴跌")

    # 跷跷板支点
    pivot_x, pivot_y = 384, 280
    svg += f'<polygon points="{pivot_x},{pivot_y-15} {pivot_x-20},{pivot_y+15} {pivot_x+20},{pivot_y+15}" fill="#F1F5F9" stroke="#475569" stroke-width="2"/>'

    # 倾斜横梁（左低右高——道指在右、涨）
    beam_len = 250
    tilt = -12
    rad = tilt * math.pi / 180
    lx = pivot_x - beam_len * math.cos(rad)
    ly = pivot_y - 10 - beam_len * math.sin(rad)
    rx = pivot_x + beam_len * math.cos(rad)
    ry = pivot_y - 10 + beam_len * math.sin(rad)

    svg += f'<line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="#475569" stroke-width="4" stroke-linecap="round"/>'

    # 左端——纳指/费半（沉下去了）
    svg += f'<rect x="{lx-90}" y="{ly-105}" width="180" height="90" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.5"/>'
    svg += label(lx, ly-82, "纳斯达克", 13, "#DC2626", "middle", True)
    svg += label(lx, ly-58, "−1.15%", 28, "#DC2626", "middle", True)
    svg += label(lx, ly-35, "费半 −5.7%", 12, "#DC2626")

    # 往下掉的小人
    svg += geo_person(lx-50, ly-20, 28, "#DC2626", "look_up")
    svg += geo_person(lx+50, ly-15, 28, "#DC2626", "look_up")

    # 右端——道指（翘起来了）
    svg += f'<rect x="{rx-90}" y="{ry-105}" width="180" height="90" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="2.5"/>'
    svg += label(rx, ry-82, "道琼斯", 13, "#16A34A", "middle", True)
    svg += label(rx, ry-58, "52,000", 28, "#16A34A", "middle", True)
    svg += label(rx, ry-35, "史上首次+0.64%", 12, "#16A34A")

    # 往上举手的小人
    svg += geo_person(rx-50, ry-130, 28, "#16A34A", "arms_up")
    svg += geo_person(rx+50, ry-125, 28, "#16A34A", "arms_up")

    # 底部：跷跷板两端标签
    svg += label(lx, pivot_y+42, "科技/AI", 12, "#DC2626", "middle", True)
    svg += label(rx, pivot_y+42, "银行/工业", 12, "#16A34A", "middle", True)

    # 顶部传导齿轮链
    for gx, gc in [(200, "#EA580C"), (280, "#D4A017"), (360, "#D4A017"), (440, "#1A56DB"), (520, "#16A34A")]:
        svg += gear(gx, 58, 14, gc, 6)
    svg += label(384, 40, "美伊协议 → 油价暴跌 → 通胀降温 → 利率见顶 → 资金大迁徙", 11, "#475569")

    svg += footnote("跷跷板的支点是「通胀预期」——油价跌，跷跷板往周期倾斜")
    svg += svg_footer()
    return svg


def comic_04_spacex():
    """03 科技: SpaceX火箭升空 vs 科技大盘下沉"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("科技：SpaceX一飞冲天，其他科技股却在失重下沉")

    # 地面
    svg += f'<rect x="30" y="400" width="708" height="6" rx="2" fill="#CBD5E1"/>'

    # 下沉的科技股（在地面以下）
    sinking = [("NVDA", 180, 420, "-2%"), ("Meta", 290, 430, "-2.8%"), ("TSLA", 410, 425, "-1.6%"),
               ("AAPL", 530, 418, "-0.4%"), ("AMD", 640, 432, "-7.3%")]
    for nm, sx, sy, sv in sinking:
        svg += f'<ellipse cx="{sx}" cy="{sy}" rx="38" ry="14" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>'
        svg += label(sx, sy-2, nm, 11, "#DC2626", "middle", True)
        svg += label(sx, sy+12, sv, 10, "#991B1B")

    # 下沉箭头
    for _, sx, sy, _ in sinking:
        svg += arrow(sx, sy-30, sx, sy-16, "#DC2626", "ar", 1.5)

    # SpaceX 火箭（居中，大幅高于地面）
    rx, ry = 384, 180
    # 箭体
    svg += f'<ellipse cx="{rx}" cy="{ry}" rx="24" ry="70" fill="#EFF6FF" stroke="#1A56DB" stroke-width="3.5"/>'
    # 头部
    svg += f'<polygon points="{rx},{ry-80} {rx-24},{ry-68} {rx+24},{ry-68}" fill="#DBEAFE" stroke="#1A56DB" stroke-width="3.5" stroke-linejoin="round"/>'
    # 窗户
    svg += f'<circle cx="{rx}" cy="{ry-50}" r="8" fill="#93C5FD" stroke="#1A56DB" stroke-width="2"/>'
    # 火焰
    svg += f'<polygon points="{rx-16},{ry+68} {rx},{ry+120} {rx+16},{ry+68}" fill="#FEF2F2" stroke="#EF4444" stroke-width="2"/>'
    svg += f'<polygon points="{rx-10},{ry+68} {rx},{ry+105} {rx+10},{ry+68}" fill="#FEE2E2" stroke="#EF4444" stroke-width="1"/>'
    # 侧翼
    svg += f'<polygon points="{rx-26},{ry+30} {rx-34},{ry+70} {rx-22},{ry+50}" fill="#DBEAFE" stroke="#1A56DB" stroke-width="2.5"/>'
    svg += f'<polygon points="{rx+26},{ry+30} {rx+34},{ry+70} {rx+22},{ry+50}" fill="#DBEAFE" stroke="#1A56DB" stroke-width="2.5"/>'

    # SpaceX 标注
    svg += label(rx+55, ry-80, "SpaceX", 16, "#1A56DB", "start", True)
    svg += label(rx+55, ry-62, "$201.80 +4.8%", 14, "#DC2626", "start", True)
    svg += label(rx+55, ry-46, "三日累涨 +50%", 13, "#DC2626", "start", True)
    svg += label(rx+55, ry-30, "市值 $2.64万亿", 12, "#64748B", "start")
    svg += label(rx+55, ry-15, "超越亚马逊全球第五", 11, "#64748B", "start")

    # 估值皮筋
    svg += f'<path d="M{rx+80},{ry-60} Q{rx+130},{ry-30} {rx+120},{ry+5}" fill="none" stroke="#F59E0B" stroke-width="2" stroke-dasharray="6,3"/>'
    svg += f'<text x="{rx+155}" y="{ry-45}" font-size="10" fill="#F59E0B" font-weight="bold">估值皮筋</text>'
    svg += f'<text x="{rx+155}" y="{ry-30}" font-size="9" fill="#F59E0B">还能拉多长?</text>'

    # 底部说明
    svg += label(384, 470, "一个涨50%，一群跌5-7%——科技板块内部也在分化", 12, "#475569", "middle", True)
    svg += svg_footer()
    return svg


def comic_05_boj():
    """04 国际: BOJ加息悖论——利率上调了，日元为什么不涨？"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("BOJ加息悖论：利率上去了，日元为什么还在地上？")

    # 日本建筑
    svg += f'<rect x="60" y="130" width="140" height="140" rx="5" fill="#FFF7ED" stroke="#EA580C" stroke-width="2.5"/>'
    svg += label(130, 150, "日本銀行", 14, "#EA580C", "middle", True)
    svg += label(130, 170, "BOJ", 11, "#EA580C")

    # 加息公告
    svg += f'<rect x="75" y="185" width="110" height="40" rx="4" fill="white" stroke="#EA580C" stroke-width="1.5"/>'
    svg += label(130, 202, "政策金利", 10, "#EA580C")
    svg += label(130, 218, "0.75%→1.00%", 13, "#DC2626", "middle", True)

    # 箭头：加息→日元应该升值
    svg += label(290, 155, "加息", 12, "#DC2626", "middle", True)
    svg += label(290, 172, "理论上", 10, "#64748B")
    svg += arrow(220, 200, 320, 200, "#DC2626", "ar", 2.5)

    # 但... 日元小人（原地不动）
    svg += geo_person(390, 290, 38, "#D4A017", "stand")
    svg += label(390, 340, "日元", 13, "#D4A017", "middle", True)
    svg += label(390, 356, "USD/JPY 160.40", 11, "#64748B")
    svg += label(390, 372, "还在原地!", 11, "#DC2626", "middle", True)

    # 实际利率解释区
    svg += f'<rect x="460" y="130" width="270" height="150" rx="8" fill="#F8FAFC" stroke="#64748B" stroke-width="2"/>'
    svg += label(595, 155, "为什么会这样?", 13, "#475569", "middle", True)

    # 实际利率公式
    svg += label(595, 185, "实际利率 = 名义利率 − 通胀", 12, "#475569", "middle", True)
    svg += f'<line x1="490" y1="198" x2="700" y2="198" stroke="#E2E8F0" stroke-width="1"/>'

    svg += label(520, 220, "1.00%", 16, "#1A56DB", "start", True)
    svg += label(520, 240, "名义利率（BOJ加息后）", 10, "#1A56DB", "start")
    svg += label(670, 220, "−", 16, "#475569")

    svg += label(530, 265, "2%+", 16, "#DC2626", "start", True)
    svg += label(530, 285, "通胀率", 10, "#DC2626", "start")

    svg += f'<line x1="490" y1="295" x2="700" y2="295" stroke="#E2E8F0" stroke-width="1"/>'

    svg += label(530, 315, "≈ −1.5%", 16, "#DC2626", "start", True)
    svg += label(530, 335, "实际利率仍是深度负值", 10, "#DC2626", "start")

    # 结论框
    svg += f'<rect x="60" y="410" width="650" height="42" rx="6" fill="#EFF6FF" stroke="#1A56DB" stroke-width="1"/>'
    svg += label(384, 436, "借日元的成本从0.75%变成1%——套利交易还在继续，日元涨不起来", 13, "#1E40AF", "middle", True)

    svg += svg_footer()
    return svg


def comic_06_fomc():
    """05 宏观: FOMC三岔路口——沃什的选择题"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("FOMC：沃什站在三岔路口，全世界都在等他的选择")

    # 沃什（居中偏上，面对三个方向）
    svg += geo_person(384, 170, 42, "#1A56DB", "look_up")

    # 三条路（从沃什脚下延伸出去）
    paths = [
        ("左", 180, 280, "#16A34A", "鸽派路径", "点阵图加息预期下移\n删除宽松倾向被弱化\n→科技反弹·美元走弱", "概率40%"),
        ("中", 384, 350, "#D4A017", "中性路径", "维持现状\n措辞模糊\n→市场按兵不动", "概率30%"),
        ("右", 588, 280, "#DC2626", "鹰派路径", "删除宽松倾向明确\n暗示加息不远\n→科技承压·轮动加速", "概率30%"),
    ]

    for align, px, py, color, title, desc, prob in paths:
        # 路面
        path_w = 120
        svg += f'<polygon points="384,265 {px-path_w/2},{py+60} {px+path_w/2},{py+60}" fill="{color}" opacity="0.08" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,4"/>'

        # 路牌
        svg += f'<rect x="{px-path_w/2-10}" y="{py-15}" width="{path_w+20}" height="30" rx="5" fill="white" stroke="{color}" stroke-width="2.5"/>'
        svg += label(px, py+6, title, 14, color, "middle", True)

        # 详细描述
        desc_lines = desc.split("\n")
        for di, dl in enumerate(desc_lines):
            svg += label(px, py+35+di*16, dl, 10, "#475569")

        # 概率标注
        svg += label(px, py+90, prob, 12, color, "middle", True)

    # 美联储大楼（上方）
    svg += f'<rect x="284" y="55" width="200" height="70" rx="6" fill="#EFF6FF" stroke="#1A56DB" stroke-width="2.5"/>'
    svg += f'<polygon points="284,55 384,20 484,55" fill="#DBEAFE" stroke="#1A56DB" stroke-width="2.5" stroke-linejoin="round"/>'
    svg += label(384, 100, "FOMC · Day 2", 16, "#1A56DB", "middle", True)
    svg += label(384, 118, "3.50%-3.75% 维持", 11, "#64748B")

    # 时钟
    svg += clock_face(180, 95, 22, 315)
    svg += label(180, 135, "北京时间", 9, "#64748B")
    svg += label(180, 148, "周四凌晨2:00", 9, "#DC2626", "middle", True)

    svg += footnote("三大悬念：点阵图是否留白·宽松倾向是否删除·沃什语气偏鸽还是偏鹰")
    svg += svg_footer()
    return svg


def comic_07_commodity():
    """06 商品: 油价瀑布 vs 黄金平台——两个资产的FOMC前夜"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("商品：油价瀑布式下跌，黄金平台等待——FOMC前夜的两种姿态")

    # 左侧——油价瀑布
    oil_x, oil_y = 60, 100
    svg += f'<rect x="{oil_x}" y="{oil_y}" width="280" height="300" rx="8" fill="white" stroke="#EA580C" stroke-width="2"/>'
    svg += label(oil_x+140, oil_y+25, "WTI 原油", 16, "#EA580C", "middle", True)

    # 油价下跌曲线
    points = [(oil_x+30, oil_y+60), (oil_x+70, oil_y+85), (oil_x+110, oil_y+110), (oil_x+150, oil_y+150),
              (oil_x+190, oil_y+200), (oil_x+230, oil_y+260)]
    path = "M" + " L".join(f"{px},{py}" for px, py in points)
    svg += f'<polyline points="{" ".join(f"{px},{py}" for px, py in points)}" fill="none" stroke="#EA580C" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    svg += arrow(points[-1][0], points[-1][1], points[-1][0], points[-1][1]+30, "#EA580C", "ar", 3)

    # 价格标注
    svg += label(oil_x+40, oil_y+50, "$81", 16, "#EA580C", "start", True)
    svg += label(oil_x+240, oil_y+248, "$76", 22, "#DC2626", "start", True)
    svg += label(oil_x+240, oil_y+270, "−5.8%", 16, "#DC2626", "start", True)

    # 油桶图标
    svg += f'<rect x="{oil_x+100}" y="{oil_y+50}" width="40" height="50" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="2.5"/>'
    svg += f'<rect x="{oil_x+105}" y="{oil_y+42}" width="30" height="12" rx="3" fill="#FED7AA" stroke="#EA580C" stroke-width="1.5"/>'
    svg += label(oil_x+120, oil_y+80, "$", 14, "#EA580C")

    # 霍尔木兹
    svg += f'<text x="{oil_x+140}" y="{oil_y+310}" font-size="11" fill="#EA580C" text-anchor="middle">霍尔木兹复航 + 伊朗石油回归</text>'

    # 右侧——黄金平台
    gold_x = 400
    svg += f'<rect x="{gold_x}" y="{oil_y}" width="280" height="300" rx="8" fill="white" stroke="#D4A017" stroke-width="2"/>'
    svg += label(gold_x+140, oil_y+25, "现货黄金", 16, "#D4A017", "middle", True)

    # 平台线
    svg += f'<line x1="{gold_x+30}" y1="{oil_y+180}" x2="{gold_x+250}" y2="{oil_y+180}" stroke="#D4A017" stroke-width="3"/>'
    svg += label(gold_x+140, oil_y+210, "$4,340", 22, "#D4A017", "middle", True)
    svg += label(gold_x+140, oil_y+232, "横盘等待方向", 12, "#64748B")

    # 三个拉扯力
    forces = [
        (gold_x+140, oil_y+75, "三股力量互扯", "#D4A017"),
        (gold_x+70, oil_y+110, "油价↓ → 通胀预期↓", "#EA580C"),
        (gold_x+70, oil_y+130, "→ 对黄金利空", "#DC2626"),
        (gold_x+210, oil_y+110, "DXY破100", "#16A34A"),
        (gold_x+210, oil_y+130, "→ 对黄金利多", "#16A34A"),
    ]
    for fx, fy, ft, fc in forces:
        bold = "bold" if "三股" in ft else "normal"
        svg += f'<text x="{fx}" y="{fy}" font-size="{10 if bold == "normal" else 12}" fill="{fc}" text-anchor="middle" font-weight="{bold}">{ft}</text>'

    # 方向箭头（左右拉扯）
    svg += arrow(gold_x+140, oil_y+95, gold_x+70, oil_y+95, "#DC2626", "ar", 2)
    svg += arrow(gold_x+140, oil_y+95, gold_x+210, oil_y+95, "#16A34A", "ag", 2)

    # FOMC标注
    svg += label(gold_x+140, oil_y+280, "FOMC决议后", 11, "#64748B")
    svg += label(gold_x+140, oil_y+298, "必选方向 ↑↓", 11, "#DC2626", "middle", True)

    # 底部总结
    svg += f'<rect x="60" y="420" width="650" height="36" rx="6" fill="#EFF6FF" stroke="#1A56DB" stroke-width="1"/>'
    svg += label(384, 444, "油价已跌回「伊朗危机前」· 黄金在等FOMC给出下一个方向", 13, "#1E40AF", "middle", True)

    svg += svg_footer()
    return svg


# ============================================================
# 生成
# ============================================================
COMICS = [
    ("01-summary", comic_01_summary, "Layer1全景·大轮动"),
    ("02-ashare", comic_02_ashare, "01 A股·冲击传导"),
    ("03-us", comic_03_us, "02 美股·跷跷板"),
    ("04-spacex", comic_04_spacex, "03 科技·SpaceX火箭"),
    ("05-boj", comic_05_boj, "04 国际·BOJ悖论"),
    ("06-fomc", comic_06_fomc, "05 宏观·FOMC三岔路"),
    ("07-commodity", comic_07_commodity, "06 商品·油价瀑布"),
]

print("=" * 70)
print("6.17 早报 Dalio SVG v2.0 漫画生成")
print("=" * 70)

for sid, fn, desc in COMICS:
    svg = fn()
    filepath = os.path.join(OUT, f"dalio-{sid}.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = len(svg.encode("utf-8")) / 1024
    print(f"  [OK] dalio-{sid}.svg  {size_kb:.1f}KB  | {desc}")

print(f"\n完成: {len(COMICS)}/7 | 输出目录: {OUT}")
print("\n旧版漫画: panel-001.svg（将被替换）")
print("新版漫画: dalio-*.svg（Dalio v2.0 几何人物+视觉隐喻）")
