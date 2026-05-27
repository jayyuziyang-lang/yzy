# 复盘：2026-05-27 早报 · 图片布局质量升级

## 触发事件

用户投诉："Python图片质量太差了！统计数据这么多表达你用的图片也太丑了，还有好多错位的、文字堆叠、以及红涨绿跌弄反的错误。"

---

## 问题清单与根因分析

### 问题一：数据可视化质量不合格（根源）

| 维度 | 问题表现 | 根因 |
|------|---------|------|
| 配色 | 红涨绿跌弄反 | 缺乏品牌色彩系统，代码内硬编码 |
| 布局 | 文字堆叠、标签错位 | 无智能标签位置算法 |
| 风格 | 图表"太丑" | 无统一 mplstyle 样式文件 |
| 字体 | 中文缺失（DejaVu Sans 回退） | font.family 被 mplstyle 覆盖 |

**根因：** 缺乏品牌视觉规范和统一样式系统。每次作图靠代码内硬编码，复用率为零。

**整改措施（已执行）：**
- ✅ 创建 `stylelib/yangshuo.mplstyle` — 品牌全局样式（尺寸、颜色、网格、轴线）
- ✅ 创建 `stylelib/yangshuo_palette.py` — 品牌色板（红涨绿跌、深浅渐变、功能函数）
- ✅ 创建 `scripts/chart_templates.py` — 6种高级图表模板（lollipop、waterfall、slope、dumbbell、waffle、trend_with_band）
- ✅ `generate-charts.py` v3.0 全面重写 — 统一风格加载、智能标签、质量自检

### 问题二：字体渲染故障（CJK 缺失）

**问题：** 图表中中文字符显示为方块（DejaVu Sans 回退）。

**根因：** `yangshuo.mplstyle` 中设置了 `font.family: sans-serif`，`plt.style.use()` 在 `setup_font()` 之后执行，覆盖了中文配置。

**整改措施：**
- ✅ `yangshuo.mplstyle` 删除 `font.family` 配置
- ✅ 代码中 `plt.style.use()` 先执行，`setup_font()` 后执行
- ✅ 在 `AGENT_HANDBOOK.md` 中记录此执行顺序约束

### 问题三：终端中文显示异常

**问题：** Windows 终端（GBK编码）无法显示 emoji 和中文（`✅` 显示为问号）。

**根因：** Python 默认 stdout 编码为 GBK，不支持 Unicode emoji。

**整改措施：**
- ✅ 脚本内添加 `sys.stdout.reconfigure(encoding='utf-8')`
- ✅ Python 调用时加 `-X utf8` 参数

### 问题四：缺乏统一的图片布局规范

**问题：** 早报文章中 section 04（前沿/国际）无数据图表；panel-001（半导体漫画）错误放置在热区后而非 section 02；panel-002（融资余额）错误放置在 section 05 而非 section 01。

**根因：** 没有文章图片布局标准，每次凭感觉放置。

**整改措施（已执行）：**
- ✅ 制定了「每板块至少一张数据图表」原则
- ✅ 漫画必须与内容主题对应的板块绑定
- ✅ 本次重新布局验证：6板块全部有图，漫画和板块对应

### 问题五：质量门禁缺失

**问题：** 图表生成后无人检查质量，错误直接流入产品。

**根因：** 无自动化质量门禁。

**整改措施（已执行）：**
- ✅ `generate-charts.py` 内置质量自检（30项检查：存在、大小、SVG有效性）
- ✅ `pre-deploy-check.sh` 新增 [7/7] 图表质量校验步骤
- ✅ `WORKFLOW.md` 新增 Layer 1.5 数据可视化质量门禁
- ✅ `AGENT_HANDBOOK.md` 质量门禁从4层升级为5层

### 问题六：Python 环境管理混乱

**问题：** `morethemes` 安装到了错误的 Python 环境。

**根因：** 多 Python 环境（WindowsApps python vs pythoncore-3.14-64），无统一依赖管理。

**整改措施：**
- ✅ 明确使用 `pythoncore-3.14-64` 作为标准环境
- ✅ 所有脚本首次运行 `which python` 确认环境

---

## 质量门禁系统 v3.0 总图

```
                    生产管线
 ┌─────────────────────────────────────────────┐
 │  Layer 1: 事实核查 (数据来源URL)              │
 │  Layer 1.5: 数据可视化 (30项质量门禁) ← 新增  │
 │  Layer 2: 风格一致性 (mplstyle + palette)    │
 │  Layer 3: 质量检查 (预部署7项)                │
 │  Layer 4: 数据准确性 (2来源交叉验证)           │
 └─────────────────────────────────────────────┘
                    不可绕过
```

---

## 后续行动项

| # | 行动 | 负责人 | 优先级 |
|---|------|--------|--------|
| 1 | 每篇文章生产前，先确认本板块需要什么类型的图表 | Claude/Codex | P0 |
| 2 | 新图表类型优先使用 `chart_templates.py` 已有模板 | Codex | P1 |
| 3 | 每周检查 `docs/charts/` 下的 SVG 是否全部通过质量门禁 | Claude | P1 |
| 4 | 每月集中训练一次数据可视化专题 | Claude | P2 |

---

## v4.0 升级记录（2026-05-27 执行）

**触发事件：** 用户反馈"目前的质量完全不够，升级的效果没有体现出来"——参考CSDN高质量图表标准后实施。

### 升级内容

| 组件 | v3.0 (之前) | v4.0 (升级后) |
|------|------------|--------------|
| `yangshuo.mplstyle` | `#F8FAFC` 纯色背景, 有spines | `#F0F2F5` 暖灰容器 + `#FFFFFF` 白色卡片面板, 零脊线 |
| `yangshuo_palette` | 基本红绿配色工具 | 新增 FIGURE_BG/CARD_BG/SUBTTITLE/FOOTNOTE 布局色 |
| `generate-charts.py` | 内联 style_ax() 控制 | **ChartCard 布局引擎**: 标题→副标题→图表面板→来源脚注 |
| SVG视觉 | 直出 matploblib | 专业财经媒体风格（Economist/FT 混合） |

### ChartCard 布局标准

所有10张图表现在都遵循：
```
0.92  标题（14pt粗体，左对齐）
0.88  副标题（9pt灰色，时间/简述）
0.10  ┌──────────────────────────────┐
      │  纯白图表面板 (spine-free)     │
0.06  └──────────────────────────────┘
0.02  来源: ×××××× (6.5pt灰色)
```

### 质量门禁升级

- ✅ 新增 ChartCard 布局完整度检查（标题+来源不得缺失）
- ✅ 新增 ChartCard 视觉检查（暖灰背景+纯白面板+零脊线）
- ✅ 30/30 门禁保持不变，但检查标准提高
- ✅ 所有图表重新生成并通过验收

---

## 铁律追加

基于今天教训，追加两条铁律至 AGENT_HANDBOOK.md：

1. **数据可视化铁律：** 每板块至少一张数据图表，漫画不得脱离对应内容板块独立放置
2. **样式加载铁律：** `plt.style.use()` 必须在 `setup_font()` 之前执行，`mplstyle` 中不得设置 `font.family`

---

*复盘人：Claude Code Agent · 2026-05-27*
*"产品质量是我们的核心竞争力，其他都是锦上添花。"*
