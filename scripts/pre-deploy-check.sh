#!/bin/bash

# =============================================================

# 扬说财经 · 预部署验证脚本（强制，失败时阻塞部署）

# =============================================================



set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"



RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

ERRORS=0



echo -e "${YELLOW}========================================${NC}"

echo -e "${YELLOW}  🔍 预部署验证 (9项)${NC}"

echo -e "${YELLOW}========================================${NC}"



# [1/8] 运行 update-index.py

echo -e "\n📊 [1/8] 运行 update-index.py..."

python scripts/update-index.py || { echo -e "${RED}  ❌ update-index.py 失败${NC}"; ((ERRORS++)); }



# [2/8] articles.js 完整性

echo -e "\n📄 [2/8] 验证 articles.js..."

LATEST_DATE=$(grep -oP 'ARTICLES_LATEST = "\K[^"]+' data/articles.js || echo "")

if [ -z "$LATEST_DATE" ]; then

    echo -e "${RED}  ❌ 无法获取最新日期${NC}"; ((ERRORS++))

else

    echo -e "  ✅ 最新日期: $LATEST_DATE"

fi



# [3/8] index.html 预渲染内容

echo -e "\n🏠 [3/8] 验证 index.html 预渲染..."

EVENING_IN_INDEX=$(grep -c "wechat-publish/evening" index.html || true)

EVENING_IN_JS=$(grep -c '"evening"' data/articles.js || true)

if [ "$EVENING_IN_JS" -gt 0 ] && [ "$EVENING_IN_INDEX" -lt 2 ]; then

    echo -e "${RED}  ❌ 有晚报数据但 index.html 缺少晚报链接！${NC}"; ((ERRORS++))

else

    echo -e "  ✅ 预渲染晚报链接数: $EVENING_IN_INDEX"

fi



# [4/8] 返回首页链接

echo -e "\n🔗 [4/8] 验证返回首页链接..."

BAD=0

# 检查标准文章目录

for f in 20*/wechat-publish/*/article.html; do

    [ ! -f "$f" ] && continue

    LINK=$(grep -oP 'href="[^"]*index\.html"' "$f" 2>/dev/null || echo "")

    if ! echo "$LINK" | grep -q "../../../index.html"; then

        echo -e "  ${RED}❌ $f: $LINK${NC}"; ((BAD++))

    fi

done

# 检查 caijing/ 目录下的文章

for f in caijing/20*/*.html; do

    [ ! -f "$f" ] && continue

    # caijing 目录文章通常位于 caijing/YYYY-MM-DD/ 层级

    LINK=$(grep -oP 'href="[^"]*index\.html"' "$f" 2>/dev/null || echo "")

    if [ -n "$LINK" ] && ! echo "$LINK" | grep -qE "../../index\.html|../../../index\.html"; then

        echo -e "  ${YELLOW}⚠️ $f: $LINK (caijing目录, 手动确认)${NC}"

    fi

done

[ "$BAD" -eq 0 ] && echo -e "  ✅ 所有链接正确" || echo -e "  ${RED}❌ $BAD 个链接异常${NC}"



# [5/8] 模板占位符

echo -e "\n🧹 [5/8] 检查模板占位符..."

PH_ERRORS=0

for f in index.html 20*/wechat-publish/*/article.html caijing/20*/article.html; do

    [ ! -f "$f" ] && continue

    PH=$(grep -n '{{' "$f" 2>/dev/null | grep -v '//' || true)

    if [ -n "$PH" ]; then

        echo -e "  ${RED}❌ $f 发现占位符:${NC}"

        echo "$PH" | while read line; do echo "    $line"; done

        ((PH_ERRORS++))

    fi

done

[ "$PH_ERRORS" -eq 0 ] && echo -e "  ✅ 所有文件无占位符残留" || ((ERRORS++))



# [6/8] git 状态

echo -e "\n📦 [6/8] git 状态..."

echo -e "  $(git status --porcelain 2>/dev/null | wc -l) 个待提交文件"



# [7/8] 图表质量校验（运行 generate-charts.py 的质量门禁）

