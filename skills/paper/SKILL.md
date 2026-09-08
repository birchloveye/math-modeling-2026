---
name: paper
description: 依据冻结结果和证据账本撰写或独立审查数学建模论文。用于 P9–P11；绝不编造结论，也不得把未验证 Claim 升格为事实。
---

# 证据约束的论文流程

开始时必须明确选择一种模式。

## Writer 模式

阅读已批准问题契约、最终模型、`workspace/experiments/FROZEN_RESULTS.json`、已验证或暂定支持的 Claim Ledger，以及冻结的图片和表格。写作前运行 Claim 与一致性检查工具。只有 `verified` Claim 可以支撑最终结论；`supported` 必须明确写成暂定结论；不得把 `draft` 或 `rejected` 写成事实。

每个重要数字或结论都必须映射到合格 Claim 与冻结来源。不得在正文中临时计算新的核心结果。诚实说明假设和局限，并回答问题契约中的每个小问。

## Reviewer 模式

独立重读最少但充分的 artifact，不依赖 Writer 的推理上下文。使用 `templates/review_report.md`。检查小问覆盖、公式与正文一致性、数字／表格／图片一致性、图片是否真正支持解释、Claim 溯源、过度解释、隐藏假设、优缺点是否诚实、摘要是否准确，以及复杂度是否合理。

运行不带 `--freeze` 的 `tools/final_audit.py`。文风成熟不等于证据充分。在 `gates/submission_gate.md` 停止；最终由人工提交。

