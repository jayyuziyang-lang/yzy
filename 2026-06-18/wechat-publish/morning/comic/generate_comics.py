"""Generate Dalio-style SVG comics for 2026-06-18 morning report."""
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

def add_title_bar(root, title):
    ET.SubElement(root, "rect", {"x":"0","y":"0","width":"768","height":"44","fill":BLUE,"opacity":"0.08"})
    t = ET.SubElement(root, "text", {"x":"384","y":"30","font-size":"18","fill":BLUE,"text-anchor":"middle","font-weight":"bold"})
    t.text = title

def add_stick_figure(root, cx, cy, scale=1.0, color=DARK):
    s = scale
    # head
    ET.SubElement(root, "circle", {"cx":str(cx),"cy":str(cy-8*s),"r":str(4*s),"fill":"none","stroke":color,"stroke-width":"2"})
    # body
    ET.SubElement(root, "line", {"x1":str(cx),"y1":str(cy-4*s),"x2":str(cx),"y2":str(cy+8*s),"stroke":color,"stroke-width":"2","stroke-linecap":"round"})
    # arms
    ET.SubElement(root, "line", {"x1":str(cx-6*s),"y1":str(cy),"x2":str(cx+6*s),"y2":str(cy),"stroke":color,"stroke-width":"1.5","stroke-linecap":"round"})
    # legs
    ET.SubElement(root, "line", {"x1":str(cx),"y1":str(cy+8*s),"x2":str(cx-5*s),"y2":str(cy+14*s),"stroke":color,"stroke-width":"1.5","stroke-linecap":"round"})
    ET.SubElement(root, "line", {"x1":str(cx),"y1":str(cy+8*s),"x2":str(cx+5*s),"y2":str(cy+14*s),"stroke":color,"stroke-width":"1.5","stroke-linecap":"round"})

def add_arrow(root, x1, y1, x2, y2, color=BLUE, width=2):
    ET.SubElement(root, "line", {
        "x1":str(x1),"y1":str(y1),"x2":str(x2),"y2":str(y2),
        "stroke":color,"stroke-width":str(width),"stroke-linecap":"round"
    })
    # arrowhead
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

def add_label_box(root, x, y, w, h, text, color=BLUE, bg_opacity="0.15"):
    ET.SubElement(root, "rect", {"x":str(x),"y":str(y),"width":str(w),"height":str(h),"rx":"6","fill":color,"opacity":bg_opacity})
    t = ET.SubElement(root, "text", {"x":str(x+w/2),"y":str(y+h/2+4),"font-size":"12","fill":color,"text-anchor":"middle","font-weight":"bold"})
    t.text = text

def serialize(root, filename):
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    raw = ET.tostring(root, encoding="unicode")
    # verify XML is valid
    ET.fromstring(raw)
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw)
    size = os.path.getsize(path)
    print(f"  {filename}: {size} bytes")
    return True


