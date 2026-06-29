#!/usr/bin/env python3
"""批量生成所有PLC控制系统图片 (西门子S7-1200)"""
import subprocess, os, sys, xml.etree.ElementTree as ET

EDGE_PATHS = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
]
BASE = r'D:\Desktop\PCL汇总'

# ============================================================
# SVG生成核心函数
# ============================================================

def make_ladder_svg(name, rungs, io_table, subtitle=""):
    """生成带TIA Portal软件界面的梯形图

    左侧: 软件项目树导航面板
    右侧: 梯形图编辑区 (含各Network梯级)
    下方: I/O地址分配表
    """
    # ── 布局常量 ──
    WIN_X, WIN_Y = 14, 14          # 窗口左上角
    WIN_W = 1250                    # 窗口总宽
    TITLE_H = 28; MENU_H = 24; TOOL_H = 30; STAT_H = 20
    LEFT_W = 238                    # 左侧项目树宽度
    HEADER_H = TITLE_H + MENU_H + TOOL_H

    rung_h = 72; ey0 = 34
    rung_count = len(rungs)
    editor_h = max(rung_count * rung_h + 60, 480)
    content_h = HEADER_H + editor_h
    WIN_H = content_h + STAT_H

    SVG_W = WIN_W + 28; SVG_H = WIN_H + 28 + 320

    ml = []; A = lambda s: ml.append(s)

    # ── 样式 ──
    A('<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" font-family="Microsoft YaHei, SimHei, sans-serif">')
    A('<style>')
    A('.ct{fill:#000;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.cg{fill:#555;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.cl{fill:#888;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.cw{fill:#fff;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.cbl{fill:#1A56DB;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.w{stroke:#000;stroke-width:1.5;fill:none}')
    A('.wt{stroke:#000;stroke-width:2.5;fill:none}')
    A('.contact-no{fill:none;stroke:#000;stroke-width:1.5}')
    A('.func-box{fill:#f0f4ff;stroke:#1A56DB;stroke-width:1.3}')
    A('.rail-l{fill:#1A56DB}')
    A('.rail-r{fill:#1A56DB}')
    A('</style>')

    # ── 桌面背景 ──
    A(f'<rect width="{SVG_W}" height="{SVG_H}" fill="#2D3748"/>')

    # <defs> 必须在引用前定义
    A('<defs>')
    A('<linearGradient id="titleGrad" x1="0" y1="0" x2="0" y2="1">')
    A('<stop offset="0%" stop-color="#2563EB"/>')
    A('<stop offset="50%" stop-color="#1D4ED8"/>')
    A('<stop offset="100%" stop-color="#1E40AF"/>')
    A('</linearGradient>')
    A('<linearGradient id="toolGrad" x1="0" y1="0" x2="0" y2="1">')
    A('<stop offset="0%" stop-color="#F8F6F2"/>')
    A('<stop offset="100%" stop-color="#E5E1DA"/>')
    A('</linearGradient>')
    A('</defs>')

    # ── 窗口阴影 ──
    A(f'<rect x="{WIN_X+3}" y="{WIN_Y+3}" width="{WIN_W}" height="{WIN_H}" rx="3" fill="rgba(0,0,0,0.4)"/>')
    A(f'<rect x="{WIN_X+1}" y="{WIN_Y+1}" width="{WIN_W}" height="{WIN_H}" rx="2" fill="rgba(0,0,0,0.2)"/>')

    # ── 窗口主体 ──
    A(f'<rect x="{WIN_X}" y="{WIN_Y}" width="{WIN_W}" height="{WIN_H}" rx="2" fill="#ECE9E4"/>')

    # ═══════════════════════════════════════
    # 标题栏
    # ═══════════════════════════════════════
    A(f'<rect x="{WIN_X}" y="{WIN_Y}" width="{WIN_W}" height="{TITLE_H}" rx="2" fill="url(#titleGrad)"/>')
    A(f'<rect x="{WIN_X}" y="{WIN_Y+TITLE_H-2}" width="{WIN_W}" height="2" fill="#1A56DB"/>')

    # 软件图标 + 标题文字
    icon_x = WIN_X + 10
    A(f'<rect x="{icon_x}" y="{WIN_Y+5}" width="17" height="17" rx="2" fill="#60A5FA" stroke="#93C5FD" stroke-width="0.8"/>')
    A(f'<text x="{icon_x+8}" y="{WIN_Y+17}" text-anchor="middle" font-size="10" fill="white" font-weight="bold">S</text>')
    txt_x = icon_x + 24
    A(f'<text x="{txt_x}" y="{WIN_Y+19}" font-size="11" fill="white" font-weight="bold" class="cw">')
    A(f'  TIA Portal V16 - [{name}]</text>')

    # 窗口控制按钮 (最小化/最大化/关闭)
    btn_w, btn_h, btn_gap = 34, 18, 2
    btn_y = WIN_Y + 5
    btn_start_x = WIN_X + WIN_W - btn_w - 6
    # 最小化
    bx = btn_start_x
    A(f'<rect x="{bx}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="1" fill="#1E40AF" stroke="#60A5FA" stroke-width="0.5"/>')
    A(f'<line x1="{bx+10}" y1="{btn_y+btn_h//2}" x2="{bx+24}" y2="{btn_y+btn_h//2}" stroke="white" stroke-width="2"/>')
    # 最大化
    bx = btn_start_x - btn_w - btn_gap
    A(f'<rect x="{bx}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="1" fill="#1E40AF" stroke="#60A5FA" stroke-width="0.5"/>')
    A(f'<rect x="{bx+10}" y="{btn_y+4}" width="14" height="10" fill="none" stroke="white" stroke-width="2"/>')
    # 关闭
    bx = btn_start_x - 2*(btn_w + btn_gap)
    A(f'<rect x="{bx}" y="{btn_y}" width="{btn_w}" height="{btn_h}" rx="1" fill="#DC2626" stroke="#F87171" stroke-width="0.5"/>')
    A(f'<line x1="{bx+11}" y1="{btn_y+4}" x2="{bx+23}" y2="{btn_y+14}" stroke="white" stroke-width="2"/>')
    A(f'<line x1="{bx+23}" y1="{btn_y+4}" x2="{bx+11}" y2="{btn_y+14}" stroke="white" stroke-width="2"/>')

    # ═══════════════════════════════════════
    # 菜单栏
    # ═══════════════════════════════════════
    menu_y = WIN_Y + TITLE_H
    A(f'<rect x="{WIN_X}" y="{menu_y}" width="{WIN_W}" height="{MENU_H}" fill="#F0EDE8"/>')
    A(f'<line x1="{WIN_X}" y1="{menu_y+MENU_H}" x2="{WIN_X+WIN_W}" y2="{menu_y+MENU_H}" stroke="#C8C0B4" stroke-width="1"/>')
    menu_items = ['文件(F)', '编辑(E)', '查看(V)', 'PLC(P)', '调试(D)', '工具(T)', '窗口(W)', '帮助(H)']
    mx = WIN_X + 10
    for mi in menu_items:
        mw = len(mi) * 11
        A(f'<text x="{mx}" y="{menu_y+16}" font-size="11" fill="#333" class="ct">{mi}</text>')
        mx += mw + 6

    # ═══════════════════════════════════════
    # 工具栏
    # ═══════════════════════════════════════
    tool_y = menu_y + MENU_H
    A(f'<rect x="{WIN_X}" y="{tool_y}" width="{WIN_W}" height="{TOOL_H}" fill="url(#toolGrad)"/>')
    A(f'<line x1="{WIN_X}" y1="{tool_y+TOOL_H}" x2="{WIN_X+WIN_W}" y2="{tool_y+TOOL_H}" stroke="#C8C0B4" stroke-width="1"/>')

    # 工具按钮
    tb_icons = [
        ('新建', 'new'), ('打开', 'open'), ('保存', 'save'), ('', ''),
        ('编译', 'cmp'), ('下载', 'dwn'), ('运行', 'run'), ('停止', 'stop'),
        ('', ''), ('上载', 'up'), ('', ''), ('程序状态', 'state'),
    ]
    tx = WIN_X + 8
    for lbl, ico in tb_icons:
        if not lbl:
            tx += 6  # separator gap
            A(f'<line x1="{tx}" y1="{tool_y+6}" x2="{tx}" y2="{tool_y+TOOL_H-6}" stroke="#C8C0B4" stroke-width="1"/>')
            tx += 10
            continue
        bw = 58
        A(f'<rect x="{tx}" y="{tool_y+3}" width="{bw}" height="{TOOL_H-6}" rx="2" fill="none"/>')
        # Simple icon representations
        cx_ico = tx + bw//2
        if ico == 'new':
            A(f'<rect x="{tx+20}" y="{tool_y+8}" width="14" height="12" fill="none" stroke="#444" stroke-width="1.2"/>')
        elif ico == 'open':
            A(f'<path d="M{tx+18},{tool_y+20} L{tx+18},{tool_y+9} L{tx+26},{tool_y+9} L{tx+28},{tool_y+7} L{tx+36},{tool_y+7} L{tx+36},{tool_y+20}Z" fill="none" stroke="#C8A030" stroke-width="1.2"/>')
        elif ico == 'save':
            A(f'<rect x="{tx+22}" y="{tool_y+7}" width="12" height="14" rx="1" fill="none" stroke="#1A56DB" stroke-width="1.2"/>')
            A(f'<rect x="{tx+25}" y="{tool_y+7}" width="6" height="4" fill="#1A56DB"/>')
        elif ico == 'cmp':
            A(f'<text x="{cx_ico}" y="{tool_y+TOOL_H-10}" text-anchor="middle" font-size="12" fill="#16A34A">\u2713</text>')
        elif ico == 'run':
            A(f'<polygon points="{tx+20},{tool_y+8} {tx+34},{tool_y+TOOL_H//2} {tx+20},{tool_y+TOOL_H-8}" fill="#16A34A"/>')
        elif ico == 'stop':
            A(f'<rect x="{tx+20}" y="{tool_y+8}" width="14" height="14" fill="#DC2626"/>')
        elif ico == 'dwn':
            A(f'<polygon points="{cx_ico-6},{tool_y+8} {cx_ico+6},{tool_y+8} {cx_ico},{tool_y+TOOL_H-5}" fill="#1A56DB"/>')
        elif ico == 'up':
            A(f'<polygon points="{cx_ico-6},{tool_y+TOOL_H-8} {cx_ico+6},{tool_y+TOOL_H-8} {cx_ico},{tool_y+5}" fill="#1A56DB"/>')
        elif ico == 'state':
            A(f'<rect x="{tx+19}" y="{tool_y+7}" width="16" height="14" rx="1" fill="none" stroke="#444" stroke-width="1.2"/>')
            A(f'<line x1="{tx+22}" y1="{tool_y+11}" x2="{tx+32}" y2="{tool_y+11}" stroke="#444" stroke-width="0.8"/>')
            A(f'<line x1="{tx+22}" y1="{tool_y+14}" x2="{tx+32}" y2="{tool_y+14}" stroke="#444" stroke-width="0.8"/>')
            A(f'<line x1="{tx+22}" y1="{tool_y+17}" x2="{tx+30}" y2="{tool_y+17}" stroke="#444" stroke-width="0.8"/>')
        else:
            A(f'<text x="{cx_ico}" y="{tool_y+TOOL_H-9}" text-anchor="middle" font-size="10" fill="#555">{ico}</text>')
        A(f'<text x="{cx_ico}" y="{tool_y+TOOL_H-3}" text-anchor="middle" font-size="8" fill="#666" class="ct">{lbl}</text>')
        tx += bw + 2

    # ═══════════════════════════════════════
    # 主内容区
    # ═══════════════════════════════════════
    content_y = tool_y + TOOL_H
    # 内容区背景
    A(f'<rect x="{WIN_X}" y="{content_y}" width="{WIN_W}" height="{editor_h}" fill="#FFFFFF"/>')

    # ── 左侧: 项目树面板 ──
    panel_x = WIN_X + 4; panel_y = content_y + 4
    panel_h = editor_h - 8
    A(f'<rect x="{panel_x}" y="{panel_y}" width="{LEFT_W}" height="{panel_h}" fill="#F8F6F2" stroke="#C8C0B4" stroke-width="1.2"/>')
    # 面板标题
    A(f'<rect x="{panel_x}" y="{panel_y}" width="{LEFT_W}" height="22" fill="#D6CFC4"/>')
    A(f'<text x="{panel_x+LEFT_W//2}" y="{panel_y+15}" text-anchor="middle" font-size="10" font-weight="bold" fill="#333" class="ct">指令树 / 项目浏览器</text>')

    # 树节点
    tree_nodes = [
        (0, 'CPU 1214C (DC/DC/DC)'),
        (0, '程序块'),
        (1, 'MAIN (OB1)'),
        (1, 'SBR_0'),
        (1, 'INT_0'),
        (0, '符号表'),
        (1, 'POU 符号'),
        (1, 'I/O 符号'),
        (0, '状态表'),
        (1, 'CHT1 (图表1)'),
        (0, '数据块'),
        (1, 'DB1 (全局数据)'),
        (0, '系统块'),
        (1, 'CPU 配置'),
        (1, '数字量输入'),
        (1, '数字量输出'),
        (0, '交叉引用'),
        (0, '通信'),
        (1, '以太网端口'),
        (0, '向导'),
        (1, 'PID'),
        (1, '运动控制'),
    ]
    ty_off = panel_y + 30
    for depth, label in tree_nodes:
        indent = 10 + depth * 18
        icon = '▸' if depth == 0 else '  '
        node_fill = "#333" if depth == 0 else "#555"
        node_wt = "bold" if depth == 0 else "normal"
        tn_fs = "10" if depth == 0 else "9"
        A(f'<text x="{panel_x+indent}" y="{ty_off}" font-size="{tn_fs}" fill="{node_fill}" font-weight="{node_wt}" class="ct">{icon} {label}</text>')
        ty_off += 16

    # ── 右侧: 梯形图编辑区 ──
    editor_x = panel_x + LEFT_W + 8
    editor_w = WIN_W - LEFT_W - 18
    left_rail = editor_x + 25
    right_rail = editor_x + editor_w - 25

    # 编辑区背景网格
    A(f'<rect x="{editor_x}" y="{panel_y}" width="{editor_w}" height="{panel_h}" fill="#FFFFFF" stroke="#D0CCC8" stroke-width="0.8"/>')

    # 顶部标签
    A(f'<rect x="{editor_x}" y="{panel_y}" width="120" height="18" fill="#E8E4DF" stroke="#B0ACA8" stroke-width="1"/>')
    A(f'<text x="{editor_x+60}" y="{panel_y+13}" text-anchor="middle" font-size="9" fill="#333" class="ct">梯形图编辑器</text>')

    rung_start_y = panel_y + 28
    editor_top = rung_start_y

    for i, rung in enumerate(rungs):
        y = rung_start_y + i * rung_h
        ey = y + ey0

        # 行背景交替
        bg = '#FAFAFA' if i % 2 == 0 else '#FFFFFF'
        A(f'<rect x="{editor_x+1}" y="{y-2}" width="{editor_w-2}" height="{rung_h-3}" fill="{bg}"/>')

        # 左右母线
        A(f'<rect x="{left_rail-2}" y="{y-2}" width="4" height="{rung_h}" class="rail-l"/>')
        A(f'<rect x="{right_rail-2}" y="{y-2}" width="4" height="{rung_h}" class="rail-r"/>')

        # 主逻辑线
        A(f'<line x1="{left_rail+4}" y1="{ey}" x2="{right_rail-2}" y2="{ey}" class="w"/>')

        # Network 标签
        lbl = rung['label']
        if ':' in lbl:
            net_part, rest = lbl.split(':', 1)
        else:
            net_part, rest = lbl, ''
        A(f'<text x="{editor_x+8}" y="{y+12}" font-size="8" font-weight="bold" fill="#1A56DB" class="ct">{net_part}</text>')

        # 梯级元素 - 需要在编辑器坐标系中偏移
        for elem in rung['elements']:
            typ, ex, lbl = elem
            # ex 原本相对于 W=850 布局，需要映射到编辑区
            # 原 left_r=45, right_r=745, 编辑区 left_rail ~ right_rail
            old_scale = (ex - 45) / 700.0  # position ratio in old layout
            lx = left_rail + old_scale * (right_rail - left_rail - 30)

            if typ == 'NO':
                ml += [
                    f'<line x1="{lx}" y1="{ey-10}" x2="{lx}" y2="{ey-16}" class="contact-no"/>',
                    f'<line x1="{lx}" y1="{ey+10}" x2="{lx}" y2="{ey+16}" class="contact-no"/>',
                    f'<line x1="{lx-5}" y1="{ey-10}" x2="{lx+5}" y2="{ey-10}" class="contact-no"/>',
                    f'<line x1="{lx-5}" y1="{ey+10}" x2="{lx+5}" y2="{ey+10}" class="contact-no"/>',
                    f'<text x="{lx}" y="{ey+26}" text-anchor="middle" font-size="8" fill="#444" class="ct">{lbl}</text>']
            elif typ == 'NC':
                ml += [
                    f'<line x1="{lx-5}" y1="{ey-10}" x2="{lx+5}" y2="{ey-10}" class="contact-no"/>',
                    f'<line x1="{lx-5}" y1="{ey+10}" x2="{lx+5}" y2="{ey+10}" class="contact-no"/>',
                    f'<line x1="{lx+5}" y1="{ey-10}" x2="{lx-5}" y2="{ey+10}" class="contact-no"/>',
                    f'<line x1="{lx}" y1="{ey-16}" x2="{lx}" y2="{ey-10}" class="contact-no"/>',
                    f'<line x1="{lx}" y1="{ey+10}" x2="{lx}" y2="{ey+16}" class="contact-no"/>',
                    f'<text x="{lx}" y="{ey+26}" text-anchor="middle" font-size="8" fill="#444" class="ct">{lbl}</text>']
            elif typ == 'COIL':
                ml += [
                    f'<ellipse cx="{lx}" cy="{ey}" rx="12" ry="9" fill="none" stroke="#000" stroke-width="1.3"/>',
                    f'<path d="M{lx-6},{ey-4} Q{lx-8},{ey} {lx-6},{ey+4}" fill="none" stroke="#000" stroke-width="1"/>',
                    f'<path d="M{lx+6},{ey-4} Q{lx+8},{ey} {lx+6},{ey+4}" fill="none" stroke="#000" stroke-width="1"/>',
                    f'<text x="{lx}" y="{ey+26}" text-anchor="middle" font-size="8" fill="#444" class="ct">{lbl}</text>',
                    f'<line x1="{lx+13}" y1="{ey}" x2="{right_rail-2}" y2="{ey}" class="w"/>']
            elif typ == 'COIL_SET':
                ml += [
                    f'<rect x="{lx-14}" y="{ey-11}" width="28" height="22" rx="3" fill="#E8F0FE" stroke="#1A56DB" stroke-width="1.3"/>',
                    f'<text x="{lx}" y="{ey+4}" text-anchor="middle" font-size="8" fill="#1A56DB" font-weight="bold">(S)</text>',
                    f'<text x="{lx}" y="{ey+26}" text-anchor="middle" font-size="8" fill="#444" class="ct">{lbl}</text>',
                    f'<line x1="{lx+14}" y1="{ey}" x2="{right_rail-2}" y2="{ey}" class="w"/>']
            elif typ == 'COIL_RESET':
                ml += [
                    f'<rect x="{lx-14}" y="{ey-11}" width="28" height="22" rx="3" fill="#FCE4EC" stroke="#DC2626" stroke-width="1.3"/>',
                    f'<text x="{lx}" y="{ey+4}" text-anchor="middle" font-size="8" fill="#DC2626" font-weight="bold">(R)</text>',
                    f'<text x="{lx}" y="{ey+26}" text-anchor="middle" font-size="8" fill="#444" class="ct">{lbl}</text>',
                    f'<line x1="{lx+14}" y1="{ey}" x2="{right_rail-2}" y2="{ey}" class="w"/>']
            elif typ == 'TIMER':
                tw, th = 64, 38
                parts = lbl.split('\n')
                ml += [
                    f'<rect x="{lx-tw//2}" y="{ey-th//2}" width="{tw}" height="{th}" rx="3" fill="#F0F4FF" stroke="#1A56DB" stroke-width="1.5"/>',
                    f'<text x="{lx}" y="{ey-9}" text-anchor="middle" font-size="9" font-weight="bold" fill="#1A56DB">{parts[0]}</text>',
                    f'<text x="{lx}" y="{ey+5}" text-anchor="middle" font-size="8" fill="#333">{parts[1] if len(parts)>1 else ""}</text>']
                ml.append(f'<line x1="{lx+tw//2}" y1="{ey}" x2="{right_rail-2}" y2="{ey}" class="w"/>')
            elif typ == 'FUNC':
                fw, fh = 48, 26
                ml += [
                    f'<rect x="{lx-fw/2}" y="{ey-fh/2}" width="{fw}" height="{fh}" rx="3" class="func-box"/>',
                    f'<text x="{lx}" y="{ey+4}" text-anchor="middle" font-size="8">{lbl}</text>']

        # 自锁支路
        if rung.get('self_hold'):
            bx_ratio = (rung['branch_from'] - 45) / 700.0
            bx = left_rail + bx_ratio * (right_rail - left_rail - 30)
            sx_ratio = (rung['self_x'] - 45) / 700.0
            sx = left_rail + sx_ratio * (right_rail - left_rail - 30)
            by2 = ey + 44
            ml += [
                f'<line x1="{bx}" y1="{ey}" x2="{bx}" y2="{by2}" class="w"/>',
                f'<line x1="{left_rail+6}" y1="{by2}" x2="{sx}" y2="{by2}" class="w"/>',
                f'<line x1="{sx}" y1="{by2-10}" x2="{sx}" y2="{by2-3}" class="contact-no"/>',
                f'<line x1="{sx}" y1="{by2+3}" x2="{sx}" y2="{by2+10}" class="contact-no"/>',
                f'<line x1="{sx-5}" y1="{by2-3}" x2="{sx+5}" y2="{by2-3}" class="contact-no"/>',
                f'<line x1="{sx-5}" y1="{by2+3}" x2="{sx+5}" y2="{by2+3}" class="contact-no"/>',
                f'<text x="{sx}" y="{by2+24}" text-anchor="middle" font-size="8" fill="#555">{rung.get("hold_lbl", "自锁")}</text>',
                f'<line x1="{sx+10}" y1="{by2}" x2="{bx}" y2="{by2}" class="w"/>']

    # ═══════════════════════════════════════
    # 状态栏
    # ═══════════════════════════════════════
    stat_y = content_y + editor_h
    A(f'<rect x="{WIN_X}" y="{stat_y}" width="{WIN_W}" height="{STAT_H}" rx="0" fill="#ECE9E4"/>')
    A(f'<line x1="{WIN_X}" y1="{stat_y}" x2="{WIN_X+WIN_W}" y2="{stat_y}" stroke="#A09890" stroke-width="0.8"/>')
    A(f'<text x="{WIN_X+10}" y="{stat_y+14}" font-size="9" fill="#666" class="ct">Ready</text>')
    A(f'<text x="{WIN_X+WIN_W-80}" y="{stat_y+14}" font-size="9" fill="#666" class="ct">Ln 1, Col 1</text>')

    # 窗口底部圆角修正
    A(f'<rect x="{WIN_X}" y="{WIN_Y+WIN_H-2}" width="2" height="2" fill="#ECE9E4"/>')
    A(f'<rect x="{WIN_X+WIN_W-2}" y="{WIN_Y+WIN_H-2}" width="2" height="2" fill="#ECE9E4"/>')

    # ═══════════════════════════════════════
    # I/O地址分配表 (窗口下方)
    # ═══════════════════════════════════════
    tbl_y = WIN_Y + WIN_H + 18
    cw = [68, 110, 68, 110, 120]
    tbl_w = sum(cw)
    tbl_x = WIN_X + 40
    cx_pos = [tbl_x]
    for k in range(1, len(cw)): cx_pos.append(cx_pos[-1] + cw[k-1])

    A(f'<text x="{tbl_x}" y="{tbl_y}" font-size="14" font-weight="bold" fill="white" class="cw">I/O 地址分配表 — {name}</text>')
    tsy = tbl_y + 14
    cols = ['输入端', '说明', '输出端', '说明', '备注']
    for j, (hdr, cx) in enumerate(zip(cols, cx_pos)):
        A(f'<rect x="{cx}" y="{tsy}" width="{cw[j]}" height="22" fill="#1A56DB"/>')
        A(f'<text x="{cx+cw[j]/2}" y="{tsy+15}" text-anchor="middle" font-size="10" font-weight="bold" fill="white" class="cw">{hdr}</text>')

    for ri, row in enumerate(io_table):
        ry = tsy + 22 + ri * 18
        fc = '#2D3748' if ri % 2 == 0 else '#374151'
        for j, (val, cx) in enumerate(zip(row, cx_pos)):
            if val:
                A(f'<rect x="{cx}" y="{ry}" width="{cw[j]}" height="18" fill="{fc}" stroke="#4B5563" stroke-width="0.5"/>')
                A(f'<text x="{cx+cw[j]/2}" y="{ry+13}" text-anchor="middle" font-size="8" fill="#E5E7EB" class="ct">{val}</text>')

    A('</svg>')
    return '\n'.join(ml)


