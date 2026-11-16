# RAG 检索评测

用 20 条人工标注的题目，量化「当前检索方案能召回多少正确答案」。所有数字均可复现。

---

## 三个脚本

| 脚本 | 作用 | 是否改文件 | 什么时候跑 |
|---|---|---|---|
| `build_eval_set.py` | 生成 20 条题目并写入 CSV | ✅ **会覆盖 `eval_set.csv`** | 只在改题目时 |
| `check_eval_set.py` | 验证每条 `answer_key` 是否真实存在于向量库 | ❌ 只读 | 改完标注随时验 |
| `run_eval.py` | 用 20 条题实测检索，算 Recall / MRR | 写入 `result_*.json` | 每次改检索方案后 |

```bash
cd D:/AIagentandRAG/Agent项目
venv/Scripts/python.exe eval/check_eval_set.py       # 验题库
venv/Scripts/python.exe eval/run_eval.py              # 跑基线
venv/Scripts/python.exe eval/run_eval.py result_rerank.json   # 保存为另一个名字，便于对比
```

> ⚠️ `build_eval_set.py` 会重写整个 CSV。手动改过标注后，只想验证请跑 `check_eval_set.py`。

---

## 当前基线（2026-10-29）

**配置**：纯向量检索 · `k=10` · 662 chunk · 含 PDF 冗余 · 默认 HNSW 参数

| 指标 | 数值 |
|---|---|
| Recall@1 | 70.6%（12/17） |
| **Recall@3** | **82.4%（14/17）** |
| Recall@5 | 82.4%（14/17） |
| Recall@10 | 94.1%（16/17） |
| MRR | 0.773 |

| 类型 | Recall@3 |
|---|---|
| single（12 条） | 92% |
| multi（5 条） | **60%** |

**关键读数**：Recall@3 = Recall@5 = 82.4%，但 @10 = 94.1%。说明正确内容都在 top-10 里，只是排序靠后（第 6–7 位）。**这是 Rerank 的明确依据。**

---

## 评测集结构

| 类型 | 数量 | 用途 |
|---|---|---|
| single | 12 | 单一事实，考基础召回 |
| multi | 5 | 需综合 2–3 个片段，考跨文档能力 |
| negative | 3 | 知识库无答案，考拒答（竞品对比 / 维修网点 / 分期付款） |

标注用**内容指纹**（`answer_key`），不用 chunk id —— Chroma 的 id 是自动生成的 UUID，重建库就失效。

---

## 已知问题（待改进）

### 1. S02 锚点过宽（自检警告）

`12000Pa` 在库里有 **9 处**命中，只有 1 处（对比表 `S3 Pro｜高端｜dToF｜AI双目｜12000Pa`）是真正答案。其余 8 处是"12000Pa 以上更彻底""边际收益递减"这类通用表述。

→ 判定偏松，命中率可能虚高。**改法**：锚点加长为对比表那一行前缀。

### 2. PDF 与 TXT 内容重复，77 个冗余 chunk

`扫地机器人100问.pdf`（77 chunk）与 `扫地机器人100问.txt`（102 chunk）是同一份内容。同一信息在库里有 2 份，会抬高命中概率。

→ **计划**：删掉 PDF 的 77 个 chunk 再跑一次，作为对照实验，量化冗余造成的虚高幅度。

### 3. 故障排除被切碎：72 条 → 156 块

该文档单条 212 字，超过 `chunk_size=200`，被系统性切断。碎片占 chunk 总数 23.6%。

→ **计划**：按文档类型分参数，该文件用 300。

### 4. multi 类 Recall@3 仅 60%

5 条里 2 条未进 top-3。根因是一个 query 只有一个向量，无法同时表达多维度需求。

→ **候选方案**：query 改写（拆成多个子查询）、Rerank、multi-query 检索。

---

## 评测流程（每次改方案都走一遍）

```
1. 改检索代码
2. python eval/check_eval_set.py      # 确认题库没坏
3. python eval/run_eval.py xxx.json   # 跑，记录指标
4. 对比上一份 result_*.json
5. 只看未命中的那几条，归类原因
```

---

## 结果文件

| 文件 | 说明 |
|---|---|
| `result_baseline.json` | 纯向量 k=10，662 chunk（含 PDF 冗余） |
| `eval_set.csv` | 20 条题目与标注 |
| `chunks.csv` | 库内全部 chunk 导出（662 条，标注时查用） |
