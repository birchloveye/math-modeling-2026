# 竞赛工作流

```text
P0 人工通读
  -> P1 题意分析
  -> [人工 Gate：确认问题契约]
  -> P2 数据概览
  -> P3 候选模型竞技场
  -> [人工 Gate：选择 1–2 条路线]
  -> P5 模型形式化
  -> P6 编码与实验
  -> P7 题型感知验证
  -> [人工 Gate：接受结果]
  -> P8 结果冻结
  -> P9 论文初稿
  -> P10 结论／图表／数字审计
  -> P11 独立终审
  -> [人工 Gate：批准提交]
  -> P12 人工提交
```

P4 即上图中的模型选择 Gate。任何跨越 Gate 的推进都需要在相应清单中记录明确的人工批准。

## 阶段契约

| 阶段 | 主要输入 | 必需输出 | 停止条件 |
|---|---|---|---|
| P0 | 原始赛题 | `workspace/problem/` 中的人工标注 | 人工启动 P1 |
| P1 | 赛题与标注 | `problem_contract.json` | 问题契约 Gate |
| P2 | 原始数据 | `data_summary.json` | 摘要已审阅 |
| P3 | 已批准契约与摘要 | 3–4 个真正不同的模型卡 | 模型 Gate |
| P5 | 已选路线 | 最终模型 artifact 与假设 | 形式化结果已审阅 |
| P6 | 最终模型与实验计划 | 机器可读实验目录 | 计划实验完成 |
| P7 | 结果与题型 | 验证报告 | 结果 Gate |
| P8 | 已接受 artifact | 含哈希的 `FROZEN_RESULTS.json` | Freeze 已生成 |
| P9 | 冻结结果与合格 Claim | 论文初稿 | 初稿完成 |
| P10 | 初稿与证据 artifact | 审计报告 | 阻断问题全部解决 |
| P11 | 独立重读所需 artifact | 终审报告 | 提交 Gate |
| P12 | 已批准提交包 | 人工提交 | 人工确认 |

## 变更控制

P7 之前允许快速探索和废弃试验。Freeze 是可复现性清单，而不仅是一个标签。P8 之后修改已接受结果或其来源，需要在必要时创建新实验 ID、重新验证、重新取得人工接受并更新哈希。仅修改论文措辞仍然允许，但必须重新通过 P10。

## 建议的 Git 分支

长期保留 `main` 和 `develop`。功能开发使用临时分支：`feature/core-workflow`、`feature/modeling-skills`、`feature/expert-library`、`feature/verification-tools`、`feature/artifact-contracts` 和 `feature/paper-pipeline`。另可按用途使用 `benchmark/*`、`experiment/*` 与 `release/*`；完成后合并并删除临时分支。

