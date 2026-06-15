#!/usr/bin/env python3
"""
扬说财经 · VIX 恐慌指数预抓取 + 趋势图生成

从 Yahoo Finance 获取 VIX 指数数据：
  1. 生成 data/vix-data.js 供首页仪表盘静态渲染（当前值+恐惧贪婪级别）
  2. 生成 docs/charts/vix_trend.svg 趋势图（近1周+近1月走势）

使用 yfinance 库（自动处理 cookie/crumb 认证）。

用法：
  python scripts/fetch-vix-data.py              # 抓取并写入所有文件
  python scripts/fetch-vix-data.py --no-chart   # 只抓取数据，不生成图表
  python scripts/fetch-vix-data.py --print      # 只打印不写入
"""

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = time.strftime('%Y-%m-%d')

OUTPUT_FILE = os.path.join(ROOT, 'data', 'vix-data.js')
CHART_DIR = os.path.join(ROOT, 'docs', 'charts')
CHART_FILE = os.path.join(CHART_DIR, 'vix_trend.svg')
VIX_CHART_1W = os.path.join(CHART_DIR, 'vix_trend_1w.svg')
VIX_CHART_1M = os.path.join(CHART_DIR, 'vix_trend_1m.svg')

# ===== 确保目录存在 =====
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'docs', 'charts'), exist_ok=True)

# ===== 备用数据：当所有 API 均失败时使用 =====
# 数据来源：WebSearch 交叉验证 (Yahoo Finance / Schwab / TexMetals)
FALLBACK_DATA = {
    'current': 16.79,
    'prev': 17.68,
    'change': -0.89,
    'changePct': -5.03,
    'level': '冷静',
    'cls': 'greed',
    'pct': 16.0,
    'date': '2026-06-15',
    'updateTime': '2026-06-15 20:00',
    'source': '备用数据 (CBOE/Yahoo, VIX=16.79)',
    'note': '6/15周一VIX从17.68跌至16.79(-5.03%)创逾一周新低，美伊和平协议落地后市场恐慌情绪持续释放，科技涨停潮推动risk-on行情'
}

# ===== 备用历史数据（用于生成趋势图） =====
# 基于已知的 VIX 近期走势：从5月初~12到6月初~17.82
FALLBACK_HISTORY = {
    'dates': [
        '2026-05-13', '2026-05-14', '2026-05-15', '2026-05-18',
        '2026-05-19', '2026-05-20', '2026-05-21', '2026-05-22',
        '2026-05-25', '2026-05-26', '2026-05-27', '2026-05-28',
        '2026-05-29', '2026-06-01', '2026-06-02', '2026-06-03',
        '2026-06-04', '2026-06-05', '2026-06-08', '2026-06-09',
        '2026-06-10', '2026-06-11',
    ],
    'closes': [
        12.35, 12.18, 11.95, 12.42,
        13.01, 13.57, 13.89, 14.22,
        14.05, 13.88, 14.56, 15.10,
        15.72, 16.39, 16.44, 17.82,
        15.25, 21.51, 18.95, 19.87,
        22.22, 19.44,
    ]
}


def get_vix_level(vix: float) -> dict:
    """根据 VIX 数值返回恐慌级别和进度条位置
    标准：VIX<15=平静, 15-20=焦虑, 20+=恐慌"""
    if vix > 20:
        pct = max(0, 25 - ((vix - 20) / 30) * 25)
        return {'level': '恐慌', 'cls': 'fear', 'pct': round(pct, 1)}
    if vix > 15:
        pct = 50 - ((vix - 15) / 5) * 25
        return {'level': '焦虑', 'cls': 'neutral', 'pct': round(pct, 1)}
    return {'level': '平静', 'cls': 'greed', 'pct': max(50, 100 - (vix / 15) * 50)}


# ===== VIX 趋势图生成（matplotlib） =====

