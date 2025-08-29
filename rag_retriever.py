import pickle
import numpy as np
from openai import OpenAI
import faiss

class RAGRetriever:
    def __init__(self, index_path="SoT.pkl"):
        # Load the pre-built index
        data = pickle.load(open(index_path, "rb"))
        self.index = data['index']
        self.metas = data['metas']
        
        # Initialize OpenAI client for embeddings
        self.client = OpenAI(
            api_key="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",
            base_url="https://models.github.ai/inference"
        )
    
    def embed(self, text):
        """Embed text using OpenAI's embedding model"""
        r = self.client.embeddings.create(
            model="text-embedding-3-small", 
            input=text
        )
        v = np.array(r.data[0].embedding, dtype='float32')
        faiss.normalize_L2(v.reshape(1,-1))
        return v
    
    def search(self, query, k=5):
        """Search for relevant document chunks"""
        qv = self.embed(query)
        D, I = self.index.search(np.ascontiguousarray(qv.reshape(1,-1)), k)
        
        results = []
        for score, idx in zip(D[0], I[0]):
            m = self.metas[int(idx)]
            results.append({
                "id": m['id'], 
                "text": m['text'], 
                "file": m.get('file'), 
                "score": float(score)
            })
        
        return results
    
    def get_relevant_context(self, query, k=3):
        """Get formatted context for a query"""
        results = self.search(query, k)
        context = "\n\n".join([
            f"[{r['id']}] (relevance: {r['score']:.3f})\n{r['text']}" 
            for r in results
        ])
        return context

# Create a global instance
rag_retriever = RAGRetriever()
