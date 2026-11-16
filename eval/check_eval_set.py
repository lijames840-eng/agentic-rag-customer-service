# -*- coding: utf-8 -*-
"""评测集自检：读 eval_set.csv，验证 answer_key 是否真实存在于向量库。

特点：
1. 只读 CSV 和向量库，不修改任何文件 —— 改完标注可随时复跑
2. 检查 answer_key 是否命中、命中的 chunk 来自哪个文件、锚点区分度高不高
3. 检查负样本是否真的没有标注答案

用法：
    cd D:/AIagentandRAG/Agent项目
    venv/Scripts/python.exe eval/check_eval_set.py
"""
import collections
import csv
import os
import sys

# 强制锚定项目根：无论从哪个目录调用，都能找到 rag 包和 chroma_db
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from rag.vector_store import VectorStoreService

CSV_PATH = 'eval/eval_set.csv'


def main():
    if not os.path.exists(CSV_PATH):
        print(f'找不到 {CSV_PATH}，请先运行 eval/build_eval_set.py')
        return

    with open(CSV_PATH, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    vs = VectorStoreService()
    data = vs.vector_store._collection.get(include=['documents', 'metadatas'])
    docs, metas = data['documents'], data['metadatas']

    print('评测集 %d 条  |  库内 chunk %d 条' % (len(rows), len(docs)))
    print()
    print('%-5s %-6s %-7s %-24s %s' % ('qid', '状态', '命中块', '来源', '说明'))
    print('-' * 80)

    fails, warns, ok_cnt, neg_cnt = [], [], 0, 0

    for r in rows:
        qid = (r.get('qid') or '').strip()
        typ = (r.get('type') or '').strip()
        keys = [k.strip() for k in (r.get('answer_key') or '').split('|') if k.strip()]

        if typ == 'negative':
            neg_cnt += 1
            if keys:
                print('%-5s %-6s %-7s %-24s %s' % (qid, 'WARN', '-', '-', '负样本不该有 answer_key'))
                warns.append(qid)
            else:
                print('%-5s %-6s %-7s %-24s %s' % (qid, 'NEG', '-', '-', '负样本，无需标注'))
            continue

        if not keys:
            print('%-5s %-6s %-7s %-24s %s' % (qid, 'FAIL', '0', '-', '缺少 answer_key'))
            fails.append(qid)
            continue

        # 逐个 key 找命中的 chunk
        miss, hit_idx = [], set()
        for k in keys:
            idx = [i for i, d in enumerate(docs) if k in d]
            if not idx:
                miss.append(k)
            hit_idx |= set(idx)

        if miss:
            print('%-5s %-6s %-7s %-24s %s' % (qid, 'FAIL', '0', '-', '找不到：' + ' / '.join(miss)))
            fails.append(qid)
            continue

        srcs = collections.Counter(
            os.path.basename(str((metas[i] or {}).get('source', ''))) for i in hit_idx
        )
        src_str = ','.join(s for s, _ in srcs.most_common(2))

        note = ''
        if len(hit_idx) > 8:
            note = '锚点区分度偏低（%d 块命中）' % len(hit_idx)
            warns.append(qid)

        print('%-5s %-6s %-7d %-24s %s' % (qid, 'OK', len(hit_idx), src_str[:22], note))
        ok_cnt += 1

    print('-' * 80)
    print('正样本通过 %d 条 | 负样本 %d 条 | 失败 %d | 警告 %d'
          % (ok_cnt, neg_cnt, len(fails), len(warns)))
    if fails:
        print('失败清单：', ', '.join(fails))
    if warns:
        print('警告清单：', ', '.join(warns))


if __name__ == '__main__':
    main()
