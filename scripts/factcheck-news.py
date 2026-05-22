#!/usr/bin/env python3
"""
扬说财经 · 事实核查 Agent

功能：
  1. 扫描文章HTML，提取所有数据点（百分比、价格、历史对比等）
  2. 对每个数据点标注来源要求
  3. 标记可疑的"历史第X次"类无法验证的表述
  4. 生成结构化的事实核查报告

用法：
  python scripts/factcheck-news.py                          # 核查今天的文章
  python scripts/factcheck-news.py --edition morning         # 只核查早报
  python scripts/factcheck-news.py --date 2026-05-22         # 核查指定日期
  python scripts/factcheck-news.py --check-script            # 也核查口播稿
"""

import argparse
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = time.strftime('%Y-%m-%d')

# 已知的"无法独立验证"模式 — 这些需要标注
# 注意：中文中\b边界不适用，使用纯文本匹配
SUSPICIOUS_PATTERNS = [
    r'历史第[一二三四五六七八九十\d][次回]',
    r'A股历史上[只仅]有',
    r'(?<!\w)史(上|无前例|诗级)',
    r'前所未有',
    r'惊天|狂跌|狂涨',  # 情绪化用语
]

# 已确认的客观事实（不标记）
KNOWN_FACTS = [
    '创下收盘历史新高',  # 道指50285点是已报道的事实
]

# 需要来源的数值模式
DATA_PATTERNS = [
    (r'\d+\.?\d*%', '百分比变化'),           # 涨跌幅
    (r'\d+\.?\d*万亿', '万亿级数字'),          # 成交额等
    (r'\d+\.?\d*亿', '亿级数字'),
    (r'\$\d+[\.\,\d]*', '美元价格'),           # 价格
    (r'¥\d+[\.\,\d]*', '人民币价格'),
    (r'\d+[\.\,\d]*点', '指数点位'),
    (r'\d+[\.\,\d]*[bpBP]{2}', '基点'),
]


def parse_args():
    parser = argparse.ArgumentParser(description='扬说财经 · 事实核查 Agent')
    parser.add_argument('--edition', choices=['morning', 'evening'], default=None,
                        help='版次 (默认：早报+晚报都查)')
    parser.add_argument('--date', default=TODAY, help='日期 (YYYY-MM-DD)')
    parser.add_argument('--check-script', action='store_true', help='同时核查口播稿')
    parser.add_argument('--output', action='store_true', help='输出报告到文件')
    return parser.parse_args()


def find_article_path(date, edition):
    """查找 article.html 路径"""
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'article.html')
    if os.path.exists(path):
        return path
    return None


def find_script_path(date, edition):
    path = os.path.join(ROOT, date, 'wechat-publish', edition, 'script.txt')
    if os.path.exists(path):
        return path
    return None


def check_data_points(text, source_label):
    """提取并标记所有数据点"""
    findings = []
    for pattern, desc in DATA_PATTERNS:
        matches = re.findall(pattern, text)
        for m in set(matches):
            findings.append({
                'value': m,
                'type': desc,
                'source': source_label,
            })
    return findings


def check_suspicious(text, source_label):
    """检查可疑/无法验证的表述"""
    flags = []
    for pattern in SUSPICIOUS_PATTERNS:
        matches = re.findall(pattern, text)
        for m in set(matches):
            # 跳过已确认的客观事实
            m_clean = m.strip()
            if any(fact in m_clean for fact in KNOWN_FACTS):
                continue
            flags.append({
                'text': m_clean,
                'issue': '无法独立验证的表述，需要标注来源',
                'source': source_label,
            })
    return flags