def make_flow_svg(name, nodes, connections, subtitle=""):
    W, H = 650, 1060
    subtitle = subtitle or '西门子S7-1200控制流程'
    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" font-family="Microsoft YaHei, SimHei, sans-serif">',
        '<defs><marker id="ah" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#333"/></marker></defs>',
        f'<rect width="{W}" height="{H}" fill="#FAFBFC"/>',
        f'<text x="{W/2}" y="24" text-anchor="middle" font-size="14" font-weight="bold" fill="#1A56DB">{name} — 软件流程图 ({subtitle})</text>',
    ]

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


def make_circuit_dxf(name, io_table, folder):
    """生成电气原理图DXF — A3横向 CAD格式 (GB/T 4728, GB/T 14689)

    使用ezdxf库生成, 与SVG版内容一致, 含完整CAD图层和标题栏
    """
    import ezdxf
    from ezdxf import units
    doc = ezdxf.new('R2010')
    doc.units = units.MM
    # ── 图层 ──
    for ln,lw in [('FRAME',50),('FRAME_INNER',25),('POWER',50),('CONTROL',25),
                  ('PLC',25),('VFD',25),('HMI',18),('DEVICE',25),
                  ('TEXT',13),('WIRENO',13),('TERMINAL',25),('DASHED',18)]:
        ly=doc.layers.add(ln); ly.dxf.color=7; ly.dxf.lineweight=lw
    msp=doc.modelspace()
    def L(x1,y1,x2,y2,la='POWER'): msp.add_line((x1,y1),(x2,y2),dxfattribs={'layer':la})
    def T(x,y,t,h=3.0,la='TEXT'): msp.add_text(t,dxfattribs={'layer':la,'height':h,'insert':(x,y)})
    def Rx(x,y,w,h,la='DEVICE'): msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],dxfattribs={'layer':la})
    def C(x,y,r,la='DEVICE'): msp.add_circle((x,y),r,dxfattribs={'layer':la})

    # ── IO解析 ──
    inp=[(r[0].upper(),r[1]) for r in io_table if r[0] and r[0].upper().startswith('I') and not r[0].upper().startswith('IO')]
    out=[(r[2].upper(),r[3],r[4] if len(r)>4 else '') for r in io_table if r[2] and r[2].upper().startswith('Q')]
    pi=[(a,d) for a,d in inp if '.' in a and a.split('.')[0] in ('I0','I1')]
    po=[(a,d,r) for a,d,r in out if a]
    ni=len(pi); no=len(po)
    hfr=any('反转' in d or '下降' in d or '右转' in d or '后退' in d or '逆时针' in d or 'CCW' in d.upper() for _,d,_ in out)
    hbz=any('蜂鸣' in d for _,d,_ in out); hsw=any('限位' in r[1] for r in io_table if r[0] and 'I' in str(r[0]).upper()); hsn=any('传感器' in d or '液位' in d or '检测' in d for _,d in inp)
    hk3=any('KM3' in d or '补液' in d for _,d,_ in out); lc=3 if '塔吊' in name else 1
    ro={}
    for a,d,_ in out:
        ac=a.strip()
        if any(w in d for w in ['正转','前进','上升','左转','加注泵','CCW']): ro['fwd']=ac
        if any(w in d for w in ['反转','后退','下降','右转','回吸','CW']): ro['rev']=ac
        if '蜂鸣' in d: ro['buzzer']=ac
        if '指示' in d or '灯' in d: ro['lamp']=ac
        if hfr:
            if '低速' in d or 'S1' in d: ro['s1']=ac
            if '中速' in d or 'S2' in d: ro['s2']=ac
            if '高速' in d or 'S3' in d: ro['s3']=ac
        else:
            if '低速' in d or 'S1' in d: ro['s1']=ac
            if '中速' in d or 'S2' in d: ro['s2']=ac
            if '高速' in d or 'S3' in d: ro['s3']=ac
        if 'KM3' in d or '补液' in d: ro['km3']=ac
    def el(ak,fb):
        if ak in ro:
            dd=next((d for a,d,_ in out if a.strip()==ro[ak]),'')
            for kw,lb in [('上升','上升'),('下降','下降'),('左转','左转'),('右转','右转'),('加注泵','加注'),('回吸阀','回吸'),('打紧','打紧'),('松开','松开'),('正摆','正摆'),('反摆','反摆'),('前进','前进'),('后退','后退'),('正转','正转'),('反转','反转')]:
                if kw in dd: return lb
        return fb
    k1=el('fwd','运行'); k2=el('rev','反转')
    if not hfr: k1='运行'
    if '海盗船' in name: k1,k2='正摆','反摆'

    # ═══════════════════ A3图框 420×297mm ═══════════════════
    Rx(0,0,420,297,'FRAME'); Rx(25,10,385,277,'FRAME_INNER'); Rx(230,10,180,32,'FRAME')
    for y in [18,26,34]: L(230,y,410,y,'FRAME_INNER')
    for x in [255,290,315,335]: L(x,10,x,42,'FRAME_INNER')
    # 标题栏
    T(242.5,14,'自动化(专升本)252',2.5); T(302.5,14,'学    号',3.0); T(347.5,14,'图    幅',3.0); T(380,14,'A3',3.0)
    T(242.5,22,'制    图',3.0); T(302.5,22,'指导教师',3.0); T(347.5,22,'比    例',3.0); T(380,22,'NTS',3.0)
    T(242.5,30,'图    名',3.0); T(272.5,30,'电气原理图',3.0); T(302.5,30,'图    号',3.0)
    dn='KDBGL-'+('01' if '快递' in name or '包裹' in name else '02' if '混凝土' in name else '03' if '轮毂' in name else '04' if '电动葫芦' in name else '05' if '加注' in name else '06' if '塔吊' in name else '07' if '海盗船' in name else '08' if '轮胎' in name else '09')
    T(325,30,dn,3.0); T(347.5,30,'日    期',3.0); T(380,30,'2026.06',3.0)
    T(242.5,38,'设计题目',3.0); T(315,38,name,3.0)

    # ══════════ 虚线分区 (与参考DXF一致) ══════════
    Rx(25,166.5,177.1,120.5,'DASHED'); Rx(202.1,166.5,207.9,120.5,'DASHED')
    Rx(25,46,177.1,120.5,'DASHED'); Rx(202.1,46,207.9,120.5,'DASHED')
    T(113.5,283,'1. 主电路 (MAIN CIRCUIT)',3.2); T(306.1,283,'2. 控制电源及HMI通信 (CONTROL & HMI)',3.2)
    T(113.5,162.5,'3. PLC输入接线 (INPUT WIRING)',3.2); T(306.1,162.5,'4. PLC输出及变频器接线 (OUTPUT & VFD)',3.2)

    # ══════════ 1. 主电路: 水平布局 VFD→KM→FR→Motor (全部在A3框内) ══════════
    # L1/L2/L3/PE标签
    T(93,277,'L1',2.2,'WIRENO'); T(95,277,'L2',2.2,'WIRENO'); T(97,277,'L3',2.2,'WIRENO')
    T(41,279,'L1',3.5,'POWER'); T(41,266,'L2',3.5,'POWER'); T(41,253,'L3',3.5,'POWER')
    # 水平母线
    L(43,273,98,273,'POWER'); L(43,260,98,260,'POWER'); L(43,247,98,247,'POWER')
    L(43,234,98,234,'POWER')
    # QF1 断路器框
    Rx(59,231,24,32,'DEVICE')
    T(71,226,'QF1 DZ47-63/3P C16',3.5,'TEXT')
    L(62,242,80,242,'DEVICE'); L(62,247,80,247,'DEVICE'); L(62,252,80,252,'DEVICE')
    # QF进线
    L(98,273,83,273,'POWER'); L(98,260,85,260,'POWER'); L(98,247,87,247,'POWER')
    L(83,273,83,263,'POWER'); L(85,260,85,263,'POWER'); L(87,247,87,263,'POWER')
    # QF出线
    L(59,267,59,253,'POWER'); L(61,254,61,253,'POWER'); L(63,241,63,253,'POWER')
    # QF→VFD
    L(59,253,83,253,'POWER'); L(61,253,85,253,'POWER'); L(63,253,87,253,'POWER')
    L(83,231,83,219,'POWER'); L(85,231,85,219,'POWER'); L(87,231,87,219,'POWER')

    # VFD主框 (111,183)-(166,253)
    Rx(111,183,55,70,'VFD')
    T(138,218,'U1 变频器 V20',3.5,'VFD'); T(138,211,'1.5kW 0-50Hz',3.0,'VFD')
    for i,lb in enumerate(['R','S','T']): T(108,187+i*8,lb,2.8,'VFD')
    for i,lb in enumerate(['U','V','W']): T(168,187+i*8,lb,2.8,'VFD')
    # 进线→VFD
    L(83,219,112,219,'POWER'); L(85,219,116,219,'POWER'); L(87,219,120,219,'POWER')
    L(112,219,119,254,'POWER'); L(116,219,133,254,'POWER'); L(120,219,147,254,'POWER')

    # VFD输出→右侧水平 (3相线 U/V/W)
    voy=[237,245,253]  # 3相输出Y坐标, 都在VFD框内(183-253)
    L(147,voy[0],166,voy[0],'POWER'); L(147,voy[1],166,voy[1],'POWER'); L(147,voy[2],166,voy[2],'POWER')

    # KM+FR+Motor 水平布局参数
    km_x1,km_x2=172,190; fr_x1,fr_x2=198,216; mot_cx,mot_cy=258,245

    # 3相线: VFD右边缘→KM→FR→电机
    for py in voy:
        L(166,py,km_x1,py,'POWER'); L(fr_x2,py,mot_cx-9,py,'POWER')

    if hfr:
        # 正反转: KM1+KM2 上下排列
        Rx(km_x1,237,18,22,'POWER'); T(km_x1,232,f'KM1 {k1}',2.5,'TEXT')
        Rx(km_x1,217,18,16,'POWER'); T(km_x1,212,f'KM2 {k2}',2.5,'TEXT')
        for py in voy: C(km_x1+9,py,1.5,'POWER')
        L(km_x2,voy[0],fr_x1,voy[0],'POWER'); L(km_x2,voy[1],fr_x1,voy[1],'POWER'); L(km_x2,voy[2],fr_x1,voy[2],'POWER')
    else:
        # 单方向: 一个KM框覆盖3相
        Rx(km_x1,233,18,24,'POWER'); T(km_x1,230,f'KM1 ({k1})',2.5,'TEXT')
        for py in voy: C(km_x1+9,py,1.5,'POWER')
        L(km_x2,voy[0],fr_x1,voy[0],'POWER'); L(km_x2,voy[1],fr_x1,voy[1],'POWER'); L(km_x2,voy[2],fr_x1,voy[2],'POWER')

    # FR热继电器框
    Rx(fr_x1,233,18,24,'POWER'); T(fr_x1,230,'FR',2.5,'TEXT'); T(fr_x1,227,'NR2-25',2.2,'TEXT')
    for py in voy: C(fr_x1+9,py,1.5,'POWER')

    # 电机M (在FR右侧, 参考位置x≈258,y≈245)
    C(mot_cx,mot_cy,10,'DEVICE')
    T(mot_cx-2,mot_cy-2,'M',6.0,'DEVICE'); T(mot_cx-2,mot_cy+16,'3~',3.5,'POWER')
    T(mot_cx,mot_cy-14,'电机 0.75kW',2.5,'TEXT'); T(mot_cx,mot_cy-18,'380V',2.5,'TEXT')
    # 电机进线: 三相线汇聚到电机圆
    L(mot_cx-9,voy[0],mot_cx-4,mot_cy-4,'POWER')
    L(mot_cx-9,voy[1],mot_cx-2,mot_cy,'POWER')
    L(mot_cx-9,voy[2],mot_cx-4,mot_cy+4,'POWER')

    # PE接地 (左侧垂直向下)
    T(41,237,'PE',3.5,'POWER')
    pe_y=mot_cy+16; L(43,234,43,pe_y,'POWER')
    for j,gw in enumerate([24,16,8]): L(43-gw//2,pe_y+j*3,43+gw//2,pe_y+j*3,'POWER')

    # ══════════ 2. 控制电源及HMI: 严格参照参考DXF ══════════
    # L1取电
    L(98,273,217.1,273,'CONTROL'); L(217.1,273,217.1,272,'CONTROL')
    L(217.1,272,239.1,272,'CONTROL'); L(217.1,264,239.1,264,'CONTROL')
    T(215.1,275,'L',3.2,'CONTROL'); T(215.1,262,'N',3.2,'CONTROL')
    # FU1熔断器
    Rx(237.1,264,8,8,'CONTROL'); T(241.1,278,'FU1',3.0,'TEXT'); T(241.1,274,'2A',2.5,'TEXT')
    L(239.1,272,243.1,272,'CONTROL'); L(245.1,268,255.1,268,'CONTROL'); L(253.1,268,253.1,252,'CONTROL')
    # PS1开关电源
    Rx(235.1,220,32,32,'CONTROL')
    T(251.1,246,'PS1',3.5,'CONTROL'); T(251.1,240,'AC220V/',3.0,'CONTROL'); T(251.1,236,'DC24V',3.0,'CONTROL'); T(251.1,232,'100W',3.0,'CONTROL')
    L(253.1,252,259.1,252,'CONTROL'); L(259.1,252,259.1,244,'CONTROL')
    # +24V/0V母线
    L(267.1,244,328.1,244,'CONTROL'); L(267.1,232,328.1,232,'CONTROL')
    T(273.1,249,'+24V',3.5,'CONTROL'); T(273.1,228,'0V',3.5,'CONTROL')
    T(280.1,240,'DC 24V 供电: PLC, HMI, 按钮, 指示灯',2.8,'TEXT')
    # HMI
    Rx(220.1,181.5,55,35,'HMI'); Rx(223.1,184.5,49,25,'HMI')
    T(247.6,201,'HMI1 KTP700 Basic',3.2,'HMI')
    L(275.1,199,313.1,199,'HMI')
    T(280.1,204,'Profinet / Ethernet',2.8,'TEXT'); T(280.1,196,'← PLC1 PROFINET',2.5,'TEXT')
    # +24V/0V向下
    L(328.1,244,328.1,155,'CONTROL'); L(328.1,232,328.1,155,'CONTROL')

    # ══════════ 3. PLC输入接线 (参照参考DXF) ══════════
    # PLC框:参考 30,49→95,151.5
    plx,ply=30,49; plw,plh=65,102.5
    Rx(plx,ply,plw,plh,'PLC'); Rx(plx,ply,plw,plh,'FRAME_INNER')  # 双线框
    T(62,145,'PLC1 CPU 1214C',3.5,'PLC'); T(62,139,'DC/DC/DC',3.5,'PLC'); T(62,133,'24DI/16DQ',3.5,'PLC')

    # DI端子小方块
    rh=9.0; dby=73.0  # I0.0起始Y (参考73.0)
    for j,(addr,_) in enumerate(pi):
        dy=dby+j*rh
        if dy>=149: break
        Rx(26,dy-1.5,4,3,'PLC'); L(3,dy,26,dy,'PLC')

    # X1端子排
    T(-30,142.5,'X1',3.0,'TERMINAL')
    for j,(addr,desc) in enumerate(pi):
        dy=dby+j*rh
        if dy>=149: break
        Rx(-28,dy-1.5,4,3,'TERMINAL')

    # 输入器件
    for j,(addr,desc) in enumerate(pi):
        dy=dby+j*rh
        if dy>=149: break
        sn=desc[:8]
        T(-18,dy+1,sn,2.5,'TEXT')
        nc='停止' in desc or '急停' in desc
        if nc:
            # NC触点
            L(-17,dy,-11,dy,'DEVICE'); L(-9,dy,-3,dy,'DEVICE')
            L(-11,dy-3,-11,dy+3,'DEVICE'); L(-9,dy-3,-9,dy+3,'DEVICE')
            L(-11,dy,-9,dy+3,'DEVICE')
            L(-17,dy-3,-17,dy+3,'DEVICE'); L(-3,dy-3,-3,dy+3,'DEVICE')
        elif '限位' in desc:
            L(-17,dy,-12,dy,'DEVICE'); L(-9,dy,-3,dy,'DEVICE')
            L(-9,dy-3,-15,dy,'DEVICE'); L(-12,dy-3,-12,dy+3,'DEVICE'); L(-9,dy-3,-9,dy+3,'DEVICE')
        elif '液位' in desc or '传感器' in desc or '检测' in desc:
            L(-17,dy,-12,dy,'DEVICE'); L(-9,dy,-3,dy,'DEVICE'); C(-12,dy,2,'DEVICE')
        else:
            # NO触点
            L(-17,dy,-11,dy,'DEVICE'); L(-9,dy,-3,dy,'DEVICE')
            L(-11,dy-3,-11,dy+3,'DEVICE'); L(-9,dy-3,-9,dy+3,'DEVICE')
        L(-3,dy,3,dy,'CONTROL')

    # +24V→X1
    T(-13,145.5,'+24V',3.0,'TEXT')
    L(-13,145,3,dby,'CONTROL')

    # ══════════ 4. PLC输出&VFD (参照参考DXF) ══════════
    # DQ端子
    for j,(addr,_,_) in enumerate(po):
        dy=dby+j*rh
        if dy>=149: break
        Rx(95,dy-1.5,4,3,'PLC'); L(99,dy,125,dy,'PLC')

    # X2端子排
    T(142.5,142.5,'X2',3.0,'TERMINAL')
    for j,(addr,_,_) in enumerate(po):
        dy=dby+j*rh
        if dy>=149: break
        Rx(100,dy-1.5,4,3,'TERMINAL')

    # 输出器件
    for j,(addr,desc,_) in enumerate(po):
        dy=dby+j*rh
        if dy>=149: break
        is_km=any(w in desc for w in ['正转','反转','上升','下降','左转','右转','加注','回吸','打紧','松开','前进','后退','正摆','反摆','补液'])
        is_la='灯' in desc or '指示' in desc
        is_bz='蜂鸣' in desc
        L(125,dy,135,dy,'CONTROL')
        if is_km:
            Rx(135,dy-5,14,10,'DEVICE')
            kl=desc[:6].replace('输出','').replace(' ','')
            if j==0: kl=k1[:4]
            elif j==1 and hfr: kl=k2[:4]
            T(137,dy-3,kl,2.2,'TEXT')
            L(149,dy+1,200,dy+1,'CONTROL')
        elif is_la:
            C(142,dy,4.5,'DEVICE')
            L(139.5,dy-2.5,144.5,dy+2.5,'DEVICE'); L(144.5,dy-2.5,139.5,dy+2.5,'DEVICE')
            T(150,dy+1,desc[:6],2.5,'TEXT')
        elif is_bz:
            Rx(135,dy-5,14,10,'DEVICE'); T(137,dy-3,'HA',2.2,'TEXT')
        T(98,dy+1,addr,2.5,'WIRENO')

    # VFD控制端子框 (参考: 182,86.5→234,136.5)
    Rx(182,86.5,52,50,'VFD'); T(208,138,'U1 变频器控制端子',3.2,'VFD')
    # 6路端子线
    term_ys=[132.5,125.5,118.5,111.5,104.5,97.5]
    for oy in term_ys: L(213,oy,233,oy,'VFD')
    # 端子标注
    T(185,133,f'DI1  {k1}',2.8,'VFD')
    if hfr: T(185,126,f'DI2  {k2}',2.8,'VFD')
    else: T(185,126,'DI2  反转',2.8,'VFD')
    T(185,119,'DI3  使能',2.8,'VFD')
    T(185,112,'DCM  公共端',2.8,'VFD'); T(185,105,'AI1   0-10V',2.8,'VFD'); T(185,98,'ACM  模拟公共',2.8,'VFD')
    T(200,91.9,'X3',3.0,'TERMINAL')

    # 指示灯/蜂鸣器标签
    if lc>=1: T(135,110.1,'HL1 绿色运行灯',2.5,'DEVICE')
    if lc>=2: T(135,101.2,'HL2 黄色停止灯',2.5,'DEVICE')
    if lc>=3: T(135,92.3,'HL3 蓝色常亮',2.5,'DEVICE')
    if hbz: T(135,83.4,'HA 蜂鸣器',2.5,'DEVICE')

    # ══════════ 注释 ══════════
    nt=['注: 1. 急停SB和停止SB采用常闭(NC)触点 — 断线时系统自动停止(失效安全原则)。']
    if hfr:
        nt.append('     2. 正反转通过PLC程序互锁，Q0.0与Q0.1不能同时为ON，变频器输出U/V/W直接连接电机。')
        n3='     3. 绿色运行灯HL1通过闪烁实现1s间隔亮灭；'
        if lc>=2: n3+='黄色HL2停止时点亮；'
        if lc>=3: n3+='蓝色HL3常停时点亮。'
        nt.append(n3)
    for j,tt in enumerate(nt): T(30,47-j*3.5,tt,2.5,'TEXT')

    # ── 保存 ──
    dxf_path=os.path.join(folder,f'{name}电路原理图.dxf')
    doc.saveas(dxf_path)
    print(f'[OK] 原理图DXF: {os.path.getsize(dxf_path)//1024}KB')
    return dxf_path


def make_circuit_svg(name, io_table):
    """生成电气原理图 — A3横向 黑白CAD风格 (GB/T 4728, GB/T 14689)

    纯黑白配色, 精细元件符号, 含QS刀开关/熔断器/端子排/线号/互锁/辅助触点
    标题栏: GB/T学生格式, 图名两行
    """
    VW, VH = 1680, 1188
    OF_X, OF_Y = 15, 12
    OF_W, OF_H = VW - 30, VH - 24
    IF_L, IF_R, IF_T, IF_B = 100, 20, 20, 20
    IF_X = OF_X + IF_L; IF_Y = OF_Y + IF_T
    IF_W = OF_W - IF_L - IF_R; IF_H = OF_H - IF_T - IF_B

    inputs = [(r[0].upper(), r[1]) for r in io_table if r[0] and r[0].upper().startswith('I') and not r[0].upper().startswith('IO')]
    outputs = [(r[2].upper(), r[3], r[4] if len(r) > 4 else '') for r in io_table if r[2] and r[2].upper().startswith('Q')]
    has_fwd_rev = any('反转' in d or '下降' in d or '右转' in d or '后退' in d or '逆时针' in d or 'CCW' in d.upper() for _, d, _ in outputs)
    has_buzzer = any('蜂鸣' in d for _, d, _ in outputs)
    has_limit_sw = any('限位' in r[1] for r in io_table if r[0] and 'I' in str(r[0]).upper() and not 'IO' in str(r[0]).upper())
    has_sensor = any('传感器' in d or '液位' in d or '检测' in d for _, d in inputs)
    has_km3 = any('KM3' in d or '补液' in d or '补液泵' in n for _, d, n in outputs)
    km_count = 2 if has_fwd_rev else 1
    sb_count = sum(1 for _, d in inputs if 'SB' in d)
    # Detect specific output roles
    out_roles = {}
    for addr, desc, note in outputs:
        addr_clean = addr.strip()
        if any(w in desc for w in ['正转','前进','上升','左转','加注泵','CCW']): out_roles['fwd'] = addr_clean
        if any(w in desc for w in ['反转','后退','下降','右转','回吸','CW']): out_roles['rev'] = addr_clean
        if '蜂鸣' in desc: out_roles['buzzer'] = addr_clean
        if '指示' in desc or '灯' in desc: out_roles['lamp'] = addr_clean
        if '低速' in desc or 'S1' in desc: out_roles['s1'] = addr_clean
        if '中速' in desc or 'S2' in desc: out_roles['s2'] = addr_clean
        if '高速' in desc or 'S3' in desc: out_roles['s3'] = addr_clean
        if 'KM3' in desc or '补液' in desc: out_roles['km3'] = addr_clean

    # Extract KM labels from output descriptions
    def _extract_label(addr_key, fallback):
        if addr_key in out_roles:
            desc = next((d for a, d, _ in outputs if a.strip() == out_roles[addr_key]), '')
            for kw, lbl in [('上升','上升'),('下降','下降'),('左转','左转'),('右转','右转'),
                            ('加注泵','加注'),('回吸阀','回吸'),('打紧','打紧'),('松开','松开'),
                            ('正摆','正摆'),('反摆','反摆'),('前进','前进'),('后退','后退'),
                            ('正转','正转'),('反转','反转')]:
                if kw in desc: return lbl
        return fallback
    # Detect system name from io_table context (passed via name param)
    is_tower_crane = '塔吊' in name
    is_filling = '加注' in name
    is_hoist = '电动葫芦' in name
    is_hub = '轮毂' in name
    is_pirate = '海盗船' in name
    is_concrete = '混凝土' in name or '搅拌' in name
    is_package = '快递' in name or '包裹' in name
    is_tire = '轮胎' in name
    is_cups = '转转杯' in name

    km1_label = _extract_label('fwd', '运行')
    km2_label = _extract_label('rev', '反转')
    # Single-direction systems use '运行' regardless of description
    if not has_fwd_rev:
        km1_label = '运行'
    # System-specific label overrides
    if is_pirate:
        km1_label, km2_label = '正摆', '反摆'

    ml = []
    A = lambda s: ml.append(s)

    # ── 纯黑白样式 ──
    A(f'<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" font-family="Microsoft YaHei, SimHei, sans-serif">')
    A('<style>')
    A('.f14{font:14px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.f12{font:12px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.f11{font:11px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.f10{font:10px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.f9{font:9px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.f8{font:8px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.f7{font:7px Microsoft YaHei,SimHei,sans-serif;fill:#000}')
    A('.cm{text-anchor:middle;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.ce{text-anchor:end;font-family:Microsoft YaHei,SimHei,sans-serif}')
    A('.fw{font-weight:bold}')
    A('.th{stroke:#000;stroke-width:3;fill:none}')
    A('.tn{stroke:#000;stroke-width:1.5;fill:none}')
    A('.td{stroke:#000;stroke-width:0.8;fill:none;stroke-dasharray:4,3}')
    A('.bx{fill:#fff;stroke:#000;stroke-width:2}')
    A('.bxg{fill:#f5f5f5;stroke:#000;stroke-width:1.8}')
    A('.bxw{fill:#fff;stroke:#000;stroke-width:1.5}')
    A('.d{fill:#000}')
    A('</style>')
    A(f'<rect width="{VW}" height="{VH}" fill="#fff"/>')

    # ═══════════════════════════════
    # A3图框
    # ═══════════════════════════════
    A(f'<rect x="{OF_X}" y="{OF_Y}" width="{OF_W}" height="{OF_H}" fill="none" stroke="#000" stroke-width="1"/>')
    A(f'<rect x="{IF_X}" y="{IF_Y}" width="{IF_W}" height="{IF_H}" fill="none" stroke="#000" stroke-width="2.5"/>')
    for (cx, cy, w, h) in [(VW//2, OF_Y-3, 20, 3), (VW//2, OF_Y+OF_H, 20, 3),
                             (OF_X-3, VH//2, 3, 20), (OF_X+OF_W, VH//2, 3, 20)]:
        A(f'<rect x="{cx-w//2}" y="{cy-h//2}" width="{w}" height="{h}" fill="#000"/>')

    # ═══════════════════════════════
    # 元件明细表
    # ═══════════════════════════════
    BOM_X=IF_X+8; BOM_Y=IF_Y+6; BOM_W=455; BOM_RH=15
    # ── 动态元件明细表 ──
    _bom = [('序号','代号','名称','型号规格','数量','备注')]
    _n = 1
    _bom.append((str(_n),'QS','刀开关','HD11-40/38 40A','1','电源总开关')); _n+=1
    _bom.append((str(_n),'QF','断路器','DZ47-63 3P/16A','1','短路/过载')); _n+=1
    _bom.append((str(_n),'FU1-3','熔断器','RT18-32 16A','3','主电路保护')); _n+=1
    _bom.append((str(_n),'FU4','熔断器','RT18-32 2A','1','控制回路')); _n+=1
    _bom.append((str(_n),'VFD','变频器','台达VFD-M 1.5kW','1','0-50Hz')); _n+=1
    if has_fwd_rev:
        _bom.append((str(_n),'KM1-2','交流接触器','CJX2-0910','2',f'{km1_label}/{km2_label}')); _n+=1
    else:
        _bom.append((str(_n),'KM1','交流接触器','CJX2-0910','1',km1_label)); _n+=1
    if has_km3:
        _bom.append((str(_n),'KM3','交流接触器','CJX2-0910','1','补液泵')); _n+=1
    _bom.append((str(_n),'FR','热继电器','NR2-25 7-10A','1','过载保护')); _n+=1
    _bom.append((str(_n),'M','三相异步电机','Y2-90L-4 1.5kW','1','380V')); _n+=1
    _bom.append((str(_n),'PLC','可编程控制器','S7-1200 CPU 1214C','1','DC/DC/DC')); _n+=1
    _bom.append((str(_n),'PS','开关电源','S-100-24','1','DC24V/4.5A')); _n+=1
    _bom.append((str(_n),f'SB1-{sb_count}','按钮','LA38-11',str(sb_count),'启/停/急停'+(',方向' if sb_count>=4 else ''))); _n+=1
    _lamp_count = 3 if is_tower_crane else 1
    _bom.append((str(_n),'HL1'+(f'-{_lamp_count}' if _lamp_count>1 else ''),'指示灯','AD16-22DS',str(_lamp_count),'24V'+(',方向指示' if is_tower_crane else ''))); _n+=1
    if has_buzzer:
        _bom.append((str(_n),'HA','蜂鸣器','AD16-22SM','1','24V')); _n+=1
    if has_limit_sw:
        _bom.append((str(_n),'SQ1-2','限位开关','LX19-001','2','行程终端保护')); _n+=1
    if has_sensor:
        if is_filling:
            _bom.append((str(_n),'SL1-2','液位传感器','LJ12A3-4-Z/BX','2','液位上下限')); _n+=1
        else:
            _bom.append((str(_n),'SQ1','光电传感器','E3F-DS30C4','1','到位检测')); _n+=1
    parts = _bom
    BOM_H=len(parts)*BOM_RH+4
    col_w = [30,52,70,110,28,105]
    A(f'<rect x="{BOM_X}" y="{BOM_Y}" width="{BOM_W}" height="{BOM_H}" fill="none" stroke="#000" stroke-width="1.5"/>')
    A(f'<text x="{BOM_X+BOM_W//2}" y="{BOM_Y-5}" class="f9 cm fw">元件明细表</text>')
    for ri,row in enumerate(parts):
        ry=BOM_Y+2+ri*BOM_RH
        if ri==0:
            A(f'<rect x="{BOM_X}" y="{ry-2}" width="{BOM_W}" height="{BOM_RH}" fill="#f0f0f0" stroke="#000" stroke-width="0.8"/>')
        else:
            A(f'<line x1="{BOM_X}" y1="{ry-2}" x2="{BOM_X+BOM_W}" y2="{ry-2}" stroke="#000" stroke-width="0.3"/>')
        cx=BOM_X+1
        for ci,(cell,cw) in enumerate(zip(row,col_w)):
            if ci>0:
                A(f'<line x1="{cx}" y1="{ry-2}" x2="{cx}" y2="{ry+BOM_RH-2}" stroke="#000" stroke-width="0.3"/>')
            fs='f10 cm fw' if ri==0 else 'f8'
            tx=cx+(cw//2 if ri==0 else 2)
            ty=ry+BOM_RH-5
            A(f'<text x="{tx}" y="{ty}" class="{fs}">{cell}</text>')
            cx+=cw

    # ═══════════════════════════════
    # 分区标签
    # ═══════════════════════════════
    SEC_Y=IF_Y+BOM_H+20
    A(f'<text x="{IF_X+40}" y="{SEC_Y+12}" class="f14 fw">主电路 (Main Circuit) · AC 380V 50Hz</text>')
    A(f'<text x="{IF_X+460}" y="{SEC_Y+12}" class="f14 fw">控制电路 (Control Circuit) · DC 24V</text>')
    A(f'<line x1="{IF_X}" y1="{SEC_Y+18}" x2="{IF_X+IF_W}" y2="{SEC_Y+18}" stroke="#000" stroke-width="0.6"/>')

    # ═══════════════════════════════
    # 主电路 (左侧 380V)
    # ═══════════════════════════════
    LX=IF_X+55; LX2=LX+50; LX3=LX+100; MCX=LX+50
    MTOP=SEC_Y+35

    # ── 三相电源引入 ──
    A(f'<text x="{MCX}" y="{MTOP-10}" class="f8 cm">~380V 50Hz 三相四线制</text>')
    for lx,lbl in [(LX,'L1'),(LX2,'L2'),(LX3,'L3')]:
        A(f'<text x="{lx}" y="{MTOP-18}" class="f10 cm fw">{lbl}</text>')
        A(f'<circle cx="{lx}" cy="{MTOP}" r="3" class="d"/>')
        A(f'<line x1="{lx}" y1="{MTOP}" x2="{lx}" y2="{MTOP+22}" class="th"/>')
        A(f'<text x="{lx+12}" y="{MTOP+16}" class="f7">1</text>')

    # ── QS 刀开关 (电源总开关) ──
    QS_Y=MTOP+22; QS_H=70
    A(f'<rect x="{LX-18}" y="{QS_Y}" width="136" height="{QS_H}" rx="2" class="bxg"/>')
    A(f'<text x="{MCX}" y="{QS_Y-5}" class="f11 cm fw">QS</text>')
    A(f'<text x="{MCX}" y="{QS_Y+QS_H+12}" class="f8 cm">HD11-40/38 刀开关</text>')
    for lx in [LX,LX2,LX3]:
        A(f'<circle cx="{lx}" cy="{QS_Y+8}" r="2.5" class="d"/>')
        A(f'<line x1="{lx}" y1="{QS_Y+8}" x2="{lx}" y2="{QS_Y+22}" class="th"/>')
        # 刀开关符号: 斜线表示可断开
        A(f'<line x1="{lx-10}" y1="{QS_Y+22}" x2="{lx+16}" y2="{QS_Y+46}" stroke="#000" stroke-width="2.5"/>')
        A(f'<circle cx="{lx+16}" cy="{QS_Y+46}" r="3" fill="none" stroke="#000" stroke-width="1.5"/>')
        A(f'<line x1="{lx}" y1="{QS_Y+46}" x2="{lx}" y2="{QS_Y+QS_H}" class="th"/>')
        A(f'<circle cx="{lx}" cy="{QS_Y+QS_H}" r="2.5" class="d"/>')

    # ── QF 断路器 ──
    QF_Y=QS_Y+QS_H+14; QF_H=72
    A(f'<rect x="{LX-18}" y="{QF_Y}" width="136" height="{QF_H}" rx="2" class="bxg"/>')
    A(f'<text x="{MCX}" y="{QF_Y-5}" class="f11 cm fw">QF</text>')
    A(f'<text x="{MCX}" y="{QF_Y+QF_H+11}" class="f8 cm">DZ47-63 3P/16A</text>')
    for lx in [LX,LX2,LX3]:
        A(f'<circle cx="{lx}" cy="{QF_Y+6}" r="2" class="d"/>')
        A(f'<line x1="{lx}" y1="{QS_Y+QS_H}" x2="{lx}" y2="{QF_Y+6}" class="th"/>')
        A(f'<line x1="{lx}" y1="{QF_Y+6}" x2="{lx}" y2="{QF_Y+18}" class="th"/>')
        A(f'<line x1="{lx-6}" y1="{QF_Y+18}" x2="{lx+6}" y2="{QF_Y+34}" class="th"/>')
        A(f'<line x1="{lx+6}" y1="{QF_Y+18}" x2="{lx-6}" y2="{QF_Y+34}" class="th"/>')
        A(f'<line x1="{lx}" y1="{QF_Y+34}" x2="{lx}" y2="{QF_Y+QF_H}" class="th"/>')
        A(f'<circle cx="{lx}" cy="{QF_Y+QF_H}" r="2" class="d"/>')

    # ── FU1-FU3 熔断器 ──
    FU_Y=QF_Y+QF_H+12; FU_H=36
    A(f'<text x="{MCX}" y="{FU_Y-4}" class="f10 cm fw">FU1~3</text>')
    A(f'<text x="{MCX+70}" y="{FU_Y+10}" class="f7">RT18-32/16A</text>')
    for lx in [LX,LX2,LX3]:
        A(f'<rect x="{lx-5}" y="{FU_Y}" width="10" height="{FU_H}" rx="1.5" fill="none" stroke="#000" stroke-width="1.5"/>')
        A(f'<line x1="{lx-4}" y1="{FU_Y+5}" x2="{lx+4}" y2="{FU_Y+12}" stroke="#000" stroke-width="0.7"/>')
        A(f'<line x1="{lx}" y1="{QF_Y+QF_H}" x2="{lx}" y2="{FU_Y}" class="th"/>')
        A(f'<line x1="{lx}" y1="{FU_Y+FU_H}" x2="{lx}" y2="{FU_Y+FU_H+10}" class="th"/>')

    # ── 端子排 XT1 (主电路) ──
    XT1_Y=FU_Y+FU_H+10; XT1_H=22
    A(f'<rect x="{LX-18}" y="{XT1_Y}" width="136" height="{XT1_H}" rx="2" fill="none" stroke="#000" stroke-width="1.5" stroke-dasharray="3,2"/>')
    A(f'<text x="{MCX}" y="{XT1_Y+14}" class="f9 cm fw">XT1 (主电路端子排)</text>')
    for lx in [LX,LX2,LX3]:
        A(f'<line x1="{lx}" y1="{FU_Y+FU_H}" x2="{lx}" y2="{XT1_Y}" class="th"/>')
        A(f'<line x1="{lx}" y1="{XT1_Y+XT1_H}" x2="{lx}" y2="{XT1_Y+XT1_H+7}" class="th"/>')
        A(f'<circle cx="{lx}" cy="{XT1_Y+XT1_H+7}" r="2" class="d"/>')

    # ── VFD 变频器 ──
    VFD_Y=XT1_Y+XT1_H+7; VFD_H=130
    A(f'<rect x="{LX-20}" y="{VFD_Y}" width="140" height="{VFD_H}" rx="3" class="bxw"/>')
    A(f'<text x="{MCX}" y="{VFD_Y-5}" class="f11 cm fw">VFD</text>')
    A(f'<text x="{MCX}" y="{VFD_Y+16}" class="f9 cm fw">台达 VFD-M</text>')
    A(f'<text x="{MCX}" y="{VFD_Y+32}" class="f8 cm">1.5kW 0-50Hz</text>')
    A(f'<text x="{MCX}" y="{VFD_Y+47}" class="f8 cm">3Φ380Vin→0-380Vout</text>')
    # 输入端子
    for i,lb in enumerate(['R','S','T']):
        A(f'<text x="{LX-26}" y="{VFD_Y+16+i*12}" class="f7 ce">{lb}</text>')
        A(f'<circle cx="{LX-8}" cy="{VFD_Y+11+i*12}" r="1.5" class="d"/>')
    # 输出端子
    for i,lb in enumerate(['U','V','W']):
        A(f'<text x="{LX+132}" y="{VFD_Y+68+i*12}" class="f7">{lb}</text>')
        A(f'<circle cx="{LX+124}" cy="{VFD_Y+63+i*12}" r="1.5" class="d"/>')
    # 控制端子
    _vfd_terms = f'M0 M1 M2 GND S1 S2 S3' if has_fwd_rev else f'M0 GND S1 S2 S3'
    _vfd_funcs = f'{km1_label} {km2_label} 复位 地 多段速' if has_fwd_rev else f'{km1_label} 地 多段速'
    A(f'<text x="{MCX}" y="{VFD_Y+98}" class="f7 cm">{_vfd_terms}</text>')
    A(f'<text x="{MCX}" y="{VFD_Y+112}" class="f7 cm">{_vfd_funcs}</text>')
    # XT1→VFD (R/S/T) 连线
    for lx in [LX,LX2,LX3]:
        A(f'<line x1="{lx}" y1="{XT1_Y+XT1_H+7}" x2="{lx}" y2="{VFD_Y}" class="th"/>')
    # VFD输出引出
    for i,lx in enumerate([LX,LX2,LX3]):
        A(f'<line x1="{lx}" y1="{VFD_Y+VFD_H}" x2="{lx}" y2="{VFD_Y+VFD_H+10}" class="th"/>')
        A(f'<circle cx="{lx}" cy="{VFD_Y+VFD_H+10}" r="2" class="d"/>')

    # ── 端子排 XT2 (VFD输出→KM) ──
    XT2_Y=VFD_Y+VFD_H+10; XT2_H=20
    A(f'<rect x="{LX-18}" y="{XT2_Y}" width="136" height="{XT2_H}" rx="2" fill="none" stroke="#000" stroke-width="1.5" stroke-dasharray="3,2"/>')
    A(f'<text x="{MCX}" y="{XT2_Y+13}" class="f9 cm fw">XT2 (变频器输出端子排)</text>')
    for lx in [LX,LX2,LX3]:
        A(f'<line x1="{lx}" y1="{XT2_Y}" x2="{lx}" y2="{XT2_Y+XT2_H}" class="th"/>')

    # ── KM 接触器主触点 ──
    KM_Y=XT2_Y+XT2_H+10; KM_H=50
    if has_fwd_rev:
        A(f'<text x="{LX-14}" y="{KM_Y-4}" class="f10 cm fw">KM1</text>')
        A(f'<text x="{LX-14}" y="{KM_Y+KM_H+12}" class="f8 cm">{km1_label}</text>')
        A(f'<text x="{LX3+38}" y="{KM_Y-4}" class="f10 cm fw">KM2</text>')
        A(f'<text x="{LX3+38}" y="{KM_Y+KM_H+12}" class="f8 cm">{km2_label}</text>')
        # KM1: L1相
        A(f'<rect x="{LX-10}" y="{KM_Y}" width="20" height="{KM_H}" rx="2" class="bxw"/>')
        for tag,ky in [('in',KM_Y+6),('out',KM_Y+KM_H-6)]:
            A(f'<circle cx="{LX}" cy="{ky}" r="2" class="d"/>')
        A(f'<circle cx="{LX}" cy="{KM_Y+22}" r="4.5" fill="none" stroke="#000" stroke-width="2"/>')
        A(f'<line x1="{LX}" y1="{KM_Y+6}" x2="{LX}" y2="{KM_Y+22}" class="th"/>')
        A(f'<line x1="{LX}" y1="{KM_Y+22}" x2="{LX}" y2="{KM_Y+KM_H-6}" class="th"/>')
        # KM2: L3相
        A(f'<rect x="{LX3-10}" y="{KM_Y}" width="20" height="{KM_H}" rx="2" class="bxw"/>')
        for tag,ky in [('in',KM_Y+6),('out',KM_Y+KM_H-6)]:
            A(f'<circle cx="{LX3}" cy="{ky}" r="2" class="d"/>')
        A(f'<circle cx="{LX3}" cy="{KM_Y+22}" r="4.5" fill="none" stroke="#000" stroke-width="2"/>')
        A(f'<line x1="{LX3}" y1="{KM_Y+6}" x2="{LX3}" y2="{KM_Y+22}" class="th"/>')
        A(f'<line x1="{LX3}" y1="{KM_Y+22}" x2="{LX3}" y2="{KM_Y+KM_H-6}" class="th"/>')
        # L2相直通
        A(f'<circle cx="{LX2}" cy="{KM_Y+KM_H}" r="2" class="d"/>')
        # 互锁标志
        A(f'<line x1="{LX+10}" y1="{KM_Y+KM_H//2}" x2="{LX3-10}" y2="{KM_Y+KM_H//2}" class="td"/>')
        A(f'<text x="{MCX}" y="{KM_Y+KM_H//2+3}" class="f7 cm">互锁</text>')
        # XT2→KM 连线
        for lx in [LX,LX2,LX3]:
            A(f'<line x1="{lx}" y1="{XT2_Y+XT2_H}" x2="{lx}" y2="{KM_Y}" class="th"/>')
    else:
        A(f'<text x="{LX-14}" y="{KM_Y-4}" class="f10 cm fw">KM1</text>')
        A(f'<text x="{LX-14}" y="{KM_Y+KM_H+12}" class="f8 cm">{km1_label}</text>')
        for lx in [LX,LX2,LX3]:
            A(f'<rect x="{lx-10}" y="{KM_Y}" width="20" height="{KM_H}" rx="2" class="bxw"/>')
            A(f'<circle cx="{lx}" cy="{KM_Y+6}" r="2" class="d"/>')
            A(f'<circle cx="{lx}" cy="{KM_Y+22}" r="4.5" fill="none" stroke="#000" stroke-width="2"/>')
            A(f'<line x1="{lx}" y1="{KM_Y+6}" x2="{lx}" y2="{KM_Y+22}" class="th"/>')
            A(f'<line x1="{lx}" y1="{KM_Y+22}" x2="{lx}" y2="{KM_Y+KM_H-6}" class="th"/>')
            A(f'<circle cx="{lx}" cy="{KM_Y+KM_H-6}" r="2" class="d"/>')
            A(f'<line x1="{lx}" y1="{XT2_Y+XT2_H}" x2="{lx}" y2="{KM_Y}" class="th"/>')

    # ── FR 热继电器 ──
    FR_Y=KM_Y+KM_H+12; FR_H=50
    A(f'<rect x="{LX-18}" y="{FR_Y}" width="136" height="{FR_H}" rx="2" class="bxg"/>')
    A(f'<text x="{MCX}" y="{FR_Y-4}" class="f10 cm fw">FR</text>')
    A(f'<text x="{MCX}" y="{FR_Y+FR_H+11}" class="f8 cm">NR2-25 7-10A</text>')
    for lx in [LX,LX2,LX3]:
        A(f'<rect x="{lx-8}" y="{FR_Y+5}" width="16" height="{FR_H-10}" rx="1.5" fill="#fafafa" stroke="#000" stroke-width="1.2"/>')
        for k in range(3):
            A(f'<line x1="{lx-6}" y1="{FR_Y+10+k*11}" x2="{lx+6}" y2="{FR_Y+15+k*11}" stroke="#000" stroke-width="0.7"/>')
        A(f'<circle cx="{lx}" cy="{FR_Y-2}" r="2.5" class="d"/>')
        A(f'<line x1="{lx}" y1="{KM_Y+KM_H-6 if not has_fwd_rev else KM_Y+KM_H}" x2="{lx}" y2="{FR_Y-2}" class="th"/>')
        A(f'<circle cx="{lx}" cy="{FR_Y+FR_H}" r="2.5" class="d"/>')

    # ── 电机 M ──
    MOT_R=30; MOT_CY=FR_Y+FR_H+MOT_R+10
    A(f'<circle cx="{MCX}" cy="{MOT_CY}" r="{MOT_R}" class="bx"/>')
    A(f'<text x="{MCX}" y="{MOT_CY-7}" class="f14 cm fw">M</text>')
    A(f'<text x="{MCX}" y="{MOT_CY+18}" class="f10 cm">Y2-90L-4</text>')
    A(f'<text x="{MCX}" y="{MOT_CY+32}" class="f8 cm">1.5kW 3~</text>')
    for i,(lx,la) in enumerate([(LX,'U1'),(LX2,'V1'),(LX3,'W1')]):
        A(f'<line x1="{lx}" y1="{FR_Y+FR_H}" x2="{lx}" y2="{MOT_CY-18+i*14}" class="th"/>')
        A(f'<text x="{lx+10}" y="{MOT_CY-22}" class="f7">{la}</text>')
    # PE 接地
    gy=MOT_CY+MOT_R
    A(f'<line x1="{MCX}" y1="{gy}" x2="{MCX}" y2="{gy+14}" class="th"/>')
    for j,gw in enumerate([26,16,8]):
        A(f'<line x1="{MCX-gw//2}" y1="{gy+14+j*4}" x2="{MCX+gw//2}" y2="{gy+14+j*4}" class="th"/>')
    A(f'<text x="{MCX+16}" y="{gy+28}" class="f9">PE</text>')

    # ═══════════════════════════════
    # 控制电路 — 极简：器件—线—PLC—线—器件
    # ═══════════════════════════════
    CX0=IF_X+430; CY0=SEC_Y+40
    phys_in=[(a,d) for a,d in inputs if '.' in a and a.split('.')[0] in ('I0','I1')]
    phys_out=[(a,d,r) for a,d,r in outputs if a]
    ni=len(phys_in); no=len(phys_out)
    row_h=20; plc_h=max(ni,no)*row_h+50

    # ── PLC 块 ──
    PLC_X=CX0+120; PLC_Y=CY0+14; PLC_W=220
    A(f'<rect x="{PLC_X}" y="{PLC_Y}" width="{PLC_W}" height="{plc_h}" rx="3" class="bxg"/>')
    A(f'<text x="{PLC_X+PLC_W//2}" y="{PLC_Y+18}" class="f9 cm fw">PLC S7-1200</text>')
    A(f'<text x="{PLC_X+PLC_W//2}" y="{PLC_Y+32}" class="f7 cm">CPU 1214C DC/DC/DC</text>')

    # DI/DQ 引脚
    di_y0=PLC_Y+46; dq_y0=PLC_Y+46
    for j,(addr,desc) in enumerate(phys_in):
        dy=di_y0+j*row_h
        A(f'<circle cx="{PLC_X}" cy="{dy}" r="2" class="d"/>')
        A(f'<text x="{PLC_X+6}" y="{dy+3}" class="f7 fw">{addr}</text>')
        A(f'<text x="{PLC_X+42}" y="{dy+3}" class="f7">{desc[:8]}</text>')
    for j,(addr,desc,_) in enumerate(phys_out):
        dy=dq_y0+j*row_h
        A(f'<circle cx="{PLC_X+PLC_W}" cy="{dy}" r="2" class="d"/>')
        A(f'<text x="{PLC_X+PLC_W-44}" y="{dy+3}" class="f7 fw">{addr}</text>')
        A(f'<text x="{PLC_X+PLC_W-92}" y="{dy+3}" class="f7 ce">{desc[:8]}</text>')

    # ── 输入器件 (左侧) + 连线 ──
    in_x=CX0; in_sx=in_x+32
    for j,(addr,desc) in enumerate(phys_in):
        iy=di_y0+j*row_h
        # 简单触点符号
        A(f'<circle cx="{in_x+16}" cy="{iy}" r="2" class="d"/>')
        A(f'<line x1="{in_x+20}" y1="{iy}" x2="{in_sx}" y2="{iy}" class="tn"/>')
        if '急停' in desc:
            A(f'<line x1="{in_sx}" y1="{iy-7}" x2="{in_x+20}" y2="{iy+6}" stroke="#000" stroke-width="1.2"/>')
            A(f'<circle cx="{in_sx+4}" cy="{iy}" r="2" class="d"/>')
        elif '限位' in desc:
            A(f'<line x1="{in_sx-4}" y1="{iy-5}" x2="{in_sx}" y2="{iy}" stroke="#000" stroke-width="0.8"/>')
            A(f'<circle cx="{in_sx+4}" cy="{iy}" r="2" class="d"/>')
        elif '液位' in desc or '传感器' in desc or '检测' in desc:
            A(f'<rect x="{in_sx-4}" y="{iy-5}" width="5" height="10" rx="1" fill="none" stroke="#000" stroke-width="1"/>')
            A(f'<circle cx="{in_sx+5}" cy="{iy}" r="2" class="d"/>')
        else:
            A(f'<circle cx="{in_sx+4}" cy="{iy}" r="2" class="d"/>')
        # 器件名称
        A(f'<text x="{in_x+44}" y="{iy+4}" class="f8">{desc[:6]}</text>')
        # 连线→PLC
        A(f'<line x1="{in_sx+5}" y1="{iy}" x2="{PLC_X}" y2="{iy}" class="tn"/>')

    # ── 输出器件 (右侧) + 连线 ──
    out_x=PLC_X+PLC_W+52
    for j,(addr,desc,_) in enumerate(phys_out):
        oy=dq_y0+j*row_h
        A(f'<line x1="{PLC_X+PLC_W}" y1="{oy}" x2="{out_x}" y2="{oy}" class="tn"/>')
        # 器件符号
        if any(w in desc for w in ['正转','反转','上升','下降','左转','右转','加注','回吸','打紧','松开','前进','后退','正摆','反摆','补液']):
            A(f'<rect x="{out_x}" y="{oy-6}" width="18" height="12" rx="2" class="bxw"/>')
            A(f'<line x1="{out_x}" y1="{oy-6}" x2="{out_x+18}" y2="{oy+6}" stroke="#000" stroke-width="0.7"/>')
            _sym_w=18
        elif '蜂鸣' in desc:
            A(f'<path d="M{out_x+3},{oy} L{out_x+3},{oy-6} L{out_x+15},{oy-6} L{out_x+15},{oy}" fill="none" stroke="#000" stroke-width="1.2"/>')
            A(f'<rect x="{out_x}" y="{oy-6}" width="18" height="12" rx="2" class="bxw"/>')
            _sym_w=18
        elif '灯' in desc or '指示' in desc:
            A(f'<circle cx="{out_x+9}" cy="{oy}" r="6" fill="none" stroke="#000" stroke-width="1.2"/>')
            A(f'<line x1="{out_x+3}" y1="{oy-5}" x2="{out_x+15}" y2="{oy+5}" stroke="#000" stroke-width="0.5"/>')
            A(f'<line x1="{out_x+15}" y1="{oy-5}" x2="{out_x+3}" y2="{oy+5}" stroke="#000" stroke-width="0.5"/>')
            _sym_w=18
        else:
            _sym_w=0
        A(f'<text x="{out_x+_sym_w+4}" y="{oy+4}" class="f8">{desc[:10]}</text>')

	    # ── 电源 ──
    A(f'<text x="{PLC_X+PLC_W//2}" y="{PLC_Y-6}" class="f7 cm fw">DC 24V (S-100-24)</text>')
    A(f'<line x1="{PLC_X+PLC_W//2}" y1="{PLC_Y-2}" x2="{PLC_X+PLC_W//2}" y2="{PLC_Y}" class="tn"/>')

    # ── VFD控制端子接线 (紧凑表) ──
    TY=PLC_Y+plc_h+10
    _fwd_q=out_roles.get('fwd','Q0.0'); _rev_q=out_roles.get('rev','Q0.1')
    _s1_q=out_roles.get('s1','Q0.4'); _s2_q=out_roles.get('s2','Q0.5'); _s3_q=out_roles.get('s3','Q0.6')
    vfd_lines=[]
    if has_fwd_rev:
        vfd_lines.append(f'VFD M0({km1_label})←PLC {_fwd_q}    VFD M1({km2_label})←PLC {_rev_q}')
    else:
        vfd_lines.append(f'VFD M0({km1_label})←PLC {_fwd_q}    VFD GND←PLC COM')
    vfd_lines.append(f'VFD S1(低速)←PLC {_s1_q}    VFD S2(中速)←PLC {_s2_q}')
    vfd_lines.append(f'VFD S3(高速)←PLC {_s3_q}    DCM←PLC 1M')
    for j,ln in enumerate(vfd_lines):
        A(f'<text x="{CX0+50}" y="{TY+12+j*14}" class="f7">{ln}</text>')

    # ── 保护说明 (紧凑两列) ──
    PTY=TY+len(vfd_lines)*14+10
    notes=[]
    if has_fwd_rev: notes.append(f'KM1-KM2 电气互锁({km1_label}/{km2_label})')
    if has_limit_sw: notes.append('SQ1-SQ2 硬限位行程保护')
    if has_sensor:
        notes.append('液位传感器自动补液控制' if is_filling else '到位传感器自动停止')
    if is_tower_crane: notes.append('方向指示灯+蜂鸣器双重警示')
    notes.append('急停最高优先级,触发即停')
    notes.append('电机外壳PE接地≤4Ω')
    for j,nt in enumerate(notes):
        A(f'<text x="{CX0+8+(j%2)*400}" y="{PTY+j//2*13}" class="f7">· {nt}</text>')

    # ── 图幅分区 ──
    div_w=IF_W/8
    for di in range(9):
        dx=IF_X+di*div_w
        A(f'<text x="{dx-5}" y="{IF_Y+IF_H+10}" class="f7 cm">{di}</text>')
        A(f'<line x1="{dx}" y1="{IF_Y+IF_H}" x2="{dx}" y2="{IF_Y+IF_H+5}" stroke="#000" stroke-width="0.5"/>')
    for di,dl in enumerate(['A','B','C','D']):
        dy=IF_Y+(di+0.5)*(IF_H/4)
        A(f'<text x="{IF_X-10}" y="{dy+4}" class="f7 ce">{dl}</text>')

    A('</svg>')
    return '\n'.join(ml)


def make_hmi_svg(name, io_table):
    """生成人机界面(HMI) — KTP700 Basic 7寸触摸屏 800x480

    根据系统类型自动生成对应操作界面：状态指示灯/控制按钮/参数显示/报警条
    """
    VW, VH = 800, 480

    # ── 解析IO ──
    inputs = [(r[0].upper(), r[1]) for r in io_table if r[0] and r[0].upper().startswith('I')]
    outputs = [(r[2].upper(), r[3], r[4] if len(r) > 4 else '') for r in io_table if r[2] and r[2].upper().startswith('Q')]
    has_fwd_rev = any('反转' in d or '下降' in d or '右转' in d or '后退' in d or '逆时针' in d or 'CCW' in d.upper() for _, d, _ in outputs)
    has_buzzer = any('蜂鸣' in d for _, d, _ in outputs)
    has_limit = any('限位' in d for _, d in inputs)
    has_sensor = any('传感器' in d or '液位' in d or '检测' in d for _, d in inputs)
    has_speed_adj = any('加速' in d or '减速' in d for _, d in inputs)
    has_estop = any('急停' in d for _, d in inputs)
    sb_count = sum(1 for _, d in inputs if 'SB' in d)

    # 解析输出角色
    out_roles = {}
    for addr, desc, _ in outputs:
        a = addr.strip()
        if any(w in desc for w in ['正转','前进','上升','左转','加注泵','CCW','正摆']): out_roles['fwd'] = a
        if any(w in desc for w in ['反转','后退','下降','右转','回吸','CW','反摆']): out_roles['rev'] = a
        if '蜂鸣' in desc: out_roles['buzzer'] = a
        if '指示' in desc or '灯' in desc:
            lst = out_roles.get('lamps', []); lst.append((a, desc)); out_roles['lamps'] = lst
        if '低速' in desc or 'S1' in desc: out_roles['s1'] = a
        if '中速' in desc or 'S2' in desc: out_roles['s2'] = a
        if '高速' in desc or 'S3' in desc: out_roles['s3'] = a
        if 'KM3' in desc or '补液' in desc: out_roles['km3'] = a

    lamps = out_roles.get('lamps', [])
    lamp_count = len(lamps)

    # 系统类型检测
    is_concrete = '混凝土' in name or '搅拌' in name
    is_package = '快递' in name or '包裹' in name
    is_hub = '轮毂' in name
    is_hoist = '电动葫芦' in name
    is_filling = '加注' in name
    is_pirate = '海盗船' in name
    is_tire = '轮胎' in name
    is_cups = '转转杯' in name
    is_tower = '塔吊' in name

    # 方向标签
    if is_hoist:
        fwd_lbl, rev_lbl = '上升', '下降'
    elif is_hub:
        fwd_lbl, rev_lbl = '打紧', '松开'
    elif is_filling:
        fwd_lbl, rev_lbl = '加注', '回吸'
    elif is_pirate:
        fwd_lbl, rev_lbl = '正摆', '反摆'
    elif is_tower:
        fwd_lbl, rev_lbl = '左转', '右转'
    else:
        fwd_lbl, rev_lbl = '正转', '反转'

    ml = []
    A = lambda s: ml.append(s)

    A(f'<?xml version="1.0" encoding="UTF-8"?>')
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" font-family="Microsoft YaHei, SimHei, sans-serif">')
    A('<style>')
    A('.bg{fill:#E8ECF0} .header{fill:#1A56DB} .panel{fill:#FFF;stroke:#B0B8C4;stroke-width:1.5;rx:6}')
    A('.btn{fill:#1A56DB;rx:4} .btn_stop{fill:#DC2626;rx:4} .btn_estop{fill:#F59E0B;rx:4} .btn_dis{fill:#9CA3AF;rx:4}')
    A('.led_green{fill:#16A34A} .led_red{fill:#DC2626} .led_yellow{fill:#F59E0B} .led_gray{fill:#D1D5DB}')
    A('.txt_w{fill:#FFF;font-size:13px;text-anchor:middle;font-weight:bold}')
    A('.txt_b{fill:#1E293B;font-size:13px;text-anchor:middle}')
    A('.txt_bb{fill:#1E293B;font-size:14px;text-anchor:middle;font-weight:bold}')
    A('.txt_s{fill:#64748B;font-size:11px;text-anchor:middle}')
    A('.txt_h{fill:#FFF;font-size:16px;font-weight:bold}')
    A('.txt_alarm{fill:#DC2626;font-size:12px;font-weight:bold}')
    A('.alarm_bar{fill:#FEF2F2;stroke:#FCA5A5;stroke-width:1;rx:3}')
    A('.gauge_bg{fill:#F1F5F9;stroke:#CBD5E1;stroke-width:2}')
    A('.gauge_fill{fill:#1A56DB}')
    A('</style>')

    # ── 背景 ──
    A(f'<rect width="{VW}" height="{VH}" class="bg"/>')

    # ══════════ 顶部标题栏 ══════════
    A(f'<rect x="0" y="0" width="{VW}" height="42" class="header"/>')
    A(f'<text x="20" y="28" class="txt_h">SIEMENS</text>')
    A(f'<text x="{VW//2}" y="28" class="txt_h" text-anchor="middle">{name}</text>')
    A(f'<text x="{VW-20}" y="28" class="txt_h" text-anchor="end">KTP700 Basic</text>')

    # ══════════ 主区域布局 ══════════
    # 左侧面板: 状态指示 (x=10..210, y=52..440)
    left_x, left_w = 10, 195
    A(f'<rect x="{left_x}" y="52" width="{left_w}" height="388" class="panel"/>')
    A(f'<text x="{left_x+left_w//2}" y="72" class="txt_bb">系统状态</text>')
    A(f'<line x1="{left_x+15}" y1="80" x2="{left_x+left_w-15}" y2="80" stroke="#E2E8F0" stroke-width="1"/>')

    # LED指示灯
    led_x = left_x + 30; val_x = left_x + 50
    led_items = [('运行', 'green', any(w in name for w in ['快递','混凝土','海盗船','轮胎','转转杯','塔吊','搅拌','加注'])),
                 ('蜂鸣器', 'yellow' if has_buzzer else 'gray', has_buzzer),
                 ('急停', 'red' if has_estop else 'gray', has_estop)]
    if has_fwd_rev:
        led_items.insert(1, (fwd_lbl, 'green', True))
        led_items.insert(2, (rev_lbl, 'green', True))
    if has_limit:
        led_items.append(('上限位', 'yellow', True))
        led_items.append(('下限位', 'yellow', True))
    if has_sensor:
        if is_filling:
            led_items.append(('液位低', 'red', True))
            led_items.append(('液位高', 'green', True))
        else:
            led_items.append(('传感器', 'green', True))
    if has_speed_adj:
        led_items.append(('加速', 'green', True))
        led_items.append(('减速', 'yellow', True))

    for j, (lbl, color, _) in enumerate(led_items):
        ly = 92 + j * 28
        cls = f'led_{color}'
        A(f'<circle cx="{led_x}" cy="{ly+4}" r="7" class="{cls}"/>')
        A(f'<text x="{val_x+5}" y="{ly+8}" class="txt_b" text-anchor="start">{lbl}</text>')

    # 速度档位显示
    speed_y = 92 + len(led_items) * 28 + 10
    A(f'<line x1="{left_x+15}" y1="{speed_y-5}" x2="{left_x+left_w-15}" y2="{speed_y-5}" stroke="#E2E8F0" stroke-width="1"/>')
    A(f'<text x="{left_x+left_w//2}" y="{speed_y+14}" class="txt_bb">速度档位</text>')
    speeds = ['低速 15Hz', '中速 25Hz', '高速 50Hz']
    if is_cups: speeds = ['低速 10Hz', '中速 25Hz', '高速 40Hz']
    if is_concrete: speeds = ['低速 15Hz', '中速 20Hz', '高速 30Hz']
    if is_tire: speeds = ['低速 20Hz', '中速 35Hz', '高速 50Hz']
    if is_filling: speeds = ['低速 20Hz', '中速 35Hz', '—']
    for j, sp in enumerate(speeds):
        sy = speed_y + 26 + j * 22
        A(f'<rect x="{led_x-7}" y="{sy-3}" width="14" height="14" rx="2" class="led_gray"/>')
        A(f'<text x="{val_x+5}" y="{sy+9}" class="txt_s" text-anchor="start">{sp}</text>')

    # ══════════ 中央面板: 流程可视化 ══════════
    ctr_x, ctr_w = 215, 370
    A(f'<rect x="{ctr_x}" y="52" width="{ctr_w}" height="388" class="panel"/>')
    A(f'<text x="{ctr_x+ctr_w//2}" y="72" class="txt_bb">运行监控</text>')
    A(f'<line x1="{ctr_x+15}" y1="80" x2="{ctr_x+ctr_w-15}" y2="80" stroke="#E2E8F0" stroke-width="1"/>')

    cx, cy = ctr_x + ctr_w//2, 210

    if is_concrete:
        # 搅拌循环示意图: 正转6s → 反转6s 循环
        A(f'<circle cx="{cx-80}" cy="{cy}" r="30" class="gauge_bg"/>')
        A(f'<text x="{cx-80}" y="{cy+5}" class="txt_bb">搅拌罐</text>')
        A(f'<path d="M{cx-80},{cy-30} A30,30 0 1,1 {cx-79},{cy-30}" stroke="#16A34A" stroke-width="5" fill="none" stroke-dasharray="94,94" stroke-dashoffset="47"/>')
        A(f'<text x="{cx-80}" y="{cy+45}" class="txt_s">正转6s/反转6s</text>')
        # 定时器
        A(f'<text x="{cx+40}" y="{cy-15}" class="txt_bb" text-anchor="start">T37 正转计时</text>')
        A(f'<rect x="{cx+40}" y="{cy-5}" width="100" height="18" class="gauge_bg" rx="3"/>')
        A(f'<rect x="{cx+42}" y="{cy-3}" width="60" height="14" class="gauge_fill" rx="2"/>')
        A(f'<text x="{cx+90}" y="{cy+8}" class="txt_s">6.0s</text>')
        A(f'<text x="{cx+40}" y="{cy+35}" class="txt_bb" text-anchor="start">T38 反转计时</text>')
        A(f'<rect x="{cx+40}" y="{cy+45}" width="100" height="18" class="gauge_bg" rx="3"/>')
        A(f'<rect x="{cx+42}" y="{cy+47}" width="30" height="14" rx="2" fill="#F59E0B"/>')
        A(f'<text x="{cx+90}" y="{cy+58}" class="txt_s">3.0s</text>')
    elif is_package or is_tire:
        # 传送带示意图
        A(f'<rect x="{cx-90}" y="{cy-25}" width="80" height="50" rx="8" class="gauge_bg"/>')
        A(f'<text x="{cx-50}" y="{cy+5}" class="txt_bb">传送带</text>')
        # 包裹
        A(f'<rect x="{cx-20}" y="{cy-18}" width="28" height="18" rx="3" fill="#F59E0B" stroke="#D97706" stroke-width="1"/>')
        A(f'<text x="{cx-6}" y="{cy-6}" class="txt_s">包裹</text>')
        # 方向箭头
        A(f'<text x="{cx-50}" y="{cy+45}" class="txt_s">方向: {fwd_lbl}</text>')
        # 传感器 (仅轮胎)
        if is_tire:
            A(f'<circle cx="{cx+40}" cy="{cy}" r="6" class="led_green"/>')
            A(f'<text x="{cx+55}" y="{cy+5}" class="txt_s" text-anchor="start">检测传感器</text>')
    elif is_hub:
        # 打紧机示意图
        A(f'<circle cx="{cx-50}" cy="{cy}" r="35" class="gauge_bg"/>')
        A(f'<text x="{cx-50}" y="{cy+5}" class="txt_bb">轮毂</text>')
        A(f'<text x="{cx-50}" y="{cy+50}" class="txt_s">SQ1正转限位 / SQ2反转限位</text>')
        # 力矩指示
        A(f'<text x="{cx+50}" y="{cy-15}" class="txt_bb" text-anchor="start">操作状态</text>')
        A(f'<rect x="{cx+50}" y="{cy-5}" width="80" height="22" rx="4" class="gauge_fill"/>')
        A(f'<text x="{cx+90}" y="{cy+10}" class="txt_w">{fwd_lbl}中</text>')
    elif is_hoist:
        # 电动葫芦示意图
        A(f'<rect x="{cx-30}" y="{cy-40}" width="60" height="80" rx="6" class="gauge_bg"/>')
        A(f'<text x="{cx}" y="{cy+5}" class="txt_bb">吊钩</text>')
        A(f'<line x1="{cx+35}" y1="{cy-40}" x2="{cx+35}" y2="{cy+40}" stroke="#1A56DB" stroke-width="2" stroke-dasharray="4,3"/>')
        # 限位标记
        A(f'<text x="{cx+50}" y="{cy-35}" class="txt_s" text-anchor="start">SQ1上限位</text>')
        A(f'<text x="{cx+50}" y="{cy+35}" class="txt_s" text-anchor="start">SQ2下限位</text>')
        A(f'<text x="{cx+50}" y="{cy}" class="txt_b" text-anchor="start">高度: 安全</text>')
    elif is_filling:
        # 加注机示意图
        A(f'<rect x="{cx-80}" y="{cy-35}" width="50" height="70" rx="5" class="gauge_bg"/>')
        A(f'<text x="{cx-55}" y="{cy+5}" class="txt_bb">储液罐</text>')
        # 液位
        A(f'<rect x="{cx-75}" y="{cy+15}" width="40" height="15" rx="2" class="gauge_fill"/>')
        A(f'<text x="{cx-55}" y="{cy+55}" class="txt_s">SL1/SL2液位</text>')
        # 加注/回吸状态
        A(f'<text x="{cx+20}" y="{cy-10}" class="txt_bb" text-anchor="start">加注泵 KM1</text>')
        A(f'<rect x="{cx+20}" y="{cy}" width="80" height="18" class="gauge_fill" rx="3"/>')
        A(f'<text x="{cx+60}" y="{cy+13}" class="txt_w">{fwd_lbl}中</text>')
        A(f'<text x="{cx+20}" y="{cy+35}" class="txt_bb" text-anchor="start">回吸阀 KM2</text>')
        A(f'<rect x="{cx+20}" y="{cy+45}" width="80" height="18" rx="3" fill="#9CA3AF"/>')
        A(f'<text x="{cx+60}" y="{cy+58}" class="txt_w">待机</text>')
    elif is_pirate:
        # 海盗船摆动示意图
        A(f'<rect x="{cx-70}" y="{cy-45}" width="140" height="90" rx="8" class="gauge_bg"/>')
        A(f'<text x="{cx}" y="{cy+5}" class="txt_bb">海盗船摆台</text>')
        # 摆动弧线
        A(f'<path d="M{cx-50},{cy+40} Q{cx},{cy-20} {cx+50},{cy+40}" stroke="#1A56DB" stroke-width="2" fill="none"/>')
        A(f'<text x="{cx-60}" y="{cy+55}" class="txt_s">正摆3s</text>')
        A(f'<text x="{cx+60}" y="{cy+55}" class="txt_s">反摆3s</text>')
        A(f'<text x="{cx}" y="{cy-50}" class="txt_bb">T37/T38循环</text>')
    elif is_cups:
        # 转转杯旋转示意图
        A(f'<circle cx="{cx}" cy="{cy}" r="45" class="gauge_bg"/>')
        A(f'<circle cx="{cx}" cy="{cy}" r="20" fill="#1A56DB" opacity="0.3"/>')
        A(f'<text x="{cx}" y="{cy+5}" class="txt_bb">旋转杯台</text>')
        A(f'<text x="{cx}" y="{cy+55}" class="txt_s">MW0: 速度等级 1/2/3</text>')
    elif is_tower:
        # 塔吊旋转示意图
        A(f'<rect x="{cx-15}" y="{cy-40}" width="30" height="80" rx="4" class="gauge_bg"/>')
        A(f'<text x="{cx}" y="{cy+5}" class="txt_bb">塔身</text>')
        A(f'<line x1="{cx-50}" y1="{cy-30}" x2="{cx+50}" y2="{cy-30}" stroke="#1A56DB" stroke-width="3"/>')
        A(f'<text x="{cx-60}" y="{cy-25}" class="txt_s">左转CCW</text>')
        A(f'<text x="{cx+60}" y="{cy-25}" class="txt_s">右转CW</text>')
        A(f'<circle cx="{cx}" cy="{cy-30}" r="5" class="led_green"/>')
        A(f'<text x="{cx}" y="{cy+50}" class="txt_s">HL1/HL2/HL3 方向指示</text>')

    # 定时器显示 (通用)
    if any(w in name for w in ['快递','海盗船','轮胎','转转杯']):
        timer_label = 'T37 预警计时'
        if is_pirate: timer_label = 'T37/T38/T39 摆动定时'
        A(f'<text x="{ctr_x+ctr_w//2}" y="320" class="txt_bb">{timer_label}</text>')
        A(f'<rect x="{ctr_x+60}" y="330" width="{ctr_w-120}" height="22" class="gauge_bg" rx="4"/>')
        A(f'<rect x="{ctr_x+62}" y="332" width="{ctr_w-170}" height="18" class="gauge_fill" rx="3"/>')
        A(f'<text x="{ctr_x+ctr_w//2}" y="347" class="txt_w">3.0s / 3.0s</text>')

    # ══════════ 右侧面板: 控制按钮 ══════════
    btn_x, btn_w = 595, 195
    A(f'<rect x="{btn_x}" y="52" width="{btn_w}" height="388" class="panel"/>')
    A(f'<text x="{btn_x+btn_w//2}" y="72" class="txt_bb">操作面板</text>')
    A(f'<line x1="{btn_x+15}" y1="80" x2="{btn_x+btn_w-15}" y2="80" stroke="#E2E8F0" stroke-width="1"/>')

    btn_cx = btn_x + btn_w//2; bw, bh = 150, 36
    by = 100; bgap = 46

    # 启动按钮
    A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh}" class="btn"/>')
    A(f'<text x="{btn_cx}" y="{by+bh//2+5}" class="txt_w">启 动 (SB1)</text>')

    # 停止按钮
    by += bgap
    A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh}" class="btn_stop"/>')
    A(f'<text x="{btn_cx}" y="{by+bh//2+5}" class="txt_w">停 止 (SB2)</text>')

    # 方向按钮
    if has_fwd_rev:
        by += bgap
        A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh}" class="btn"/>')
        A(f'<text x="{btn_cx}" y="{by+bh//2+5}" class="txt_w">{fwd_lbl} (SB)</text>')

        by += bgap
        A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh}" class="btn"/>')
        A(f'<text x="{btn_cx}" y="{by+bh//2+5}" class="txt_w">{rev_lbl} (SB)</text>')
    elif has_speed_adj:
        by += bgap
        A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh}" class="btn"/>')
        A(f'<text x="{btn_cx}" y="{by+bh//2+5}" class="txt_w">加 速 (SB4)</text>')
        by += bgap
        A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh}" class="btn"/>')
        A(f'<text x="{btn_cx}" y="{by+bh//2+5}" class="txt_w">减 速 (SB5)</text>')

    # 急停按钮
    by += bgap
    A(f'<rect x="{btn_cx-bw//2}" y="{by}" width="{bw}" height="{bh+8}" class="btn_estop"/>')
    A(f'<text x="{btn_cx}" y="{by+bh//2+9}" class="txt_w" font-size="15">急 停 (EMG)</text>')

    # ══════════ 底部报警栏 ══════════
    bar_y = 448
    A(f'<rect x="10" y="{bar_y}" width="780" height="24" class="alarm_bar"/>')
    alarm_texts = []
    if has_buzzer: alarm_texts.append('蜂鸣器预警')
    if has_limit: alarm_texts.append('限位开关触发')
    if has_estop: alarm_texts.append('急停按钮释放')
    alarm_msg = ' | '.join(alarm_texts) if alarm_texts else '系统正常 — 无报警'
    A(f'<text x="20" y="{bar_y+16}" class="txt_alarm" text-anchor="start">报警: {alarm_msg}</text>')

    A('</svg>')
    return '\n'.join(ml)


