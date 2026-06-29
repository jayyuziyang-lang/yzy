#!/usr/bin/env python3
"""生成PLC梯形图SVG - 快递包裹运输控制系统"""

W = 820
rung_h = 95
left_rail = 50
right_rail = 710
rail_w = 4
contact_y_offset = 38
coil_x = 600

rungs = []

# ---- Rung 1: System Run Enable (Self-holding) ----
rungs.append({
    'label': '梯级1: 系统运行使能(自锁电路)',
    'elements': [
        {'type': 'NO', 'label': 'X000\n启动', 'x': 80},
        {'type': 'NO', 'label': 'X002\n确认', 'x': 170},
        {'type': 'NC', 'label': 'X001\n停止', 'x': 260},
        {'type': 'NC', 'label': 'X004\n急停', 'x': 350},
        {'type': 'COIL', 'label': 'M0\n运行使能', 'x': coil_x},
    ]
})

# ---- Rung 2: Direction Toggle Pulse ----
rungs.append({
    'label': '梯级2: 方向切换(上升沿脉冲)',
    'elements': [
        {'type': 'NO', 'label': 'X003\n方向', 'x': 80},
        {'type': 'FUNC', 'label': 'PLS\nM10', 'x': 170},
    ]
})

# ---- Rung 3: Direction Flip-Flop ----
rungs.append({
    'label': '梯级3: 方向记忆(交替翻转)',
    'elements': [
        {'type': 'NO', 'label': 'M10\n脉冲', 'x': 80},
        {'type': 'FUNC', 'label': 'ALT\nM1', 'x': 170},
    ]
})

# ---- Rung 4: Forward Output ----
rungs.append({
    'label': '梯级4: 正转输出(M1=OFF时正转, 含互锁)',
    'elements': [
        {'type': 'NO', 'label': 'M0\n运行', 'x': 80},
        {'type': 'NC', 'label': 'M1\n方向', 'x': 170},
        {'type': 'NC', 'label': 'Y001\n反转\n互锁', 'x': 260},
        {'type': 'COIL', 'label': 'Y000\n正转', 'x': coil_x},
    ]
})

# ---- Rung 5: Reverse Output ----
rungs.append({
    'label': '梯级5: 反转输出(M1=ON时反转, 含互锁)',
    'elements': [
        {'type': 'NO', 'label': 'M0\n运行', 'x': 80},
        {'type': 'NO', 'label': 'M1\n方向', 'x': 170},
        {'type': 'NC', 'label': 'Y000\n正转\n互锁', 'x': 260},
        {'type': 'COIL', 'label': 'Y001\n反转', 'x': coil_x},
    ]
})

# ---- Rung 6: Flashing Circuit ----
rungs.append({
    'label': '梯级6: 闪烁电路(0.5s ON + 0.5s OFF = 1s周期)',
    'elements': [
        {'type': 'NO', 'label': 'M0\n运行', 'x': 80},
        {'type': 'NC', 'label': 'T1', 'x': 160},
        {'type': 'COIL', 'label': 'T0\nK5', 'x': 250},
        {'type': 'NO', 'label': 'T0', 'x': 330},
        {'type': 'COIL', 'label': 'T1\nK5', 'x': 410},
        {'type': 'NO', 'label': 'M0\n运行', 'x': 490},
        {'type': 'NO', 'label': 'T0', 'x': 560},
        {'type': 'COIL', 'label': 'Y002\n红灯', 'x': 640},
    ]
})

# ---- Rung 7: Speed Control ----
rungs.append({
    'label': '梯级7: 速度调节(加速/减速按钮, D0范围0-3)',
    'elements': [
        {'type': 'NO', 'label': 'X005\n加速', 'x': 80},
        {'type': 'FUNC', 'label': 'INCP\nD0', 'x': 190},
        {'type': 'NO', 'label': 'X006\n减速', 'x': 310},
        {'type': 'FUNC', 'label': 'DECP\nD0', 'x': 420},
    ]
})

# ---- Rung 8: Status Indicators ----
rungs.append({
    'label': '梯级8: 状态指示灯(正转绿灯, 反转黄灯)',
    'elements': [
        {'type': 'NO', 'label': 'Y000\n正转', 'x': 80},
        {'type': 'COIL', 'label': 'Y003\n正转灯', 'x': 200},
        {'type': 'NO', 'label': 'Y001\n反转', 'x': 310},
        {'type': 'COIL', 'label': 'Y004\n反转灯', 'x': 430},
    ]
})

# ---- Rung 9: Speed Output to VFD ----
rungs.append({
    'label': '梯级9: 速度输出至变频器(多段速: D0=1低速, D0=2中速, D0=3高速)',
    'elements': [
        {'type': 'FUNC', 'label': '=\nD0 K1', 'x': 80},
        {'type': 'COIL', 'label': 'Y010\n低速', 'x': 180},
        {'type': 'FUNC', 'label': '=\nD0 K2', 'x': 290},
        {'type': 'COIL', 'label': 'Y011\n中速', 'x': 390},
        {'type': 'FUNC', 'label': '=\nD0 K3', 'x': 500},
        {'type': 'COIL', 'label': 'Y012\n高速', 'x': 600},
    ]
})


