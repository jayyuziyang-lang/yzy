#!/usr/bin/env python3
"""塔吊旋转控制系统 - 西门子S7-200 SMART 梯形图+流程图 -> PNG"""
import subprocess, os, sys, xml.etree.ElementTree as ET

OUT = r'D:\Desktop\CAD1'
os.makedirs(OUT, exist_ok=True)
NAME = '塔吊旋转控制系统'
PREFIX = '塔吊旋转控制系统'

IO_TABLE = [
    ['I0.0', '启动按钮 SB1',   'Q0.0', '电机左转(CCW) KM1', '逆时针旋转'],
    ['I0.1', '停止按钮 SB2',   'Q0.1', '电机右转(CW) KM2',  '顺时针旋转'],
    ['I0.2', '急停按钮 SB3',   'Q0.2', '蜂鸣器 HA',         '预警3秒'],
    ['I0.3', '左转按钮 SB4',   'Q0.3', '运行指示灯 HL1',    '绿色'],
    ['I0.4', '右转按钮 SB5',   'Q0.4', '左转指示灯 HL2',    '黄色'],
    ['I0.5', '加速按钮 SB6',   'Q0.5', '右转指示灯 HL3',    '蓝色'],
    ['I0.6', '减速按钮 SB7',   'Q0.6', '低速 VFD-S1',       '变频器多段速1'],
    ['M0.0', '系统运行使能',    'Q0.7', '中速 VFD-S2',       '变频器多段速2'],
    ['M0.1', '左转请求',       'Q1.0', '高速 VFD-S3',       '变频器多段速3'],
    ['M0.2', '右转请求',       'T37',  '左转预警定时器',     'TON 100ms×30=3s'],
    ['MW0',  '速度等级 1-3',   'T38',  '右转预警定时器',     'TON 100ms×30=3s'],
    ['SM0.0','常ON触点',       '',     '',                  ''],
]

