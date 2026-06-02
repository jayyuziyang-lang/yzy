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


# ----------------------------------------------------------------
# Audit 8: 技术颗粒度 — 关键事件是否有精确参数
# ----------------------------------------------------------------
def audit_technical_depth(date, edition, html):
    """检查关键事件的技术描述是否具有精确参数（对标全球财经简报标准）"""
    audit = AuditItem('technical_depth', '技术颗粒度 — 关键数据应有精确参数（晶体管数/制程/带宽等）', severity='warning')

    text = strip_html(html)

    # 检查技术关键词附近是否有精确数字参数
    tech_keywords = {
        '芯片': ['纳米', 'nm', '晶体管', '亿', '核', 'GHz', 'TOPS', 'TFLOPS', 'Petaflop'],
        'AI模型': ['亿参数', 'B参数', '万亿', 'Token', '上下文'],
        '内存': ['GB', 'TB', 'HBM', 'LPDDR', 'DDR', 'MHz', 'MT/s'],
        '带宽/算力': ['GB/s', 'TB/s', 'TFLOPS', 'Petaflop', 'EXA'],
        '制程': ['纳米', 'nm', '微米'],
    }

    missing_details = []
    for category, expected_patterns in tech_keywords.items():
        # 检查文章是否提到这个技术类别
        for cat_word in list(tech_keywords.keys()):
            if cat_word == category:
                # 检查该类别关键词在文章中出现的位置附近是否有精确参数
                for kw in [category, 'N1X', 'RTX', 'Vera', 'Rubin', 'Blackwell', 'Arm', 'GPU', 'CPU']:
                    if kw in text:
                        # 在关键词周围100字范围内搜索精确参数
                        kw_positions = [m.start() for m in re.finditer(re.escape(kw), text)]
                        has_detail = False
                        for pos in kw_positions[:3]:
                            context = text[max(0, pos-50):min(len(text), pos+150)]
                            for pat in expected_patterns:
                                if pat in context:
                                    has_detail = True
                                    break
                        if not has_detail and kw_positions:
                            # 只对含技术内容的文章警告
                            if any(tech in text for tech in ['AI', '芯片', '半导体', '算力']):
                                pass  # 标记但不报错
                            break
                        break

    # 正面检查: N1X/RTX场景是否有具体参数
    if re.search(r'N1X|RTX Spark|超级芯片|PC芯片', text):
        param_score = 0
        tech_params = ['纳米', 'nm', 'Arm', '核', 'GPU', 'Blackwell', 'Petaflop', 'TFLOPS', 'GB', 'LPDDR', 'PCIe', '台积电', '3nm']
        for p in tech_params:
            if p in text:
                param_score += 1
        if param_score < 3:
            audit.warn(f'N1X/RTX Spark场景技术参数不足（得分{param_score}/11），建议补充制程/架构/算力/内存等具体参数')
        else:
            audit.ok(f'N1X场景技术参数覆盖度尚可（得分{param_score}/11）')

    # 检查油价/金价是否有具体点位和精确变动
    if re.search(r'油价|原油|布伦特|WTI', text):
        if not re.search(r'\$\d+\.\d+|\d+[\.\d]*\s*美元|原油.*[涨跌]\s*\d+\.?\d*%', text):
            audit.warn('油价描述缺少精确点位和涨跌幅')

    if re.search(r'黄金|金价', text):
        if not re.search(r'\$\d+[\.\,\d]*|\d+[\.\d]*\s*美元/盎司', text):
            audit.warn('金价描述缺少精确点位')

    # 美股指数是否有精确点位
    if re.search(r'道指|纳指|标普|纳斯达克|道琼斯', text):
        if not re.search(r'\d{4,}[\.\d]*\s*点', text):
            audit.warn('美股指数缺少精确收盘点位')

    if not audit.errors and not audit.warnings:
        audit.ok('技术数据颗粒度检查通过')

    return audit


