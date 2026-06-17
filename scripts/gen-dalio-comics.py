"""
扬说财经 · Dalio 简笔科普漫画生成器 v2.0
============================================
对标 Ray Dalio《经济机器是如何运行的》
核心理念：简笔小人 + 具体物件 + 白底 + 清晰标注 = 一眼就懂

使用方式：
  1. 复制本文件到 gen-comics-{日期}.py
  2. 读取 article.html 提取当日6故事
  3. 每故事填写「三个一」隐喻设计
  4. 实现对应的 comic_01() ~ comic_06()
  5. 运行 python gen-comics-{日期}.py

质量标准：见 docs/workflow/DALIO_COMIC_STANDARD.md
"""
import math, os, sys

# ============================================================
# 全局配置
# ============================================================

# 输出目录（由调用者覆盖）
DATE = "2026-06-16"
EDITION = "morning"  # morning | evening
OUT = f"D:/Desktop/每日财经/{DATE}/wechat-publish/{EDITION}/comic"

# ============================================================
# 配色体系
# ============================================================

# 版次主色
if EDITION == "morning":
    ACCENT = "#1A56DB"   # 早报蓝
else:
    ACCENT = "#D4A017"   # 晚报金

# 语义色（全版次统一）
RED     = "#DC2626"   # 上涨/风险/热
GREEN   = "#16A34A"   # 下跌/安全/冷
GRAY    = "#475569"   # 文字灰
LIGHT   = "#FAFBFC"   # 背景白
ORANGE  = "#D97706"   # 强调橙
DARK    = "#2C3E50"   # 描边黑

# ============================================================
# 画布规范
# ============================================================
W, H = 768, 512
TITLE_Y = 36
SUMMARY_Y = 465

# ============================================================
# 共用 SVG 组件
# ============================================================

