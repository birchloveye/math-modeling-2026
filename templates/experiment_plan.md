# 实验计划模板

实验计划必须符合 `schemas/experiment.schema.json`。Runner 接收 `--config <生成的配置文件> --output <实验目录>`，并写出 `metrics.json`、`results.json` 和 `runtime.json`。批量工具负责记录日志与完整配置。使用稳定的实验 ID 和明确的随机种子。

