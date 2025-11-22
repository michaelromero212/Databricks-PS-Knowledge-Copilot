from sentence_transformers import SentenceTransformer
from typing import List

class Embedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
