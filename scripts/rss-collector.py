#!/usr/bin/env python3
"""
扬说财经 · RSS 财经新闻采集器

从配置的RSS源自动采集财经新闻，输出到 docs/review/news-rss-{date}.md。
使用 Python 标准库实现，无外部依赖。

用法：
  python scripts/rss-collector.py                    # 采集并保存为今日文件
  python scripts/rss-collector.py --preview          # 只打印不保存
  python scripts/rss-collector.py --date 2026-05-24  # 指定日期
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = time.strftime('%Y-%m-%d')

# ============================================================
# RSS 源配置 — 可在此自由增删
# 格式: (名称, RSS URL, 分类)
# 分类: "国内" 或 "国际"
# ============================================================
RSS_SOURCES = [
    # ---- 国内财经 ----
    ("证券时报", "https://www.stcn.com/rss/rss.xml", "国内"),
    ("东方财富-要闻", "https://finance.eastmoney.com/rss/", "国内"),
    ("新浪财经", "https://finance.sina.com.cn/rss/", "国内"),
    ("华尔街见闻", "https://wallstreetcn.com/rss", "国内"),
    ("第一财经", "https://www.yicai.com/rss", "国内"),
    ("36氪", "https://36kr.com/feed", "国内"),

    # ---- 国际财经 ----
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex", "国际"),
    ("CNBC Top News", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "国际"),
    ("Google News - Finance", "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB", "国际"),
    ("MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories", "国际"),
    ("Reuters - Business", "https://news.google.com/rss/search?q=site:reuters.com+business&hl=en-US&gl=US&ceid=US:en", "国际"),
    ("Bloomberg - Markets", "https://feeds.bloomberg.com/markets/news.rss", "国际"),
]

# 缓存文件路径
CACHE_FILE = os.path.join(ROOT, "data", ".rss-cache.json")

# 缓存有效期（秒）
CACHE_TTL = 3600  # 1小时

# 单个RSS源请求超时（秒）
REQUEST_TIMEOUT = 15

# 每条新闻摘要最大长度
SUMMARY_MAX_LEN = 120

# 输出目录
OUTPUT_DIR = os.path.join(ROOT, "docs", "review")

# ============================================================
# 工具函数
# ============================================================

def load_cache():
    """加载缓存文件，返回 {url: {'ts': timestamp, 'items': [...]}}"""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        # 清理过期条目
        now = time.time()
        return {k: v for k, v in raw.items() if now - v.get('ts', 0) < CACHE_TTL}
    except (json.JSONDecodeError, ValueError, OSError):
        return {}


def save_cache(cache):
    """保存缓存到文件"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"  [警告] 缓存写入失败: {e}", file=sys.stderr)


def clean_html(raw):
    """移除HTML标签，返回纯文本"""
    if not raw:
        return ""
    text = re.sub(r'<[^>]+>', '', raw)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate(text, max_len=SUMMARY_MAX_LEN):
    """截断文本，在词边界处截断"""
    if not text or len(text) <= max_len:
        return text or ""
    truncated = text[:max_len].rsplit(' ', 1)[0]
    if len(truncated) < max_len * 0.6:
        truncated = text[:max_len]
    return truncated + "…"


def parse_rss_date(date_str):
    """尝试解析常见RSS日期格式，返回格式化字符串 'YYYY-MM-DD HH:MM'"""
    if not date_str:
        return ""
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',   # RFC 822
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',         # ISO 8601
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
    ]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            # 转换为北京时间
            bjt = dt.astimezone(timezone(timedelta(hours=8)))
            return bjt.strftime('%Y-%m-%d %H:%M')
        except (ValueError, OverflowError):
            continue
    return date_str.strip()[:19]


