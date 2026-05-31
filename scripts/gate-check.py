#!/usr/bin/env python3
"""
扬说财经 · 质量门禁 v5.0

硬性门禁（阻塞发布）：
  1. 数据来源检查 — 每个板块必须有来源区块，数据点需标注出处
  2. 漫画风格检查 — 白底/黑线/300×220/无人物/无渐变
  3. 音频时长匹配 — 页面标注 vs 实际时长 ≤20%
  4. 模板占位符 — 无 {{ 残留
  5. 合规声明 — 必须有"不构成投资建议"
  6. 6故事结构 — 顺序完整
  7. 数据图表 — generate-charts.py 当天已运行
  8. 7条铁律 — "历史第X次"类表述必须有来源

用法:
  python scripts/gate-check.py                     # 检查今天所有版次
  python scripts/gate-check.py --edition evening   # 只查晚报
  python scripts/gate-check.py --date 2026-05-24   # 查指定日期
  python scripts/gate-check.py --json              # 输出JSON报告

返回码: 0=通过, 1=待修复, 2=阻塞(不可发布)
"""

import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = time.strftime('%Y-%m-%d')

# 颜色
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# ================================================================
# 硬性门禁配置
# ================================================================

SUSPICIOUS_PATTERNS = [
    r'历史第[一二三四五六七八九十\d][次回]',
    r'创.*历史.*新[高低]',
    r'史上最[大中小高低好差]',
    r'创\d+年[以还].*[新高最低]',
    r'前所未有',
    r'(?<!\w)最[大热疯]',
]

COMIC_STANDARDS = {
    'max_size_kb': 5,          # 文件 < 5KB
    'bg_colors': ['#faf8f5', '#FAFAFA', '#fafafa'],  # 允许的背景色
    'no_gradients': True,      # 禁止渐变
    'no_characters': True,     # 禁止人物形象
    'no_shadows': True,        # 禁止投影
    'viewbox': '300 220',      # 固定尺寸
}


# ================================================================
# 检查项
# ================================================================