def make_svg():
    total_h = len(rungs) * rung_h + 60 + 280

    lines = []
    lines.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total_h}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">')
    lines.append('<style>')
    lines.append('  text { font-size: 11px; fill: #1a1a1a; }')
    lines.append('  .io-label { font-size: 9px; fill: #333; text-anchor: middle; }')
    lines.append('  .contact-no { fill: none; stroke: #1a1a1a; stroke-width: 1.5; }')
    lines.append('  .func-box { fill: #f5f5f5; stroke: #1a1a1a; stroke-width: 1.5; }')
    lines.append('  .wire { stroke: #1a1a1a; stroke-width: 1.5; fill: none; }')
    lines.append('  .rung-label { font-size: 10px; fill: #666; text-anchor: middle; }')
    lines.append('  .rail { fill: #333; }')
    lines.append('</style>')

    # Background
    lines.append(f'<rect width="{W}" height="{total_h}" fill="#FAFBFC"/>')

    # Title
    lines.append(f'<text x="{W/2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1A56DB">快递包裹运输控制系统 — PLC梯形图</text>')
    lines.append(f'<text x="{W/2}" y="48" text-anchor="middle" font-size="11" fill="#666">PLC: 三菱FX3U | 变频器多段速 | 闪烁周期1s | 正反转互锁</text>')

    rung_start_y = 65

    for i, rung in enumerate(rungs):
        y = rung_start_y + i * rung_h
        ey = y + contact_y_offset

        # Background grid line
        lines.append(f'<rect x="0" y="{y-5}" width="{W}" height="{rung_h-2}" fill="none" stroke="#e8e8e8" stroke-width="0.5"/>')

        # Left rail
        lines.append(f'<rect x="{left_rail}" y="{y}" width="{rail_w}" height="{rung_h-15}" class="rail"/>')

        # Right rail
        lines.append(f'<rect x="{right_rail}" y="{y}" width="{rail_w}" height="{rung_h-15}" class="rail"/>')

        # Main horizontal bus wire
        lines.append(f'<line x1="{left_rail + rail_w}" y1="{ey}" x2="{right_rail}" y2="{ey}" class="wire"/>')

        # Rung label at bottom
        lines.append(f'<text x="{W/2}" y="{y + rung_h - 8}" text-anchor="middle" class="rung-label">{rung["label"]}</text>')

        for elem in rung['elements']:
            ex = elem['x']

            if elem['type'] == 'NO':
                # Vertical lines up and down
                lines.append(f'<line x1="{ex}" y1="{ey-10}" x2="{ex}" y2="{ey-18}" class="contact-no"/>')
                lines.append(f'<line x1="{ex}" y1="{ey+10}" x2="{ex}" y2="{ey+18}" class="contact-no"/>')
                # Contact tips
                lines.append(f'<line x1="{ex-6}" y1="{ey-10}" x2="{ex+6}" y2="{ey-10}" class="contact-no"/>')
                lines.append(f'<line x1="{ex-6}" y1="{ey+10}" x2="{ex+6}" y2="{ey+10}" class="contact-no"/>')
                lines.append(f'<text x="{ex}" y="{ey+32}" class="io-label">{elem["label"]}</text>')

            elif elem['type'] == 'NC':
                lines.append(f'<line x1="{ex-6}" y1="{ey-10}" x2="{ex+6}" y2="{ey-10}" class="contact-no"/>')
                lines.append(f'<line x1="{ex-6}" y1="{ey+10}" x2="{ex+6}" y2="{ey+10}" class="contact-no"/>')
                lines.append(f'<line x1="{ex+6}" y1="{ey-10}" x2="{ex-6}" y2="{ey+10}" class="contact-no"/>')
                lines.append(f'<line x1="{ex}" y1="{ey-18}" x2="{ex}" y2="{ey-10}" class="contact-no"/>')
                lines.append(f'<line x1="{ex}" y1="{ey+10}" x2="{ex}" y2="{ey+18}" class="contact-no"/>')
                lines.append(f'<text x="{ex}" y="{ey+32}" class="io-label">{elem["label"]}</text>')

            elif elem['type'] == 'COIL':
                cx = ex
                lines.append(f'<ellipse cx="{cx}" cy="{ey}" rx="14" ry="11" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
                # parentheses effect
                lines.append(f'<path d="M{cx-8},{ey-6} Q{cx-10},{ey} {cx-8},{ey+6}" fill="none" stroke="#1a1a1a" stroke-width="1"/>')
                lines.append(f'<path d="M{cx+8},{ey-6} Q{cx+10},{ey} {cx+8},{ey+6}" fill="none" stroke="#1a1a1a" stroke-width="1"/>')
                lines.append(f'<text x="{cx}" y="{ey+32}" class="io-label">{elem["label"]}</text>')
                # Wire to right rail
                lines.append(f'<line x1="{cx+14}" y1="{ey}" x2="{right_rail}" y2="{ey}" class="wire"/>')

            elif elem['type'] == 'FUNC':
                fx = ex
                fw = 50
                fh = 30
                lines.append(f'<rect x="{fx - fw/2}" y="{ey - fh/2}" width="{fw}" height="{fh}" rx="3" class="func-box"/>')
                text_lines = elem['label'].split('\n')
                for li, line in enumerate(text_lines):
                    ly = ey - (len(text_lines)-1)*7 + li*14
                    lines.append(f'<text x="{fx}" y="{ly+4}" text-anchor="middle" font-size="10" fill="#1a1a1a">{line}</text>')

        # Special: Self-holding branch for Rung 0
        if i == 0:
            branch_x = 220
            branch_y_bottom = ey + 55
            # Drop from main bus
            lines.append(f'<line x1="{branch_x}" y1="{ey}" x2="{branch_x}" y2="{branch_y_bottom}" class="wire"/>')
            # Left to M0 contact
            m0_x = 130
            lines.append(f'<line x1="{left_rail + 8}" y1="{branch_y_bottom}" x2="{m0_x}" y2="{branch_y_bottom}" class="wire"/>')
            # M0 NO contact vertical
            for dy in [-14, -6, 6, 14]:
                lines.append(f'<line x1="{m0_x}" y1="{branch_y_bottom+dy-1}" x2="{m0_x}" y2="{branch_y_bottom+dy+1}" class="contact-no" stroke-width="2"/>')
            lines.append(f'<line x1="{m0_x-6}" y1="{branch_y_bottom-6}" x2="{m0_x+6}" y2="{branch_y_bottom-6}" class="contact-no"/>')
            lines.append(f'<line x1="{m0_x-6}" y1="{branch_y_bottom+6}" x2="{m0_x+6}" y2="{branch_y_bottom+6}" class="contact-no"/>')
            lines.append(f'<text x="{m0_x}" y="{branch_y_bottom+32}" class="io-label">M0 自锁</text>')
            # Right side back to branch
            lines.append(f'<line x1="{m0_x+12}" y1="{branch_y_bottom}" x2="{branch_x}" y2="{branch_y_bottom}" class="wire"/>')

    # ---- I/O Table ----
    table_y = rung_start_y + len(rungs) * rung_h + 15
    lines.append(f'<text x="30" y="{table_y}" font-size="13" font-weight="bold" fill="#1A56DB">I/O地址分配表 (三菱FX3U系列)</text>')

    t_start_y = table_y + 15
    col_w = [70, 100, 70, 100, 150]
    col_x = [30]
    for i in range(1, len(col_w)):
        col_x.append(col_x[-1] + col_w[i-1])

    io_rows = [
        ['X000', '启动按钮 SB1', 'Y000', '电机正转 KM1', 'NO触点, 绿色'],
        ['X001', '停止按钮 SB2', 'Y001', '电机反转 KM2', 'NC触点, 红色'],
        ['X002', '确认按钮 SB3', 'Y002', '运行指示灯 HL1', '红色, 1s周期闪烁'],
        ['X003', '方向切换 SB4', 'Y003', '正转指示灯 HL2', '绿色'],
        ['X004', '急停按钮 SB5', 'Y004', '反转指示灯 HL3', '黄色'],
        ['X005', '加速按钮 SB6', 'Y010', '低速 VFD-S1', '变频器多段速1'],
        ['X006', '减速按钮 SB7', 'Y011', '中速 VFD-S2', '变频器多段速2'],
        ['M0',   '运行使能(内部)', 'Y012', '高速 VFD-S3', '变频器多段速3'],
        ['M1',   '方向记忆(内部)', 'T0/T1', '闪烁定时器', 'K5 = 0.5s, 1s周期'],
        ['M10',  '方向脉冲(内部)', 'D0',   '速度等级 0-3', 'INCP/DECP调节'],
    ]

    hdr_h, row_h_val = 22, 18
    headers = ['输入端', '说明', '输出端', '说明', '备注']

    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        lines.append(f'<rect x="{cx}" y="{t_start_y}" width="{col_w[j]}" height="{hdr_h}" fill="#1A56DB" stroke="#1A56DB" stroke-width="1"/>')
        lines.append(f'<text x="{cx + col_w[j]/2}" y="{t_start_y + 15}" text-anchor="middle" font-size="10" font-weight="bold" fill="white">{hdr}</text>')

    for ri, row in enumerate(io_rows):
        ry = t_start_y + hdr_h + ri * row_h_val
        fc = '#f8f9fa' if ri % 2 == 0 else '#fff'
        for j, (val, cx) in enumerate(zip(row, col_x)):
            lines.append(f'<rect x="{cx}" y="{ry}" width="{col_w[j]}" height="{row_h_val}" fill="{fc}" stroke="#ddd" stroke-width="0.5"/>')
            lines.append(f'<text x="{cx + col_w[j]/2}" y="{ry + 13}" text-anchor="middle" font-size="9" fill="#333">{val}</text>')

    lines.append('</svg>')
    return '\n'.join(lines)


if __name__ == '__main__':
    import os
    svg = make_svg()
    out_path = r'D:\Desktop\每日财经\tools\ladder_diagram.svg'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'SVG saved to: {out_path}')
    print(f'Size: {len(svg)} bytes')
