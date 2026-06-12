#!/usr/bin/env python3
"""Fix AI chain tab: ascending sort, latest/history split, remove hash prefix."""
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# === Step 1: Replace renderAiChain ===
p1_start = html.find('function renderAiChain()')
p1_end = html.find('function renderAiPage(container)', p1_start)
old_chain = html[p1_start:p1_end]

new_chain = '''function renderAiChain() {
  var container = document.getElementById('aiChainList');
  if (!container) return;

  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'data/ai-chain.json?t=' + Date.now(), true);
  xhr.onload = function() {
    if (xhr.status !== 200) {
      container.innerHTML = '<div class="no-data"><span class="big">\u26a0\ufe0f</span>\u52a0\u8f7d\u5931\u8d25</div>';
      return;
    }
    try {
      var data = JSON.parse(xhr.responseText);
      var articles = data.articles || [];
      // \u6309\u65e5\u671f\u5347\u5e8f\uff08\u6700\u65e9\u53d1\u5e03\u7684\u4e3a #1\uff09
      articles.sort(function(a, b) {
        return a.date < b.date ? -1 : (a.date > b.date ? 1 : 0);
      });
      window.__aiArticles = articles;
      if (articles.length === 0) {
        container.innerHTML = '<div class="no-data"><span class="big">\u23f3</span>\u5185\u5bb9\u7f16\u8f91\u4e2d</div>';
        return;
      }
      renderAiPage(container);
    } catch(e) {
      container.innerHTML = '<div class="no-data"><span class="big">\u26a0\ufe0f</span>\u6570\u636e\u89e3\u6790\u5931\u8d25</div>';
    }
  };
  xhr.onerror = function() {
    container.innerHTML = '<div class="no-data"><span class="big">\u23f3</span>\u5185\u5bb9\u7f16\u8f91\u4e2d</div>';
  };
  xhr.send();
}

'''

html = html[:p1_start] + new_chain + html[p1_end:]
print('[OK] Step 1: renderAiChain replaced')

# === Step 2: Replace renderAiPage ===
p2_start = html.find('function renderAiPage(container)')
p2_end = html.find('function aiPrevPage()', p2_start)
old_page = html[p2_start:p2_end]

