#!/usr/bin/env python3
"""批量生成三个PLC控制系统的梯形图SVG"""

import os, sys
sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r'D:\Desktop\CAD1'
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 通用SVG绘制引擎
# ============================================================
W, left_rail, right_rail, rail_w = 820, 50, 710, 4
contact_y = 38  # offset within rung
coil_x = 600
rung_h = 92

def svg_header(title, subtitle, total_h):
    return [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total_h}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">',
        '<style>',
        '  text{font-size:11px;fill:#1a1a1a} .io-label{font-size:9px;fill:#333;text-anchor:middle}',
        '  .contact-no{fill:none;stroke:#1a1a1a;stroke-width:1.5}',
        '  .func-box{fill:#f5f5f5;stroke:#1a1a1a;stroke-width:1.5}',
        '  .wire{stroke:#1a1a1a;stroke-width:1.5;fill:none}',
        '  .rung-label{font-size:10px;fill:#666;text-anchor:middle}',
        '  .rail{fill:#333}',
        '</style>',
        f'<rect width="{W}" height="{total_h}" fill="#FAFBFC"/>',
        f'<text x="{W/2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#1A56DB">{title}</text>',
        f'<text x="{W/2}" y="48" text-anchor="middle" font-size="11" fill="#666">{subtitle}</text>',
    ]

