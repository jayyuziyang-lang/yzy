#!/usr/bin/env python3
"""批量生成三个PLC控制系统的软件流程图SVG"""

import os, sys
sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r'D:\Desktop\CAD1'
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 650, 980

def flow_svg_header(title, lines):
    lines.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">')
    lines.append('<defs>')
    lines.append('  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">')
    lines.append('    <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>')
    lines.append('  </marker>')
    lines.append('  <marker id="arrow-red" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">')
    lines.append('    <polygon points="0 0, 10 3.5, 0 7" fill="#DC2626"/>')
    lines.append('  </marker>')
    lines.append('</defs>')
    lines.append(f'<rect width="{W}" height="{H}" fill="#FAFBFC"/>')
    lines.append(f'<text x="{W/2}" y="22" text-anchor="middle" font-size="15" font-weight="bold" fill="#1A56DB">{title}</text>')


def flow_node(lines, nid, text, cx, cy, w, h, shape, color):
    """Draw a flowchart node"""
    x, y = cx - w//2, cy - h//2
    lines_list = text.split('\n')
    if shape == 'startend':
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" ry="18" fill="{color}" stroke="{color}" stroke-width="1.5"/>')
        for li, line in enumerate(lines_list):
            ly = cy - (len(lines_list)-1)*7 + li*14
            lines.append(f'<text x="{cx}" y="{ly+5}" text-anchor="middle" font-size="10" fill="white" font-weight="bold">{line}</text>')
    elif shape == 'diamond':
        lines.append(f'<polygon points="{cx},{y} {x+w},{cy} {cx},{y+h} {x},{cy}" fill="{color}" stroke="#856404" stroke-width="1.5"/>')
        for li, line in enumerate(lines_list):
            ly = cy - (len(lines_list)-1)*7 + li*14
            lines.append(f'<text x="{cx}" y="{ly+5}" text-anchor="middle" font-size="9.5" fill="#856404">{line}</text>')
    elif shape == 'box':
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{color}" stroke="#1A56DB" stroke-width="1.2"/>')
        for li, line in enumerate(lines_list):
            ly = cy - (len(lines_list)-1)*7 + li*14
            lines.append(f'<text x="{cx}" y="{ly+5}" text-anchor="middle" font-size="9.5" fill="#1a1a1a">{line}</text>')


def flow_arrow(lines, x1, y1, x2, y2, color='#333', marker='url(#arrowhead)'):
    lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="{marker}"/>')


def flow_polyline(lines, points, color='#333', marker='url(#arrowhead)'):
    pts = ' '.join(f'{x},{y}' for x,y in points)
    lines.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5" marker-end="{marker}"/>')


def flow_label(lines, x, y, text, color='#333', size=9):
    lines.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{color}">{text}</text>')


def add_legend(lines):
    ly = 40
    lines.append(f'<rect x="{W-180}" y="32" width="170" height="90" fill="white" stroke="#ddd" stroke-width="1" rx="4"/>')
    flow_label(lines, W-95, ly+5, '图例', '#333', 10)
    ly += 15
    lines.append(f'<rect x="{W-168}" y="{ly}" width="18" height="12" fill="#E8F0FE" stroke="#1A56DB" stroke-width="1" rx="2"/>')
    flow_label(lines, W-128, ly+10, '处理过程', '#333', 9)
    ly += 18
    lines.append(f'<polygon points="{W-159},{ly+6} {W-150},{ly} {W-159},{ly-6} {W-168},{ly}" fill="#FFF3CD" stroke="#856404" stroke-width="1"/>')
    flow_label(lines, W-128, ly+5, '判断分支', '#333', 9)
    ly += 18
    lines.append(f'<rect x="{W-168}" y="{ly-6}" width="18" height="12" fill="#1A56DB" rx="6"/>')
    flow_label(lines, W-128, ly+2, '开始/结束', '#333', 9)