def check_english_terms(text, source_label):
    """检查英文术语是否标注中文"""
    # 常见知名公司/术语不需要中文标注
    ALLOWED = {
        'A股', 'B股', 'H股', 'IPO', 'ETF', 'GDP', 'CPI', 'PMI',
        'AI', 'GPU', 'CPU', 'HBM', 'PCB', 'PE', 'PB', 'ROE', 'ROA',
        'CEO', 'CFO', 'YoY', 'QoQ', 'OTC', 'NASDAQ', 'NYSE', 'COMEX',
        'WTI', 'Brent', 'VIX', 'TMT', 'IBM', 'ARM', 'D-Wave',
    }
    # CSS/HTML相关词汇 — 忽略
    CSS_TERMS = {
        'SC', 'Neue', 'YaHei', 'PingFang', 'Microsoft', 'Helvetica',
        'Layer', 'src', 'href', 'class', 'style', 'div', 'img', 'svg',
        'span', 'th', 'td', 'tr', 'li', 'ul', 'ol', 'br', 'hr', 'h1', 'h2', 'h3',
        'auto', 'min', 'max', 'repeat', 'fit', 'content', 'stretch',
        'sans', 'serif', 'monospace', 'rgba', 'hsla',
        'deg', 'rad', 'grad', 'turn',
    }
    BLOCKED = ALLOWED | CSS_TERMS | set()

    # 额外跳过六位十六进制颜色码
    hex_colors = set(re.findall(r'#[0-9A-Fa-f]{6}', text))
    BLOCKED |= hex_colors

    # 检查英文专有名词
    terms = set(re.findall(r'\b[A-Z][A-Za-z0-9.+\-]{2,}\b', text))
    # 过滤掉前面有#的（CSS颜色码如 #EF4444 → 去掉EF4444）
    terms = {t for t in terms if not re.search(rf'#{t}\b', text)}
    suspicious = terms - BLOCKED
    findings = []
    for t in suspicious:
        # 检查前面是否已有中文标注
        idx = text.find(t)
        before = text[max(0, idx - 20):idx]
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', before))
        if not has_cn:
            findings.append({
                'text': t,
                'issue': '英文专有名词缺少中文标注',
                'source': source_label,
            })
    return findings


def factcheck_article(date, edition):
    """核查一篇文章"""
    article_path = find_article_path(date, edition)
    if not article_path:
        return {
            'date': date,
            'edition': edition,
            'status': 'SKIP',
            'reason': f'article.html 不存在',
            'data_points': [],
            'flags': [],
            'errors': [],
        }

    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取文本部分（去掉HTML标签）
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text).strip()

    result = {
        'date': date,
        'edition': edition,
        'title': extract_title(content),
        'word_count': len(text),
        'status': 'PASS',
        'data_points': [],
        'flags': [],
        'errors': [],
    }

    # 1. 检查数据点
    result['data_points'] = check_data_points(text, f'{date}/{edition}/article.html')

    # 2. 检查可疑表述
    result['flags'] = check_suspicious(text, f'{date}/{edition}/article.html')

    # 3. 检查英文术语
    result['flags'] += check_english_terms(text, f'{date}/{edition}/article.html')

    # 4. 特别检查：文章中是否包含合规声明（如"不构成投资建议"）
    if '不构成' not in content or '投资建议' not in content:
        result['errors'].append('缺少合规声明 "不构成投资建议"')

    # 5. 特别检查：是否有明确的数据来源标注
    has_source = bool(re.search(r'来源|数据来自|据.*(报|社|网|数据|统计)', content))
    if not has_source:
        result['flags'].append({
            'text': '全文未标注数据来源',
            'issue': '建议在关键数据后标注来源（如Wind、同花顺、路透等）',
            'source': f'{date}/{edition}/article.html',
        })

    # 判断结果
    if result['errors']:
        result['status'] = 'FAIL'
    elif any(f['issue'] == '无法独立验证的表述，需要标注来源' for f in result['flags']):
        result['status'] = 'WARN'
    elif result['flags']:
        result['status'] = 'PASS_WITH_FLAGS'

    return result


def factcheck_script(date, edition):
    """核查口播稿"""
    script_path = find_script_path(date, edition)
    if not script_path:
        return None

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        'date': date,
        'edition': edition,
        'char_count': len(content),
        'status': 'PASS',
        'flags': [],
        'errors': [],
    }

    # 1. 检查数据点
    data_points = check_data_points(content, f'{date}/{edition}/script.txt')
    result['data_points'] = data_points

    # 2. 检查可疑表述
    result['flags'] = check_suspicious(content, f'{date}/{edition}/script.txt')

    # 3. 检查英文术语
    result['flags'] += check_english_terms(content, f'{date}/{edition}/script.txt')

    # 4. 检查内容长度（太短的口播稿）
    if len(content) < 200:
        result['errors'].append(f'口播稿过短 ({len(content)} chars，建议至少300+)')

    # 判断结果
    if result['errors']:
        result['status'] = 'FAIL'
    elif result['flags']:
        result['status'] = 'WARN'

    return result


