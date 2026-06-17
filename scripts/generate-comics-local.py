#!/usr/bin/env python3
"""
扬说财经 · 本地漫画生成管线 v2.0
基于 SD 1.5 / SDXL + RTX 5070 Ti 本地推理，生成中国日报风格的新闻编辑漫画。

SDXL 优先（1024×1024 原生分辨率，更好构图）；SD 1.5 作为降级（768×512）。
SD 1.5 作为快速模式（3s/张），SDXL 为质量模式（~8s/张）。

用法:
  python generate-comics-local.py --topic fomc
  python generate-comics-local.py --batch fomc boj gold --model sdxl
  python generate-comics-local.py --prompt "FOMC like a lighthouse" --output test.png
"""

import os
import sys
import argparse
import json
import gc
from pathlib import Path
from datetime import datetime

# ── 环境配置 ──────────────────────────────────────────
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = 'D:/CACHE/hf'
os.environ['HUGGINGFACE_HUB_CACHE'] = 'D:/CACHE/hf'
os.environ['TRANSFORMERS_CACHE'] = 'D:/CACHE/hf'

import torch
import numpy as np
from PIL import Image

# ── 样式定义 ──────────────────────────────────────────

# 中国日报海外版头版插画风格（李旻工笔线描风）
CHINADAILY_STYLE = {
    "name": "中国日报工笔插画风",
    "positive_prefix": (
        "editorial illustration, China Daily Global Edition style, "
        "gongbi ink line technique by Li Min, fine flowing outlines, "
        "white background, muted earth tones and subtle blues, "
        "visual metaphor, hand-painted gouache texture, "
        "professional newspaper editorial artwork"
    ),
    "negative": (
        "photograph, photorealistic, 3D render, CGI, anime, manga, cartoon, "
        "chibi, kawaii, dark background, black background, cluttered, messy, "
        "text, letters, words, numbers, watermark, signature, logo, "
        "data chart, bar chart, graph, dashboard, infographic, "
        "low quality, blurry, pixelated, jpeg artifacts, ugly, deformed"
    )
}

# 水粉手绘风格（备用）
GOUACHE_STYLE = {
    "name": "水粉手绘风格",
    "positive_prefix": (
        "editorial cartoon, gouache painting, hand-drawn illustration, "
        "professional newspaper editorial style, sophisticated visual metaphor, "
        "clean composition, muted professional colors, white background, "
        "expressive brushwork, artistic, not photography"
    ),
    "negative": "photograph, photorealistic, 3D, CGI, dark background, text, watermark"
}

# ── 漫画主题提示词库 ──────────────────────────────────

COMIC_THEMES = {
    "fomc": {
        "topic_cn": "FOMC·灯塔航行",
        "positive": (
            "A majestic lighthouse on a rocky cliff at dawn, powerful golden beam "
            "cutting through fog, cargo ships navigating stormy seas below, "
            "the beam creating a bright path on the water, dramatic sky, "
            "metaphor for central bank guidance through uncertainty"
        ),
    },
    "boj": {
        "topic_cn": "BOJ·温度计冲破冰点",
        "positive": (
            "A glass thermometer rising through cracked ice on a frozen lake, "
            "red mercury pushing past zero, cherry blossoms framing the scene, "
            "Mount Fuji in the distance, metaphor for Japan emerging from deflation"
        ),
    },
    "gold": {
        "topic_cn": "黄金·金山与沙丘",
        "positive": (
            "A golden mountain on solid rock foundation, contrasted with a shimmering "
            "sand dune mirage beside it, Chinese ink wash landscape style, "
            "scholars in robes observing both, metaphor for real value versus speculation"
        ),
    },
    "spacex": {
        "topic_cn": "SpaceX·火箭拖锚链",
        "positive": (
            "A sleek rocket ascending through clouds, heavy iron anchor chain dragging behind, "
            "chain links shaped like dollar signs, storm clouds below, clear sky above, "
            "metaphor for innovation burdened by constraints"
        ),
    },
    "market_rally": {
        "topic_cn": "市场反弹·春笋破土",
        "positive": (
            "Vigorous bamboo shoots pushing through melting winter snow, "
            "each shoot a different shade of green, warm spring sunlight, "
            "traditional Chinese ink brush painting, upward dynamic growth"
        ),
    },
    "volatility": {
        "topic_cn": "波动率·惊弓之鸟",
        "positive": (
            "Birds taking sudden flight from a pine tree, startled by a bowstring twang, "
            "scattering in all directions, traditional Chinese gongbi painting, "
            "autumn golden leaves, metaphor for market overreaction"
        ),
    },
    "trade_war": {
        "topic_cn": "贸易博弈·围棋对弈",
        "positive": (
            "A go board as a vast landscape, black and white stones forming territorial "
            "patterns, two hands placing stones from opposite sides, "
            "misty valleys between territories, East Asian aesthetic"
        ),
    },
    "ai_boom": {
        "topic_cn": "AI浪潮·大江东去",
        "positive": (
            "A mighty river of glowing data streams flowing through dramatic landscape, "
            "traditional Chinese painting style, boats with chip-shaped sails, "
            "waterfalls representing breakthroughs, flowing toward bright horizon"
        ),
    },
}