# ============================================================
# 系统1: 混凝土搅拌控制系统 流程图
# ============================================================
def gen_concrete_mixer_flow():
    lines = []
    flow_svg_header('混凝土搅拌控制系统 — 软件流程图', lines)

    nodes = [
        ('start','开始\n(系统上电)',325,45,120,38,'startend','#1A56DB'),
        ('init','初始化\nD0=1(默认20Hz)',325,108,140,42,'box','#E8F0FE'),
        ('chk_estop','急停\n按下?',325,165,100,45,'diamond','#FFF3CD'),
        ('wait_start','等待启动按钮',325,232,130,40,'box','#E8F0FE'),
        ('chk_start','启动\n按下?',325,292,100,45,'diamond','#FFF3CD'),
        ('start_run','M0=1 运行使能\nY000=1 正转 6s\nT0开始计时',325,360,170,50,'box','#D4EDDA'),
        ('chk_t0','T0=6s\n正转时间到?',325,430,110,45,'diamond','#FFF3CD'),
        ('rev_run','切换反转 Y001=1\nY000=0\nT1计时 6s',325,505,170,50,'box','#FCE4D6'),
        ('chk_t1','T1=6s\n反转时间到?',325,580,110,45,'diamond','#FFF3CD'),
        ('chk_stop','停止\n按下?',325,655,100,45,'diamond','#FFF3CD'),
        ('stop_delay','停止延时3s\nT2=K30',500,660,120,40,'box','#F8D7DA'),
        ('end','结束\nM0=0 全部复位',500,725,120,38,'startend','#6C757D'),
        ('chk_speed','速度选择\n变化?',175,440,100,45,'diamond','#FFF3CD'),
        ('set_speed','更新速度输出\nY010/Y011/Y012',60,500,130,40,'box','#E8F0FE'),
    ]

    # Draw all nodes
    for n in nodes:
        flow_node(lines, *n)

    # Connections
    # start -> init
    flow_arrow(lines, 325, 64, 325, 87)
    # init -> chk_estop
    flow_arrow(lines, 325, 129, 325, 142)
    # chk_estop -> wait_start (NO=未按下)
    flow_label(lines, 270, 172, '否', '#856404', 9)
    flow_arrow(lines, 275, 165, 275, 212)  # left branch
    flow_arrow(lines, 275, 212, 325, 212)
    # chk_estop -> end (YES=急停)
    flow_label(lines, 408, 168, '是', '#DC2626', 9)
    # wait_start -> chk_start
    flow_arrow(lines, 325, 252, 325, 269)
    # chk_start -> start_run (YES)
    flow_label(lines, 395, 298, '是', '#856404', 9)
    flow_arrow(lines, 375, 292, 375, 335)
    flow_arrow(lines, 375, 335, 325, 335)
    # chk_start -> wait_start (NO)
    flow_label(lines, 270, 298, '否', '#856404', 9)
    flow_polyline(lines, [(275,292),(275,250),(280,250)])
    # start_run -> chk_t0
    flow_arrow(lines, 325, 385, 325, 407)
    # chk_t0 -> rev_run (YES)
    flow_label(lines, 395, 436, '是', '#856404', 9)
    flow_arrow(lines, 380, 430, 380, 480)
    flow_arrow(lines, 380, 480, 325, 480)
    # chk_t0 -> chk_t0 (NO, wait)
    flow_polyline(lines, [(270,430),(270,400),(290,400)])
    flow_label(lines, 250, 415, '否,等待', '#856404', 9)
    # rev_run -> chk_t1
    flow_arrow(lines, 325, 530, 325, 557)
    # chk_t1 -> start_run (YES, next cycle)
    flow_label(lines, 420, 586, '是', '#856404', 9)
    flow_polyline(lines, [(380,580),(380,340),(380,340)])
    # chk_t1 -> chk_t1 (NO)
    flow_polyline(lines, [(270,580),(270,550),(290,550)])
    flow_label(lines, 250, 565, '否,等待', '#856404', 9)
    # During forward/reverse, check stop
    # chk_stop -> stop_delay (YES)
    flow_label(lines, 408, 662, '是', '#DC2626', 9)
    flow_arrow(lines, 375, 655, 500, 660, '#DC2626', 'url(#arrow-red)')
    # chk_stop -> continue loop (NO)
    flow_polyline(lines, [(325,700),(325,430)])
    flow_label(lines, 340, 680, '否,继续运行', '#856404', 9)
    # stop_delay -> end
    flow_arrow(lines, 500, 680, 500, 706)
    # Emergency stop path
    flow_polyline(lines, [(375,165),(500,142),(500,660)], '#DC2626', 'url(#arrow-red)')

    add_legend(lines)
    lines.append('</svg>')

    path = os.path.join(OUT_DIR, '软件流程图_混凝土搅拌控制系统.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {path} ({len("\n".join(lines))} bytes)')


