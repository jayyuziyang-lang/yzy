#!/usr/bin/env python3
"""Site health check — run before deploy to catch issues."""
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0
FAIL = 0

def check(ok, msg):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f'  ✅ {msg}')
    else:
        FAIL += 1
        print(f'  ❌ {msg}')

def main():
    global PASS, FAIL
    print(f'\n{"="*50}')
    print('  扬说财经 · Site Health Check')
    print(f'  ROOT: {ROOT}')
    print(f'{"="*50}\n')

    # 1. Check data/articles.json
    print('[1/6] Data files')
    articles_path = os.path.join(ROOT, 'data', 'articles.json')
    holidays_path = os.path.join(ROOT, 'data', 'holidays-2026.json')

    if os.path.exists(articles_path):
        with open(articles_path, encoding='utf-8') as f:
            articles = json.load(f)
        check(True, f'articles.json exists — {len(articles.get("articles", []))} articles, latest: {articles.get("latest_date")}')
    else:
        check(False, 'articles.json missing — run update-index.py')

    if os.path.exists(holidays_path):
        with open(holidays_path, encoding='utf-8') as f:
            holidays = json.load(f)
        check(True, f'holidays-2026.json exists — {len(holidays)} entries')
    else:
        check(False, 'holidays-2026.json missing')

    # 2. Check index.html
    print('\n[2/6] Homepage')
    index_path = os.path.join(ROOT, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, encoding='utf-8') as f:
            idx_html = f.read()
        checks = [
            ('Hero clock widget', 'heroClockValue'),
            ('Hero date display', 'heroDateValue'),
            ('Today section', 'todayContent'),
            ('History section', 'historyContent'),
            ('Hero character area', 'hero-char-area'),
            ('Tab navigation', 'switchTab'),
            ('Articles data embedded', 'ARTICLES_BY_DATE'),
            ('Holidays data embedded', 'HOLIDAYS_DATA'),
            ('Midnight refresh', 'scheduleMidnightRefresh'),
        ]
        for label, needle in checks:
            check(needle in idx_html, f'index.html — {label}')
    else:
        check(False, 'index.html missing!')

    # 3. Check article files
    print('\n[3/6] Article files')
    article_ok = 0
    article_total = 0
    if 'by_date' in articles:
        for date_str, sessions in articles['by_date'].items():
            for session_key, session_data in sessions.items():
                article_total += 1
                url = session_data.get('url', '')
                article_path = os.path.join(ROOT, url)
                if os.path.exists(article_path):
                    article_ok += 1
                    # Check nav bar
                    with open(article_path, encoding='utf-8') as f:
                        html = f.read()
                    has_nav = ('top-nav' in html or 'site-top-bar' in html) and '返回首页' in html
                    check(has_nav, f'{date_str} {session_key} — nav bar present')
                else:
                    check(False, f'{date_str} {session_key} — file missing: {url}')
    if article_total == 0:
        print('  (no articles to check)')

    # 3b. Check AI chain articles
    print('\n[3b/6] AI chain articles')
    ai_chain_json = os.path.join(ROOT, 'data', 'ai-chain.json')
    if os.path.exists(ai_chain_json):
        with open(ai_chain_json, encoding='utf-8') as f:
            ai_data = json.load(f)
        ai_articles = ai_data.get('articles', [])
        check(len(ai_articles) > 0, f'ai-chain.json — {len(ai_articles)} articles')
        for aa in ai_articles:
            url = aa.get('url', '')
            status = aa.get('status', 'draft')
            if url and status != 'draft':
                ap = os.path.join(ROOT, url)
                if os.path.exists(ap):
                    with open(ap, encoding='utf-8') as f:
                        html = f.read()
                    has_nav = ('top-nav' in html or 'site-top-bar' in html) and '返回首页' in html
                    check(has_nav, f'AI: {aa.get("title","?")} — article.html + nav')
                else:
                    check(False, f'AI: {aa.get("title","?")} — file MISSING: {url}')
    else:
        check(False, 'ai-chain.json not found')

    # 4. Check character assets
    print('\n[4/6] Character assets')
    char_dir = os.path.join(ROOT, 'assets', 'character')
    if os.path.isdir(char_dir):
        files = os.listdir(char_dir)
        expected = ['ayang-sticker.png', 'ayang-square.jpg']
        for fname in expected:
            fpath = os.path.join(char_dir, fname)
            check(os.path.exists(fpath), f'assets/character/{fname} — {os.path.getsize(fpath)//1024} KB' if os.path.exists(fpath) else 'MISSING')
    else:
        check(False, 'assets/character/ directory missing')

    # 5. Check GitHub Pages config
    print('\n[5/6] Deploy config')
    workflow = os.path.join(ROOT, '.github', 'workflows', 'deploy.yml')
    check(os.path.exists(workflow), 'deploy.yml exists')

    deploy_sh = os.path.join(ROOT, 'deploy.sh')
    check(os.path.exists(deploy_sh), 'deploy.sh exists')

    git_dir = os.path.join(ROOT, '.git')
    check(os.path.isdir(git_dir), 'Git repository initialized')

    # 6. Check file sizes
    print('\n[6/6] Size audit')
    total_kb = 0
    for root, dirs, files in os.walk(ROOT):
        # Skip .git
        if '.git' in root.split(os.sep):
            continue
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                total_kb += sz // 1024
                if sz > 500 * 1024:  # >500KB
                    print(f'  ⚠️  Large file: {os.path.relpath(fp, ROOT)} ({sz//1024} KB)')
            except OSError:
                pass
    print(f'  📊 Total site size: ~{total_kb} KB')

    # Summary
    print(f'\n{"="*50}')
    total = PASS + FAIL
    if FAIL == 0:
        print(f'  ✅ ALL {PASS}/{PASS} CHECKS PASSED')
    else:
        print(f'  ⚠️  {PASS}/{total} passed, {FAIL}/{total} failed')
    print(f'{"="*50}\n')
    return FAIL

if __name__ == '__main__':
    sys.exit(main())
