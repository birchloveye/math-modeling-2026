# Skill 阶段路由

本文件规定 P0–P12 每个阶段应加载的最小 Skill 集。原则是先使用核心领域 Skill，再按 artifact 类型加载官方辅助 Skill；不得一次性把所有 Skill 放入上下文。

## 路由表

| 阶段 | 必需 Skill | 条件式 Skill | 使用边界 |
|---|---|---|---|
| P0 人工通读 | 无 | `pdf`：原题为 PDF 且版面、图表或公式位置影响理解时 | 只协助读取和渲染，不替代人工通读 |
| P1 题意分析 | `analyze` | `pdf`：需要核对原题页面时 | 生成问题契约后必须停止 |
| P2 数据概览 | 无，优先 `tools/data_profile.py` | `jupyter-notebook`：需要交互式探索、单位核对或异常可视化时 | Notebook 只做探索，正式摘要仍写入 JSON |
| P3 候选建模 | `model` | 无 | 只生成候选模型卡，不实现模型 |
| P4 人工选择 | 无 | 无 | ZERO-AI，人工选择一至两条路线 |
| P5 模型形式化 | `solve` | `jupyter-notebook`：需要小规模推导验证或原型试算时 | Notebook 结果不得直接成为最终结论 |
| P6 编码与实验 | `solve` | `jupyter-notebook`：探索性实验；正式批量运行使用 Python Runner | 权威结果必须进入标准实验目录 |
| P7 结果验证 | `validate` | `jupyter-notebook`：验证 Notebook 可从头重跑时 | 缺少适用证据即失败；随后进入人工 Gate |
| P8 结果冻结 | `validate` | 无 | 只冻结人工接受的标准 artifact |
| P9 论文初稿 | `paper` Writer 模式 | `pdf`：生成或预览 PDF 时 | 只能引用冻结结果与合格 Claim |
| P10 一致性审计 | `paper` Reviewer 模式 | `pdf`：检查分页、图片、表格、公式与字体时 | 语义审计与视觉审计都必须通过 |
| P11 最终审稿 | `paper` Reviewer 模式 | `pdf`：逐页终审最终版本时 | 独立重读必要 artifact，不继承 Writer 结论 |
| P12 人工提交 | 无 | `pdf`：提交前验证最终 PDF 可读性时 | 只能由人工提交 |

## 冲突优先级

1. `AGENTS.md`、人工 Gate 和结果 Freeze 规则优先。
2. 本仓库核心 Skill 优先于辅助 Skill 的通用工作目录约定。
3. `jupyter-notebook` 不得取代 `experiment_plan.json`、批量 Runner 或机器可读结果。
4. `pdf` 只负责 PDF 提取、生成和视觉检查，不得从版面内容推断未经验证的新结论。

## 上游版本

辅助 Skill 来源于 [openai/skills](https://github.com/openai/skills)，锁定提交 `49f948faa9258a0c61caceaf225e179651397431`。升级前必须重新检查差异、许可证、依赖和 Gate 兼容性。

