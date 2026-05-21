#!/usr/bin/env python3
"""Scan article directories and generate data/articles.json for the homepage."""
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_title(html_path):
    """Extract article title from HTML <title> tag or first h1."""
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
    """Scan all date directories for morning/evening articles."""
    articles = []
    for entry in sorted(os.listdir(ROOT)):
        # Match YYYY-MM-DD directories
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', entry):
            continue
        date_str = entry
        pub_dir = os.path.join(ROOT, entry, 'wechat-publish')

        for session in ('morning', 'evening'):
            article_dir = os.path.join(pub_dir, session)
            html_path = os.path.join(article_dir, 'article.html')
            if not os.path.exists(html_path):
                continue

            title = extract_title(html_path)
            edition_cn = '早报' if session == 'morning' else '晚报'
            edition_icon = '🌅' if session == 'morning' else '🌙'
            url = f'{entry}/wechat-publish/{session}/article.html'

            articles.append({
                'date': date_str,
                'session': session,
                'edition_cn': edition_cn,
                'icon': edition_icon,
                'title': title,
                'url': url,
            })

    # Sort by date desc, then morning before evening
    articles.sort(key=lambda a: (a['date'], 0 if a['session'] == 'morning' else 1), reverse=True)
    return articles

def generate_json(articles):
    """Write articles to data/articles.json, grouped by date."""
    # Group by date
    by_date = {}
    for a in articles:
        by_date.setdefault(a['date'], {})[a['session']] = a

    output = {
        'generated_at': '2026-05-21T00:00:00+08:00',
        'latest_date': articles[0]['date'] if articles else None,
        'articles': articles,
        'by_date': {d: by_date[d] for d in sorted(by_date.keys(), reverse=True)},
    }

    data_dir = os.path.join(ROOT, 'data')
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, 'articles.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'[OK] data/articles.json — {len(articles)} articles, latest: {output["latest_date"]}')

def generate_holidays_json():
    """Generate holidays-2026.json with Chinese public holidays for 2026."""
    holidays = [
        # 2026 Chinese public holidays
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

        # International observances
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
    ]

    # Financial market holidays (non-trading days)
    fin_holidays = [
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

    all_holidays = holidays + fin_holidays

    data_dir = os.path.join(ROOT, 'data')
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, 'holidays-2026.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(all_holidays, f, ensure_ascii=False, indent=2)
    print(f'[OK] data/holidays-2026.json — {len(all_holidays)} entries')

if __name__ == '__main__':
    articles = scan_articles()
    generate_json(articles)
    generate_holidays_json()
    print('[DONE] Archive updated')
