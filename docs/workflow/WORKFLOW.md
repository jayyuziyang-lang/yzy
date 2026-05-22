# 扬说财经 · 生产工作流程 v3.0

> 版本: v3.0 | 更新: 2026-05-22
> 核心变更: 10人Agent团队 + Think块/证据块/四原则审计

---

## 核心原则

- **专职核查**：事实核查员独立运作，可阻塞流水线（v2.0最大教训）
- **独立质检**：质检审查官不参与生产，专门找问题
- **先假设后验证**：每个Agent启动输出假设，完成输出证据
- **早晚分离**：早报和晚报是两次独立的生产调用
- **早晚不重复（v3.1强制规则）**：晚报深度复盘A股 → 次日早报仅做简要数据回顾，聚焦隔夜全球新事件。早报Layer 2严禁重复晚报已深度分析的内容
- **日报读晚报**：生产早报前必须检查前日晚报内容，确保Layer 2不重复
- **新闻有源**：每条数据必须标注来源URL，关键数字交叉验证
- **每日复盘**：附四原则审计，问题不过夜

---

## 五层质量控制体系

```
Layer 1: Agent 2（事实核查员）→ 数据来源追溯 ← 新增独立层
Layer 2: Agent 3（主笔编辑）→ 内容一致性审查  
Layer 3: Agent 4/5/6/7（生产者）→ 各自模块自检
Layer 4: Agent 8（质检审查官）→ 客观证据收集 ← 新增独立层
Layer 5: Claude Code（主编统筹）→ 终审门禁
```

---

## 晚报生产流程（10阶段）

### Phase 0: 环境验证（主编）
```
Think 假设:
1. [工具链可用性假设]
2. [数据源可用性假设]

验证:
→ python --version
→ git status (仓库干净)
→ 生产目录就绪
→ edge-tts 可用 (python -c "import edge_tts")
```

### Phase 1: 新闻采集（Agent 1）
搜索国内外财经新闻，每条必须含来源URL。
输出: `docs/review/news-evening-{YYYY-MM-DD}.md`
完成后输出验证证据块。

### Phase 2: 事实核查（Agent 2）
逐条验证新闻的数据点来源，标记可疑数据。
输出: `docs/review/factcheck-{YYYY-MM-DD}.md`
**发现编造数据 → 阻塞流水线。**

### Phase 3: 主笔编辑（Agent 3）
撰写 article.html + article.md + storyboard.json。
**强制调用Claude Code。**
输出三层结构文章，底部含合规声明。

### Phase 4: 漫画设计（Agent 4）
创建 3-4 格 SVG 漫画面板。
每个面板 300x220 viewBox，含角色头像。
调用: upgrade-comic.py 或手动创建。

### Phase 5: 音频制作（Agent 5）
写口播稿 → script.txt → [主编审核] → audio.mp3
调用: python -m edge_tts --voice zh-CN-YunyangNeural --rate=-5%

### Phase 6: 数据可视化（Agent 6）
调用: python scripts/generate-charts.py
验证 5+ 个 SVG 图表生成成功。

### Phase 7: PDF深度分析（Agent 7）
6条精选新闻 × 4维度深度分析。
输出: finance_daily_{YYYYMMDD}_深度版.html

### Phase 8: 质量审查（Agent 8）
Agent 8 独立执行质检，收集客观证据。
**强制调用Claude Code。**
全部通过才放行，有问题直接驳回。

### Phase 9: 发布部署（Agent 9）
更新索引 → git commit → git push → 验证URL。

### Phase 10: 复盘（Agent 10）
当日总结 → 四原则审计 → 改进项记录。
输出: docs/review/daily-{YYYY-MM-DD}.md

---

## 早报生产流程（6阶段，简化版）

早报与晚报的不同之处在于内容导向——**不做深度复盘，聚焦隔夜新鲜资讯**。

### 早报 Phase 0: 检查前日晚报内容（主编）
```
❓ 检查问题：
1. 前日晚报深度分析的主题是什么？
2. 今日早报Layer 2是否有与晚报重复的内容？
3. 如果有 → 删除重复，替换为隔夜全球新事件
```

### 早报 Phase 1: 新闻采集（Agent 1）
搜索隔夜发生的全球财经新闻（美股收盘、大宗商品隔夜变动、政策突发、科技产业动态）。
输出: `docs/review/news-morning-{YYYY-MM-DD}.md`

### 早报 Phase 2: 事实核查（Agent 2）
逐条验证数据来源。重点核实股价、涨跌幅、政策消息的准确性。

### 早报 Phase 3: 主笔编辑（Agent 3）
撰写文章，三层结构：
- **Layer 1**：热点速览（含A股数据 — 仅做事实呈现）
- **Layer 2**：隔夜全球焦点（美股/量子/存储/政策/大宗），A股仅1段简要回顾
- **Layer 3**：数据表 + 图表

### 早报 Phase 4-6: 漫画 + 音频 + 部署
复用晚报流程的漫画设计、音频制作和部署步骤。

---

## 快速命令速查

| 用途 | 命令 |
|------|------|
| 晚报全流程 | `bash scripts/evening.sh` |
| 数据图表 | `python scripts/generate-charts.py` |
| 音频合成 | `python -m edge_tts --voice zh-CN-YunyangNeural --rate=-5% --text "..." --write-media audio.mp3` |
| 完整质量检查 | `python scripts/quality-check.py` |
| 索引更新 | `python scripts/update-index.py` |
| 部署验证 | `bash scripts/verify-deploy.sh` |

---

## 事后复盘清单

每次生产结束后执行：

- [ ] Think假设块是否输出（每个Agent启动时）
- [ ] 验证证据块是否输出（每个Agent完成时）
- [ ] 数据来源是否全部可追溯
- [ ] 质检是否通过（Agent 8 报告）
- [ ] 四原则审计是否完成
- [ ] 改进项是否记录并落实