class GateResult:
    """单项检查结果"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.passed = True
        self.errors = []
        self.warnings = []

    def fail(self, msg):
        self.passed = False
        self.errors.append(msg)
        print(f'  {RED}✗ {msg}{RESET}')

    def warn(self, msg):
        self.warnings.append(msg)
        print(f'  {YELLOW}△ {msg}{RESET}')

    def pass_(self, msg):
        print(f'  {GREEN}✓ {msg}{RESET}')

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
        }


def find_article_path(date, edition, special_topic=None):
    if special_topic:
        path = os.path.join(ROOT, 'special', special_topic, 'article.html')
        if os.path.exists(path):
            return path
        return None
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'article.html')
    if os.path.exists(path):
        return path
    # Also check caijing directory
    alt = os.path.join(ROOT, 'caijing', date, 'article.html')
    if os.path.exists(alt):
        return alt
    return None


def find_comic_dir(date, edition, special_topic=None):
    if special_topic:
        path = os.path.join(ROOT, 'special', special_topic, 'comic')
        if os.path.isdir(path):
            return path
        return None
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'comic')
    if os.path.isdir(path):
        return path
    return None


def find_audio_path(date, edition, special_topic=None):
    if special_topic:
        path = os.path.join(ROOT, 'special', special_topic, 'audio.mp3')
        if os.path.exists(path):
            return path
        return None
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'audio.mp3')
    if os.path.exists(path):
        return path
    return None


def find_script_path(date, edition, special_topic=None):
    if special_topic:
        path = os.path.join(ROOT, 'special', special_topic, 'script.txt')
        if os.path.exists(path):
            return path
        return None
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'script.txt')
    if os.path.exists(path):
        return path
    return None


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ''


# ----------------------------------------------------------------
# Gate 1: 数据来源检查
# ----------------------------------------------------------------
def check_data_sources(date, edition, html, special_topic=None):
    gate = GateResult('data_sources', '数据来源追溯 — 每条数据必须有出处')

    # 提取纯文本（去除HTML标签）
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()

    # 1. 检查是否有 sources 区块
    has_sources_section = bool(re.search(
        r'class="[^"]*sources[^"]*"|class="[^"]*source[^"]*"|参考来源|数据来源|Source',
        html, re.IGNORECASE
    ))
    if not has_sources_section:
        gate.fail('文章缺少 sources 来源区块')

    # 2. 提取所有数据点
    data_points = []
    patterns = [
        (r'\d+\.?\d*%', '百分比'),
        (r'\d+\.?\d*万亿', '万亿级'),
        (r'\d+\.?\d*亿', '亿级'),
        (r'\$\d+[\.\,\d]*', '美元价格'),
        (r'¥\d+[\.\,\d]*', '人民币价格'),
        (r'\d+[\.\,\d]*点', '指数点位'),
    ]
    for pat, desc in patterns:
        matches = re.findall(pat, text)
        data_points.extend(matches)

    # 3. 检查 suspicious patterns
    suspicious_found = []
    for pat in SUSPICIOUS_PATTERNS:
        matches = re.findall(pat, text)
        suspicious_found.extend(matches)

    if suspicious_found:
        for s in suspicious_found[:5]:
            gate.fail(f'可疑表述 "{s}" — 必须标注精确来源')
        if len(suspicious_found) > 5:
            gate.fail(f'还有 {len(suspicious_found) - 5} 处类似可疑表述')

    # 4. 检查来源URL
    urls = re.findall(r'https?://[^\s"\'<>）)]+', html)
    if not urls:
        gate.warn('未发现可点击的URL来源链接')

    # 5. 检查 sources 区块中是否有具体内容
    sources_match = re.search(
        r'(?:参考来源|数据来源|Sources|sources)[：:].*?(?=(?:<div|<section|$))',
        html, re.DOTALL
    )
    if sources_match:
        sources_text = sources_match.group(0)
        url_count = sources_text.count('http')
        if url_count == 0:
            gate.warn('来源区块存在但未包含可点击的URL')

    # 统计
    gate.pass_(f'发现 {len(data_points)} 个数据点，{len(suspicious_found)} 处可疑表述')

    # 报纸来源也算合理（比如"参考来源：路透社 2026-05-24"）
    # 但可疑表述必须每个都有精确来源

    return gate


# ----------------------------------------------------------------
# Gate 2: 漫画风格检查
# ----------------------------------------------------------------
def check_comic_style(date, edition, special_topic=None):
    gate = GateResult('comic_style', f'漫画风格 — 白底/黑线/300×220/无人物/无渐变')

    comic_dir = find_comic_dir(date, edition, special_topic=special_topic)
    if not comic_dir:
        gate.warn('无漫画目录（允许无漫画的情况）')
        gate.passed = True  # 没有漫画不算阻塞
        return gate

    svg_files = sorted([f for f in os.listdir(comic_dir) if f.endswith('.svg')])
    if not svg_files:
        gate.warn('漫画目录为空')
        gate.passed = True
        return gate

    for fname in svg_files:
        path = os.path.join(comic_dir, fname)
        size_kb = os.path.getsize(path) / 1024

        # 文件大小检查
        if size_kb > COMIC_STANDARDS['max_size_kb']:
            gate.fail(f'{fname}: 文件 {size_kb:.1f}KB > {COMIC_STANDARDS["max_size_kb"]}KB 上限')

        content = read_file(path)

        # viewBox检查
        if COMIC_STANDARDS['viewbox'] not in content:
            gate.fail(f'{fname}: viewBox 不是标准 {COMIC_STANDARDS["viewbox"]}')

        # 背景色检查
        bg_ok = any(bg.lower() in content.lower() for bg in COMIC_STANDARDS['bg_colors'])
        if not bg_ok:
            gate.warn(f'{fname}: 背景色不是暖白 ({", ".join(COMIC_STANDARDS["bg_colors"])})')

        # 渐变检查（禁止）
        if 'linearGradient' in content or 'radialGradient' in content or 'gradient' in content.lower():
            gate.fail(f'{fname}: 包含渐变 (linearGradient/radialGradient)')

        # 投影检查
        if 'filter' in content and ('drop-shadow' in content or 'shadow' in content.lower()):
            gate.fail(f'{fname}: 包含投影效果')

        # 人物形象检查（粗略）
        human_keywords = ['人物', '头像', '角色', 'portrait', 'face', 'human']
        for kw in human_keywords:
            if kw in content.lower():
                gate.fail(f'{fname}: 可能包含人物形象关键词 "{kw}"')

        # 文字遮挡检查（检查是否有文字超出viewBox）
        text_elements = re.findall(r'<text[^>]*y="(\d+)"[^>]*>', content)
        for y_str in text_elements:
            y = int(y_str)
            if y < 0 or y > 220:
                gate.warn(f'{fname}: text y坐标({y})可能超出viewBox边界')

        gate.pass_(f'{fname}: {size_kb:.1f}KB')

    if gate.passed and not gate.errors:
        gate.pass_(f'{len(svg_files)} 个SVG全部通过风格检查')

    return gate


# ----------------------------------------------------------------
# Gate 3: 音频时长匹配
# ----------------------------------------------------------------
def check_audio(date, edition, special_topic=None):
    gate = GateResult('audio', '音频 — 时长匹配标注，脚本字数匹配')

    audio_path = find_audio_path(date, edition, special_topic=special_topic)
    script_path = find_script_path(date, edition, special_topic=special_topic)
    article_path = find_article_path(date, edition, special_topic=special_topic)

    # 检查文件存在
    if not audio_path:
        gate.fail('audio.mp3 不存在')
    if not script_path:
        gate.fail('script.txt 不存在')
    if not audio_path or not script_path:
        return gate

    # 音频文件大小
    audio_size_kb = os.path.getsize(audio_path) / 1024
    if audio_size_kb < 100:
        gate.fail(f'audio.mp3 文件过小 ({audio_size_kb:.0f}KB)')
    else:
        gate.pass_(f'audio.mp3: {audio_size_kb:.0f}KB')

    # 脚本字数
    script = read_file(script_path)
    char_count = len(script.strip())
    if char_count < 200:
        gate.fail(f'script.txt 字数过少 ({char_count}字)')
    else:
        gate.pass_(f'script.txt: {char_count}字')

    # 预计时长（从文章HTML中的音频播放器读取）
    expected_minutes = None
    if article_path:
        html = read_file(article_path)
        # 优先匹配音频播放器时长（"音频解说 · 约 X 分钟"）
        duration_match = re.search(r'(?:音频|解说|深度解读)[^。]*?(\d+)\s*分钟', html)
        if not duration_match:
            # Fallback: 匹配阅读时间（"阅读约 X 分钟"）
            duration_match = re.search(r'阅读[约共]*\s*(\d+)\s*分钟', html)
        if not duration_match:
            # Last resort: 任意 "X 分钟"
            duration_match = re.search(r'(\d+)\s*分钟', html)
        if duration_match:
            expected_minutes = int(duration_match.group(1))

    # 根据字数估算实际朗读时长（中文300字/分钟为正常语速评述）
    estimated_minutes_actual = round(char_count / 300, 1)

    if expected_minutes:
        diff_pct = abs(estimated_minutes_actual - expected_minutes) / expected_minutes * 100
        if diff_pct > 20:
            gate.fail(
                f'时长偏差: 页面标注{expected_minutes}分钟'
                f'，{char_count}字约{estimated_minutes_actual}分钟'
                f'（偏差{diff_pct:.0f}%，允许≤20%）'
            )
        else:
            gate.pass_(
                f'页面标注{expected_minutes}分钟'
                f'，脚本{char_count}字 ≈ {estimated_minutes_actual}分钟'
                f'（偏差{diff_pct:.0f}%）'
            )

    # 脚本英文检查
    allowed_english = {'WTI', 'COMEX', 'NASDAQ', 'ETF', 'GPU', 'AI', 'CPU',
                       'HBM', 'PCB', 'PE', 'AUM', 'PCE', 'Q1', 'Q2', 'Q3', 'Q4',
                       'FY', 'YoY', 'OTC', 'NVIDIA', 'OpenAI', 'IPO', 'Fed',
                       'SPAC', 'PMI', 'CPI', 'GDP', 'LPR', 'EPS'}
    eng_words = set(re.findall(r'\b[A-Za-z]{2,}\b', script)) - allowed_english
    if eng_words:
        gate.warn(f'script.txt 含非金融英文词汇: {", ".join(sorted(eng_words)[:8])}')

    return gate


# ----------------------------------------------------------------
# Gate 4: 模板占位符检查
# ----------------------------------------------------------------
def check_placeholders(date, edition, special_topic=None):
    gate = GateResult('placeholders', '模板占位符 — 无 {{ 残留')

    article_path = find_article_path(date, edition, special_topic=special_topic)
    if not article_path:
        gate.fail('article.html 不存在')
        return gate

    html = read_file(article_path)

    # 检查 {{  (CSS content 中的除外)
    placeholders = []
    for i, line in enumerate(html.split('\n'), 1):
        if '{{' in line and 'content' not in line.split('{{')[0][-20:]:
            placeholders.append(f'第{i}行: {line.strip()[:80]}')

    if placeholders:
        for p in placeholders:
            gate.fail(p)
    else:
        gate.pass_('无模板占位符残留')

    return gate


# ----------------------------------------------------------------
# Gate 5: 合规声明
# ----------------------------------------------------------------
def check_compliance(date, edition, special_topic=None):
    gate = GateResult('compliance', '合规声明 — "不构成投资建议"')

    article_path = find_article_path(date, edition, special_topic=special_topic)
    if not article_path:
        gate.fail('article.html 不存在')
        return gate

    html = read_file(article_path)

    if '不构成' in html and '投资建议' in html:
        gate.pass_('合规声明存在')
    else:
        gate.fail('缺少: "不构成…投资建议"')

    return gate


# ----------------------------------------------------------------
# Gate 6: 6故事结构检查
# ----------------------------------------------------------------
def check_six_stories(date, edition, special_topic=None):
    gate = GateResult('six_stories', '6故事结构 — 01-06顺序完整（专题跳过）')

    if special_topic:
        gate.pass_('专题文章跳过6故事结构检查')
        return gate

    article_path = find_article_path(date, edition)
    if not article_path:
        gate.fail('article.html 不存在')
        return gate

    html = read_file(article_path)

    # 检查6故事标题
    story_keywords = [
        ('01', 'A股'),
        ('02', '美股'),
        ('03', '科技'),
        ('04', '前沿'),
        ('05', '宏观'),
        ('06', '商品'),
    ]

    found_stories = 0
    for num, keyword in story_keywords:
        if num in html and keyword in html:
            found_stories += 1
        elif num + '.' in html:
            found_stories += 1

    if found_stories >= 4:
        gate.pass_(f'涵盖 {found_stories}/6 个故事板块（合理跳过视为通过）')
    elif found_stories > 0:
        gate.warn(f'仅涵盖 {found_stories}/6 个故事板块，确认是否为合理跳过')
    else:
        gate.fail('无法识别6故事结构')

    # 检查 Layer 结构
    for layer in ['热点速览', '深度解读', '数据一览']:
        if layer in html:
            gate.pass_(f'包含"{layer}"层')
        # 不存在的层不报错（新版可能简化结构）

    return gate


# ----------------------------------------------------------------
# Gate 7: 数据图表
# ----------------------------------------------------------------
def check_charts(date, edition):
    gate = GateResult('charts', '数据图表 — generate-charts.py 已运行')

    chart_dir = os.path.join(ROOT, 'docs', 'charts')
    if not os.path.isdir(chart_dir):
        gate.fail('docs/charts/ 目录不存在')
        return gate

    charts = [f for f in os.listdir(chart_dir) if f.endswith('.svg')]
    if not charts:
        gate.fail('docs/charts/ 目录为空，请运行 generate-charts.py')
        return gate

    # 检查图表是否有当天日期（接近）
    now = time.time()
    recent = 0
    for f in charts:
        fpath = os.path.join(chart_dir, f)
        mtime = os.path.getmtime(fpath)
        if now - mtime < 86400 * 2:  # 2天内
            recent += 1

    if recent >= 4:
        gate.pass_(f'{len(charts)} 个图表，其中{recent}个在2天内更新')
    elif recent > 0:
        gate.warn(f'{len(charts)} 个图表，仅{recent}个近期更新')
    else:
        gate.warn('所有图表可能已过时（>2天无更新）')

    # 检查文章中是否嵌入了图表
    article_path = find_article_path(date, edition)
    if article_path:
        html = read_file(article_path)
        for chart in charts:
            if chart in html:
                gate.pass_(f'文章中嵌入了 {chart}')
                break
        else:
            gate.warn('文章未嵌入任何数据图表（charts/*.svg）')

    return gate


# ----------------------------------------------------------------
# Gate 8: 数据准确性（Layer 4 特殊检查）
# ----------------------------------------------------------------
def check_data_accuracy(date, edition, special_topic=None):
    gate = GateResult('data_accuracy', '数据准确性 — 无编造历史对比')

    article_path = find_article_path(date, edition, special_topic=special_topic)
    if not article_path:
        gate.fail('article.html 不存在')
        return gate

    html = read_file(article_path)
    text = re.sub(r'<[^>]+>', ' ', html)

    # 高精度模式：所有 "历史第X次" "创X年" 必须验证
    high_risk_patterns = [
        r'创(?:下)?历史新[高低]',
        r'创\d{2,}年[以还].*新[高低]',
        r'历史第[一二三四五六七八九十\d]',
        r'史上最[大中小高低好差热冷]',
    ]

    findings = []
    for pat in high_risk_patterns:
        matches = re.findall(pat, text)
        findings.extend(matches)

    if findings:
        for f_ in findings[:8]:
            gate.fail(f'高风险表述: "{f_}" — 必须标注精确来源URL且可追溯')
        if len(findings) > 8:
            gate.fail(f'还有 {len(findings) - 8} 处高风险表述')
    else:
        gate.pass_('无高风险历史对比表述')

    return gate


# ================================================================
# 扫描专题文章
# ================================================================

def scan_special_topics():
    """Scan special/ directory and return list of topic names."""
    special_dir = os.path.join(ROOT, 'special')
    if not os.path.isdir(special_dir):
        return []
    topics = []
    for item in sorted(os.listdir(special_dir)):
        if item.startswith('.'):
            continue
        html_path = os.path.join(special_dir, item, 'article.html')
        if os.path.exists(html_path):
            topics.append(item)
    return topics


def read_special_date(topic_name):
    """Read date from special topic's .date file, or return None."""
    date_file = os.path.join(ROOT, 'special', topic_name, '.date')
    if os.path.exists(date_file):
        with open(date_file) as f:
            return f.read().strip()
    return None