def svg2png_edge(svg_paths, folder):
    """Convert SVGs to PNGs using Edge headless"""
    edge = None
    for p in EDGE_PATHS:
        if os.path.exists(p):
            edge = p
            break
    if not edge:
        print('[WARN] Edge not found')
        return

    for svg_path in svg_paths:
        if not os.path.exists(svg_path):
            continue
        png_path = svg_path.replace('.svg', '.png')
        html_path = svg_path.replace('.svg', '_tmp.html')
        fname = os.path.basename(svg_path)
        html = f'<html><head><meta charset="utf-8"></head><body style="margin:0;padding:0;background:white"><object data="{fname}" type="image/svg+xml" style="width:100%"></object></body></html>'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        if '梯形图' in fname:
            size = '1800,2600'
        elif '原理图' in fname:
            size = '1680,1188'  # A3 viewBox 1680×1188 at 1:1
        else:
            size = '1400,2200'
        cmd = [edge, '--headless=new', '--disable-gpu', '--no-sandbox',
               f'--window-size={size}', '--hide-scrollbars', '--force-device-scale-factor=2',
               f'--screenshot={os.path.abspath(png_path)}', html_path]
        subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=folder)
        if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
            print(f'  [OK] {os.path.basename(png_path)} ({os.path.getsize(png_path)//1024}KB)')
        else:
            print(f'  [FAIL] {os.path.basename(png_path)}')
        if os.path.exists(html_path):
            os.remove(html_path)


