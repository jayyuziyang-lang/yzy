#!/usr/bin/env python3
"""Fix 4 issues in one pass:
1. AI chain tab -> use edition/history-item style (like daily report)
2. Article edition: 第1期 -> 第2期
3. Remove duplicate top-nav (navigation overlap)
4. Add preload=none to videos for smoother loading
"""
import shutil

# ============================================================
# FIX 1: AI chain tab style (index.html JS functions)
# ============================================================
with open('index.html', 'r', encoding='utf-8') as f:
    idx_html = f.read()

# Replace renderAiPage with edition-based style
old_page_start = idx_html.find('function renderAiPage(container)')
old_page_end = idx_html.find('function aiPrevPage()', old_page_start)
# If aiPrevPage doesn't exist, find the next section
if old_page_end < 0:
    old_page_end = idx_html.find('\n\n// ============', old_page_start)

new_renderAiPage = """function renderAiPage(container) {
  var articles = window.__aiArticles;
  var html = '';

  if (articles.length === 0) {
    container.innerHTML = '<div class="no-data"><span class="big">\\u23f3</span>\\u5185\\u5bb9\\u7f16\\u8f91\\u4e2d</div>';
    return;
  }

  // \\u6700\\u65b0\\u5185\\u5bb9\\uff1a\\u663e\\u793a\\u6700\\u65b0\\u53d1\\u5e03\\u7684\\u6587\\u7ae0
  var latestArticle = articles[articles.length - 1];
  html += '<div class="today-section" style="margin-top:0;">\\u6700\\u65b0\\u5185\\u5bb9</div>';
  html += '<div class="today-list">';

  var la = latestArticle;
  if (la.url && la.status !== 'draft') {
    html += '<a class="edition edition-morning" href="' + la.url + '">';
  } else {
    html += '<div class="edition edition-morning">';
  }
  html +=
    '<div class="edition-icon">\\U0001f451</div>' +
    '<div class="edition-info">' +
      '<div class="edition-title">' + la.title + '</div>' +
    '</div>';
  if (la.url && la.status !== 'draft') {
    html += '</a>';
  } else {
    html += '</div>';
  }
  html += '</div>';

  // \\u5386\\u53f2\\u5185\\u5bb9\\uff1a\\u6700\\u65e9\\u53d1\\u5e03\\u7684\\u4e3a #1
  var historyArticles = articles.slice(0, -1);
  if (historyArticles.length > 0) {
    html += '<div style="margin-top:20px;"><h2>\\u5386\\u53f2\\u5185\\u5bb9</h2></div>';

    for (var i = 0; i < historyArticles.length; i++) {
      var a = historyArticles[i];
      var idx = i + 1;
      var statusHtml = '';
      if (a.status === 'draft' || !a.url) {
        statusHtml = ' [\\u7f16\\u8f91\\u4e2d]';
      }
      var dateStr = a.date || '';

      html += '<div class="history-item">';
      html += '<span class="h-icon">' + idx + '</span>';
      if (a.url && a.status !== 'draft') {
        html += '<a href="' + a.url + '">' + a.title + '</a>';
      } else {
        html += '<span style="flex:1;color:#94A3B8;font-size:13px;">' + a.title + statusHtml + '</span>';
      }
      if (dateStr) {
        html += '<span class="h-time">' + dateStr + '</span>';
      }
      html += '</div>';
    }
  }

  container.innerHTML = html;
}

"""

# Extract old renderAiPage
old_page = idx_html[old_page_start:old_page_end]
idx_html = idx_html.replace(old_page, new_renderAiPage)
print('[OK] Fix 1: AI chain tab -> edition/history-item style')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx_html)
print('  index.html written')

# ============================================================
# FIX 2 & 3: MLCC article - edition number + remove top-nav
# ============================================================
with open('ai-chain/mlcc-series/article.html', 'r', encoding='utf-8') as f:
    article_html = f.read()

# Replace 第1期 -> 第2期 (in site-top-bar and article body)
article_html = article_html.replace('\\u7b2c1\\u671f', '\\u7b2c2\\u671f')
# Also replace in plain text (if not already)
article_html = article_html.replace('第1期', '第2期')
article_html = article_html.replace('| 第1期', '| 第2期')
print('[OK] Fix 2: Edition changed to 第2期')