echo -e "\n📊 [7/8] 图表质量校验..."

if python scripts/generate-charts.py 2>/dev/null; then

    echo -e "  ✅ 图表生成成功 + 质量门禁通过"

else

    echo -e "  ${RED}❌ 图表质量门禁未通过${NC}"

    echo "  python scripts/generate-charts.py 报错，请先修复"

    ((ERRORS++))

fi



# [8/8] 综合审核（audit-article.py — 自动检测版次）

echo -e "\n🔬 [8/8] 综合审核 (audit-article.py)..."

TODAY=$(date +%Y-%m-%d)

AUDIT_OK=0; AUDIT_WARN=0; AUDIT_FAIL=0



# 检查 morning 版是否存在

if [ -d "$TODAY/wechat-publish/morning" ] && [ -f "$TODAY/wechat-publish/morning/article.html" ]; then

    echo -e "  📋 检测到早报 → 运行审核..."

    set +e
    python scripts/audit-article.py --date "$TODAY" --edition morning 2>/dev/null
    AUDIT_RC=$?
    if [ "$AUDIT_RC" -eq 0 ]; then

        echo -e "    ✅ 早报审核通过"

        ((AUDIT_OK++))

    elif [ "$AUDIT_RC" -eq 1 ]; then

        echo -e "  ${YELLOW}    ⚠️ 早报审核有警告${NC}"

        ((AUDIT_WARN++))

    else

        echo -e "  ${RED}    ❌ 早报审核阻塞${NC}"

        ((AUDIT_FAIL++))

    fi

fi
    set -e



# 检查 evening 版是否存在

if [ -d "$TODAY/wechat-publish/evening" ] && [ -f "$TODAY/wechat-publish/evening/article.html" ]; then

    echo -e "  📋 检测到晚报送 → 运行审核..."

    set +e
    python scripts/audit-article.py --date "$TODAY" --edition evening 2>/dev/null
    AUDIT_RC=$?
    if [ "$AUDIT_RC" -eq 0 ]; then

        echo -e "    ✅ 晚报审核通过"

        ((AUDIT_OK++))

    elif [ "$AUDIT_RC" -eq 1 ]; then

        echo -e "  ${YELLOW}    ⚠️ 晚报审核有警告${NC}"

        ((AUDIT_WARN++))

    else

        echo -e "  ${RED}    ❌ 晚报审核阻塞${NC}"

        ((AUDIT_FAIL++))

    fi

fi
    set -e



if [ "$AUDIT_OK" -eq 0 ] && [ "$AUDIT_WARN" -eq 0 ] && [ "$AUDIT_FAIL" -eq 0 ]; then

    echo -e "  ${YELLOW}  ⚠️ 今日无文章（morning/evening均不存在），跳过审核${NC}"

elif [ "$AUDIT_FAIL" -gt 0 ]; then

    echo -e "  ${RED}❌ 综合审核阻塞 — 共 $AUDIT_FAIL 个版次审核失败${NC}"

    ((ERRORS++))

elif [ "$AUDIT_WARN" -gt 0 ]; then

    echo -e "  ${YELLOW}⚠️ 综合审核有警告（$AUDIT_WARN 个版次），请确认后继续${NC}"

else

    echo -e "  ✅ 综合审核全部通过（$AUDIT_OK 个版次）"

fi



# [9/9] 专题文章资产完整性检查

echo -e "\n📚 [9/9] 专题文章资产完整性检查..."

SPECIAL_DIR="$ROOT_DIR/special"

SPECIAL_ERRORS=0