LADDER_RUNGS = [
    {
        'label': 'Network 1: 系统运行使能(自锁)',
        'elements': [
            ('NO', 100, 'I0.0\n启动'),
            ('NC', 210, 'I0.1\n停止'),
            ('NC', 300, 'I0.2\n急停'),
            ('COIL', 500, 'M0.0\n运行'),
        ],
        'self_hold': True, 'self_x': 155, 'branch_from': 250, 'hold_lbl': 'M0.0'
    },
    {
        'label': 'Network 2: 左转请求(运行中+左转键+无右转→置位M0.1)',
        'elements': [
            ('NO', 100, 'M0.0\n运行'),
            ('NO', 210, 'I0.3\n左转键'),
            ('NC', 320, 'M0.2\n右转中'),
            ('COIL_SET', 500, 'M0.1\n左转请求'),
        ]
    },
    {
        'label': 'Network 3: 右转请求(运行中+右转键+无左转→置位M0.2)',
        'elements': [
            ('NO', 100, 'M0.0\n运行'),
            ('NO', 210, 'I0.4\n右转键'),
            ('NC', 320, 'M0.1\n左转中'),
            ('COIL_SET', 500, 'M0.2\n右转请求'),
        ]
    },
    {
        'label': 'Network 4: 左转蜂鸣3秒预警 T37(100ms×30=3s)',
        'elements': [
            ('NO', 100, 'M0.1\n左转请求'),
            ('TIMER', 250, 'T37\nTON\nPT=30'),
        ]
    },
    {
        'label': 'Network 5: 右转蜂鸣3秒预警 T38(100ms×30=3s)',
        'elements': [
            ('NO', 100, 'M0.2\n右转请求'),
            ('TIMER', 250, 'T38\nTON\nPT=30'),
        ]
    },
    {
        'label': 'Network 6: 左转输出(T37到后启动, 含右转互锁)',
        'elements': [
            ('NO', 100, 'M0.1\n左转请求'),
            ('NO', 210, 'T37\n3s到'),
            ('NC', 320, 'Q0.1\n右转互锁'),
            ('COIL', 500, 'Q0.0\n左转CCW'),
        ]
    },
    {
        'label': 'Network 7: 右转输出(T38到后启动, 含左转互锁)',
        'elements': [
            ('NO', 100, 'M0.2\n右转请求'),
            ('NO', 210, 'T38\n3s到'),
            ('NC', 320, 'Q0.0\n左转互锁'),
            ('COIL', 500, 'Q0.1\n右转CW'),
        ]
    },
    {
        'label': 'Network 8: 蜂鸣器输出(预警期间鸣响)',
        'elements': [
            ('NO', 100, 'M0.1\n左转请求'),
            ('NC', 210, 'T37\n左3s到'),
            ('COIL', 350, 'Q0.2\n蜂鸣器'),
            ('NO', 450, 'M0.2\n右转请求'),
            ('NC', 560, 'T38\n右3s到'),
        ]
    },
    {
        'label': 'Network 9: 状态指示灯',
        'elements': [
            ('NO', 100, 'M0.0\n运行'),
            ('COIL', 220, 'Q0.3\n运行灯'),
            ('NO', 330, 'Q0.0\n左转'),
            ('COIL', 450, 'Q0.4\n左转灯'),
            ('NO', 560, 'Q0.1\n右转'),
            ('COIL', 680, 'Q0.5\n右转灯'),
        ]
    },
    {
        'label': 'Network 10: 速度调节(MW0范围1-3)',
        'elements': [
            ('NO', 100, 'I0.5\n加速'),
            ('FUNC', 210, 'INC_W\nMW0'),
            ('NO', 330, 'I0.6\n减速'),
            ('FUNC', 440, 'DEC_W\nMW0'),
            ('FUNC', 560, 'LIMIT\nMW0\n1-3'),
        ]
    },
    {
        'label': 'Network 11: 速度输出至变频器',
        'elements': [
            ('FUNC', 100, '==I\nMW0\n1'),
            ('COIL', 220, 'Q0.6\n低速'),
            ('FUNC', 330, '==I\nMW0\n2'),
            ('COIL', 450, 'Q0.7\n中速'),
            ('FUNC', 560, '==I\nMW0\n3'),
            ('COIL', 680, 'Q1.0\n高速'),
        ]
    },
    {
        'label': 'Network 12: 停止/急停→复位所有(最高优先级)',
        'elements': [
            ('NC', 100, 'I0.1\n停止'),
            ('COIL_RESET', 250, 'M0.0\n(5点)'),
            ('NC', 400, 'I0.2\n急停'),
            ('COIL_RESET', 550, 'Q0.0\n(6点)'),
        ]
    },
]

FLOW_NODES = [
    ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
    ('init', '初始化\nMW0=1(低速)', 325, 95, 120, 45, 'box', '#E8F0FE'),
    ('chk_estop', '急停释放?', 325, 170, 100, 45, 'diamond', '#FFF3CD'),
    ('wait_start', '等待启动键', 200, 250, 110, 40, 'box', '#E8F0FE'),
    ('chk_start', '启动按下?', 200, 320, 95, 45, 'diamond', '#FFF3CD'),
    ('sys_run', 'M0.0=1 系统运行\n运行灯Q0.3亮\n进入待命', 200, 400, 145, 50, 'box', '#D4EDDA'),
    ('chk_left', '左转键\n按下?', 100, 490, 90, 45, 'diamond', '#FFF3CD'),
    ('chk_right', '右转键\n按下?', 430, 490, 90, 45, 'diamond', '#FFF3CD'),
    ('buzzer_left', '蜂鸣器Q0.2响\nT37计时3s', 100, 570, 130, 45, 'box', '#FFF3CD'),
    ('buzzer_right', '蜂鸣器Q0.2响\nT38计时3s', 430, 570, 130, 45, 'box', '#FFF3CD'),
    ('left_run', 'T37到!\nQ0.0左转CCW\nQ0.4左转灯亮', 100, 650, 140, 50, 'box', '#D4EDDA'),
    ('right_run', 'T38到!\nQ0.1右转CW\nQ0.5右转灯亮', 430, 650, 140, 50, 'box', '#D4EDDA'),
    ('chk_stop', '停止/急停?', 325, 570, 100, 45, 'diamond', '#F8D7DA'),
    ('chk_speed', '加速/减速?', 325, 740, 100, 45, 'diamond', '#FFF3CD'),
    ('adj_speed', 'INC_W/DEC_W\nLIMIT MW0 1-3', 325, 820, 140, 45, 'box', '#FCE4D6'),
    ('stop_act', '急停/停止:\nRST M0.0~M0.2\nRST Q0.0~Q0.5', 325, 900, 160, 55, 'box', '#F8D7DA'),
    ('end', '结束', 325, 980, 90, 35, 'startend', '#6C757D'),
]