def draw_rung(lines, y, ey, label, elements, has_self_hold=False, self_hold_data=None):
    """Draw one rung of the ladder diagram"""
    # Background
    lines.append(f'<rect x="0" y="{y-5}" width="{W}" height="{rung_h-2}" fill="none" stroke="#e8e8e8" stroke-width="0.5"/>')
    # Rails
    lines.append(f'<rect x="{left_rail}" y="{y}" width="{rail_w}" height="{rung_h-15}" class="rail"/>')
    lines.append(f'<rect x="{right_rail}" y="{y}" width="{rail_w}" height="{rung_h-15}" class="rail"/>')
    # Bus wire
    lines.append(f'<line x1="{left_rail+rail_w}" y1="{ey}" x2="{right_rail}" y2="{ey}" class="wire"/>')
    # Label
    lines.append(f'<text x="{W/2}" y="{y+rung_h-8}" text-anchor="middle" class="rung-label">{label}</text>')

    for elem in elements:
        ex = elem['x']
        if elem['type'] == 'NO':
            lines.append(f'<line x1="{ex}" y1="{ey-10}" x2="{ex}" y2="{ey-18}" class="contact-no"/>')
            lines.append(f'<line x1="{ex}" y1="{ey+10}" x2="{ex}" y2="{ey+18}" class="contact-no"/>')
            lines.append(f'<line x1="{ex-6}" y1="{ey-10}" x2="{ex+6}" y2="{ey-10}" class="contact-no"/>')
            lines.append(f'<line x1="{ex-6}" y1="{ey+10}" x2="{ex+6}" y2="{ey+10}" class="contact-no"/>')
            if 'label' in elem:
                lines.append(f'<text x="{ex}" y="{ey+32}" class="io-label">{elem["label"]}</text>')
        elif elem['type'] == 'NC':
            lines.append(f'<line x1="{ex-6}" y1="{ey-10}" x2="{ex+6}" y2="{ey-10}" class="contact-no"/>')
            lines.append(f'<line x1="{ex-6}" y1="{ey+10}" x2="{ex+6}" y2="{ey+10}" class="contact-no"/>')
            lines.append(f'<line x1="{ex+6}" y1="{ey-10}" x2="{ex-6}" y2="{ey+10}" class="contact-no"/>')
            lines.append(f'<line x1="{ex}" y1="{ey-18}" x2="{ex}" y2="{ey-10}" class="contact-no"/>')
            lines.append(f'<line x1="{ex}" y1="{ey+10}" x2="{ex}" y2="{ey+18}" class="contact-no"/>')
            if 'label' in elem:
                lines.append(f'<text x="{ex}" y="{ey+32}" class="io-label">{elem["label"]}</text>')
        elif elem['type'] == 'COIL':
            cx = ex
            lines.append(f'<ellipse cx="{cx}" cy="{ey}" rx="14" ry="11" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
            lines.append(f'<path d="M{cx-8},{ey-6} Q{cx-10},{ey} {cx-8},{ey+6}" fill="none" stroke="#1a1a1a" stroke-width="1"/>')
            lines.append(f'<path d="M{cx+8},{ey-6} Q{cx+10},{ey} {cx+8},{ey+6}" fill="none" stroke="#1a1a1a" stroke-width="1"/>')
            if 'label' in elem:
                lines.append(f'<text x="{cx}" y="{ey+32}" class="io-label">{elem["label"]}</text>')
            lines.append(f'<line x1="{cx+14}" y1="{ey}" x2="{right_rail}" y2="{ey}" class="wire"/>')
        elif elem['type'] == 'FUNC':
            fx, fw, fh = ex, 50, 30
            lines.append(f'<rect x="{fx-fw/2}" y="{ey-fh/2}" width="{fw}" height="{fh}" rx="3" class="func-box"/>')
            text_lines = elem['label'].split('\n')
            for li, line in enumerate(text_lines):
                ly = ey - (len(text_lines)-1)*7 + li*14
                lines.append(f'<text x="{fx}" y="{ly+4}" text-anchor="middle" font-size="10" fill="#1a1a1a">{line}</text>')

    # Self-holding branch
    if has_self_hold and self_hold_data:
        bx = self_hold_data['branch_x']
        bby = ey + 52
        mx = self_hold_data['m_x']
        # Drop from bus
        lines.append(f'<line x1="{bx}" y1="{ey}" x2="{bx}" y2="{bby}" class="wire"/>')
        # Left connection
        lines.append(f'<line x1="{left_rail+8}" y1="{bby}" x2="{mx}" y2="{bby}" class="wire"/>')
        # M0 NO contact
        for dy in [-14,-6,6,14]:
            lines.append(f'<line x1="{mx}" y1="{bby+dy-1}" x2="{mx}" y2="{bby+dy+1}" class="contact-no" stroke-width="2"/>')
        lines.append(f'<line x1="{mx-6}" y1="{bby-6}" x2="{mx+6}" y2="{bby-6}" class="contact-no"/>')
        lines.append(f'<line x1="{mx-6}" y1="{bby+6}" x2="{mx+6}" y2="{bby+6}" class="contact-no"/>')
        lines.append(f'<text x="{mx}" y="{bby+28}" class="io-label">{self_hold_data.get("m_label","M0\n自锁")}</text>')
        # Right side back to branch
        lines.append(f'<line x1="{mx+12}" y1="{bby}" x2="{bx}" y2="{bby}" class="wire"/>')


def draw_io_table(lines, table_y, io_rows):
    """Draw I/O address allocation table"""
    lines.append(f'<text x="30" y="{table_y}" font-size="13" font-weight="bold" fill="#1A56DB">I/O地址分配表 (三菱FX3U系列)</text>')
    t_start_y = table_y + 15
    col_w = [70, 105, 70, 105, 145]
    col_x = [30]
    for i in range(1, len(col_w)):
        col_x.append(col_x[-1] + col_w[i-1])
    headers = ['输入端', '说明', '输出端', '说明', '备注']
    hdr_h, row_h_val = 22, 18

    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        lines.append(f'<rect x="{cx}" y="{t_start_y}" width="{col_w[j]}" height="{hdr_h}" fill="#1A56DB" stroke="#1A56DB" stroke-width="1"/>')
        lines.append(f'<text x="{cx+col_w[j]/2}" y="{t_start_y+15}" text-anchor="middle" font-size="10" font-weight="bold" fill="white">{hdr}</text>')

    for ri, row in enumerate(io_rows):
        ry = t_start_y + hdr_h + ri * row_h_val
        fc = '#f8f9fa' if ri % 2 == 0 else '#fff'
        for j, (val, cx) in enumerate(zip(row, col_x)):
            lines.append(f'<rect x="{cx}" y="{ry}" width="{col_w[j]}" height="{row_h_val}" fill="{fc}" stroke="#ddd" stroke-width="0.5"/>')
            lines.append(f'<text x="{cx+col_w[j]/2}" y="{ry+13}" text-anchor="middle" font-size="9" fill="#333">{val}</text>')

    return t_start_y + hdr_h + len(io_rows) * row_h_val


# ============================================================
# 系统1: 混凝土搅拌控制系统
# ============================================================
def gen_concrete_mixer():
    rungs = []
    # Rung 1: Run enable self-holding
    rungs.append({
        'label': '梯级1: 运行使能(自锁) - 启动后M0自锁，停止或急停时断开',
        'elems': [
            {'type':'NO','label':'X000\n启动','x':80},
            {'type':'NC','label':'X001\n停止','x':170},
            {'type':'NC','label':'X002\n急停','x':260},
            {'type':'COIL','label':'M0\n运行','x':coil_x},
        ],
        'self_hold': True,
        'sh_data': {'branch_x':220,'m_x':130,'m_label':'M0\n自锁'}
    })
    # Rung 2: Forward 6s timer
    rungs.append({
        'label': '梯级2: 正转6秒定时 - M0=ON且M1=OFF(反转未激活)时T0计时6秒',
        'elems': [
            {'type':'NO','label':'M0\n运行','x':80},
            {'type':'NC','label':'M1\n反转中','x':170},
            {'type':'COIL','label':'T0\nK60','x':300},
        ],
    })
    # Rung 3: Reverse 6s timer
    rungs.append({
        'label': '梯级3: 反转6秒定时 - T0计时到→M1置位(反转),T1计时6秒后→M1复位',
        'elems': [
            {'type':'NO','label':'T0\n正转到','x':80},
            {'type':'FUNC','label':'SET\nM1','x':170},
            {'type':'NO','label':'M1\n反转中','x':300},
            {'type':'COIL','label':'T1\nK60','x':410},
            {'type':'NO','label':'T1\n反转到','x':500},
            {'type':'FUNC','label':'RST\nM1','x':590},
        ],
    })
    # Rung 4: Forward output
    rungs.append({
        'label': '梯级4: 正转输出 - M0=ON, M1=OFF, Y001互锁 → Y000正转',
        'elems': [
            {'type':'NO','label':'M0\n运行','x':80},
            {'type':'NC','label':'M1\n反转中','x':170},
            {'type':'NC','label':'Y001\n反转\n互锁','x':260},
            {'type':'COIL','label':'Y000\n正转','x':coil_x},
        ],
    })
    # Rung 5: Reverse output
    rungs.append({
        'label': '梯级5: 反转输出 - M0=ON, M1=ON, Y000互锁 → Y001反转',
        'elems': [
            {'type':'NO','label':'M0\n运行','x':80},
            {'type':'NO','label':'M1\n反转中','x':170},
            {'type':'NC','label':'Y000\n正转\n互锁','x':260},
            {'type':'COIL','label':'Y001\n反转','x':coil_x},
        ],
    })
    # Rung 6: Speed selection
    rungs.append({
        'label': '梯级6: 速度选择 - X003/X004组合选择15/20/30Hz输出至变频器',
        'elems': [
            {'type':'NC','label':'X003\n速选1','x':80},
            {'type':'NC','label':'X004\n速选2','x':160},
            {'type':'COIL','label':'Y010\n15Hz','x':260},
            {'type':'NO','label':'X003\n速选1','x':360},
            {'type':'NC','label':'X004\n速选2','x':440},
            {'type':'COIL','label':'Y011\n20Hz','x':530},
            {'type':'NO','label':'X004\n速选2','x':620},
            {'type':'COIL','label':'Y012\n30Hz','x':700},
        ],
    })
    # Rung 7: Stop delay 3s
    rungs.append({
        'label': '梯级7: 停止延时3s - 按下停止后T2延时3秒再断开M0(电机惯性运转后停止)',
        'elems': [
            {'type':'NC','label':'X001\n停止','x':80},
            {'type':'COIL','label':'T2\nK30','x':200},
            {'type':'NO','label':'T2\n延时到','x':300},
            {'type':'FUNC','label':'RST\nM0','x':390},
        ],
    })
    # Rung 8: Status lights
    rungs.append({
        'label': '梯级8: 状态指示灯',
        'elems': [
            {'type':'NO','label':'M0\n运行','x':80},
            {'type':'COIL','label':'Y002\n运行灯','x':200},
            {'type':'NO','label':'Y000\n正转','x':310},
            {'type':'COIL','label':'Y003\n正转灯','x':430},
            {'type':'NO','label':'Y001\n反转','x':540},
            {'type':'COIL','label':'Y004\n反转灯','x':660},
        ],
    })

    num_rungs = len(rungs)
    table_h = 260
    total_h = 60 + num_rungs * rung_h + 20 + table_h
    lines = svg_header('混凝土搅拌控制系统 — PLC梯形图', '三菱FX3U | 正转6s→反转6s循环 | 三级调速(15/20/30Hz) | 停止延时3s', total_h)

    rung_start_y = 65
    for i, rung in enumerate(rungs):
        y = rung_start_y + i * rung_h
        ey = y + contact_y
        draw_rung(lines, y, ey, rung['label'], rung['elems'],
                  has_self_hold=rung.get('self_hold', False),
                  self_hold_data=rung.get('sh_data'))

    # IO Table
    io_rows = [
        ['X000','启动按钮 SB1','Y000','电机正转 KM1','正转6秒'],
        ['X001','停止按钮 SB2','Y001','电机反转 KM2','反转6秒'],
        ['X002','急停按钮 SB3','Y002','运行指示灯 HL1','绿色'],
        ['X003','速度选择1 SA1','Y003','正转指示灯 HL2','绿色'],
        ['X004','速度选择2 SA2','Y004','反转指示灯 HL3','黄色'],
        ['M0','运行使能(内部)','Y010','15Hz输出 VFD-S1','低速搅拌'],
        ['M1','反转状态(内部)','Y011','20Hz输出 VFD-S2','中速搅拌'],
        ['T0','正转定时 K60','Y012','30Hz输出 VFD-S3','高速搅拌'],
        ['T1','反转定时 K60','T2','停止延时 K30','延时3s停止'],
    ]
    table_y = rung_start_y + num_rungs * rung_h + 15
    draw_io_table(lines, table_y, io_rows)
    lines.append('</svg>')

    path = os.path.join(OUT_DIR, '梯形图_混凝土搅拌控制系统.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {path} ({len("\n".join(lines))} bytes)')


# ============================================================
# 系统2: 简易轮毂打紧机控制系统
# ============================================================
def gen_hub_tightener():
    rungs = []
    # Rung 1: Forward control
    rungs.append({
        'label': '梯级1: 正转控制 - X000正转键→M1置位(正转使能), X004限位→M1复位',
        'elems': [
            {'type':'NO','label':'X000\n正转键','x':80},
            {'type':'FUNC','label':'SET\nM1','x':170},
            {'type':'NO','label':'X004\n正转限位','x':290},
            {'type':'FUNC','label':'RST\nM1','x':380},
        ],
    })
    # Rung 2: Reverse control
    rungs.append({
        'label': '梯级2: 反转控制 - X001反转键→M2置位(反转使能), X005限位→M2复位',
        'elems': [
            {'type':'NO','label':'X001\n反转键','x':80},
            {'type':'FUNC','label':'SET\nM2','x':170},
            {'type':'NO','label':'X005\n反转限位','x':290},
            {'type':'FUNC','label':'RST\nM2','x':380},
        ],
    })
    # Rung 3: Forward output
    rungs.append({
        'label': '梯级3: 正转输出 - M1=ON, 急停未按下, Y001互锁 → Y000 正转',
        'elems': [
            {'type':'NO','label':'M1\n正转使能','x':80},
            {'type':'NC','label':'X003\n急停','x':170},
            {'type':'NC','label':'Y001\n反转\n互锁','x':260},
            {'type':'COIL','label':'Y000\n正转','x':coil_x},
        ],
    })
    # Rung 4: Reverse output
    rungs.append({
        'label': '梯级4: 反转输出 - M2=ON, 急停未按下, Y000互锁 → Y001 反转',
        'elems': [
            {'type':'NO','label':'M2\n反转使能','x':80},
            {'type':'NC','label':'X003\n急停','x':170},
            {'type':'NC','label':'Y000\n正转\n互锁','x':260},
            {'type':'COIL','label':'Y001\n反转','x':coil_x},
        ],
    })
    # Rung 5: Stop button
    rungs.append({
        'label': '梯级5: 停止复位 - X002停止键→复位M1/M2, 停止所有运动',
        'elems': [
            {'type':'NO','label':'X002\n停止','x':80},
            {'type':'FUNC','label':'RST\nM1','x':170},
            {'type':'FUNC','label':'RST\nM2','x':290},
        ],
    })
    # Rung 6: Speed control
    rungs.append({
        'label': '梯级6: 速度调节 - X006加速/X007减速, D0范围0-3级',
        'elems': [
            {'type':'NO','label':'X006\n加速','x':80},
            {'type':'FUNC','label':'INCP\nD0','x':190},
            {'type':'NO','label':'X007\n减速','x':310},
            {'type':'FUNC','label':'DECP\nD0','x':420},
            {'type':'FUNC','label':'=\nD0 K1','x':530},
            {'type':'COIL','label':'Y010\n低速','x':620},
            {'type':'FUNC','label':'=\nD0 K2','x':700},
            {'type':'COIL','label':'Y011\n中速','x':760},
        ],
    })
    # Rung 7: Running water lights (4 lights, 1s period)
    rungs.append({
        'label': '梯级7: 4流水灯(1s周期) - T10/T11/T12/T13产生脉冲, 移位点亮Y005→Y006→Y007→Y010→循环',
        'elems': [
            {'type':'NO','label':'M1\n正转','x':80},
            {'type':'NC','label':'T11','x':150},
            {'type':'COIL','label':'T10\nK2.5','x':240},
            {'type':'NO','label':'T10','x':320},
            {'type':'COIL','label':'T11\nK2.5','x':400},
            {'type':'NO','label':'T10','x':480},
            {'type':'COIL','label':'Y005\n灯1','x':560},
            {'type':'NO','label':'T10','x':630},
            {'type':'COIL','label':'Y006\n灯2','x':700},
        ],
    })
    # Rung 8: Water lights continue
    rungs.append({
        'label': '梯级8: 流水灯续 - 移位脉冲触发Y007(灯3)和Y010(灯4)',
        'elems': [
            {'type':'NO','label':'T10','x':80},
            {'type':'COIL','label':'Y007\n灯3','x':200},
            {'type':'NC','label':'T10','x':310},
            {'type':'COIL','label':'Y010\n灯4','x':430},
            {'type':'NO','label':'M0','x':530},
            {'type':'COIL','label':'Y002\n运行灯','x':620},
        ],
    })
    # Rung 9: Status lights
    rungs.append({
        'label': '梯级9: 状态指示灯 - 正转绿灯, 反转黄灯, 运行红灯',
        'elems': [
            {'type':'NO','label':'Y000\n正转','x':80},
            {'type':'COIL','label':'Y003\n正转灯','x':200},
            {'type':'NO','label':'Y001\n反转','x':310},
            {'type':'COIL','label':'Y004\n反转灯','x':430},
        ],
    })

    num_rungs = len(rungs)
    table_h = 240
    total_h = 60 + num_rungs * rung_h + 20 + table_h
    lines = svg_header('简易轮毂打紧机控制系统 — PLC梯形图', '三菱FX3U | 正反转限位停止 | 4流水灯1s周期 | 三级调速', total_h)

    rung_start_y = 65
    for i, rung in enumerate(rungs):
        y = rung_start_y + i * rung_h
        ey = y + contact_y
        draw_rung(lines, y, ey, rung['label'], rung['elems'])

    io_rows = [
        ['X000','正转按钮 SB1','Y000','电机正转 KM1','到达限位停止'],
        ['X001','反转按钮 SB2','Y001','电机反转 KM2','到达限位停止'],
        ['X002','停止按钮 SB3','Y002','运行指示灯 HL1','红色'],
        ['X003','急停按钮 SB4','Y003','正转指示灯 HL2','绿色'],
        ['X004','正转限位 SQ1','Y004','反转指示灯 HL3','黄色'],
        ['X005','反转限位 SQ2','Y005','流水灯1 HL4','1s周期循环'],
        ['X006','加速按钮 SB5','Y006','流水灯2 HL5','1s周期循环'],
        ['X007','减速按钮 SB6','Y007','流水灯3 HL6','1s周期循环'],
        ['M1','正转使能(内部)','Y010','流水灯4 + 低速','灯4+速度1'],
        ['M2','反转使能(内部)','Y011','中速输出 VFD-S2','中速'],
        ['D0','速度等级(0-2)','Y012','高速输出 VFD-S3','高速'],
        ['T10/T11','流水灯定时器','-','K2.5=0.25s','4灯=1s周期'],
    ]
    table_y = rung_start_y + num_rungs * rung_h + 15
    draw_io_table(lines, table_y, io_rows)
    lines.append('</svg>')

    path = os.path.join(OUT_DIR, '梯形图_简易轮毂打紧机控制系统.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {path} ({len("\n".join(lines))} bytes)')


# ============================================================
# 系统3: 电动葫芦控制系统
# ============================================================
def gen_electric_hoist():
    rungs = []
    # Rung 1: Up control
    rungs.append({
        'label': '梯级1: 上升控制 - X000上升键→M1置位, X004上限位→M1复位',
        'elems': [
            {'type':'NO','label':'X000\n上升键','x':80},
            {'type':'FUNC','label':'SET\nM1','x':170},
            {'type':'NO','label':'X004\n上限位','x':290},
            {'type':'FUNC','label':'RST\nM1','x':380},
        ],
    })
    # Rung 2: Down control
    rungs.append({
        'label': '梯级2: 下降控制 - X001下降键→M2置位, X005下限位→M2复位',
        'elems': [
            {'type':'NO','label':'X001\n下降键','x':80},
            {'type':'FUNC','label':'SET\nM2','x':170},
            {'type':'NO','label':'X005\n下限位','x':290},
            {'type':'FUNC','label':'RST\nM2','x':380},
        ],
    })
    # Rung 3: Up output (forward)
    rungs.append({
        'label': '梯级3: 上升输出(正转) - M1=ON, 急停未按下, Y001互锁 → Y000',
        'elems': [
            {'type':'NO','label':'M1\n上升使能','x':80},
            {'type':'NC','label':'X003\n急停','x':170},
            {'type':'NC','label':'Y001\n下降\n互锁','x':260},
            {'type':'COIL','label':'Y000\n上升','x':coil_x},
        ],
    })
    # Rung 4: Down output (reverse)
    rungs.append({
        'label': '梯级4: 下降输出(反转) - M2=ON, 急停未按下, Y000互锁 → Y001',
        'elems': [
            {'type':'NO','label':'M2\n下降使能','x':80},
            {'type':'NC','label':'X003\n急停','x':170},
            {'type':'NC','label':'Y000\n上升\n互锁','x':260},
            {'type':'COIL','label':'Y001\n下降','x':coil_x},
        ],
    })
    # Rung 5: Stop
    rungs.append({
        'label': '梯级5: 停止复位 - X002停止键→复位M1/M2, 急停也复位',
        'elems': [
            {'type':'NO','label':'X002\n停止','x':80},
            {'type':'FUNC','label':'RST\nM1','x':170},
            {'type':'FUNC','label':'RST\nM2','x':270},
            {'type':'NO','label':'X003\n急停','x':380},
            {'type':'FUNC','label':'ZRST\nM1 M2','x':470},
        ],
    })
    # Rung 6: Speed control
    rungs.append({
        'label': '梯级6: 速度调节 - X006加速/X007减速, D0范围0-3级',
        'elems': [
            {'type':'NO','label':'X006\n加速','x':80},
            {'type':'FUNC','label':'INCP\nD0','x':190},
            {'type':'NO','label':'X007\n减速','x':310},
            {'type':'FUNC','label':'DECP\nD0','x':420},
            {'type':'FUNC','label':'=\nD0 K1','x':530},
            {'type':'COIL','label':'Y011\n低速','x':620},
            {'type':'FUNC','label':'=\nD0 K2','x':700},
            {'type':'COIL','label':'Y012\n中速','x':760},
        ],
    })
    # Rung 7: 6 water lights (1s period)
    rungs.append({
        'label': '梯级7: 6流水灯定时器(1s周期) - T20/T21产生0.167s脉冲',
        'elems': [
            {'type':'NO','label':'M0\n运行','x':80},
            {'type':'NC','label':'T21','x':160},
            {'type':'COIL','label':'T20\nK1.67','x':250},
            {'type':'NO','label':'T20','x':340},
            {'type':'COIL','label':'T21\nK1.67','x':420},
        ],
    })
    # Rung 8: Water lights output
    rungs.append({
        'label': '梯级8: 6流水灯输出 - Y005→Y010循环点亮, T20脉冲触发移位',
        'elems': [
            {'type':'NO','label':'T20','x':80},
            {'type':'COIL','label':'Y005\n灯1','x':170},
            {'type':'NO','label':'T20','x':250},
            {'type':'COIL','label':'Y006\n灯2','x':340},
            {'type':'NO','label':'T20','x':420},
            {'type':'COIL','label':'Y007\n灯3','x':510},
            {'type':'NO','label':'T20','x':590},
            {'type':'COIL','label':'Y010\n灯4','x':680},
        ],
    })
    # Rung 9: Water lights cont + status
    rungs.append({
        'label': '梯级9: 流水灯5/6 + 状态指示灯(上升绿灯, 下降黄灯, 运行红灯)',
        'elems': [
            {'type':'NO','label':'T20','x':80},
            {'type':'COIL','label':'Y011\n灯5','x':180},
            {'type':'NO','label':'T20','x':270},
            {'type':'COIL','label':'Y012\n灯6','x':360},
            {'type':'NO','label':'Y000\n上升','x':460},
            {'type':'COIL','label':'Y003\n上升灯','x':560},
            {'type':'NO','label':'Y001\n下降','x':660},
            {'type':'COIL','label':'Y004\n下降灯','x':740},
        ],
    })

    num_rungs = len(rungs)
    table_h = 260
    total_h = 60 + num_rungs * rung_h + 20 + table_h
    lines = svg_header('电动葫芦控制系统 — PLC梯形图', '三菱FX3U | 上升/下降限位停止 | 6流水灯1s周期 | 三级调速', total_h)

    rung_start_y = 65
    for i, rung in enumerate(rungs):
        y = rung_start_y + i * rung_h
        ey = y + contact_y
        draw_rung(lines, y, ey, rung['label'], rung['elems'])

    io_rows = [
        ['X000','上升按钮 SB1','Y000','电机正转(上升)','到达上限位停止'],
        ['X001','下降按钮 SB2','Y001','电机反转(下降)','到达下限位停止'],
        ['X002','停止按钮 SB3','Y002','运行指示灯 HL1','红色'],
        ['X003','急停按钮 SB4','Y003','上升指示灯 HL2','绿色'],
        ['X004','上限位 SQ1','Y004','下降指示灯 HL3','黄色'],
        ['X005','下限位 SQ2','Y005','流水灯1 HL4','1s周期,6灯循环'],
        ['X006','加速按钮 SB5','Y006','流水灯2 HL5','1s周期,6灯循环'],
        ['X007','减速按钮 SB6','Y007','流水灯3 HL6','1s周期,6灯循环'],
        ['M1','上升使能(内部)','Y010','流水灯4 HL7','1s周期,6灯循环'],
        ['M2','下降使能(内部)','Y011','流水灯5 HL8','1s周期,6灯循环'],
        ['D0','速度等级(0-2)','Y012','流水灯6 HL9','1s周期,6灯循环'],
        ['T20/T21','流水灯定时器','-','K1.67=0.167s','6灯=1s周期'],
    ]
    table_y = rung_start_y + num_rungs * rung_h + 15
    draw_io_table(lines, table_y, io_rows)
    lines.append('</svg>')

    path = os.path.join(OUT_DIR, '梯形图_电动葫芦控制系统.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'[OK] {path} ({len("\n".join(lines))} bytes)')


if __name__ == '__main__':
    gen_concrete_mixer()
    gen_hub_tightener()
    gen_electric_hoist()
    print('\n全部梯形图生成完成!')
