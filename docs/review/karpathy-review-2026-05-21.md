# Karpathy 原则审查报告 — 2026-05-21

> 基于 andrej-karpathy-skills 四大原则对扬说财经项目进行系统性审查
> 审查人: 运营总监 (Claude) + code-reviewer + code-simplifier

---

## 一、假设核查 (Think Before Coding)

### 发现的问题

| # | 假设 | 确信度 | 状态 |
|---|------|--------|------|
| 1 | `daily-pipeline.sh` 已被 `morning.sh`+`evening.sh` 替代 | 高 | ✅ 确认 |
| 2 | 旧 `quality_report.md` 文件是会话残留，不参与管线 | 高 | ✅ 确认 |
| 3 | 所有脚本默认 UTF-8 编码 | 中 | ✅ 已处理 |
| 4 | `node_modules/` 来自 Playwright 自动化 | 中 | ⚠️ 待确认 |
| 5 | SVG 文件中的 `ayang-portrait.jpg` 相对路径正确 | 高 | ✅ 已验证 |

### 修正

**问题1: daily-pipeline.sh 已过时**
- 最初是统一管线，后被拆分为 `morning.sh` + `evening.sh`
- 当前仍被 `quality-check.py` 的 pipeline 检查列为期望文件
- 决定：保留文件但不移除检查（以防需要一键全流程），添加弃用注释

---

## 二、精准变更审查 (Surgical Changes)

### 1. 孤儿代码

#### 旧质量报告文件
```
2026-05-19/quality_report.md
2026-05-20/quality_report.md
2026-05-20/quality_report_v2.md
2026-05-21/quality_report.md
2026-05-21/deep_analysis_framework.md
2026-05-21/draft_news.md
2026-05-21/polish_prompt.md
2026-05-21/team_retrospective_v3.3.md
```
- **来源**：历史会话的产出，不参与当前生产管线
- **处理**：移至 `archive/` 目录，不删除（保留历史可追溯）

#### `.handoff/task.md`
- **来源**：Codex CLI 手递手任务文件
- **处理**：保留（Codex 可能还在使用）

### 2. 未使用的变量/函数

- `character_svg.py:7` — `CHAR_IMG` 改为 `CHAR_IMG_REL` 后，检查是否还有地方引用旧名
- `upgrade-audio.py` — `article_html` 参数在 `generate_script()` 中未使用

---

## 三、代码简化审查 (Simplicity First)

### 过度设计点 #1: fact-checker.sh 中的整数比较

**问题**：`grep -c` 输出可能带换行，导致 `[ "$count" -gt 0 ]` 报错
**简化**：已修复为 `tr -d ' '` 清理输出 + `{var:-0}` 兜底

### 过度设计点 #2: daily-pipeline.sh

**问题**：11700 字节的管线脚本，功能被 `morning.sh`(4103B) + `evening.sh`(4318B) 完全覆盖
**简化**：保留但标记为弃用，`quality-check.py` 中仍检查其存在性

### 过度设计点 #3: upgrade-comic.py 的 `replace_comic_character()`

**问题**：多个复杂正则在 SVG 中匹配角色，但成功率低（输出"需要手动检查"）
**简化**：更简单的做法是确保人物图片文件路径正确即可——SVG 引用的是文件路径，不是内嵌代码

---

## 四、目标驱动验证 (Goal-Driven)

### 验证点

| 检查项 | 标准 | 结果 |
|--------|------|------|
| 所有脚本可执行 | `chmod +x` 已设置 | ✅ |
| 人物图片引用正确 | 所有 SVG 引用 `ayang-portrait.jpg` | ✅ |
| 文章图片排版 | 使用 `auto-fill minmax` 自适应 | ✅ |
| 质量检查通过 | 67项检查 | 63PASS/2FAIL* |
| 复盘机制运行 | `daily-review.sh` 完成 | ✅ |

\* 2 FAIL 是新闻简报 [待采集] 标记，属正常运行状态

---

## 五、学习总结

### 本次审查学到的教训

1. **不要保留"可能有用"的旧文件** — 旧质量报告分散在各目录中，造成认知负担
2. **废弃代码要标记清晰** — `daily-pipeline.sh` 没标注已被替代，造成混淆
3. **复杂度要主动控制** — `fact-checker.sh` 的整数比较问题说明 shell 脚本需要更小心的错误处理
4. **验证要可重复** — 67项质量检查让每次改动都能快速回归

### 后续改进方向

1. 定期运行 `code-reviewer` + `code-simplifier` 审查新代码
2. 每次新增 Agent 时先运行 `solution-architect` 设计方案
3. 每次发布前运行 `goal-verifier` 验证成功标准

---

*本报告由运营总监依据 Karpathy 四大原则编制*
*审查 Agent: code-reviewer | code-simplifier*