FLOW_CONNECTIONS = [
    ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
    ('chk_estop', 'wait_start', 'right', '是'), ('chk_estop', 'stop_act', 'left_estop', '急停'),
    ('wait_start', 'chk_start', 'down', ''), ('chk_start', 'sys_run', 'down', '是'),
    ('chk_start', 'wait_start', 'left_loop', '否'),
    ('sys_run', 'chk_left', 'left', ''), ('sys_run', 'chk_right', 'right', ''),
    ('chk_left', 'buzzer_left', 'down', '是'), ('chk_left', 'sys_run', 'left_loop', '否'),
    ('chk_right', 'buzzer_right', 'down', '是'), ('chk_right', 'sys_run', 'right_loop', '否'),
    ('buzzer_left', 'left_run', 'down', '3s到'),
    ('buzzer_right', 'right_run', 'down', '3s到'),
    ('left_run', 'chk_stop', 'right', ''), ('left_run', 'chk_speed', 'down', ''),
    ('right_run', 'chk_stop', 'left', ''), ('right_run', 'chk_speed', 'down', ''),
    ('chk_stop', 'stop_act', 'down', '是'), ('chk_stop', 'chk_speed', 'right', '否'),
    ('chk_speed', 'adj_speed', 'down', '是'), ('chk_speed', 'left_run', 'right_loop', '否(继续)'),
    ('adj_speed', 'left_run', 'up_loop', ''), ('stop_act', 'end', 'down', ''),
]