# ============================================================
# 系统2: 简易轮毂打紧机控制系统 流程图
# ============================================================
def gen_hub_tightener_flow():
    lines = []
    flow_svg_header('简易轮毂打紧机控制系统 — 软件流程图', lines)

    nodes = [
        ('start','开始\n(系统上电)',325,46,120,38,'startend','#1A56DB'),
        ('init','初始化\nM1=0 M2=0 D0=1',325,110,150,42,'box','#E8F0FE'),
        ('chk_fwd','正转键\n按下?',200,175,95,45,'diamond','#FFF3CD'),
        ('chk_rev','反转键\n按下?',450,175,95,45,'diamond','#FFF3CD'),
        ('fwd_run','M1=1 正转使能\nY000=1 电机正转\nY003=1 正转灯亮\n流水灯启动',200,255,160,55,'box','#D4EDDA'),
        ('rev_run','M2=1 反转使能\nY001=1 电机反转\nY004=1 反转灯亮\n流水灯启动',450,255,160,55,'box','#FCE4D6'),
        ('chk_fwd_lim','正转限位\n到达?',200,340,100,45,'diamond','#FFF3CD'),
        ('chk_rev_lim','反转限位\n到达?',450,340,100,45,'diamond','#FFF3CD'),
        ('fwd_stop','M1=0 停止正转\nY000=0 灯灭',200,418,140,42,'box','#F8D7DA'),
        ('rev_stop','M2=0 停止反转\nY001=0 灯灭',450,418,140,42,'box','#F8D7DA'),
        ('chk_stop','停止\n按下?',325,500,95,45,'diamond','#FFF3CD'),
        ('all_stop','全部复位\nM1=0 M2=0\nY全部=0',325,575,140,50,'box','#F8D7DA'),
        ('end','结束',325,658,100,35,'startend','#6C757D'),
        ('water_lights','4流水灯循环\nT10/T11 1s周期\nY005→Y006→Y007→Y010',325,490,170,55,'box','#E8F0FE'),
    ]

    for n in nodes:
        flow_node(lines, *n)

    # Connections
    flow_arrow(lines, 325, 65, 325, 89)
    flow_arrow(lines, 325, 131, 200, 152)
    flow_arrow(lines, 325, 131, 450, 152)
    # Forward branch
    flow_label(lines, 255, 182, '是', '#856404', 9)
    flow_arrow(lines, 200, 197, 200, 227)
    flow_label(lines, 140, 182, '否', '#856404', 9)
    # Reverse branch
    flow_label(lines, 508, 182, '是', '#856404', 9)
    flow_arrow(lines, 450, 197, 450, 227)
    flow_label(lines, 390, 182, '否', '#856404', 9)
    # Forward limit check
    flow_arrow(lines, 200, 282, 200, 317)
    flow_label(lines, 260, 346, '是', '#DC2626', 9)
    flow_arrow(lines, 250, 340, 250, 397)
    flow_arrow(lines, 250, 397, 200, 397)
    flow_polyline(lines, [(150,340),(150,310),(180,310)])
    flow_label(lines, 130, 325, '否,继续', '#856404', 9)
    # Reverse limit check
    flow_arrow(lines, 450, 282, 450, 317)
    flow_label(lines, 510, 346, '是', '#DC2626', 9)
    flow_arrow(lines, 500, 340, 500, 397)
    flow_arrow(lines, 500, 397, 450, 397)
    flow_polyline(lines, [(400,340),(400,310),(430,310)])
    flow_label(lines, 380, 325, '否,继续', '#856404', 9)
    # To water lights
    flow_arrow(lines, 200, 439, 200, 465)
    flow_arrow(lines, 200, 465, 325, 465)
    flow_arrow(lines, 450, 439, 450, 465)
    flow_arrow(lines, 450, 465, 325, 465)
    # Water lights to stop check
    flow_arrow(lines, 325, 517, 325, 477)
    # Stop check
    flow_arrow(lines, 325, 545, 325, 547)
    flow_label(lines, 388, 506, '是', '#DC2626', 9)
    flow_arrow(lines, 375, 500, 375, 547)
    flow_arrow(lines, 375, 547, 325, 547)
    flow_polyline(lines, [(325,500),(250,500),(250,175)])
    flow_label(lines, 270, 490, '否,返回主循环', '#856404', 9)
    # all_stop -> end
    flow_arrow(lines, 325, 600, 325, 640)

    add_legend(lines)
    lines.append('</svg>')

    path = os.path.join(OUT_DIR, '软件流程图_简易轮毂打紧机控制系统.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {path} ({len("\n".join(lines))} bytes)')


