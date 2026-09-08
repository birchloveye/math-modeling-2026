---
name: analyze
description: 将数学建模赛题分析为机器可读的问题契约，并停下来等待人工批准。用于人工已阅读并标注题目后的 P1 阶段；不要用它选择模型。
---

# 分析赛题

阅读 `AGENTS.md`、`WORKFLOW.md`、原始赛题，以及 `workspace/problem/` 中的人工标注。只生成符合 `schemas/problem.schema.json` 的 `workspace/problem/problem_contract.json`。

拆分所有小问；识别输入、输出、决策变量、已知约束、隐含约束、不确定点、可验证目标和小问之间的有向依赖。解决歧义时引用或指出题目依据；真正无法确定的解释必须显式保留。不要进行深入数据分析，也不要提出模型路线。

校验 JSON Schema。只汇总会实质影响后续工作的歧义，然后在 `gates/human_gate.md` 停止。未经明确批准，不得进入 P2 或 P3。

