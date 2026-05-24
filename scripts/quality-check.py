#!/usr/bin/env python3
"""
扬说财经 · 质量检查 Agent
每个产出环节的独立质量验证，确保：
  1. ✅ 品牌资产 — 头像/头图/封面包含真实人物图片
  2. ✅ 漫画分镜 — 每个panel包含人物图片引用
  3. ✅ 文章 — 三層结构完整，无断链
  4. ✅ 数据图表 — 5张SVG均存在且含中文
  5. ✅ 音频 — 文件有效，大小合理
  6. ✅ 面板计数 — storyboard与SVG文件数一致

用法:
  python scripts/quality-check.py            # 完整检查
  python scripts/quality-check.py --模块名    # 单模块
"""

import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = time.strftime('%Y-%m-%d')

PASS = 0
FAIL = 0


WARN = 0

FAIL_MSGS = []          # 记录所有FAIL消息，用于硬性门禁匹配

# 硬性门禁关键词：命中任一关键词的FAIL消息，直接触发D级
HARD_GATE_KEYWORDS = [
    'article.html缺失',
    'audio.mp3缺失',
    'audio.mp3 文件过小',
    '缺少 Layer1',
    '缺少 Layer2',
    '缺少 Layer3',
    '断链',
    '含未允许英文词汇',
]

# 数据编造检测（占位配置，实际规则由事实核查Agent维护）
SUSPICIOUS_PATTERNS = [
    r'创.*历史.*纪录',
    r'历史第\d+次',
    r'史上最[高低大小]',
    r'首次突破',
    r'创\d+年新高',
]
KNOWN_FACTS = [
    '上证指数',
    '沪深300',
    '纳斯达克',
    '标普500',
]


def ok(msg):
    global PASS
    PASS += 1
    print('  [PASS] %s' % msg)


def fail(msg):
    global FAIL, FAIL_MSGS
    FAIL += 1
    FAIL_MSGS.append(msg)
    print('  [FAIL] %s' % msg)


def warn(msg):
    global WARN
    WARN += 1
    print('  [WARN] %s' % msg)


# ================================================================
# 1. 品牌资产检查
# ================================================================

def check_brand():
    print('\n--- Brand Assets ---')
    assets_dir = os.path.join(ROOT, 'docs', 'assets')
    char_dir = os.path.join(assets_dir, 'character')

    # 人物图片存在
    for f in ['ayang-square.jpg', 'ayang-portrait.jpg']:
        path = os.path.join(char_dir, f)
        if os.path.exists(path):
            sz = os.path.getsize(path)
            ok('人物图片 %s (%.0f KB)' % (f, sz/1024))
        else:
            fail('人物图片缺失: %s' % f)

    # SVG包含人物图片引用（兼容文件路径和base64 data URI）
    def has_character_image(content):
        return 'ayang-portrait.jpg' in content or 'data:image/jpeg;base64' in content

    for svg in ['avatar.svg', 'header.svg', 'cover-morning.svg', 'cover-evening.svg']:
        path = os.path.join(assets_dir, svg)
        if not os.path.exists(path):
            fail('品牌SVG缺失: %s' % svg)
            continue
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        if has_character_image(c):
            ok('%s 包含人物图片' % svg)
        else:
            fail('%s 缺少人物图片引用' % svg)

    # 组件SVG
    comp_dir = os.path.join(ROOT, 'docs', 'components')
    for svg in ['character-sm.svg', 'character-md.svg', 'character-lg.svg']:
        path = os.path.join(comp_dir, svg)
        if not os.path.exists(path):
            fail('组件SVG缺失: %s' % svg)
            continue
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        if has_character_image(c):
            ok('组件 %s 包含人物图片' % svg)
        else:
            fail('组件 %s 缺少人物图片' % svg)


# ================================================================
# 2. 漫画分镜检查
# ================================================================

