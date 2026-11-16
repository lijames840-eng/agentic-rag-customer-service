# eval/export_chunks.py
import csv, os, sys
sys.path.insert(0, '.')

from rag.vector_store import VectorStoreService

vs = VectorStoreService()
col = vs.vector_store._collection
data = col.get(include=['documents', 'metadatas'])

os.makedirs('eval', exist_ok=True)
with open('eval/chunks.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['chunk_id', 'source', 'page', 'text'])
    for cid, doc, meta in zip(data['ids'], data['documents'], data['metadatas']):
        meta = meta or {}
        w.writerow([cid, os.path.basename(str(meta.get('source', ''))),
                    meta.get('page', ''), doc])

print(f'已导出 {len(data["ids"])} 条 → eval/chunks.csv')