# ============ Panel 001: FOMC Hawkish + Iran Deal ============
def panel_001():
    root = svg()
    add_title_bar(root, "一夜两件大事：FOMC鹰派转向 + 美伊签署备忘录")

    # LEFT: FOMC - hawkish Fed
    # Fed building icon
    ET.SubElement(root, "rect", {"x":"60","y":"80","width":"32","height":"40","rx":"3","fill":"none","stroke":RED,"stroke-width":"2.5"})
    ET.SubElement(root, "polygon", {"points":"56,80 76,60 96,80","fill":"none","stroke":RED,"stroke-width":"2.5"})
    ET.SubElement(root, "rect", {"x":"88","y":"92","width":"10","height":"16","rx":"1","fill":"none","stroke":RED,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"92","y":"104","font-size":"8","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "F"
    t = ET.SubElement(root, "text", {"x":"76","y":"140","font-size":"13","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "FOMC鹰派"

    # FOMC details
    items_left = [
        ("利率3.50-3.75%不变", RED),
        ("9/18官员支持加息", RED),
        ("删除全部前瞻指引", RED),
        ("核心PCE→3.3%", RED),
    ]
    for i, (txt, clr) in enumerate(items_left):
        y = 165 + i*22
        ET.SubElement(root, "circle", {"cx":"50","cy":str(y),"r":"3","fill":clr})
        t = ET.SubElement(root, "text", {"x":"60","y":str(y+4),"font-size":"10","fill":DARK})
        t.text = txt

    # RIGHT: Iran Deal
    ET.SubElement(root, "circle", {"cx":"690","cy":"100","r":"22","fill":"none","stroke":GREEN,"stroke-width":"2.5"})
    # peace dove - simplified
    ET.SubElement(root, "path", {"d":"M680,95 Q690,85 700,95","fill":"none","stroke":GREEN,"stroke-width":"1.5"})
    ET.SubElement(root, "path", {"d":"M680,105 Q690,115 700,105","fill":"none","stroke":GREEN,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"690","y":"140","font-size":"13","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "美伊签署备忘录"

    items_right = [
        ("永久停火", GREEN),
        ("霍尔木兹重开", GREEN),
        ("解除全部制裁", GREEN),
        ("$3000亿重建", GREEN),
    ]
    for i, (txt, clr) in enumerate(items_right):
        y = 165 + i*22
        ET.SubElement(root, "circle", {"cx":"560","cy":str(y),"r":"3","fill":clr})
        t = ET.SubElement(root, "text", {"x":"570","y":str(y+4),"font-size":"10","fill":DARK})
        t.text = txt

    # CENTER: Tug of war - balance scale
    # Scale beam
    ET.SubElement(root, "line", {"x1":"220","y1":"260","x2":"548","y2":"260","stroke":DARK,"stroke-width":"3"})
    # Pivot
    ET.SubElement(root, "polygon", {"points":"384,260 378,280 390,280","fill":DARK})
    ET.SubElement(root, "line", {"x1":"384","y1":"280","x2":"384","y2":"310","stroke":DARK,"stroke-width":"2"})

    # Left pan (FOMC hawkish = market down)
    ET.SubElement(root, "path", {"d":"M240,260 Q240,300 220,310 L260,310 Q280,300 280,260","fill":"none","stroke":RED,"stroke-width":"2"})
    ET.SubElement(root, "line", {"x1":"240","y1":"260","x2":"220","y2":"310","stroke":RED,"stroke-width":"1.5"})
    ET.SubElement(root, "line", {"x1":"280","y1":"260","x2":"260","y2":"310","stroke":RED,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"250","y":"295","font-size":"10","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "美股↓"

    # Right pan (Iran deal = bullish offset)
    ET.SubElement(root, "path", {"d":"M488,260 Q488,300 468,310 L528,310 Q548,300 548,260","fill":"none","stroke":GREEN,"stroke-width":"2"})
    ET.SubElement(root, "line", {"x1":"488","y1":"260","x2":"468","y2":"310","stroke":GREEN,"stroke-width":"1.5"})
    ET.SubElement(root, "line", {"x1":"548","y1":"260","x2":"528","y2":"310","stroke":GREEN,"stroke-width":"1.5"})
    t = ET.SubElement(root, "text", {"x":"518","y":"295","font-size":"10","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "油↓亚↑"

    # Center text
    t = ET.SubElement(root, "text", {"x":"384","y":"340","font-size":"12","fill":DARK,"text-anchor":"middle","font-weight":"bold"})
    t.text = "同一天，两股力量在天平两端——市场在找均衡"

    # Bottom: 3 stick figures looking at the scale
    for i, (x, label) in enumerate([(280, "空头"), (384, "观望"), (488, "多头")]):
        add_stick_figure(root, x, 400, scale=1.2)
        t = ET.SubElement(root, "text", {"x":str(x),"y":"430","font-size":"9","fill":GRAY,"text-anchor":"middle"})
        t.text = label

    t = ET.SubElement(root, "text", {"x":"384","y":"500","font-size":"11","fill":LIGHT_GRAY,"text-anchor":"middle"})
    t.text = "FOMC鹰派 vs 美伊和平：市场在两个极端之间寻找定价"

    serialize(root, "panel-001.svg")


# ============ Panel 002: Semis vs Megacap Divergence ============
def panel_002():
    root = svg()
    add_title_bar(root, "美国科技股内部分裂：半导体逆势涨  vs  科技巨头遭抛售")

    # LEFT: Megacaps going DOWN
    ET.SubElement(root, "rect", {"x":"40","y":"70","width":"280","height":"200","rx":"8","fill":WHITE,"stroke":RED,"stroke-width":"2"})
    t = ET.SubElement(root, "text", {"x":"180","y":"95","font-size":"14","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "科技七巨头遭抛售"

    megacaps = [("Meta", "-5%"), ("微软", "-3%"), ("亚马逊", "-3%"), ("英伟达", "-1%"), ("苹果", "-1%"), ("特斯拉", "-2%")]
    for i, (name, chg) in enumerate(megacaps):
        x = 80 + (i%3)*100
        y = 120 + (i//3)*40
        # down arrow
        ET.SubElement(root, "line", {"x1":str(x),"y1":str(y),"x2":str(x+15),"y2":str(y+15),"stroke":RED,"stroke-width":"2"})
        ET.SubElement(root, "line", {"x1":str(x+15),"y1":str(y),"x2":str(x),"y2":str(y+15),"stroke":RED,"stroke-width":"2"})
        t = ET.SubElement(root, "text", {"x":str(x+25),"y":str(y+5),"font-size":"10","fill":DARK,"font-weight":"bold"})
        t.text = name
        t = ET.SubElement(root, "text", {"x":str(x+25),"y":str(y+17),"font-size":"9","fill":RED,"font-weight":"bold"})
        t.text = chg

    # ARROW between
    add_arrow(root, 330, 165, 400, 165, color=DARK, width=3)
    t = ET.SubElement(root, "text", {"x":"365","y":"155","font-size":"10","fill":DARK,"text-anchor":"middle","font-weight":"bold"})
    t.text = "vs"

    # RIGHT: Semis going UP
    ET.SubElement(root, "rect", {"x":"410","y":"70","width":"280","height":"200","rx":"8","fill":WHITE,"stroke":GREEN,"stroke-width":"2"})
    t = ET.SubElement(root, "text", {"x":"550","y":"95","font-size":"14","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "费半 +1.44%"

    semis = [("Arm", "+5%"), ("博通", "+4%"), ("Wolfspeed", "+8%"), ("英特尔", "+3.46%"), ("费城半导体", "逆势涨"), ("18A-P工艺", "投产")]
    for i, (name, chg) in enumerate(semis):
        x = 450 + (i%3)*100
        y = 120 + (i//3)*40
        # up arrow
        ET.SubElement(root, "line", {"x1":str(x),"y1":str(y+15),"x2":str(x+15),"y2":str(y),"stroke":GREEN,"stroke-width":"2"})
        ET.SubElement(root, "line", {"x1":str(x),"y1":str(y),"x2":str(x+15),"y2":str(y+15),"stroke":GREEN,"stroke-width":"2"})
        t = ET.SubElement(root, "text", {"x":str(x+25),"y":str(y+5),"font-size":"10","fill":DARK,"font-weight":"bold"})
        t.text = name
        t = ET.SubElement(root, "text", {"x":str(x+25),"y":str(y+17),"font-size":"9","fill":GREEN,"font-weight":"bold"})
        t.text = chg

    # Bottom explanation
    ET.SubElement(root, "rect", {"x":"80","y":"295","width":"608","height":"80","rx":"6","fill":BLUE,"opacity":"0.08"})
    lines = [
        "利率敏感度不同：Meta/微软/亚马逊 → 高估值 + 远期现金流 → 利率↑ = 估值压缩",
        "半导体：AI算力需求刚性 + 英特尔18A-P投产 + 芯片法案 → 硬制造逻辑",
        "钱从\"讲故事\"切向\"有产能\"——这不是崩盘，是板块大轮动",
    ]
    for i, line in enumerate(lines):
        y = 318 + i*18
        t = ET.SubElement(root, "text", {"x":"384","y":str(y),"font-size":"10","fill":DARK,"text-anchor":"middle"})
        t.text = line

    # Stick figures: one holding semis flag, one looking at falling megacaps
    add_stick_figure(root, 230, 440, scale=1.0, color=RED)
    t = ET.SubElement(root, "text", {"x":"230","y":"468","font-size":"9","fill":RED,"text-anchor":"middle"})
    t.text = "重仓Mag7?"

    add_stick_figure(root, 538, 440, scale=1.0, color=GREEN)
    t = ET.SubElement(root, "text", {"x":"538","y":"468","font-size":"9","fill":GREEN,"text-anchor":"middle"})
    t.text = "切换半导体"

    t = ET.SubElement(root, "text", {"x":"384","y":"500","font-size":"11","fill":LIGHT_GRAY,"text-anchor":"middle"})
    t.text = "同是美国科技——方向却完全相反。这是\"利率敏感\"与\"需求刚性\"的对决"

    serialize(root, "panel-002.svg")


# ============ Panel 003: Asia Rising ============
def panel_003():
    root = svg()
    add_title_bar(root, "东升西降：日韩创新高，亚洲独立于Fed紧缩周期")

    # LEFT: US market (dark/rain)
    ET.SubElement(root, "rect", {"x":"30","y":"70","width":"210","height":"150","rx":"6","fill":"#FEF2F2","stroke":RED,"stroke-width":"2"})
    t = ET.SubElement(root, "text", {"x":"135","y":"95","font-size":"13","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "🇺🇸 美股"

    # Rain drops (falling)
    for drop_x in [70, 110, 150, 190]:
        for drop_y in [115, 135, 155, 175]:
            ET.SubElement(root, "line", {"x1":str(drop_x),"y1":str(drop_y),"x2":str(drop_x+3),"y2":str(drop_y+8),"stroke":RED,"stroke-width":"1.5","opacity":"0.4"})

    us_lines = ["道指 -0.98%", "纳指 -1.34%", "Meta -5%领跌", "VIX +12.37%"]
    for i, line in enumerate(us_lines):
        t = ET.SubElement(root, "text", {"x":"135","y":str(205+i*15),"font-size":"9","fill":RED,"text-anchor":"middle","font-weight":"bold"})
        t.text = line

    # CENTER: big arrow
    add_arrow(root, 250, 145, 480, 145, color=GREEN, width=3)
    t = ET.SubElement(root, "text", {"x":"365","y":"135","font-size":"11","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "资金东流 →"

    # RIGHT: Japan/Korea (sun rising)
    ET.SubElement(root, "rect", {"x":"490","y":"70","width":"248","height":"150","rx":"6","fill":"#F0FDF4","stroke":GREEN,"stroke-width":"2"})
    t = ET.SubElement(root, "text", {"x":"614","y":"95","font-size":"13","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
    t.text = "🇯🇵🇰🇷 日韩创新高"

    # Rising sun
    ET.SubElement(root, "circle", {"cx":"614","cy":"125","r":"18","fill":GREEN,"opacity":"0.2"})
    ET.SubElement(root, "circle", {"cx":"614","cy":"125","r":"10","fill":GREEN,"opacity":"0.5"})

    asia_lines = ["日经225: 71,306", "首次突破71000!", "+2.0% 领涨亚洲", "KOSPI: 8,953"]
    for i, line in enumerate(asia_lines):
        t = ET.SubElement(root, "text", {"x":"614","y":str(205+i*15),"font-size":"9","fill":GREEN,"text-anchor":"middle","font-weight":"bold"})
        t.text = line

    # Bottom: Why this is happening
    ET.SubElement(root, "rect", {"x":"30","y":"255","width":"708","height":"90","rx":"6","fill":BLUE,"opacity":"0.06"})
    why_lines = [
        "为什么日韩不跟美股跌？",
        "① 美伊协议 → 油价回落 → 亚洲制造业成本下降 → 日本出口企业利润预期上调",
        "② 日元弱势（美元走强）+ 日股估值相对美股仍低 → 国际资金再配置",
        "③ A股陆家嘴论坛政策红利 + DeepSeek资本信号 → 科技独立叙事确立",
    ]
    for i, line in enumerate(why_lines):
        y = 278 + i*18
        is_bold = "bold" if i == 0 else "normal"
        clr = DARK if i == 0 else DARK
        t = ET.SubElement(root, "text", {"x":"384","y":str(y),"font-size":"10.5" if i>0 else "12","fill":clr,"text-anchor":"middle","font-weight":is_bold})
        t.text = line

    # Stick figures
    add_stick_figure(root, 135, 420, scale=1.0, color=RED)
    t = ET.SubElement(root, "text", {"x":"135","y":"448","font-size":"9","fill":RED,"text-anchor":"middle"})
    t.text = "美股投资者"

    add_stick_figure(root, 614, 420, scale=1.0, color=GREEN)
    t = ET.SubElement(root, "text", {"x":"614","y":"448","font-size":"9","fill":GREEN,"text-anchor":"middle"})
    t.text = "亚洲投资者"

    t = ET.SubElement(root, "text", {"x":"384","y":"500","font-size":"11","fill":LIGHT_GRAY,"text-anchor":"middle"})
    t.text = "历史上，Fed鹰派=新兴市场受伤。这一次，日韩说不。"

    serialize(root, "panel-003.svg")


# ============ Panel 004: Gold vs Dollar ============
def panel_004():
    root = svg()
    add_title_bar(root, "黄金失守4300 vs 美元重回100：利率预期的跷跷板")

    # Big seesaw in center
    # Fulcrum
    ET.SubElement(root, "polygon", {"points":"384,320 370,340 398,340","fill":DARK})

    # Seesaw beam - tilted: gold side down (left), dollar side up (right)
    ET.SubElement(root, "line", {"x1":"100","y1":"220","x2":"668","y2":"370","stroke":DARK,"stroke-width":"5","stroke-linecap":"round"})

    # LEFT: Gold going down
    ET.SubElement(root, "rect", {"x":"60","y":"130","width":"180","height":"90","rx":"6","fill":"#FFF7ED","stroke":ORANGE,"stroke-width":"2.5"})
    t = ET.SubElement(root, "text", {"x":"150","y":"155","font-size":"14","fill":ORANGE,"text-anchor":"middle","font-weight":"bold"})
    t.text = "💰 黄金暴跌"

    gold_items = ["COMEX: $4,276", "-1.79%", "盘中$4,381→$4,218", "波动超$160"]
    for i, txt in enumerate(gold_items):
        clr = RED if "-" in txt else DARK
        y = 175 + i*14
        t = ET.SubElement(root, "text", {"x":"150","y":str(y),"font-size":"9","fill":clr,"text-anchor":"middle","font-weight":"bold"})
        t.text = txt

    # big down arrow under gold
    ET.SubElement(root, "line", {"x1":"150","y1":"240","x2":"150","y2":"280","stroke":RED,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"150,285 143,275 157,275","fill":RED})

    # RIGHT: Dollar going up
    ET.SubElement(root, "rect", {"x":"528","y":"330","width":"180","height":"90","rx":"6","fill":"#EFF6FF","stroke":BLUE,"stroke-width":"2.5"})
    t = ET.SubElement(root, "text", {"x":"618","y":"355","font-size":"14","fill":BLUE,"text-anchor":"middle","font-weight":"bold"})
    t.text = "💵 美元飙升"

    dxy_items = ["DXY 突破100", "+0.86%", "2Y收益率+16bp→4.22%", "10Y→4.49%"]
    for i, txt in enumerate(dxy_items):
        clr = RED if "+" in txt else DARK
        y = 375 + i*14
        t = ET.SubElement(root, "text", {"x":"618","y":str(y),"font-size":"9","fill":clr,"text-anchor":"middle","font-weight":"bold"})
        t.text = txt

    # up arrow under dollar
    ET.SubElement(root, "line", {"x1":"618","y1":"310","x2":"618","y2":"270","stroke":GREEN,"stroke-width":"3"})
    ET.SubElement(root, "polygon", {"points":"618,265 611,275 625,275","fill":GREEN})

    # Labels on seesaw
    t = ET.SubElement(root, "text", {"x":"170","y":"205","font-size":"11","fill":ORANGE,"text-anchor":"middle","font-weight":"bold"})
    t.text = "避险资产承压"

    t = ET.SubElement(root, "text", {"x":"598","y":"360","font-size":"11","fill":BLUE,"text-anchor":"middle","font-weight":"bold"})
    t.text = "美元资产受追捧"

    # Center: the driver
    ET.SubElement(root, "rect", {"x":"294","y":"390","width":"180","height":"40","rx":"6","fill":RED,"opacity":"0.1"})
    t = ET.SubElement(root, "text", {"x":"384","y":"415","font-size":"11","fill":RED,"text-anchor":"middle","font-weight":"bold"})
    t.text = "实际利率预期↑ = 金价↓"

    # Bottom stick figures + closing text
    add_stick_figure(root, 200, 465, scale=0.9, color=ORANGE)
    t = ET.SubElement(root, "text", {"x":"200","y":"490","font-size":"8","fill":ORANGE,"text-anchor":"middle"})
    t.text = "黄金多头"

    add_stick_figure(root, 568, 465, scale=0.9, color=BLUE)
    t = ET.SubElement(root, "text", {"x":"568","y":"490","font-size":"8","fill":BLUE,"text-anchor":"middle"})
    t.text = "美元多头"

    t = ET.SubElement(root, "text", {"x":"384","y":"500","font-size":"11","fill":LIGHT_GRAY,"text-anchor":"middle"})
    t.text = "FOMC鹰派信号 → 实际利率↑ → 黄金失血。但亚洲盘已在$4,280出现抄底盘"

    serialize(root, "panel-004.svg")


if __name__ == "__main__":
    print("Generating Dalio SVG comics for 2026-06-18 morning...")
    panel_001()
    panel_002()
    panel_003()
    panel_004()
    print("Done! All panels generated.")
