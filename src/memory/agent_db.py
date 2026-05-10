"""
AgentDB - Vector database for storing and retrieving task results

Stores:
- Task descriptions
- Solutions/code
- Embeddings (for similarity search)
- Metadata (timestamp, success rate, etc.)
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class AgentDB:
    """Vector database for task storage and retrieval"""
    
    def __init__(self):
        self.tasks = []  # List of stored tasks
        self.embeddings = []  # Corresponding embeddings
        self.index = {}  # task_id -> task mapping
        
    def store_task(self, task_id: str, task_data: Dict, embedding: List[float]) -> bool:
        """
        Store task with embedding
        
        Args:
            task_id: Unique task identifier
            task_data: Task description, code, results
            embedding: Vector embedding for similarity search
            
        Returns:
            True if stored successfully
        """
        try:
            # Add metadata
            task_data['id'] = task_id
            task_data['timestamp'] = datetime.now().isoformat()
            task_data['embedding'] = embedding
            
            # Store in database
            self.tasks.append(task_data)
            self.embeddings.append(embedding)
            self.index[task_id] = len(self.tasks) - 1
            
            logger.info(f"Task stored: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing task: {str(e)}")
            return False
    
    def retrieve_task(self, task_id: str) -> Optional[Dict]:
        """
        Retrieve task by ID
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task data or None if not found
        """
        if task_id not in self.index:
            return None
        
        idx = self.index[task_id]
        return self.tasks[idx]
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar tasks using embeddings
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            List of similar tasks with similarity scores
        """
        if not self.embeddings:
            return []
        
        # Calculate similarity scores (cosine similarity)
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, emb in enumerate(self.embeddings):
            emb_vec = np.array(emb)
            
            # Cosine similarity
            dot_product = np.dot(query_vec, emb_vec)
            norm_query = np.linalg.norm(query_vec)
            norm_emb = np.linalg.norm(emb_vec)
            
            if norm_query > 0 and norm_emb > 0:
                similarity = dot_product / (norm_query * norm_emb)
            else:
                similarity = 0
            
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results
        results = []
        for idx, score in similarities[:top_k]:
            task = self.tasks[idx].copy()
            task['similarity_score'] = float(score)
            results.append(task)
        
        logger.info(f"Found {len(results)} similar tasks")
        return results
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all stored tasks"""
        return self.tasks.copy()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'total_tasks': len(self.tasks),
            'successful_tasks': len([t for t in self.tasks if t.get('success', False)]),
            'average_success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate average success rate"""
        if not self.tasks:
            return 0.0
        
        successful = len([t for t in self.tasks if t.get('success', False)])
        return successful / len(self.tasks)