def make_ladder_svg(name, rungs, io_table):
    W = 850; rung_h = 78; left_r, right_r = 45, 745; rung_start_y, ey0 = 55, 35
    total_h = len(rungs) * rung_h + 60 + 320
    lines = [f'<?xml version="1.0" encoding="UTF-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total_h}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">',
             '<style>text{font-size:10px;fill:#1a1a1a}.io-label{font-size:8px;fill:#333;text-anchor:middle}.nw-label{font-size:9px;fill:#666;text-anchor:middle}.contact-no{fill:none;stroke:#1a1a1a;stroke-width:1.5}.func-box{fill:#f0f4ff;stroke:#1a1a1a;stroke-width:1.5}.wire{stroke:#1a1a1a;stroke-width:1.5;fill:none}.rail{fill:#1A56DB}</style>',
             f'<rect width="{W}" height="{total_h}" fill="#FAFBFC"/>',
             f'<text x="{W/2}" y="24" text-anchor="middle" font-size="15" font-weight="bold" fill="#1A56DB">{name} — PLC梯形图 (西门子S7-200 SMART)</text>',
             f'<text x="{W/2}" y="42" text-anchor="middle" font-size="10" fill="#666">PLC: 西门子S7-200 SMART | 变频器: 台达VFD-M | 蜂鸣器预警3s | 左右转互锁 | 急停最高优先级</text>']

    for i, rung in enumerate(rungs):
        y = rung_start_y + i * rung_h; ey = y + ey0
        lines.append(f'<rect x="0" y="{y-3}" width="{W}" height="{rung_h-4}" fill="none" stroke="#e8e8e8" stroke-width="0.5"/>')
        # Siemens blue power rails
        lines.append(f'<rect x="{left_r}" y="{y}" width="3" height="{rung_h-12}" class="rail"/>')
        lines.append(f'<rect x="{right_r}" y="{y}" width="3" height="{rung_h-12}" class="rail"/>')
        lines.append(f'<line x1="{left_r+3}" y1="{ey}" x2="{right_r}" y2="{ey}" class="wire"/>')
        lines.append(f'<text x="{W/2}" y="{y+rung_h-6}" text-anchor="middle" class="nw-label">{rung["label"]}</text>')

        for elem in rung['elements']:
            typ, ex, lbl = elem
            if typ == 'NO':
                lines += [f'<line x1="{ex}" y1="{ey-10}" x2="{ex}" y2="{ey-16}" class="contact-no"/>',
                          f'<line x1="{ex}" y1="{ey+10}" x2="{ex}" y2="{ey+16}" class="contact-no"/>',
                          f'<line x1="{ex-5}" y1="{ey-10}" x2="{ex+5}" y2="{ey-10}" class="contact-no"/>',
                          f'<line x1="{ex-5}" y1="{ey+10}" x2="{ex+5}" y2="{ey+10}" class="contact-no"/>',
                          f'<text x="{ex}" y="{ey+28}" class="io-label">{lbl}</text>']
            elif typ == 'NC':
                lines += [f'<line x1="{ex-5}" y1="{ey-10}" x2="{ex+5}" y2="{ey-10}" class="contact-no"/>',
                          f'<line x1="{ex-5}" y1="{ey+10}" x2="{ex+5}" y2="{ey+10}" class="contact-no"/>',
                          f'<line x1="{ex+5}" y1="{ey-10}" x2="{ex-5}" y2="{ey+10}" class="contact-no"/>',
                          f'<line x1="{ex}" y1="{ey-16}" x2="{ex}" y2="{ey-10}" class="contact-no"/>',
                          f'<line x1="{ex}" y1="{ey+10}" x2="{ex}" y2="{ey+16}" class="contact-no"/>',
                          f'<text x="{ex}" y="{ey+28}" class="io-label">{lbl}</text>']
            elif typ == 'COIL':
                cx = ex
                lines += [f'<ellipse cx="{cx}" cy="{ey}" rx="13" ry="10" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>',
                          f'<path d="M{cx-7},{ey-5} Q{cx-9},{ey} {cx-7},{ey+5}" fill="none" stroke="#1a1a1a" stroke-width="1"/>',
                          f'<path d="M{cx+7},{ey-5} Q{cx+9},{ey} {cx+7},{ey+5}" fill="none" stroke="#1a1a1a" stroke-width="1"/>',
                          f'<text x="{cx}" y="{ey+28}" class="io-label">{lbl}</text>',
                          f'<line x1="{cx+13}" y1="{ey}" x2="{right_r}" y2="{ey}" class="wire"/>']
            elif typ == 'COIL_SET':
                cx = ex
                lines += [f'<rect x="{cx-14}" y="{ey-12}" width="28" height="24" rx="3" fill="#E8F0FE" stroke="#1A56DB" stroke-width="1.5"/>',
                          f'<text x="{cx}" y="{ey+4}" text-anchor="middle" font-size="9" fill="#1A56DB" font-weight="bold">(S)</text>',
                          f'<text x="{cx}" y="{ey+28}" class="io-label">{lbl}</text>',
                          f'<line x1="{cx+14}" y1="{ey}" x2="{right_r}" y2="{ey}" class="wire"/>']
            elif typ == 'COIL_RESET':
                cx = ex
                lines += [f'<rect x="{cx-14}" y="{ey-12}" width="28" height="24" rx="3" fill="#FCE4EC" stroke="#DC2626" stroke-width="1.5"/>',
                          f'<text x="{cx}" y="{ey+4}" text-anchor="middle" font-size="9" fill="#DC2626" font-weight="bold">(R)</text>',
                          f'<text x="{cx}" y="{ey+28}" class="io-label">{lbl}</text>',
                          f'<line x1="{cx+14}" y1="{ey}" x2="{right_r}" y2="{ey}" class="wire"/>']
            elif typ == 'TIMER':
                tx = ex; tw, th = 70, 42
                lines += [f'<rect x="{tx-tw//2}" y="{ey-th//2}" width="{tw}" height="{th}" rx="4" fill="#f0f4ff" stroke="#1A56DB" stroke-width="2"/>',
                          f'<text x="{tx}" y="{ey-10}" text-anchor="middle" font-size="10" font-weight="bold" fill="#1A56DB">{lbl.split(chr(10))[0]}</text>',
                          f'<text x="{tx}" y="{ey+6}" text-anchor="middle" font-size="9" fill="#333">{lbl.split(chr(10))[1] if len(lbl.split(chr(10)))>1 else ""}</text>']
                lines.append(f'<line x1="{tx+tw//2}" y1="{ey}" x2="{right_r}" y2="{ey}" class="wire"/>')
            elif typ == 'FUNC':
                fw, fh = 52, 28
                lines += [f'<rect x="{ex-fw/2}" y="{ey-fh/2}" width="{fw}" height="{fh}" rx="3" class="func-box"/>',
                          f'<text x="{ex}" y="{ey+4}" text-anchor="middle" font-size="9">{lbl}</text>']

        if rung.get('self_hold'):
            bx = rung['branch_from']; sx = rung['self_x']
            by2 = ey + 48
            lines += [f'<line x1="{bx}" y1="{ey}" x2="{bx}" y2="{by2}" class="wire"/>',
                      f'<line x1="{left_r+6}" y1="{by2}" x2="{sx}" y2="{by2}" class="wire"/>',
                      f'<line x1="{sx}" y1="{by2-12}" x2="{sx}" y2="{by2-4}" class="contact-no"/>',
                      f'<line x1="{sx}" y1="{by2+4}" x2="{sx}" y2="{by2+12}" class="contact-no"/>',
                      f'<line x1="{sx-5}" y1="{by2-4}" x2="{sx+5}" y2="{by2-4}" class="contact-no"/>',
                      f'<line x1="{sx-5}" y1="{by2+4}" x2="{sx+5}" y2="{by2+4}" class="contact-no"/>',
                      f'<text x="{sx}" y="{by2+26}" class="io-label">{rung.get("hold_lbl", "自锁")}</text>',
                      f'<line x1="{sx+10}" y1="{by2}" x2="{bx}" y2="{by2}" class="wire"/>']

    # I/O Table
    ty = rung_start_y + len(rungs) * rung_h + 12
    cw = [68, 100, 68, 100, 148]; cx_pos = [25]
    for i in range(1, len(cw)): cx_pos.append(cx_pos[-1] + cw[i-1])
    lines.append(f'<text x="25" y="{ty}" font-size="13" font-weight="bold" fill="#1A56DB">I/O地址分配表 (西门子S7-200 SMART)</text>')
    tsy = ty + 12
    for j, (hdr, cx) in enumerate(zip(['输入端', '说明', '输出端', '说明', '备注'], cx_pos)):
        lines.append(f'<rect x="{cx}" y="{tsy}" width="{cw[j]}" height="20" fill="#1A56DB"/>')
        lines.append(f'<text x="{cx+cw[j]/2}" y="{tsy+14}" text-anchor="middle" font-size="9" font-weight="bold" fill="white">{hdr}</text>')
    for ri, row in enumerate(io_table):
        ry = tsy + 20 + ri * 17; fc = '#f8f9fa' if ri % 2 == 0 else '#fff'
        for j, (val, cx) in enumerate(zip(row, cx_pos)):
            lines.append(f'<rect x="{cx}" y="{ry}" width="{cw[j]}" height="17" fill="{fc}" stroke="#ddd" stroke-width="0.5"/>')
            lines.append(f'<text x="{cx+cw[j]/2}" y="{ry+12}" text-anchor="middle" font-size="8" fill="#333">{val}</text>')
    lines.append('</svg>')
    return '\n'.join(lines)


