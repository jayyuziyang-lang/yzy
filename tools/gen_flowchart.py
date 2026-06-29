#!/usr/bin/env python3
"""生成软件流程图SVG - 快递包裹运输控制系统"""

W, H = 650, 950

# Flow chart nodes as boxes
# Format: (id, text, x, y, w, h, shape_type, fill_color)
# shape_type: 'box' | 'diamond' | 'startend'

nodes = [
    # Start
    ('start', '开始\n(系统上电初始化)', 325, 30, 140, 45, 'startend', '#1A56DB'),
    # Init
    ('init', '参数初始化\nD0=1(默认低速)\nM0=0, M1=0', 325, 100, 160, 55, 'box', '#E8F0FE'),
    # Check E-Stop
    ('chk_estop', '急停按钮\n是否释放?', 325, 185, 130, 50, 'diamond', '#FFF3CD'),
    # Wait for start
    ('wait_start', '等待启动按钮\n+ 确认按钮', 325, 270, 150, 50, 'box', '#E8F0FE'),
    # Check start
    ('chk_start', '启动+确认\n是否按下?', 325, 350, 130, 50, 'diamond', '#FFF3CD'),
    # Set run
    ('set_run', 'M0=1 运行使能\n电机默认正转 Y000=1\n运行灯Y002 1s闪烁', 325, 430, 180, 55, 'box', '#D4EDDA'),
    # Main loop
    ('loop', '主循环\n扫描输入信号', 325, 515, 140, 45, 'box', '#E8F0FE'),
    # Check direction
    ('chk_dir', '方向按钮\n按下?', 325, 590, 110, 50, 'diamond', '#FFF3CD'),
    # Toggle dir
    ('toggle_dir', '翻转M1\n切换正/反转', 500, 595, 120, 45, 'box', '#FCE4D6'),
    # Check speed up
    ('chk_spup', '加速按钮\n按下?', 325, 670, 110, 50, 'diamond', '#FFF3CD'),
    # Speed up
    ('sp_up', 'D0+1\n(上限3)', 500, 675, 100, 40, 'box', '#FCE4D6'),
    # Check speed down
    ('chk_spdn', '减速按钮\n按下?', 325, 750, 110, 50, 'diamond', '#FFF3CD'),
    # Speed down
    ('sp_dn', 'D0-1\n(下限0)', 500, 755, 100, 40, 'box', '#FCE4D6'),
    # Check stop
    ('chk_stop', '停止按钮\n或急停?', 325, 830, 110, 50, 'diamond', '#FFF3CD'),
    # Stop
    ('stop_act', 'M0=0 停止\n所有输出复位', 150, 835, 140, 45, 'box', '#F8D7DA'),
    # End
    ('end', '结束', 150, 910, 100, 35, 'startend', '#6C757D'),
]


def draw_arrow(lines, x1, y1, x2, y2):
    """Draw an arrow from (x1,y1) to (x2,y2)"""
    lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')


def draw_polyline(lines, points):
    """Draw a polyline"""
    pts = ' '.join(f'{x},{y}' for x, y in points)
    lines.append(f'<polyline points="{pts}" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')


def draw_label(lines, x, y, text, color='#333', size=10):
    lines.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="{color}">{text}</text>')


