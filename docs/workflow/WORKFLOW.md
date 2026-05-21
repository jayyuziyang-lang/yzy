# 扬说财经 · 生产工作流程

## 核心原则

- **早晚分离**：早报和晚报是两次独立的生产调用，互不依赖
- **先审后发**：音频脚本必须经专人审核后才能生成最终音频
- **质量门禁**：每个环节产出后自动运行质量检查，不通过不进入下一环节
- **新闻有源**：每条数据必须标注来源URL，关键数字交叉验证
- **每日复盘**：当天工作结束后运行复盘Agent，问题不过夜
- **持续迭代**：每周至少一次竞争分析+漫画风格评估

---

## 团队架构

扬说财经由 **1位运营总监 (Claude) + 13个AI子Agent** 组成，详见：
- [团队架构与职责](../team/TEAM.md)
- [Agent操作手册](../team/AGENT_HANDBOOK.md)

---

## 每日完整工作流

### 步骤0：运营总监启动新闻采集（用户说"给我今天的早报"）

```bash
# 运营总监执行WebSearch采集新闻
# → 填充 news-collector.sh 生成的模板
# → 运行事实核查
bash scripts/agents/fact-checker.sh
```

### 步骤1：内容策划（运营总监 + 主编Agent协作）
编写：
- `storyboard.json` — 漫画分镜表
- `article.md` — 文章Markdown（≥3000字）
- `article.html` — 发布用HTML（三层结构）

### 步骤2：内容验证
```bash
bash scripts/agents/content-prep.sh morning
```

### 步骤3：生产管线
```bash
bash scripts/morning.sh
```
自动执行：图表 → 品牌 → 漫画 → 脚本 → [人工审核] → 音频

### 步骤4：全量质量检查
```bash
python scripts/quality-check.py
```

### 步骤5：每日复盘（当天工作结束后）
```bash
bash scripts/agents/daily-review.sh
```

---

## 一、早报流程（用户发起）

用户说：*"请给我今天的早报"*

### Phase 1：内容准备（人工 + Claude 协作）

1. 收集当日财经新闻
2. 确定早报主题（英伟达 / A股 / 宏观等）
3. 编写 `storyboard.json`（漫画分镜表）
4. 编写 `article.md` + `article.html`（三层结构文章）

**产出：**
```
wechat-publish/morning/
├── storyboard.json       # 漫画分镜（必须）
├── article.md            # 文章Markdown（必须）
└── article.html          # 文章HTML（必须）
```

### Phase 2：数据图表

```bash
python scripts/generate-charts.py
python scripts/quality-check.py charts
```

**产出：** `docs/charts/*.svg`（5张数据图）

### Phase 3：品牌资产

```bash
python scripts/rebrand-character.py
python scripts/quality-check.py brand
```

**产出：** `docs/assets/*.svg`（含人物图片）

### Phase 4：漫画分镜

```bash
python scripts/upgrade-comic.py
python scripts/quality-check.py comics
```

**产出：** `wechat-publish/morning/comic/panel-*.svg`

### Phase 5：口播脚本

```bash
python scripts/upgrade-audio.py --script-only morning
```

**产出：** `wechat-publish/morning/script.txt`

### → 人工审核脚本

1. 打开 `script.txt` 逐行检查
2. 确认无英文字母、网址、异常符号
3. 如有修改，直接编辑 `script.txt`

### Phase 6：音频生成

```bash
python scripts/upgrade-audio.py --from-script morning
python scripts/quality-check.py audio
```

**产出：** `wechat-publish/morning/audio.mp3`

### Phase 7：全量验证

```bash
python scripts/quality-check.py
```

### 交付物

```
wechat-publish/morning/
├── storyboard.json
├── article.md
├── article.html          # ← 公众号发布内容
├── comic/
│   ├── panel-000.svg ~ panel-004.svg
├── script.txt
└── audio.mp3
```

---

## 二、晚报流程（用户发起）

用户说：*"请给我今天的晚报"*

流程与早报一致，session 替换为 `evening`：

```bash
# Phase 1：内容准备（人工 + Claude）
# 编写 storyboard.json / article.md / article.html

# Phase 2-4：图表 + 品牌 + 漫画
python scripts/generate-charts.py
python scripts/quality-check.py charts
python scripts/rebrand-character.py
python scripts/quality-check.py brand
python scripts/upgrade-comic.py
python scripts/quality-check.py comics

# Phase 5：口播脚本
python scripts/upgrade-audio.py --script-only evening

# → 人工审核 script.txt

# Phase 6-7：音频 + 全量验证
python scripts/upgrade-audio.py --from-script evening
python scripts/quality-check.py
```

---

## 三、快速命令速查

| 用途 | 命令 |
|------|------|
| 早报全流程 | `bash scripts/morning.sh` |
| 晚报全流程 | `bash scripts/evening.sh` |
| 仅出音频脚本 | `python scripts/upgrade-audio.py --script-only morning` |
| 从脚本生成音频 | `python scripts/upgrade-audio.py --from-script evening` |
| 完整质量检查 | `python scripts/quality-check.py` |
| 单模块检查 | `python scripts/quality-check.py audio` |
| 生产状态预览 | `bash scripts/agents/status.sh` |

---

## 四、质量门禁标准

| 检查项 | 通过标准 | 失败处理 |
|--------|----------|----------|
| 品牌资产 | 9项全部通过 | 重新生成品牌资产 |
| 漫画分镜 | 6项全部通过 | 检查SVG文件、storyboard一致性 |
| 文章 | 14项全部通过 | 检查三层结构、断链、MD长度 |
| 图表 | 5项全部通过 | 检查数据源、SVG生成 |
| 音频 | 8项全部通过 | 检查script.txt内容、SSML纯净度 |
| 脚本 | 7项全部通过 | 检查文件完整性 |

---

## 五、故障排除

**"目录不存在"**
```bash
mkdir -p 2026-05-22/wechat-publish/morning/comic
mkdir -p 2026-05-22/wechat-publish/evening/comic
```

**"音频质量不佳"**
1. 编辑 `script.txt` 调整措辞
2. 重新运行 `python scripts/upgrade-audio.py --from-script morning`

**"SVG漫画未更新"**
```bash
python scripts/upgrade-comic.py --dir 2026-05-22/wechat-publish/morning/comic
```

---

## 六、公众号发布检查清单

□ 文章 HTML 在浏览器打开后视觉完整
□ 漫画 SVG 在浏览器中正常渲染
□ 音频 MP3 可正常播放、无杂音
□ 脚本已审核、无英文字母或异常符号
□ 49项质量检查全部通过
□ 所有图片引用为相对路径、无断链
□ 品牌标识（扬说财经）出现在文章中
