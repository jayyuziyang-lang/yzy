#!/usr/bin/env python3
"""为所有文章添加JS动态返回首页机制，解决相对路径导航不可靠的问题。"""
import sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BACK_JS = '''
<script>
// 动态返回首页 — 根据URL路径深度自动计算，不依赖静态相对路径
document.addEventListener('DOMContentLoaded',function(){
  var back=document.querySelector('.back');
  if(back){
    back.addEventListener('click',function(e){
      e.preventDefault();
      var p=location.pathname.replace(/\\/$/,'').split('/');
      location.href='../'.repeat(Math.max(0,p.length-2))||'.';
    });
  }
});
</script>
</body>'''

def fix_back_link(html_path):
    if not os.path.exists(html_path):
        return False
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    # Check if already has the fix
    if '动态返回首页' in html:
        return False

    # Add the JS before </body>
    if '</body>' in html:
        html = html.replace('</body>', BACK_JS)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False

def main():
    fixed = 0
    skipped = 0

    # Scan daily articles
    for entry in sorted(os.listdir(ROOT)):
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', entry):
            continue
        for session in ('morning', 'evening'):
            html_path = os.path.join(ROOT, entry, 'wechat-publish', session, 'article.html')
            if fix_back_link(html_path):
                print(f'  [OK] {entry}/{session}')
                fixed += 1
            else:
                skipped += 1

    # Scan special articles
    special_dir = os.path.join(ROOT, 'special')
    if os.path.exists(special_dir):
        for topic_dir in sorted(os.listdir(special_dir)):
            if topic_dir.startswith('.'):
                continue
            html_path = os.path.join(special_dir, topic_dir, 'article.html')
            if fix_back_link(html_path):
                print(f'  [OK] special/{topic_dir}')
                fixed += 1
            else:
                skipped += 1

    print(f'\nDone: {fixed} files fixed, {skipped} skipped (already done or no nav)')

if __name__ == '__main__':
    main()