# ============================================================
# 系统定义
# ============================================================

def sys_package_conveyor():
    """快递包裹运输控制系统"""
    name = '快递包裹运输控制系统'
    folder = os.path.join(BASE, '快递包裹运输控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '正转输出 KM1',     '电机正转/传送带前进'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '反转输出 KM2',     '电机反转/传送带后退'],
        ['I0.2', '确认按钮 SB3',   'Q0.2', '蜂鸣器 HA',        '3秒预警提示'],
        ['I0.3', '方向选择 SB4',   'Q0.3', '运行指示灯 HL1',   '绿色'],
        ['I0.4', '急停按钮 SB5',   'Q0.4', '低速 VFD-S1',      '15Hz'],
        ['M0.0', '系统运行使能',    'Q0.5', '中速 VFD-S2',      '30Hz'],
        ['M0.1', '正转方向',       'Q0.6', '高速 VFD-S3',      '50Hz'],
        ['M0.2', '反转方向',       'T37',  '闪烁定时器',        'TON 100ms×10=1s'],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 系统运行使能(自锁) - 启动+确认=ON, 停止/急停=OFF',
            'elements': [
                ('NO', 100, 'I0.0\n启动'), ('NO', 210, 'I0.2\n确认'),
                ('NC', 320, 'I0.1\n停止'), ('NC', 430, 'I0.4\n急停'),
                ('COIL', 600, 'M0.0\n运行'),
            ],
            'self_hold': True, 'self_x': 155, 'branch_from': 350, 'hold_lbl': 'M0.0'
        },
        {
            'label': 'Network 2: 方向切换(上升沿检测) - 方向键触发脉冲M0.3',
            'elements': [
                ('NO', 100, 'I0.3\n方向'),
                ('FUNC', 250, 'PLS\nM0.3'),
            ]
        },
        {
            'label': 'Network 3: 方向记忆(交替翻转) - M0.3脉冲→M0.1/M0.2交替',
            'elements': [
                ('NO', 100, 'M0.3\n脉冲'),
                ('NC', 210, 'M0.1\n正转'),
                ('COIL_SET', 350, 'M0.2\n反转'),
                ('NO', 480, 'M0.3\n脉冲'),
                ('NO', 590, 'M0.2\n反转'),
                ('COIL_RESET', 730, 'M0.1\n正转'),
            ]
        },
        {
            'label': 'Network 4: 正转输出(M0.0+M0.1+互锁→Q0.0)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NO', 210, 'M0.1\n正转'),
                ('NC', 320, 'Q0.1\n反转互锁'), ('COIL', 500, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 5: 反转输出(M0.0+M0.2+互锁→Q0.1)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NO', 210, 'M0.2\n反转'),
                ('NC', 320, 'Q0.0\n正转互锁'), ('COIL', 500, 'Q0.1\n反转'),
            ]
        },
        {
            'label': 'Network 6: 闪烁定时器 T37(100ms×10=1s)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'),
                ('TIMER', 250, 'T37\nTON\nPT=10'),
            ]
        },
        {
            'label': 'Network 7: 蜂鸣器预警(M0.0运行后, 首次3s鸣响)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'T37\n1s到'),
                ('COIL', 400, 'Q0.2\n蜂鸣器'),
            ]
        },
        {
            'label': 'Network 8: 速度选择(默认中速Q0.5)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('COIL', 250, 'Q0.5\n中速'),
            ]
        },
        {
            'label': 'Network 9: 急停/停止→复位所有',
            'elements': [
                ('NC', 100, 'I0.1\n停止'),
                ('COIL_RESET', 250, 'M0.0\n(3点)'),
                ('NC', 400, 'I0.4\n急停'),
                ('COIL_RESET', 550, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化\n默认中速Q0.5', 325, 95, 120, 45, 'box', '#E8F0FE'),
        ('chk_estop', '急停释放?', 325, 170, 100, 45, 'diamond', '#FFF3CD'),
        ('wait', '等待启动+确认', 325, 245, 120, 40, 'box', '#E8F0FE'),
        ('sys_run', 'M0.0=1\n系统运行\n运行灯Q0.3亮', 325, 320, 135, 50, 'box', '#D4EDDA'),
        ('buzzer', '蜂鸣器Q0.2响\nT37计时', 325, 405, 130, 45, 'box', '#FFF3CD'),
        ('chk_dir', '方向键\n按下?', 200, 490, 90, 45, 'diamond', '#FFF3CD'),
        ('fwd_run', 'M0.1=1正转\nQ0.0正转输出\n互锁Q0.1', 120, 580, 140, 50, 'box', '#D4EDDA'),
        ('rev_run', 'M0.2=1反转\nQ0.1反转输出\n互锁Q0.0', 410, 580, 140, 50, 'box', '#D4EDDA'),
        ('chk_stop', '停止/急停?', 325, 680, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', 'RST M0.0-M0.2\nRST Q0.0-Q0.6\n系统停止', 325, 770, 160, 55, 'box', '#F8D7DA'),
        ('end', '结束', 325, 870, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
        ('chk_estop', 'wait', 'right', '是'), ('chk_estop', 'stop', 'left_estop', '急停'),
        ('wait', 'sys_run', 'down', '启动+确认'),
        ('sys_run', 'buzzer', 'down', ''),
        ('buzzer', 'chk_dir', 'down', ''),
        ('chk_dir', 'fwd_run', 'left', 'M0.1=1'),
        ('chk_dir', 'rev_run', 'right', 'M0.2=1'),
        ('fwd_run', 'chk_stop', 'right', ''), ('rev_run', 'chk_stop', 'left', ''),
        ('chk_stop', 'stop', 'down', '是'),
        ('chk_stop', 'fwd_run', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_concrete_mixer():
    """混凝土搅拌控制系统"""
    name = '混凝土搅拌控制系统'
    folder = os.path.join(BASE, '混凝土搅拌控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '正转输出 KM1',     '电机正转(顺时针)'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '反转输出 KM2',     '电机反转(逆时针)'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '运行指示灯 HL1',   '绿色'],
        ['M0.0', '系统运行使能',    'Q0.3', '低速 VFD-S1',      '15Hz'],
        ['M0.1', '反转运行中',     'Q0.4', '中速 VFD-S2',      '20Hz'],
        ['T37',  '正转定时6s',     'Q0.5', '高速 VFD-S3',      '30Hz'],
        ['T38',  '反转定时6s',     '',     '',                  ''],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 系统运行使能(自锁)',
            'elements': [
                ('NO', 100, 'I0.0\n启动'), ('NC', 210, 'I0.1\n停止'),
                ('NC', 300, 'I0.2\n急停'), ('COIL', 500, 'M0.0\n运行'),
            ],
            'self_hold': True, 'self_x': 155, 'branch_from': 250, 'hold_lbl': 'M0.0'
        },
        {
            'label': 'Network 2: 正转6秒定时 T37(100ms×60=6s) - M0.0=ON且不在反转→T37',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'M0.1\n反转'),
                ('TIMER', 400, 'T37\nTON\nPT=60'),
            ]
        },
        {
            'label': 'Network 3: T37到→启动反转6秒 T38(100ms×60=6s)',
            'elements': [
                ('NO', 100, 'T37\n6s到'), ('COIL_SET', 250, 'M0.1\n反转'),
                ('TIMER', 420, 'T38\nTON\nPT=60'),
            ]
        },
        {
            'label': 'Network 4: T38到→复位反转，重新正转(循环)',
            'elements': [
                ('NO', 100, 'T38\n6s到'), ('COIL_RESET', 280, 'M0.1\n反转'),
            ]
        },
        {
            'label': 'Network 5: 正转输出(运行+非反转→Q0.0)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'M0.1\n反转'),
                ('COIL', 400, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 6: 反转输出(运行+反转中→Q0.1)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NO', 210, 'M0.1\n反转'),
                ('NC', 300, 'Q0.0\n互锁'), ('COIL', 480, 'Q0.1\n反转'),
            ]
        },
        {
            'label': 'Network 7: 速度输出(正转低速→反转中速→循环递增)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'),
                ('COIL', 250, 'Q0.3\n低速'),
                ('NO', 360, 'M0.1\n反转'),
                ('COIL', 500, 'Q0.4\n中速'),
            ]
        },
        {
            'label': 'Network 8: 急停/停止→复位所有',
            'elements': [
                ('NC', 100, 'I0.1\n停止'),
                ('COIL_RESET', 300, 'M0.0\n(2点)'),
                ('NC', 430, 'I0.2\n急停'),
                ('COIL_RESET', 630, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化\n默认低速Q0.3', 325, 95, 120, 45, 'box', '#E8F0FE'),
        ('chk_estop', '急停释放?', 325, 170, 100, 45, 'diamond', '#FFF3CD'),
        ('wait', '等待启动', 325, 245, 110, 40, 'box', '#E8F0FE'),
        ('sys_run', 'M0.0=1 系统运行\n运行灯Q0.2亮', 325, 320, 135, 50, 'box', '#D4EDDA'),
        ('fwd_6s', 'M0.1=OFF\nQ0.0正转 低速\nT37计时6s', 325, 405, 140, 50, 'box', '#D4EDDA'),
        ('rev_6s', 'T37到!\nM0.1=ON 反转\nQ0.1反转 中速\nT38计时6s', 325, 490, 145, 55, 'box', '#FCE4D6'),
        ('cycle', 'T38到!\nRST M0.1\n重新正转', 325, 580, 140, 45, 'box', '#FFF3CD'),
        ('chk_stop', '停止/急停?', 325, 665, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', 'RST M0.0-M0.1\nRST Q0.0-Q0.5\n系统停止', 325, 755, 160, 55, 'box', '#F8D7DA'),
        ('end', '结束', 325, 855, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
        ('chk_estop', 'wait', 'right', '是'), ('chk_estop', 'stop', 'left_estop', '急停'),
        ('wait', 'sys_run', 'down', '启动'),
        ('sys_run', 'fwd_6s', 'down', ''),
        ('fwd_6s', 'rev_6s', 'down', 'T37到'),
        ('rev_6s', 'cycle', 'down', 'T38到'),
        ('cycle', 'fwd_6s', 'up_loop', '循环'),
        ('fwd_6s', 'chk_stop', 'right', ''), ('rev_6s', 'chk_stop', 'right', ''),
        ('chk_stop', 'stop', 'down', '是'), ('chk_stop', 'fwd_6s', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_hub_tightener():
    """简易轮毂打紧机控制系统"""
    name = '简易轮毂打紧机控制系统'
    folder = os.path.join(BASE, '简易轮毂打紧机控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '正转/打紧键 SB1','Q0.0', '正转输出 KM1',     '电机正转(打紧)'],
        ['I0.1', '反转/松开键 SB2','Q0.1', '反转输出 KM2',     '电机反转(松开)'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '运行指示灯 HL1',   '绿色'],
        ['I0.3', '正转限位 SQ1',   'Q0.3', '蜂鸣器 HA',        '预警'],
        ['I0.4', '反转限位 SQ2',   'Q0.4', '低速 VFD-S1',      '15Hz'],
        ['M0.1', '正转使能(S)',    'Q0.5', '中速 VFD-S2',      '30Hz'],
        ['M0.2', '反转使能(S)',    'Q0.6', '高速 VFD-S3',      '50Hz'],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 正转置位 - 正转键→M0.1(S), 正转限位→M0.1(R)',
            'elements': [
                ('NO', 100, 'I0.0\n正转键'),
                ('COIL_SET', 300, 'M0.1\n正转'),
                ('NO', 430, 'I0.3\n正转限位'),
                ('COIL_RESET', 630, 'M0.1\n正转'),
            ]
        },
        {
            'label': 'Network 2: 反转置位 - 反转键→M0.2(S), 反转限位→M0.2(R)',
            'elements': [
                ('NO', 100, 'I0.1\n反转键'),
                ('COIL_SET', 300, 'M0.2\n反转'),
                ('NO', 430, 'I0.4\n反转限位'),
                ('COIL_RESET', 630, 'M0.2\n反转'),
            ]
        },
        {
            'label': 'Network 3: 正转输出(含急停+互锁)',
            'elements': [
                ('NO', 100, 'M0.1\n正转'), ('NC', 210, 'I0.2\n急停'),
                ('NC', 310, 'Q0.1\n反转互锁'), ('COIL', 500, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 4: 反转输出(含急停+互锁)',
            'elements': [
                ('NO', 100, 'M0.2\n反转'), ('NC', 210, 'I0.2\n急停'),
                ('NC', 310, 'Q0.0\n正转互锁'), ('COIL', 500, 'Q0.1\n反转'),
            ]
        },
        {
            'label': 'Network 5: 蜂鸣器预警(运行中+限位到达时鸣响)',
            'elements': [
                ('NO', 100, 'M0.1\n正转'), ('NC', 210, 'I0.3\n限位'),
                ('COIL', 350, 'Q0.3\n蜂鸣器'),
                ('NO', 460, 'M0.2\n反转'), ('NC', 570, 'I0.4\n限位'),
            ]
        },
        {
            'label': 'Network 6: 默认中速+运行指示',
            'elements': [
                ('NO', 100, 'M0.1\n正转'), ('COIL', 250, 'Q0.2\n运行灯'),
                ('COIL', 370, 'Q0.5\n中速'),
                ('NO', 470, 'M0.2\n反转'),
            ]
        },
        {
            'label': 'Network 7: 急停→复位所有',
            'elements': [
                ('NO', 100, 'I0.2\n急停'),
                ('COIL_RESET', 300, 'M0.1\n(2点)'),
                ('COIL_RESET', 500, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化', 325, 95, 100, 40, 'box', '#E8F0FE'),
        ('wait', '等待按键', 325, 165, 110, 40, 'box', '#E8F0FE'),
        ('chk_fwd', '正转键\n按下?', 160, 245, 90, 45, 'diamond', '#FFF3CD'),
        ('chk_rev', '反转键\n按下?', 460, 245, 90, 45, 'diamond', '#FFF3CD'),
        ('fwd_set', 'M0.1=(S)\n正转使能', 160, 335, 120, 45, 'box', '#D4EDDA'),
        ('rev_set', 'M0.2=(S)\n反转使能', 460, 335, 120, 45, 'box', '#D4EDDA'),
        ('fwd_run', 'Q0.0正转\nQ0.2运行灯\n蜂鸣器预警', 160, 425, 130, 50, 'box', '#D4EDDA'),
        ('rev_run', 'Q0.1反转\nQ0.2运行灯\n蜂鸣器预警', 460, 425, 130, 50, 'box', '#FCE4D6'),
        ('chk_limit', '限位到达?', 325, 515, 100, 45, 'diamond', '#FFF3CD'),
        ('reset_m', '限位(R)复位\nM0.1或M0.2=OFF', 325, 600, 145, 45, 'box', '#FFF3CD'),
        ('chk_estop', '急停?', 325, 685, 100, 45, 'diamond', '#F8D7DA'),
        ('stop_all', '急停:RST全部', 325, 770, 140, 45, 'box', '#F8D7DA'),
        ('end', '结束', 325, 860, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'wait', 'down', ''),
        ('wait', 'chk_fwd', 'left', ''), ('wait', 'chk_rev', 'right', ''),
        ('chk_fwd', 'fwd_set', 'down', '是'), ('chk_fwd', 'wait', 'left_loop', '否'),
        ('chk_rev', 'rev_set', 'down', '是'), ('chk_rev', 'wait', 'right_loop', '否'),
        ('fwd_set', 'fwd_run', 'down', ''), ('rev_set', 'rev_run', 'down', ''),
        ('fwd_run', 'chk_limit', 'right', ''), ('rev_run', 'chk_limit', 'left', ''),
        ('chk_limit', 'reset_m', 'down', '是'), ('chk_limit', 'chk_estop', 'right', '否'),
        ('reset_m', 'wait', 'up_loop', ''),
        ('chk_estop', 'stop_all', 'down', '是'), ('chk_estop', 'wait', 'right_loop', '否'),
        ('stop_all', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_electric_hoist():
    """电动葫芦控制系统"""
    name = '电动葫芦控制系统'
    folder = os.path.join(BASE, '电动葫芦控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '上升按钮 SB1',   'Q0.0', '上升/正转 KM1',    '电机正转(上升)'],
        ['I0.1', '下降按钮 SB2',   'Q0.1', '下降/反转 KM2',    '电机反转(下降)'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '蜂鸣器 HA',        '预警提示'],
        ['I0.3', '上限位 SQ1',     'Q0.3', '运行指示灯 HL1',   '绿色'],
        ['I0.4', '下限位 SQ2',     'Q0.4', '低速 VFD-S1',      '15Hz'],
        ['M0.1', '上升使能(S)',    'Q0.5', '中速 VFD-S2',      '25Hz'],
        ['M0.2', '下降使能(S)',    'Q0.6', '高速 VFD-S3',      '50Hz'],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 上升置位 - 上升键→M0.1(S), 上限位→M0.1(R)',
            'elements': [
                ('NO', 100, 'I0.0\n上升键'),
                ('COIL_SET', 300, 'M0.1\n上升'),
                ('NO', 430, 'I0.3\n上限位'),
                ('COIL_RESET', 630, 'M0.1\n上升'),
            ]
        },
        {
            'label': 'Network 2: 下降置位 - 下降键→M0.2(S), 下限位→M0.2(R)',
            'elements': [
                ('NO', 100, 'I0.1\n下降键'),
                ('COIL_SET', 300, 'M0.2\n下降'),
                ('NO', 430, 'I0.4\n下限位'),
                ('COIL_RESET', 630, 'M0.2\n下降'),
            ]
        },
        {
            'label': 'Network 3: 上升输出(含急停+互锁)',
            'elements': [
                ('NO', 100, 'M0.1\n上升'), ('NC', 210, 'I0.2\n急停'),
                ('NC', 310, 'Q0.1\n互锁'), ('COIL', 500, 'Q0.0\n上升'),
            ]
        },
        {
            'label': 'Network 4: 下降输出(含急停+互锁)',
            'elements': [
                ('NO', 100, 'M0.2\n下降'), ('NC', 210, 'I0.2\n急停'),
                ('NC', 310, 'Q0.0\n互锁'), ('COIL', 500, 'Q0.1\n下降'),
            ]
        },
        {
            'label': 'Network 5: 蜂鸣器预警(运行时鸣响)',
            'elements': [
                ('NO', 100, 'M0.1\n上升'), ('COIL', 250, 'Q0.2\n蜂鸣器'),
                ('NO', 360, 'M0.2\n下降'),
            ]
        },
        {
            'label': 'Network 6: 状态指示+默认中速',
            'elements': [
                ('NO', 100, 'M0.1\n上升'), ('COIL', 250, 'Q0.3\n运行灯'),
                ('COIL', 380, 'Q0.5\n中速'),
                ('NO', 470, 'M0.2\n下降'),
            ]
        },
        {
            'label': 'Network 7: 急停→复位所有',
            'elements': [
                ('NO', 100, 'I0.2\n急停'),
                ('COIL_RESET', 300, 'M0.1\n(2点)'),
                ('COIL_RESET', 500, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('wait', '等待按键', 325, 105, 110, 40, 'box', '#E8F0FE'),
        ('chk_up', '上升键?', 150, 185, 90, 45, 'diamond', '#FFF3CD'),
        ('chk_dn', '下降键?', 470, 185, 90, 45, 'diamond', '#FFF3CD'),
        ('up_set', 'M0.1=(S)\n上升使能', 150, 275, 120, 45, 'box', '#D4EDDA'),
        ('dn_set', 'M0.2=(S)\n下降使能', 470, 275, 120, 45, 'box', '#D4EDDA'),
        ('up_run', 'Q0.0上升\nQ0.3运行灯\n蜂鸣器Q0.2', 150, 360, 130, 50, 'box', '#D4EDDA'),
        ('dn_run', 'Q0.1下降\nQ0.3运行灯\n蜂鸣器Q0.2', 470, 360, 130, 50, 'box', '#FCE4D6'),
        ('chk_limit', '限位到达?', 325, 445, 100, 45, 'diamond', '#FFF3CD'),
        ('reset', '上限位→RST M0.1\n下限位→RST M0.2', 325, 530, 150, 45, 'box', '#FFF3CD'),
        ('chk_estop', '急停?', 325, 615, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', '急停:RST全部', 325, 700, 140, 45, 'box', '#F8D7DA'),
        ('end', '结束', 325, 790, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'wait', 'down', ''),
        ('wait', 'chk_up', 'left', ''), ('wait', 'chk_dn', 'right', ''),
        ('chk_up', 'up_set', 'down', '是'), ('chk_up', 'wait', 'left_loop', '否'),
        ('chk_dn', 'dn_set', 'down', '是'), ('chk_dn', 'wait', 'right_loop', '否'),
        ('up_set', 'up_run', 'down', ''), ('dn_set', 'dn_run', 'down', ''),
        ('up_run', 'chk_limit', 'right', ''), ('dn_run', 'chk_limit', 'left', ''),
        ('chk_limit', 'reset', 'down', '是'), ('chk_limit', 'chk_estop', 'right', '否'),
        ('reset', 'wait', 'up_loop', ''),
        ('chk_estop', 'stop', 'down', '是'), ('chk_estop', 'wait', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_filling_machine():
    """简易加注机控制系统"""
    name = '简易加注机控制系统'
    folder = os.path.join(BASE, '简易加注机控制系统')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '加注泵 KM1',       '正转输出'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '回吸阀 KM2',       '反转输出'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '蜂鸣器 HA',        '预警'],
        ['I0.3', '液位下限 SL1',   'Q0.3', '运行指示灯 HL1',   '绿色'],
        ['I0.4', '液位上限 SL2',   'Q0.4', '补液泵 KM3',       ''],
        ['M0.0', '系统运行使能',    'Q0.5', '低速 VFD-S1',      '20Hz'],
        ['M0.1', '加注中',         'Q0.6', '中速 VFD-S2',      '35Hz'],
        ['M0.2', '回吸中',         '',     '',                  ''],
        ['T37',  '加注定时',       '',     '',                  ''],
        ['T38',  '回吸定时',       '',     '',                  ''],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 系统运行使能(自锁)',
            'elements': [
                ('NO', 100, 'I0.0\n启动'), ('NC', 210, 'I0.1\n停止'),
                ('NC', 300, 'I0.2\n急停'), ('COIL', 500, 'M0.0\n运行'),
            ],
            'self_hold': True, 'self_x': 155, 'branch_from': 250, 'hold_lbl': 'M0.0'
        },
        {
            'label': 'Network 2: 加注控制 - M0.0运行后置位M0.1, T37定时脉冲重置',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'M0.2\n回吸中'),
                ('COIL_SET', 360, 'M0.1\n加注'),
                ('TIMER', 500, 'T37\nTON\nPT=50'),
            ]
        },
        {
            'label': 'Network 3: T37到→结束加注, 置位回吸',
            'elements': [
                ('NO', 100, 'T37\n5s到'), ('COIL_RESET', 260, 'M0.1\n加注'),
                ('COIL_SET', 400, 'M0.2\n回吸'),
                ('TIMER', 540, 'T38\nTON\nPT=20'),
            ]
        },
        {
            'label': 'Network 4: T38到→结束回吸, 循环',
            'elements': [
                ('NO', 100, 'T38\n2s到'), ('COIL_RESET', 300, 'M0.2\n回吸'),
            ]
        },
        {
            'label': 'Network 5: 加注泵输出(M0.1=ON→Q0.0)',
            'elements': [
                ('NO', 100, 'M0.1\n加注'), ('NC', 210, 'I0.2\n急停'),
                ('COIL', 400, 'Q0.0\n加注泵'),
            ]
        },
        {
            'label': 'Network 6: 回吸输出(M0.2=ON→Q0.1)',
            'elements': [
                ('NO', 100, 'M0.2\n回吸'), ('COIL', 300, 'Q0.1\n回吸阀'),
            ]
        },
        {
            'label': 'Network 7: 液位控制+蜂鸣器',
            'elements': [
                ('NC', 100, 'I0.3\n液位低'), ('COIL', 250, 'Q0.4\n补液泵'),
                ('COIL', 370, 'Q0.2\n蜂鸣器'),
            ]
        },
        {
            'label': 'Network 8: 急停/停止→复位所有',
            'elements': [
                ('NC', 100, 'I0.1\n停止'),
                ('COIL_RESET', 300, 'M0.0\n(6点)'),
                ('NC', 450, 'I0.2\n急停'),
                ('COIL_RESET', 650, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化', 325, 95, 100, 40, 'box', '#E8F0FE'),
        ('chk_estop', '急停释放?', 325, 165, 100, 45, 'diamond', '#FFF3CD'),
        ('wait', '等待启动', 325, 235, 110, 40, 'box', '#E8F0FE'),
        ('sys_run', 'M0.0=1 系统运行\nQ0.3运行灯亮', 325, 310, 135, 50, 'box', '#D4EDDA'),
        ('fill', 'M0.1=(S) 加注中\nQ0.0加注泵\nT37计时5s', 325, 395, 145, 50, 'box', '#D4EDDA'),
        ('suck_back', 'T37到\nRST M0.1\nM0.2=(S) 回吸\nQ0.1回吸阀 T38计时2s', 325, 480, 155, 55, 'box', '#FCE4D6'),
        ('cycle', 'T38到\nRST M0.2\n重新加注', 325, 570, 140, 45, 'box', '#FFF3CD'),
        ('chk_level', '液位低?', 325, 655, 100, 45, 'diamond', '#FFF3CD'),
        ('refill', 'Q0.4补液泵\nQ0.2蜂鸣器', 325, 735, 130, 45, 'box', '#F8D7DA'),
        ('chk_stop', '停止/急停?', 325, 820, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', 'RST全部', 325, 900, 120, 40, 'box', '#F8D7DA'),
        ('end', '结束', 325, 975, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
        ('chk_estop', 'wait', 'right', '是'), ('chk_estop', 'stop', 'left_estop', '急停'),
        ('wait', 'sys_run', 'down', '启动'),
        ('sys_run', 'fill', 'down', ''),
        ('fill', 'suck_back', 'down', 'T37到'),
        ('suck_back', 'cycle', 'down', 'T38到'),
        ('cycle', 'fill', 'up_loop', '循环'),
        ('fill', 'chk_level', 'right', ''), ('suck_back', 'chk_level', 'right', ''),
        ('chk_level', 'refill', 'down', '是'), ('chk_level', 'chk_stop', 'right', '否'),
        ('refill', 'chk_stop', 'down', ''),
        ('chk_stop', 'stop', 'down', '是'), ('chk_stop', 'fill', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_tower_crane():
    """塔吊旋转控制系统 (西门子格式, 已有梯形图和流程图, 补充原理图)"""
    name = '塔吊旋转控制系统'
    folder = os.path.join(BASE, '塔吊旋转控制系统')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '左转 CCW KM1',     '逆时针旋转'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '右转 CW KM2',      '顺时针旋转'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '蜂鸣器 HA',        '预警3秒'],
        ['I0.3', '左转按钮 SB4',   'Q0.3', '运行指示灯 HL1',   '绿色'],
        ['I0.4', '右转按钮 SB5',   'Q0.4', '左转指示灯 HL2',   '黄色'],
        ['I0.5', '加速按钮 SB6',   'Q0.5', '右转指示灯 HL3',   '蓝色'],
        ['I0.6', '减速按钮 SB7',   'Q0.6', '低速 VFD-S1',      '15Hz'],
        ['M0.0', '系统运行使能',    'Q0.7', '中速 VFD-S2',      '25Hz'],
        ['M0.1', '左转请求',       'Q1.0', '高速 VFD-S3',      '50Hz'],
        ['M0.2', '右转请求',       '',     '',                  ''],
    ]

    # For tower crane, just generate circuit diagram since ladder+flowchart already exist
    return name, folder, io_table, None, None, None


def sys_amusement_pirate():
    """海盗船控制系统 (新设计)"""
    name = '海盗船控制系统'
    folder = os.path.join(BASE, '海盗船控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '正转/前进 KM1',    '电机正转'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '反转/后退 KM2',    '电机反转'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '蜂鸣器 HA',        '3秒预警'],
        ['M0.0', '系统运行使能',    'Q0.3', '运行指示灯 HL1',   '绿色'],
        ['M0.1', '正摆请求',       'Q0.4', '低速 VFD-S1',      '15Hz'],
        ['M0.2', '反摆请求',       'Q0.5', '中速 VFD-S2',      '30Hz'],
        ['T37',  '正摆定时3s',     'Q0.6', '高速 VFD-S3',      '50Hz'],
        ['T38',  '反摆定时3s',     '',     '',                  ''],
        ['T39',  '预警定时3s',     '',     '',                  ''],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 系统运行使能(自锁) - 启动+急停/停止=OFF',
            'elements': [
                ('NO', 100, 'I0.0\n启动'), ('NC', 210, 'I0.1\n停止'),
                ('NC', 300, 'I0.2\n急停'), ('COIL', 500, 'M0.0\n运行'),
            ],
            'self_hold': True, 'self_x': 155, 'branch_from': 250, 'hold_lbl': 'M0.0'
        },
        {
            'label': 'Network 2: 蜂鸣器3秒预警 T39(100ms×30=3s)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'),
                ('TIMER', 280, 'T39\nTON\nPT=30'),
            ]
        },
        {
            'label': 'Network 3: T39到→置位正摆(首次摆动方向)',
            'elements': [
                ('NO', 100, 'T39\n3s到'), ('NO', 210, 'M0.0\n运行'),
                ('COIL_SET', 400, 'M0.1\n正摆'),
            ]
        },
        {
            'label': 'Network 4: 正摆3秒 T37(100ms×30=3s)',
            'elements': [
                ('NO', 100, 'M0.1\n正摆'),
                ('TIMER', 280, 'T37\nTON\nPT=30'),
            ]
        },
        {
            'label': 'Network 5: T37到→切换到反摆(RST M0.1, SET M0.2)',
            'elements': [
                ('NO', 100, 'T37\n3s到'), ('COIL_RESET', 280, 'M0.1\n正摆'),
                ('COIL_SET', 450, 'M0.2\n反摆'),
            ]
        },
        {
            'label': 'Network 6: 反摆3秒 T38(100ms×30=3s)',
            'elements': [
                ('NO', 100, 'M0.2\n反摆'),
                ('TIMER', 280, 'T38\nTON\nPT=30'),
            ]
        },
        {
            'label': 'Network 7: T38到→切换到正摆(RST M0.2, SET M0.1) 循环',
            'elements': [
                ('NO', 100, 'T38\n3s到'), ('COIL_RESET', 280, 'M0.2\n反摆'),
                ('COIL_SET', 450, 'M0.1\n正摆'),
            ]
        },
        {
            'label': 'Network 8: 正转输出(M0.1+互锁→Q0.0)',
            'elements': [
                ('NO', 100, 'M0.1\n正摆'), ('NC', 210, 'Q0.1\n互锁'),
                ('COIL', 400, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 9: 反转输出(M0.2+互锁→Q0.1)',
            'elements': [
                ('NO', 100, 'M0.2\n反摆'), ('NC', 210, 'Q0.0\n互锁'),
                ('COIL', 400, 'Q0.1\n反转'),
            ]
        },
        {
            'label': 'Network 10: 蜂鸣器输出(预警期间T39未到时鸣响)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'T39\n3s到'),
                ('COIL', 400, 'Q0.2\n蜂鸣器'),
            ]
        },
        {
            'label': 'Network 11: 运行指示+默认中速',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('COIL', 280, 'Q0.3\n运行灯'),
                ('COIL', 430, 'Q0.5\n中速'),
            ]
        },
        {
            'label': 'Network 12: 急停/停止→复位所有',
            'elements': [
                ('NC', 100, 'I0.1\n停止'),
                ('COIL_RESET', 300, 'M0.0\n(3点)'),
                ('NC', 450, 'I0.2\n急停'),
                ('COIL_RESET', 650, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化\n默认中速', 325, 95, 120, 40, 'box', '#E8F0FE'),
        ('chk_estop', '急停释放?', 325, 165, 100, 45, 'diamond', '#FFF3CD'),
        ('wait', '等待启动', 325, 235, 110, 40, 'box', '#E8F0FE'),
        ('sys_run', 'M0.0=1 系统运行\nQ0.3运行灯亮', 325, 310, 135, 45, 'box', '#D4EDDA'),
        ('buzzer', '蜂鸣器Q0.2响\nT39计时3s', 325, 390, 130, 45, 'box', '#FFF3CD'),
        ('fwd3s', 'M0.1=ON 正摆\nQ0.0正转 中速\nT37计时3s', 325, 470, 145, 50, 'box', '#D4EDDA'),
        ('rev3s', 'T37到!\nRST M0.1/SET M0.2\nQ0.1反转\nT38计时3s', 325, 555, 150, 55, 'box', '#FCE4D6'),
        ('cycle', 'T38到!\nRST M0.2/SET M0.1\n循环摆动', 325, 645, 150, 45, 'box', '#FFF3CD'),
        ('chk_stop', '停止/急停?', 325, 730, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', 'RST全部', 325, 815, 120, 40, 'box', '#F8D7DA'),
        ('end', '结束', 325, 900, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
        ('chk_estop', 'wait', 'right', '是'), ('chk_estop', 'stop', 'left_estop', '急停'),
        ('wait', 'sys_run', 'down', '启动'),
        ('sys_run', 'buzzer', 'down', ''),
        ('buzzer', 'fwd3s', 'down', 'T39到'),
        ('fwd3s', 'rev3s', 'down', 'T37到'),
        ('rev3s', 'cycle', 'down', 'T38到'),
        ('cycle', 'fwd3s', 'up_loop', '循环'),
        ('fwd3s', 'chk_stop', 'right', ''), ('rev3s', 'chk_stop', 'right', ''),
        ('chk_stop', 'stop', 'down', '是'), ('chk_stop', 'fwd3s', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_tire_conveyor():
    """简易轮胎输送线控制系统 (新设计)"""
    name = '简易轮胎输送线控制系统'
    folder = os.path.join(BASE, '简易轮胎输送线控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '电机正转 KM1',     '传送带前进'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '蜂鸣器 HA',        '3秒预警'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '运行指示灯 HL1',   '绿色'],
        ['I0.3', '检测传感器 SQ1',  'Q0.3', '低速 VFD-S1',      '20Hz'],
        ['M0.0', '系统运行使能',    'Q0.4', '中速 VFD-S2',      '35Hz'],
        ['M0.5', '轮胎到位标志',    'Q0.5', '高速 VFD-S3',      '50Hz'],
        ['T37',  '预警定时器',      '',     '',                  ''],
        ['T38',  '到位延时',       '',     '',                  ''],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 系统运行使能(自锁)',
            'elements': [
                ('NO', 100, 'I0.0\n启动'), ('NC', 210, 'I0.1\n停止'),
                ('NC', 300, 'I0.2\n急停'), ('COIL', 500, 'M0.0\n运行'),
            ],
            'self_hold': True, 'self_x': 155, 'branch_from': 250, 'hold_lbl': 'M0.0'
        },
        {
            'label': 'Network 2: 蜂鸣器3秒预警 T37(100ms×30=3s)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'),
                ('TIMER', 280, 'T37\nTON\nPT=30'),
            ]
        },
        {
            'label': 'Network 3: T37到→电机启动, 传感器检测轮胎到位',
            'elements': [
                ('NO', 100, 'T37\n3s到'), ('COIL', 300, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 4: 传感器检测→轮胎到位标志置位 T38延时',
            'elements': [
                ('NO', 100, 'I0.3\n传感器'), ('NO', 210, 'Q0.0\n运行中'),
                ('COIL_SET', 380, 'M0.5\n到位'),
                ('TIMER', 540, 'T38\nTON\nPT=20'),
            ]
        },
        {
            'label': 'Network 5: T38延时到→停止电机, 等待下一轮胎',
            'elements': [
                ('NO', 100, 'T38\n2s到'), ('COIL_RESET', 300, 'M0.5\n到位'),
                ('COIL_RESET', 460, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 6: 蜂鸣器预警输出',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'T37\n3s到'),
                ('COIL', 400, 'Q0.1\n蜂鸣器'),
            ]
        },
        {
            'label': 'Network 7: 默认中速+运行指示',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('COIL', 280, 'Q0.2\n运行灯'),
                ('COIL', 430, 'Q0.4\n中速'),
            ]
        },
        {
            'label': 'Network 8: 急停/停止→复位所有',
            'elements': [
                ('NC', 100, 'I0.1\n停止'),
                ('COIL_RESET', 300, 'M0.0\n(2点)'),
                ('NC', 450, 'I0.2\n急停'),
                ('COIL_RESET', 650, 'Q0.0\n(5点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化\n默认中速', 325, 95, 120, 40, 'box', '#E8F0FE'),
        ('chk_estop', '急停释放?', 325, 165, 100, 45, 'diamond', '#FFF3CD'),
        ('wait', '等待启动', 325, 235, 110, 40, 'box', '#E8F0FE'),
        ('sys_run', 'M0.0=1 系统运行\nQ0.2运行灯亮', 325, 310, 135, 45, 'box', '#D4EDDA'),
        ('buzzer', '蜂鸣器Q0.1响\nT37计时3s', 325, 390, 130, 45, 'box', '#FFF3CD'),
        ('motor_on', 'T37到!\nQ0.0电机正转\n传送带前进', 325, 470, 135, 45, 'box', '#D4EDDA'),
        ('chk_sensor', '传感器检测\n到轮胎?', 325, 550, 100, 45, 'diamond', '#FFF3CD'),
        ('tire_ok', 'M0.5=ON 到位\nT38延时2s\n(轮胎移出)', 325, 635, 145, 50, 'box', '#D4EDDA'),
        ('motor_off', 'T38到!\nRST M0.5\nRST Q0.0 停机\n等待下一个', 325, 720, 150, 50, 'box', '#FCE4D6'),
        ('chk_stop', '停止/急停?', 325, 805, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', 'RST全部', 325, 885, 120, 40, 'box', '#F8D7DA'),
        ('end', '结束', 325, 960, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
        ('chk_estop', 'wait', 'right', '是'), ('chk_estop', 'stop', 'left_estop', '急停'),
        ('wait', 'sys_run', 'down', '启动'),
        ('sys_run', 'buzzer', 'down', ''),
        ('buzzer', 'motor_on', 'down', 'T37到'),
        ('motor_on', 'chk_sensor', 'down', ''),
        ('chk_sensor', 'tire_ok', 'down', '是'), ('chk_sensor', 'motor_on', 'right_loop', '否'),
        ('tire_ok', 'motor_off', 'down', 'T38到'),
        ('motor_off', 'motor_on', 'up_loop', '循环'),
        ('motor_on', 'chk_stop', 'right', ''), ('tire_ok', 'chk_stop', 'right', ''),
        ('chk_stop', 'stop', 'down', '是'), ('chk_stop', 'motor_on', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


def sys_spinning_cups():
    """转转杯控制系统 (新设计)"""
    name = '转转杯控制系统'
    folder = os.path.join(BASE, '转转杯控制系统设计')
    os.makedirs(folder, exist_ok=True)

    io_table = [
        ['I0.0', '启动按钮 SB1',   'Q0.0', '电机正转 KM1',     '旋转杯台'],
        ['I0.1', '停止按钮 SB2',   'Q0.1', '蜂鸣器 HA',        '3秒预警'],
        ['I0.2', '急停按钮 SB3',   'Q0.2', '运行指示灯 HL1',   '绿色'],
        ['I0.3', '加速按钮 SB4',   'Q0.3', '低速 VFD-S1',      '10Hz'],
        ['I0.4', '减速按钮 SB5',   'Q0.4', '中速 VFD-S2',      '25Hz'],
        ['M0.0', '系统运行使能',    'Q0.5', '高速 VFD-S3',      '40Hz'],
        ['MW0',  '速度等级 1-3',   '',     '',                  ''],
        ['T37',  '预警定时器',      '',     '',                  ''],
        ['SM0.0', '常ON触点',      '',     '',                  ''],
    ]

    rungs = [
        {
            'label': 'Network 1: 系统运行使能(自锁)',
            'elements': [
                ('NO', 100, 'I0.0\n启动'), ('NC', 210, 'I0.1\n停止'),
                ('NC', 300, 'I0.2\n急停'), ('COIL', 500, 'M0.0\n运行'),
            ],
            'self_hold': True, 'self_x': 155, 'branch_from': 250, 'hold_lbl': 'M0.0'
        },
        {
            'label': 'Network 2: 蜂鸣器3秒预警 T37(100ms×30=3s)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'),
                ('TIMER', 280, 'T37\nTON\nPT=30'),
            ]
        },
        {
            'label': 'Network 3: T37到→电机启动旋转',
            'elements': [
                ('NO', 100, 'T37\n3s到'), ('COIL', 300, 'Q0.0\n正转'),
            ]
        },
        {
            'label': 'Network 4: 蜂鸣器预警输出(T37未到时)',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('NC', 210, 'T37\n3s到'),
                ('COIL', 400, 'Q0.1\n蜂鸣器'),
            ]
        },
        {
            'label': 'Network 5: 速度等级调节(MW0 1-3)',
            'elements': [
                ('NO', 100, 'I0.3\n加速'),
                ('FUNC', 230, 'INC_W\nMW0'),
                ('NO', 350, 'I0.4\n减速'),
                ('FUNC', 480, 'DEC_W\nMW0'),
                ('FUNC', 600, 'LIMIT\nMW0 1-3'),
            ]
        },
        {
            'label': 'Network 6: 初始化速度(MW0=1) + 速度输出',
            'elements': [
                ('FUNC', 100, '==I\nMW0\n1'), ('COIL', 250, 'Q0.3\n低速'),
                ('FUNC', 370, '==I\nMW0\n2'), ('COIL', 520, 'Q0.4\n中速'),
                ('FUNC', 640, '==I\nMW0\n3'), ('COIL', 790, 'Q0.5\n高速'),
            ]
        },
        {
            'label': 'Network 7: 运行指示',
            'elements': [
                ('NO', 100, 'M0.0\n运行'), ('COIL', 300, 'Q0.2\n运行灯'),
            ]
        },
        {
            'label': 'Network 8: 急停/停止→复位所有',
            'elements': [
                ('NC', 100, 'I0.1\n停止'),
                ('COIL_RESET', 300, 'M0.0\n(1点)'),
                ('NC', 450, 'I0.2\n急停'),
                ('COIL_RESET', 650, 'Q0.0\n(6点)'),
            ]
        },
    ]

    flow_nodes = [
        ('start', '开始\n(系统上电)', 325, 30, 130, 40, 'startend', '#1A56DB'),
        ('init', '初始化\nMW0=1(低速)', 325, 95, 120, 40, 'box', '#E8F0FE'),
        ('chk_estop', '急停释放?', 325, 165, 100, 45, 'diamond', '#FFF3CD'),
        ('wait', '等待启动', 325, 235, 110, 40, 'box', '#E8F0FE'),
        ('sys_run', 'M0.0=1 系统运行\nQ0.2运行灯亮', 325, 310, 135, 45, 'box', '#D4EDDA'),
        ('buzzer', '蜂鸣器Q0.1响\nT37计时3s', 325, 390, 130, 45, 'box', '#FFF3CD'),
        ('motor_on', 'T37到!\nQ0.0电机正转\n杯台旋转', 325, 470, 135, 45, 'box', '#D4EDDA'),
        ('chk_speed', '加速/减速\n按下?', 325, 550, 100, 45, 'diamond', '#FFF3CD'),
        ('adj_speed', 'INC_W/DEC_W\nLIMIT MW0 1-3\nQ0.3-Q0.5对应', 325, 635, 155, 45, 'box', '#FCE4D6'),
        ('chk_stop', '停止/急停?', 325, 720, 100, 45, 'diamond', '#F8D7DA'),
        ('stop', 'RST全部', 325, 805, 120, 40, 'box', '#F8D7DA'),
        ('end', '结束', 325, 885, 90, 35, 'startend', '#6C757D'),
    ]

    connections = [
        ('start', 'init', 'down', ''), ('init', 'chk_estop', 'down', ''),
        ('chk_estop', 'wait', 'right', '是'), ('chk_estop', 'stop', 'left_estop', '急停'),
        ('wait', 'sys_run', 'down', '启动'),
        ('sys_run', 'buzzer', 'down', ''),
        ('buzzer', 'motor_on', 'down', 'T37到'),
        ('motor_on', 'chk_speed', 'down', ''),
        ('chk_speed', 'adj_speed', 'down', '是'), ('chk_speed', 'chk_stop', 'right', '否'),
        ('adj_speed', 'motor_on', 'up_loop', ''),
        ('chk_stop', 'stop', 'down', '是'), ('chk_stop', 'motor_on', 'right_loop', '否'),
        ('stop', 'end', 'down', ''),
    ]

    return name, folder, io_table, rungs, flow_nodes, connections


# ============================================================
# Main
# ============================================================

ALL_SYSTEMS = [
    sys_package_conveyor,
    sys_concrete_mixer,
    sys_hub_tightener,
    sys_electric_hoist,
    sys_filling_machine,
    sys_amusement_pirate,
    sys_tire_conveyor,
    sys_spinning_cups,
]


def process_system(sys_func):
    name, folder, io_table, rungs, flow_nodes, connections = sys_func()
    print(f'\n{"="*60}')
    print(f'>>> {name}')
    print(f'    Folder: {folder}')
    svg_files = []

    # 1. Ladder diagram
    if rungs is not None:
        lad_svg = make_ladder_svg(name, rungs, io_table)
        lad_path = os.path.join(folder, f'{name}梯形图.svg')
        with open(lad_path, 'w', encoding='utf-8') as f:
            f.write(lad_svg)
        print(f'[OK] 梯形图SVG: {len(lad_svg)} bytes')
        svg_files.append(lad_path)
        # Validate
        try:
            ET.fromstring(lad_svg)
            print('[OK] 梯形图 XML通过')
        except ET.ParseError as e:
            print(f'[FAIL] 梯形图 XML: {e}')

    # 2. Flowchart
    if flow_nodes is not None:
        flo_svg = make_flow_svg(name, flow_nodes, connections)
        flo_path = os.path.join(folder, f'{name}软件流程图.svg')
        with open(flo_path, 'w', encoding='utf-8') as f:
            f.write(flo_svg)
        print(f'[OK] 流程图SVG: {len(flo_svg)} bytes')
        svg_files.append(flo_path)
        try:
            ET.fromstring(flo_svg)
            print('[OK] 流程图 XML通过')
        except ET.ParseError as e:
            print(f'[FAIL] 流程图 XML: {e}')

    # 3. Circuit diagram (SVG)
    circ_svg = make_circuit_svg(name, io_table)
    circ_path = os.path.join(folder, f'{name}电路原理图.svg')
    with open(circ_path, 'w', encoding='utf-8') as f:
        f.write(circ_svg)
    print(f'[OK] 原理图SVG: {len(circ_svg)} bytes')
    svg_files.append(circ_path)
    try:
        ET.fromstring(circ_svg)
        print('[OK] 原理图 XML通过')
    except ET.ParseError as e:
        print(f'[FAIL] 原理图 XML: {e}')

    # 3.5 HMI (人机界面)
    hmi_svg = make_hmi_svg(name, io_table)
    hmi_path = os.path.join(folder, f'{name}人机界面.svg')
    with open(hmi_path, 'w', encoding='utf-8') as f:
        f.write(hmi_svg)
    print(f'[OK] 人机界面SVG: {len(hmi_svg)} bytes')
    svg_files.append(hmi_path)
    try:
        ET.fromstring(hmi_svg)
        print('[OK] 人机界面 XML通过')
    except ET.ParseError as e:
        print(f'[FAIL] 人机界面 XML: {e}')

    # 4. Circuit diagram (DXF)
    try:
        make_circuit_dxf(name, io_table, folder)
    except Exception as e:
        print(f'[FAIL] 原理图DXF: {e}')

    return svg_files, folder


if __name__ == '__main__':
    all_pngs = []
    for sys_func in ALL_SYSTEMS:
        svg_files, folder = process_system(sys_func)
        all_pngs.append((svg_files, folder))

    # Batch convert to PNG
    print(f'\n{"="*60}')
    print('>>> SVG → PNG 转换 (Edge headless)')
    for svg_files, folder in all_pngs:
        if svg_files:
            svg2png_edge(svg_files, folder)

    # Also process tower crane (already has ladder/flowchart PNGs in CAD1, just need circuit)
    print(f'\n{"="*60}')
    print('>>> 塔吊旋转控制系统 (原理图)')
    tc_name, tc_folder, tc_io, _, _, _ = sys_tower_crane()
    circ_svg = make_circuit_svg(tc_name, tc_io)
    circ_path = os.path.join(tc_folder, f'{tc_name}电路原理图.svg')
    with open(circ_path, 'w', encoding='utf-8') as f:
        f.write(circ_svg)
    print(f'[OK] 原理图SVG: {len(circ_svg)} bytes')

    hmi_svg = make_hmi_svg(tc_name, tc_io)
    hmi_path = os.path.join(tc_folder, f'{tc_name}人机界面.svg')
    with open(hmi_path, 'w', encoding='utf-8') as f:
        f.write(hmi_svg)
    print(f'[OK] 人机界面SVG: {len(hmi_svg)} bytes')

    svg2png_edge([circ_path, hmi_path], tc_folder)
    # DXF
    try:
        make_circuit_dxf(tc_name, tc_io, tc_folder)
    except Exception as e:
        print(f'[FAIL] 原理图DXF: {e}')

    print(f'\n{"="*60}')
    print('>>> 全部完成!')