# ============================================================
# 系统3: 电动葫芦控制系统 流程图
# ============================================================
def gen_electric_hoist_flow():
    lines = []
    flow_svg_header('电动葫芦控制系统 — 软件流程图', lines)

    nodes = [
        ('start','开始\n(系统上电)',325,46,120,38,'startend','#1A56DB'),
        ('init','初始化\nM1=0 M2=0 D0=1',325,110,150,42,'box','#E8F0FE'),
        ('chk_up','上升键\n按下?',190,180,95,45,'diamond','#FFF3CD'),
        ('chk_down','下降键\n按下?',460,180,95,45,'diamond','#FFF3CD'),
        ('up_run','M1=1 上升使能\nY000=1 电机正转\nY003=1 上升灯亮\n6流水灯启动',190,265,165,55,'box','#D4EDDA'),
        ('down_run','M2=1 下降使能\nY001=1 电机反转\nY004=1 下降灯亮\n6流水灯启动',460,265,165,55,'box','#FCE4D6'),
        ('chk_up_lim','上限位\n到达?',190,350,100,45,'diamond','#FFF3CD'),
        ('chk_down_lim','下限位\n到达?',460,350,100,45,'diamond','#FFF3CD'),
        ('up_stop','M1=0 停止上升\nY000=0 上升灯灭',190,430,150,42,'box','#F8D7DA'),
        ('down_stop','M2=0 停止下降\nY001=0 下降灯灭',460,430,150,42,'box','#F8D7DA'),
        ('water_lights','6流水灯循环\nT20/T21 1s周期\nY005→Y006→Y007\n→Y010→Y011→Y012',325,520,175,55,'box','#E8F0FE'),
        ('chk_stop','停止\n按下?',325,608,95,45,'diamond','#FFF3CD'),
        ('all_stop','全部复位\nM1=0 M2=0\nY全部=0',325,683,140,50,'box','#F8D7DA'),
        ('end','结束',325,760,100,35,'startend','#6C757D'),
        ('chk_estop','急停\n按下?',50,350,90,45,'diamond','#FFF3CD'),
    ]

    for n in nodes:
        flow_node(lines, *n)

    # Connections
    flow_arrow(lines, 325, 65, 325, 89)
    flow_arrow(lines, 325, 131, 190, 157)
    flow_arrow(lines, 325, 131, 460, 157)
    # Up branch
    flow_label(lines, 245, 187, '是', '#856404', 9)
    flow_arrow(lines, 190, 202, 190, 237)
    flow_label(lines, 130, 187, '否', '#856404', 9)
    # Down branch
    flow_label(lines, 515, 187, '是', '#856404', 9)
    flow_arrow(lines, 460, 202, 460, 237)
    # Up limit check
    flow_arrow(lines, 190, 292, 190, 327)
    flow_label(lines, 250, 356, '是', '#DC2626', 9)
    flow_arrow(lines, 240, 350, 240, 409)
    flow_arrow(lines, 240, 409, 190, 409)
    flow_polyline(lines, [(140,350),(140,320),(170,320)])
    flow_label(lines, 120, 335, '否,继续', '#856404', 9)
    # Down limit check
    flow_arrow(lines, 460, 292, 460, 327)
    flow_label(lines, 518, 356, '是', '#DC2626', 9)
    flow_arrow(lines, 510, 350, 510, 409)
    flow_arrow(lines, 510, 409, 460, 409)
    flow_polyline(lines, [(410,350),(410,320),(440,320)])
    flow_label(lines, 390, 335, '否,继续', '#856404', 9)
    # To water lights
    flow_arrow(lines, 190, 451, 190, 490)
    flow_arrow(lines, 190, 490, 325, 490)
    flow_arrow(lines, 460, 451, 460, 490)
    flow_arrow(lines, 460, 490, 325, 490)
    # Water lights to stop
    flow_arrow(lines, 325, 547, 325, 585)
    # Stop check
    flow_label(lines, 388, 614, '是', '#DC2626', 9)
    flow_arrow(lines, 373, 608, 325, 655)
    flow_polyline(lines, [(325,608),(250,608),(250,180)])
    flow_label(lines, 270, 598, '否,返回主循环', '#856404', 9)
    # all_stop -> end
    flow_arrow(lines, 325, 708, 325, 742)
    # Emergency stop path
    flow_polyline(lines, [(50,372),(50,655),(185,655)], '#DC2626', 'url(#arrow-red)')
    flow_label(lines, 90, 625, '是,急停', '#DC2626', 9)

    add_legend(lines)
    lines.append('</svg>')

    path = os.path.join(OUT_DIR, '软件流程图_电动葫芦控制系统.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {path} ({len("\n".join(lines))} bytes)')


if __name__ == '__main__':
    gen_concrete_mixer_flow()
    gen_hub_tightener_flow()
    gen_electric_hoist_flow()
    print('\n全部流程图生成完成!')
