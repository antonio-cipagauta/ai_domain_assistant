import os

import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_embedding(text: str) -> np.ndarray:
    """Gets text embedding from Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Using the verified stable embedding model
    result = client.models.embed_content(
        model="models/gemini-embedding-001", contents=text
    )
    return np.array(result.embeddings[0].values)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class RAGEngine:
    def __init__(self):
        self.knowledge_base = []
        self.embeddings = []
        self.load_knowledge()

    def load_knowledge(self):
        knowledge_dir = "knowledge"
        if not os.path.exists(knowledge_dir):
            print(f"Directory {knowledge_dir} not found.")
            return

        print("Loading knowledge base...")
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".md"):
                path = os.path.join(knowledge_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # We can chunk the content if it's long,
                    # but here we'll keep it simple
                    self.knowledge_base.append(content)
                    self.embeddings.append(get_embedding(content))
        print(f"Loaded {len(self.knowledge_base)} documents.")

    def get_relevant_context(self, query: str, top_k: int = 1) -> str:
        if not self.embeddings:
            return ""

        query_embedding = get_embedding(query)
        similarities = [
            cosine_similarity(query_embedding, emb) for emb in self.embeddings
        ]

        # Get indices of top_k results sorted by similarity using numpy
        top_indices = np.argsort(similarities)[::-1][:top_k]

        relevant_chunks = [self.knowledge_base[i] for i in top_indices]
        return "\n\n".join(relevant_chunks)


if __name__ == "__main__":
    # Quick test
    engine = RAGEngine()
    context = engine.get_relevant_context("AI startup domains")
    print(f"--- RELEVANT CONTEXT ---\n{context[:500]}...")
