# -*- coding: utf-8 -*-
"""生成 20 条 RAG 评测集，并自检 answer_key 是否真实存在于向量库中。"""
import csv
import os
import sys

# 强制锚定项目根：脚本可能被从任意目录调用（IDE 运行、绝对路径运行），
# 若依赖当前工作目录，会连到别处新建的空向量库，导致全部作答被判为「找不到」
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

ROWS = [
    # qid, query, type, expected_source, answer_key, notes
    ("S01", "滤网多久换一次？", "single", "维护保养.txt",
     "5次或2个月", "耗材周期表，考基础事实"),
    ("S02", "S3 Pro 的吸力是多少？", "single", "选购指南.txt",
     "12000Pa", "机型对比表，考精确数值"),
    ("S03", "APP 上显示 E09 是什么故障？", "single", "故障排除.txt",
     "E09 定位失败", "错误码精确定位"),
    ("S04", "我家门槛有 2.1 厘米高，哪款机型能过去？", "single", "选购指南.txt",
     "X1支持2.2厘米", "需跨字段推理：2.1 落在 2.0 与 2.2 之间"),
    ("S05", "沙发底下只有 10 厘米，S3 Pro 能钻进去扫吗？", "single", "扫地机器人100问.txt",
     "净空大于11厘米", "需推理：10cm < 11cm 门槛，且 S3 Pro 高 103mm"),
    ("S06", "主刷多久需要换一次？", "single", "维护保养.txt",
     "6—12个月", "有养宠条件分支，考是否答全"),
    ("S07", "拖完地地上有印子，多久能干？", "single", "扫地机器人100问2.txt",
     "留水痕的原因：水量过大", "口语化改写，考语义匹配"),
    ("S08", "清水箱可以直接加自来水吗？", "single", "扫拖一体机器人100问.txt",
     "自来水硬度高", "水垢问题，实用高频"),
    ("S09", "扫地机器人对孕妇有没有影响？", "single", "行业标准与安全规范参考.txt",
     "远低于国际非电离辐射防护委员会", "合规话术，考是否越界承诺"),
    ("S10", "第一次使用需要做哪些准备？", "single", "扫地机器人100问.txt",
     "① 装上边刷、滚刷、尘盒", "多步操作，考完整性"),
    ("S11", "扫完地地上还有一层细灰是什么原因？", "single", "扫地机器人100问2.txt",
     "细灰来自三处", "现象诊断，需列全三种原因"),
    ("S12", "X1 第一次充电要充多久？", "single", "选购指南.txt",
     "X1约5小时", "四机型并列，考指代消解"),

    ("M01", "我家 90 平、养猫、全屋木地板，预算 6000 左右，选哪款？", "multi",
     "选购指南.txt", "5999|双盘旋转+下压+抬升10mm",
     "需综合户型/宠物/材质/价位四维"),
    ("M02", "机器经常卡在门槛上，扫完还有细灰，这两个问题怎么一起解决？", "multi",
     "故障排除.txt|扫地机器人100问2.txt", "① 滤网饱和|门槛或地毯阻挡",
     "跨两份文档，考多问题拆解"),
    ("M03", "我每天扫两次、120 平、养狗，一年耗材大概多少钱？", "multi",
     "维护保养.txt", "550—750元", "需按使用强度分档，考条件匹配"),
    ("M04", "南方梅雨季，保养上跟平时有什么不同？", "multi",
     "维护保养.txt", "尘袋受潮会结块", "季节性调整，考是否脱离常规答案"),
    ("M05", "预算 4000，想扫拖一体又不想天天倒尘盒，一年耗材多少？", "multi",
     "选购指南.txt|维护保养.txt", "3499|350—500元",
     "选型 + 持有成本，跨两段"),

    ("N01", "你们和石头、科沃斯比，优势在哪？", "negative", "",
     "", "竞品对比，文档只有自家四款"),
    ("N02", "我家附近有维修网点吗？能上门修吗？", "negative", "",
     "", "线下服务，文档只讲报修流程不讲网点"),
    ("N03", "支持分期付款或者租赁吗？", "negative", "",
     "", "支付方式，文档完全没有"),
]

os.makedirs("eval", exist_ok=True)
with open("eval/eval_set.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["qid", "query", "type", "expected_source", "answer_key", "notes"])
    w.writerows(ROWS)
print("已写入 eval/eval_set.csv，共 %d 条" % len(ROWS))

# ---------- 自检：每个 answer_key 必须真实存在于某个 chunk ----------
from rag.vector_store import VectorStoreService
vs = VectorStoreService()
data = vs.vector_store._collection.get(include=["documents"])
docs = data["documents"]

print("\n%-5s %-8s %s" % ("qid", "状态", "说明"))
print("-" * 62)
bad = 0
for qid, q, t, src, keys, _ in ROWS:
    if t == "negative":
        print("%-5s %-8s 负样本，无需 answer_key" % (qid, "OK"))
        continue
    miss = [k for k in keys.split("|") if not any(k in d for d in docs)]
    if miss:
        bad += 1
        print("%-5s %-8s 找不到: %s" % (qid, "FAIL", miss))
    else:
        print("%-5s %-8s 命中" % (qid, "OK"))

print("\n自检结果: %d/%d 条通过" % (len([r for r in ROWS if r[2] != 'negative']) - bad,
                                len([r for r in ROWS if r[2] != 'negative'])))
