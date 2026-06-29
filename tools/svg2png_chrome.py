"""Convert SVG to PNG using Chrome headless screenshot"""
import subprocess, os, sys

folder = r'D:\Desktop\简易加注机控制系统'

chrome_paths = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Users\91615\AppData\Local\Google\Chrome\Application\chrome.exe',
]
chrome = None
for p in chrome_paths:
    if os.path.exists(p):
        chrome = p
        break

if not chrome:
    print('Chrome not found, trying Edge...')
    chrome_paths = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    ]
    for p in chrome_paths:
        if os.path.exists(p):
            chrome = p
            break

if not chrome:
    print('No browser found')
    sys.exit(1)

print(f'Using: {chrome}')

files = ['简易加注机控制系统梯形图.svg', '简易加注机控制系统软件流程图.svg']

for f in files:
    svg_path = os.path.join(folder, f)
    png_path = svg_path.replace('.svg', '.png')
    abs_svg = os.path.abspath(svg_path)

    # Write HTML wrapper
    html_path = svg_path.replace('.svg', '_temp.html')
    html_content = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:white;">
<object data="file:///{abs_svg.replace(chr(92), '/')}" type="image/svg+xml" style="width:100%;">
</object>
</body></html>'''

    with open(html_path, 'w', encoding='utf-8') as fh:
        fh.write(html_content)

    abs_html = os.path.abspath(html_path)

    # Determine window size based on viewBox
    # ladder: 820x~1195, flowchart: 650x~900
    if '梯形图' in f:
        winsize = '1700,2400'
    else:
        winsize = '1400,1900'

    cmd = [
        chrome,
        '--headless=new',
        '--disable-gpu',
        '--no-sandbox',
        f'--window-size={winsize}',
        '--hide-scrollbars',
        '--force-device-scale-factor=2',
        f'--screenshot={os.path.abspath(png_path)}',
        f'file:///{abs_html.replace(chr(92), "/")}'
    ]

    print(f'Converting: {f}...')
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if os.path.exists(png_path) and os.path.getsize(png_path) > 1000:
        print(f'  [OK] -> {os.path.basename(png_path)} ({os.path.getsize(png_path)//1024}KB)')
    else:
        print(f'  [FAIL] stderr: {result.stderr[:300]}')

    # Clean up
    if os.path.exists(html_path):
        os.remove(html_path)

print('Done!')
