"""
6.17 晚报 Dalio SVG 漫画 V3 — Dalio建筑插图风格
对标《经济机器是如何运转》动画品质
核心升级: 柱廊建筑 + 山墙 + 台阶 + 暖色调 + 多层投影
"""
import math, os, xml.etree.ElementTree as ET

OUT = "D:/Desktop/每日财经/2026-06-17/wechat-publish/evening/comic"
os.makedirs(OUT, exist_ok=True)

W, H = 768, 512

# ===== 共用定义 =====

def svg_header():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Microsoft YaHei, SimHei, PingFang SC, sans-serif">\n'

DEFS = '''  <defs>
    <filter id="soft"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#3D3222" flood-opacity="0.12"/></filter>
    <filter id="med"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#3D3222" flood-opacity="0.16"/></filter>
    <filter id="deep"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#3D3222" flood-opacity="0.20"/></filter>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FBF9F4"/><stop offset="100%" stop-color="#F4EFE6"/></linearGradient>
    <linearGradient id="bldg-warm" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FDF6EE"/><stop offset="100%" stop-color="#F5E6D3"/></linearGradient>
    <linearGradient id="bldg-cool" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#F0F4F8"/><stop offset="100%" stop-color="#DCE4EE"/></linearGradient>
    <linearGradient id="roof-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#D4A017"/><stop offset="100%" stop-color="#B8860B"/></linearGradient>
    <linearGradient id="roof-slate" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#475569"/><stop offset="100%" stop-color="#334155"/></linearGradient>
    <linearGradient id="roof-red" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#DC2626"/><stop offset="100%" stop-color="#991B1B"/></linearGradient>
    <linearGradient id="gold-bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#FDE68A"/><stop offset="50%" stop-color="#FEF3C7"/><stop offset="100%" stop-color="#FDE68A"/></linearGradient>
    <linearGradient id="rocket-body" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#FEF2F2"/><stop offset="40%" stop-color="#FEE2E2"/><stop offset="100%" stop-color="#FECACA"/></linearGradient>
    <linearGradient id="flame" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FEE2E2"/><stop offset="35%" stop-color="#FCA5A5"/><stop offset="70%" stop-color="#EF4444"/><stop offset="100%" stop-color="#DC2626"/></linearGradient>
    <linearGradient id="oil-well" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#475569"/><stop offset="100%" stop-color="#1E293B"/></linearGradient>
    <linearGradient id="gold-vault" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FEF3C7"/><stop offset="100%" stop-color="#FDE68A"/></linearGradient>
    <marker id="ar" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#DC2626"/></marker>
    <marker id="ag" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#16A34A"/></marker>
    <marker id="agold" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#D4A017"/></marker>
    <marker id="ablue" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#1A56DB"/></marker>
  </defs>\n'''

def svg_footer():
    return '</svg>'

def bg_rect():
    return '<rect width="768" height="512" fill="url(#sky)"/>\n'

def title_bar(text, color="#D4A017"):
    return (f'  <rect x="0" y="0" width="768" height="42" fill="{color}" opacity="0.06"/>\n'
            f'  <line x1="0" y1="42" x2="768" y2="42" stroke="{color}" stroke-width="0.5" opacity="0.2"/>\n'
            f'  <text x="384" y="28" font-size="16" fill="#8B6914" text-anchor="middle" font-weight="bold" letter-spacing="0.5">{text}</text>\n')

def footnote(text, y=506):
    return f'  <text x="384" y="{y}" font-size="9" fill="#A8A49A" text-anchor="middle">{text}</text>\n'

def label(x, y, text, size=12, color="#334155", anchor="middle", bold=False):
    w = "bold" if bold else "normal"
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{w}">{text}</text>'

def badge(cx, y, w, h, text, text_color="#DC2626", bg="white", stroke="#FCA5A5", size=11):
    parts = f'<rect x="{cx-w/2}" y="{y}" width="{w}" height="{h}" rx="6" fill="{bg}" stroke="{stroke}" stroke-width="1.5" filter="url(#soft)"/>\n'
    parts += f'  <text x="{cx}" y="{y+h/2+4}" font-size="{size}" fill="{text_color}" text-anchor="middle" font-weight="bold">{text}</text>'
    return parts

def gear_chain(items, y, start_x=60, end_x=708):
    """items: list of (text, color, fill_color)"""
    parts = ''
    n = len(items)
    spacing = (end_x - start_x) / (n - 1)
    r = 16
    for i, (txt, clr, fclr) in enumerate(items):
        cx = start_x + i * spacing
        parts += f'  <g filter="url(#soft)">\n'
        parts += f'    <circle cx="{cx}" cy="{y}" r="{r}" fill="{fclr}" stroke="{clr}" stroke-width="2.5"/>\n'
        parts += f'    <circle cx="{cx}" cy="{y}" r="{r*0.45}" fill="none" stroke="{clr}" stroke-width="1.2"/>\n'
        parts += f'    <circle cx="{cx}" cy="{y}" r="3" fill="{clr}"/>\n'
        parts += f'  </g>\n'
        parts += f'  <text x="{cx}" y="{y+28}" font-size="9" fill="{clr}" text-anchor="middle" font-weight="bold">{txt}</text>\n'
        if i < n - 1:
            nx = start_x + (i + 1) * spacing
            parts += f'  <line x1="{cx+r+4}" y1="{y}" x2="{nx-r-4}" y2="{y}" stroke="{clr}" stroke-width="2" marker-end="url(#agold)"/>\n'
    return parts

