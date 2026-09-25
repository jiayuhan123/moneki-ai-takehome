# EVAL_REPORT

## Starter 初始基线

- 时间：2026-09-25
- commit：作业原始版本（第一步修复前）
- 模式：mock，未配置大模型 Key
- 命令：`python eval/run_eval.py --base-url http://127.0.0.1:8000 --questions eval/public_questions.jsonl --out baseline-report`
- 结果：**17.00 / 100.00**，11 / 55 题全绿
- 其中：metrics 1/6，health 0/1

## 第一关阶段验收

- 时间：2026-09-26
- commit：以本分支第 10 个 commit 为准
- 模式：mock，未配置大模型 Key（第一关不需要 Key）
- 指标命令：`python eval/run_eval.py --base-url http://127.0.0.1:8000 --questions eval/public_questions.jsonl --only metrics --out gate1-metrics-report`
- 指标结果：**6.00 / 6.00**，6 / 6 题全绿
- 健康命令：`python eval/run_eval.py --base-url http://127.0.0.1:8000 --questions eval/public_questions.jsonl --only health --out gate1-health-report`
- 健康结果：**1.00 / 1.00**，1 / 1 题全绿
- 本地回归：`29 passed`；前端 `vue-tsc -b && vite build` 通过。

同时运行完整公开题库作为阶段 checkpoint：

- 命令：`python eval/run_eval.py --base-url http://127.0.0.1:8000 --questions eval/public_questions.jsonl --out gate1-final-report`
- 结果：**44.50 / 100.00**
- 第一关直接相关：metrics 6/6、health 1/1
- 其他当前得分：retrieval 8/15、data 12/12、hybrid 3/18、multi_turn 3.5/9、refusal 8/8、safety 3/9
- 尚未开始：doc 0/16、version 0/6；这些属于后续 RAG 与混合问答开发范围。

> 这是第一关 checkpoint，不冒充最终 100 分报告。检索、数据问答、文档问答、混合问答与多轮会在第二、三关完成后重新跑全量公开题库，并在本文追加最终模型和配置。
