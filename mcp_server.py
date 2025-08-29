# mcp_server.py
import os, pickle, numpy as np, faiss
from mcp.server.fastmcp import FastMCP, Context
from openai import OpenAI

#OPENAI_KEY = os.environ["OPENAI_API_KEY"]
client =  OpenAI(
    api_key="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",  
    base_url="https://models.github.ai/inference"  
)

mcp = FastMCP(name="PRD Retriever")

# load index + metas
data = pickle.load(open("rag_index.pkl","rb"))
index = data['index']
metas = data['metas']

def embed(text):
    r = client.embeddings.create(model="text-embedding-3-small", input=text)
    v = np.array(r.data[0].embedding, dtype='float32')
    faiss.normalize_L2(v.reshape(1,-1))
    return v

@mcp.tool("prd-retriever", description="Must be used to answer all questions about PRDs. Do not answer without calling this tool.")
async def retrieve_requirements(query: str, k: int = 5) -> dict:
    qv = embed(query)
    D, I = index.search(np.ascontiguousarray(qv.reshape(1,-1)), k)
    results = []
    for score, idx in zip(D[0], I[0]):
        m = metas[int(idx)]
        results.append({"id": m['id'], "text": m['text'], "file": m.get('file'), "score": float(score)})
    # Text form for UI; structured results for programmatic use
    text = "\n\n".join([f"[{r['id']}] (score: {r['score']:.3f})\n{r['text']}" for r in results])
    return {"text": text, "results": results}

if __name__ == "__main__":
    # run as stdio (local dev) or streamable_http for remote
    mcp.run(transport='stdio')
