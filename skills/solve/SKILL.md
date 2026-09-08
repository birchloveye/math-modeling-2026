---
name: solve
description: 形式化人工选定的数学模型，并实现可复现的批量实验和机器可读输出。用于模型 Gate 之后的 P5–P6；不得自行接受或冻结结果。
---

# 形式化与求解

确认 `gates/model_gate.md` 已记录一至两条选定路线。只加载相关专家指南。实现前先形式化变量、单位、公式、目标函数、约束、假设、可识别性和预期失败模式。

实验代码应采用显式配置和随机种子，并尽可能确定。参数研究必须创建符合 `schemas/experiment.schema.json` 的 `experiment_plan.json`，并使用 `tools/batch_experiment.py`；不得手动逐项调用大量组合。每个实验目录必须包含 `config.json`、`metrics.json`、`results.json`、`runtime.json` 和日志。Runner 必须明确失败，禁止把部分产出伪装成成功。

与适合题目的基线比较，并保留复现所需元数据。报告异常和未完成运行，不得挑选“看起来最好”的输出。生成 artifact 后停止；结果接受属于 P7 和人工结果 Gate。

