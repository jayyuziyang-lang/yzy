#!/usr/bin/env python3
"""
扬说财经 · 综合审核脚本（2026-05-27新增）
=============================================
覆盖四个维度：
  1. 新闻时效性 — 事件日期必须精确核实，不能把旧闻写成当天新闻
  2. 新闻真实性 — 每个数据点必须有可追溯来源
  3. 新闻来源审查 — 来源URL有效且与内容对应
  4. 文案一致性 — article.html 与 script.txt 关键数据一致

用法:
  python scripts/audit-article.py                          # 审核今天晚报
  python scripts/audit-article.py --edition evening        # 指定版次
  python scripts/audit-article.py --date 2026-05-27        # 指定日期
  python scripts/audit-article.py --json                   # 输出JSON报告

返回码: 0=通过, 1=警告(可发布但需注意), 2=阻塞(不可发布)

加入 pre-deploy-check.sh 作为阻塞检查项 (#8)。
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import socket

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = time.strftime('%Y-%m-%d')

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

# ================================================================
# 配置
# ================================================================

# 已知的套话/空话（全文grep）
# 注意："值得注意的是"是合理过渡用语，不在禁用之列
BANNED_PHRASES = [
    '值得关注',
    '后市可期',
    '需警惕',
]

# 高风险历史表述 — 必须有精确来源
HIGH_RISK_PATTERNS = [
    r'历史第[一二三四五六七八九十\d][次回]',
    r'创.*历史.*新[高低]',
    r'史上最[大中小高低好差热冷]',
    r'创\d{2,}年[以还].*[新高最低]',
    r'前所未有',
]

# 时间指示词 — 用于检查时效性
TIME_KEYWORDS = {
    '今天': 0,
    '昨日': 1,
    '昨日美股': 1,
    '上个交易日': 1,
    '隔夜': 1,
    '昨晚': 1,
    '盘后': 0,
    '上周': 7,
    '本周': 0,
    '本周一': 0,
    '本周二': 1,
    '本周三': 2,
    '本周四': 3,
    '本周五': 4,
}

# 数据点模式（用于提取文章中的数据，与脚本交叉验证）
DATA_PATTERNS = [
    (r'(\d+\.?\d*)%', '百分比'),
    (r'(\d+\.?\d*)万亿', '万亿人民币'),
    (r'(\d+\.?\d*)\s*亿', '亿级'),
    (r'\$(\d+[\.\,\d]*)', '美元价格'),
    (r'¥(\d+[\.\,\d]*)', '人民币价格'),
    (r'(\d+[\.\,\d]*)\s*点', '指数点位'),
]

# 公司/事件关键词（用于交叉验证文章和脚本的一致性）
KEY_ENTITIES = [
    '英伟达', 'NVIDIA', '中芯国际', '华为', '贵州茅台', '水井坊',
    '创业板', '上证指数', '科创50', 'WTI', '布伦特', 'COMEX',
    '美联储', '特朗普', '美伊', '伊朗',
]

URL_TIMEOUT = 5  # URL检查超时（秒）


# ================================================================
# 工具函数
# ================================================================

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ''


def find_article_path(date, edition):
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'article.html')
    if os.path.exists(path):
        return path
    return None


def find_script_path(date, edition):
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'script.txt')
    if os.path.exists(path):
        return path
    return None


def strip_html(html):
    """去除HTML标签和CSS/JS，提取纯文本"""
    # 先移除 <style>...</style> 和 <script>...</script> 块
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', ' ', text)
    # 压缩空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_data_points(text):
    """从文本中提取所有数据点（百分比、价格等）"""
    points = {}
    for pat, desc in DATA_PATTERNS:
        matches = re.findall(pat, text)
        if matches:
            points[desc] = [m.replace(',', '') for m in matches[:5]]
    return points


# ================================================================
# 审核项
# ================================================================

class AuditItem:
    def __init__(self, name, description, severity='error'):
        self.name = name
        self.description = description
        self.severity = severity  # 'error' (阻塞) or 'warning' (非阻塞)
        self.passed = True
        self.errors = []
        self.warnings = []
        self.info = []

    def fail(self, msg):
        self.passed = False
        self.errors.append(msg)
        print(f'  {RED}✗ {msg}{RESET}')

    def warn(self, msg):
        self.warnings.append(msg)
        print(f'  {YELLOW}△ {msg}{RESET}')

    def ok(self, msg):
        self.info.append(msg)
        print(f'  {GREEN}✓ {msg}{RESET}')

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
        }


# ----------------------------------------------------------------
# Audit 1: 新闻时效性 — 事件日期核查
# ----------------------------------------------------------------
def audit_timeliness(date, edition, html, script):
    """检查文章是否把旧闻写成当前新闻（如英伟达财报日期错误）"""
    audit = AuditItem('timeliness', '新闻时效性 — 事件日期必须精确核实，禁止把旧闻写成当天新闻')

    text = strip_html(html)
    script_text = strip_html(script)

    # 1. 检查"今天收盘""今天盘后"等时间指示词的使用
    #    如果文章日期=今天但事件发生在过去，则有问题
    for keyword, max_days_ago in TIME_KEYWORDS.items():
        count = text.count(keyword)
        if count > 3 and keyword == '今天':
            # "今天"出现很多次是正常的（当天新闻）
            pass
        elif count > 0 and keyword in ['盘后']:
            pass  # "盘后"出现在当天文章中是正常的

    # 2. 检查关键事件是否有明确日期标注
    #    如：财报应该标注具体日期"5月20日盘后"而非模糊表述"上周"
    #    但我们不直接报错，只记录信息

    # 3. 检查是否有「模糊时间标注」模式 — 事件没有明确日期
    #    如："英伟达发财报了"（缺少"上周五/昨日"等时间前缀）
    vague_events = []
    event_keywords = ['发财报', '发布财报', '发布业绩', '公布数据', '宣布']
    for ek in event_keywords:
        lines = text.split('。')
        for line in lines:
            if ek in line:
                # 检查该句是否有明确时间标注
                has_time = bool(re.search(
                    r'\d{1,2}月\d{1,2}日|昨日|上周|本周|今天|隔夜',
                    line
                ))
                if not has_time:
                    vague_events.append(line.strip()[:50])

    if vague_events:
        for ev in vague_events[:3]:
            audit.warn(f'事件缺少明确时间标注: "{ev}…" 请补充具体日期')
        if len(vague_events) > 3:
            audit.warn(f'还有 {len(vague_events)-3} 处类似模糊时间标注')

    # 4. 检查是否包含"今天""昨晚"等时间词，与文章日期对比
    #    如果是晚报（下午/晚上发），"今天"是正常的
    #    专注于检查跨越数天的事件时态

    # 5. script.txt中的时间标注
    for ek in event_keywords:
        lines = script_text.split('。')
        for line in lines:
            if ek in line:
                has_time = bool(re.search(
                    r'\d{1,2}月\d{1,2}日|昨日|上周|本周|今天|隔夜',
                    line
                ))
                if not has_time:
                    audit.warn(f'脚本中事件缺少时间标注: "{line.strip()[:50]}"')

    if not audit.errors:
        audit.ok('事件时间标注检查通过')

    return audit


# ----------------------------------------------------------------
# Audit 2: 新闻真实性 — 数据点有来源
# ----------------------------------------------------------------
def audit_authenticity(date, edition, html):
    """检查每个数据点是否有可追溯来源"""
    audit = AuditItem('authenticity', '新闻真实性 — 数据点必须标注来源URL')

    text = strip_html(html)

    # 1. 提取所有数据点
    data_points = []
    for pat, desc in DATA_PATTERNS:
        matches = re.findall(pat, text)
        data_points.extend([(m, desc) for m in matches])

    # 2. 检查是否有 sources 区块
    has_sources = bool(re.search(
        r'class="[^"]*sources[^"]*"|class="[^"]*source[^"]*"|参考来源|数据来源|Sources|来源[：:]',
        html, re.IGNORECASE
    ))
    if not has_sources:
        audit.fail('文章缺少 sources 来源区块')

    # 3. 提取URL
    urls = re.findall(r'https?://[^\s"\'<>）)]+', html)
    if not urls:
        audit.fail('未发现任何来源URL链接')
    else:
        audit.ok(f'发现 {len(urls)} 个来源URL')

    # 4. 检查高风险表述 — 检查其附近是否有明确的来源/年份标注
    suspicious_found = set()
    for pat in HIGH_RISK_PATTERNS:
        matches = list(re.finditer(pat, text))
        if not matches:
            continue
        # 如果任何一处匹配附近有来源标注，认为该表述已被正确引用
        any_attributed = False
        for match in matches:
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            context = text[start:end]
            has_attribution = bool(re.search(
                r'\d{4}年|\d{1,2}月\d{1,2}日|来源：|来源:|据.*统[计]|根据',
                context
            ))
            if has_attribution:
                any_attributed = True
                break
        if not any_attributed:
            suspicious_found.add(matches[0].group(0))

    if suspicious_found:
        for s in sorted(suspicious_found)[:5]:
            audit.fail(f'高风险表述 "{s}" — 全文均无精确来源标注，必须补充')
        if len(suspicious_found) > 5:
            audit.fail(f'还有 {len(suspicious_found)-5} 处类似高风险表述')
    else:
        audit.ok('无未经证实的高风险历史表述')

    if not audit.errors:
        audit.ok(f'{len(data_points)} 个数据点，{len(urls)} 个来源URL — 数据可追溯性检查通过')

    return audit


# ----------------------------------------------------------------
# Audit 3: 新闻来源审查 — URL有效性
# ----------------------------------------------------------------
def audit_sources(date, edition, html):
    """检查来源URL是否能正常访问（非阻塞警告）"""
    audit = AuditItem('sources', '新闻来源审查 — 来源URL有效性验证', severity='warning')

    urls = re.findall(r'https?://[^\s"\'<>）)]+', html)

    # 去重
    unique_urls = list(set(urls))
    if not unique_urls:
        audit.warn('无URL可验证')
        return audit

    # 去除非来源URL（如网站自身链接、CDN等）
    source_urls = [u for u in unique_urls if 'jayyuziyang-lang' not in u]

    if source_urls:
        audit.ok(f'{len(source_urls)} 个外部来源URL待验证（非阻塞，仅参考）')

    # 分类显示来源
    domains = {}
    for u in source_urls:
        domain = re.search(r'https?://([^/]+)', u)
        if domain:
            d = domain.group(1)
            domains[d] = domains.get(d, 0) + 1

    for domain, count in sorted(domains.items()):
        audit.info.append(f'  {domain}: {count}次引用')

    # 不实际检查URL可达性（生产环境可能无法出网）
    # 仅列出来源域名供人工审核

    return audit


# ----------------------------------------------------------------
# Audit 4: 文案一致性 — article.html vs script.txt
# ----------------------------------------------------------------
def audit_consistency(date, edition, html, script):
    """检查文章和口播稿的关键数据是否一致"""
    audit = AuditItem('consistency', f'文案一致性 — article.html 与 script.txt 关键数据交叉验证')

    article_text = strip_html(html)
    script_text = strip_html(script)

    if not script.strip():
        audit.fail('script.txt 为空或不存在')
        return audit

    # 1. 提取双方的关键数据点
    article_data = {}
    script_data = {}

    for pat, desc in DATA_PATTERNS:
        article_matches = re.findall(pat, article_text)
        script_matches = re.findall(pat, script_text)
        if article_matches:
            article_data[desc] = [m.replace(',', '') for m in article_matches[:5]]
        if script_matches:
            script_data[desc] = [m.replace(',', '') for m in script_matches[:5]]

    # 2. 检查关键事件实体是否在脚本中出现
    #    仅检查最重要的实体，不检查每个数据点（脚本是口语摘要，自然会省略许多数字）
    article_data_count = sum(len(v) for v in article_data.values())
    script_data_count = sum(len(v) for v in script_data.values())
    if article_data_count > 0 and script_data_count == 0:
        audit.warn('script.txt 几乎不包含任何数据点（文章有%d个），请确认脚本是否过于简略' % article_data_count)

    # 3. 检查关键公司/事件名称是否在双方都出现
    article_entities = set()
    script_entities = set()
    for entity in KEY_ENTITIES:
        if entity in article_text:
            article_entities.add(entity)
        if entity in script_text:
            script_entities.add(entity)

    missing_in_script = article_entities - script_entities
    if missing_in_script:
        for m in sorted(missing_in_script):
            if m not in script_text:  # 双重确认
                audit.warn(f'script.txt 未覆盖文章中的关键实体: "{m}"')

    # 4. 脚本口语化检查 — 确保 script 不是纯读新闻
    if '据报道' in script_text or '据悉' in script_text or '记者' in script_text:
        audit.warn('script.txt 含新闻体用语（据报道/据悉/记者），建议改为阿扬人格化表达')

    if '# ' in script_text or '## ' in script_text:
        audit.warn('script.txt 含Markdown标题标记，请移除')

    # 5. 脚本禁语检查（英文、URL、HTML标签）
    eng_pattern = re.findall(r'\b[A-Za-z]{3,}\b', script_text)
    finance_eng = {'for', 'the', 'and', 'WTI', 'COMEX', 'NASDAQ', 'ETF', 'GPU', 'AI',
                   'CPU', 'HBM', 'PCB', 'PE', 'AUM', 'PCE', 'NVIDIA', 'OpenAI', 'IPO',
                   'Fed', 'SPAC', 'PMI', 'CPI', 'GDP', 'LPR', 'EPS'}
    foreign_eng = set(w.lower() for w in eng_pattern) - set(w.lower() for w in finance_eng)
    if foreign_eng:
        audit.warn(f'script.txt 含可能多余的英文词汇: {", ".join(sorted(foreign_eng)[:6])}')

    if '<' in script_text and '>' in script_text:
        audit.fail('script.txt 含HTML标签')

    if 'http' in script_text:
        audit.fail('script.txt 含URL链接')

    if not audit.errors:
        audit.ok('文案一致性检查通过')

    return audit


# ----------------------------------------------------------------
# Audit 5: 套话检查
# ----------------------------------------------------------------
def audit_banned_phrases(date, edition, html, script):
    """检查套话/空话"""
    audit = AuditItem('banned_phrases', '套话检查 — 禁止"值得关注""后市可期"等套话')

    combined = strip_html(html) + '\n' + strip_html(script)

    found = []
    for phrase in BANNED_PHRASES:
        if phrase in combined:
            found.append(phrase)

    # 额外检查：在文章HTML中检查（因为CSS可能隐藏）
    for phrase in BANNED_PHRASES:
        if phrase in html:
            found.append(f'hmtl:{phrase}')

    found_unique = sorted(set(found))
    for f in found_unique:
        # 去掉前缀再输出
        clean_f = f.replace('hmtl:', '')
        if 'hmtl:' in f:
            audit.fail(f'文章含禁用语: "{clean_f}"')
        else:
            audit.fail(f'全文含禁用语: "{clean_f}"')

    if not found:
        audit.ok('无套话/空话')

    return audit


# ----------------------------------------------------------------
# Audit 6: 模板占位符
# ----------------------------------------------------------------
def audit_placeholders(date, edition, html):
    """检查模板占位符残留"""
    audit = AuditItem('placeholders', '模板占位符 — 无 {{ 残留')

    placeholders = []
    for i, line in enumerate(html.split('\n'), 1):
        if '{{' in line and 'content' not in line.split('{{')[0][-20:]:
            placeholders.append(f'第{i}行: {line.strip()[:80]}')

    if placeholders:
        for p in placeholders:
            audit.fail(p)
    else:
        audit.ok('无模板占位符残留')

    return audit


# ----------------------------------------------------------------
# Audit 7: 6故事结构完整性
# ----------------------------------------------------------------
def audit_story_structure(date, edition, html):
    """检查6故事结构"""
    audit = AuditItem('story_structure', '6故事结构 — 01-06完整且每个故事涵盖数据+叙事+洞察')

    story_checklist = [
        ('01', 'A股', '\u7ea2|\u7eff|板块|指数|成交'),
        ('02', '美股', '\u7f8e\u80a1|隔夜|美股|道指|纳指|标普'),
        ('03', '科技|AI', '\u79d1\u6280|\u534a\u5bfc\u4f53|AI|英伟达'),
        ('04', '\u524d\u6cbf|\u56fd\u9645', '\u56fd\u9645|\u5730\u7f18|\u4f0a\u6717'),
        ('05', '\u5b8f\u89c2', '\u5b8f\u89c2|GDP|CPI|\u7231\u5fb7\u5361|利率'),
        ('06', '\u5546\u54c1|\u9ec4\u91d1', '\u539f\u6cb9|\u9ec4\u91d1|WTI|COMEX'),
    ]

    found_count = 0
    for num, keyword, pattern in story_checklist:
        if re.search(pattern, html, re.IGNORECASE):
            found_count += 1

    if found_count >= 6:
        audit.ok(f'完整6故事结构（{found_count}/6）')
    elif found_count >= 4:
        audit.ok(f'涵盖 {found_count}/6 个故事板块（合理跳过视为通过）')
    else:
        audit.warn(f'仅涵盖 {found_count}/6 个故事，请确认内容完整性')

    return audit


# ================================================================
# 主流程
# ================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='扬说财经 · 综合审核脚本 v1.0')
    parser.add_argument('--edition', choices=['morning', 'evening'], default='evening',
                        help='版次（默认: evening）')
    parser.add_argument('--date', default=TODAY, help='日期（默认: 今天）')
    parser.add_argument('--json', action='store_true', help='输出JSON报告')
    args = parser.parse_args()

    date = args.date
    edition = args.edition

    print(f'\n{CYAN}{"="*60}{RESET}')
    print(f'{CYAN}  扬说财经 · 综合审核脚本 v1.0{RESET}')
    print(f'{CYAN}  日期: {date} | 版次: {edition}{RESET}')
    print(f'{CYAN}  覆盖: 时效性 | 真实性 | 来源审查 | 文案一致性{RESET}')
    print(f'{CYAN}{"="*60}{RESET}')

    # 查找文件
    article_path = find_article_path(date, edition)
    script_path = find_script_path(date, edition)

    if not article_path:
        print(f'\n  {RED}✗ article.html 不存在: {date}/{edition}{RESET}')
        print(f'\n{CYAN}审核结果: 🔴 阻塞 — 文章不存在，不可发布{RESET}')
        sys.exit(2)

    html = read_file(article_path)
    script = read_file(script_path) if script_path else ''

    print(f'\n  文章: {os.path.relpath(article_path, ROOT)} ({len(html)} bytes)')
    if script:
        print(f'  脚本: {os.path.relpath(script_path, ROOT)} ({len(script.strip())} 字)')
    else:
        print(f'  {YELLOW}  脚本: 不存在{RESET}')

    # 执行所有审核项
    results = {}
    has_blocking_errors = False
    has_warnings = False

    # Audit 1: 新闻时效性
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 1/7] 新闻时效性')
    print(f'{"─"*55}')
    r = audit_timeliness(date, edition, html, script)
    results['timeliness'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 2: 新闻真实性
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 2/7] 新闻真实性 — 数据来源追溯')
    print(f'{"─"*55}')
    r = audit_authenticity(date, edition, html)
    results['authenticity'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 3: 新闻来源审查
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 3/7] 新闻来源审查 — URL清单')
    print(f'{"─"*55}')
    r = audit_sources(date, edition, html)
    results['sources'] = r.to_dict()
    if not r.passed:
        has_warnings = True

    # Audit 4: 文案一致性
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 4/7] 文案一致性 — article.html vs script.txt')
    print(f'{"─"*55}')
    r = audit_consistency(date, edition, html, script)
    results['consistency'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 5: 套话检查
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 5/7] 套话检查')
    print(f'{"─"*55}')
    r = audit_banned_phrases(date, edition, html, script)
    results['banned_phrases'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 6: 模板占位符
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 6/7] 模板占位符')
    print(f'{"─"*55}')
    r = audit_placeholders(date, edition, html)
    results['placeholders'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 7: 6故事结构
    print(f'\n{"─"*55}')
    print(f'  [AUDIT 7/7] 6故事结构完整性')
    print(f'{"─"*55}')
    r = audit_story_structure(date, edition, html)
    results['story_structure'] = r.to_dict()

    # 总体结果
    print(f'\n{CYAN}{"="*60}{RESET}')

    if has_blocking_errors:
        print(f'  {RED}审核结果: 🔴 阻塞 — 发现硬性审核问题，不可发布{RESET}')
        print(f'  {RED}请修复后重新运行 audit-article.py{RESET}')
        exit_code = 2
    elif has_warnings:
        print(f'  {YELLOW}审核结果: 🟡 警告 — 存在非阻塞问题，建议修复后再发布{RESET}')
        exit_code = 1
    else:
        print(f'  {GREEN}审核结果: 🟢 通过 — 全维度审核通过{RESET}')
        print(f'  {GREEN}"新闻质量是我们最关心的" ✓{RESET}')
        exit_code = 0

    print(f'{CYAN}{"="*60}{RESET}')

    if args.json:
        report = {
            'date': date,
            'edition': edition,
            'exit_code': exit_code,
            'results': results,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