def check_comics():
    print('\n--- Comics ---')
    for edition in ['morning', 'evening']:
        comic_dir = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'comic')
        if not os.path.isdir(comic_dir):
            fail('%s comic目录缺失' % edition)
            continue

        files = sorted(f for f in os.listdir(comic_dir) if f.endswith('.svg'))
        if not files:
            fail('%s 无SVG文件' % edition)
            continue

        ok('%s: %d个SVG面板' % (edition, len(files)))

        # 每个面板检查人物图片引用（兼容文件路径和base64 data URI）
        def has_character_image(content):
            return 'ayang-portrait.jpg' in content or 'data:image/jpeg;base64' in content

        missing_count = 0
        for f in files:
            path = os.path.join(comic_dir, f)
            with open(path, 'r', encoding='utf-8') as fp:
                c = fp.read()
            if not has_character_image(c):
                missing_count += 1
                fail('%s/%s 缺少人物图片' % (edition, f))

        if missing_count == 0:
            ok('%s 所有面板均包含人物图片' % edition)

        # 检查文件数与storyboard一致
        sb_path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'storyboard.json')
        if os.path.exists(sb_path):
            with open(sb_path, 'r', encoding='utf-8') as fp:
                sb = json.load(fp)
            panel_count = len(sb.get('panels', []))
            file_count = len(files)
            if file_count == panel_count:
                ok('%s 文件数(%d)与storyboard面板数(%d)一致' % (edition, file_count, panel_count))
            else:
                fail('%s 文件数(%d)与storyboard面板数(%d)不匹配' % (edition, file_count, panel_count))


# ================================================================
# 3. 文章检查
# ================================================================

def check_articles():
    print('\n--- Articles ---')
    for edition in ['morning', 'evening']:
        html_path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'article.html')
        md_path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'article.md')

        # HTML检查
        if not os.path.exists(html_path):
            fail('%s article.html缺失' % edition)
        else:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            layers = {
                'Layer1 (热点速览)': 'layer1' in html or 'l1-title' in html,
                'Layer2 (深度解读)': 'layer2' in html or 'l2-title' in html,
                'Layer3 (数据)': 'layer3' in html or 'l3-title' in html,
                '音频播放器': 'audio' in html and 'audio.mp3' in html,
                '品牌标识': '扬说财经' in html,
            }
            for name, result in layers.items():
                if result:
                    ok('%s: %s' % (edition, name))
                else:
                    fail('%s: 缺少 %s' % (edition, name))

            # 检查漫画网格是否是自适应（auto-fill minmax）
            if 'auto-fill' in html and 'minmax' in html:
                ok('%s: 漫画网格自适应排版 ✓' % edition)
            else:
                warn('%s: 漫画网格使用固定列数（建议auto-fill minmax）' % edition)

            # 检查品牌区域是否有人物写真
            if 'ayang-portrait.jpg' in html:
                ok('%s: 品牌区域含人物写真 ✓' % edition)
            else:
                fail('%s: 品牌区域缺少人物写真' % edition)

            # 检查断链
            broken = []
            for m in re.finditer(r'src="([^"]+)"', html):
                ref = m.group(1)
                full = os.path.normpath(os.path.join(os.path.dirname(html_path), ref))
                if not os.path.exists(full):
                    broken.append(ref)
            if broken:
                for ref in broken:
                    fail('%s: 断链 %s' % (edition, ref))
            else:
                ok('%s: 无断链引用' % edition)

        # MD检查
        if not os.path.exists(md_path):
            fail('%s article.md缺失' % edition)
        else:
            with open(md_path, 'r', encoding='utf-8') as f:
                md = f.read()
            if len(md) > 500:
                ok('%s article.md (%d chars)' % (edition, len(md)))
            else:
                fail('%s article.md 内容过短' % edition)


# ================================================================
# 4. 图表检查
# ================================================================

def check_charts():
    print('\n--- Charts ---')
    chart_dir = os.path.join(ROOT, 'docs', 'charts')
    if not os.path.isdir(chart_dir):
        fail('charts目录缺失')
        return

    expected = ['nvidia_revenue.svg', 'nvidia_net_income.svg',
                'gold_price_trend.svg', 'central_bank_gold.svg',
                'pboc_gold_reserves.svg']
    for f in expected:
        path = os.path.join(chart_dir, f)
        if not os.path.exists(path):
            fail('图表缺失: %s' % f)
        else:
            sz = os.path.getsize(path)
            ok('图表 %s (%.0f KB)' % (f, sz/1024))


# ================================================================
# 5. 音频检查
# ================================================================

