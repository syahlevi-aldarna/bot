"""
Memory Operation Logger - Logs all memory and learning operations

Responsibilities:
- Log memory store operations
- Log memory search operations
- Log pattern learning
- Track memory statistics
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class MemoryOperation(Enum):
    """Memory operation types"""
    STORE = "store"
    RETRIEVE = "retrieve"
    SEARCH = "search"
    DELETE = "delete"
    LEARN_PATTERN = "learn_pattern"
    APPLY_PATTERN = "apply_pattern"
    UPDATE_STATS = "update_stats"


class MemoryOperationLogger:
    """Logs memory and learning operations"""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize memory operation logger
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.operation_history = []
    
    def log_store(
        self,
        task_id: str,
        task_type: str,
        embedding_size: int,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Log memory store operation"""
        if metadata is None:
            metadata = {}
        
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.STORE.value,
            'task_id': task_id,
            'task_type': task_type,
            'embedding_size': embedding_size,
            'metadata': metadata
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Memory store: {task_id} ({task_type}, {embedding_size} dims)",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def log_retrieve(self, task_id: str, found: bool) -> Dict:
        """Log memory retrieve operation"""
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.RETRIEVE.value,
            'task_id': task_id,
            'found': found
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Memory retrieve: {task_id} ({'found' if found else 'not found'})",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def log_search(
        self,
        query: str,
        results_count: int,
        top_similarity: float,
        search_time: float
    ) -> Dict:
        """Log memory search operation"""
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.SEARCH.value,
            'query': query,
            'results_count': results_count,
            'top_similarity': top_similarity,
            'search_time': search_time
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Memory search: '{query}' → {results_count} results (top: {top_similarity:.2f}, {search_time:.3f}s)",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def log_delete(self, task_id: str, reason: str) -> Dict:
        """Log memory delete operation"""
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.DELETE.value,
            'task_id': task_id,
            'reason': reason
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Memory delete: {task_id} ({reason})",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def log_learn_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        success: bool,
        confidence: float
    ) -> Dict:
        """Log pattern learning"""
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.LEARN_PATTERN.value,
            'pattern_id': pattern_id,
            'pattern_type': pattern_type,
            'success': success,
            'confidence': confidence
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Pattern learned: {pattern_id} ({pattern_type}, success={success}, confidence={confidence:.2f})",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def log_apply_pattern(
        self,
        pattern_id: str,
        task_id: str,
        applied: bool,
        result: Optional[Dict] = None
    ) -> Dict:
        """Log pattern application"""
        if result is None:
            result = {}
        
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.APPLY_PATTERN.value,
            'pattern_id': pattern_id,
            'task_id': task_id,
            'applied': applied,
            'result': result
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Pattern applied: {pattern_id} to {task_id} ({'success' if applied else 'failed'})",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def log_update_stats(
        self,
        total_tasks: int,
        total_patterns: int,
        avg_similarity: float,
        success_rate: float
    ) -> Dict:
        """Log memory statistics update"""
        operation = {
            'timestamp': datetime.now().isoformat(),
            'operation': MemoryOperation.UPDATE_STATS.value,
            'total_tasks': total_tasks,
            'total_patterns': total_patterns,
            'avg_similarity': avg_similarity,
            'success_rate': success_rate
        }
        
        self.operation_history.append(operation)
        self.logger.info(
            f"Memory stats: {total_tasks} tasks, {total_patterns} patterns, "
            f"avg_sim={avg_similarity:.2f}, success={success_rate:.2%}",
            extra={'extra_data': operation}
        )
        
        return operation
    
    def get_operation_history(self, operation_type: Optional[str] = None) -> list:
        """Get operation history with optional filtering"""
        history = self.operation_history
        
        if operation_type:
            history = [o for o in history if o['operation'] == operation_type]
        
        return history
    
    def get_stats(self) -> Dict:
        """Get memory operation statistics"""
        total_ops = len(self.operation_history)
        
        store_ops = len([o for o in self.operation_history if o['operation'] == MemoryOperation.STORE.value])
        search_ops = len([o for o in self.operation_history if o['operation'] == MemoryOperation.SEARCH.value])
        learn_ops = len([o for o in self.operation_history if o['operation'] == MemoryOperation.LEARN_PATTERN.value])
        apply_ops = len([o for o in self.operation_history if o['operation'] == MemoryOperation.APPLY_PATTERN.value])
        
        avg_search_time = 0
        search_times = [o.get('search_time', 0) for o in self.operation_history if o['operation'] == MemoryOperation.SEARCH.value]
        if search_times:
            avg_search_time = sum(search_times) / len(search_times)
        
        return {
            'total_operations': total_ops,
            'store_operations': store_ops,
            'search_operations': search_ops,
            'learn_operations': learn_ops,
            'apply_operations': apply_ops,
            'avg_search_time': avg_search_time
        }
