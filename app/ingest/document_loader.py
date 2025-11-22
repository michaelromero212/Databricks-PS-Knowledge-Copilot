import os
import json
from typing import List, Dict
from .cleaner import Cleaner

class DocumentLoader:
    def __init__(self, docs_dir: str):
        self.docs_dir = docs_dir

    def load_documents(self) -> List[Dict[str, str]]:
        """Loads documents from the specified directory."""
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
