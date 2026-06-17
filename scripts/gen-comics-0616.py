"""
6.16早报定制漫画 v4.0 — Dalio风格
对标 Ray Dalio《经济机器是如何运行的》(How the Economic Machine Works)
核心原则：简笔卡通 + 具体物件 + 白板背景 → 一眼就懂
"""
import os, sys, time, gc
os.environ["HF_HOME"] = "D:/CACHE/hf"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
sys.path.insert(0, "D:/Desktop/每日财经/scripts")

import importlib.util
spec = importlib.util.spec_from_file_location("gen", "D:/Desktop/每日财经/scripts/generate-comics-local.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from PIL import Image, ImageDraw, ImageFont

OUT = "D:/Desktop/每日财经/2026-06-16/wechat-publish/morning/comic"
os.makedirs(OUT, exist_ok=True)

# ============================================================
# Dalio 风格 = 简笔涂鸦 + 具体场景 + 白纸背景 + 扁平色块
# 对标「经济机器是如何运行的」：简笔画人物 + 清晰物件 + 无杂物
# ============================================================
STYLE = (
    "simple doodle cartoon illustration, "
    "(hand drawn sketch style:1.3), "
    "stick figure characters, simple bold black outlines, "
    "flat solid colors, educational explainer diagram, "
    "clean white paper texture background, "
)

NEGATIVE = (
    "(photograph:1.8), (3D render:1.6), (realistic:1.5), "
    "(detailed:1.5), (complex:1.4), (abstract art:1.5), "
    "(dark background:1.4), text, watermark, low quality, blurry, deformed"
)

# ============================================================
# 6组漫画 — 每组的隐喻都力求「形象具体，一看就懂」
# ============================================================
COMICS = [
    {
        "id": "01-a股",
        "title": "A股：工厂在冒烟，商场在关门",
        "subtitle": "左边：工厂烟囱冒烟，标牌写「制造业PMI 52↑」// 右边：商场大门紧闭，标牌写「社零增速3%↓」// 中间：一道裂谷 — 生产热、消费冷，这就是结构性矛盾",
        "prompt": (
            STYLE +
            "left side a factory building with smoking chimneys rising steam, "
            "right side a closed shopping mall with shutters down dark windows, "
            "deep crack gap dividing them, sunny sky above, "
            "simple flat colors, mint green and warm orange"
        ),
    },
    {
        "id": "02-美股",
        "title": "美股：牛背上的狂欢，前方的悬崖",
        "subtitle": "一群简笔画小人(交易员)在铜牛背上跳舞狂欢 // 牛的前方就是FOMC悬崖，标牌写「6.16-17 FOMC」// 他们还没看见 — 最大的风险是「觉得自己没有风险」",
        "prompt": (
            STYLE +
            "stick figure tiny people dancing cheering on back of a charging bull statue, "
            "ahead of bull a dangerous cliff edge with sign reading FOMC, "
            "people unaware looking backward celebrating, "
            "clean white background, simple red and grey tones"
        ),
    },
    {
        "id": "03-科技",
        "title": "科技：股价飞上天，基本面还在原地",
        "subtitle": "一个火箭直冲云霄，箭体写「市值$2.5万亿↑42%」// 地面上「基本面」三个字还钉在原地，一根皮筋连接火箭和地面 // 皮筋快拉断了 — 估值能领先基本面多远？",
        "prompt": (
            STYLE +
            "simple cartoon rocket blasting upward into blue sky, "
            "rubber band stretching from rocket back to ground, "
            "ground anchor stuck labeled fundamentals, elastic band about to snap, "
            "clean white background, flat blue and orange colors"
        ),
    },
    {
        "id": "04-国际",
        "title": "国际：两个温度计，一热一冷",
        "subtitle": "两个巨型温度计并肩而立 // 左边(日本)：水银柱冲到顶部，标「日经70000·BOJ加息1%」// 右边(中国)：水银柱偏低，标「通缩压力·等政策」// 一个发烫、一个偏冷 = 亚洲的温差",
        "prompt": (
            STYLE +
            "two giant thermometers standing side by side comparison, "
            "left thermometer red liquid near top labeled Japan hot, "
            "right thermometer blue liquid low level labeled China cold, "
            "simple flat illustration, clean white background, warm red and cool blue"
        ),
    },
    {
        "id": "05-宏观",
        "title": "宏观：六面的骰子还在空中",
        "subtitle": "FOMC会议桌上围坐一圈模糊人影 // 桌上空悬着一个巨大骰子还没落地 // 六个面写着不同的数字(%)，代表不同的利率路径 // 所有人仰头盯着 — 结果落地才算数",
        "prompt": (
            STYLE +
            "simple conference table with faceless stick figures sitting around, "
            "large dice floating suspended midair above table not yet fallen, "
            "each dice face showing percentage symbols, all people looking up waiting, "
            "clean white background, flat grey blue and warm yellow"
        ),
    },
    {
        "id": "06-商品",
        "title": "商品：天平为什么往这边倒？",
        "subtitle": "一座金色天平 // 左边盘子重(利率预期)：放着一排美元符号砝码 // 右边盘子轻(避险情绪)：只有一小簇火苗 // 天平向左倾 — 黄金在$4300，不是因为战争，是因为利率",
        "prompt": (
            STYLE +
            "simple golden balance scale tilted to left side, "
            "left pan heavy with dollar sign weights stacked high, "
            "right pan light with small flame floating above, "
            "oil barrel floating on blue water waves below, "
            "clean white background, warm gold and cool blue tones"
        ),
    },
]


# ============================================================
# 文字标注：白底卡片 + 早报蓝装饰线（同 v3.0）
# ============================================================
def add_text_card(image_path, title, subtitle, output_path):
    raw = Image.open(image_path).convert("RGBA")
    w, h = raw.size

    card_h = 170
    card = Image.new("RGBA", (w, h + card_h), (0, 0, 0, 0))
    card.paste(raw, (0, 0))

    draw = ImageDraw.Draw(card)

    # 白底
    draw.rectangle([(0, h), (w, h + card_h)], fill=(255, 255, 255, 255))

    # 蓝色装饰线
    draw.rectangle([(16, h), (w - 16, h + 4)], fill=(26, 86, 219, 255))

    # 字体
    if os.path.exists("C:/Windows/Fonts/msyhbd.ttc"):
        font_title = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 28)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 21)
    elif os.path.exists("C:/Windows/Fonts/simhei.ttf"):
        font_title = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 28)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 21)
    else:
        font_title = font_sub = ImageFont.load_default()

    # 标题
    draw.text((20, h + 16), title, font=font_title, fill=(26, 86, 219, 255))

    # 副标题（// 换行）
    y = h + 56
    for line in subtitle.split("//"):
        line = line.strip()
        draw.text((20, y), line, font=font_sub, fill=(80, 80, 80, 255))
        y += 27

    result = card.convert("RGB")
    result.save(output_path, "PNG", optimize=False)
    return result