# ===== 建筑组件 =====

def building_classical(cx, by, w, h, roof_color_grad, body_grad, stroke_color, n_cols, has_clock=False):
    """古典建筑: 台阶+柱廊+山墙+门窗"""
    parts = ''
    half_w = w / 2
    top_y = by - h
    # 3级台阶
    for i, (sw, sh, sc) in enumerate([(w+30,8,"#E2DDD0"), (w+16,8,"#EDE9E0"), (w+4,8,"#F5F2EC")]):
        parts += f'  <rect x="{cx-half_w-sw/2}" y="{by+i*8}" width="{sw}" height="{sh}" rx="2" fill="{sc}" stroke="{stroke_color}" stroke-width="0.8" opacity="0.6"/>\n'
    # 主体
    parts += f'  <rect x="{cx-half_w}" y="{by+24-w-h}" width="{w}" height="{h}" rx="3" fill="url(#{body_grad})" stroke="{stroke_color}" stroke-width="2"/>\n'
    # 山墙
    ped_h = 65
    parts += f'  <polygon points="{cx-half_w},{by+24-w-h} {cx},{by+24-w-h-ped_h} {cx+half_w},{by+24-w-h}" fill="url(#{roof_color_grad})" stroke="{stroke_color}" stroke-width="2" stroke-linejoin="round"/>\n'
    parts += f'  <line x1="{cx-half_w}" y1="{by+24-w-h}" x2="{cx+half_w}" y2="{by+24-w-h}" stroke="{stroke_color}" stroke-width="2"/>\n'
    # 山墙圆窗/时钟
    ped_cy = by + 24 - w - h - ped_h/2 + 5
    if has_clock:
        parts += f'  <circle cx="{cx}" cy="{ped_cy}" r="14" fill="white" stroke="#475569" stroke-width="2"/>\n'
        parts += f'  <circle cx="{cx}" cy="{ped_cy}" r="2" fill="#475569"/>\n'
        parts += f'  <line x1="{cx}" y1="{ped_cy}" x2="{cx}" y2="{ped_cy-10}" stroke="#475569" stroke-width="2" stroke-linecap="round"/>\n'
        parts += f'  <line x1="{cx}" y1="{ped_cy}" x2="{cx+6}" y2="{ped_cy+4}" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>\n'
    else:
        parts += f'  <circle cx="{cx}" cy="{ped_cy}" r="10" fill="#FFFDF7" stroke="{stroke_color}" stroke-width="1.5"/>\n'
        parts += f'  <line x1="{cx}" y1="{ped_cy-8}" x2="{cx}" y2="{ped_cy+8}" stroke="{stroke_color}" stroke-width="0.8" opacity="0.3"/>\n'
        parts += f'  <line x1="{cx-8}" y1="{ped_cy}" x2="{cx+8}" y2="{ped_cy}" stroke="{stroke_color}" stroke-width="0.8" opacity="0.3"/>\n'
    # 柱廊
    col_w = 7 if n_cols >= 5 else 8
    col_start_x = cx - (n_cols * (col_w + 14)) / 2 + 7
    roof_bot = by + 24 - w - h
    col_top = roof_bot + 30
    col_bot = by + 24 - 4
    for i in range(n_cols):
        cx_col = col_start_x + i * (col_w + 14)
        parts += f'  <rect x="{cx_col}" y="{col_top}" width="{col_w}" height="{col_bot-col_top}" fill="#FDF8F0" stroke="{stroke_color}" stroke-width="1.5" opacity="0.9"/>\n'
        parts += f'  <rect x="{cx_col-3}" y="{col_top-4}" width="{col_w+6}" height="5" rx="1" fill="#E8D5B7" stroke="{stroke_color}" stroke-width="1" opacity="0.8"/>\n'
    # 大门
    door_w, door_h = min(40, w*0.3), h * 0.38
    parts += f'  <rect x="{cx-door_w/2}" y="{by+24-door_h}" width="{door_w}" height="{door_h}" rx="3" fill="{stroke_color}" stroke="{stroke_color}" stroke-width="1.5" opacity="0.7"/>\n'
    parts += f'  <rect x="{cx-door_w/2+6}" y="{by+24-door_h+6}" width="{door_w-12}" height="{door_h*0.4}" rx="1" fill="#FDF8F0" stroke="{stroke_color}" stroke-width="1"/>\n'
    parts += f'  <rect x="{cx-door_w/2+6}" y="{by+24-door_h*0.6+4}" width="{door_w-12}" height="{door_h*0.3}" rx="1" fill="#FDF8F0" stroke="{stroke_color}" stroke-width="1"/>\n'
    # 侧面窗户 (各1个)
    win_w, win_h = 16, 20
    for side in [-1, 1]:
        wx = cx + side * (w*0.32)
        parts += f'  <rect x="{wx-win_w/2}" y="{col_top+10}" width="{win_w}" height="{win_h}" rx="2" fill="#FFFDF7" stroke="{stroke_color}" stroke-width="1" opacity="0.8"/>\n'
        parts += f'  <line x1="{wx}" y1="{col_top+10}" x2="{wx}" y2="{col_top+10+win_h}" stroke="{stroke_color}" stroke-width="0.5" opacity="0.3"/>\n'
    return parts

