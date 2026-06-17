"""
6.16 早报 Dalio SVG 漫画 v2.0 — 对标金融科普视觉风格指南
升级点:
  1. 几何人物 (圆头+梯形身体) 替代 线段简笔画
  2. 扩充视觉隐喻库: 齿轮/旋钮/阀门/管道/气球/阶梯/传送带
  3. 配色比例: 60%白+20%蓝+10%金+10%红绿
  4. 构图系统: 左右对比/流程图/循环图/上下分层
"""
import math, os

OUT = "D:/Desktop/每日财经/2026-06-16/wechat-publish/morning/comic"
os.makedirs(OUT, exist_ok=True)

# ============================================================
# 共用组件 v2.0
# ============================================================

def svg_header(w=768, h=512):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="Microsoft YaHei, SimHei, sans-serif">
  <rect width="{w}" height="{h}" fill="#FAFBFC"/>
'''

def svg_footer():
    return '</svg>'

# --- 几何人物 v2.0 ---
def geo_person(x, y, h=44, color="#1A56DB", role="stand", direction="right"):
    """几何形状人物 — 圆头+梯形身体 — 金融教育动画角色风格
    role: stand/arms_up/look_up/walk/carry/count
    direction: left/right (面向方向)
    """
    parts = []
    head_r = 10
    body_top_w = 16
    body_bot_w = 20
    body_h = h * 0.45

    cx = x  # 身体中心
    head_cy = y - body_h - head_r + 2

    # 头（圆）
    parts.append(f'<circle cx="{cx}" cy="{head_cy}" r="{head_r}" fill="#E2E8F0" stroke="{color}" stroke-width="2"/>')

    # 身体（倒梯形 — 肩膀宽）
    bx, by = cx - body_top_w, head_cy + head_r
    bw_top = body_top_w * 2
    bw_bot = body_bot_w * 2
    parts.append(
        f'<polygon points="{cx-bw_top/2},{by} {cx+bw_top/2},{by} '
        f'{cx+bw_bot/2},{by+body_h} {cx-bw_bot/2},{by+body_h}" '
        f'fill="#EFF6FF" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'
    )

    # 腿
    leg_y = by + body_h
    leg_len = h * 0.35
    parts.append(f'<line x1="{cx-7}" y1="{leg_y}" x2="{cx-9}" y2="{leg_y+leg_len}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
    parts.append(f'<line x1="{cx+7}" y1="{leg_y}" x2="{cx+9}" y2="{leg_y+leg_len}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')

    # 手臂（根据角色变）
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
    else:  # stand
        parts.append(f'<line x1="{cx-bw_top/2}" y1="{arm_y}" x2="{cx-bw_top/2-10}" y2="{arm_y+12}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        parts.append(f'<line x1="{cx+bw_top/2}" y1="{arm_y}" x2="{cx+bw_top/2+10}" y2="{arm_y+12}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')

    return '\n  '.join(parts)


def label(x, y, text, size=13, color="#334155", anchor="middle", bold=False, bg=None):
    """带可选背景的文字"""
    out = ''
    if bg:
        # 简单估算文字宽度
        tw = len(text) * size * 0.65
        out += f'<rect x="{x-tw/2-4}" y="{y-size+2}" width="{tw+8}" height="{size+4}" rx="3" fill="{bg}" opacity="0.85"/>\n  '
    w = "bold" if bold else "normal"
    out += f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{w}">{text}</text>'
    return out


def arrow_v(x1, y1, x2, y2, color="#1A56DB", label_text=""):
    """带标签的箭头"""
    out = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" stroke-linecap="round" marker-end="url(#arrowhead-{color.replace('#','')})"/>\n'
    if label_text:
        mx, my = (x1+x2)/2, (y1+y2)/2
        out += f'  <text x="{mx}" y="{my-6}" font-size="10" fill="{color}" text-anchor="middle">{label_text}</text>\n'
    return out


def dashed_line(x1, y1, x2, y2, color="#CBD5E1"):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,4"/>'


def gear(cx, cy, r, color="#1A56DB", teeth=8):
    """齿轮"""
    parts = []
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="3"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.55}" fill="none" stroke="{color}" stroke-width="1.5"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.2}" fill="{color}"/>')
    for i in range(teeth):
        angle = 2 * math.pi * i / teeth
        tx = cx + r * math.cos(angle)
        ty = cy + r * math.sin(angle)
        parts.append(
            f'<rect x="{tx-3}" y="{ty-3}" width="6" height="6" rx="1" '
            f'fill="{color}" transform="rotate({angle*180/math.pi},{tx},{ty})"/>'
        )
    return '\n  '.join(parts)


def knob(cx, cy, r, angle=0, color="#1A56DB"):
    """旋钮/调节器"""
    parts = []
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="{color}" stroke-width="2.5"/>')
    # 刻度标记
    for i in range(8):
        a = -math.pi*0.6 + i * math.pi*1.2/7
        ix = cx + (r-4) * math.cos(a)
        iy = cy + (r-4) * math.sin(a)
        ox = cx + (r+3) * math.cos(a)
        oy = cy + (r+3) * math.sin(a)
        parts.append(f'<line x1="{ix}" y1="{iy}" x2="{ox}" y2="{oy}" stroke="{color}" stroke-width="1"/>')
    # 指针
    pa = -math.pi*0.6 + angle * math.pi*1.2/100
    px = cx + (r-8) * math.cos(pa)
    py = cy + (r-8) * math.sin(pa)
    parts.append(f'<line x1="{cx}" y1="{cy}" x2="{px}" y2="{py}" stroke="#DC2626" stroke-width="2.5" stroke-linecap="round"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#DC2626"/>')
    return '\n  '.join(parts)


def valve(cx, cy, w, h, open_pct=50, color="#1A56DB"):
    """阀门/管道调节器"""
    parts = []
    # 管道
    parts.append(f'<rect x="{cx-w/2}" y="{cy-h/4}" width="{w}" height="{h/2}" rx="4" fill="#E2E8F0" stroke="{color}" stroke-width="2"/>')
    # 阀门手柄
    vy = cy - h/4 - 10
    parts.append(f'<rect x="{cx-4}" y="{vy-12}" width="8" height="24" rx="2" fill="#F1F5F9" stroke="{color}" stroke-width="2"/>')
    parts.append(f'<circle cx="{cx}" cy="{vy-12}" r="8" fill="white" stroke="#DC2626" stroke-width="2.5"/>')
    return '\n  '.join(parts)


def thermometer(cx, cy, h, temp_pct, color="#DC2626", label_text=""):
    """温度计 — 表示热度/冷度"""
    parts = []
    w = 28
    bulb_r = 18
    # 外壳
    parts.append(f'<rect x="{cx-w/2}" y="{cy-h}" width="{w}" height="{h}" rx="{w/2}" fill="white" stroke="#64748B" stroke-width="2"/>')
    # 球部
    parts.append(f'<circle cx="{cx}" cy="{cy+bulb_r-14}" r="{bulb_r}" fill="white" stroke="#64748B" stroke-width="2"/>')
    # 液体
    liquid_h = h * temp_pct / 100
    liquid_top = cy - liquid_h
    if liquid_h > 0:
        parts.append(f'<rect x="{cx-w/2+4}" y="{liquid_top}" width="{w-8}" height="{liquid_h+bulb_r-10}" rx="10" fill="{color}" opacity="0.85"/>')
        parts.append(f'<circle cx="{cx}" cy="{liquid_top}" r="{w/2-4}" fill="{color}" opacity="0.85"/>')
    if label_text:
        parts.append(f'<text x="{cx}" y="{cy+bulb_r+10}" font-size="12" fill="{color}" text-anchor="middle" font-weight="bold">{label_text}</text>')
    return '\n  '.join(parts)


def factory(x, y, w, h, color="#1A56DB", smoking=True):
    """工厂建筑"""
    parts = []
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#EBF5FF" stroke="{color}" stroke-width="2.5"/>')
    # 窗户
    ww, wh = w*0.18, h*0.2
    for row in range(2):
        for col in range(3):
            wx = x + w*0.12 + col*(ww+w*0.1)
            wy = y + h*0.2 + row*(wh+h*0.15)
            parts.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="#DBEAFE" stroke="{color}" stroke-width="1"/>')
    # 烟囱
    ch_x = x + w*0.6
    ch_w = w*0.12
    parts.append(f'<rect x="{ch_x}" y="{y-h*0.35}" width="{ch_w}" height="{h*0.35}" fill="#CBD5E1" stroke="{color}" stroke-width="1.5"/>')
    if smoking:
        for i, (cx, cr) in enumerate([(ch_x+ch_w/2, h*0.08), (ch_x+ch_w/2+6, h*0.06), (ch_x+ch_w/2-4, h*0.04)]):
            smokey = y - h*0.35 - (i+1)*12
            parts.append(f'<circle cx="{cx}" cy="{smokey}" r="{cr}" fill="none" stroke="#94A3B8" stroke-width="1.5"/>')
    return '\n  '.join(parts)


def store_closed(x, y, w, h):
    """关门的商店"""
    parts = []
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#FFF5F5" stroke="#EF4444" stroke-width="2"/>')
    # 卷帘门
    shutter_y = y + h*0.15
    shutter_h = h*0.55
    parts.append(f'<rect x="{x+w*0.08}" y="{shutter_y}" width="{w*0.84}" height="{shutter_h}" fill="#FEE2E2" stroke="#EF4444" stroke-width="1.5"/>')
    for i in range(5):
        ly = shutter_y + (i+1)*shutter_h/6
        parts.append(f'<line x1="{x+w*0.1}" y1="{ly}" x2="{x+w*0.9}" y2="{ly}" stroke="#EF4444" stroke-width="1"/>')
    # 关门标志
    parts.append(f'<text x="{x+w/2}" y="{shutter_y+shutter_h/2+5}" font-size="18" fill="#DC2626" text-anchor="middle" font-weight="bold">停业</text>')
    # 招牌
    parts.append(f'<rect x="{x+w*0.15}" y="{y-h*0.12}" width="{w*0.7}" height="{h*0.12}" rx="2" fill="#DC2626"/>')
    return '\n  '.join(parts)


def scale(x, y, tilt_deg=0, l_weight=False, r_weight=False):
    """天平 — 表示多空/利弊平衡"""
    parts = []
    # 底座
    parts.append(f'<rect x="{x-50}" y="{y+110}" width="100" height="14" rx="4" fill="#F1F5F9" stroke="#475569" stroke-width="2"/>')
    parts.append(f'<line x1="{x}" y1="{y+110}" x2="{x}" y2="{y-10}" stroke="#475569" stroke-width="3"/>')
    # 支点
    parts.append(f'<polygon points="{x},{y-10} {x-10},{y+5} {x+10},{y+5}" fill="#F1F5F9" stroke="#475569" stroke-width="1.5"/>')
    # 横梁（倾斜）
    import math
    rad = tilt_deg * math.pi / 180
    beam_len = 130
    lx = x - beam_len * math.cos(rad)
    ly = y - 10 - beam_len * math.sin(rad)
    rx = x + beam_len * math.cos(rad)
    ry = y - 10 + beam_len * math.sin(rad)
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="#475569" stroke-width="3" stroke-linecap="round"/>')
    # 左盘
    parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx}" y2="{ly+30}" stroke="#475569" stroke-width="1.5"/>')
    parts.append(f'<path d="M{lx-45},{ly+30} Q{lx},{ly+55} {lx+45},{ly+30}" fill="{ "#FEF2F2" if l_weight else "#F8FAFC"}" stroke="{ "#DC2626" if l_weight else "#94A3B8"}" stroke-width="2"/>')
    # 右盘
    parts.append(f'<line x1="{rx}" y1="{ry}" x2="{rx}" y2="{ry+50}" stroke="#475569" stroke-width="1.5"/>')
    parts.append(f'<path d="M{rx-45},{ry+50} Q{rx},{ry+75} {rx+45},{ry+50}" fill="{ "#FEF2F2" if r_weight else "#F8FAFC"}" stroke="{ "#DC2626" if r_weight else "#94A3B8"}" stroke-width="2"/>')
    return '\n  '.join(parts)


def balloon(x, y, r, expanding=False, color="#DC2626"):
    """气球 — 表示泡沫"""
    line_y = y + r + 20
    return (
        f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*1.25}" fill="{color}" opacity="0.35" stroke="{color}" stroke-width="2"/>\n'
        f'  <line x1="{x}" y1="{y+r*1.25}" x2="{x}" y2="{line_y}" stroke="{color}" stroke-width="1.5"/>\n'
        f'  <polygon points="{x-2},{line_y} {x+2},{line_y} {x},{line_y+6}" fill="{color}"/>'
        + ('\n  <text x="{x}" y="{y+5}" font-size="11" fill="white" text-anchor="middle" font-weight="bold">涨</text>' if expanding else '')
    )


def title_bar(text):
    """顶部标题栏"""
    return (
        f'<rect x="0" y="0" width="768" height="42" fill="#1A56DB" opacity="0.08"/>\n'
        f'  <text x="384" y="29" font-size="18" fill="#1A56DB" text-anchor="middle" font-weight="bold">{text}</text>'
    )


def footnote(text):
    """底部说明"""
    return f'<text x="384" y="498" font-size="11" fill="#94A3B8" text-anchor="middle">{text}</text>'


def divider(y):
    return f'<line x1="30" y1="{y}" x2="738" y2="{y}" stroke="#E2E8F0" stroke-width="1"/>'


# ============================================================
# 箭头定义
# ============================================================
ARROW_DEFS = '''
  <defs>
    <marker id="arrow-blue" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#1A56DB"/>
    </marker>
    <marker id="arrow-red" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#DC2626"/>
    </marker>
    <marker id="arrow-gold" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#D4A017"/>
    </marker>
  </defs>