# ============================================================
# 生成
# ============================================================
print("=" * 60)
print("6.16早报漫画 v4.0 — Dalio风格 (简笔涂鸦 + 白底卡片)")
print("=" * 60)

results = []
for c in COMICS:
    sid = c["id"]
    title = c["title"]
    subtitle = c["subtitle"]
    tmp = os.path.join(OUT, f"panel-{sid}-raw.png")
    final = os.path.join(OUT, f"panel-{sid}.png")

    print(f"\n--- {sid}: {title} ---")

    t0 = time.time()
    img, path, mtype = mod.generate_comic(
        prompt_positive=c["prompt"],
        prompt_negative=NEGATIVE,
        style="chinadaily",
        output_path=tmp,
        prefer_model="sd15",
    )
    dt = time.time() - t0

    add_text_card(tmp, title, subtitle, final)
    sz = os.path.getsize(final) / 1024
    print(f"  Done: {dt:.1f}s [{mtype}] | {img.size} | {sz:.0f}KB")

    results.append({"id": sid, "path": final})
    if os.path.exists(tmp):
        os.remove(tmp)

mod.unload_pipeline()
gc.collect()
import torch
torch.cuda.empty_cache()

print(f"\n{'=' * 60}")
print(f"完成: {len(results)}/6 | Dalio风格 (简笔涂鸦+白底卡片)")
for r in results:
    print(f'  <img src="comic/panel-{r["id"]}.png" alt="" style="width:100%">')
