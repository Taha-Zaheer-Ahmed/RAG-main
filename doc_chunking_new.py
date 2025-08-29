import re
import os, numpy as np, faiss, pickle
from openai import OpenAI 

client = OpenAI(api_key="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", 
                base_url="https://models.github.ai/inference")

def split_by_id(text, file_name):
    pattern = re.compile(r'(\{#[-A-Za-z0-9_]+\}|\{FR-\d+\})')
    matches = list(pattern.finditer(text))
    sections = []

    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        raw = text[start:end].strip()
        id_token = m.group(0).strip('{}')

        sections.append({
            'id': id_token,
            'text': raw,
            'file': file_name,
            'chunk_idx': i
        })

    return sections


file = 'Multi-User AI Chat Platform — Source of Truth.md'
with open(file, 'r', encoding='utf-8') as f:
    filedata = f.read()

chunks = split_by_id(filedata, file)

# --- Batch Embedding Call ---
texts = [c['text'] for c in chunks]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

# Collect embeddings for all chunks in order
vecs = np.vstack([np.array(d.embedding, dtype='float32') for d in response.data])

# --- FAISS Indexing ---
faiss.normalize_L2(vecs)
dim = vecs.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(vecs)

pickle.dump({'index': index, 'metas': chunks}, open('SoT.pkl','wb'))