def fetch_rss(url):
    """
    抓取单个RSS源，返回 (title, link, summary, pub_date) 列表。
    失败返回空列表并打印错误。
    """
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        print(f"  [错误] 网络错误: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  [错误] 请求失败: {e}", file=sys.stderr)
        return []

    # 解码
    content = None
    for encoding in ['utf-8', 'gb2312', 'gbk', 'latin-1']:
        try:
            content = raw.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if content is None:
        print(f"  [错误] 无法解码响应内容", file=sys.stderr)
        return []

    # 清理XML中可能干扰解析的内容
    content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', content)

    # 解析XML
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"  [错误] XML解析失败: {e}", file=sys.stderr)
        return []

    items = []

    # RSS 2.0 格式 (<channel> → <item>)
    channel = root.find('channel')
    if channel is not None:
        for item in channel.findall('item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '').strip()
            pub_date = item.findtext('pubDate', '') or item.findtext('dc:date', '')

            if not title:
                continue

            items.append({
                'title': clean_html(title),
                'link': link,
                'summary': truncate(clean_html(description)),
                'pub_date': parse_rss_date(pub_date.strip() if pub_date else ''),
            })

    # Atom 格式 (<feed> → <entry>)
    if not items:
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.findtext('{http://www.w3.org/2005/Atom}title', '').strip()
            link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
            link = link_elem.get('href', '').strip() if link_elem is not None else ''
            summary = entry.findtext('{http://www.w3.org/2005/Atom}summary', '') or ''
            published = entry.findtext('{http://www.w3.org/2005/Atom}published', '') or ''

            if not title:
                continue

            items.append({
                'title': clean_html(title),
                'link': link,
                'summary': truncate(clean_html(summary)),
                'pub_date': parse_rss_date(published.strip() if published else ''),
            })

    return items


def collect_all(cache):
    """
    遍历所有RSS源，返回按分类聚合的新闻列表。
    返回: {'国内': [(title, source, link, pub_date, summary), ...],
            '国际': [...]}
    """
    result = {'国内': [], '国际': []}
    new_cache = dict(cache)  # 复制一份用于更新

    for name, url, category in RSS_SOURCES:
        print(f"[RSS] 采集: {name} ({category})")
        print(f"       {url}")

        # 检查缓存
        if url in cache:
            cached = cache[url]
            age = time.time() - cached.get('ts', 0)
            if age < CACHE_TTL and cached.get('items'):
                print(f"  [缓存] 命中 ({age:.0f}秒前), {len(cached['items'])}条")
                items = cached['items']
            else:
                print(f"  [缓存] 已过期, 重新抓取")
                items = fetch_rss(url)
        else:
            print(f"  [缓存] 无缓存, 抓取中")
            items = fetch_rss(url)

        if not items:
            print(f"  [结果] 采集到 0 条")
            # 保留旧缓存
            new_cache[url] = cache.get(url, {'ts': time.time(), 'items': []})
            continue

        print(f"  [结果] 采集到 {len(items)} 条")

        # 更新缓存
        new_cache[url] = {
            'ts': time.time(),
            'items': items,
        }

        # 添加到结果（带上来源名）
        for item in items:
            result[category].append((
                item['title'],
                name,
                item['link'],
                item['pub_date'],
                item['summary'],
            ))

    # 保存新缓存
    save_cache(new_cache)

    # 去重（按标题去重，保留第一个）
    for cat in result:
        seen = set()
        deduped = []
        for entry in result[cat]:
            key = entry[0][:60]  # 用标题前60字符作为去重键
            if key not in seen:
                seen.add(key)
                deduped.append(entry)
        result[cat] = deduped

    return result


def generate_markdown(collected, date_str):
    """生成Markdown格式的输出"""
    lines = []
    lines.append(f"# RSS 财经新闻采集报告 — {date_str}")
    lines.append("")
    lines.append(f"> 自动采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} (北京时间)")
    lines.append(f"> 采集源: {len(RSS_SOURCES)} 个 RSS 源")
    lines.append("")

    section_icons = {'国内': '国内财经', '国际': '国际财经'}

    for cat in ['国内', '国际']:
        items = collected.get(cat, [])
        total = len(items)
        lines.append(f"## {section_icons[cat]}（共 {total} 条）")
        lines.append("")

        if not items:
            lines.append("> 该分类暂无采集结果")
            lines.append("")
            continue

        # 表头
        lines.append("| 时间 | 标题 | 来源 |")
        lines.append("|------|------|------|")

        for title, source, link, pub_date, summary in items:
            # 构建链接的Markdown
            if link:
                title_cell = f"[{title}]({link})"
            else:
                title_cell = title

            # 摘要（tooltip风格）
            if summary:
                title_cell += f"<br><small>{summary}</small>"

            time_cell = pub_date if pub_date else "-"
            lines.append(f"| {time_cell} | {title_cell} | {source} |")

        lines.append("")

    # 页脚统计
    total_all = sum(len(v) for v in collected.values())
    lines.append("---")
    lines.append("")
    lines.append(f"**总计:** {total_all} 条新闻 | **国内:** {len(collected.get('国内', []))} 条 | "
                 f"**国际:** {len(collected.get('国际', []))} 条")
    lines.append("")
    lines.append(f"> 采集脚本: `scripts/rss-collector.py` | 缓存有效期: {CACHE_TTL}秒")

    return "\n".join(lines)


def generate_preview(collected, date_str):
    """生成终端预览输出（简洁版）"""
    print()
    print(f"{'='*70}")
    print(f"  RSS 财经新闻采集报告 — {date_str}")
    print(f"  采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} (北京时间)")
    print(f"  采集源: {len(RSS_SOURCES)} 个 RSS 源")
    print(f"{'='*70}")

    section_icons = {'国内': '国内财经', '国际': '国际财经'}

    for cat in ['国内', '国际']:
        items = collected.get(cat, [])
        print(f"\n  ── {section_icons[cat]}（共 {len(items)} 条）──")
        if not items:
            print("    (无数据)")
            continue
        for i, (title, source, link, pub_date, summary) in enumerate(items, 1):
            time_str = f"[{pub_date}]" if pub_date else ""
            print(f"    {i:2d}. {time_str} {title}")
            print(f"        来源: {source}  链接: {link}")
            if summary:
                print(f"        摘要: {summary}")

    total_all = sum(len(v) for v in collected.values())
    print(f"\n  {'─'*70}")
    print(f"  总计: {total_all} 条 | 国内: {len(collected.get('国内', []))} 条 | "
          f"国际: {len(collected.get('国际', []))} 条")
    print()


def parse_args():
    parser = argparse.ArgumentParser(
        description='扬说财经 · RSS 财经新闻采集器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python scripts/rss-collector.py                    # 采集并保存
  python scripts/rss-collector.py --preview          # 只预览不保存
  python scripts/rss-collector.py --date 2026-05-24  # 指定日期
        '''
    )
    parser.add_argument('--date', default=TODAY, help='日期 (YYYY-MM-DD)，默认今天')
    parser.add_argument('--preview', action='store_true', help='只打印预览，不保存文件')
    return parser.parse_args()


def main():
    args = parse_args()
    date_str = args.date

    print(f"扬说财经 · RSS 采集器启动")
    print(f"日期: {date_str} | 模式: {'仅预览' if args.preview else '保存文件'}")
    print(f"RSS源: {len(RSS_SOURCES)} 个")
    print(f"缓存: {'已启用' if os.path.exists(CACHE_FILE) else '无缓存文件'}")
    print(f"{'─'*60}")

    # 加载缓存
    cache = load_cache()
    if cache:
        print(f"[缓存] 已加载 {len(cache)} 条有效缓存记录")
    print()

    # 采集
    collected = collect_all(cache)

    if args.preview:
        generate_preview(collected, date_str)
    else:
        # 生成Markdown并保存
        markdown = generate_markdown(collected, date_str)

        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        output_file = os.path.join(OUTPUT_DIR, f"news-rss-{date_str}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        total_all = sum(len(v) for v in collected.values())
        print(f"\n[保存] 已写入: {output_file}")
        print(f"[统计] 总计 {total_all} 条（国内 {len(collected.get('国内', []))} 条, "
              f"国际 {len(collected.get('国际', []))} 条）")

    print(f"\n[完成] RSS 采集任务结束")


if __name__ == '__main__':
    main()
