import chromadb
from typing import List, Dict, Any

class ChromaClient:
    def __init__(self, persistence_path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        self.collection = self.client.get_or_create_collection(name="knowledge_base")

    def upsert_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str], embeddings: List[List[float]]):
        """Upserts documents into the Chroma collection."""
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

    def search(self, query_embeddings: List[List[float]], k: int = 5) -> Dict[str, Any]:
        """Searches the Chroma collection."""
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=k
        )
