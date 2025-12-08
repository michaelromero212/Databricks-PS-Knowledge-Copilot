import os
import json
from typing import List, Dict, Optional
from .cleaner import Cleaner
from .chunker import TextChunker


class DocumentLoader:
    """
    Loads and processes documents from a directory for RAG ingestion.
    
    Supports:
    - Markdown (.md)
    - Plain text (.txt)
    - Jupyter notebooks (.ipynb)
    
    Documents are automatically cleaned and chunked for optimal retrieval.
    """
    
    def __init__(self, docs_dir: str, chunker: Optional[TextChunker] = None):
        """
        Initialize the document loader.
        
        Args:
            docs_dir: Directory containing documents to load
            chunker: Optional TextChunker instance. If None, creates default.
        """
        self.docs_dir = docs_dir
        self.chunker = chunker or TextChunker()

    def load_documents(self, chunk: bool = True) -> List[Dict[str, str]]:
        """
        Loads documents from the specified directory.
        
        Args:
            chunk: Whether to chunk documents (default True for better retrieval)
            
        Returns:
            List of document dictionaries with content and metadata
        """
        documents = []
        for root, _, files in os.walk(self.docs_dir):
            for file in files:
                file_path = os.path.join(root, file)
                content = self._load_file(file_path)
                if content:
                    documents.append({
                        "source": file,
                        "content": content,
                        "path": file_path
                    })
        
        # Apply chunking if enabled
        if chunk and documents:
            return self.chunker.chunk_documents(documents)
        
        return documents

    def _load_file(self, file_path: str) -> str:
        """Loads a single file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in ['.md', '.txt']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return Cleaner.clean_text(f.read())
            elif ext == '.ipynb':
                return self._load_notebook(file_path)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
        return ""

    def _load_notebook(self, file_path: str) -> str:
        """Extracts code and markdown from a Jupyter notebook."""
        text_content = []
        with open(file_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
            for cell in nb.get('cells', []):
                if cell.get('cell_type') in ['markdown', 'code']:
                    source = ''.join(cell.get('source', []))
                    text_content.append(source)
        return Cleaner.clean_text('\n'.join(text_content))