def svg_open(title=""):
    """SVG 头部"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="Microsoft YaHei, SimHei, sans-serif">\n'
        f'  <rect width="{W}" height="{H}" fill="{LIGHT}"/>\n'
        + (f'<text x="{W//2}" y="{TITLE_Y}" font-size="20" fill="{ACCENT}" '
           f'text-anchor="middle" font-weight="bold">{title}</text>\n' if title else "")
    )

def svg_close():
    return '</svg>'

def stick_figure(x, y, h=40, color=None, action="stand"):
    """简笔画小人 — Dalio 标志性元素"""
    if color is None: color = DARK
    parts = []
    # 头
    parts.append(f'<circle cx="{x}" cy="{y-h+8}" r="8" fill="none" stroke="{color}" stroke-width="2.5"/>')
    # 身体
    parts.append(f'<line x1="{x}" y1="{y-h+16}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
    if action == "stand":
        parts.append(f'<line x1="{x}" y1="{y-h+24}" x2="{x-12}" y2="{y-5}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
        parts.append(f'<line x1="{x}" y1="{y-h+24}" x2="{x+12}" y2="{y-5}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
        parts.append(f'<line x1="{x}" y1="{y}" x2="{x-10}" y2="{y+18}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
        parts.append(f'<line x1="{x}" y1="{y}" x2="{x+10}" y2="{y+18}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
    elif action == "arms_up":
        parts.append(f'<line x1="{x}" y1="{y-h+24}" x2="{x-14}" y2="{y-h+10}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
        parts.append(f'<line x1="{x}" y1="{y-h+24}" x2="{x+14}" y2="{y-h+10}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
        parts.append(f'<line x1="{x}" y1="{y}" x2="{x-10}" y2="{y+18}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
        parts.append(f'<line x1="{x}" y1="{y}" x2="{x+10}" y2="{y+18}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
    return '\n  '.join(parts)

def label(x, y, text, size=13, color=None, anchor="middle", bold=False):
    """文字标注"""
    if color is None: color = GRAY
    w = "bold" if bold else "normal"
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{w}">{text}</text>'

def arrow(x1, y1, x2, y2, color=None):
    """带箭头线"""
    if color is None: color = ACCENT
    dx, dy = x2-x1, y2-y1
    L = math.sqrt(dx*dx+dy*dy)
    if L == 0: return ""
    ux, uy = dx/L*8, dy/L*8
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
        f'<polygon points="{x2},{y2} {x2-ux-uy*0.6},{y2-uy+ux*0.6} {x2-ux+uy*0.6},{y2-uy-ux*0.6}" fill="{color}"/>'
    )

def dashed_line(x1, y1, x2, y2, color=None):
    """虚线"""
    if color is None: color = "#94A3B8"
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,4"/>'

def rect_card(x, y, w, h, fill="#F8FAFC", stroke=None, rx=4):
    """圆角矩形卡片"""
    if stroke is None: stroke = ACCENT
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

def double_arrow(x1, y1, x2, y2, color=None):
    """双向箭头"""
    if color is None: color = ACCENT
    return arrow(x1, y1, x2, y2, color) + arrow(x2, y2, x1, y1, color)

# ============================================================
# 6 故事漫画模板（示例 — 每次生产重写此部分）
# ============================================================

def comic_01():
    """A股：一边热火朝天，一边关门歇业"""
    svg = svg_open("A股：一边热火朝天，一边关门歇业")

    # 左侧 — 工厂
    svg += f'<rect x="60" y="100" width="180" height="120" rx="4" fill="#EBF5FF" stroke="{ACCENT}" stroke-width="2.5"/>\n'
    for rx, ry in [(80,120),(140,120),(80,170),(140,170)]:
        svg += f'<rect x="{rx}" y="{ry}" width="40" height="30" fill="#DBEAFE" stroke="{ACCENT}" stroke-width="1.5"/>\n'
    svg += f'<rect x="130" y="55" width="20" height="50" fill="#CBD5E1" stroke="{ACCENT}" stroke-width="2"/>\n'
    for cx, cy, r in [(140,42,10),(155,30,8),(148,18,6)]:
        svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#64748B" stroke-width="1.5"/>\n'
    svg += f'<circle cx="240" cy="140" r="22" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="8,5"/>\n'
    svg += f'<circle cx="240" cy="140" r="6" fill="{ACCENT}"/>\n'
    svg += stick_figure(110, 240, 30, ACCENT, "stand")
    svg += stick_figure(170, 240, 30, ACCENT, "stand")
    svg += label(120, 285, "制造业PMI 52↑", 12, ACCENT)
    svg += label(105, 74, "生产火热", 13, RED, "middle", True)

    # 右侧 — 商场
    svg += f'<rect x="520" y="100" width="180" height="160" rx="4" fill="#FFF5F5" stroke="#EF4444" stroke-width="2.5"/>\n'
    svg += f'<rect x="540" y="120" width="140" height="50" fill="#FEE2E2" stroke="#EF4444" stroke-width="1.5"/>\n'
    for yy in [140,155,165]:
        svg += f'<line x1="550" y1="{yy}" x2="670" y2="{yy}" stroke="#EF4444" stroke-width="1.5"/>\n'
    svg += f'<text x="610" y="145" font-size="22" fill="{RED}" text-anchor="middle">✕</text>\n'
    svg += f'<rect x="540" y="190" width="140" height="40" fill="#FEE2E2" stroke="#EF4444" stroke-width="1.5"/>\n'
    svg += f'<line x1="610" y1="195" x2="610" y2="225" stroke="#EF4444" stroke-width="2"/>\n'
    svg += f'<line x1="595" y1="210" x2="625" y2="210" stroke="#EF4444" stroke-width="2"/>\n'
    svg += label(705, 285, "社零增速3%↓", 12, "#EF4444")
    svg += label(610, 78, "消费低迷", 13, "#EF4444", "middle", True)

    # 中间裂缝
    svg += f'<line x1="375" y1="80" x2="395" y2="280" stroke="{GRAY}" stroke-width="4"/>\n'
    svg += f'<line x1="375" y1="80" x2="370" y2="120" stroke="{GRAY}" stroke-width="3"/>\n'
    for i in range(4):
        svg += f'<line x1="378" y1="{110+i*40}" x2="390" y2="{95+i*40}" stroke="{GRAY}" stroke-width="2"/>\n'

    svg += label(W//2, SUMMARY_Y, "结构性矛盾：生产强 + 消费弱 = 经济冷热不均", 14, GRAY)
    return svg + svg_close()


def comic_02():
    """美股：牛背上的狂欢，前方有悬崖"""
    svg = svg_open("美股：牛背上的狂欢，前方有悬崖")

    # 地面
    svg += f'<line x1="40" y1="360" x2="540" y2="360" stroke="#64748B" stroke-width="2"/>\n'
    # 悬崖
    svg += f'<rect x="530" y="300" width="200" height="65" fill="#F1F5F9" stroke="#64748B" stroke-width="2"/>\n'
    svg += f'<line x1="530" y1="300" x2="530" y2="200" stroke="#64748B" stroke-width="2.5"/>\n'
    svg += f'<line x1="530" y1="200" x2="540" y2="300" stroke="#64748B" stroke-width="2"/>\n'
    for yy in [220,250,280]:
        svg += f'<line x1="530" y1="{yy}" x2="520" y2="{yy+10}" stroke="#94A3B8" stroke-width="1.5"/>\n'
    # FOMC 标牌
    svg += f'<rect x="555" y="340" width="100" height="36" rx="4" fill="#FEF2F2" stroke="{RED}" stroke-width="2"/>\n'
    svg += label(605, 363, "FOMC 加息", 13, RED, "middle", True)

    # 铜牛
    svg += f'<ellipse cx="340" cy="330" rx="120" ry="50" fill="#FFF7ED" stroke="{ORANGE}" stroke-width="3"/>\n'
    svg += f'<ellipse cx="450" cy="300" rx="30" ry="25" fill="#FFF7ED" stroke="{ORANGE}" stroke-width="3"/>\n'
    svg += f'<path d="M455,278 Q465,255 475,260" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>\n'
    svg += f'<path d="M445,278 Q435,255 425,260" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>\n'
    svg += f'<circle cx="455" cy="295" r="3" fill="{ORANGE}"/>\n'
    for lx in [270, 300, 380, 410]:
        svg += f'<line x1="{lx}" y1="370" x2="{lx}" y2="395" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>\n'

    # 狂欢小人
    svg += stick_figure(300, 286, 32, ACCENT, "arms_up")
    svg += stick_figure(340, 280, 32, ACCENT, "arms_up")
    svg += stick_figure(380, 284, 32, ACCENT, "arms_up")
    svg += stick_figure(420, 270, 32, ACCENT, "arms_up")
    svg += label(370, 258, "新高!", 13, RED, "middle", True)

    svg += f'<line x1="480" y1="360" x2="530" y2="360" stroke="#EF4444" stroke-width="1.5" stroke-dasharray="4,4"/>\n'
    svg += label(W//2, SUMMARY_Y, "最大的风险是「觉得自己没有风险」", 14, GRAY)
    return svg + svg_close()


def comic_03():
    """科技：火箭飞上天，基本面还在地上"""
    svg = svg_open("科技：火箭飞上天，基本面还在地上")

    # 地面 + 锚
    svg += f'<line x1="40" y1="390" x2="250" y2="390" stroke="#64748B" stroke-width="2"/>\n'
    svg += f'<polygon points="130,390 150,390 145,370 135,370" fill="#F1F5F9" stroke="{GRAY}" stroke-width="2.5"/>\n'
    svg += label(140, 415, "基本面", 14, GRAY, "middle", True)

    # 皮筋
    svg += f'<path d="M140,370 C140,300 300,280 370,160" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="8,3" stroke-linecap="round"/>\n'
    svg += f'<path d="M140,370 C180,320 320,250 370,160" fill="none" stroke="{ORANGE}" stroke-width="2.5" stroke-dasharray="6,4" stroke-linecap="round"/>\n'

    # 火箭
    svg += f'<ellipse cx="370" cy="140" rx="22" ry="55" fill="#EFF6FF" stroke="{ACCENT}" stroke-width="3"/>\n'
    svg += f'<polygon points="370,72 348,95 392,95" fill="#DBEAFE" stroke="{ACCENT}" stroke-width="3" stroke-linejoin="round"/>\n'
    svg += f'<circle cx="370" cy="120" r="8" fill="#93C5FD" stroke="{ACCENT}" stroke-width="2"/>\n'
    svg += f'<polygon points="348,185 330,205 348,195" fill="#DBEAFE" stroke="{ACCENT}" stroke-width="2"/>\n'
    svg += f'<polygon points="392,185 410,205 392,195" fill="#DBEAFE" stroke="{ACCENT}" stroke-width="2"/>\n'
    svg += f'<polygon points="360,192 370,230 380,192" fill="#FEF2F2" stroke="#EF4444" stroke-width="2"/>\n'
    svg += f'<polygon points="364,192 370,215 376,192" fill="#FEE2E2" stroke="#EF4444" stroke-width="1.5"/>\n'

    # 标注
    svg += label(430, 108, "市值$2.5万亿", 13, RED, "start", True)
    svg += label(430, 128, "5天涨42% ↑", 12, RED, "start")
    arrow(420, 118, 395, 128, RED)

    svg += label(240, 260, "皮筋快断了!", 12, ORANGE, "middle")
    svg += label(W//2, SUMMARY_Y, "估值能领先基本面多远？皮筋拉得太长，一定会弹回来", 14, GRAY)
    return svg + svg_close()


def comic_04():
    """国际：两个温度计，一热一冷"""
    svg = svg_open("国际：两个温度计，一热一冷")

    def thermometer(tx, ty, liquid_h, color, label_text, details, tag, tag_color):
        """画一个温度计"""
        p = []
        p.append(f'<rect x="{tx-18}" y="{ty-180}" width="36" height="190" rx="18" fill="white" stroke="#64748B" stroke-width="2.5"/>')
        p.append(f'<circle cx="{tx}" cy="{ty}" r="24" fill="{color}10" stroke="{color}" stroke-width="2.5"/>')
        p.append(f'<rect x="{tx-8}" y="{ty-liquid_h}" width="16" height="{liquid_h}" rx="8" fill="{color}"/>')
        p.append(f'<circle cx="{tx}" cy="{ty-liquid_h}" r="8" fill="{color}"/>')
        for i in range(5):
            yy = ty-160 + i*28
            p.append(f'<line x1="{tx-12}" y1="{yy}" x2="{tx-5}" y2="{yy}" stroke="#64748B" stroke-width="1.5"/>')
        p.append(label(tx, ty+45, label_text, 15, color, "middle", True))
        y = ty-165
        for d in details:
            p.append(label(tx+50, y, d, 12, color, "start"))
            y += 20
        p.append(label(tx, ty-190, tag, 13, tag_color, "middle", True))
        return '\n  '.join(p)

    svg += thermometer(220, 370, 140, RED, "日本",
                       ["日经破7万", "BOJ加息至1%", "经济过热↑"], "过热!", RED)
    svg += thermometer(548, 370, 55, ACCENT, "中国",
                       ["通缩压力", "等政策落地", "经济偏冷↓"], "偏冷", ACCENT)

    # 分隔线
    svg += dashed_line(W//2, 180, W//2, 420)
    svg += label(W//2, SUMMARY_Y, "亚洲经济温差：一个发烫，一个发冷", 14, GRAY)
    return svg + svg_close()


def comic_05():
    """宏观：骰子还没落地，所有人都在等"""
    svg = svg_open("宏观：骰子还没落地，所有人都在等")

    # 会议桌
    svg += f'<ellipse cx="384" cy="320" rx="250" ry="40" fill="#F1F5F9" stroke="#64748B" stroke-width="2.5"/>\n'
    svg += f'<path d="M134,320 L134,260 L634,260 L634,320" fill="#F8FAFC" stroke="#64748B" stroke-width="2" stroke-dasharray="4,2"/>\n'

    # 围坐小人（模糊背影）
    positions = [(190,288),(240,265),(320,250),(384,245),(448,250),(528,265),(578,288)]
    for px, py in positions:
        svg += f'<circle cx="{px}" cy="{py-20}" r="10" fill="#CBD5E1" stroke="#94A3B8" stroke-width="2"/>\n'
        svg += f'<line x1="{px}" y1="{py-10}" x2="{px}" y2="{py+10}" stroke="#94A3B8" stroke-width="2.5"/>\n'

    # 前排抬头小人
    for px, py in [(240,265),(384,245),(528,265)]:
        svg += f'<circle cx="{px}" cy="{py-42}" r="9" fill="white" stroke="{GRAY}" stroke-width="2"/>\n'
        svg += f'<line x1="{px}" y1="{py-33}" x2="{px}" y2="{py-10}" stroke="{GRAY}" stroke-width="2.5"/>\n'
        svg += f'<line x1="{px}" y1="{py-25}" x2="{px-12}" y2="{py-18}" stroke="{GRAY}" stroke-width="2"/>\n'
        svg += f'<line x1="{px}" y1="{py-25}" x2="{px+12}" y2="{py-18}" stroke="{GRAY}" stroke-width="2"/>\n'

    # 悬空骰子
    dx, dy = 384, 130
    svg += f'<polygon points="{dx},{dy-30} {dx+40},{dy-45} {dx},{dy-60} {dx-40},{dy-45}" fill="#FEF3C7" stroke="{ORANGE}" stroke-width="2.5" stroke-linejoin="round"/>\n'
    svg += f'<polygon points="{dx},{dy-30} {dx+40},{dy-45} {dx+40},{dy-5} {dx},{dy+10}" fill="#FDE68A" stroke="{ORANGE}" stroke-width="2.5" stroke-linejoin="round"/>\n'
    svg += f'<polygon points="{dx},{dy-30} {dx-40},{dy-45} {dx-40},{dy-5} {dx},{dy+10}" fill="#FEF3C7" stroke="{ORANGE}" stroke-width="2.5" stroke-linejoin="round"/>\n'
    svg += label(dx+10, dy-25, "?", 18, ORANGE, "middle", True)
    svg += label(dx-15, dy-20, "%", 14, ORANGE, "middle")
    svg += label(dx+20, dy-15, "%", 13, ORANGE, "middle")

    svg += dashed_line(dx-30, dy+25, dx+30, dy+25)
    svg += label(W//2, SUMMARY_Y, "FOMC 6月16-17日开会 · 点阵图结果将决定一切", 13, GRAY)
    return svg + svg_close()


def comic_06():
    """商品：黄金天平，为什么往这边倒？"""
    svg = svg_open("商品：黄金天平，为什么往这边倒？")

    # 天平
    bx, by = W//2, 420
    svg += f'<rect x="{bx-60}" y="{by-15}" width="120" height="20" rx="3" fill="#F1F5F9" stroke="{GRAY}" stroke-width="2.5"/>\n'
    svg += f'<line x1="{bx}" y1="{by-15}" x2="{bx}" y2="{by-120}" stroke="{GRAY}" stroke-width="3"/>\n'

    beam_y = by - 125
    svg += f'<line x1="{bx-170}" y1="{beam_y-8}" x2="{bx+150}" y2="{beam_y+12}" stroke="{GRAY}" stroke-width="4" stroke-linecap="round"/>\n'
    svg += f'<polygon points="{bx},{beam_y} {bx-8},{beam_y+10} {bx+8},{beam_y+10}" fill="#F1F5F9" stroke="{GRAY}" stroke-width="2"/>\n'

    # 左盘 — 重（利率）
    lx, ly = bx-170, beam_y-8
    svg += f'<line x1="{lx}" y1="{ly}" x2="{lx}" y2="{ly+30}" stroke="{GRAY}" stroke-width="2"/>\n'
    svg += f'<path d="M{lx-50},{ly+30} Q{lx},{ly+55} {lx+50},{ly+30}" fill="#FEF2F2" stroke="{RED}" stroke-width="2.5"/>\n'
    for ox, oy in [(lx-25,ly+20),(lx+10,ly+15),(lx-8,ly+8),(lx+20,ly+28),(lx-32,ly+10),(lx,ly-2)]:
        svg += label(ox, oy, "$", 16, RED, "middle", True)
    svg += label(lx, 112, "利率预期", 15, RED, "middle", True)
    svg += label(lx, 128, "(真正的驱动力)", 13, RED)
    arrow(lx-60, 70, lx-30, 90, RED)
    svg += label(lx-70, 60, "重!往下沉", 13, RED, "middle")

    # 右盘 — 轻（避险）
    rx, ry = bx+150, beam_y+12
    svg += f'<line x1="{rx}" y1="{ry}" x2="{rx}" y2="{ry+50}" stroke="{GRAY}" stroke-width="2"/>\n'
    svg += f'<path d="M{rx-50},{ry+50} Q{rx},{ry+75} {rx+50},{ry+50}" fill="#FFF7ED" stroke="{ORANGE}" stroke-width="2.5"/>\n'
    svg += f'<path d="M{rx},{ry+35} Q{rx-10},{ry+20} {rx},{ry+10} Q{rx+10},{ry+20} {rx},{ry+35}" fill="#FCD34D" stroke="{ORANGE}" stroke-width="1.5"/>\n'
    svg += label(rx, 112, "避险情绪", 15, ORANGE, "middle", True)
    svg += label(rx, 128, "(只是个假象)", 13, ORANGE)

    # 黄金价格
    svg += f'<rect x="{W//2-84}" y="450" width="168" height="34" rx="6" fill="{ACCENT}"/>\n'
    svg += label(W//2, 473, "黄金坚守 $4300", 17, "#FFFFFF", "middle", True)

    return svg + svg_close()


# ============================================================
# 生成入口
# ============================================================

COMICS = [
    ("01-a股", comic_01),
    ("02-美股", comic_02),
    ("03-科技", comic_03),
    ("04-国际", comic_04),
    ("05-宏观", comic_05),
    ("06-商品", comic_06),
]

def generate():
    os.makedirs(OUT, exist_ok=True)
    print("=" * 60)
    print(f"Dalio 漫画生成 — {DATE} {EDITION}")
    print("=" * 60)
    for sid, fn in COMICS:
        svg_str = fn()
        filepath = os.path.join(OUT, f"panel-{sid}.svg")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_str)
        kb = len(svg_str.encode("utf-8")) / 1024
        print(f"  [OK] panel-{sid}.svg  {kb:.1f}KB")
    print(f"完成: {len(COMICS)}/6 | 输出: {OUT}")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        DATE = sys.argv[1]
    if len(sys.argv) >= 3:
        EDITION = sys.argv[2]
    generate()