def make_flow_svg(name, nodes, connections):
    W, H = 650, 1060
    lines = [f'<?xml version="1.0" encoding="UTF-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">',
             '<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#333"/></marker></defs>',
             f'<rect width="{W}" height="{H}" fill="#FAFBFC"/>',
             f'<text x="{W/2}" y="24" text-anchor="middle" font-size="14" font-weight="bold" fill="#1A56DB">{name} — 软件流程图 (西门子S7-200 SMART)</text>',
             f'<text x="{W/2}" y="40" text-anchor="middle" font-size="10" fill="#666">启动→待命→左/右转→蜂鸣器3s预警→电机旋转 | 急停最高优先级</text>']

    nc = {}
    for n in nodes:
        nid, txt, cx, cy, w, h, shape, color = n
        nc[nid] = (cx, cy, w, h, shape)
        x, y = cx - w//2, cy - h//2
        if shape == 'startend':
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" ry="18" fill="{color}"/>')
            for li, ln in enumerate(txt.split('\n')):
                lines.append(f'<text x="{cx}" y="{cy-(len(txt.split(chr(10)))-1)*6+li*12+3}" text-anchor="middle" font-size="9" fill="white" font-weight="bold">{ln}</text>')
        elif shape == 'diamond':
            lines.append(f'<polygon points="{cx},{y} {x+w},{cy} {cx},{y+h} {x},{cy}" fill="{color}" stroke="#856404" stroke-width="1.5"/>')
            for li, ln in enumerate(txt.split('\n')):
                lines.append(f'<text x="{cx}" y="{cy-(len(txt.split(chr(10)))-1)*6+li*12+3}" text-anchor="middle" font-size="9" fill="#856404">{ln}</text>')
        elif shape == 'box':
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{color}" stroke="#1A56DB" stroke-width="1.2"/>')
            for li, ln in enumerate(txt.split('\n')):
                lines.append(f'<text x="{cx}" y="{cy-(len(txt.split(chr(10)))-1)*6+li*12+3}" text-anchor="middle" font-size="9" fill="#1a1a1a">{ln}</text>')

    for conn in connections:
        fid, tid, direction, label = conn
        fx, fy, fw, fh, _ = nc[fid]; tx, ty, tw, th, _ = nc[tid]
        if direction == 'down':
            lines.append(f'<line x1="{fx}" y1="{fy+fh//2}" x2="{tx}" y2="{ty-th//2}" stroke="#333" stroke-width="1.5" marker-end="url(#ah)"/>')
            if label: lines.append(f'<text x="{fx+14}" y="{(fy+fh//2+ty-th//2)/2+4}" font-size="9" fill="#856404">{label}</text>')
        elif direction in ('right','left'):
            x1 = fx + fw//2 if direction == 'right' else fx - fw//2
            x2 = tx - tw//2 if direction == 'right' else tx + tw//2
            lines.append(f'<line x1="{x1}" y1="{fy}" x2="{x2}" y2="{ty}" stroke="#333" stroke-width="1.5" marker-end="url(#ah)"/>')
            if label: lines.append(f'<text x="{(x1+x2)/2}" y="{fy-6}" text-anchor="middle" font-size="9" fill="#856404">{label}</text>')
        elif direction == 'left_loop':
            xs = fx - fw//2
            lines.append(f'<polyline points="{xs},{fy} {xs-22},{fy} {xs-22},{ty} {tx+tw//2},{ty}" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#ah)"/>')
            if label: lines.append(f'<text x="{xs-24}" y="{fy-6}" font-size="9" fill="#DC2626">{label}</text>')
        elif direction == 'right_loop':
            xs = fx + fw//2
            lines.append(f'<polyline points="{xs},{fy} {xs+25},{fy} {xs+25},{ty} {tx-tw//2},{ty}" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#ah)"/>')
            if label: lines.append(f'<text x="{xs+27}" y="{ty-8}" font-size="9" fill="#856404">{label}</text>')
        elif direction == 'up_loop':
            xs = fx - fw//2
            lines.append(f'<polyline points="{xs},{fy} {xs-40},{fy} {xs-40},{ty} {tx},{ty+th//2}" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#ah)"/>')
        elif direction == 'left_estop':
            lines.append(f'<line x1="{fx-fw//2}" y1="{fy}" x2="{tx+tw//2}" y2="{ty}" stroke="#DC2626" stroke-width="2" marker-end="url(#ah)"/>')
            if label: lines.append(f'<text x="{(fx-fw//2+tx+tw//2)/2}" y="{fy-8}" text-anchor="middle" font-size="10" fill="#DC2626" font-weight="bold">{label}</text>')
    lines.append('</svg>')
    return '\n'.join(lines)


