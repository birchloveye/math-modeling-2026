# 项目自审报告

审查日期：2026-09-07

## 审查结论

仓库已实现 P0–P12 全部阶段、五个职责分离的 Skill、四个人工 Gate、四个严格 Schema、八份按需专家指南、确定性辅助工具、Workspace 契约与 Benchmark 说明。运行契约阻止系统自动跨越 P1、P4、P7/P8 和 P11/P12。Writer 模式受 Freeze 证据和 Claim 状态约束。

## 风险审查

- 重复 Skill：无。Analyze、Model、Solve、Validate 和 Paper 的阶段职责互不重叠。
- 无意义 Token 消耗：大型数据概览和参数组合交给 Python；专家指南按题型读取。
- 绕过 Gate：文档中没有绕过明确人工批准的路径；CLI 不会提交赛题或选择路线。
- Writer 生成未验证结果：`AGENTS.md` 与 `skills/paper/SKILL.md` 明确禁止；Claim 与 Freeze 检查采用失败关闭策略。
- 代理指标：不强制固定图片、算法、消融或实验数量。候选路线数量取决于是否存在真正不同的方案。
- Schema 与 Skill 一致性：字段名和枚举与实施 brief 一致。
- Quick Start：提示词指明所需文件，并在目标 Gate 停止；只有明确批准后才继续。

## 已执行验证

- `tools/` 与 `tests/` 的 Python 编译成功。
- 所有 CLI 的 `--help` 成功返回。
- 单元测试覆盖数据概览、失败关闭／题型感知验证和 Freeze 源变更检测。
- 所有 JSON 与 JSON Schema 文件均可成功解析。

## 已知未完成项

- 尚未完成真实赛题的端到端 Benchmark，目前只包含 Benchmark 协议。
- 轻量数据概览工具暂不直接读取 XLSX；可先转换为 CSV/JSON，或后续添加可选适配器。
- 人工 Gate 使用 Markdown 记录，尚未采用数字签名。
- 论文一致性检查依赖显式 Claim 标签，不会自动理解所有未标注的自然语言数字。

## 推荐的首轮 Benchmark

选择三道许可条件明确的历史题：预测、约束优化和仿真／机制题各一道。冻结题目、数据和评分标准；在相同人工时间预算下从干净分支运行工作流；记录每次 Gate、失败、返工、Token 相对成本与 Claim 错误；最后由盲审人员按正确性、完整性、证据、可复现性、表达和局限性评分。根据实际失败模式安排 0.2 版本，而不是根据奖项承诺优化。

