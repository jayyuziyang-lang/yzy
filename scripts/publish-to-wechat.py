#!/usr/bin/env python3
"""
扬说财经 - 微信公众号发布脚本 v2.0 (方案A: 半自动)
========================================================
个人订阅号无法调用草稿/发布 API，改走「脚本转换 + 人工粘贴发布」流程:

  1. 读取 article.html -> 用 premailer 将 CSS 转为内联样式
  2. SVG 漫画/图表用 Playwright 渲染为 PNG -> 上传到微信 CDN
  3. 替换正文中所有图片 src 为微信 CDN URL
  4. 移除 <audio>/<style>/导航栏 等微信不支持的元素
  5. 生成微信兼容 HTML -> 复制到剪贴板 -> 打开公众号后台

用法:
  python scripts/publish-to-wechat.py --date 2026-07-24 --edition morning
  python scripts/publish-to-wechat.py --date 2026-07-24 --edition morning --no-browser
  python scripts/publish-to-wechat.py --date 2026-07-24 --edition morning --no-clipboard
"""

import os
import sys
import json
import argparse
import time
import re
import logging
import subprocess
import webbrowser
from pathlib import Path
from io import BytesIO

# 屏蔽 premailer/cssutils 的 CSS 2.1 兼容性警告
logging.getLogger("cssutils").setLevel(logging.CRITICAL)
logging.getLogger("premailer").setLevel(logging.CRITICAL)

import requests
from premailer import Premailer
from PIL import Image
from playwright.sync_api import sync_playwright

# -- 配置 ---------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WECHAT_APPID = "wx4c34a89cf90193a0"
WECHAT_SECRET = "c76b65bfada2d4ca24c37faaddaf92d9"
WECHAT_API_BASE = "https://api.weixin.qq.com"
WECHAT_BACKEND_URL = "https://mp.weixin.qq.com"

# 公众号作者名
AUTHOR_NAME = "小财"

# -- Token 缓存 ----------------------------------------
_token_cache = {"token": None, "expires_at": 0}


def get_access_token() -> str:
    """获取微信公众号 access_token（带缓存，2小时有效）"""
    global _token_cache
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 300:
        return _token_cache["token"]

    resp = requests.get(
        f"{WECHAT_API_BASE}/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": WECHAT_APPID,
            "secret": WECHAT_SECRET,
        },
        timeout=15,
    )
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"获取 access_token 失败: {data}")

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 7200)
    return _token_cache["token"]


# -- Playwright 浏览器实例（懒加载）--------------------
_playwright = None
_browser = None


def _get_browser():
    global _playwright, _browser
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)
    return _browser


def svg_to_png_bytes(svg_path: Path) -> bytes:
    """将 SVG 文件转为 PNG bytes（Playwright 无头浏览器渲染）"""
    browser = _get_browser()
    page = browser.new_page(viewport={"width": 900, "height": 600})

    svg_content = svg_path.read_text(encoding="utf-8")
    # 提取 viewBox 尺寸
    vb_match = re.search(r'viewBox="[^"]*\d+\s+\d+\s+(\d+)\s+(\d+)"', svg_content)
    width = int(vb_match.group(1)) if vb_match else 768
    height = int(vb_match.group(2)) if vb_match else 512

    html_wrapper = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center;
         width: {width}px; height: {height}px; }}
  svg {{ max-width: 100%; height: auto; }}