def extract_title(html):
    m = re.search(r'<title>([^<]+)</title>', html)
    return m.group(1) if m else 'Unknown'


def print_report(results, scripts_results, output_to_file=False):
    """打印结构化报告"""
    edition_cn = {'morning': '🌅 早报', 'evening': '🌙 晚报'}

    report_lines = []
    report_lines.append('=' * 55)
    report_lines.append('  扬说财经 · 事实核查报告')
    report_lines.append(f'  日期: {TODAY}')
    report_lines.append('=' * 55)

    all_pass = True

    for edition in ['morning', 'evening']:
        result = results.get(edition)
        if not result:
            continue

        title = edition_cn.get(edition, edition)
        report_lines.append(f'\n{"─" * 55}')
        report_lines.append(f'  {title}: {result.get("title", "")}')
        report_lines.append(f'{"─" * 55}')

        if result['status'] == 'SKIP':
            report_lines.append(f'  ⏭️  {result["reason"]}')
            continue

        # 状态
        status_icon = {'PASS': '✅', 'WARN': '⚠️', 'PASS_WITH_FLAGS': '⚠️', 'FAIL': '❌'}
        report_lines.append(f'  状态: {status_icon.get(result["status"], "?")} {result["status"]}')
        report_lines.append(f'  字数: {result["word_count"]}')

        if result['errors']:
            all_pass = False
            report_lines.append(f'\n  ❌ 必须修复:')
            for err in result['errors']:
                report_lines.append(f'     - {err}')

        # 可疑表述
        suspicious_flags = [f for f in result['flags'] if f['issue'] == '无法独立验证的表述，需要标注来源']
        if suspicious_flags:
            all_pass = False
            report_lines.append(f'\n  ⚠️ 可疑表述（需标注来源）:')
            for f in suspicious_flags:
                report_lines.append(f'     - "{f["text"]}"')

        # 其他标记
        other_flags = [f for f in result['flags'] if f['issue'] != '无法独立验证的表述，需要标注来源']
        if other_flags:
            report_lines.append(f'\n  📝 建议:')
            for f in other_flags:
                report_lines.append(f'     - [{f["issue"]}] "{f["text"]}"')

        # 数据点概览
        if result['data_points']:
            report_lines.append(f'\n  📊 提取到 {len(result["data_points"])} 个数据点')
            # 按类型统计
            from collections import Counter
            types = Counter(d['type'] for d in result['data_points'])
            for t, c in types.most_common():
                report_lines.append(f'     - {t}: {c}个')

        # 口播稿结果
        scr = scripts_results.get(edition)
        if scr:
            report_lines.append(f'\n  🎤 口播稿 ({scr["char_count"]}字):')
            if scr['errors']:
                all_pass = False
                for err in scr['errors']:
                    report_lines.append(f'     ❌ {err}')
            if scr['flags']:
                for f in scr['flags']:
                    report_lines.append(f'     ⚠️ {f["text"]}')

    report_lines.append(f'\n{"=" * 55}')
    report_lines.append(f'  总体: {"✅ 全部通过" if all_pass else "❌ 存在问题待修复"}')
    report_lines.append(f'{"=" * 55}')

    report = '\n'.join(report_lines)

    if output_to_file:
        report_dir = os.path.join(ROOT, TODAY, 'wechat-publish')
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, 'factcheck-report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f'\n报告已保存: {report_path}')
    else:
        print(report)

    return all_pass


def main():
    args = parse_args()
    date = args.date
    editions = [args.edition] if args.edition else ['morning', 'evening']

    from collections import Counter
    results = {}
    scripts_results = {}

    for edition in editions:
        results[edition] = factcheck_article(date, edition)
        if args.check_script:
            scripts_results[edition] = factcheck_script(date, edition)

    all_pass = print_report(results, scripts_results, args.output)

    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