# ── 模型加载 ──────────────────────────────────────────

_pipe = None
_pipe_model_type = None  # "sd15" or "sdxl"

# SD 1.5 路径
SD15_CACHE = "D:/CACHE/hf/models--runwayml--stable-diffusion-v1-5/snapshots/451f4fe16113bff5a5d2269ed5ad43b0592e9a14"

# SDXL 路径（按优先级）
SDXL_CANDIDATES = [
    "D:/Desktop/每日财经/tools/models/sdxl-complete",
    "D:/Desktop/每日财经/tools/models/models--stabilityai--stable-diffusion-xl-base-1.0/snapshots/462165984030d82259a11f4367a4eed129e94a7b",
]


def _check_sdxl_unet(dirpath):
    """检查 SDXL 目录中是否有 UNet 权重（真正可用的标志）"""
    unet_path = os.path.join(dirpath, "unet", "diffusion_pytorch_model.fp16.safetensors")
    if os.path.exists(unet_path) and os.path.getsize(unet_path) > 100_000_000:  # >100MB
        return True
    unet_path = os.path.join(dirpath, "unet", "diffusion_pytorch_model.safetensors")
    if os.path.exists(unet_path) and os.path.getsize(unet_path) > 100_000_000:
        return True
    return False


def _detect_best_model():
    """自动检测最佳可用模型，返回 (model_type, model_path)"""
    # 优先 SDXL（质量更好）
    for path in SDXL_CANDIDATES:
        if os.path.exists(os.path.join(path, "model_index.json")) and _check_sdxl_unet(path):
            return "sdxl", path

    # 回退 SD 1.5
    if os.path.exists(os.path.join(SD15_CACHE, "model_index.json")):
        return "sd15", SD15_CACHE

    # 最后尝试在线
    return "online", None


def load_pipeline(force_reload=False, prefer_model=None):
    """加载 SD pipeline（单例模式，SDXL 优先）

    Args:
        force_reload: 强制重新加载
        prefer_model: "sd15" | "sdxl" | None（自动检测）
    """
    global _pipe, _pipe_model_type

    if _pipe is not None and not force_reload:
        if prefer_model and prefer_model != _pipe_model_type:
            # 需要切换模型类型
            unload_pipeline()
        else:
            return _pipe, _pipe_model_type

    if _pipe is not None:
        unload_pipeline()

    if prefer_model:
        model_type = prefer_model
        if model_type == "sdxl":
            for path in SDXL_CANDIDATES:
                if os.path.exists(os.path.join(path, "model_index.json")):
                    model_path = path
                    break
            else:
                print("[WARN] SDXL not available, falling back to SD 1.5")
                model_type = "sd15"
                model_path = SD15_CACHE
        else:
            model_path = SD15_CACHE
    else:
        model_type, model_path = _detect_best_model()

    print(f"[LOAD] 加载 {model_type.upper()} 模型...")

    if model_type == "sdxl":
        from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler

        pipe = StableDiffusionXLPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
            local_files_only=True,
        )
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

    elif model_type == "sd15":
        from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler

        pipe = StableDiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
            local_files_only=True,
        )
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

    else:
        raise RuntimeError("无可用的本地模型，请先下载")

    # 内存优化
    pipe.vae.enable_slicing()
    if model_type == "sd15":
        pipe.vae.enable_tiling()
    else:
        # SDXL VAE 在 fp16 下容易产生 NaN，开启 tiling 改善数值稳定性
        pipe.vae.enable_tiling()

    pipe = pipe.to("cuda")

    # SDXL VAE fp16 -> NaN：在 CUDA 后上转 VAE 为 fp32
    # 但在 generate_comic 中需要手动处理 latent 类型转换
    if model_type == "sdxl":
        pipe.vae.to(torch.float32)

    _pipe = pipe
    _pipe_model_type = model_type
    vram_used = torch.cuda.memory_allocated() / 1024**3
    print(f"[OK] {model_type.upper()} 加载完成 | 显存: {vram_used:.1f} GB")
    return pipe, model_type


