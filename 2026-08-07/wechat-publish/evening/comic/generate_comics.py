"""
Generate Dalio-style SVG comics for 2026-08-07 evening report.
Panel-001: 钱换桌子 — 资金从拥挤的AI硬件(光模块)换到超跌的创新药
隐喻: 跷跷板 — AI硬件那边人太多(拥挤)被压下去, 创新药那边空着翘起来,
     一个"资金"金币从低处飞向高处。
"""
import os

GOLD = "#D4A017"
PURPLE = "#7C3AED"
RED = "#DC2626"
INK = "#334155"
GRAY = "#64748B"
LIGHT = "#94A3B8"
BG = "#FAFBFC"
LINE = "#CBD5E1"
GREEN = "#16A34A"


def person(x, ground, h=38, color=INK, arms="stand"):
    """几何小人: 圆头 + 梯形身体 + 腿 + 手臂。ground=脚底y。"""
    head_r = 7
    hy = ground - h * 0.72          # 头心y
    ty = ground - h * 0.5           # 身体顶y
    bx = x - 8, x + 8               # 身体上宽
    by = x - 11, x + 11             # 身体下宽
    els = [
        f'<circle cx="{x}" cy="{hy:.0f}" r="{head_r}" fill="{color}"/>',
        f'<polygon points="{bx[0]},{ty:.0f} {bx[1]},{ty:.0f} {by[1]},{ground-4:.0f} {by[0]},{ground-4:.0f}" fill="{color}"/>',
        f'<line x1="{x-4}" y1="{ground-4:.0f}" x2="{x-6}" y2="{ground}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
        f'<line x1="{x+4}" y1="{ground-4:.0f}" x2="{x+6}" y2="{ground}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
    ]
    arm_y = ground - h * 0.4
    if arms == "stand":
        els.append(f'<line x1="{x-7}" y1="{arm_y:.0f}" x2="{x-12}" y2="{ground-6:.0f}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        els.append(f'<line x1="{x+7}" y1="{arm_y:.0f}" x2="{x+12}" y2="{ground-6:.0f}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
    elif arms == "point":           # 右臂斜向上指(指向资金方向)
        els.append(f'<line x1="{x-7}" y1="{arm_y:.0f}" x2="{x-12}" y2="{ground-6:.0f}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        els.append(f'<line x1="{x+7}" y1="{arm_y:.0f}" x2="{x+16}" y2="{arm_y-16:.0f}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
    elif arms == "arms_up":
        els.append(f'<line x1="{x-7}" y1="{arm_y:.0f}" x2="{x-13}" y2="{arm_y-15:.0f}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        els.append(f'<line x1="{x+7}" y1="{arm_y:.0f}" x2="{x+13}" y2="{arm_y-15:.0f}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
    return "".join(els)


E = []
E.append(f'<rect width="768" height="512" fill="{BG}"/>')

# ===== 标题栏 (晚报金色系) =====
E.append(f'<text x="384" y="36" text-anchor="middle" font-size="18" font-weight="700" fill="{GOLD}">钱换桌子：从拥挤的AI硬件，到超跌的创新药</text>')
E.append(f'<text x="384" y="56" text-anchor="middle" font-size="11" fill="{LIGHT}">2026年8月7日 · 周五 · 扬说晚报</text>')

# ===== 跷跷板 =====
# 三角支架
E.append(f'<polygon points="384,298 344,412 424,412" fill="#FFF7E6" stroke="{GOLD}" stroke-width="3" stroke-linejoin="round"/>')
# 横梁: 左低(150,362) → 右高(618,238)
E.append(f'<line x1="150" y1="362" x2="618" y2="238" stroke="{GOLD}" stroke-width="11" stroke-linecap="round"/>')
E.append(f'<line x1="150" y1="362" x2="618" y2="238" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.5"/>')
E.append(f'<circle cx="384" cy="300" r="8" fill="{GOLD}"/>')

# ===== 左端(低,沉): 光模块盒子 + 3个拥挤小人 =====
# 盒子站在 x≈200 处横梁上(横梁该处y≈349), 盒底到 345
E.append(f'<rect x="125" y="282" width="150" height="63" rx="10" fill="#FFFFFF" stroke="{PURPLE}" stroke-width="2.5"/>')
E.append(f'<text x="200" y="312" text-anchor="middle" font-size="16" font-weight="700" fill="{PURPLE}">光模块</text>')
E.append(f'<text x="200" y="332" text-anchor="middle" font-size="10" fill="{GRAY}">AI硬件 · 拥挤</text>')
# 3个拥挤小人站盒顶(ground=282)
for px in (158, 188, 218):
    E.append(person(px, 282, h=36, color=PURPLE, arms="stand"))

# ===== 右端(高,翘): 创新药药瓶 + 1个招手小人 =====
# 药瓶站在 x≈606 处横梁上(该处y≈241), 瓶底到 240
E.append(f'<rect x="576" y="156" width="60" height="84" rx="26" fill="#FEF2F2" stroke="{RED}" stroke-width="2.5"/>')
E.append(f'<text x="606" y="192" text-anchor="middle" font-size="14" font-weight="700" fill="{RED}">创新药</text>')
E.append(f'<text x="606" y="212" text-anchor="middle" font-size="10" fill="{GRAY}">超跌反弹</text>')
# 药瓶旁招手小人(指向资金来的方向)
E.append(person(658, 240, h=38, color=RED, arms="arms_up"))

# ===== 资金搬家: 虚线轨迹 + 金币飞向右上 =====
E.append(f'<path d="M 280,290 Q 380,120 545,165" fill="none" stroke="{GOLD}" stroke-width="3" stroke-dasharray="7 6" opacity="0.7"/>')
E.append(f'<circle cx="505" cy="152" r="17" fill="{GOLD}"/>')
E.append(f'<text x="505" y="158" text-anchor="middle" font-size="16" font-weight="800" fill="#FFFFFF">￥</text>')
E.append(f'<polygon points="562,156 574,143 552,138" fill="{GOLD}"/>')
E.append(f'<text x="430" y="120" text-anchor="middle" font-size="13" font-weight="700" fill="{GOLD}">资金搬家 →</text>')

# ===== 底部 =====
E.append(f'<line x1="24" y1="466" x2="744" y2="466" stroke="{GOLD}" stroke-width="2" opacity="0.3"/>')
E.append(f'<text x="384" y="492" text-anchor="middle" font-size="11" fill="{INK}">CRO<tspan fill="{RED}" font-weight="700">+10.63%</tspan>创新药涨停潮 · 中际旭创<tspan fill="{GREEN}" font-weight="700">-3.68%</tspan>尾盘跳水 · A股四连涨重上年线</text>')

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 512" width="768" height="512" '
    f'font-family="Microsoft YaHei, SimHei, sans-serif">\n'
    + "\n".join(E) +
    f'\n</svg>\n'
)

out = os.path.join(os.path.dirname(__file__), "panel-001.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write(svg)
print("written:", out, len(svg), "chars")
