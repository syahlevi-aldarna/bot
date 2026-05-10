"""
SONA Learner - Self-Optimizing Neural Architecture pattern learning

Learns patterns from successful task executions and applies them to new tasks.
Tracks:
- Solution patterns
- Success rates
- Execution times
- Code patterns
"""

import logging
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class SONALearner:
    """Learns patterns from task execution history"""
    
    def __init__(self):
        self.patterns = {}  # pattern_id -> pattern data
        self.pattern_success = defaultdict(lambda: {'success': 0, 'total': 0})
        self.code_patterns = []  # Common code patterns
        self.execution_history = []  # All executions
        
    def learn_from_task(self, task: Dict, result: Dict) -> bool:
        """
        Learn from completed task
        
        Args:
            task: Task description
            result: Execution result
            
        Returns:
            True if pattern learned
        """
        try:
            logger.info(f"Learning from task: {task.get('id', 'unknown')}")
            
            # Extract pattern
            pattern = self._extract_pattern(task, result)
            
            # Store pattern
            pattern_id = f"pattern_{len(self.patterns)}"
            self.patterns[pattern_id] = pattern
            
            # Update success rate
            success = result.get('success', False)
            self.pattern_success[pattern_id]['total'] += 1
            if success:
                self.pattern_success[pattern_id]['success'] += 1
            
            # Store execution
            self.execution_history.append({
                'task_id': task.get('id'),
                'pattern_id': pattern_id,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Pattern learned: {pattern_id}")
            return True
        except Exception as e:
            logger.error(f"Error learning from task: {str(e)}")
            return False
    
    def get_applicable_patterns(self, task: Dict, top_k: int = 3) -> List[Dict]:
        """
        Get patterns applicable to task
        
        Args:
            task: Task description
            top_k: Number of patterns to return
            
        Returns:
            List of applicable patterns with success rates
        """
        applicable = []
        
        for pattern_id, pattern in self.patterns.items():
            # Check if pattern applies to task
            if self._pattern_applies(pattern, task):
                success_rate = self._get_success_rate(pattern_id)
                
                applicable.append({
                    'pattern_id': pattern_id,
                    'pattern': pattern,
                    'success_rate': success_rate,
                    'executions': self.pattern_success[pattern_id]['total']
                })
        
        # Sort by success rate
        applicable.sort(key=lambda x: x['success_rate'], reverse=True)
        
        logger.info(f"Found {len(applicable)} applicable patterns")
        return applicable[:top_k]
    
    def _extract_pattern(self, task: Dict, result: Dict) -> Dict:
        """Extract pattern from task and result"""
        return {
            'task_type': task.get('type', 'unknown'),
            'task_keywords': self._extract_keywords(task.get('description', '')),
            'solution_type': result.get('solution_type', 'unknown'),
            'code_pattern': result.get('code_pattern', ''),
            'execution_time': result.get('execution_time', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def _pattern_applies(self, pattern: Dict, task: Dict) -> bool:
        """Check if pattern applies to task"""
        # Simple keyword matching
        task_keywords = set(self._extract_keywords(task.get('description', '')))
        pattern_keywords = set(pattern.get('task_keywords', []))
        
        # Pattern applies if there's keyword overlap
        overlap = len(task_keywords & pattern_keywords)
        return overlap > 0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if len(w) > 3]
        return keywords
    
    def _get_success_rate(self, pattern_id: str) -> float:
        """Get success rate for pattern"""
        stats = self.pattern_success[pattern_id]
        if stats['total'] == 0:
            return 0.0
        return stats['success'] / stats['total']
    
    def get_stats(self) -> Dict:
        """Get learning statistics"""
        total_patterns = len(self.patterns)
        successful_patterns = len([
            p for p, s in self.pattern_success.items()
            if s['success'] > 0
        ])
        
        return {
            'total_patterns': total_patterns,
            'successful_patterns': successful_patterns,
            'total_executions': len(self.execution_history),
            'average_success_rate': self._calculate_avg_success_rate()
        }
    
    def _calculate_avg_success_rate(self) -> float:
        """Calculate average success rate across all patterns"""
        if not self.pattern_success:
            return 0.0
        
        total_success = sum(s['success'] for s in self.pattern_success.values())
        total_executions = sum(s['total'] for s in self.pattern_success.values())
        
        if total_executions == 0:
            return 0.0
        
        return total_success / total_executions