# Remove the duplicate .top-nav section
# Find start: <nav class="top-nav" ...>
nav_start = article_html.find('<nav class="top-nav"')
nav_end = article_html.find('</nav>', nav_start) + 6  # +6 for </nav>
if nav_start >= 0:
    top_nav_html = article_html[nav_start:nav_end]
    article_html = article_html.replace(top_nav_html, '')
    print('[OK] Fix 3: Removed duplicate .top-nav')

    # Adjust CSS: remove top-nav overrides, fix header padding and side-toc
    # Remove the old inline style block for site-top-bar
    style_start = article_html.find('<style>  <!-- \\u9002\\u914d\\u626c\\u8bf4\\u8d22\\u7ecf\\u7f51\\u7ad9')
    if style_start < 0:
        style_start = article_html.find('<style>')
    style_end = article_html.find('</style>', style_start) + 8
    old_style = article_html[style_start:style_end]

    new_style = """<style>
  .site-top-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 2000;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-bottom: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    padding: 0 24px;
    height: 44px;
  }
  .site-top-bar .back {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #1A56DB;
    text-decoration: none;
    font-size: 13px;
    font-weight: 600;
  }
  .site-top-bar .back:active { opacity: 0.6; }
  .site-top-bar .nav-label {
    flex: 1;
    text-align: center;
    font-size: 12px;
    color: #64748B;
  }
  .site-top-bar .nav-edition {
    font-size: 11px;
    background: #EFF6FF;
    color: #1A56DB;
    padding: 2px 8px;
    border-radius: 8px;
    font-weight: 600;
  }
  /* \\u8c03\\u6574\\u7ad9\\u70b9\\u9876\\u8ddd - \\u53ea\\u4fdd\\u7559 site-top-bar */
  .article-header { padding-top: 104px !important; }
  .side-toc { top: 84px !important; }
  @media (max-width: 768px) {
    .article-header { padding-top: 84px !important; }
  }"""

    # Fix: the style block in the article uses JS unicode or actual Chinese
    # The original file might have actual Chinese characters
    article_html = article_html.replace(old_style, new_style)
    print('[OK] Fix 3: Updated CSS for single nav bar')

# Also check site-top-bar nav-edition
article_html = article_html.replace('class="site-top-bar">\\n  <a class="back"', 'class="site-top-bar">\n  <a class="back"')
# The edition number should already be fixed from the replace above

with open('ai-chain/mlcc-series/article.html', 'w', encoding='utf-8') as f:
    f.write(article_html)
print('  article.html written')

# ============================================================
# FIX 4: Video - add preload="none" to reduce stuttering
# ============================================================
with open('ai-chain/mlcc-series/article.html', 'r', encoding='utf-8') as f:
    article_html = f.read()

# Add preload="none" to both video tags if not already present
if 'preload="none"' not in article_html:
    article_html = article_html.replace(
        '<video loop muted playsinline controls\n             poster="../assets/images/mlcc_structure_cover.png"\n             style="width:100%; aspect-ratio:16/9; background:#F8FAFC;">',
        '<video loop muted playsinline controls preload="none"\n             poster="../assets/images/mlcc_structure_cover.png"\n             style="width:100%; aspect-ratio:16/9; background:#F8FAFC;">'
    )
    article_html = article_html.replace(
        '<video loop muted playsinline controls\n             poster="../assets/images/mlcc_process_cover.png"\n             style="width:100%; aspect-ratio:16/9; background:#F8FAFC;">',
        '<video loop muted playsinline controls preload="none"\n             poster="../assets/images/mlcc_process_cover.png"\n             style="width:100%; aspect-ratio:16/9; background:#F8FAFC;">'
    )
    print('[OK] Fix 4: Added preload="none" to videos')
else:
    print('[OK] Fix 4: Videos already have preload="none"')

with open('ai-chain/mlcc-series/article.html', 'w', encoding='utf-8') as f:
    f.write(article_html)

print('\\n[DONE] All fixes applied')
