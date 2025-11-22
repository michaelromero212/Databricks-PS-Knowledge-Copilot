from typing import List, Dict, Any
from ..vectorstore.chroma_client import ChromaClient
from ..vectorstore.databricks_vs_client import DatabricksVectorSearchClient
from .embedder import Embedder

class Retriever:
    def __init__(self, use_databricks: bool = False):
        self.embedder = Embedder()
        self.use_databricks = use_databricks
        if self.use_databricks:
            self.vector_store = DatabricksVectorSearchClient()
        else:
            self.vector_store = ChromaClient()

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant documents for a query."""
        query_embedding = self.embedder.generate_embeddings([query])[0]
        
        if self.use_databricks:
            # Placeholder for Databricks search logic
            results = self.vector_store.search("knowledge_index", [query_embedding], k)
        else:
            results = self.vector_store.search([query_embedding], k)
            # Format Chroma results to a standard list of dicts
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "id": results['ids'][0][i]
                    })
            return formatted_results
        return []
