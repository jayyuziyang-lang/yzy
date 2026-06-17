"""组装 SDXL 完整模型：复用已有的 UNet + 刚下载的其他组件"""
import os, sys, shutil

# 源文件位置
UNET_SRC = "D:/Desktop/每日财经/tools/models/modelscope-sdxl/AI-ModelScope/stable-diffusion-xl-base-1___0/unet/diffusion_pytorch_model.fp16.safetensors"
MS_CACHE = "D:/Desktop/每日财经/tools/models/modelscope-sdxl-full"

# 目标：完整 SDXL 模型目录
DST = "D:/Desktop/每日财经/tools/models/sdxl-complete"

def find_ms_file(filename):
    """在 ModelScope 缓存中查找文件"""
    for root, dirs, files in os.walk(MS_CACHE):
        for f in files:
            if f == os.path.basename(filename):
                full = os.path.join(root, f)
                # 跳过临时文件
                if '._____temp' in full:
                    continue
                # 检查是否是目标文件的匹配路径
                rel = os.path.relpath(full, MS_CACHE)
                if filename in rel or rel.endswith(filename):
                    return full
    return None

def assemble():
    os.makedirs(DST, exist_ok=True)

    # 1. Copy UNet
    print("Copying UNet (4.8GB)...")
    dst_unet = os.path.join(DST, 'unet')
    os.makedirs(dst_unet, exist_ok=True)
    dst_file = os.path.join(dst_unet, 'diffusion_pytorch_model.fp16.safetensors')
    if not os.path.exists(dst_file):
        shutil.copy2(UNET_SRC, dst_file)
        print(f"  [OK] UNet -> {dst_file}")
    else:
        print(f"  [SKIP] UNet already exists")

    # Also copy unet config if it exists in MS cache
    unet_config = find_ms_file('unet/config.json')
    if unet_config:
        shutil.copy2(unet_config, os.path.join(dst_unet, 'config.json'))
        print(f"  [OK] unet/config.json")

    # 2. Copy all downloaded ModelScope files
    components = [
        'model_index.json',
        'scheduler/scheduler_config.json',
        'text_encoder/config.json',
        'text_encoder/model.fp16.safetensors',
        'text_encoder_2/config.json',
        'text_encoder_2/model.fp16.safetensors',
        'vae/config.json',
        'vae/diffusion_pytorch_model.fp16.safetensors',
        'tokenizer/special_tokens_map.json',
        'tokenizer/tokenizer_config.json',
        'tokenizer/vocab.json',
        'tokenizer/merges.txt',
        'tokenizer_2/special_tokens_map.json',
        'tokenizer_2/tokenizer_config.json',
        'tokenizer_2/vocab.json',
        'tokenizer_2/merges.txt',
    ]

    for comp in components:
        src = find_ms_file(comp)
        if src:
            dst = os.path.join(DST, comp)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                sz = os.path.getsize(dst) / 1024**2
                print(f"  [OK] {comp} ({sz:.0f}MB)")
            else:
                print(f"  [SKIP] {comp}")
        else:
            # Try to find by path pattern
            basename = os.path.basename(comp)
            found = False
            for root, dirs, files in os.walk(MS_CACHE):
                if '._____temp' in root:
                    continue
                for f in files:
                    if f == basename and comp.replace('/', '\\') in os.path.join(root, f).replace('/', '\\'):
                        dst = os.path.join(DST, comp)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if not os.path.exists(dst):
                            shutil.copy2(os.path.join(root, f), dst)
                            print(f"  [OK] {comp} (found by basename)")
                        found = True
                        break
                if found:
                    break
            if not found:
                print(f"  [MISS] {comp}")

    # 3. Verify
    print("\nVerification:")
    model_index = os.path.join(DST, 'model_index.json')
    if os.path.exists(model_index):
        import json
        with open(model_index) as f:
            mi = json.load(f)
        print(f"  model_index.json: {list(mi.keys())}")

    # Check total size
    total = 0
    for root, dirs, files in os.walk(DST):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    print(f"  Total: {total/1024**3:.2f} GB")

    print(f"\nAssembled at: {DST}")
    return DST

if __name__ == '__main__':
    assemble()
