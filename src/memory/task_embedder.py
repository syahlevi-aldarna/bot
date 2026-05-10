"""
Task Embedder - Convert task descriptions to vector embeddings

Uses simple TF-IDF based embedding for similarity search.
Can be replaced with more sophisticated embeddings (BERT, etc.)
"""

import logging
import math
from typing import List, Dict
from collections import Counter

logger = logging.getLogger(__name__)


class TaskEmbedder:
    """Converts task descriptions to embeddings"""
    
    def __init__(self):
        self.vocabulary = {}  # word -> index
        self.idf = {}  # word -> IDF score
        self.vocab_size = 0
        
    def build_vocabulary(self, documents: List[str]):
        """
        Build vocabulary from documents
        
        Args:
            documents: List of task descriptions
        """
        logger.info(f"Building vocabulary from {len(documents)} documents...")
        
        # Count document frequency
        doc_freq = Counter()
        all_words = set()
        
        for doc in documents:
            words = set(self._tokenize(doc))
            all_words.update(words)
            doc_freq.update(words)
        
        # Build vocabulary
        for i, word in enumerate(sorted(all_words)):
            self.vocabulary[word] = i
        
        # Calculate IDF
        num_docs = len(documents)
        for word, freq in doc_freq.items():
            self.idf[word] = math.log(num_docs / freq) if freq > 0 else 0
        
        self.vocab_size = len(self.vocabulary)
        logger.info(f"Vocabulary built: {self.vocab_size} words")
    
    def embed_task(self, task_description: str) -> List[float]:
        """
        Convert task description to embedding
        
        Args:
            task_description: Task description text
            
        Returns:
            Vector embedding
        """
        if self.vocab_size == 0:
            logger.warning("Vocabulary not built, using default embedding")
            return self._default_embedding(task_description)
        
        # Tokenize
        words = self._tokenize(task_description)
        word_freq = Counter(words)
        
        # Create TF-IDF vector
        embedding = [0.0] * self.vocab_size
        
        for word, freq in word_freq.items():
            if word in self.vocabulary:
                idx = self.vocabulary[word]
                tf = freq / len(words) if len(words) > 0 else 0
                idf = self.idf.get(word, 0)
                embedding[idx] = tf * idf
        
        # Normalize
        norm = sum(x**2 for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and split
        words = text.lower().split()
        
        # Remove punctuation and short words
        words = [w.strip('.,!?;:') for w in words]
        words = [w for w in words if len(w) > 2]
        
        return words
    
    def _default_embedding(self, text: str) -> List[float]:
        """Create default embedding when vocabulary not built"""
        # Simple hash-based embedding
        words = self._tokenize(text)
        embedding = [0.0] * 100  # Fixed size
        
        for word in words:
            idx = hash(word) % 100
            embedding[idx] += 1.0
        
        # Normalize
        norm = sum(x**2 for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