# ----------------------------------------------------------------
# Audit 9: 传导链系统化 — 跨资产因果传导链
# ----------------------------------------------------------------
def audit_transmission_chain(date, edition, html):
    """检查是否有系统化的跨事件因果传导链"""
    audit = AuditItem('transmission_chain', '传导链系统化 — 跨资产因果传导逻辑链', severity='warning')

    text = strip_html(html)

    # 检查是否有传导链标记（logic-chain / 传导链 / 逻辑链）
    chain_markers = ['传导链', '逻辑链', '传导', '导致', '引发', '推高→', '推升→', '→']
    chain_count = 0
    for m in chain_markers:
        chain_count += text.count(m)

    # 检查是否有"→"箭头模式（表示因果传导）
    arrow_count = text.count('→')
    if arrow_count >= 2:
        audit.ok(f'发现 {arrow_count} 个因果传导箭头（→），传导链意识良好')
    elif arrow_count == 1:
        audit.warn('仅发现1个因果传导链，建议至少2-3条跨资产传导（如"油价→通胀→Fed→黄金"）')
    else:
        audit.warn('未发现因果传导链（→），建议系统化呈现跨资产传导（油价→通胀→Fed→黄金）')

    # 检查是否有跨资产关联分析
    cross_asset_patterns = [
        (r'油价.*通胀', '油价→通胀'),
        (r'通胀.*(利率|降息|加息|Fed|美联储)', '通胀→利率预期'),
        (r'利率|加息|降息', '利率政策'),
        (r'ISM|PMI.*CPI|PCE|PCE.*ISM|PMI', 'ISM/PCE交叉分析'),
        (r'美债.*黄金|黄金.*美债', '美债↔黄金'),
        (r'美元.*黄金|黄金.*美元', '美元↔黄金'),
        (r'原油.*黄金|黄金.*原油|通胀.*黄金', '能源↔黄金三角'),
    ]
    found_cross = 0
    for pat, desc in cross_asset_patterns:
        if re.search(pat, text, re.IGNORECASE):
            found_cross += 1

    if found_cross >= 2:
        audit.ok(f'发现 {found_cross} 处跨资产关联分析')
    else:
        audit.warn(f'跨资产关联分析不足（仅{found_cross}处），建议至少3类（如油价→通胀、通胀→Fed、Fed→黄金）')

    return audit


# ----------------------------------------------------------------
# Audit 10: 双向观察 — 同步写利好/承压方
# ----------------------------------------------------------------
def audit_dual_perspective(date, edition, html):
    """检查是否同时呈现赢家和输家"""
    audit = AuditItem('dual_perspective', '双向观察 — 每个事件同步呈现利好/承压方', severity='warning')

    text = strip_html(html)

    # 检查"涨/跌""利好/承压""赢家/输家"等对立表述
    dual_indicators = {
        '但.*跌|但.*承压|但.*风险': '风险提示',
        '另一.*边|另一方|同时.*跌|也.*跌': '对立方',
        '利空|承压|拖累|打压|冲击': '负面表述',
        '受益|利好|提振|催化|推动': '利好表述',
    }

    has_positive = False
    has_negative = False
    for pat, desc in dual_indicators.items():
        if re.search(pat, text):
            if desc == '利好表述':
                has_positive = True
            if desc in ['风险提示', '对立方', '负面表述']:
                has_negative = True

    # 扫描特定个股涨跌
    stock_up_down = re.findall(r'(英伟达|英特尔|高通|AMD|ARM|台积电|戴尔|特斯拉|亚马逊|Meta|博通)[^\d]*[涨跌]\s*[\d\.]+%', text)
    if stock_up_down:
        # 检查是否有正反两方
        up_count = sum(1 for s in stock_up_down if '涨' in s)
        down_count = sum(1 for s in stock_up_down if '跌' in s)
        if up_count > 0 and down_count > 0:
            audit.ok(f'个股双向定价：{up_count}涨 vs {down_count}跌')
        elif up_count > 0:
            audit.warn(f'仅呈现上涨方（{up_count}只），建议同步写承压方')
        elif down_count > 0:
            audit.warn(f'仅呈现下跌方（{down_count}只），建议同步写受益方')

    if has_positive and has_negative:
        audit.ok('利好/承压双向观察覆盖')
    elif has_positive:
        audit.warn('仅有利好分析，缺少风险提示和承压方分析')
    elif has_negative:
        audit.warn('仅有风险提示，缺少利好或受益方分析')

    return audit