def _ensure_matplotlib():
    """Import matplotlib and set up Chinese fonts. Returns (plt, np, mdates) or None."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import matplotlib.font_manager as fm
        import numpy as np
    except ImportError:
        print('  [VIX 图表] matplotlib 不可用，跳过', file=sys.stderr)
        return None

    chinese_fonts = [
        'Noto Sans SC', 'Noto Sans CJK SC', 'Source Han Sans SC',
        'PingFang SC', 'Microsoft YaHei', 'SimHei',
        'WenQuanYi Micro Hei', 'Droid Sans Fallback'
    ]
    font_set = False
    available = {f.name for f in fm.fontManager.ttflist}
    for font in chinese_fonts:
        if font in available:
            plt.rcParams['font.family'] = font
            plt.rcParams['axes.unicode_minus'] = False
            font_set = True
            break
    if not font_set:
        for f in fm.fontManager.ttflist:
            if 'CJK' in f.name or 'SC' in f.name or 'Hei' in f.name or 'YaHei' in f.name:
                plt.rcParams['font.family'] = f.name
                plt.rcParams['axes.unicode_minus'] = False
                break
    return plt, np, mdates


def _prepare_vix_data(hist_data):
    """Unified data preparation: returns (df, dates, values, source_note) or raises ValueError."""
    import numpy as np
    if isinstance(hist_data, dict) and 'dates' in hist_data:
        from datetime import datetime
        import pandas as pd
        dates_raw = [datetime.strptime(d, '%Y-%m-%d') for d in hist_data['dates']]
        values_raw = hist_data['closes']
        pairs = sorted(zip(dates_raw, values_raw))
        dates = [p[0] for p in pairs]
        values = np.array([p[1] for p in pairs])
        df = pd.Series(values, index=pd.DatetimeIndex(dates))
        source_note = '备用数据 (近1月走势参考)'
    else:
        import pandas as pd
        df = hist_data['Close'].dropna().copy()
        if len(df) < 2:
            raise ValueError('数据点不足')
        dates = df.index
        values = df.values
        source_note = '数据来源: Yahoo Finance | 扬说财经'
    return df, dates, values, source_note


def _draw_vix_axes(ax, plot_data, dates, title, colors, mdates):
    """Draw a single VIX trend subplot."""
    d, v = plot_data
    latest_val = v[-1]
    max_v = max(v) * 1.25

    # fear/greed zone backgrounds (keep same subtle alpha)
    ax.axhspan(0, 15, xmin=0, xmax=1, facecolor=colors['GREEN'], alpha=0.06, zorder=0)
    ax.axhspan(15, 20, xmin=0, xmax=1, facecolor=colors['GOLD'], alpha=0.06, zorder=0)
    ax.axhspan(20, max_v * 1.1, xmin=0, xmax=1, facecolor=colors['RED'], alpha=0.06, zorder=0)
    ax.axhline(y=15, color=colors['GREEN'], linewidth=0.8, linestyle='--', alpha=0.4)
    ax.axhline(y=20, color=colors['RED'], linewidth=0.8, linestyle='--', alpha=0.4)

    # zone labels on the left side of chart (axes coordinate, inside plot area)
    zone_style = dict(fontsize=13, fontweight='bold', va='center',
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                edgecolor='none', alpha=0.85))
    ax.text(0.01, 0.25, '  平静', color=colors['GREEN'], transform=ax.transAxes, **zone_style)
    ax.text(0.01, 0.55, '  焦虑', color=colors['GOLD'], transform=ax.transAxes, **zone_style)
    ax.text(0.01, 0.82, '  恐慌', color=colors['RED'], transform=ax.transAxes, **zone_style)

    ax.set_facecolor(colors['WHITE'])
    ax.fill_between(d.index, v, alpha=0.10, color=colors['BLUE'])
    ms = 5 if len(v) <= 10 else 4
    ax.plot(d.index, v, color=colors['BLUE'], linewidth=2.0, marker='o',
            markersize=ms, markeredgecolor=colors['WHITE'],
            markeredgewidth=1.5, zorder=3)
    ax.annotate(f'{latest_val:.2f}',
                xy=(d.index[-1], latest_val),
                xytext=(5, 12), textcoords='offset points',
                fontsize=11, fontweight='bold', color=colors['BLUE'],
                bbox=dict(boxstyle='round,pad=0.2', facecolor=colors['WHITE'],
                          edgecolor=colors['BLUE'], linewidth=0.8))

    ax.set_title(title, fontsize=12, fontweight='bold',
                  color=colors['DARK'], pad=8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color(colors['LINE'])
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_color(colors['LINE'])
    ax.spines['bottom'].set_linewidth(0.5)
    ax.tick_params(colors=colors['GRAY'], labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    import matplotlib.ticker as ticker
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
    ax.grid(axis='y', alpha=0.12, color=colors['GRAY'], linewidth=0.5)
    ax.set_axisbelow(True)
    return ax


def generate_vix_charts(hist_data):
    """生成两个独立的 VIX 趋势 SVG：近1周 + 近1月"""
    result = _ensure_matplotlib()
    if result is None:
        return
    plt, np, mdates = result

    try:
        df, dates_all, values_all, source_note = _prepare_vix_data(hist_data)
    except ValueError as e:
        print(f'  [VIX 图表] {e}，跳过', file=sys.stderr)
        return

    colors = {
        'BLUE': '#1A56DB', 'DARK': '#1E293B', 'GRAY': '#64748B',
        'BG': '#F8FAFC', 'LINE': '#E2E8F0',
        'RED': '#DC2626', 'GREEN': '#16A34A', 'GOLD': '#D4A017',
        'WHITE': '#FFFFFF',
    }

    # 定义两个图表
    periods = [
        {'label': '近1周', 'tail': 7,  'path': VIX_CHART_1W},
        {'label': '近1月', 'tail': 23, 'path': VIX_CHART_1M},
    ]

    for p in periods:
        tail = p['tail']
        d_series = df.tail(tail)
        v = values_all[-tail:]
        if len(v) < 2:
            print(f'  [VIX 图表] {p["label"]} 数据点不足，跳过', file=sys.stderr)
            continue

        fig, ax = plt.subplots(1, 1, figsize=(5.5, 2.6))
        fig.patch.set_facecolor(colors['WHITE'])

        _draw_vix_axes(ax, (d_series, v), dates_all,
                       f'VIX 恐慌指数 · {p["label"]}', colors, mdates)

        fig.text(0.5, 0.01, source_note, ha='center', fontsize=7, color='#94A3B8')

        plt.tight_layout(pad=1.5)
        fig.savefig(p['path'], dpi=120, bbox_inches='tight',
                    facecolor=colors['WHITE'], edgecolor='none')
        plt.close(fig)
        print(f'  [VIX 图表] 生成: docs/charts/vix_trend_{p["label"]}.svg ({len(v)} 个数据点)')

    # 兼容：仍生成旧版合并图（用于 fallback）
    from pathlib import Path
    if Path(VIX_CHART_1W).exists():
        import shutil
        shutil.copy2(VIX_CHART_1W, CHART_FILE)
        print(f'  [VIX 图表] 兼容: 复制到 {CHART_FILE}')


def fetch_via_yfinance() -> dict:
    """使用 yfinance 库获取 VIX 数据"""
    try:
        import yfinance as yf
        vix = yf.Ticker('^VIX')
        hist = vix.history(period='5d')
        if hist.empty:
            return None

        closes = hist['Close'].dropna().values
        if len(closes) == 0:
            return None

        current_vix = float(closes[-1])
        prev_vix = float(closes[-2]) if len(closes) >= 2 else current_vix
        change = current_vix - prev_vix
        change_pct = (change / prev_vix * 100) if prev_vix > 0 else 0

        # 取最近交易日日期
        last_date = hist.index[-1].strftime('%Y-%m-%d')

        level_info = get_vix_level(current_vix)

        return {
            'current': round(current_vix, 2),
            'prev': round(prev_vix, 2),
            'change': round(change, 2),
            'changePct': round(change_pct, 2),
            'level': level_info['level'],
            'cls': level_info['cls'],
            'pct': round(level_info['pct'], 1),
            'date': last_date,
            'updateTime': time.strftime('%Y-%m-%d %H:%M', time.localtime()),
            'source': 'Yahoo Finance (yfinance)',
        }
    except Exception as e:
        print(f'  [VIX] yfinance 抓取失败: {e}', file=sys.stderr)
        return None


def fetch_vix_history(period='1mo') -> object:
    """
    获取 VIX 历史行情用于生成趋势图
    返回 yfinance DataFrame 或 fallback dict 或 None
    """
    try:
        import yfinance as yf
        vix = yf.Ticker('^VIX')
        hist = vix.history(period=period)
        if hist.empty or len(hist['Close'].dropna()) < 2:
            return None
        return hist
    except Exception as e:
        print(f'  [VIX 历史] yfinance 抓取失败，使用备用数据: {e}', file=sys.stderr)
        return dict(FALLBACK_HISTORY)  # 返回备用历史数据


def fetch_vix() -> dict:
    """从多个来源依次尝试获取 VIX 数据"""
    # 方案1: yfinance
    data = fetch_via_yfinance()
    if data:
        return data

    # 方案2: 备用数据
    print('  [VIX] 所有 API 失败，使用备用数据', file=sys.stderr)
    fallback = dict(FALLBACK_DATA)
    fallback['updateTime'] = time.strftime('%Y-%m-%d %H:%M', time.localtime())
    return fallback


def generate_js(vix_data: dict) -> str:
    """生成 vix-data.js 内容"""
    if vix_data is None:
        return (
            '// VIX 数据暂不可用\n'
            '// Generated by scripts/fetch-vix-data.py\n'
            'window.__VIX_DATA = null;\n'
        )

    note_line = f'// 备注: {vix_data["note"]}\n' if 'note' in vix_data else ''

    return (
        '// VIX 恐慌指数 — 由 scripts/fetch-vix-data.py 自动生成\n'
        f'// 生成时间: {vix_data["updateTime"]} | 数据源: {vix_data["source"]}\n'
        f'{note_line}'
        'window.__VIX_DATA = {\n'
        f'  current: {vix_data["current"]},\n'
        f'  prev: {vix_data["prev"]},\n'
        f'  change: {vix_data["change"]},\n'
        f'  changePct: {vix_data["changePct"]},\n'
        f'  level: "{vix_data["level"]}",\n'
        f'  cls: "{vix_data["cls"]}",\n'
        f'  pct: {vix_data["pct"]},\n'
        f'  date: "{vix_data["date"]}",\n'
        f'  updateTime: "{vix_data["updateTime"]}",\n'
        f'  source: "{vix_data["source"]}",\n'
        '};\n'
    )


def main():
    print('[VIX] 正在抓取 VIX 恐慌指数...')
    vix_data = fetch_vix()

    if vix_data:
        arrow = '\u2191' if vix_data['change'] >= 0 else '\u2193'
        print(f'  [OK] 当前: {vix_data["current"]}  {vix_data["level"]}')
        print(f'       前一交易日: {vix_data["prev"]}  {arrow} {abs(vix_data["change"])} ({vix_data["changePct"]:+.2f}%)')
        print(f'       日期: {vix_data["date"]}')
        if 'note' in vix_data:
            print(f'       ({vix_data["note"]})')
    else:
        print('  [!!] 抓取失败，数据标记为 null')
        print('       首页将显示"暂无数据"')

    js_content = generate_js(vix_data)

    if '--print' in sys.argv:
        print('\n' + js_content)
        return

    # 写入 JS 数据文件
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f'  [OK] 写入: data/vix-data.js')

    # 生成趋势图（除非指定 --no-chart）
    if '--no-chart' not in sys.argv and vix_data is not None:
        print('[VIX] 正在获取历史数据生成趋势图...')
        hist = fetch_vix_history(period='1mo')
        if hist is not None:
            generate_vix_charts(hist)
        else:
            print('  [VIX 图表] 历史数据不可用，跳过')
    else:
        print('  [VIX 图表] 跳过')


if __name__ == '__main__':
    main()