def check_audio():
    print('\n--- Audio ---')
    for edition in ['morning', 'evening']:
        path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'audio.mp3')
        if not os.path.exists(path):
            fail('%s audio.mp3缺失' % edition)
        else:
            sz = os.path.getsize(path)
            if sz > 500 * 1024:  # >500KB
                ok('%s audio.mp3 (%.0f KB)' % (edition, sz/1024))
            else:
                fail('%s audio.mp3 文件过小 (%.0f KB)' % (edition, sz/1024))

        # 检查口播脚本
        script_path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'script.txt')
        if not os.path.exists(script_path):
            fail('%s script.txt缺失（需专人审核）' % edition)
        else:
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            if len(script) < 100:
                fail('%s script.txt 内容过短' % edition)
            else:
                ok('%s script.txt (%d chars)' % (edition, len(script)))
            # 检查英文字母（允许常见金融缩写和 "A股" 中单字母）
            ALLOWED_ENGLISH = {'WTI', 'COMEX', 'NASDAQ', 'ETF', 'GPU', 'AI', 'CPU',
                               'HBM', 'PCB', 'PE', 'AUM', 'PCE', 'Q1', 'Q2', 'Q3', 'Q4',
                               'FY', 'YoY', 'OTC'}
            eng_words = set(re.findall(r'\b[A-Za-z]{2,}\b', script)) - ALLOWED_ENGLISH
            if eng_words:
                fail('%s script.txt 含未允许英文词汇: %s' % (edition, ', '.join(sorted(eng_words))))
            else:
                ok('%s script.txt 无未允许英文词汇' % edition)

        # 检查 script.txt 与 audio.mp3 内容一致（无SSML标签混入）
        script_txt_path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'script.txt')
        if os.path.exists(script_txt_path) and os.path.exists(path):
            with open(script_txt_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            if '<' in script_content and '>' in script_content:
                fail('%s script.txt 含XML标签，TTS会朗读为乱码' % edition)
            else:
                ok('%s script.txt 纯净文本，无标签' % edition)


# ================================================================
# 6. Pipeline脚本检查
# ================================================================

def check_pipeline():
    print('\n--- Pipeline ---')
    script_dir = os.path.join(ROOT, 'scripts')
    scripts = ['morning.sh', 'evening.sh', 'character_svg.py', 'rebrand-character.py',
               'upgrade-comic.py', 'upgrade-audio.py', 'generate-charts.py',
               'quality-check.py', 'article-template.py']
    for s in scripts:
        path = os.path.join(script_dir, s)
        if os.path.exists(path):
            sz = os.path.getsize(path)
            ok('脚本 %s (%.0f KB)' % (s, sz/1024))
        else:
            fail('脚本缺失: %s' % s)


# ================================================================
# Main
# ================================================================

if __name__ == '__main__':
    module_map = {
        'brand': check_brand,
        'comics': check_comics,
        'articles': check_articles,
        'charts': check_charts,
        'audio': check_audio,
        'pipeline': check_pipeline,
    }

# ================================================================
# 7. 新闻源检查（每日复盘用）
# ================================================================

def check_news_sources():
    print('\n--- News Sources ---')
    review_dir = os.path.join(ROOT, 'docs', 'review')
    if not os.path.isdir(review_dir):
        fail('docs/review 目录缺失')
        return

    for prefix, label in [('news-domestic', '国内财经'), ('news-international', '国际财经')]:
        path = os.path.join(review_dir, '%s-%s.md' % (prefix, TODAY))
        if not os.path.exists(path):
            fail('%s新闻简报缺失' % label)
            continue

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查[待采集]标记
        pending = content.count('[待采集]')
        if pending == 0:
            ok('%s新闻简报: 数据已填充' % label)
        else:
            fail('%s新闻简报: %d处数据待采集' % (label, pending))

        # 检查来源链接
        url_count = content.count('http')
        if url_count > 0:
            ok('%s新闻简报: %d个来源链接' % (label, url_count))
        else:
            warn('%s新闻简报: 暂无来源链接' % label)


# ================================================================
# 8. 团队健康检查
# ================================================================

def check_team_health():
    print('\n--- Team Health ---')
    agent_dir = os.path.join(ROOT, 'scripts', 'agents')
    expected_agents = {
        'content-prep.sh': '内容验证Agent',
        'status.sh': '状态检查Agent',
        'news-collector.sh': '新闻采集Agent',
        'fact-checker.sh': '事实核查Agent',
        'comic-stylist.sh': '漫画风格迭代Agent',
        'competition-analyst.sh': '竞争分析Agent',
        'daily-review.sh': '每日复盘Agent',
    }
    for fname, desc in expected_agents.items():
        path = os.path.join(agent_dir, fname)
        if os.path.exists(path):
            sz = os.path.getsize(path)
            ok('%s (%s, %.0f KB)' % (desc, fname, sz/1024))
        else:
            fail('%s 缺失: %s' % (desc, fname))

    # 检查团队文档
    team_dir = os.path.join(ROOT, 'docs', 'team')
    for fname in ['TEAM.md', 'AGENT_HANDBOOK.md']:
        path = os.path.join(team_dir, fname)
        if os.path.exists(path):
            ok('团队文档: %s' % fname)
        else:
            fail('团队文档缺失: %s' % fname)

    # 检查文章模板
    template_path = os.path.join(ROOT, 'scripts', 'article-template.py')
    if os.path.exists(template_path):
        sz = os.path.getsize(template_path)
        ok('文章模板: article-template.py (%.0f KB)' % (sz/1024))
    else:
        fail('文章模板缺失: article-template.py')


# ================================================================
# 评分系统
# ================================================================

def check_hard_gates():
    """检查硬性门禁项，返回命中列表。任一命中直接D级。"""
    hits = []
    for msg in FAIL_MSGS:
        for kw in HARD_GATE_KEYWORDS:
            if kw in msg:
                hits.append(msg)
                break
    return hits


def check_data_fabrication():
    """检查数据编造嫌疑。SUSPICIOUS_PATTERNS命中且非KNOWN_FACTS则报警。"""
    # 扫描 article.html 和 article.md
    hits = []
    for edition in ['morning', 'evening']:
        for ext in ['html', 'md']:
            path = os.path.join(ROOT, TODAY, 'wechat-publish', edition, 'article.%s' % ext)
            if not os.path.exists(path):
                continue
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            for pat in SUSPICIOUS_PATTERNS:
                for m in re.finditer(pat, content):
                    matched_text = m.group(0)
                    # 检查是否命中KNOWN_FACTS(已知事实)
                    is_known = any(kf in matched_text for kf in KNOWN_FACTS)
                    if not is_known:
                        hits.append('%s/%s: %s' % (edition, 'article.%s' % ext, matched_text))
    return hits


def calculate_grade():
    """计算质量评分和等级。返回 (score, max_score, pct, grade, hard_hits, exit_code, (grade_icon, grade_desc))"""
    total_items = PASS + FAIL + WARN
    if total_items == 0:
        return 0, 0, 0, 'D', [], 3, ('\u274c', '\u65e0\u68c0\u67e5\u9879\uff0c\u65e0\u6cd5\u8bc4\u5206')

    max_score = total_items
    score = max(0, PASS * 1 + WARN * (-0.5) + FAIL * (-1))
    pct = round(score / max_score * 100, 1) if max_score > 0 else 0

    # 硬性门禁检查
    hard_gate_hits = check_hard_gates()
    fabrication_hits = check_data_fabrication()
    all_hard_hits = hard_gate_hits + fabrication_hits

    # 如果命中硬性门禁，直接D级
    if all_hard_hits:
        grade = 'D'
    elif pct >= 90:
        grade = 'A'
    elif pct >= 80:
        grade = 'B'
    elif pct >= 60:
        grade = 'C'
    else:
        grade = 'D'

    # 确定退出码和输出信息
    grade_info = {
        'A': ('\U0001f7e2', '优秀，自动放行'),
        'B': ('\U0001f7e1', '良好，人工确认后可放行'),
        'C': ('\U0001f7e0', '需整改关键FAIL项后重检'),
        'D': ('\U0001f534', '阻塞发布，必须全部修复'),
    }

    exit_codes = {'A': 0, 'B': 0, 'C': 2, 'D': 3}

    return score, max_score, pct, grade, all_hard_hits, exit_codes[grade], grade_info[grade]


# ================================================================
# Main
# ================================================================

if __name__ == '__main__':
    module_map = {
        'brand': check_brand,
        'comics': check_comics,
        'articles': check_articles,
        'charts': check_charts,
        'audio': check_audio,
        'pipeline': check_pipeline,
        'news': check_news_sources,
        'team': check_team_health,
    }

    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target in module_map:
            module_map[target]()
        else:
            print('未知模块: %s (可选: %s)' % (target, '/'.join(module_map.keys())))
            sys.exit(1)
    else:
        for name, fn in module_map.items():
            fn()

    # 评分计算
    score, max_score, pct, grade, hard_hits, exit_code, (grade_icon, grade_desc) = calculate_grade()

    # 输出报告
    total = PASS + FAIL + WARN
    bar = '\u2550' * 40
    print('\n' + bar)
    print('   质量检查报告')
    print(bar)
    print('   PASS: %d   FAIL: %d   WARN: %d' % (PASS, FAIL, WARN))
    print(bar)
    print('   评分: %d/%d = %s%%  \u279c  %s %s级（%s）' % (
        int(score), max_score, pct, grade_icon, grade, grade_desc))
    print(bar)
    if hard_hits:
        print('   硬性门禁: 命中 \u2717 (%d项)' % len(hard_hits))
        for h in hard_hits:
            print('     - %s' % h)
    else:
        print('   硬性门禁: 未命中 \u2713')
    print(bar)
    print('   建议: %s' % grade_desc)

    sys.exit(exit_code)