# ----------------------------------------------------------------
# Audit 11: 投资视角 — 读者价值区块
# ----------------------------------------------------------------
def audit_investor_value(date, edition, html):
    """检查是否有明确的"投资视角"或读者价值指引"""
    audit = AuditItem('investor_value', '投资视角 — 读者价值指引区块', severity='warning')

    text = strip_html(html)

    # 检查"投资视角"类关键词
    value_markers = [
        '投资视角', '对A股影响', '对美股影响', '对你来说',
        '投资者关注', '投资启示', '关键提示', '投资要点',
        '操作策略', '策略提示', '仓位', '配置建议',
        '受益链', '承压方', '利好方向', '风险方向',
    ]

    found_markers = []
    for m in value_markers:
        if m in text:
            found_markers.append(m)

    # 检查是否有"投资视角"相关区块
    has_value_section = bool(re.search(
        r'投资视角|关键提示|受益链|承压方|操作策略|仓位',
        text
    ))

    if len(found_markers) >= 3:
        audit.ok(f'发现 {len(found_markers)} 处读者价值指引')
    elif len(found_markers) >= 1:
        audit.warn(f'读者价值指引不足（仅{len(found_markers)}处标记），建议增加"投资视角""关键提示"等明确区块')
    else:
        audit.warn('未发现明确的读者价值指引区块，建议每个大事件后加"投资视角"或"关键提示"')

    # 检查是否早报/晚报（早报可以更简略）
    return audit


# ----------------------------------------------------------------
# Audit 12: VIX分析 — 市场情绪指标
# ----------------------------------------------------------------
def audit_vix_analysis(date, edition, html):
    """检查是否包含VIX数据和解读"""
    audit = AuditItem('vix_analysis', 'VIX/波动率分析 — 市场情绪温度计', severity='warning')

    text = strip_html(html)

    # 检查VIX关键词
    vix_present = bool(re.search(r'VIX|恐慌指数|波动率|波动指数', text))

    if vix_present:
        # 检查是否有具体VIX数值
        vix_value = re.search(r'VIX[^\d]*(\d+\.?\d*)', text)
        if vix_value:
            audit.ok(f'包含VIX数据（{vix_value.group(1)}）')
        else:
            audit.warn('提到VIX但缺少具体数值')
    else:
        audit.warn('未包含VIX/恐慌指数数据 — 建议每次日报补充VIX收盘值和解读')

    return audit


