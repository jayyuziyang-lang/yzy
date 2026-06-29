"""
Generate Dalio-style SVG comics for 6.29 evening report.
Panel-000: Radar overview — 6-node 今日热点速览
"""
import xml.etree.ElementTree as ET
import math

# ============================================================
# Panel-000: 今日热点速览 — 辐射状雷达图
# ============================================================
W, H = 768, 512
CX, CY = 384, 260
R = 180
R_inner = 45

nodes = [
    ("科创50\n+4.61%", "创历史新高", "#DC2626", 0),
    ("创新药\n涨停潮", "医药+5.91%", "#DC2626", 60),
    ("上证+1.16%", "收复4073", "#DC2626", 120),
    ("恒指+1.57%", "七周连跌后反弹", "#1A56DB", 180),
    ("美伊明日\n多哈谈判", "霍尔木兹焦点", "#D4A017", 240),
    ("美股期货\n全线上涨", "纳指期货+1%", "#16A34A", 300),
]

def rad(deg):
    return math.radians(deg - 90)

lines = []
for label, sub, color, angle in nodes:
    x = CX + R * math.cos(rad(angle))
    y = CY + R * math.sin(rad(angle))
    inner_x = CX + R_inner * math.cos(rad(angle))
    inner_y = CY + R_inner * math.sin(rad(angle))
    lines.append(f'  <line x1="{CX:.0f}" y1="{CY:.0f}" x2="{x:.0f}" y2="{y:.0f}" stroke="#CBD5E1" stroke-width="1.5"/>')
    # Node circle
    nx = CX + (R+35) * math.cos(rad(angle))
    ny = CY + (R+35) * math.sin(rad(angle))
    lines.append(f'  <circle cx="{nx:.0f}" cy="{ny:.0f}" r="32" fill="{color}" opacity="0.12"/>')
    lines.append(f'  <circle cx="{nx:.0f}" cy="{ny:.0f}" r="32" fill="none" stroke="{color}" stroke-width="2"/>')
    lines.append(f'  <text x="{nx:.0f}" y="{ny-3:.0f}" text-anchor="middle" font-size="11" font-weight="700" fill="{color}">{label}</text>')
    lines.append(f'  <text x="{nx:.0f}" y="{ny+14:.0f}" text-anchor="middle" font-size="9" fill="#64748B">{sub}</text>')

# Center hub
hub = f'''  <circle cx="{CX}" cy="{CY}" r="{R_inner}" fill="#1A56DB" opacity="0.08"/>
  <circle cx="{CX}" cy="{CY}" r="{R_inner}" fill="none" stroke="#1A56DB" stroke-width="2.5"/>
  <text x="{CX}" y="{CY-2}" text-anchor="middle" font-size="14" font-weight="800" fill="#1A56DB">今日</text>
  <text x="{CX}" y="{CY+14}" text-anchor="middle" font-size="14" font-weight="800" fill="#1A56DB">速览</text>'''

panel_000 = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Microsoft YaHei, SimHei, sans-serif">
  <rect width="{W}" height="{H}" fill="#FAFBFC"/>
  <text x="{CX}" y="38" text-anchor="middle" font-size="18" font-weight="700" fill="#D4A017">今日热点速览 · 60秒掌握关键信息</text>
  <text x="{CX}" y="58" text-anchor="middle" font-size="11" fill="#94A3B8">2026年6月29日 · 周一 · 扬说晚报</text>
  {chr(10).join(lines)}
  {hub}
  <line x1="24" y1="480" x2="744" y2="480" stroke="#D4A017" stroke-width="2" opacity="0.3"/>
  <text x="384" y="496" text-anchor="middle" font-size="9" fill="#94A3B8">扬说财经晚报 · 2026.06.29</text>
</svg>'''

with open("panel-000.svg", "w", encoding="utf-8") as f:
    f.write(panel_000)

# Validate
try:
    ET.parse("panel-000.svg")
    size = len(panel_000)
    print(f"[OK] panel-000.svg: XML valid, {size}B ({size/1024:.1f}KB)")
except Exception as e:
    print(f"[FAIL] panel-000.svg: {e}")