def make_flowchart():
    lines = []
    lines.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">')

    lines.append('<defs>')
    lines.append('  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">')
    lines.append('    <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>')
    lines.append('  </marker>')
    lines.append('</defs>')

    # Background
    lines.append(f'<rect width="{W}" height="{H}" fill="#FAFBFC"/>')

    # Title
    lines.append(f'<text x="{W/2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1A56DB">快递包裹运输控制系统 — 软件流程图</text>')
    lines.append(f'<text x="{W/2}" y="46" text-anchor="middle" font-size="10" fill="#666">主程序循环扫描工作方式 | 变频器多段速 | 正反转互锁</text>')

    # Draw all nodes first
    for node in nodes:
        nid, text, cx, cy, w, h, shape, color = node
        x = cx - w // 2
        y = cy - h // 2

        if shape == 'startend':
            # Rounded rectangle
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" ry="20" fill="{color}" stroke="{color}" stroke-width="1.5"/>')
            # White text
            for li, line in enumerate(text.split('\n')):
                ly = cy - (len(text.split('\n'))-1)*7 + li*14
                lines.append(f'<text x="{cx}" y="{ly+5}" text-anchor="middle" font-size="10" fill="white" font-weight="bold">{line}</text>')

        elif shape == 'diamond':
            # Diamond: (cx, y), (x+w/2, cy), (cx, y+h), (x, cy)
            diamond_pts = f'{cx},{y} {x+w},{cy} {cx},{y+h} {x},{cy}'
            lines.append(f'<polygon points="{diamond_pts}" fill="{color}" stroke="#856404" stroke-width="1.5"/>')
            for li, line in enumerate(text.split('\n')):
                ly = cy - (len(text.split('\n'))-1)*7 + li*14
                lines.append(f'<text x="{cx}" y="{ly+5}" text-anchor="middle" font-size="9.5" fill="#856404">{line}</text>')

        elif shape == 'box':
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{color}" stroke="#1A56DB" stroke-width="1.2"/>')
            for li, line in enumerate(text.split('\n')):
                ly = cy - (len(text.split('\n'))-1)*7 + li*14
                lines.append(f'<text x="{cx}" y="{ly+5}" text-anchor="middle" font-size="9.5" fill="#1a1a1a">{line}</text>')

    # Draw connections (arrows)
    connections = [
        # start -> init (vertical down)
        ('start', 'init', 'down', ''),
        # init -> chk_estop
        ('init', 'chk_estop', 'down', ''),
        # chk_estop -> wait_start (YES - released)
        ('chk_estop', 'wait_start', 'right', '是'),
        # wait_start -> chk_start
        ('wait_start', 'chk_start', 'down', ''),
        # chk_start -> set_run (YES)
        ('chk_start', 'set_run', 'right', '是'),
        # chk_start -> wait_start (NO - loop back)
        ('chk_start', 'wait_start', 'left_loop', '否'),
        # set_run -> loop
        ('set_run', 'loop', 'down', ''),
        # loop -> chk_dir
        ('loop', 'chk_dir', 'down', ''),
        # chk_dir -> toggle_dir (YES)
        ('chk_dir', 'toggle_dir', 'right', '是'),
        # chk_dir -> chk_spup (NO - skip)
        ('chk_dir', 'chk_spup', 'bottom', '否'),
        # toggle_dir -> chk_spup
        ('toggle_dir', 'chk_spup', 'down', ''),
        # chk_spup -> sp_up (YES)
        ('chk_spup', 'sp_up', 'right', '是'),
        # chk_spup -> chk_spdn (NO)
        ('chk_spup', 'chk_spdn', 'bottom', '否'),
        # sp_up -> chk_spdn
        ('sp_up', 'chk_spdn', 'down', ''),
        # chk_spdn -> sp_dn (YES)
        ('chk_spdn', 'sp_dn', 'right', '是'),
        # chk_spdn -> chk_stop (NO)
        ('chk_spdn', 'chk_stop', 'bottom', '否'),
        # sp_dn -> chk_stop
        ('sp_dn', 'chk_stop', 'down', ''),
        # chk_stop -> stop_act (YES)
        ('chk_stop', 'stop_act', 'left', '是'),
        # chk_stop -> loop (NO - continue)
        ('chk_stop', 'loop', 'right_loop', '否'),
        # stop_act -> end
        ('stop_act', 'end', 'down', ''),
        # chk_estop -> stop_act (NO - estop pressed)
        ('chk_estop', 'stop_act', 'left_estop', '急停'),
    ]

    # Node coordinate lookup
    node_coords = {}
    for node in nodes:
        nid, text, cx, cy, w, h, shape, color = node
        node_coords[nid] = (cx, cy, w, h, shape)

    for conn in connections:
        from_id, to_id, direction, label = conn
        fx, fy, fw, fh, fshape = node_coords[from_id]
        tx, ty, tw, th, tshape = node_coords[to_id]

        if direction == 'down':
            y1 = fy + fh // 2
            y2 = ty - th // 2
            # For diamond, adjust
            if fshape == 'diamond':
                y1 = fy + fh // 2
            if tshape == 'diamond':
                y2 = ty - th // 2
            lines.append(f'<line x1="{fx}" y1="{y1}" x2="{tx}" y2="{y2}" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')
            if label:
                draw_label(lines, fx + 18, (y1 + y2) / 2 + 4, label, '#856404', 9)

        elif direction == 'right':
            x1 = fx + fw // 2
            x2 = tx - tw // 2
            if tshape == 'diamond':
                x2 = tx - tw // 2
            lines.append(f'<line x1="{x1}" y1="{fy}" x2="{x2}" y2="{ty}" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')
            if label:
                draw_label(lines, (x1 + x2) / 2, fy - 8, label, '#856404', 9)

        elif direction == 'bottom':
            # Go straight down from bottom of diamond to next diamond center
            y1_val = fy + fh // 2
            y2_val = ty - th // 2
            lines.append(f'<line x1="{fx}" y1="{y1_val}" x2="{tx}" y2="{y2_val}" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')
            if label:
                draw_label(lines, fx + 18, (y1_val + y2_val) / 2 + 4, label, '#856404', 9)

        elif direction == 'left_loop':
            # Loop back left and up (从chk_start左方绕回wait_start)
            x_start = fx - fw // 2
            y_mid = fy - 50
            points = [(x_start, fy), (x_start - 30, fy), (x_start - 30, y_mid), (tx, y_mid), (tx, ty + th // 2)]
            pts_str = ' '.join(f'{x},{y}' for x, y in points)
            lines.append(f'<polyline points="{pts_str}" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')
            draw_label(lines, x_start - 30, fy - 25, label, '#DC2626', 9)

        elif direction == 'right_loop':
            # Loop back right and up (从chk_stop右方绕回loop)
            x_start = fx + fw // 2
            points = [(x_start, fy), (x_start + 30, fy), (x_start + 30, ty), (tx + tw // 2, ty)]
            pts_str = ' '.join(f'{x},{y}' for x, y in points)
            lines.append(f'<polyline points="{pts_str}" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')
            draw_label(lines, x_start + 32, ty - 10, label, '#856404', 9)

        elif direction == 'left_estop':
            # From estop diamond left to stop_act (急停)
            x1 = fx - fw // 2
            x2 = tx + tw // 2
            lines.append(f'<line x1="{x1}" y1="{fy}" x2="{x2}" y2="{ty}" stroke="#DC2626" stroke-width="2" marker-end="url(#arrowhead)"/>')
            draw_label(lines, (x1 + x2) / 2, fy - 12, label, '#DC2626', 10)

        elif direction == 'left':
            # Go left
            x1 = fx - fw // 2
            x2 = tx + tw // 2
            lines.append(f'<line x1="{x1}" y1="{fy}" x2="{x2}" y2="{ty}" stroke="#333" stroke-width="1.5" marker-end="url(#arrowhead)"/>')
            if label:
                draw_label(lines, (x1 + x2) / 2, fy - 8, label, '#856404', 9)

    # Legend
    ly = 60
    lines.append(f'<rect x="{W-180}" y="55" width="170" height="95" fill="white" stroke="#ddd" stroke-width="1" rx="4"/>')
    draw_label(lines, W-95, ly, '图例', '#333', 10)
    ly += 18
    # Box
    lines.append(f'<rect x="{W-170}" y="{ly}" width="20" height="14" fill="#E8F0FE" stroke="#1A56DB" stroke-width="1" rx="2"/>')
    draw_label(lines, W-130, ly+12, '处理过程', '#333', 9)
    ly += 20
    # Diamond
    lines.append(f'<polygon points="{W-160},{ly+7} {W-150},{ly} {W-160},{ly-7} {W-170},{ly}" fill="#FFF3CD" stroke="#856404" stroke-width="1"/>')
    draw_label(lines, W-130, ly+5, '判断分支', '#333', 9)
    ly += 20
    # Start/end
    lines.append(f'<rect x="{W-170}" y="{ly-7}" width="20" height="14" fill="#1A56DB" rx="7"/>')
    draw_label(lines, W-130, ly+5, '开始/结束', '#333', 9)

    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    import os
    svg = make_flowchart()
    out_path = r'D:\Desktop\每日财经\tools\software_flowchart.svg'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'Flowchart saved to: {out_path}')
    print(f'Size: {len(svg)} bytes')