def unload_pipeline():
    """释放显存"""
    global _pipe
    if _pipe is not None:
        del _pipe
        _pipe = None
        gc.collect()
        torch.cuda.empty_cache()
        print("[CLEAN] 显存已释放")


# ── 提示词构建 ────────────────────────────────────────

def build_prompt(topic_key=None, custom_positive="", style="chinadaily", extra_elements=""):
    """构建完整的 SDXL 提示词"""
    style_config = CHINADAILY_STYLE if style == "chinadaily" else GOUACHE_STYLE

    # 获取主题提示词
    if topic_key and topic_key in COMIC_THEMES:
        topic_positive = COMIC_THEMES[topic_key]["positive"]
    else:
        topic_positive = custom_positive

    # 组合
    positive = (
        f"{style_config['positive_prefix']}, "
        f"{topic_positive}"
    )

    if extra_elements:
        positive += f", {extra_elements}"

    negative = style_config["negative"]

    return positive, negative


# ── 图像生成 ──────────────────────────────────────────

def generate_comic(
    prompt_positive="",
    prompt_negative="",
    topic_key=None,
    style="chinadaily",
    width=None,
    height=None,
    steps=None,
    guidance_scale=None,
    seed=None,
    output_path=None,
    prefer_model=None,
):
    """生成一张漫画（自动选择最佳模型）

    SDXL 默认: 1024×768, 30步, guidance=7.0
    SD 1.5 默认: 768×512, 25步, guidance=8.0
    """
    pipe, model_type = load_pipeline(prefer_model=prefer_model)

    # SDXL 默认参数（更高原生分辨率）
    if model_type == "sdxl":
        width = width or 1024
        height = height or 768
        steps = steps or 30
        guidance_scale = guidance_scale or 7.0
    else:
        width = width or 768
        height = height or 512
        steps = steps or 25
        guidance_scale = guidance_scale or 8.0

    # 构建提示词
    if not prompt_positive:
        prompt_positive, prompt_negative = build_prompt(topic_key=topic_key, style=style)

    # SDXL 需要单独处理 negative prompt（两个 text encoder 都接收）
    if model_type == "sdxl" and prompt_negative:
        # SDXL 使用负提示词的完整形式
        pass  # SDXL pipeline 自动处理

    # 设置随机种子
    if seed is None:
        seed = torch.seed() & 0xFFFFFFFF

    generator = torch.Generator(device="cuda").manual_seed(seed)

    print(f"[DRAW] [{model_type.upper()}] {topic_key or 'custom'}")
    print(f"   尺寸: {width}×{height}, 步数: {steps}, CFG: {guidance_scale}, 种子: {seed}")

    # SDXL: output latent + manual fp32 VAE decode (avoids fp16 NaN)
    if model_type == "sdxl":
        with torch.autocast("cuda"):
            result = pipe(
                prompt=prompt_positive,
                negative_prompt=prompt_negative,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator,
                output_type="latent",
            )
        # Manual decode: cast latent to fp32 for VAE, then cast result back
        latents = result.images  # actually latents when output_type="latent"
        latents_f32 = latents.to(torch.float32)
        with torch.no_grad():
            image = pipe.vae.decode(latents_f32, return_dict=False)[0]
        # Convert back to PIL
        image = pipe.image_processor.postprocess(image, output_type="pil")[0]
    else:
        result = pipe(
            prompt=prompt_positive,
            negative_prompt=prompt_negative,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            generator=generator,
        )
        image = result.images[0]

    # 保存
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        image.save(output_path, "PNG", optimize=False)
        print(f"[OK] 保存: {output_path} ({os.path.getsize(output_path)/1024:.0f} KB)")
    else:
        output_dir = Path("D:/Desktop/每日财经/demo/new-charts")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_name = topic_key or "custom"
        output_path = output_dir / f"comic-{topic_name}-{model_type}-{timestamp}.png"
        image.save(str(output_path), "PNG", optimize=False)
        print(f"[OK] 保存: {output_path} ({os.path.getsize(output_path)/1024:.0f} KB)")

    return image, output_path, model_type