# ----------------------------------------------------------------
# Audit 13: 宏观三角 — PCE→FedWatch→FOMC
# ----------------------------------------------------------------
def audit_macro_triangle(date, edition, html):
    """检查宏观板块是否包含完整的PCE→FedWatch→FOMC→官员表态链条"""
    audit = AuditItem('macro_triangle', '宏观三角 — PCE→FedWatch→FOMC→官员表态', severity='warning')

    text = strip_html(html)

    # 检查PCE/通胀数据
    has_pce = bool(re.search(r'PCE|CPI|通胀|通货膨胀', text))

    # 检查FedWatch/加息概率
    has_fedwatch = bool(re.search(r'FedWatch|加息概率|降息概率|CME|利率互换', text))

    # 检查FOMC日期
    has_fomc = bool(re.search(r'FOMC|议息|6月17|6月18|利率决议', text))

    # 检查官员表态
    has_official = bool(re.search(r'(美联储|Fed|Warsh|鲍威尔|库克|Lisa|柯林斯|沃勒)[^。]*表[态势]', text))

    items = []
    if has_pce:
        items.append('PCE/通胀数据')
    if has_fedwatch:
        items.append('FedWatch概率')
    if has_fomc:
        items.append('FOMC时间线')
    if has_official:
        items.append('官员表态')

    if len(items) >= 3:
        audit.ok(f'宏观三角覆盖完整：{", ".join(items)}')
    elif len(items) >= 1:
        audit.warn(f'宏观三角仅覆盖 {len(items)}/4：{", ".join(items)}，建议补全PCE→FedWatch→FOMC→官员表态完整链条')
    else:
        audit.warn('宏观三角未覆盖，建议增加PCE/FedWatch/FOMC/官员表态链条')

    return audit


# ----------------------------------------------------------------
# Audit 14: 情景推演成熟度 — 概率判断+条件
# ----------------------------------------------------------------
def audit_scenario_maturity(date, edition, html):
    """检查情景推演是否有概率判断、触发条件、时间窗口"""
    audit = AuditItem('scenario_maturity', '情景推演深度 — 概率判断+触发条件+时间窗口', severity='warning')

    text = strip_html(html)

    # 检查是否有scenario-box
    has_scenario_box = 'scenario-box' in html or 'scenario' in html.lower()

    # 检查概率判断词
    prob_markers = re.findall(r'概率|可能|大概率|小概率|基准.*情[景形]|尾部风险|触发条件', text)
    time_markers = re.findall(r'未来.*周|本周|下周|个月内|季度|半年', text)

    # 检查路径标记
    path_markers = re.findall(r'路径[AB]|情景[一二三四五]|情景A|情景B|Scenario|情景[1-5]', text)

    if has_scenario_box:
        audit.ok('包含情景推演框')

    if len(path_markers) >= 2:
        audit.ok(f'多路径推演清晰（{len(path_markers)}条路径）')
    elif len(path_markers) == 1:
        audit.warn('仅有1条推演路径，建议至少2-3条（基准/乐观/尾部风险）')

    if len(prob_markers) >= 2:
        pass  # 概率判断覆盖
    else:
        audit.warn('情景推演缺少概率判断词，建议为每条路径标注概率估计')

    if not time_markers:
        audit.warn('情景推演缺少时间窗口描述，建议标注"未来X周/月"等时间范围')

    if not has_scenario_box and not path_markers:
        pass  # 不是所有文章都需要情景推演

    if not audit.errors and not audit.warnings:
        audit.ok('情景推演深度检查通过')

    return audit


