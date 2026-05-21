#!/usr/bin/env python3
"""Scan article directories and generate data files for the homepage."""
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_title(html_path):
    if not os.path.exists(html_path):
        return None
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'<title>(.*?)</title>', html)
    if m:
        return m.group(1).strip()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html)
    if m:
        return m.group(1).strip()
    return '财经内容'

def scan_articles():
    articles = []
    for entry in sorted(os.listdir(ROOT)):
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', entry):
            continue
        for session in ('morning', 'evening'):
            html_path = os.path.join(ROOT, entry, 'wechat-publish', session, 'article.html')
            if not os.path.exists(html_path):
                continue
            title = extract_title(html_path)
            edition_cn = '早报' if session == 'morning' else '晚报'
            edition_icon = '🌅' if session == 'morning' else '🌙'
            articles.append({
                'date': entry,
                'session': session,
                'edition_cn': edition_cn,
                'icon': edition_icon,
                'title': title,
                'url': f'{entry}/wechat-publish/{session}/article.html',
            })
    articles.sort(key=lambda a: (a['date'], 0 if a['session'] == 'morning' else 1), reverse=True)
    return articles

def generate_json(articles):
    by_date = {}
    for a in articles:
        by_date.setdefault(a['date'], {})[a['session']] = a
    output = {
        'generated_at': '2026-05-21T00:00:00+08:00',
        'latest_date': articles[0]['date'] if articles else None,
        'articles': articles,
        'by_date': {d: by_date[d] for d in sorted(by_date.keys(), reverse=True)},
    }
    path = os.path.join(ROOT, 'data', 'articles.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'[OK] data/articles.json — {len(articles)} articles')

def generate_js(articles, holidays):
    """Generate data/articles.js — embedded JS for instant loading (no fetch needed)."""
    by_date = {}
    for a in articles:
        by_date.setdefault(a['date'], {})[a['session']] = a
    sorted_dates = sorted(by_date.keys(), reverse=True)

    articles_js = json.dumps(articles, ensure_ascii=False)
    by_date_js = json.dumps({d: by_date[d] for d in sorted_dates}, ensure_ascii=False)
    latest = f'"{articles[0]["date"]}"' if articles else 'null'
    holidays_js = json.dumps(holidays, ensure_ascii=False)

    js = f'''var ARTICLES_DATA = {articles_js};
var ARTICLES_BY_DATE = {by_date_js};
var ARTICLES_LATEST = {latest};
var HOLIDAYS_DATA = {holidays_js};
'''
    path = os.path.join(ROOT, 'data', 'articles.js')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f'[OK] data/articles.js — {len(articles)} articles + {len(holidays)} holidays embedded')

def generate_holidays():
    holidays = [
        {"date": "2026-01-01", "name": "元旦", "type": "public"},
        {"date": "2026-01-02", "name": "元旦假期", "type": "public"},
        {"date": "2026-01-03", "name": "元旦假期", "type": "public"},
        {"date": "2026-02-15", "name": "除夕", "type": "public"},
        {"date": "2026-02-16", "name": "春节", "type": "public"},
        {"date": "2026-02-17", "name": "春节假期", "type": "public"},
        {"date": "2026-02-18", "name": "春节假期", "type": "public"},
        {"date": "2026-02-19", "name": "春节假期", "type": "public"},
        {"date": "2026-02-20", "name": "春节假期", "type": "public"},
        {"date": "2026-02-21", "name": "春节假期", "type": "public"},
        {"date": "2026-04-04", "name": "清明节", "type": "public"},
        {"date": "2026-04-05", "name": "清明假期", "type": "public"},
        {"date": "2026-04-06", "name": "清明假期", "type": "public"},
        {"date": "2026-05-01", "name": "劳动节", "type": "public"},
        {"date": "2026-05-02", "name": "劳动节假期", "type": "public"},
        {"date": "2026-05-03", "name": "劳动节假期", "type": "public"},
        {"date": "2026-05-04", "name": "青年节", "type": "public"},
        {"date": "2026-05-05", "name": "劳动节假期", "type": "public"},
        {"date": "2026-06-19", "name": "端午节", "type": "public"},
        {"date": "2026-06-20", "name": "端午假期", "type": "public"},
        {"date": "2026-06-21", "name": "端午假期", "type": "public"},
        {"date": "2026-09-27", "name": "中秋节", "type": "public"},
        {"date": "2026-09-28", "name": "中秋假期", "type": "public"},
        {"date": "2026-09-29", "name": "中秋假期", "type": "public"},
        {"date": "2026-10-01", "name": "国庆节", "type": "public"},
        {"date": "2026-10-02", "name": "国庆假期", "type": "public"},
        {"date": "2026-10-03", "name": "国庆假期", "type": "public"},
        {"date": "2026-10-04", "name": "国庆假期", "type": "public"},
        {"date": "2026-10-05", "name": "国庆假期", "type": "public"},
        {"date": "2026-10-06", "name": "国庆假期", "type": "public"},
        {"date": "2026-10-07", "name": "国庆假期", "type": "public"},
        {"date": "2026-01-01", "name": "元旦", "type": "international"},
        {"date": "2026-02-14", "name": "情人节", "type": "international"},
        {"date": "2026-03-08", "name": "国际妇女节", "type": "international"},
        {"date": "2026-04-22", "name": "世界地球日", "type": "international"},
        {"date": "2026-05-01", "name": "国际劳动节", "type": "international"},
        {"date": "2026-06-01", "name": "国际儿童节", "type": "international"},
        {"date": "2026-10-31", "name": "万圣节", "type": "international"},
        {"date": "2026-11-26", "name": "感恩节", "type": "international"},
        {"date": "2026-12-25", "name": "圣诞节", "type": "international"},
        {"date": "2026-12-31", "name": "跨年夜", "type": "international"},
        {"date": "2026-01-01", "name": "元旦休市", "type": "market"},
        {"date": "2026-02-16", "name": "春节休市", "type": "market"},
        {"date": "2026-02-17", "name": "春节休市", "type": "market"},
        {"date": "2026-04-04", "name": "清明休市", "type": "market"},
        {"date": "2026-05-01", "name": "劳动节休市", "type": "market"},
        {"date": "2026-06-19", "name": "端午休市", "type": "market"},
        {"date": "2026-09-27", "name": "中秋休市", "type": "market"},
        {"date": "2026-10-01", "name": "国庆休市", "type": "market"},
        {"date": "2026-10-02", "name": "国庆休市", "type": "market"},
        {"date": "2026-10-05", "name": "国庆休市", "type": "market"},
        {"date": "2026-10-06", "name": "国庆休市", "type": "market"},
        {"date": "2026-10-07", "name": "国庆休市", "type": "market"},
    ]
    # Write JSON
    path = os.path.join(ROOT, 'data', 'holidays-2026.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(holidays, f, ensure_ascii=False, indent=2)
    print(f'[OK] data/holidays-2026.json — {len(holidays)} entries')
    return holidays

if __name__ == '__main__':
    articles = scan_articles()
    generate_json(articles)
    holidays = generate_holidays()
    generate_js(articles, holidays)
    print('[DONE] All data files generated')