new_page = '''function renderAiPage(container) {
  var articles = window.__aiArticles;
  var html = '';

  if (articles.length === 0) {
    container.innerHTML = '<div class="no-data"><span class="big">\u23f3</span>\u5185\u5bb9\u7f16\u8f91\u4e2d</div>';
    return;
  }

  // \u6700\u65b0\u5185\u5bb9\uff1a\u663e\u793a\u6700\u65b0\u53d1\u5e03\u7684\u6587\u7ae0\uff08\u6570\u7ec4\u6700\u540e\u4e00\u4e2a\uff09
  var latestArticle = articles[articles.length - 1];
  html += '<div class="today-section" style="margin-top:0;">\u6700\u65b0\u5185\u5bb9</div>';
  html += '<div class="today-list">';

  var la = latestArticle;
  var laStatus = '';
  if (la.status === 'draft' || !la.url) {
    laStatus = '<span class="ai-status-draft">\U0001f4dd \u7f16\u8f91\u4e2d</span>';
  }
  var laTags = '';
  if (la.tags && la.tags.length > 0) {
    laTags = '<div class="ai-tags">';
    for (var t = 0; t < la.tags.length; t++) {
      laTags += '<span class="ai-tag">' + la.tags[t] + '</span>';
    }
    laTags += '</div>';
  }
  var laDateBadge = '<span class="ai-date-badge">' + (la.date || '\u5f85\u5b9a') + '</span>';

  if (la.url && la.status !== 'draft') {
    html += '<a class="ai-card" href="' + la.url + '">';
  } else {
    html += '<div class="ai-card">';
  }
  html +=
    '<div class="ai-icon"><span style="font-size:22px;">\U0001f451</span></div>' +
    '<div class="ai-body">' +
      '<div class="ai-title">' + la.title + '</div>' +
      '<div class="ai-meta">' + laDateBadge + ' \u00b7 ' + la.readTime + '\u5206\u949f\u9605\u8bfb' + ' ' + laStatus + '</div>' +
      '<div class="ai-summary">' + (la.summary || '') + '</div>' +
      laTags +
    '</div>' +
    '<span class="ai-arrow">\u203a</span>';
  if (la.url && la.status !== 'draft') {
    html += '</a>';
  } else {
    html += '</div>';
  }
  html += '</div>';

  // \u5386\u53f2\u5185\u5bb9\uff1a\u6700\u65e9\u53d1\u5e03\u7684\u4e3a #1
  var historyArticles = articles.slice(0, -1);
  if (historyArticles.length > 0) {
    html += '<div class="history-header">\u5386\u53f2\u5185\u5bb9</div>';
    html += '<div class="history-list">';

    for (var i = 0; i < historyArticles.length; i++) {
      var a = historyArticles[i];
      var idx = i + 1;

      var statusHtml = '';
      if (a.status === 'draft' || !a.url) {
        statusHtml = '<span class="ai-status-draft">\U0001f4dd \u7f16\u8f91\u4e2d</span>';
      }
      var tagsHtml = '';
      if (a.tags && a.tags.length > 0) {
        tagsHtml = '<div class="ai-tags">';
        for (var t = 0; t < a.tags.length; t++) {
          tagsHtml += '<span class="ai-tag">' + a.tags[t] + '</span>';
        }
        tagsHtml += '</div>';
      }
      var dateStr = a.date || '\u5f85\u5b9a';
      var dateBadge = '<span class="ai-date-badge">' + dateStr + '</span>';

      if (a.url && a.status !== 'draft') {
        html += '<a class="ai-card" href="' + a.url + '">';
      } else {
        html += '<div class="ai-card">';
      }
      html +=
        '<div class="ai-icon">' + idx + '</div>' +
        '<div class="ai-body">' +
          '<div class="ai-title">' + a.title + '</div>' +
          '<div class="ai-meta">' + dateBadge + ' \u00b7 ' + a.readTime + '\u5206\u949f\u9605\u8bfb' + ' ' + statusHtml + '</div>' +
          '<div class="ai-summary">' + (a.summary || '') + '</div>' +
          tagsHtml +
        '</div>' +
        '<span class="ai-arrow">\u203a</span>';
      if (a.url && a.status !== 'draft') {
        html += '</a>';
      } else {
        html += '</div>';
      }
    }

    html += '</div>';
  }

  container.innerHTML = html;
}

'''

html = html[:p2_start] + new_page + html[p2_end:]
print('[OK] Step 2: renderAiPage replaced')

# === Step 3: Remove aiPrevPage and aiNextPage functions ===
p3_start = html.find('function aiPrevPage()')
if p3_start >= 0:
    # Find the line that starts with "// ===" after aiNextPage
    rest = html[p3_start:]
    fn_end = rest.find('\n\n// ==')
    if fn_end > 0:
        html = html[:p3_start] + html[p3_start + fn_end:]
        print('[OK] Step 3: Pagination functions removed')
    else:
        # Fallback: find next function
        fn_end = rest.find('\n\nfunction')
        if fn_end > 0:
            html = html[:p3_start] + html[p3_start + fn_end:]
            print('[OK] Step 3: Pagination functions removed (fallback)')
        else:
            print('[WARN] Step 3: Could not find end boundary')
else:
    print('[OK] Step 3: No aiPrevPage found (already removed)')

# Write
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
c1 = html.count('function renderAiChain()')
c2 = html.count('function renderAiPage(container)')
c3 = html.count('function aiPrevPage()')
c4 = html.count('\u6700\u65b0\u5185\u5bb9')
c5 = html.count('\u5386\u53f2\u5185\u5bb9')
c6 = html.count('ai-icon')
print(f'\n=== Verification ===')
print(f'  renderAiChain: {c1} (expected 1)')
print(f'  renderAiPage: {c2} (expected 1)')
print(f'  aiPrevPage: {c3} (expected 0)')
print(f'  \u201c\u6700\u65b0\u5185\u5bb9\u201d: {c4} (expected 1)')
print(f'  \u201c\u5386\u53f2\u5185\u5bb9\u201d: {c5} (expected 1)')
print(f'  ai-icon: {c6} (expected ~10)')
