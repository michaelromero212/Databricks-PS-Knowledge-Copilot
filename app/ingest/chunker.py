"""
Text Chunking Module for RAG Pipeline

This module implements intelligent text chunking strategies optimized for 
retrieval-augmented generation with the MiniLM embedding model.

Key Features:
- Recursive character-based splitting for semantic coherence
- Configurable chunk sizes optimized for different embedding models
- Overlap to preserve context between chunks
- Metadata preservation for source tracking
"""

from typing import List, Dict, Any
import re


class TextChunker:
    """
    Splits documents into smaller chunks optimized for embedding and retrieval.
    
    The default parameters are tuned for `all-MiniLM-L6-v2` which has a 
    max sequence length of 256 tokens (~1000 characters).
    """
    
    # Chunk size presets for different embedding models
    PRESETS = {
        "minilm": {"chunk_size": 800, "chunk_overlap": 150},
        "bge-small": {"chunk_size": 1000, "chunk_overlap": 200},
        "nomic": {"chunk_size": 2000, "chunk_overlap": 400},
    }
    
    def __init__(
        self, 
        chunk_size: int = 800, 
        chunk_overlap: int = 150,
        separators: List[str] = None
    ):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
            separators: List of separators to split on, in order of priority
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or [
            "\n\n",      # Paragraph breaks (highest priority)
            "\n",        # Line breaks
            ". ",        # Sentence endings
            "? ",        # Question endings
            "! ",        # Exclamation endings
            "; ",        # Semicolon breaks
            ", ",        # Comma breaks
            " ",         # Word breaks (lowest priority)
        ]
    
    @classmethod
    def from_preset(cls, preset_name: str) -> "TextChunker":
        """
        Create a chunker from a preset configuration.
        
        Args:
            preset_name: One of 'minilm', 'bge-small', 'nomic'
            
        Returns:
            Configured TextChunker instance
        """
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(cls.PRESETS.keys())}")
        return cls(**cls.PRESETS[preset_name])
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks using recursive character splitting.
        
        Args:
            text: The input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        return self._recursive_split(text, self.separators)
    
    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using a hierarchy of separators.
        
        Args:
            text: Text to split
            separators: Remaining separators to try
            
        Returns:
            List of text chunks
        """
        if not separators:
            # Fallback: hard split by chunk_size
            return self._hard_split(text)
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by current separator
        parts = text.split(separator)
        
        chunks = []
        current_chunk = ""
        
        for i, part in enumerate(parts):
            # Add separator back (except for last part)
            part_with_sep = part + separator if i < len(parts) - 1 else part
            
            if len(current_chunk) + len(part_with_sep) <= self.chunk_size:
                current_chunk += part_with_sep
            else:
                # Current chunk is full
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Check if this single part is too large
                if len(part_with_sep) > self.chunk_size:
                    # Recursively split with next separator
                    sub_chunks = self._recursive_split(part_with_sep, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part_with_sep
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Apply overlap
        return self._apply_overlap(chunks)
    
    def _hard_split(self, text: str) -> List[str]:
        """
        Hard split text by chunk_size when no separators work.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """
        Apply overlap between consecutive chunks for context preservation.
        
        Args:
            chunks: List of non-overlapping chunks
            
        Returns:
            List of overlapping chunks
        """
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks
        
        overlapped = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            curr_chunk = chunks[i]
            
            # Get overlap from previous chunk
            overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
            
            # Find a clean break point in the overlap
            clean_break = self._find_clean_break(overlap_text)
            if clean_break:
                overlap_text = overlap_text[clean_break:]
            
            overlapped.append(overlap_text + " " + curr_chunk)
        
        return overlapped
    
    def _find_clean_break(self, text: str) -> int:
        """
        Find a clean break point (sentence or paragraph boundary) in text.
        
        Args:
            text: Text to search for break point
            
        Returns:
            Index of break point, or 0 if none found
        """
        # Look for sentence boundaries
        for pattern in [r'\. ', r'\? ', r'! ', r'\n']:
            match = re.search(pattern, text)
            if match:
                return match.end()
        return 0
    
    def chunk_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Chunk a list of documents, preserving metadata.
        
        Args:
            documents: List of document dicts with 'content' and 'source' keys
            
        Returns:
            List of chunked documents with updated metadata
        """
        chunked_docs = []
        
        for doc in documents:
            content = doc.get("content", "")
            source = doc.get("source", "unknown")
            original_path = doc.get("path", "")
            
            chunks = self.chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    "content": chunk,
                    "source": source,
                    "path": original_path,
                    "metadata": {
                        "source": source,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "original_path": original_path,
                    }
                })
        
        return chunked_docs


# Convenience function for simple usage
def chunk_text(
    text: str, 
    chunk_size: int = 800, 
    chunk_overlap: int = 150
) -> List[str]:
    """
    Simple function to chunk text with default settings.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_text(text)
