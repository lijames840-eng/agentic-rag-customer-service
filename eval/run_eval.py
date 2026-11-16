# -*- coding: utf-8 -*-
"""检索基线评测：用 eval_set.csv 的 20 条题去考当前检索系统。

指标：
  Recall@k  —— 正确片段出现在前 k 条里的比例
  MRR       —— 正确片段的排名倒数均值（排第 1 得 1.0，排第 3 得 0.33）

产物：
  eval/result_baseline.json —— 逐条明细，便于后续做方案对比

用法：
    venv/Scripts/python.exe eval/run_eval.py [结果文件名]
"""
import csv
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from rag.vector_store import VectorStoreService

TOP = 10
CSV_PATH = 'eval/eval_set.csv'


def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else 'result_baseline.json'

    with open(CSV_PATH, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    vs = VectorStoreService()
    retriever = vs.vector_store.as_retriever(search_kwargs={'k': TOP})
    print('检索配置: 纯向量 | k=%d | 库内 chunk=%d\n' % (TOP, vs.vector_store._collection.count()))

    details = []
    for i, r in enumerate(rows, 1):
        if r['type'] == 'negative':
            continue
        keys = [k.strip() for k in (r['answer_key'] or '').split('|') if k.strip()]
        docs = retriever.invoke(r['query'])

        rank = None
        for pos, d in enumerate(docs, 1):
            if any(k in d.page_content for k in keys):
                rank = pos
                break

        details.append({
            'qid': r['qid'],
            'type': r['type'],
            'query': r['query'],
            'rank': rank,
            'top': [
                {
                    'src': os.path.basename(str((d.metadata or {}).get('source', ''))),
                    'text': d.page_content[:60].replace('\n', ' '),
                }
                for d in docs[:3]
            ],
        })
        print('  [%2d/%d] %-4s rank=%-4s %s' % (i, len(rows), r['qid'],
                                                rank if rank else '未中', r['query'][:26]))

    n = len(details)

    print('\n' + '=' * 56)
    print('整体指标（正样本 %d 条）' % n)
    print('=' * 56)
    for k in (1, 3, 5, 10):
        hit = sum(1 for d in details if d['rank'] and d['rank'] <= k)
        print('  Recall@%-2d  %2d/%d  %5.1f%%' % (k, hit, n, 100 * hit / n))
    mrr = sum(1 / d['rank'] for d in details if d['rank']) / n
    print('  MRR        %.3f' % mrr)

    print('\n分类型')
    for t in ('single', 'multi'):
        sub = [d for d in details if d['type'] == t]
        if not sub:
            continue
        hit3 = sum(1 for d in sub if d['rank'] and d['rank'] <= 3)
        print('  %-7s %d 条  Recall@3 = %.0f%%' % (t, len(sub), 100 * hit3 / len(sub)))

    missed = [d for d in details if not d['rank']]
    print('\n' + '=' * 56)
    print('未命中 %d 条' % len(missed))
    print('=' * 56)
    for d in missed:
        print('[%s] %s | %s' % (d['qid'], d['type'], d['query']))
        for i, t in enumerate(d['top'], 1):
            print('    top%d [%s] %s' % (i, t['src'], t['text']))

    path = os.path.join('eval', out_name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'config': {'mode': 'vector_only', 'k': TOP},
                   'metrics': {'recall@3': sum(1 for d in details if d['rank'] and d['rank'] <= 3) / n,
                               'recall@10': sum(1 for d in details if d['rank'] and d['rank'] <= 10) / n,
                               'mrr': mrr},
                   'details': details}, f, ensure_ascii=False, indent=2)
    print('\n明细已保存: %s' % path)


if __name__ == '__main__':
    main()