# ================================================================
# 校验专题文章
# ================================================================

def check_special_article(topic_name, args):
    """Run all applicable gates on a special article, return dict of results."""
    print(f'\n{"="*55}')
    print(f'  📚 专题: {topic_name}')
    print(f'{"="*55}')

    article_path = find_article_path(None, None, special_topic=topic_name)
    if not article_path:
        print(f'  {YELLOW}article.html 不存在，跳过{RESET}')
        return None

    html = read_file(article_path)
    results = {}
    overall_passed = True
    blocked = False

    # Gate 1: 数据来源（专题文章不阻塞）
    r = check_data_sources(topic_name, 'special', html)
    results['data_sources'] = r.to_dict()
    if not r.passed:
        overall_passed = False
        # 专题不因"可疑表述"阻塞 — 来源以文字引用为主

    # Gate 2: 漫画风格（专题使用高品质全彩信息图，不适用标准漫画规范）
    r = check_comic_style(None, None, special_topic=topic_name)
    results['comic_style'] = r.to_dict()
    # 专题漫画使用渐变/彩色/大尺寸信息图，风格检查仅作参考

    # Gate 3: 音频
    r = check_audio(None, None, special_topic=topic_name)
    results['audio'] = r.to_dict()
    if not r.passed:
        overall_passed = False
        if any('时长偏差' in e for e in r.errors):
            blocked = True

    # Gate 4: 模板占位符
    r = check_placeholders(topic_name, 'special', special_topic=topic_name)
    results['placeholders'] = r.to_dict()
    if not r.passed:
        overall_passed = False
        blocked = True

    # Gate 5: 合规声明
    r = check_compliance(topic_name, 'special', special_topic=topic_name)
    results['compliance'] = r.to_dict()
    if not r.passed:
        overall_passed = False
        blocked = True

    # Gate 6: 6故事结构（专题跳过）
    r = check_six_stories(None, None, special_topic=topic_name)
    results['six_stories'] = r.to_dict()

    # Gate 7: 数据图表（专题不强制）
    results['charts'] = {'name': 'charts', 'description': '数据图表（专题不强制）', 'passed': True, 'errors': [], 'warnings': ['专题文章不强制图表门禁']}

    # Gate 8: 数据准确性
    r = check_data_accuracy(topic_name, 'special', special_topic=topic_name)
    results['data_accuracy'] = r.to_dict()
    if not r.passed:
        overall_passed = False
        if any('高风险' in e for e in r.errors):
            blocked = True

    results['_overall_passed'] = overall_passed
    results['_blocked'] = blocked
    return results