</style></head><body>{svg_content}</body></html>"""

    page.set_content(html_wrapper)
    svg_elem = page.locator("svg")
    screenshot = svg_elem.screenshot(type="png")
    page.close()
    return screenshot


def _cleanup_browser():
    global _browser, _playwright
    try:
        if _browser:
            _browser.close()
        if _playwright:
            _playwright.stop()
    except Exception:
        pass


# -- 图片处理 ------------------------------------------
def optimize_image(filepath: Path) -> BytesIO:
    """读取图片（SVG 用 Playwright 先渲染为 PNG），压缩/优化后返回 BytesIO"""
    ext = filepath.suffix.lower()

    if ext == ".svg":
        png_bytes = svg_to_png_bytes(filepath)
        img = Image.open(BytesIO(png_bytes)).convert("RGB")
        out = BytesIO()
        img.save(out, format="JPEG", quality=85, optimize=True)
        out.seek(0)
        return out
    else:
        img = Image.open(filepath)
        out = BytesIO()
        fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
        if fmt == "JPEG":
            img = img.convert("RGB")
            img.save(out, format="JPEG", quality=85, optimize=True)
        else:
            img.save(out, format="PNG", optimize=True)
        out.seek(0)
        if out.getbuffer().nbytes > 2 * 1024 * 1024:
            img = img.convert("RGB")
            out = BytesIO()
            img.save(out, format="JPEG", quality=80, optimize=True)
        out.seek(0)
        return out


def upload_content_image(filepath: Path, token: str) -> str:
    """
    上传图文消息内的图片 -> 返回微信 CDN URL
    API: POST /cgi-bin/media/uploadimg
    """
    url = f"{WECHAT_API_BASE}/cgi-bin/media/uploadimg?access_token={token}"
    img_data = optimize_image(filepath)

    resp = requests.post(
        url,
        files={"media": (f"{filepath.stem}.jpg", img_data, "image/jpeg")},
        timeout=60,
    )
    data = resp.json()
    if "url" not in data:
        raise RuntimeError(f"上传图片失败 {filepath.name}: {data}")
    return data["url"]


# -- HTML 适配 -----------------------------------------
def extract_title(html: str) -> str:
    """从 HTML <title> 中提取文章标题"""
    m = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    return m.group(1).strip() if m else "扬说财经"


def extract_digest(html: str, max_len: int = 120) -> str:
    """从正文生成摘要"""
    # 先去 <style>/<script>/<head> 再提取文本
    clean = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    clean = re.sub(r"<script[^>]*>.*?</script>", "", clean, flags=re.DOTALL)
    clean = re.sub(r"<head[^>]*>.*?</head>", "", clean, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", clean)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[:max_len - 1] + "..."
    return text


def resolve_image_path(src: str, article_dir: Path) -> Path | None:
    """解析图片 src 为本地路径"""
    if src.startswith("http://") or src.startswith("https://"):
        return None
    if src.startswith("data:"):
        return None
    return (article_dir / src).resolve()


def adapt_html_for_wechat(html_path: Path) -> dict:
    """
    将 article.html 适配为微信兼容格式。

    返回: {
        "title": str,
        "digest": str,
        "content": str,
        "image_map": dict,
        "image_count": int,
    }
    """
    raw_html = html_path.read_text(encoding="utf-8")
    article_dir = html_path.parent

    # 提取标题（限制 64 字，微信允许多一点）
    title = extract_title(raw_html)
    if len(title) > 64:
        title = title[:62] + "..."

    # 提取摘要
    digest = extract_digest(raw_html)

    # -- CSS 内联 --
    try:
        pm = Premailer(
            raw_html,
            base_url=str(article_dir) + "/",
            preserve_internal_links=True,
            remove_classes=False,
            strip_important=False,
        )
        inlined = pm.transform()
    except Exception as e:
        print(f"  [WARN] premailer 转换失败 ({e})，使用原始 HTML")
        inlined = raw_html

    # -- 移除微信不支持的标签 --
    removals = [
        (r"<style[^>]*>.*?</style>", ""),
        (r"<script[^>]*>.*?</script>", ""),
        (r"<audio[^>]*>.*?</audio>", ""),
        (r"<link[^>]*>", ""),
        (r"<meta[^>]*>", ""),
        # 移除导航栏
        (r'<div[^>]*class="[^"]*top-nav[^"]*"[^>]*>.*?</div>\s*</div>', ""),
        # 移除音频播放器区域
        (r'<div[^>]*class="[^"]*player[^"]*"[^>]*>.*?</div>\s*</div>', ""),
        # 移除播放器 SVG 图标
        (r'<div[^>]*class="[^"]*player-icon[^"]*"[^>]*>.*?</div>', ""),
    ]
    for pattern, replacement in removals:
        inlined = re.sub(pattern, replacement, inlined, flags=re.DOTALL)

    # -- 提取 body 内容 --
    body_match = re.search(r"<body[^>]*>(.*?)</body>", inlined, re.DOTALL)
    body_html = body_match.group(1).strip() if body_match else inlined

    # -- 收集需上传的图片 --
    image_map = {}
    img_srcs = re.findall(r'<img[^>]+src="([^"]+)"', body_html)

    for src in img_srcs:
        local_path = resolve_image_path(src, article_dir)
        if local_path and local_path.exists():
            image_map[src] = local_path

    return {
        "title": title,
        "digest": digest,
        "content": body_html,
        "image_map": image_map,
        "image_count": len(image_map),
    }


# -- 剪贴板 --------------------------------------------
def copy_to_clipboard(text: str) -> bool:
    """将文本复制到系统剪贴板（跨平台）"""
    try:
        if sys.platform == "win32":
            # Windows: 用 PowerShell 设置剪贴板
            process = subprocess.Popen(
                ["powershell", "-Command", "Set-Clipboard", "-Value", "$input"],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            process.communicate(input=text.encode("utf-16-le"))
            return process.returncode == 0
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            return True
        else:
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=True)
            return True
    except Exception as e:
        print(f"  [WARN] 复制到剪贴板失败: {e}")
        return False


# -- 进度条 --------------------------------------------
def progress_bar(current: int, total: int, label: str = "") -> None:
    pct = current / total * 100 if total else 100
    bar_len = 30
    filled = int(bar_len * current / total) if total else bar_len
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"\r  [{bar}] {current}/{total} {pct:.0f}% {label}", end="", flush=True)
    if current >= total:
        print()


# -- 主流程 --------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="扬说财经 - 微信公众号发布 (方案A: 半自动)")
    parser.add_argument("--date", default=None, help="日期 YYYY-MM-DD")
    parser.add_argument("--edition", default=None,
                        choices=["morning", "evening", "special"],
                        help="版次")
    parser.add_argument("--path", default=None,
                        help="直接指定 article.html 路径（替代 --date/--edition）")
    parser.add_argument("--no-browser", action="store_true",
                        help="不自动打开公众号后台")
    parser.add_argument("--no-clipboard", action="store_true",
                        help="不复制到剪贴板")
    parser.add_argument("--no-upload", action="store_true",
                        help="跳过图片上传（调试用）")
    args = parser.parse_args()

    # 定位文章目录
    if args.path:
        html_path = Path(args.path).resolve()
        if not html_path.exists():
            print(f"[FAIL] 文章不存在: {html_path}")
            sys.exit(1)
        article_dir = html_path.parent
    elif args.date and args.edition:
        article_dir = PROJECT_ROOT / args.date / "wechat-publish" / args.edition
        html_path = article_dir / "article.html"
    else:
        print("[FAIL] 需要指定 --path 或 (--date + --edition)")
        sys.exit(1)

    if not html_path.exists():
        print(f"[FAIL] 文章不存在: {html_path}")
        sys.exit(1)

    print("=" * 60)
    print("  扬说财经 - 微信公众号发布 (方案A)")
    if args.path:
        print(f"  路径: {html_path}")
    else:
        print(f"  日期: {args.date}  版次: {args.edition}")
    print("=" * 60)

    # ---- Phase 1: HTML 适配 ----
    print("\n--- Phase 1: HTML 适配 ---")
    adapted = adapt_html_for_wechat(html_path)
    print(f"  标题: {adapted['title']}")
    print(f"  摘要: {adapted['digest'][:60]}...")
    print(f"  图片: {adapted['image_count']} 张")

    # ---- Phase 2: 上传图片 ----
    content = adapted["content"]
    if not args.no_upload and adapted["image_count"] > 0:
        print(f"\n--- Phase 2: 上传图片到微信 CDN ({adapted['image_count']} 张) ---")
        token = get_access_token()
        uploaded = {}
        failed = []

        for i, (orig_src, local_path) in enumerate(adapted["image_map"].items(), 1):
            fname = local_path.name
            try:
                progress_bar(i - 1, adapted["image_count"], fname)
                wechat_url = upload_content_image(local_path, token)
                uploaded[orig_src] = wechat_url
                print(f"  [OK] [{i}/{adapted['image_count']}] {fname}")
            except Exception as e:
                failed.append(fname)
                print(f"  [FAIL] [{i}/{adapted['image_count']}] {fname}: {e}")

        # 替换 HTML 中的图片 src
        for orig_src, wechat_url in uploaded.items():
            content = content.replace(f'src="{orig_src}"', f'src="{wechat_url}"')
            abs_src = "file://" + str(adapted["image_map"][orig_src].resolve())
            content = content.replace(f'src="{abs_src}"', f'src="{wechat_url}"')

        print(f"\n  成功: {len(uploaded)}/{adapted['image_count']} 张")
        if failed:
            print(f"  [WARN] 失败: {', '.join(failed)}")
            print(f"  [WARN] 失败图片保留本地路径, 需手动上传")
    else:
        print(f"\n--- Phase 2: 图片上传 (跳过) ---")
        print(f"  注意: HTML 中图片仍为本地路径, 需手动处理")

    # ---- Phase 3: 生成输出 ----
    print(f"\n--- Phase 3: 生成输出 ---")

    # 保存适配后的 HTML 到文件
    output_path = article_dir / "article-wechat.html"
    output_path.write_text(content, encoding="utf-8")
    print(f"  [OK] 微信兼容 HTML 已保存: {output_path}")

    # 生成发布说明文件
    brief_path = article_dir / "PUBLISH_BRIEF.md"
    brief = f"""# 微信公众号发布清单

