# Math Modeling Plus

Math Modeling Plus 是一套面向 ChatGPT Plus、Codex 与 Python 的数学建模竞赛工作流。它以获奖表现为导向，通过人在回路决策、可复现实验和证据约束，提高建模质量、论文一致性与有限 Token 的利用效率。**本项目不保证获得任何竞赛奖项。**

Codex 在本项目中主要承担题意拆解、模型设计、数学推导、异常解释和独立审稿等高价值推理任务。Python 负责数据概览、参数组合、验证记录、证据检查和哈希等确定性工作。题意判断、路线选择、异常结果判断、论文逻辑与最终提交始终由人工负责。

## 工作流

```text
P0 人工通读 → P1 分析 → 人工确认问题契约
  → P2 数据概览 → P3 候选竞技场 → P4 人工选择模型
  → P5 形式化 → P6 求解 → P7 验证 → 人工接受结果
  → P8 冻结 → P9 写作 → P10 审计 → P11 终审
  → 人工批准提交 → P12 人工提交
```

五个核心 Skill 分工如下：

- `analyze`：生成问题契约并停止。
- `model`：提出显著不同的候选路线，并等待人工选择。
- `solve`：形式化已选路线，批量运行可复现实验。
- `validate`：根据题型选择检查；缺少适用证据时按失败处理。
- `paper`：仅依据冻结证据写作，或执行独立审稿。

此外，仓库从 OpenAI 官方 GitHub Skill 库接入了两个辅助 Skill：

- `jupyter-notebook`：用于数据探索、模型原型和可复现 Notebook；不能替代正式批量实验。
- `pdf`：用于赛题 PDF 阅读、论文渲染和逐页视觉审查；不能生成未经验证的结论。

`SKILL_ROUTING.md` 给出 P0–P12 的逐阶段加载表。辅助 Skill 锁定到明确上游提交，并在 `THIRD_PARTY_NOTICES.md` 中保留来源与许可证信息。

`AGENTS.md` 是 Agent 运行契约；`WORKFLOW.md` 定义每个阶段的输入、输出和停止条件。JSON Schema 约束核心 artifact。专家指南与辅助 Skill 只在当前阶段确实需要时读取，以控制上下文和 Token 消耗。

## 快速开始

需要 Python 3.11 或更高版本。命令行工具仅使用 Python 标准库。

1. 将原始赛题和人工标注放入 `workspace/problem/`，将数据放入 `workspace/data/`。
2. 使用以下提示启动 P1：

   ```text
   请读取 AGENTS.md 和 skills/analyze/SKILL.md。

   赛题位于 workspace/problem/，数据位于 workspace/data/。
   从 P1 开始。完成 Problem Contract 后停止，不要自动进入模型设计。
   只向我输出需要人工确认的关键问题。
   ```

3. 检查 `gates/human_gate.md` 并明确批准后，启动候选模型阶段：

   ```text
   P1 已人工确认。读取 skills/model/SKILL.md。
   生成 3–4 条显著不同的候选模型路线，只生成 model cards，不写完整代码。
   完成后停止，等待人工选择。
   ```

4. 在 `gates/model_gate.md` 中选择一至两条路线，然后继续：

   ```text
   Route B 已确认。继续完成模型形式化和实验设计。
   参数扫描必须生成 experiment_plan.json，优先使用批量脚本执行，不要逐项调用模型。
   ```

全部 CLI 均提供 `--help`。常用命令：

```bash
python tools/data_profile.py workspace/data/input.csv
python tools/batch_experiment.py workspace/experiments/experiment_plan.json
python tools/validate_results.py --evidence workspace/experiments/validation_evidence.json
python tools/final_audit.py --freeze --manifest workspace/experiments/freeze_manifest.json
python tools/claim_checker.py
python tools/consistency_checker.py workspace/paper/paper.md
python tools/final_audit.py
```

结果 Gate 使用的 Freeze Manifest 必须包含 `accepted_model`、`accepted_experiment_ids`、`final_metrics`、`final_tables`、`final_figures` 和 `files`。表格和图片使用仓库相对路径。冻结工具会自动将每个已接受实验的配置、指标、结果与运行信息加入哈希；`files` 用于列出最终模型和验证报告等其他来源。

## 竞赛纪律

P8 之前允许灵活探索。冻结后，已接受结果使用内容哈希约束：任何源文件变化都会使终审失败，必须重新验证并再次取得人工接受。论文结论在 Claim Ledger 中使用 `draft`、`supported`、`verified` 或 `rejected` 状态；最终结论只能由 `verified` Claim 支撑。

验证规则由题型决定，而非代理数量目标。例如，预测模型检查时间泄漏和预测不确定性；优化模型检查可行性与最优性证据。不存在通用的图片数、算法数或消融次数要求。

## Benchmark

`benchmarks/README.md` 定义了 Token 相对成本、Gate、失败运行、返工、验证失败、Claim 错误、论文完整性和盲审分数等记录项。Benchmark 只用于比较工作流版本，不代表获奖概率。

## License

项目采用 MIT License，详见 `LICENSE`。