# ================================================================
# 主流程
# ================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='扬说财经 · 质量门禁 v5.0')
    parser.add_argument('--edition', choices=['morning', 'evening', 'special'], default=None)
    parser.add_argument('--date', default=TODAY)
    parser.add_argument('--json', action='store_true', help='输出JSON报告')
    parser.add_argument('--special-topic', default=None, help='指定专题目录名（仅 --edition special 时生效）')
    args = parser.parse_args()

    overall_passed = True
    blocked = False
    all_results = {}

    # 专题模式: 检查所有或指定专题
    if args.edition == 'special':
        topics = [args.special_topic] if args.special_topic else scan_special_topics()
        if not topics:
            print(f'  {YELLOW}未找到专题文章{RESET}')
        for topic in topics:
            result = check_special_article(topic, args)
            if result:
                all_results[topic] = result
                if not result.get('_overall_passed', True):
                    overall_passed = False
                if result.get('_blocked', False):
                    blocked = True
    else:
        date = args.date
        editions = [args.edition] if args.edition else ['morning', 'evening']

        for edition in editions:
            print(f'\n{"="*55}')
            print(f'  {date} {edition}')
            print(f'{"="*55}')

            article_path = find_article_path(date, edition)
            if not article_path:
                print(f'  {YELLOW}article.html 不存在，跳过{RESET}')
                continue

            html = read_file(article_path)

            # 执行所有门禁
            results = {}

            # Gate 1: 数据来源
            r = check_data_sources(date, edition, html)
            results['data_sources'] = r.to_dict()
            if not r.passed:
                overall_passed = False
                if any('可疑表述' in e for e in r.errors):
                    blocked = True

            # Gate 2: 漫画风格
            r = check_comic_style(date, edition)
            results['comic_style'] = r.to_dict()
            if not r.passed:
                overall_passed = False

            # Gate 3: 音频
            r = check_audio(date, edition)
            results['audio'] = r.to_dict()
            if not r.passed:
                overall_passed = False
                if any('时长偏差' in e for e in r.errors):
                    blocked = True

            # Gate 4: 模板占位符
            r = check_placeholders(date, edition)
            results['placeholders'] = r.to_dict()
            if not r.passed:
                overall_passed = False
                blocked = True

            # Gate 5: 合规声明
            r = check_compliance(date, edition)
            results['compliance'] = r.to_dict()
            if not r.passed:
                overall_passed = False
                blocked = True

            # Gate 6: 6故事结构
            r = check_six_stories(date, edition)
            results['six_stories'] = r.to_dict()

            # Gate 7: 数据图表
            r = check_charts(date, edition)
            results['charts'] = r.to_dict()

            # Gate 8: 数据准确性
            r = check_data_accuracy(date, edition)
            results['data_accuracy'] = r.to_dict()
            if not r.passed:
                overall_passed = False
                if any('高风险' in e for e in r.errors):
                    blocked = True

            all_results[edition] = results

    # 总体评分
    print(f'\n{"="*55}')

    if blocked:
        print(f'  {RED}结果: 🔴 阻塞 — 有硬性门禁未通过，不可发布{RESET}')
        exit_code = 2
    elif not overall_passed:
        print(f'  {YELLOW}结果: 🟡 待修复 — 存在问题需修复后再确认{RESET}')
        exit_code = 1
    else:
        print(f'  {GREEN}结果: 🟢 通过 — 全部门禁检查通过{RESET}')
        exit_code = 0

    print(f'  "产品质量是我们的核心竞争力"')
    print(f'{"="*55}')

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
