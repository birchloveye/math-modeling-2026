# 工作流 Benchmark

Benchmark 用于在同一道归档赛题和固定数据快照上比较不同工作流版本，不用于预测或宣称竞赛奖项。人工时间与人工决策应单独记录；必须遵守赛题许可要求；不得把评审保留信息泄漏到模型选择阶段。

每次 Benchmark 使用 UTF-8 JSON 记录：

```json
{
  "workflow_version": "",
  "problem": "",
  "token_relative_cost": null,
  "human_gates": null,
  "failed_runs": null,
  "code_rework_count": null,
  "validation_failures": null,
  "claim_errors": null,
  "paper_completeness": null,
  "review_score": null
}
```

运行前先固定评分细则和 Token 成本基线。首轮建议包含预测、优化，以及仿真或机制建模题各一道。从干净分支运行当前工作流，保留 Gate 决策与全部 artifact；下一版本使用同一题目和数据快照。最终由盲审人员依据正确性、完整性、证据、可复现性、清晰度与局限性进行评分。