def svg2png_edge(svg_paths, folder):
    """Convert SVGs to PNGs using Edge headless"""
    edge = None
    for p in [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Microsoft\Edge\Application\msedge.exe']:
        if os.path.exists(p): edge = p; break
    if not edge:
        print('[WARN] Edge not found, PNG not generated')
        return

    for svg_path in svg_paths:
        png_path = svg_path.replace('.svg', '.png')
        html_path = svg_path.replace('.svg', '_tmp.html')
        fname = os.path.basename(svg_path)
        html = f'<html><head><meta charset="utf-8"></head><body style="margin:0;padding:0;background:white"><object data="{fname}" type="image/svg+xml" style="width:100%"></object></body></html>'
        with open(html_path, 'w', encoding='utf-8') as f: f.write(html)
        size = '1700,2500' if '梯形图' in fname else '1400,2200'
        cmd = [edge, '--headless=new', '--disable-gpu', '--no-sandbox',
               f'--window-size={size}', '--hide-scrollbars', '--force-device-scale-factor=2',
               f'--screenshot={os.path.abspath(png_path)}', html_path]
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=folder)
        if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
            print(f'[OK] PNG: {os.path.basename(png_path)} ({os.path.getsize(png_path)//1024}KB)')
        else:
            print(f'[FAIL] {os.path.basename(png_path)}')
        os.remove(html_path)


