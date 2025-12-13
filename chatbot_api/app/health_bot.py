import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class HealthBot:
    def __init__(self):
        self.model_name = 'all-MiniLM-L6-v2'
        print(f"Loading HealthBot model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        
        self.corpus_path = os.path.join(os.path.dirname(__file__), '../corpus/cleaned/health_data.json')
        self.index_path = os.path.join(os.path.dirname(__file__), '../embeddings/faiss_index.bin')
        
        self.corpus = []
        self.index = None
        self._load_resources()

    def _load_resources(self):
        # Load Corpus
        if os.path.exists(self.corpus_path):
             with open(self.corpus_path, 'r', encoding='utf-8') as f:
                 self.corpus = json.load(f)
             print(f"Loaded {len(self.corpus)} documents from corpus.")
        else:
            print("Warning: Corpus file not found.")

        # Load or Build FAISS Index
        if os.path.exists(self.index_path):
            print("Loading FAISS index...")
            self.index = faiss.read_index(self.index_path)
        else:
            print("Building FAISS index...")
            self._build_index()

    def _build_index(self):
        if not self.corpus:
            print("No corpus to build index.")
            return

        texts = [doc['text'] for doc in self.corpus]
        embeddings = self.model.encode(texts)
        
        # Initialize FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save
        faiss.write_index(self.index, self.index_path)
        print("FAISS index built and saved.")

    def search(self, query: str, top_k: int = 2):
        if not self.index or not self.corpus:
            return "I'm sorry, my health knowledge base is currently unavailable."

        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        results = []
        for i in range(top_k):
            idx = indices[0][i]
            if idx < len(self.corpus):
                results.append(self.corpus[idx]['text'])
                
        if results:
            return "Based on my health verification:\n" + "\n\n".join(results)
        return "I couldn't find relevant health information for your query."