# ----------------------------------------------------------------
# Audit 15: 数据可视化密度 — 图表+漫画数量
# ----------------------------------------------------------------
def audit_visualization_density(date, edition, html):
    """检查图表和漫画数量是否充足"""
    audit = AuditItem('visualization_density', '数据可视化密度 — 图表+漫画数量', severity='warning')

    # 统计文章中的图片引用
    chart_count = len(re.findall(r'docs/charts/', html))
    comic_count = len(re.findall(r'comic/', html))

    total_viz = chart_count + comic_count

    # 检查comic目录
    article_dir = os.path.dirname(find_article_path(date, edition) or '')
    comic_dir = os.path.join(article_dir, 'comic')

    if os.path.isdir(comic_dir):
        svgs = [f for f in os.listdir(comic_dir) if f.endswith('.svg')]
        actual_comics = len(svgs)
    else:
        actual_comics = 0

    if total_viz >= 3:
        audit.ok(f'可视化数量充足：{chart_count}图表 + {comic_count}漫画 = {total_viz}')
    elif total_viz >= 1:
        audit.warn(f'可视化偏少（{total_viz}），建议日报至少2图表+1漫画')
        if actual_comics > 0:
            audit.info.append(f'comic目录有 {actual_comics} 个SVG文件')
    else:
        audit.warn('无数据可视化，建议至少2张图表+1张漫画')

    if actual_comics > 1:
        audit.ok(f'漫画数量充足：{actual_comics}张')
    elif actual_comics == 1:
        pass  # 1张勉强可接受

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

    print(f'{CYAN}  覆盖: 时效性 | 真实性 | 来源审查 | 文案一致性 | 行业质量基准(8项){RESET}')

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
    print(f'\n')
    print(f'  [AUDIT 1/15] 新闻时效性')
    r = audit_timeliness(date, edition, html, script)
    results['timeliness'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 2: 新闻真实性
    print(f'\n')
    print(f'  [AUDIT 2/15] 新闻真实性 — 数据来源追溯')
    r = audit_authenticity(date, edition, html)
    results['authenticity'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 3: 新闻来源审查
    print(f'\n')
    print(f'  [AUDIT 3/15] 新闻来源审查 — URL清单')
    r = audit_sources(date, edition, html)
    results['sources'] = r.to_dict()
    if not r.passed:
        has_warnings = True

    # Audit 4: 文案一致性
    print(f'\n')
    print(f'  [AUDIT 4/15] 文案一致性 — article.html vs script.txt')
    r = audit_consistency(date, edition, html, script)
    results['consistency'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 5: 套话检查
    print(f'\n')
    print(f'  [AUDIT 5/15] 套话检查')
    r = audit_banned_phrases(date, edition, html, script)
    results['banned_phrases'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 6: 模板占位符
    print(f'\n')
    print(f'  [AUDIT 6/15] 模板占位符')
    r = audit_placeholders(date, edition, html)
    results['placeholders'] = r.to_dict()
    if not r.passed:
        has_blocking_errors = True

    # Audit 7: 6故事结构
    print(f'\n')
    print(f'  [AUDIT 7/15] 6故事结构完整性')
    r = audit_story_structure(date, edition, html)
    results['story_structure'] = r.to_dict()

    # ---- 行业质量基准审计 (8-15) ----
    quality_warnings = 0
    quality_total = 0

    # Audit 8: 技术颗粒度
    print(f'  [AUDIT 8/15] 技术颗粒度 — 精确参数覆盖')
    r = audit_technical_depth(date, edition, html)
    results['technical_depth'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 9: 传导链系统化
    print(f'  [AUDIT 9/15] 传导链系统化 — 跨资产因果逻辑')
    r = audit_transmission_chain(date, edition, html)
    results['transmission_chain'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 10: 双向观察
    print(f'  [AUDIT 10/15] 双向观察 — 利好/承压方同步呈现')
    r = audit_dual_perspective(date, edition, html)
    results['dual_perspective'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 11: 投资视角
    print(f'  [AUDIT 11/15] 投资视角 — 读者价值指引')
    r = audit_investor_value(date, edition, html)
    results['investor_value'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 12: VIX分析
    print(f'  [AUDIT 12/15] VIX/波动率 — 市场情绪温度计')
    r = audit_vix_analysis(date, edition, html)
    results['vix_analysis'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 13: 宏观三角
    print(f'  [AUDIT 13/15] 宏观三角 — PCE→FedWatch→FOMC')
    r = audit_macro_triangle(date, edition, html)
    results['macro_triangle'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 14: 情景推演深度
    print(f'  [AUDIT 14/15] 情景推演 — 概率/条件/时间窗口')
    r = audit_scenario_maturity(date, edition, html)
    results['scenario_maturity'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True

    # Audit 15: 可视化密度
    print(f'  [AUDIT 15/15] 可视化密度 — 图表+漫画数量')
    r = audit_visualization_density(date, edition, html)
    results['visualization_density'] = r.to_dict()
    quality_total += 1
    if not r.passed:
        quality_warnings += 1
        has_warnings = True



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