if __name__ == '__main__':
    print(f'=== {NAME} | 西门子S7-200 SMART ===')

    # Generate SVGs
    lad_svg = make_ladder_svg(NAME, LADDER_RUNGS, IO_TABLE)
    lad_path = os.path.join(OUT, f'{PREFIX}梯形图.svg')
    with open(lad_path, 'w', encoding='utf-8') as f: f.write(lad_svg)
    print(f'[OK] 梯形图SVG: {len(lad_svg)} bytes')

    flo_svg = make_flow_svg(NAME, FLOW_NODES, FLOW_CONNECTIONS)
    flo_path = os.path.join(OUT, f'{PREFIX}软件流程图.svg')
    with open(flo_path, 'w', encoding='utf-8') as f: f.write(flo_svg)
    print(f'[OK] 流程图SVG: {len(flo_svg)} bytes')

    # XML validate
    for fp, fn in [(lad_path, '梯形图'), (flo_path, '流程图')]:
        try:
            ET.fromstring(open(fp, 'r', encoding='utf-8').read())
            print(f'[OK] {fn} XML通过')
        except ET.ParseError as e: print(f'[FAIL] {fn}: {e}')

    # Convert to PNG
    svg2png_edge([lad_path, flo_path], OUT)

    print(f'\nFiles in: {OUT}')