'''


# ============================================================
# 6张漫画 v2.0
# ============================================================

def comic_01():
    """A股：工厂冒烟 vs 商场关门 — 左右对比构图"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("A股：一边机器轰鸣，一边门可罗雀")
    svg += divider(52)

    # 左侧 — 制造业火热
    svg += factory(50, 140, 180, 130, "#1A56DB", True)
    svg += gear(260, 190, 18, "#1A56DB")
    svg += gear(285, 175, 14, "#1A56DB")
    svg += label(140, 310, "制造业 PMI 52↑", 14, "#DC2626", "middle", True)
    svg += label(140, 330, "工厂满负荷运转", 12, "#64748B")
    svg += geo_person(105, 380, 36, "#1A56DB", "stand")
    svg += geo_person(175, 380, 36, "#1A56DB", "carry")

    # 右侧 — 消费冷清
    svg += store_closed(500, 140, 180, 130)
    svg += label(590, 310, "社零增速 3%↓", 14, "#EF4444", "middle", True)
    svg += label(590, 330, "消费者捂紧钱包", 12, "#64748B")

    # 中间裂缝
    svg += f'<line x1="378" y1="100" x2="392" y2="290" stroke="#475569" stroke-width="4.5"/>'
    for i in range(5):
        yy = 120 + i*35
        svg += f'<line x1="379" y1="{yy}" x2="391" y2="{yy-12}" stroke="#475569" stroke-width="2.5"/>'

    svg += footnote("结构性矛盾：生产端火热 · 消费端冰冷 · 经济冷热不均")
    svg += svg_footer()
    return svg


def comic_02():
    """美股：牛背狂欢 vs 前方FOMC悬崖 — 流程图构图"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("美股：牛背上的狂欢，前方是悬崖")

    # 地面
    svg += f'<rect x="30" y="370" width="470" height="8" rx="2" fill="#CBD5E1"/>'
    # 悬崖
    svg += f'<polygon points="500,370 500,230 540,370" fill="#F1F5F9" stroke="#64748B" stroke-width="2.5"/>'
    for yy in [260, 300, 340]:
        svg += f'<line x1="500" y1="{yy}" x2="490" y2="{yy+15}" stroke="#94A3B8" stroke-width="1.5"/>'

    # FOMC 警示牌
    svg += f'<rect x="565" y="340" width="110" height="36" rx="4" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.5"/>'
    svg += label(620, 363, "FOMC 加息", 13, "#DC2626", "middle", True)
    # 警示三角
    svg += f'<polygon points="560,320 620,320 590,290" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>'
    svg += label(590, 312, "!", 16, "#DC2626", "middle", True)

    # 铜牛
    svg += f'<ellipse cx="320" cy="330" rx="110" ry="45" fill="#FFF7ED" stroke="#D97706" stroke-width="3.5"/>'
    svg += f'<ellipse cx="430" cy="305" rx="28" ry="22" fill="#FFF7ED" stroke="#D97706" stroke-width="3.5"/>'
    svg += f'<path d="M435,285 Q445,260 455,265" fill="none" stroke="#D97706" stroke-width="3" stroke-linecap="round"/>'
    svg += f'<path d="M425,285 Q415,260 405,265" fill="none" stroke="#D97706" stroke-width="3" stroke-linecap="round"/>'
    svg += f'<circle cx="435" cy="302" r="3" fill="#D97706"/>'
    for lx in [250, 290, 350, 390]:
        svg += f'<line x1="{lx}" y1="370" x2="{lx}" y2="395" stroke="#D97706" stroke-width="3" stroke-linecap="round"/>'

    # 小人跳舞
    svg += geo_person(280, 290, 30, "#1A56DB", "arms_up")
    svg += geo_person(320, 284, 30, "#1A56DB", "arms_up")
    svg += geo_person(360, 288, 30, "#1A56DB", "arms_up")
    svg += geo_person(400, 278, 30, "#1A56DB", "arms_up")

    # 地面裂缝
    for cx in [470, 485]:
        svg += f'<line x1="{cx}" y1="370" x2="{cx}" y2="378" stroke="#EF4444" stroke-width="2"/>'

    svg += footnote("最大的风险，是「觉得自己没有风险」")
    svg += svg_footer()
    return svg


def comic_03():
    """科技：火箭皮筋 — 股价飞涨，基本面留在原地"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("科技：股价飞上天，基本面还在地上")

    # 地面 + 锚桩
    svg += f'<rect x="50" y="400" width="200" height="6" rx="2" fill="#CBD5E1"/>'
    svg += f'<polygon points="130,400 150,400 145,380 135,380" fill="#F1F5F9" stroke="#475569" stroke-width="2.5"/>'
    svg += label(140, 420, "基本面 (Revenue)", 13, "#475569", "middle", True)
    # 一个小标签
    svg += label(140, 438, "同比增长仅 8%", 11, "#94A3B8")

    # 皮筋
    svg += f'<path d="M140,380 C140,310 280,270 370,150" fill="none" stroke="#F59E0B" stroke-width="3.5" stroke-dasharray="8,3"/>'
    svg += f'<path d="M140,380 C170,330 300,240 370,150" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="6,5"/>'

    # 张力标注
    svg += f'<text x="225" y="245" font-size="11" fill="#F59E0B" text-anchor="middle" font-weight="bold">估值张力</text>'
    svg += f'<text x="225" y="260" font-size="10" fill="#F59E0B" text-anchor="middle">皮筋快断了!</text>'

    # 火箭
    svg += f'<ellipse cx="370" cy="130" rx="20" ry="50" fill="#EFF6FF" stroke="#1A56DB" stroke-width="3"/>'
    svg += f'<polygon points="370,68 350,90 390,90" fill="#DBEAFE" stroke="#1A56DB" stroke-width="3" stroke-linejoin="round"/>'
    svg += f'<circle cx="370" cy="112" r="7" fill="#93C5FD" stroke="#1A56DB" stroke-width="1.5"/>'
    svg += f'<polygon points="350,175 335,192 350,182" fill="#DBEAFE" stroke="#1A56DB" stroke-width="2"/>'
    svg += f'<polygon points="390,175 405,192 390,182" fill="#DBEAFE" stroke="#1A56DB" stroke-width="2"/>'
    # 火焰
    svg += f'<polygon points="362,178 370,215 378,178" fill="#FEF2F2" stroke="#EF4444" stroke-width="2"/>'
    svg += f'<polygon points="366,178 370,200 374,178" fill="#FEE2E2" stroke="#EF4444" stroke-width="1"/>'

    # 火箭标签
    svg += label(425, 100, "市值 $2.5万亿", 13, "#DC2626", "start", True)
    svg += label(425, 118, "5天暴涨 +42%", 12, "#DC2626", "start")
    svg += label(425, 136, "PS Ratio: 45x →", 11, "#64748B", "start")

    svg += footnote("估值能领先基本面多远？皮筋拉得太长，一定会弹回来")
    svg += svg_footer()
    return svg


def comic_04():
    """国际：两个温度计 — 日本过热 vs 中国偏冷"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("国际：一热一冷，亚洲经济温差")

    # 温度计1 — 日本
    tx1 = 220
    svg += thermometer(tx1, 160, 200, 85, "#DC2626", "日本 · 过热")
    svg += label(tx1+55, 90, "日经首破 70000", 13, "#DC2626", "start", True)
    svg += label(tx1+55, 110, "BOJ 加息至 1%", 12, "#DC2626", "start")
    svg += label(tx1+55, 130, "经济持续升温 ↑", 11, "#64748B", "start")
    # 小火苗
    svg += f'<path d="M{tx1+45},70 Q{tx1+35},55 {tx1+45},40 Q{tx1+55},55 {tx1+45},70" fill="#FCD34D" stroke="#F59E0B" stroke-width="1.5"/>'

    # 温度计2 — 中国
    tx2 = 548
    svg += thermometer(tx2, 160, 200, 30, "#1A56DB", "中国 · 偏冷")
    svg += label(tx2+55, 240, "通缩压力持续", 13, "#1A56DB", "start", True)
    svg += label(tx2+55, 260, "等待政策信号", 12, "#1A56DB", "start")
    svg += label(tx2+55, 280, "经济偏冷 ↓", 11, "#64748B", "start")
    # 雪花
    svg += f'<text x="{tx2+45}" y="280" font-size="18" fill="#93C5FD">❄</text>'

    # 中间分隔
    svg += f'<line x1="384" y1="200" x2="384" y2="400" stroke="#E2E8F0" stroke-width="2" stroke-dasharray="4,10"/>'

    svg += footnote("亚洲经济温差：一个在发烧，一个在发冷 — 政策分化将持续")
    svg += svg_footer()
    return svg


def comic_05():
    """宏观：FOMC会议桌 + 悬空骰子 — 居中构图"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("宏观：骰子还在空中，所有人都在等")

    # 会议桌
    svg += f'<ellipse cx="384" cy="340" rx="260" ry="45" fill="#F1F5F9" stroke="#64748B" stroke-width="2.5"/>'
    svg += f'<path d="M124,340 L124,270 L644,270 L644,340" fill="none" stroke="#64748B" stroke-width="1.5" stroke-dasharray="4,3"/>'

    # 围坐小人（模糊背景 + 前排清晰）
    bg_positions = [(180, 305), (250, 278), (330, 265), (384, 260), (438, 265), (518, 278), (588, 305)]
    for px, py in bg_positions:
        svg += f'<circle cx="{px}" cy="{py-24}" r="10" fill="#CBD5E1" stroke="#94A3B8" stroke-width="1.5"/>'
        svg += f'<line x1="{px}" y1="{py-14}" x2="{px}" y2="{py+12}" stroke="#94A3B8" stroke-width="2"/>'

    # 前排清晰人物（3个look_up）
    for px in [250, 384, 518]:
        svg += geo_person(px, 310, 32, "#475569", "look_up")

    # 悬空骰子
    dx, dy = 384, 120
    # 左右面
    svg += f'<polygon points="{dx},{dy-28} {dx+42},{dy-42} {dx},{dy-58} {dx-42},{dy-42}" fill="#FEF3C7" stroke="#D97706" stroke-width="2.5" stroke-linejoin="round"/>'
    svg += f'<polygon points="{dx},{dy-28} {dx+42},{dy-42} {dx+42},{dy-2} {dx},{dy+12}" fill="#FDE68A" stroke="#D97706" stroke-width="2.5" stroke-linejoin="round"/>'
    svg += f'<polygon points="{dx},{dy-28} {dx-42},{dy-42} {dx-42},{dy-2} {dx},{dy+12}" fill="#FEF3C7" stroke="#D97706" stroke-width="2.5" stroke-linejoin="round"/>'
    # 问号/数字在各面
    svg += f'<text x="{dx+12}" y="{dy-22}" font-size="20" fill="#D97706" text-anchor="middle" font-weight="bold">?</text>'
    svg += f'<text x="{dx-18}" y="{dy-18}" font-size="15" fill="#D97706" text-anchor="middle">3.75%</text>'
    svg += f'<text x="{dx+24}" y="{dy-12}" font-size="13" fill="#D97706" text-anchor="middle">4.25%</text>'

    # 悬空阴影
    svg += f'<ellipse cx="384" cy="150" rx="30" ry="5" fill="#E2E8F0"/>'

    svg += footnote("FOMC 6月16-17日开会 · 点阵图结果未定 · 沃什首次主持")
    svg += svg_footer()
    return svg


def comic_06():
    """商品：黄金天平 — 利率 vs 避险"""
    svg = svg_header() + ARROW_DEFS
    svg += title_bar("商品：黄金天平为何向左倾斜？")

    # 天平
    import math
    tilt = -8  # 左倾（左边重）
    rad = tilt * math.pi / 180
    cx, cy = 384, 390
    beam_len = 140

    # 底座
    svg += f'<rect x="{cx-55}" y="{cy+18}" width="110" height="16" rx="4" fill="#F1F5F9" stroke="#475569" stroke-width="2.5"/>'
    svg += f'<line x1="{cx}" y1="{cy+18}" x2="{cx}" y2="{cy-110}" stroke="#475569" stroke-width="3"/>'

    beam_y = cy - 115
    lx = cx - beam_len * math.cos(rad)
    ly = beam_y - beam_len * math.sin(rad)
    rx = cx + beam_len * math.cos(rad)
    ry = beam_y + beam_len * math.sin(rad)

    svg += f'<line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="#475569" stroke-width="4" stroke-linecap="round"/>'
    svg += f'<polygon points="{cx},{beam_y} {cx-10},{beam_y+12} {cx+10},{beam_y+12}" fill="#F1F5F9" stroke="#475569" stroke-width="2"/>'

    # 左盘 — 重
    svg += f'<line x1="{lx}" y1="{ly}" x2="{lx}" y2="{ly+28}" stroke="#475569" stroke-width="2"/>'
    svg += f'<path d="M{lx-55},{ly+28} Q{lx},{ly+58} {lx+55},{ly+28}" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.5"/>'
    # $符号堆叠
    for i, (ox, oy) in enumerate([(lx-28,ly+18),(lx+12,ly+12),(lx-8,ly+6),(lx+22,ly+28),(lx-32,ly+8),(lx,ly-2),(lx-15,ly+22)]):
        svg += f'<text x="{ox}" y="{oy}" font-size="15" fill="#DC2626" text-anchor="middle" font-weight="bold">$</text>'
    svg += label(lx, 68, "利率预期", 13, "#DC2626", "middle", True)
    svg += label(lx, 84, "真正的驱动力", 11, "#DC2626")

    # 右盘 — 轻
    svg += f'<line x1="{rx}" y1="{ry}" x2="{rx}" y2="{ry+48}" stroke="#475569" stroke-width="2"/>'
    svg += f'<path d="M{rx-55},{ry+48} Q{rx},{ry+78} {rx+55},{ry+48}" fill="#FFF7ED" stroke="#F59E0B" stroke-width="2.5"/>'
    svg += f'<path d="M{rx},{ry+38} Q{rx-12},{ry+22} {rx},{ry+10} Q{rx+12},{ry+22} {rx},{ry+38}" fill="#FCD34D" stroke="#F59E0B" stroke-width="1.5" opacity="0.7"/>'
    svg += label(rx, 68, "避险情绪", 13, "#F59E0B", "middle", True)
    svg += label(rx, 84, "只是假象", 11, "#F59E0B")

    # 箭头提示
    svg += f'<line x1="{lx-60}" y1="80" x2="{lx-30}" y2="95" stroke="#DC2626" stroke-width="2" marker-end="url(#arrow-red)"/>'
    svg += label(lx-80, 72, "重!", 14, "#DC2626", "middle", True)

    # 底部黄金价格
    svg += f'<rect x="290" y="450" width="188" height="38" rx="6" fill="#1A56DB"/>'
    svg += label(384, 476, "黄金坚守 $4,300", 18, "white", "middle", True)

    svg += svg_footer()
    return svg


# ============================================================
# 生成
# ============================================================
COMICS = [
    ("01-a股", comic_01),
    ("02-美股", comic_02),
    ("03-科技", comic_03),
    ("04-国际", comic_04),
    ("05-宏观", comic_05),
    ("06-商品", comic_06),
]

print("=" * 60)
print("Dalio SVG v2.0 — 金融科普视觉风格指南对标版")
print("=" * 60)

for sid, fn in COMICS:
    svg = fn()
    # 保存为 v2 版本
    filepath = os.path.join(OUT, f"panel-{sid}-v2.svg")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = len(svg.encode("utf-8")) / 1024
    print(f"  [OK] panel-{sid}-v2.svg  {size_kb:.1f}KB")

print(f"\n完成: 6/6 | Dalio SVG v2.0")
print(f"\n对比文件:")
for sid, _ in COMICS:
    print(f"  v1: comic/panel-{sid}.svg  →  v2: comic/panel-{sid}-v2.svg")
