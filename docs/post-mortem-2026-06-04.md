---
name: 2026-06-04 团队复盘
description: 名词解释缺失+VIX流程优化+deploy.sh自动rebase — 三项系统性整改
type: project
---

## 2026-06-04 团队复盘

### 问题1: 早报缺少名词解释板块

**表现：** 2026-06-04早报没有名词解释板块，违背了v6.0质量维度第7条"名词解释+立场透明"。
**根因：** 名词解释在CLAUDE.md的7大质量升级维度中有记录，但WORKFLOW.md的终审清单和文章撰写规范中没有对应的强制检查项。生产流程缺少"生成后逐条核对7维度"的执行机制。
**整改：**
- WORKFLOW.md v6.1: 写入终审清单新增 `□ 名词解释：文末有术语解释板块`
- WORKFLOW.md Phase 2: 文章撰写写入"名词解释强制：文末9项铁律"
- 本期早报已补全9个专业术语的解释

### 问题2: VIX更新不是早报前置步骤

**表现：** VIX更新在WORKFLOW.md中只标注为"晚报前置步骤"，早报生产时容易遗漏。
**根因：** 规则定义不完整，只覆盖了晚报场景。
**整改：**
- WORKFLOW.md v6.1: VIX标题改为"早报/晚报前置步骤"
- 部署阶段增加一步: `python scripts/fetch-vix-data.py`

### 问题3: deploy.sh 频繁 git 冲突（data/latest-cdn.json）

**表现：** GitHub Actions的`commit-cdn-version` job每次部署后推送data/latest-cdn.json，导致本地deploy.sh总是rejected。
**根因：** deploy.sh只做了"推送失败→retry with upstream"，没有"先同步远程变更再推送"的逻辑。
**整改：**
- deploy.sh: 在`git push`前增加`git pull --rebase origin main`
- 检测到冲突时自动`git checkout --ours data/latest-cdn.json`并`git rebase --continue`
- 整个过程无需人工干预

### 后续行动

| # | 行动 | 负责人 | 截止 |
|---|------|--------|------|
| 1 | 旧文章的"名词解释"模板沉淀为标准HTML片段 | 下次生产前 | — |
| 2 | 终审清单+claudeMd+WORKFLOW三者保持同步 | 每次规则变更 | — |