def arrow_line(x1, y1, x2, y2, color="#DC2626", marker="ar", sw=2.5):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" marker-end="url(#{marker})"/>\n'

def up_arrow(cx, top_y, bot_y, color="#DC2626"):
    return (f'<polygon points="{cx-8},{top_y+12} {cx},{top_y} {cx+8},{top_y+12}" fill="{color}"/>\n'
            f'<line x1="{cx}" y1="{top_y+10}" x2="{cx}" y2="{bot_y}" stroke="{color}" stroke-width="2.5" marker-end="url(#ar)"/>\n')

def down_arrow(cx, top_y, bot_y, color="#16A34A"):
    return (f'<polygon points="{cx-8},{bot_y-12} {cx},{bot_y} {cx+8},{bot_y-12}" fill="{color}"/>\n'
            f'<line x1="{cx}" y1="{top_y}" x2="{cx}" y2="{bot_y-8}" stroke="{color}" stroke-width="2.5" marker-end="url(#ag)"/>\n')


# ============================================================
# 6张漫画
# ============================================================

def comic_001_summary():
    """Layer 1: 全景速览 — 上交所+美联储双建筑+天平+传导链"""
    svg = svg_header() + DEFS + bg_rect()
    svg += title_bar("2026年6月17日 · 晚报速览")

    # === 左: 上交所大楼 (科创50暴涨) ===
    svg += '  <g filter="url(#med)">\n'
    svg += building_classical(120, 385, 140, 135, "roof-gold", "bldg-warm", "#C4A97D", 6)
    svg += '  </g>\n'
    # 名牌
    svg += badge(120, 390, 110, 24, "上交所 · 科创50", "#8B6914", "white", "#D4A017", 10)
    # 涨幅标签
    svg += f'  <rect x="33" y="100" width="174" height="44" rx="8" fill="white" stroke="#FCA5A5" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="120" y="118" font-size="11" fill="#991B1B" text-anchor="middle" font-weight="bold">科创50 收盘</text>\n'
    svg += f'  <text x="120" y="137" font-size="17" fill="#DC2626" text-anchor="middle" font-weight="bold">1,840.82 +4.69%</text>\n'
    svg += up_arrow(120, 62, 92, "#DC2626")
    # 半导体标签
    svg += badge(120, 440, 150, 22, "半导体净流入 154亿", "#DC2626", "#FEF2F2", "#FCA5A5", 10)

    # === 右: 美联储大楼 (FOMC) ===
    svg += '  <g filter="url(#med)">\n'
    svg += building_classical(648, 355, 128, 115, "roof-slate", "bldg-cool", "#94A3B8", 4, has_clock=True)
    svg += '  </g>\n'
    svg += badge(648, 360, 116, 24, "美联储 · FOMC", "#334155", "white", "#64748B", 10)
    svg += f'  <rect x="590" y="108" width="116" height="42" rx="8" fill="white" stroke="#FDE68A" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="648" y="125" font-size="11" fill="#8B6914" text-anchor="middle" font-weight="bold">北京时间 凌晨 2:00</text>\n'
    svg += f'  <text x="648" y="142" font-size="13" fill="#DC2626" text-anchor="middle" font-weight="bold">沃什首秀</text>\n'

    # === 中央: 天平 (一九分化) ===
    svg += '  <g filter="url(#deep)">\n'
    svg += f'    <rect x="349" y="370" width="70" height="12" rx="3" fill="#E2DDD0" stroke="#A8A49A" stroke-width="1.5"/>\n'
    svg += f'    <rect x="369" y="382" width="30" height="20" rx="3" fill="#EDE9E0" stroke="#A8A49A" stroke-width="1.5"/>\n'
    svg += f'    <rect x="380" y="240" width="8" height="142" rx="3" fill="#D4CFC2" stroke="#A8A49A" stroke-width="1.5"/>\n'
    svg += f'    <line x1="220" y1="260" x2="548" y2="250" stroke="#5D5A52" stroke-width="4" stroke-linecap="round"/>\n'
    svg += f'    <ellipse cx="234" cy="272" rx="48" ry="14" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="2.5"/>\n'
    svg += f'    <text x="234" y="294" font-size="11" fill="#DC2626" text-anchor="middle" font-weight="bold">科创50 +4.69%</text>\n'
    svg += f'    <ellipse cx="534" cy="262" rx="44" ry="12" fill="#F0FDF4" stroke="#86EFAC" stroke-width="2"/>\n'
    svg += f'    <text x="534" y="280" font-size="11" fill="#16A34A" text-anchor="middle" font-weight="bold">3734只股跌</text>\n'
    svg += '  </g>\n'
    svg += f'  <rect x="328" y="218" width="112" height="30" rx="6" fill="white" stroke="#FCA5A5" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="235" font-size="13" fill="#DC2626" text-anchor="middle" font-weight="bold">一九分化</text>\n'
    svg += f'  <text x="384" y="246" font-size="8" fill="#64748B" text-anchor="middle">涨跌比 1 : 2.2</text>\n'

    # === 底部 齿轮传导链 ===
    svg += f'  <line x1="60" y1="472" x2="708" y2="472" stroke="#D4A017" stroke-width="1" opacity="0.25" stroke-dasharray="4,4"/>\n'
    chain_items = [
        ("陆家嘴论坛", "#D4A017", "#FEF3C7"),
        ("硬科技政策", "#D4A017", "#FEF3C7"),
        ("半导体涨停", "#DC2626", "#FEE2E2"),
        ("3700股下跌", "#16A34A", "#DCFCE7"),
        ("FOMC", "#1A56DB", "#DBEAFE"),
        ("明天方向?", "#D4A017", "#FEF3C7"),
    ]
    svg += gear_chain(chain_items, 472, 60, 700)

    svg += footnote("不是全面牛市，是极致抱团 · FOMC凌晨2:00揭晓")
    svg += svg_footer()
    return svg


def comic_002_ashare():
    """01 A股: 一九分化— 半导体大楼冲天 vs 消费股下沉"""
    svg = svg_header() + DEFS + bg_rect()
    svg += title_bar("A股：科创50暴涨4.69% vs 3734只个股下跌")

    # 左: 上交所(涨)
    svg += '  <g filter="url(#med)">\n'
    svg += building_classical(120, 340, 120, 110, "roof-gold", "bldg-warm", "#C4A97D", 5)
    svg += '  </g>\n'
    svg += badge(120, 348, 100, 22, "科创50 +4.69%", "#DC2626", "#FEF2F2", "#FCA5A5", 10)

    # 上涨火焰(楼顶冲出)
    svg += f'  <polygon points="106,165 120,125 134,165" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>\n'
    svg += up_arrow(120, 85, 155, "#DC2626")

    # 半导体标签组
    for i, (txt, yy) in enumerate([("盛美上海 20CM涨停", 368), ("普冉股份 20CM涨停", 384), ("兆易创新 涨停·4100亿+", 400)]):
        svg += f'  <rect x="28" y="{yy}" width="184" height="14" rx="3" fill="#FEF2F2" stroke="#FECACA" stroke-width="0.8"/>\n'
        svg += f'  <text x="120" y="{yy+10}" font-size="9" fill="#DC2626" text-anchor="middle" font-weight="bold">{txt}</text>\n'

    # 中: 裂谷
    svg += f'  <line x1="260" y1="80" x2="500" y2="80" stroke="#DC2626" stroke-width="1" stroke-dasharray="6,4" opacity="0.4"/>\n'
    svg += f'  <text x="384" y="72" font-size="10" fill="#DC2626" text-anchor="middle" font-weight="bold">"一九分化"裂谷</text>\n'

    # 右: 下沉区(消费/汽车)
    svg += f'  <rect x="520" y="100" width="220" height="210" rx="10" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.5" opacity="0.5"/>\n'
    svg += f'  <text x="630" y="122" font-size="12" fill="#16A34A" text-anchor="middle" font-weight="bold">被抛弃的板块</text>\n'
    sinking = [("白酒", 520, 148, "#16A34A"), ("汽车", 600, 160, "#16A34A"), ("煤炭", 540, 178, "#16A34A"),
               ("钢铁", 620, 192, "#16A34A"), ("商贸", 560, 210, "#16A34A"), ("零售", 640, 222, "#16A34A")]
    for txt, sx, sy, sc in sinking:
        svg += f'  <ellipse cx="{sx}" cy="{sy}" rx="36" ry="12" fill="#DCFCE7" stroke="{sc}" stroke-width="1.5" opacity="0.7"/>\n'
        svg += f'  <text x="{sx}" y="{sy+4}" font-size="9" fill="{sc}" text-anchor="middle">{txt}</text>\n'

    svg += f'  <rect x="530" y="250" width="200" height="52" rx="8" fill="white" stroke="#86EFAC" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="630" y="270" font-size="12" fill="#166534" text-anchor="middle" font-weight="bold">3734只个股下跌</text>\n'
    svg += f'  <text x="630" y="288" font-size="10" fill="#166534" text-anchor="middle">中位数 -1.19% · 涨跌比 1:2.2</text>\n'

    # 裂谷两侧箭头
    svg += arrow_line(250, 70, 320, 70, "#DC2626", "ar", 2)
    svg += arrow_line(450, 70, 380, 70, "#16A34A", "ag", 2)

    # 底部: 政策驱动
    svg += f'  <rect x="60" y="420" width="650" height="44" rx="8" fill="#FFF8E7" stroke="#D4A017" stroke-width="2" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="440" font-size="12" fill="#92400E" text-anchor="middle" font-weight="bold">催化剂：陆家嘴论坛 — 科创板第五套标准扩至AI大模型</text>\n'
    svg += f'  <text x="384" y="456" font-size="10" fill="#B8860B" text-anchor="middle">"硬科技" 从产业概念变为政策意志 → "卖铲子给淘金者"</text>\n'

    svg += footnote("一九分化≠健康牛市。上涨广度越窄，抱团松动时回调越剧烈")
    svg += svg_footer()
    return svg


def comic_003_spacex():
    """03 科技: SpaceX火箭 vs 其他科技股下沉 + 科创板政策"""
    svg = svg_header() + DEFS + bg_rect()
    svg += title_bar("科技：SpaceX一枝独秀 vs 科技板块集体下沉")

    # 地面线
    svg += f'  <line x1="30" y1="380" x2="738" y2="380" stroke="#CBD5E1" stroke-width="1.5"/>\n'

    # 中央: SpaceX火箭
    svg += '  <g filter="url(#med)">\n'
    # 火箭主体
    svg += f'    <ellipse cx="384" cy="230" rx="32" ry="90" fill="url(#rocket-body)" stroke="#DC2626" stroke-width="2.5"/>\n'
    # 头部
    svg += f'    <path d="M352,145 Q352,105 384,95 Q416,105 416,145" fill="#FEF2F2" stroke="#DC2626" stroke-width="2.5" stroke-linejoin="round"/>\n'
    # 舷窗
    svg += f'    <circle cx="384" cy="200" r="11" fill="#DBEAFE" stroke="#1A56DB" stroke-width="2"/>\n'
    svg += f'    <circle cx="384" cy="200" r="5" fill="#93C5FD" opacity="0.8"/>\n'
    # 机翼
    svg += f'    <path d="M352,260 L330,290 L330,278 L352,272 Z" fill="#FECACA" stroke="#DC2626" stroke-width="2" stroke-linejoin="round"/>\n'
    svg += f'    <path d="M416,260 L438,290 L438,278 L416,272 Z" fill="#FECACA" stroke="#DC2626" stroke-width="2" stroke-linejoin="round"/>\n'
    # 火焰
    svg += f'    <path d="M360,316 Q358,355 384,382 Q410,355 408,316" fill="url(#flame)" opacity="0.85"/>\n'
    svg += f'    <path d="M368,316 Q370,345 384,362 Q398,345 400,316" fill="#FEF2F2" opacity="0.5"/>\n'
    svg += '  </g>\n'
    # 标签
    svg += f'  <rect x="319" y="68" width="130" height="42" rx="8" fill="white" stroke="#FCA5A5" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="85" font-size="11" fill="#991B1B" text-anchor="middle" font-weight="bold">SpaceX $2.66万亿</text>\n'
    svg += f'  <text x="384" y="102" font-size="13" fill="#DC2626" text-anchor="middle" font-weight="bold">超越亚马逊 +50%</text>\n'

    # 估值皮筋(顶部拉伸)
    svg += f'  <path d="M384,95 Q250,40 180,160" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="8,5"/>\n'
    svg += f'  <text x="250" y="65" font-size="9" fill="#F59E0B" text-anchor="middle" font-weight="bold">估值皮筋拉伸中</text>\n'

    # 周围下沉科技股
    sinking = [("费半 -5.7%", 140, 390, "#DC2626"), ("英伟达 -2%", 250, 395, "#DC2626"),
               ("Meta -2.8%", 520, 395, "#DC2626"), ("AMD -7.3%", 630, 390, "#DC2626")]
    for txt, sx, sy, sc in sinking:
        svg += f'  <ellipse cx="{sx}" cy="{sy}" rx="42" ry="14" fill="#FEF2F2" stroke="{sc}" stroke-width="1.5"/>\n'
        svg += f'  <text x="{sx}" y="{sy+4}" font-size="9" fill="{sc}" text-anchor="middle" font-weight="bold">{txt}</text>\n'

    # 科创板政策
    svg += f'  <rect x="140" y="420" width="490" height="42" rx="8" fill="#FFF8E7" stroke="#D4A017" stroke-width="2" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="440" font-size="11" fill="#92400E" text-anchor="middle" font-weight="bold">科创板第五套标准扩至AI大模型 — 不盈利也能上市融资</text>\n'
    svg += f'  <text x="384" y="456" font-size="9" fill="#B8860B" text-anchor="middle">"卖铲子给淘金者" — 已上市半导体公司 = AI公司的供应链核心</text>\n'

    svg += footnote("一边是SpaceX估值皮筋越拉越紧，一边是A股硬科技制度红利刚刚开始")
    svg += svg_footer()
    return svg


def comic_004_fomc():
    """05 宏观: FOMC — 美联储大楼 + 三岔路 + 时钟"""
    svg = svg_header() + DEFS + bg_rect()
    svg += title_bar("FOMC倒计时：沃什首秀 · 三岔路口 · 全球屏息")

    # 美联储大楼(中央)
    svg += '  <g filter="url(#deep)">\n'
    svg += building_classical(384, 280, 110, 100, "roof-slate", "bldg-cool", "#64748B", 4, has_clock=True)
    svg += '  </g>\n'
    svg += badge(384, 288, 100, 22, "FOMC · 美联储", "#334155", "white", "#64748B", 10)

    # 顶部时钟
    svg += f'  <rect x="660" y="56" width="90" height="44" rx="8" fill="white" stroke="#FDE68A" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="705" y="74" font-size="10" fill="#8B6914" text-anchor="middle" font-weight="bold">北京时间</text>\n'
    svg += f'  <text x="705" y="93" font-size="14" fill="#DC2626" text-anchor="middle" font-weight="bold">凌晨 2:00</text>\n'

    # 沃什小人(楼前)
    svg += f'  <circle cx="384" cy="265" r="9" fill="#E2E8F0" stroke="#475569" stroke-width="2"/>\n'
    svg += f'  <polygon points="374,276 394,276 398,292 370,292" fill="#EFF6FF" stroke="#475569" stroke-width="2" stroke-linejoin="round"/>\n'
    svg += f'  <line x1="374" y1="280" x2="360" y2="272" stroke="#475569" stroke-width="2" stroke-linecap="round"/>\n'
    svg += f'  <line x1="394" y1="280" x2="408" y2="275" stroke="#475569" stroke-width="2" stroke-linecap="round"/>\n'
    svg += f'  <line x1="378" y1="292" x2="375" y2="304" stroke="#475569" stroke-width="2.5" stroke-linecap="round"/>\n'
    svg += f'  <line x1="390" y1="292" x2="393" y2="304" stroke="#475569" stroke-width="2.5" stroke-linecap="round"/>\n'
    svg += f'  <text x="384" y="316" font-size="9" fill="#475569" text-anchor="middle" font-weight="bold">沃什</text>\n'

    # 分叉点
    split_x, split_y = 384, 350
    svg += f'  <circle cx="{split_x}" cy="{split_y}" r="5" fill="#D4A017"/>\n'

    # 三岔路
    # 左: 鸽派
    svg += arrow_line(split_x-3, split_y+3, 180, 420, "#16A34A", "ag", 3)
    svg += f'  <rect x="70" y="400" width="180" height="72" rx="10" fill="#F0FDF4" stroke="#86EFAC" stroke-width="2" filter="url(#soft)"/>\n'
    svg += f'  <text x="160" y="422" font-size="13" fill="#16A34A" text-anchor="middle" font-weight="bold">鸽派情景</text>\n'
    svg += f'  <text x="160" y="440" font-size="10" fill="#166534" text-anchor="middle">沃什留白 + 宽松保留</text>\n'
    svg += f'  <text x="160" y="456" font-size="10" fill="#166534" text-anchor="middle">→ A股高开 · 半导体继续涨</text>\n'
    svg += f'  <text x="160" y="470" font-size="9" fill="#16A34A" text-anchor="middle">科创50 → 1900?</text>\n'

    # 右下: 鹰派
    svg += arrow_line(split_x+3, split_y+3, 600, 420, "#DC2626", "ar", 3)
    svg += f'  <rect x="520" y="400" width="180" height="72" rx="10" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="2" filter="url(#soft)"/>\n'
    svg += f'  <text x="610" y="422" font-size="13" fill="#DC2626" text-anchor="middle" font-weight="bold">鹰派情景</text>\n'
    svg += f'  <text x="610" y="440" font-size="10" fill="#991B1B" text-anchor="middle">删除宽松 + 暗示加息</text>\n'
    svg += f'  <text x="610" y="456" font-size="10" fill="#991B1B" text-anchor="middle">→ A股低开 · 半导体回吐</text>\n'
    svg += f'  <text x="610" y="470" font-size="9" fill="#DC2626" text-anchor="middle">沪指 → 4050?</text>\n'

    # 中下: 中性
    svg += arrow_line(split_x, split_y+5, 384, 490, "#D4A017", "agold", 3)
    svg += f'  <rect x="294" y="474" width="180" height="32" rx="8" fill="#FFF8E7" stroke="#FDE68A" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="494" font-size="11" fill="#92400E" text-anchor="middle" font-weight="bold">中性 · 窄幅震荡等催化剂</text>\n'

    # 顶部: 三大悬念
    svg += f'  <rect x="28" y="70" width="160" height="72" rx="8" fill="white" stroke="#CBD5E1" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="108" y="90" font-size="11" fill="#475569" text-anchor="middle" font-weight="bold">三大悬念</text>\n'
    svg += f'  <text x="108" y="106" font-size="9" fill="#64748B" text-anchor="middle">1. 点阵图加息?</text>\n'
    svg += f'  <text x="108" y="120" font-size="9" fill="#64748B" text-anchor="middle">2. 沃什"留白"?</text>\n'
    svg += f'  <text x="108" y="134" font-size="9" fill="#64748B" text-anchor="middle">3. 宽松措辞删除?</text>\n'

    svg += footnote("最佳策略不是预测结果——而是准备好应对三种结果")
    svg += svg_footer()
    return svg


def comic_005_commodity():
    """06 商品: 油价下跌煤矿+黄金金库拱顶"""
    svg = svg_header() + DEFS + bg_rect()
    svg += title_bar("商品：油价三日暴跌 · 黄金横盘等FOMC选方向")

    # 左: 油井架(下跌)
    # 油井架结构
    svg += '  <g filter="url(#med)">\n'
    derrick_x, derrick_top, derrick_bot = 150, 100, 340
    dw = 80
    svg += f'    <line x1="{derrick_x-dw/2}" y1="{derrick_bot}" x2="{derrick_x-6}" y2="{derrick_top}" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>\n'
    svg += f'    <line x1="{derrick_x+dw/2}" y1="{derrick_bot}" x2="{derrick_x+6}" y2="{derrick_top}" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>\n'
    # 横梁
    for yb in [280, 220, 160]:
        ratio = (yb - derrick_top) / (derrick_bot - derrick_top)
        lx = (derrick_x - dw/2) + (dw/2 - 6) * ratio
        rx = (derrick_x + dw/2) - (dw/2 - 6) * ratio
        svg += f'    <line x1="{lx}" y1="{yb}" x2="{rx}" y2="{yb}" stroke="#94A3B8" stroke-width="2"/>\n'
    # 顶部横梁+滑轮
    svg += f'    <line x1="{derrick_x-6}" y1="{derrick_top}" x2="{derrick_x+6}" y2="{derrick_top}" stroke="#475569" stroke-width="3"/>\n'
    svg += f'    <circle cx="{derrick_x}" cy="{derrick_top}" r="4" fill="#475569"/>\n'
    svg += f'    <line x1="{derrick_x}" y1="{derrick_top+4}" x2="{derrick_x}" y2="260" stroke="#64748B" stroke-width="1.5"/>\n'
    # 油桶
    svg += f'    <rect x="{derrick_x-16}" y="260" width="32" height="24" rx="5" fill="#FEF3C7" stroke="#EA580C" stroke-width="2"/>\n'
    svg += f'    <text x="{derrick_x}" y="276" font-size="10" fill="#EA580C" text-anchor="middle" font-weight="bold">油</text>\n'
    svg += '  </g>\n'

    # 油价下跌标签
    svg += f'  <rect x="38" y="348" width="224" height="76" rx="8" fill="white" stroke="#FED7AA" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="150" y="368" font-size="11" fill="#EA580C" text-anchor="middle" font-weight="bold">WTI 三日暴跌</text>\n'
    svg += f'  <text x="150" y="388" font-size="14" fill="#DC2626" text-anchor="middle" font-weight="bold">$95 → $81 → $74.80</text>\n'
    svg += f'  <text x="150" y="406" font-size="10" fill="#991B1B" text-anchor="middle">三日累计跌超$6 · 入技术性熊市</text>\n'
    svg += f'  <text x="150" y="420" font-size="9" fill="#64748B" text-anchor="middle">美伊和平协议挤出"战争溢价"</text>\n'

    # 右: 黄金金库拱顶(横盘)
    svg += '  <g filter="url(#med)">\n'
    # 拱顶建筑
    vault_cx, vault_y = 570, 240
    svg += f'    <rect x="{vault_cx-60}" y="{vault_y}" width="120" height="90" rx="5" fill="url(#bldg-cool)" stroke="#94A3B8" stroke-width="2.5"/>\n'
    # 拱形屋顶
    svg += f'    <path d="M{vault_cx-60},{vault_y} Q{vault_cx},{vault_y-55} {vault_cx+60},{vault_y}" fill="url(#gold-vault)" stroke="#D4A017" stroke-width="2.5"/>\n'
    # 金砖堆
    svg += f'    <rect x="{vault_cx-25}" y="{vault_y+15}" width="22" height="14" rx="2" fill="#FDE68A" stroke="#D4A017" stroke-width="1.5"/>\n'
    svg += f'    <rect x="{vault_cx-25}" y="{vault_y+5}" width="22" height="12" rx="2" fill="#FEF3C7" stroke="#D4A017" stroke-width="1.5"/>\n'
    svg += f'    <rect x="{vault_cx+3}" y="{vault_y+10}" width="22" height="19" rx="2" fill="#FDE68A" stroke="#D4A017" stroke-width="1.5"/>\n'
    svg += f'    <text x="{vault_cx}" y="{vault_y+60}" font-size="10" fill="#D4A017" text-anchor="middle" font-weight="bold">$ 金库</text>\n'
    svg += '  </g>\n'

    svg += f'  <rect x="460" y="340" width="220" height="76" rx="8" fill="white" stroke="#FDE68A" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="570" y="360" font-size="11" fill="#D4A017" text-anchor="middle" font-weight="bold">现货黄金 横盘</text>\n'
    svg += f'  <text x="570" y="380" font-size="14" fill="#B8860B" text-anchor="middle" font-weight="bold">$4,310 - $4,340</text>\n'
    svg += f'  <text x="570" y="398" font-size="10" fill="#64748B" text-anchor="middle">三重均衡：油价↓通胀↓ / DXY弱 / FOMC?</text>\n'
    svg += f'  <text x="570" y="414" font-size="9" fill="#B8860B" text-anchor="middle">横盘越久，突破后趋势越强</text>\n'

    # FOMC方向选择(底部)
    svg += f'  <rect x="120" y="440" width="530" height="36" rx="8" fill="#FFF8E7" stroke="#D4A017" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="462" font-size="11" fill="#92400E" text-anchor="middle" font-weight="bold">FOMC后：鸽派 → 黄金 $4,400 ↑ ｜ 鹰派 → 黄金 $4,200 ↓</text>\n'

    svg += footnote("FOMC打破三重均衡 — 黄金横盘时的方向选择往往是趋势性的")
    svg += svg_footer()
    return svg


def comic_006_boj():
    """04 国际: BOJ旋钮悖论 + 日银大楼"""
    svg = svg_header() + DEFS + bg_rect()
    svg += title_bar("国际：BOJ加息至1% · 日元为何不涨反疲？")

    # 左: 日银大楼
    svg += '  <g filter="url(#med)">\n'
    # 简化日银风格
    svg += f'    <rect x="60" y="240" width="110" height="110" rx="3" fill="url(#bldg-warm)" stroke="#C4A97D" stroke-width="2"/>\n'
    svg += f'    <polygon points="60,240 115,190 170,240" fill="url(#roof-gold)" stroke="#B8860B" stroke-width="2" stroke-linejoin="round"/>\n'
    svg += f'    <circle cx="115" cy="218" r="8" fill="#FFFDF7" stroke="#B8860B" stroke-width="1.5"/>\n'
    # 柱子
    for ci in [72, 92, 112, 132, 152]:
        svg += f'    <rect x="{ci}" y="260" width="6" height="90" fill="#FDF8F0" stroke="#D4B896" stroke-width="1.2"/>\n'
    # 门
    svg += f'    <rect x="96" y="310" width="38" height="40" rx="3" fill="#8B6914" stroke="#6B4F10" stroke-width="1.5" opacity="0.7"/>\n'
    svg += f'    <rect x="103" y="316" width="24" height="16" rx="1" fill="#FDF8F0" stroke="#6B4F10" stroke-width="1"/>\n'
    svg += f'    <rect x="103" y="336" width="24" height="10" rx="1" fill="#FDF8F0" stroke="#6B4F10" stroke-width="1"/>\n'
    svg += '  </g>\n'
    svg += badge(115, 358, 90, 22, "日本央行", "#8B6914", "white", "#D4A017", 10)

    # BOJ旋钮(上调到1%)
    svg += f'  <g filter="url(#soft)">\n'
    svg += f'    <circle cx="115" cy="140" r="38" fill="white" stroke="#1A56DB" stroke-width="3"/>\n'
    # 刻度
    for i in range(8):
        a = -2.2 + i * 2.5 / 7
        ix, iy = 115 + 30 * math.cos(a), 140 + 30 * math.sin(a)
        ox, oy = 115 + 35 * math.cos(a), 140 + 35 * math.sin(a)
        svg += f'    <line x1="{ix}" y1="{iy}" x2="{ox}" y2="{oy}" stroke="#93C5FD" stroke-width="1.5"/>\n'
    # 指针(指向1%)
    pa = -2.2 + 2.5 * 0.75
    px, py = 115 + 28 * math.cos(pa), 140 + 28 * math.sin(pa)
    svg += f'    <line x1="115" y1="140" x2="{px}" y2="{py}" stroke="#DC2626" stroke-width="3" stroke-linecap="round"/>\n'
    svg += f'    <circle cx="115" cy="140" r="4" fill="#DC2626"/>\n'
    svg += '  </g>\n'
    svg += f'  <text x="115" y="195" font-size="12" fill="#1A56DB" text-anchor="middle" font-weight="bold">利率↑ 至 1%</text>\n'
    svg += f'  <text x="115" y="210" font-size="9" fill="#64748B" text-anchor="middle">31年最高利率</text>\n'

    # 理论箭头: 加息→日元升(预期)
    svg += arrow_line(155, 140, 220, 115, "#1A56DB", "ablue", 2.5)
    svg += f'  <text x="200" y="108" font-size="9" fill="#1A56DB" text-anchor="middle">理论: 日元应升值</text>\n'

    # 实际: 日元贬
    svg += f'  <rect x="240" y="130" width="160" height="80" rx="8" fill="#FEF2F2" stroke="#FCA5A5" stroke-width="2" filter="url(#soft)"/>\n'
    svg += f'  <text x="320" y="154" font-size="11" fill="#DC2626" text-anchor="middle" font-weight="bold">实际: 美元/日元</text>\n'
    svg += f'  <text x="320" y="176" font-size="18" fill="#DC2626" text-anchor="middle" font-weight="bold">160.40</text>\n'
    svg += f'  <text x="320" y="196" font-size="10" fill="#991B1B" text-anchor="middle">日元没涨,反而疲软!</text>\n'

    # 交叉矛盾
    svg += arrow_line(280, 128, 320, 122, "#DC2626", "ar", 2)

    # 底部解释
    svg += f'  <rect x="60" y="400" width="650" height="68" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" filter="url(#soft)"/>\n'
    svg += f'  <text x="384" y="420" font-size="12" fill="#475569" text-anchor="middle" font-weight="bold">为什么加息了日元还不涨？</text>\n'
    svg += f'  <text x="200" y="444" font-size="11" fill="#DC2626" text-anchor="middle" font-weight="bold">实际利率 = 1% − 2%通胀 = −1%</text>\n'
    svg += f'  <text x="500" y="444" font-size="11" fill="#DC2626" text-anchor="middle" font-weight="bold">日美利差 ≈ 250bp+ 仍巨大</text>\n'
    svg += f'  <text x="384" y="462" font-size="9" fill="#64748B" text-anchor="middle">"借日元买全球" 套利成本从0.75%→1% —— 结构完全没变</text>\n'

    svg += footnote("加息≠货币走强 — 实际利率和利差才是真正的驱动力")
    svg += svg_footer()
    return svg


# ============================================================
# 生成
# ============================================================
comics = [
    ("panel-001", comic_001_summary, "全景速览"),
    ("panel-002", comic_002_ashare, "A股一九分化"),
    ("panel-003", comic_003_spacex, "科技SpaceX"),
    ("panel-004", comic_004_fomc, "FOMC三岔路"),
    ("panel-005", comic_005_commodity, "商品油价黄金"),
    ("panel-006", comic_006_boj, "国际BOJ悖论"),
]

for fname, fn, desc in comics:
    svg = fn()
    path = os.path.join(OUT, f"{fname}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    size_kb = len(svg.encode("utf-8")) / 1024
    # Quick validation
    try:
        ET.parse(path)
        xml_ok = "OK"
    except:
        xml_ok = "XML_FAIL"
    print(f"  {fname}.svg ({desc}): {size_kb:.1f}KB [{xml_ok}]")

print(f"\n全部 6 张漫画已生成到 {OUT}")
