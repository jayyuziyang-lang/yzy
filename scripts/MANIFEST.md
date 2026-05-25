# 扬说财经 · 统一资产清单 v5.0

> 最后更新: 2026-05-24
> 核心理念: Claude为质量门，Codex为生产力
> 本清单是项目全部可执行资产的权威目录，新增/删除/废弃必须更新此清单。

---

## 一、核心生产链（必需，每天使用）

这些是每天生产流程中必须调用的脚本。缺少任何一个都会导致生产中断。

| 序号 | 资产 | 部门 | 负责人 | 用途 | 状态 |
|------|------|------|--------|------|------|
| 1 | `scripts/generate-charts.py` | 数据可视化 | Python | 生成8张标准数据图表到 docs/charts/ | ✅ 活跃 |
| 2 | `scripts/gate-check.py` | 质量门禁 | Claude Code | 8道硬性门禁，阻塞项不可发布 | ✅ 活跃 |
| 3 | `scripts/factcheck-news.py` | 事实核查 | Codex/DeepSeek | 扫描文章提取数据点，标记可疑表述 | ✅ 活跃 |
| 4 | `scripts/update-index.py` | 数据索引 | Python | 更新 data/articles.json 和首页索引 | ✅ 活跃 |
| 5 | `scripts/article-template.py` | 文章模板 | Python | 标准化文章HTML模板生成 | ✅ 活跃 |

### 核心部门职责

| 部门 | 负责工作 | 执行人 | 质量门审 |
|------|---------|--------|---------|
| **新闻采集** | 搜索国内外财经新闻，逐条标注来源 | Codex/DeepSeek | Claude Code |
| **事实核查** | 交叉验证所有数据点，标记可疑表述 | Codex/DeepSeek | Claude Code |
| **数据可视化** | 运行 generate-charts.py 产出图表 | Python脚本 | 检查生成成功 |
| **文章撰写** | 基于核查后的新闻撰写文章 | Codex初稿/Claude润色 | Claude Code |
| **漫画设计** | 设计分镜、编写SVG | Claude Code | Claude Code |
| **音频制作** | 写口播稿 + edge-tts合成 | Codex初稿/edge-tts | 文件大小+时长校验 |
| **质量门禁** | 8道门禁检查，阻塞项不可发布 | **Claude Code** | 唯一把关人 |
| **数据索引** | 更新索引、同步首页 | Python脚本 | Claude Code |
| **部署** | git commit → push → 验证 | Claude Code | 自动验证 |

---

## 二、辅助工具链（有用，但不是每天用）

按优先级分为三个层级。根据需求调用。

### Level A: 高频辅助（每周使用）

| 序号 | 资产 | 用途 | 触发条件 |
|------|------|------|---------|
| 1 | `scripts/rss-collector.py` | RSS财经新闻采集，辅助新闻采集部门 | 新闻采集时需要补充来源 |
| 2 | `scripts/notify-wecom.py` | 企业微信通知，向指挥部群发送消息 | 发布后通知 |
| 3 | `scripts/site-health.py` | 站点健康检查，验证数据文件和URL可访问 | 部署后验证 |
| 4 | `scripts/verify-deploy.sh` | 部署后curl验证关键页面 | 部署后执行 |

### Level B: 低频辅助（每月使用）

| 序号 | 资产 | 用途 | 触发条件 |
|------|------|------|---------|
| 1 | `scripts/fetch-vix-data.py` | VIX恐慌指数数据采集 | GitHub Actions自动 |
| 2 | `scripts/generate-xkcd-charts.py` | 手绘风格图表生成 | 用户特别要求时 |
| 3 | `scripts/upgrade-audio.py` | 音频质量升级（备用管线） | edge-tts直出质量不达标时 |
| 4 | `scripts/pre-deploy-check.sh` | 部署前综合检查 | 部署前执行 |

### Level C: 一次性/偶尔使用