# ── 批量生成 ──────────────────────────────────────────

def generate_article_comics(topic_keys, output_dir=None, style="chinadaily", prefer_model=None):
    """为一篇文章批量生成多张漫画"""
    pipe, model_type = load_pipeline(prefer_model=prefer_model)
    results = []

    if output_dir is None:
        output_dir = Path("D:/Desktop/每日财经/demo/new-charts")
    else:
        output_dir = Path(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    # SDXL 默认更高分辨率
    if model_type == "sdxl":
        width, height, steps, cfg = 1024, 768, 30, 7.0
    else:
        width, height, steps, cfg = 768, 512, 25, 8.0

    for i, topic_key in enumerate(topic_keys):
        print(f"\n{'='*50}")
        theme_name = COMIC_THEMES.get(topic_key, {}).get('topic_cn', topic_key)
        print(f"漫画 {i+1}/{len(topic_keys)}: {theme_name} [{model_type.upper()}]")
        print(f"{'='*50}")

        positive, negative = build_prompt(topic_key=topic_key, style=style)

        filename = output_dir / f"comic-{i+1:02d}-{topic_key}-{model_type}.png"
        image, path, _ = generate_comic(
            prompt_positive=positive,
            prompt_negative=negative,
            topic_key=topic_key,
            style=style,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=cfg,
            output_path=str(filename),
            prefer_model=prefer_model,
        )
        results.append({
            "topic_key": topic_key,
            "path": str(path),
            "size": f"{image.width}×{image.height}",
            "model": model_type,
        })

    return results


# ── CLI ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="扬说财经 · 本地漫画生成管线 v2.0")
    parser.add_argument("--topic", type=str, help="单个主题 key（fomc/boj/gold/spacex 等）")
    parser.add_argument("--prompt", type=str, help="自定义正面提示词")
    parser.add_argument("--negative", type=str, help="自定义负面提示词")
    parser.add_argument("--output", type=str, help="输出路径")
    parser.add_argument("--style", type=str, default="chinadaily", choices=["chinadaily", "gouache"])
    parser.add_argument("--model", type=str, default=None, choices=["sd15", "sdxl"],
                        help="模型选择（默认自动检测：SDXL 优先）")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--seed", type=int, help="随机种子（可复现）")
    parser.add_argument("--batch", type=str, nargs="+", help="批量生成多个主题")
    parser.add_argument("--list-themes", action="store_true", help="列出所有可用主题")

    args = parser.parse_args()

    if args.list_themes:
        print("可用主题:")
        for key, theme in COMIC_THEMES.items():
            print(f"  {key}: {theme['topic_cn']}")
        return

    if args.batch:
        results = generate_article_comics(args.batch, style=args.style, prefer_model=args.model)
        print(f"\n[SUMMARY] 批量生成完成: {len(results)} 张")
        for r in results:
            print(f"  [{r.get('model', '?')}] {r['topic_key']}: {r['path']} ({r['size']})")
    else:
        generate_comic(
            prompt_positive=args.prompt or "",
            prompt_negative=args.negative or "",
            topic_key=args.topic,
            style=args.style,
            width=args.width,
            height=args.height,
            steps=args.steps,
            seed=args.seed,
            output_path=args.output,
            prefer_model=args.model,
        )

    # 清理
    unload_pipeline()


if __name__ == "__main__":
    main()
