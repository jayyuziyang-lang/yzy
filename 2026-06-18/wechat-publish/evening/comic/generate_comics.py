"""Generate Dalio-style SVG comics for 2026-06-18 evening report."""
import xml.etree.ElementTree as ET
import os

OUT = os.path.dirname(os.path.abspath(__file__))

NS = "http://www.w3.org/2000/svg"
BLUE = "#1A56DB"
RED = "#DC2626"
GREEN = "#16A34A"
PURPLE = "#7C3AED"
GOLD = "#D4A017"
ORANGE = "#EA580C"
DARK = "#475569"
GRAY = "#64748B"
LIGHT_GRAY = "#94A3B8"
BG = "#FAFBFC"
WHITE = "#FFFFFF"

def svg():
    root = ET.Element("svg", {
        "xmlns": NS, "viewBox": "0 0 768 512", "width": "768", "height": "512",
        "font-family": "Microsoft YaHei, SimHei, sans-serif"
    })
    ET.SubElement(root, "rect", {"width": "768", "height": "512", "fill": BG})
    return root

def add_title_bar(root, title, color=GOLD):
    ET.SubElement(root, "rect", {"x":"0","y":"0","width":"768","height":"44","fill":color,"opacity":"0.08"})
    t = ET.SubElement(root, "text", {"x":"384","y":"30","font-size":"18","fill":color,"text-anchor":"middle","font-weight":"bold"})
    t.text = title

def add_stick_figure(root, cx, cy, scale=1.0, color=DARK):
    s = scale
    ET.SubElement(root, "circle", {"cx":str(cx),"cy":str(cy-8*s),"r":str(4*s),"fill":"none","stroke":color,"stroke-width":"2"})
    ET.SubElement(root, "line", {"x1":str(cx),"y1":str(cy-4*s),"x2":str(cx),"y2":str(cy+8*s),"stroke":color,"stroke-width":"2","stroke-linecap":"round"})
    ET.SubElement(root, "line", {"x1":str(cx-6*s),"y1":str(cy),"x2":str(cx+6*s),"y2":str(cy),"stroke":color,"stroke-width":"1.5","stroke-linecap":"round"})
    ET.SubElement(root, "line", {"x1":str(cx),"y1":str(cy+8*s),"x2":str(cx-5*s),"y2":str(cy+14*s),"stroke":color,"stroke-width":"1.5","stroke-linecap":"round"})
    ET.SubElement(root, "line", {"x1":str(cx),"y1":str(cy+8*s),"x2":str(cx+5*s),"y2":str(cy+14*s),"stroke":color,"stroke-width":"1.5","stroke-linecap":"round"})

def add_arrow(root, x1, y1, x2, y2, color=GOLD, width=2):
    ET.SubElement(root, "line", {
        "x1":str(x1),"y1":str(y1),"x2":str(x2),"y2":str(y2),
        "stroke":color,"stroke-width":str(width),"stroke-linecap":"round"
    })
    dx, dy = x2-x1, y2-y1
    length = (dx**2 + dy**2)**0.5
    if length < 1: return
    ux, uy = dx/length, dy/length
    px, py = -uy, ux
    ax, ay = x2-6*ux+4*px, y2-6*uy+4*py
    bx, by = x2-6*ux-4*px, y2-6*uy-4*py
    ET.SubElement(root, "polygon", {
        "points": f"{x2},{y2} {ax:.1f},{ay:.1f} {bx:.1f},{by:.1f}",
        "fill": color
    })

def serialize(root, filename):
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    raw = ET.tostring(root, encoding="unicode")
    ET.fromstring(raw)
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw)
    size = os.path.getsize(path)
    print(f"  {filename}: {size} bytes")
    return True


