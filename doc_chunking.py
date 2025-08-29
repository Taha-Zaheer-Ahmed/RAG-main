import re
import os, numpy as np, faiss, pickle
from openai import OpenAI 


client = OpenAI(api_key="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",
                base_url="https://models.github.ai/inference")

def embed(text):
    r = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(r.data[0].embedding, dtype='float32')



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



vecs = np.vstack([embed(c['text']) for c in chunks])

faiss.normalize_L2(vecs)
dim = vecs.shape[1]
index = faiss.IndexFlatIP(dim)   
index.add(vecs)

pickle.dump({'index': index, 'metas': chunks}, open('SoT.pkl','wb'))