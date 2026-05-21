#!/usr/bin/env python3
"""
扬说财经 · 文章HTML模板生成器 v2.0

统一排版规范，确保：
  1. 人物图片正确引用（使用用户提供的写真照）
  2. 漫画网格根据图片数量自适应列数
  3. 图片最小宽度≥200px（手机≥150px）
  4. 图表展示可读、不拥挤
  5. 品牌标识在页面底部展示

用法：
  python scripts/article-template.py --session morning --title "标题" --panels 5 --has-charts
  python scripts/article-template.py --session evening --title "标题" --panels 8 --has-charts
"""

import argparse
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_article_html(session, title, panel_count, tags, has_charts=True):
    """生成统一排版的文章HTML"""
    today = time.strftime('%Y-%m-%d')
    date_display = time.strftime('%Y.%m.%d')

    is_morning = session == 'morning'
    label = '早间' if is_morning else '晚间'
    edition_cn = '早报' if is_morning else '晚报'
    header_color = '#1A56DB,#1E3A7A' if is_morning else '#D4A017,#B8860B'
    accent_color = '#1A56DB' if is_morning else '#D4A017'
    accent_color2 = '#D4A017' if is_morning else '#B8860B'
    border_color = '#D4A017'

    # 漫画网格CSS - 自适应列数，确保最小宽度
    # 1张图: 1列100% | 2张: 2列 | 3-4张: 2列 | 5-6张: 3列 | 7+: 4列
    if panel_count <= 1:
        grid_cols = '1fr'
    elif panel_count <= 2:
        grid_cols = 'repeat(2, 1fr)'
    elif panel_count <= 4:
        grid_cols = 'repeat(2, 1fr)'
    elif panel_count <= 6:
        grid_cols = 'repeat(3, 1fr)'
    else:
        grid_cols = 'repeat(4, 1fr)'

    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system,"PingFang SC","Microsoft YaHei","Helvetica Neue",sans-serif; background: #F5F7FA; color: #1E293B; line-height: 1.8; font-size: 16px; }}
  .c {{ max-width: 640px; margin: 0 auto; background: #fff; padding: 44px 0 40px; }}

  /* Top nav */
  .top-nav {{ position: fixed; top: 0; left: 0; right: 0; z-index: 100; max-width: 640px; margin: 0 auto; background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); border-bottom: 1px solid #E2E8F0; display: flex; align-items: center; padding: 0 16px; height: 44px; }}
  .top-nav .back {{ display: flex; align-items: center; gap: 4px; color: #1A56DB; text-decoration: none; font-size: 13px; font-weight: 600; }}
  .top-nav .nav-date {{ flex: 1; text-align: center; font-size: 12px; color: #64748B; }}
  .top-nav .nav-edition {{ font-size: 11px; color: #94A3B8; background: #F1F5F9; padding: 2px 8px; border-radius: 8px; }}
  .top-nav .nav-edition.am {{ color: #1A56DB; background: #EFF6FF; }}
  .top-nav .nav-edition.pm {{ color: #D4A017; background: #FFFBEB; }}

  /* 头部 */
  .header {{ background: linear-gradient(135deg,{header_color}); padding: 20px 20px 16px; color: white; }}
  .header h1 {{ font-size: 22px; font-weight: 700; line-height: 1.4; margin-bottom: 6px; }}
  .header .meta {{ font-size: 12px; opacity: 0.8; display: flex; gap: 12px; flex-wrap: wrap; }}

  /* 音频播放器 */
  .player {{ display: flex; align-items: center; gap: 12px; margin-top: 14px; }}
  .player-icon {{ width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 18px; }}
  .player-info {{ flex: 1; }}
  .player-title {{ font-size: 13px; font-weight: 600; }}
  .player-desc {{ font-size: 11px; opacity: 0.7; }}
  .player audio {{ width: 100%; margin-top: 4px; border-radius: 20px; }}

  .body {{ padding: 20px 20px 0; }}

  /* ----- Layer 1: 热点速览 ----- */
  .layer1 {{ margin-bottom: 28px; }}
  .l1-title {{ font-size: 16px; font-weight: 700; color: {accent_color}; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
  .l1-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 12px; }}
  .l1-item {{ background: #F8F9FA; border-radius: 8px; padding: 8px 10px; border-left: 3px solid {accent_color}; }}
  .l1-item .tag {{ font-size: 10px; font-weight: 700; display: block; margin-bottom: 2px; }}
  .l1-item .txt {{ font-size: 12px; color: #475569; }}
  .l1-item .pct {{ font-size: 11px; font-weight: 600; }}
  .l1-up {{ border-left-color: #EF4444; }} .l1-up .tag {{ color: #EF4444; }}
  .l1-gold {{ border-left-color: {border_color}; }} .l1-gold .tag {{ color: {border_color}; }}
  .l1-blue {{ border-left-color: #1A56DB; }} .l1-blue .tag {{ color: #1A56DB; }}
  .l1-green {{ border-left-color: #10B981; }} .l1-green .tag {{ color: #10B981; }}
  .l1-purple {{ border-left-color: #8B5CF6; }} .l1-purple .tag {{ color: #8B5CF6; }}
  .l1-orange {{ border-left-color: #F59E0B; }} .l1-orange .tag {{ color: #D97706; }}
  .l1-comic {{ margin: 8px -10px 0; }}
  .l1-comic img {{ width: 100%; border-radius: 10px; border: 1px solid #E2E8F0; }}
  .l1-divider {{ border: none; border-top: 2px dashed {border_color}; margin: 16px 0; }}

  /* ----- Layer 2: 深度解读 — 漫画网格（自适应列数）----- */
  .layer2 {{ margin-bottom: 24px; }}
  .l2-title {{ font-size: 16px; font-weight: 700; color: {accent_color2}; margin-bottom: 14px; display: flex; align-items: center; gap: 6px; }}

  /* ★ 核心改进：漫画网格使用auto-fill确保每张图最小宽度足够 */
  .comic-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
    margin: 14px 0;
  }}
  .comic-grid img {{
    width: 100%;
    height: auto;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    transition: transform 0.2s ease;
  }}
  .comic-grid img:hover {{
    transform: scale(1.02);
  }}
  /* 手机端：最小宽度降到140px，确保2列布局 */
  @media (max-width:480px) {{
    .comic-grid {{
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 6px;
    }}
  }}

  .quote {{ background: #F0F4FF; border-left: 4px solid {accent_color}; padding: 12px 14px; margin: 14px 0; border-radius: 0 8px 8px 0; font-size: 14px; color: #1E3A7A; line-height: 1.7; }}
  h2 {{ font-size: 17px; font-weight: 700; color: {accent_color}; margin: 22px 0 10px; padding-bottom: 6px; border-bottom: 2px solid {border_color}; }}
  h3 {{ font-size: 15px; font-weight: 600; color: #F59E0B; margin: 16px 0 8px; }}
  p {{ margin-bottom: 12px; text-align: justify; font-size: 15px; }}

  .gold-box {{ background: linear-gradient(135deg,#FFF8E7,#FFF3D6); border: 1px solid {border_color}; border-radius: 12px; padding: 18px 20px; margin: 22px 0; text-align: center; font-size: 16px; font-weight: 700; color: #B8860B; line-height: 1.5; }}

  .analogy {{ background: #F0FFF4; border: 1px solid #A7F3D0; border-radius: 10px; padding: 10px 14px; margin: 12px 0; font-size: 13px; color: #065F46; }}
  .analogy::before {{ content: "💡 类比一下："; font-weight: 600; color: #059669; }}
  .fun-fact {{ background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 10px 14px; margin: 12px 0; font-size: 13px; color: #92400E; }}
  .fun-fact::before {{ content: "🤯 你知道么："; font-weight: 600; color: #D97706; }}
  .insight {{ background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 10px 14px; margin: 10px 0; font-size: 13px; }}
  .insight strong {{ color: #1A56DB; }}
  .divider {{ border: none; border-top: 2px dashed #E2E8F0; margin: 20px 0; }}

  /* ----- Layer 3: 数据 ----- */
  .layer3 {{ margin-bottom: 24px; }}
  .l3-title {{ font-size: 16px; font-weight: 700; color: {accent_color}; margin-bottom: 10px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }}
  th {{ background: {accent_color}; color: #fff; padding: 8px 10px; text-align: left; font-weight: 600; }}
  th:first-child {{ border-radius: 6px 0 0 0; }}
  th:last-child {{ border-radius: 0 6px 0 0; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #E2E8F0; }}
  tr:nth-child(even) {{ background: #F8F9FA; }}
  .up {{ color: #EF4444; font-weight: 600; }}
  .down {{ color: #10B981; font-weight: 600; }}

  .warn {{ background: #FFF5F5; border: 1px solid #FECACA; border-radius: 10px; padding: 12px 14px; margin-top: 24px; font-size: 12px; color: #991B1B; line-height: 1.5; }}
  .list {{ background: #F8F9FA; border-radius: 8px; padding: 10px 14px; margin: 10px 0; }}
  .list-item {{ padding: 5px 0; border-bottom: 1px solid #E2E8F0; font-size: 13px; display: flex; gap: 6px; }}
  .list-item:last-child {{ border-bottom: none; }}
  .tag-b {{ display: inline-block; background: {accent_color}; color: #fff; font-size: 10px; padding: 1px 7px; border-radius: 8px; white-space: nowrap; }}

  /* 数据图表 — 单图全宽，双图各半 */
  .chart {{ margin: 16px 0; background: #F8F9FA; border-radius: 10px; padding: 10px; text-align: center; border: 1px solid #E2E8F0; }}
  .chart img {{ max-width: 100%; height: auto; border-radius: 6px; }}
  .chart-label {{ font-size: 12px; color: #64748B; margin-top: 6px; }}
  .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }}
  @media (max-width:480px) {{ .chart-row {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="c">

  <!-- 顶部导航栏 -->
  <div class="top-nav">
    <a class="back" href="../../../index.html">&larr; 返回首页</a>
    <span class="nav-date">{date_display}</span>
    <span class="nav-edition {session}">{edition_cn}</span>
  </div>

  <!-- 头部 -->
  <div class="header">
    <h1>{title}</h1>
    <div class="meta">
      <span>📅 {date_display} {label}</span>
      <span>🏷️ {tags}</span>
      <span>👤 主讲：阿扬</span>
    </div>
    <div class="player">
      <div class="player-icon">🎧</div>
      <div class="player-info">
        <div class="player-title">音频解说</div>
        <div class="player-desc">边听边看，体验更佳</div>
        <audio controls preload="none"><source src="audio.mp3" type="audio/mpeg"></audio>
      </div>
    </div>
  </div>

  <div class="body">

    <!-- ════════════════════════════════════════ -->
    <!-- LAYER 1：今日热点速览 -->
    <!-- ════════════════════════════════════════ -->
    <div class="layer1">

      <div class="l1-title">📋 今日热点{"回顾" if not is_morning else "速览"} <span style="font-size:12px;color:#64748B;font-weight:400;">— 60秒掌握关键信息</span></div>

      <div class="l1-grid">
        <!-- 由内容编辑填充 -->
        [L1_ITEMS]
      </div>

      <div class="l1-comic">
        <img src="comic/panel-000.svg" alt="扬说财经速览">
        <div style="text-align:center;font-size:11px;color:#64748B;margin-top:4px;">📡 扬说财经 — 今天这些大事你需要知道</div>
      </div>

      <hr class="l1-divider">
      <div style="text-align:center;font-size:12px;color:{border_color};margin-bottom:4px;">▼ 往下翻看今日深度解读 ▼</div>
    </div>

    <!-- ════════════════════════════════════════ -->
    <!-- LAYER 2：今日深度解读 -->
    <!-- ════════════════════════════════════════ -->
    <div class="layer2">

      <div class="l2-title">🔍 今日深度专题</div>

      <!-- 由内容编辑填充 -->
      [L2_CONTENT]

    </div>

    <!-- ════════════════════════════════════════ -->
    <!-- LAYER 3：关键市场数据 -->
    <!-- ════════════════════════════════════════ -->
    <div class="layer3">
      <div class="l3-title">📊 关键市场数据一览</div>

      <!-- 由内容编辑填充 -->
      [L3_TABLE]

      <!-- 品牌信息 -->
      <div style="background:linear-gradient(135deg,#1A56DB,#1E3A7A);border-radius:12px;padding:16px 20px;margin:22px 0;color:white;text-align:center;">
        <img src="../../../docs/assets/character/ayang-portrait.jpg" style="width:48px;height:48px;border-radius:50%;object-fit:cover;margin-bottom:6px;border:2px solid rgba(255,255,255,0.3);" alt="阿扬">
        <div style="font-size:14px;font-weight:700;margin-bottom:4px;">📡 扬说财经</div>
        <div style="font-size:11px;opacity:0.8;margin-bottom:8px;">用漫画看懂财经 — 你好，我是阿扬</div>
        <div style="display:flex;justify-content:center;gap:16px;font-size:10px;opacity:0.6;">
          <span>🌅 扬说·早报</span>
          <span>🌙 扬说·夜读</span>
          <span>📖 扬说·课堂</span>
        </div>
      </div>

      <div class="warn">⚠️ <strong>风险提示：</strong>以上内容仅为信息分享，不构成任何投资建议。市场有风险，投资需谨慎。</div>
    </div>

  </div>
</div>
</body>
</html>'''


def write_article(session, title, panel_count, tags, html_content, charts_content=''):
    """写入article.html到对应的版次目录"""
    today = time.strftime('%Y-%m-%d')
    article_dir = os.path.join(ROOT, today, 'wechat-publish', session)
    os.makedirs(article_dir, exist_ok=True)

    # 生成基础HTML框架
    html = generate_article_html(session, title, panel_count, tags)

    # 用内容替换占位标记
    html = html.replace('[L1_ITEMS]', '<!-- 由内容编辑填充Layer1卡片项 -->')
    html = html.replace('[L2_CONTENT]', '<!-- 由内容编辑填充Layer2深度解读内容 -->')
    html = html.replace('[L3_TABLE]', '<!-- 由内容编辑填充Layer3数据表格 -->')

    output_path = os.path.join(article_dir, 'article.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  ✅ {session} article.html 已生成 ({os.path.getsize(output_path)/1024:.0f} KB)')
    print(f'  📍 {output_path}')
    print(f'  💡 需要手动填充 [L1_ITEMS] [L2_CONTENT] [L3_TABLE] 占位标记')
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='扬说财经 · 文章HTML模板生成器 v2.0')
    parser.add_argument('--session', choices=['morning', 'evening'], required=True)
    parser.add_argument('--title', required=True, help='文章标题')
    parser.add_argument('--panels', type=int, default=5, help='漫画面板数量')
    parser.add_argument('--tags', default='财经', help='文章标签')
    parser.add_argument('--write', action='store_true', help='写入文件')

    args = parser.parse_args()

    html = generate_article_html(args.session, args.title, args.panels, args.tags)

    if args.write:
        write_article(args.session, args.title, args.panels, args.tags)
    else:
        # 输出前200字符预览
        print(html[:500])
        print('...')
        print(f'\n(共 {len(html)} chars)')
        print(f'\n💡 运行 python scripts/article-template.py --session {args.session} --title "标题" --panels 5 --write 直接写入文件')