# ============ Panel 001: A股极致分化 — 指数繁荣 vs 个股普跌 ============
def panel_001():
    root = svg()
    add_title_bar(root, "A股极致分化：指数繁荣 vs 个股普跌")

    # Big seesaw in center - tilted: left DOWN (上证/3300 stocks), right UP (科创50/创业板)
    # Fulcrum (pivot point)
    ET.SubElement(root, "polygon", {"points":"384,340 370,358 398,358","fill":DARK})

    # Seesaw beam tilted: left side lower, right side higher
    ET.SubElement(root, "line", {"x1":"80","y1":"280","x2":"688","y2":"380","stroke":DARK,"stroke-width":"5","stroke-linecap":"round"})

    # LEFT SIDE: 上证 -0.43%, 3325 stocks down
    ET.SubElement(root, "rect", {"x":"40","y":"140","width":"220","height":"130","rx":"8","fill":WHITE,"stroke":RED,"stroke-width":"2.5"})
    t = ET.SubElement(root, "text", {"x":"150","y":"168","font-size":"15","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "上证 -0.43%"

    left_items = [
        ("失守4100点", RED),
        ("3325只个股下跌", RED),
        ("大金融/电力杀跌", RED),
        ("保险券商领跌", RED),
    ]
    for i, (txt, clr) in enumerate(left_items):
        y = 190 + i*18
        ET.SubElement(root, "circle", {"cx":"65","cy":str(y),"r":"3","fill":clr})
        t = ET.SubElement(root, "text", {"x":"75","y":str(y+4),"font-size":"10","fill":DARK})
        t.text = txt

    # Big down arrow on left
    ET.SubElement(root, "line", {"x1":"150","y1":"290","x2":"150","y2":"320","stroke":RED,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"150,328 143,318 157,318","fill":RED})

    # RIGHT SIDE: 科创50 +3.84%, 创业板 +2.05%
    ET.SubElement(root, "rect", {"x":"508","y":"160","width":"220","height":"130","rx":"8","fill":WHITE,"stroke":GREEN,"stroke-width":"2.5"})
    t = ET.SubElement(root, "text", {"x":"618","y":"188","font-size":"15","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "科创50 +3.84%"

    right_items = [
        ("创业板 +2.05% 历史新高", GREEN),
        ("2018只个股上涨", GREEN),
        ("芯片/AI/创新药领涨", GREEN),
        ("中际旭创超茅台", GREEN),
    ]
    for i, (txt, clr) in enumerate(right_items):
        y = 210 + i*18
        ET.SubElement(root, "circle", {"cx":"533","cy":str(y),"r":"3","fill":clr})
        t = ET.SubElement(root, "text", {"x":"543","y":str(y+4),"font-size":"10","fill":DARK})
        t.text = txt

    # Big up arrow on right
    ET.SubElement(root, "line", {"x1":"618","y1":"300","x2":"618","y2":"270","stroke":GREEN,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"618,262 611,272 625,272","fill":GREEN})

    # Center label
    ET.SubElement(root, "rect", {"x":"284","y":"396","width":"200","height":"36","rx":"6","fill":GOLD,"opacity":"0.12"})
    t = ET.SubElement(root, "text", {"x":"384","y":"419","font-size":"12","fill":GOLD,"text-anchor":"middle","font-weight":"bold"})
    t.text = "3.31万亿成交：不是离场，是迁徙"

    # Stick figures at bottom
    add_stick_figure(root, 170, 470, scale=1.0, color=RED)
    t = ET.SubElement(root, "text", {"x":"170","y":"500","font-size":"9","fill":RED,"text-anchor":"middle"})
    t.text = "传统蓝筹持有者"

    add_stick_figure(root, 598, 470, scale=1.0, color=GREEN)
    t = ET.SubElement(root, "text", {"x":"598","y":"500","font-size":"9","fill":GREEN,"text-anchor":"middle"})
    t.text = "科技成长持有者"

    serialize(root, "panel-001.svg")


# ============ Panel 002: 中际旭创超越茅台 — 时代替换 ============
def panel_002():
    root = svg()
    add_title_bar(root, "中际旭创市值超越茅台：一个时代的替换")

    # LEFT: 茅台 tower (shorter now)
    # Bottle shape - 白酒瓶
    ET.SubElement(root, "rect", {"x":"96","y":"220","width":"60","height":"120","rx":"6","fill":"#FFF7ED","stroke":ORANGE,"stroke-width":"2.5"})
    # bottle neck
    ET.SubElement(root, "rect", {"x":"114","y":"190","width":"24","height":"30","rx":"3","fill":"#FFF7ED","stroke":ORANGE,"stroke-width":"2"})
    # bottle cap
    ET.SubElement(root, "rect", {"x":"118","y":"178","width":"16","height":"12","rx":"2","fill":ORANGE,"opacity":"0.5"})
    t = ET.SubElement(root, "text", {"x":"126","y":"270","font-size":"13","fill":ORANGE,"text-anchor":"middle","font-weight":"bold"})
    t.text = "茅台"
    t = ET.SubElement(root, "text", {"x":"126","y":"288","font-size":"10","fill":RED,"text-anchor":"middle"})
    t.text = "白酒之王"

    # Down arrow for 茅台
    ET.SubElement(root, "line", {"x1":"250","y1":"260","x2":"280","y2":"260","stroke":RED,"stroke-width":"2.5"})
    ET.SubElement(root, "polygon", {"points":"285,260 277,254 277,266","fill":RED})

    # ARROW between - passing torch
    add_arrow(root, 340, 260, 420, 260, color=GOLD, width=3)
    t = ET.SubElement(root, "text", {"x":"380","y":"250","font-size":"11","fill":GOLD,"text-anchor":"middle","font-weight":"bold"})
    t.text = "时代替换 →"

    # RIGHT: 中际旭创 tower (taller now)
    ET.SubElement(root, "rect", {"x":"450","y":"160","width":"70","height":"180","rx":"6","fill":"#F0FDF4","stroke":GREEN,"stroke-width":"2.5"})
    # circuit/tech pattern on tower
    for cy_offset in [20, 60, 100, 140]:
        ET.SubElement(root, "line", {"x1":"460","y1":str(188+cy_offset),"x2":"510","y2":str(188+cy_offset),"stroke":PURPLE,"stroke-width":"1","opacity":"0.3"})
        ET.SubElement(root, "circle", {"cx":"510","cy":str(188+cy_offset),"r":"3","fill":"none","stroke":PURPLE,"stroke-width":"1","opacity":"0.5"})
    t = ET.SubElement(root, "text", {"x":"485","y":"210","font-size":"13","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "中际旭创"
    t = ET.SubElement(root, "text", {"x":"485","y":"230","font-size":"10","fill":GREEN,"text-anchor":"middle"})
    t.text = "AI算力之矛"

    # Up arrow for 中际旭创
    ET.SubElement(root, "line", {"x1":"530","y1":"220","x2":"560","y2":"220","stroke":GREEN,"stroke-width":"2.5"})
    ET.SubElement(root, "polygon", {"points":"565,220 557,214 557,226","fill":GREEN})

    # Center: the passing of the crown
    ET.SubElement(root, "circle", {"cx":"384","cy":"330","r":"36","fill":"none","stroke":GOLD,"stroke-width":"2","stroke-dasharray":"6,3"})
    t = ET.SubElement(root, "text", {"x":"384","y":"320","font-size":"10","fill":DARK,"text-anchor":"middle"})
    t.text = "A股"
    t = ET.SubElement(root, "text", {"x":"384","y":"336","font-size":"10","fill":DARK,"text-anchor":"middle"})
    t.text = "新锚"
    t = ET.SubElement(root, "text", {"x":"384","y":"352","font-size":"10","fill":DARK,"text-anchor":"middle"})
    t.text = "确立"

    # Bottom explanation
    ET.SubElement(root, "rect", {"x":"80","y":"380","width":"608","height":"70","rx":"6","fill":GOLD,"opacity":"0.06"})
    explanation = [
        "三重推力：陆家嘴论坛AI上市改革 + DeepSeek $74亿融资 + 全球算力军备竞赛",
        "从\"喝酒\"到\"算力\"——不是股价涨跌，是中国经济结构的投影",
        "PCB概念年内+116%、寒武纪+14%——科技牛市不是概念，是产业周期",
    ]
    for i, line in enumerate(explanation):
        t = ET.SubElement(root, "text", {"x":"384","y":str(405+i*17),"font-size":"10","fill":DARK,"text-anchor":"middle"})
        t.text = line

    # Stick figures
    add_stick_figure(root, 140, 478, scale=1.0, color=ORANGE)
    t = ET.SubElement(root, "text", {"x":"140","y":"505","font-size":"8","fill":ORANGE,"text-anchor":"middle"})
    t.text = "传统投资者"

    add_stick_figure(root, 480, 478, scale=1.0, color=GREEN)
    t = ET.SubElement(root, "text", {"x":"480","y":"505","font-size":"8","fill":GREEN,"text-anchor":"middle"})
    t.text = "科技投资者"

    serialize(root, "panel-002.svg")


# ============ Panel 003: 亚洲市场内部分化 ============
def panel_003():
    root = svg()
    add_title_bar(root, "亚洲内部分裂：日韩创新高 vs 恒生暴跌")

    # LEFT: Japan - rising sun, up arrow
    ET.SubElement(root, "rect", {"x":"20","y":"70","width":"220","height":"150","rx":"8","fill":"#F0FDF4","stroke":GREEN,"stroke-width":"2"})
    # Rising sun circle
    ET.SubElement(root, "circle", {"cx":"130","cy":"115","r":"24","fill":RED,"opacity":"0.15"})
    ET.SubElement(root, "circle", {"cx":"130","cy":"115","r":"14","fill":RED,"opacity":"0.3"})
    t = ET.SubElement(root, "text", {"x":"130","y":"100","font-size":"14","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "日经225"
    t = ET.SubElement(root, "text", {"x":"130","y":"155","font-size":"22","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "+1.65%"
    t = ET.SubElement(root, "text", {"x":"130","y":"175","font-size":"10","fill":DARK,"text-anchor":"middle"})
    t.text = "71,053 连续两日历史新高"
    t = ET.SubElement(root, "text", {"x":"130","y":"195","font-size":"9","fill":GRAY,"text-anchor":"middle"})
    t.text = "半导体+弱日元"

    # Big UP arrow
    ET.SubElement(root, "line", {"x1":"130","y1":"230","x2":"130","y2":"200","stroke":GREEN,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"130,192 123,202 137,202","fill":GREEN})

    # CENTER: Korea
    ET.SubElement(root, "rect", {"x":"254","y":"70","width":"220","height":"150","rx":"8","fill":"#F0FDF4","stroke":GREEN,"stroke-width":"2"})
    t = ET.SubElement(root, "text", {"x":"364","y":"100","font-size":"14","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "韩国KOSPI"
    t = ET.SubElement(root, "text", {"x":"364","y":"155","font-size":"22","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "+2.61%"
    t = ET.SubElement(root, "text", {"x":"364","y":"175","font-size":"10","fill":DARK,"text-anchor":"middle"})
    t.text = "9,063 逼近9100"
    t = ET.SubElement(root, "text", {"x":"364","y":"195","font-size":"9","fill":GRAY,"text-anchor":"middle"})
    t.text = "三星+4.6% SK海力士+6.5%"

    ET.SubElement(root, "line", {"x1":"364","y1":"230","x2":"364","y2":"200","stroke":GREEN,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"364,192 357,202 371,202","fill":GREEN})

    # RIGHT: 港股 - storm cloud
    ET.SubElement(root, "rect", {"x":"488","y":"70","width":"260","height":"150","rx":"8","fill":"#FFF5F5","stroke":RED,"stroke-width":"2"})
    t = ET.SubElement(root, "text", {"x":"618","y":"100","font-size":"14","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "恒生指数"

    # Dark cloud
    ET.SubElement(root, "ellipse", {"cx":"618","cy":"118","rx":"35","ry":"12","fill":RED,"opacity":"0.15"})
    ET.SubElement(root, "ellipse", {"cx":"600","cy":"114","rx":"20","ry":"9","fill":RED,"opacity":"0.12"})
    ET.SubElement(root, "ellipse", {"cx":"636","cy":"116","rx":"18","ry":"8","fill":RED,"opacity":"0.12"})
    # Rain drops
    for dx in [-20, -5, 10, 25]:
        ET.SubElement(root, "line", {"x1":str(618+dx),"y1":"128","x2":str(618+dx+2),"y2":"140","stroke":RED,"stroke-width":"1.5","opacity":"0.4"})

    t = ET.SubElement(root, "text", {"x":"618","y":"155","font-size":"22","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "-2.04%"
    t = ET.SubElement(root, "text", {"x":"618","y":"175","font-size":"10","fill":DARK,"text-anchor":"middle"})
    t.text = "23,924 金融地产承压"
    t = ET.SubElement(root, "text", {"x":"618","y":"195","font-size":"9","fill":GRAY,"text-anchor":"middle"})
    t.text = "FOMC鹰派→高杠杆板块失血"

    ET.SubElement(root, "line", {"x1":"618","y1":"230","x2":"618","y2":"260","stroke":RED,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"618,268 611,258 625,258","fill":RED})

    # Bottom: Why the split
    ET.SubElement(root, "rect", {"x":"20","y":"290","width":"728","height":"100","rx":"6","fill":GOLD,"opacity":"0.06"})
    t = ET.SubElement(root, "text", {"x":"384","y":"312","font-size":"12","fill":DARK,"text-anchor":"middle","font-weight":"bold"})
    t.text = "同一亚洲，三条路径——为什么方向完全相反？"

    reasons = [
        "日韩：半导体出口超级周期 + 弱势货币利好出口企业 = 独立于Fed紧缩",
        "港股：FOMC鹰派 → 美元走强 → 资金流出 → 金融/地产等高杠杆板块承压",
        "A股：内部分化 — 科技板块跟日韩（产业周期），金融板块跟港股（利率敏感）",
    ]
    for i, line in enumerate(reasons):
        t = ET.SubElement(root, "text", {"x":"384","y":str(338+i*17),"font-size":"10","fill":DARK,"text-anchor":"middle"})
        t.text = line

    # Three stick figures
    for x, color, label in [(130, GREEN, "东京"), (364, GREEN, "首尔"), (618, RED, "香港")]:
        add_stick_figure(root, x, 460, scale=1.0, color=color)
        t = ET.SubElement(root, "text", {"x":str(x),"y":"490","font-size":"9","fill":color,"text-anchor":"middle"})
        t.text = label

    t = ET.SubElement(root, "text", {"x":"384","y":"510","font-size":"10","fill":LIGHT_GRAY,"text-anchor":"middle"})
    t.text = "\"东升西降\"是真的——但\"东\"是日韩台半导体链，不一定是港股"

    serialize(root, "panel-003.svg")


# ============ Panel 004: 黄金V反 ============
def panel_004():
    root = svg()
    add_title_bar(root, "黄金V型反转：$4,218 → $4,322 — 亚洲买盘托盘")

    # V-shaped valley - the core visual
    # Left cliff: high then drop
    ET.SubElement(root, "line", {"x1":"100","y1":"160","x2":"100","y2":"380","stroke":ORANGE,"stroke-width":"3"})
    # Price on left
    t = ET.SubElement(root, "text", {"x":"90","y":"150","font-size":"12","fill":ORANGE,"font-weight":"bold","text-anchor":"end"})
    t.text = "$4,381"
    t = ET.SubElement(root, "text", {"x":"90","y":"168","font-size":"9","fill":GRAY,"text-anchor":"end"})
    t.text = "FOMC前"

    # V bottom
    ET.SubElement(root, "polyline", {
        "points": "100,180 250,370 400,180",
        "fill": "none", "stroke": ORANGE, "stroke-width":"3.5", "stroke-linejoin":"round"
    })
    # Label at bottom
    t = ET.SubElement(root, "text", {"x":"250","y":"392","font-size":"12","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "$4,218"
    t = ET.SubElement(root, "text", {"x":"250","y":"408","font-size":"9","fill":GRAY,"text-anchor":"middle"})
    t.text = "隔夜低点"

    # Right recovery
    ET.SubElement(root, "line", {"x1":"400","y1":"180","x2":"620","y2":"180","stroke":ORANGE,"stroke-width":"3"})
    t = ET.SubElement(root, "text", {"x":"630","y":"175","font-size":"12","fill":GREEN,"font-weight":"bold"})
    t.text = "$4,322+"
    t = ET.SubElement(root, "text", {"x":"630","y":"192","font-size":"9","fill":GRAY})
    t.text = "日内反弹"

    # V label
    t = ET.SubElement(root, "text", {"x":"355","y":"250","font-size":"16","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "V"
    add_arrow(root, 330, 235, 355, 240, color=GREEN, width=1.5)

    # Annotation boxes
    # Left: FOMC冲击
    ET.SubElement(root, "rect", {"x":"20","y":"420","width":"200","height":"55","rx":"6","fill":"#FFF5F5","stroke":RED,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"120","y":"438","font-size":"10","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "FOMC鹰派冲击"
    t = ET.SubElement(root, "text", {"x":"120","y":"455","font-size":"9","fill":DARK,"text-anchor":"middle"})
    t.text = "9人支持加息 → 实际利率↑"
    t = ET.SubElement(root, "text", {"x":"120","y":"470","font-size":"9","fill":DARK,"text-anchor":"middle"})
    t.text = "美元DXY +0.86% → 黄金失血"

    # Center: V反逻辑
    ET.SubElement(root, "rect", {"x":"240","y":"420","width":"248","height":"55","rx":"6","fill":"#F0FDF4","stroke":GREEN,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"364","y":"438","font-size":"10","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "V反三理由"
    lines = ["① FOMC冲击被消化 — 加息不是明天", "② 美伊协议 → 通胀预期↓ → 利空出尽", "③ 亚洲实金买盘 $4,200附近大量入场"]
    for i, line in enumerate(lines):
        t = ET.SubElement(root, "text", {"x":"364","y":str(454+i*10),"font-size":"8","fill":DARK,"text-anchor":"middle"})
        t.text = line

    # Right: 投资信号
    ET.SubElement(root, "rect", {"x":"508","y":"420","width":"240","height":"55","rx":"6","fill":"#FFF7ED","stroke":ORANGE,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"628","y":"438","font-size":"10","fill":ORANGE,"text-anchor":"middle","font-weight":"bold"})
    t.text = "关键判断"
    t = ET.SubElement(root, "text", {"x":"628","y":"455","font-size":"9","fill":DARK,"text-anchor":"middle"})
    t.text = "$4,200 = 亚洲实金地板价"
    t = ET.SubElement(root, "text", {"x":"628","y":"470","font-size":"9","fill":DARK,"text-anchor":"middle"})
    t.text = "短期 $4,200-4,400 区间震荡"

    serialize(root, "panel-004.svg")


if __name__ == "__main__":
    print("Generating Dalio SVG comics for 2026-06-18 evening...")
    panel_001()
    panel_002()
    panel_003()
    panel_004()
    print("Done! All panels generated.")