if [ -d "$SPECIAL_DIR" ]; then

    for topic_dir in "$SPECIAL_DIR"/*/; do

        [ ! -d "$topic_dir" ] && continue

        topic_name=$(basename "$topic_dir")

        [[ "$topic_name" == .* ]] && continue



        echo -e "  📖 检查专题: $topic_name"



        # 检查 article.html

        if [ ! -f "$topic_dir/article.html" ]; then

            echo -e "  ${RED}    ❌ 缺少 article.html${NC}"; ((SPECIAL_ERRORS++))

        else

            # 检查返回首页链接

            LINK=$(grep -oP 'href="[^"]*index\.html"' "$topic_dir/article.html" 2>/dev/null || echo "")

            if echo "$LINK" | grep -q "../../index.html"; then

                echo -e "  ${GREEN}    ✅ article.html + 正确返回链接${NC}"

            else

                echo -e "  ${YELLOW}    ⚠️ $topic_dir/article.html: 返回链接异常 ($LINK)${NC}"

            fi

        fi



        # 检查 audio.mp3

        if [ -f "$topic_dir/audio.mp3" ]; then

            AUDIO_SIZE=$(stat -c%s "$topic_dir/audio.mp3" 2>/dev/null || echo 0)

            if [ "$AUDIO_SIZE" -gt 102400 ]; then

                echo -e "  ${GREEN}    ✅ audio.mp3 ($((AUDIO_SIZE/1024))KB)${NC}"

                # 音频完整性检测（2026-06-06 复盘追加）
                AUDIO_DURATION=$(ffprobe -v error -show_entries format=duration \
                    -of default=noprint_wrappers=1:nokey=1 "$topic_dir/audio.mp3" 2>/dev/null || echo 0)
                if [ "$(echo "$AUDIO_DURATION > 60" | bc 2>/dev/null)" = "1" ] || [ "$AUDIO_DURATION" = "0" ]; then
                    if [ "$AUDIO_DURATION" != "0" ]; then
                        echo -e "  ${GREEN}      ├ 时长: $(printf "%.0f" "$AUDIO_DURATION")秒 ($(echo "scale=1; $AUDIO_DURATION/60" | bc)分)${NC}"
                    fi
                else
                    echo -e "  ${YELLOW}    ⚠️ audio.mp3 时长异常 ($AUDIO_DURATION 秒) — 可能损坏或太短${NC}"
                fi
                # 检查文件末尾是否有大量填充字节（损坏标志）
                TAIL_HEX=$(tail -c 100 "$topic_dir/audio.mp3" 2>/dev/null | od -An -tx1 2>/dev/null)
                TAIL_AA=$(echo "$TAIL_HEX" | grep -o 'aa' | wc -l 2>/dev/null || echo 0)
                if [ "$TAIL_AA" -gt 80 ] 2>/dev/null; then
                    echo -e "  ${RED}    ❌ audio.mp3 末尾填充字节过多，文件可能损坏${NC}"; ((SPECIAL_ERRORS++))
                fi

            else

                echo -e "  ${RED}    ❌ audio.mp3 文件过小 ($AUDIO_SIZE 字节)${NC}"; ((SPECIAL_ERRORS++))

            fi

        else

            echo -e "  ${RED}    ❌ 缺少 audio.mp3${NC}"; ((SPECIAL_ERRORS++))

        fi



        # 检查 script.txt

        if [ -f "$topic_dir/script.txt" ]; then

            SCRIPT_WORDS=$(wc -c < "$topic_dir/script.txt" 2>/dev/null || echo 0)

            if [ "$SCRIPT_WORDS" -gt 200 ]; then

                echo -e "  ${GREEN}    ✅ script.txt ($SCRIPT_WORDS 字节)${NC}"

            else

                echo -e "  ${RED}    ❌ script.txt 太短${NC}"; ((SPECIAL_ERRORS++))

            fi

        else

            echo -e "  ${RED}    ❌ 缺少 script.txt${NC}"; ((SPECIAL_ERRORS++))

        fi



        # 检查 comic/ 目录

        if [ -d "$topic_dir/comic" ]; then

            SVG_COUNT=$(ls "$topic_dir/comic/"*.svg 2>/dev/null | wc -l)

            if [ "$SVG_COUNT" -gt 0 ]; then

                echo -e "  ${GREEN}    ✅ comic/ — $SVG_COUNT 个SVG${NC}"



                # Verify SVG references in article match files in comic/

                if [ -f "$topic_dir/article.html" ]; then

                    article_content=$(cat "$topic_dir/article.html")

                    for svg in "$topic_dir/comic/"*.svg; do

                        svg_name=$(basename "$svg")

                        if ! echo "$article_content" | grep -q "$svg_name"; then

                            echo -e "  ${YELLOW}    ⚠️  comic/$svg_name 存在但未被文章引用${NC}"

                        fi

                    done

                    for ref in $(echo "$article_content" | grep -oP 'src="comic/[^"]+\.svg"' | sed 's/src="comic\///;s/"//'); do

                        if [ ! -f "$topic_dir/comic/$ref" ]; then

                            echo -e "  ${RED}    ❌ 文章引用 comic/$ref 但文件不存在${NC}"; ((SPECIAL_ERRORS++))

                        fi

                    done

                fi

            else

                echo -e "  ${YELLOW}    ⚠️ comic/ 目录为空${NC}"

            fi

        else

            echo -e "  ${YELLOW}    ⚠️ 无 comic/ 目录${NC}"

        fi

        echo ""

    done

else

    echo -e "  ${YELLOW}  ⚠️ 无专题目录${NC}"

fi



if [ "$SPECIAL_ERRORS" -gt 0 ]; then

    echo -e "  ${RED}❌ 专题文章资产完整性检查: $SPECIAL_ERRORS 个错误${NC}"

    ((ERRORS+=SPECIAL_ERRORS))

else

    echo -e "  ${GREEN}✅ 专题文章资产完整性检查通过${NC}"

fi

# [9b/9] AI产业链文章检查
echo -e "\n🤖 [9b/9] AI产业链文章检查..."
AI_CHAIN_DIR="$ROOT_DIR/ai-chain"
AI_ERRORS=0

if [ -d "$AI_CHAIN_DIR" ]; then

    for topic_dir in "$AI_CHAIN_DIR"/*/; do
        [ ! -d "$topic_dir" ] && continue
        topic_name=$(basename "$topic_dir")
        [[ "$topic_name" == .* ]] && continue

        echo -e "  📖 检查AI文章: $topic_name"

        # 检查 article.html
        if [ ! -f "$topic_dir/article.html" ]; then
            echo -e "  ${RED}    ❌ 缺少 article.html${NC}"; ((AI_ERRORS++))
        else
            LINK=$(grep -oP 'href="[^"]*index\.html"' "$topic_dir/article.html" 2>/dev/null || echo "")
            if echo "$LINK" | grep -qE "../../index.html"; then
                echo -e "  ${GREEN}    ✅ article.html + 返回链接${NC}"
            else
                echo -e "  ${YELLOW}    ⚠️ $topic_dir/article.html: 返回链接异常 ($LINK)${NC}"
            fi
        fi

        # 检查 images/
        if [ -d "$topic_dir/images" ]; then
            IMG_COUNT=$(ls "$topic_dir/images/"*.png "$topic_dir/images/"*.svg "$topic_dir/images/"*.jpg 2>/dev/null | wc -l)
            if [ "$IMG_COUNT" -gt 0 ]; then
                echo -e "  ${GREEN}    ✅ images/ — $IMG_COUNT 张图片${NC}"
            else
                echo -e "  ${YELLOW}    ⚠️ images/ 目录为空${NC}"
            fi
        else
            echo -e "  ${YELLOW}    ⚠️ 无 images/ 目录${NC}"
        fi
        echo ""
    done

fi

if [ "$AI_ERRORS" -gt 0 ]; then
    echo -e "  ${RED}❌ AI产业链文章检查: $AI_ERRORS 个错误${NC}"
    ((ERRORS+=AI_ERRORS))
else
    echo -e "  ${GREEN}✅ AI产业链文章检查通过${NC}"
fi



# 结果

echo ""

if [ "$ERRORS" -gt 0 ]; then

    echo -e "${RED}========================================${NC}"

    echo -e "${RED}  ❌ 预部署验证失败: $ERRORS 个错误${NC}"

    echo -e "${RED}  修复后重新运行 deploy.sh${NC}"

    echo -e "${RED}========================================${NC}"

    exit 1

else

    echo -e "${GREEN}========================================${NC}"

    echo -e "${GREEN}  ✅ 预部署验证全部通过${NC}"

    echo -e "${GREEN}========================================${NC}"

fi