| 序号 | 资产 | 用途 | 触发条件 |
|------|------|------|---------|
| 1 | `scripts/upgrade-comic.py` | SVG漫画增强（备用管线） | Claude Code直出SVG质量不达标时 |
| 2 | `.github/workflows/deploy.yml` | GitHub Actions自动部署 | git push时自动触发 |
| 3 | `.github/workflows/rss-collect.yml` | GitHub Actions RSS定时采集 | 定时任务自动触发 |

---

## 三、已归档/废弃资产

这些资产不再适用当前的v5.0标准，已移入 `archive/` 或原地保留但**不再使用**。

### ❌ 完全废弃（不再使用，可删除）

| 资产 | 废弃原因 |
|------|---------|
| `scripts/agents/comic-stylist.sh` | v4.0 shell agent，v5.0理念为"Claude为质量门"，不需要单独shell agent管理漫画风格 |
| `scripts/agents/competition-analyst.sh` | shell agent脚本，竞品分析由Codex直接执行 |
| `scripts/agents/content-prep.sh` | shell agent脚本，内容准备由Codex直接执行 |
| `scripts/agents/daily-review.sh` | shell agent脚本，复盘由Claude Code直接在文档中记录 |
| `scripts/agents/fact-checker.sh` | shell agent脚本，事实核查由 factcheck-news.py 替代 |
| `scripts/agents/news-collector.sh` | shell agent脚本，新闻采集由Codex实时搜索替代 |
| `scripts/agents/status.sh` | shell agent脚本，状态检查由 gate-check.py 替代 |
| `scripts/character_svg.py` | 用户已明确禁止漫画上人物，角色SVG不再需要 |
| `scripts/embed-character.py` | 同上，人物嵌入功能废弃 |
| `scripts/rebrand-character.py` | 同上，品牌角色重建废弃 |
| `scripts/daily-pipeline.sh` | 文件自身标注已弃用，引用不存在的脚本 |
| `scripts/morning.sh` | v4.0 shell工作流，由WORKFLOW.md的8阶段流程替代 |
| `scripts/evening.sh` | 同上 |
| `scripts/daily-production.sh` | 与WORKFLOW.md v5.0不匹配的旧生产管线 |
| `scripts/daily-upgrade.sh` | 功能不明确的旧升级脚本 |

### 📦 可归档（功能重复或很少使用）

| 资产 | 说明 |
|------|------|
| `docs/components/` | 角色组件SVG（character-*.svg），因漫画禁人物已无用 |
| `docs/assets/character/` | 角色照片（ayang-*.jpg/png），保留作为品牌资产 |
| `docs/review/` | 旧版复盘文档（可清理由旧版遗留的零散文件，保留近期复盘） |

---

## 四、GitHub Actions 工作流

| 工作流 | 文件 | 触发 | 功能 |
|--------|------|------|------|
| 自动部署 | `.github/workflows/deploy.yml` | push到main | 构建→部署到GitHub Pages |
| RSS采集 | `.github/workflows/rss-collect.yml` | 定时 + push | 采集财经RSS→更新数据 |

---

## 五、如何新增/废弃一个资产

### 新增流程
1. 在 `scripts/` 下创建新脚本
2. 更新本清单，加入对应部门
3. 在工作流中注册调用点
4. 通过 Claude Code 终审后才生效

### 废弃流程
1. 在本清单中标记为 ❌ 废弃
2. 确认没有任何工作流引用它
3. 如有必要，移入 `archive/` 目录
4. 更新WORKFLOW.md中对应的引用

---

## 六、快速参考

### 每天必须运行的命令（按顺序）

```bash
# Phase 0: 数据可视化
python scripts/generate-charts.py

# Phase 1-5: 内容生产（Codex/Claude按WORKFLOW.md执行）

# Phase 6: 质量门禁（不通过不发布）
python scripts/gate-check.py

# Phase 7: 数据索引
python scripts/update-index.py

# Phase 8: 部署
git add .
git commit -m "..."
git push
```

### 每周/每月维护

```bash
# 站点健康检查
python scripts/site-health.py

# RSS采集（GitHub Actions自动执行，也可手动）
python scripts/rss-collector.py
```

---

*本清单是扬说财经项目所有可执行资产的权威管理文档。任何变更必须先更新本清单。*