## 文章信息
- **日期**: {args.date}
- **版次**: {args.edition}
- **标题**: {adapted['title']}
- **摘要**: {adapted['digest']}

## 操作步骤
1. 打开 [微信公众号后台]({WECHAT_BACKEND_URL}) -> 创作管理 -> 图文消息 -> 新建
2. 粘贴剪贴板中的 HTML（或从 `article-wechat.html` 复制全部内容）
3. 在微信编辑器中检查排版效果
4. 上传封面图: `comic/panel-001.svg` (如有)
5. 设置作者: {AUTHOR_NAME}
6. 点击"保存为草稿" -> 预览 -> 确认无误 -> 发布

## 图片状态
- 已上传到微信 CDN: {adapted['image_count']} 张
- 图片 URL 已自动替换为微信 CDN 地址
"""
    brief_path.write_text(brief, encoding="utf-8")
    print(f"  [OK] 发布清单已保存: {brief_path}")

    # ---- Phase 4: 复制到剪贴板 ----
    if not args.no_clipboard:
        print(f"\n--- Phase 4: 复制到剪贴板 ---")
        if copy_to_clipboard(content):
            print(f"  [OK] HTML 已复制到剪贴板, 可直接 Ctrl+V 粘贴到微信编辑器")
        else:
            print(f"  [WARN] 剪贴板复制失败, 请手动从 article-wechat.html 复制")

    # ---- Phase 5: 打开后台 ----
    if not args.no_browser:
        print(f"\n--- Phase 5: 打开微信公众号后台 ---")
        webbrowser.open(WECHAT_BACKEND_URL)
        print(f"  [OK] 浏览器已打开 {WECHAT_BACKEND_URL}")

    # ---- Phase 6: 清理 ----
    _cleanup_browser()

    print("\n" + "=" * 60)
    print("  [OK] 转换完成! 接下来的操作:")
    print("  1. 在微信后台点击「新建图文消息」")
    print("  2. Ctrl+V 粘贴内容到编辑器")
    print("  3. 上传封面图 + 设置摘要")
    print("  4. 保存草稿 -> 预览 -> 发布")
    print("=" * 60)


if __name__ == "__main__":
    main()
