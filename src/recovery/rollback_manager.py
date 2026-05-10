"""
Rollback Manager - Handles file operation rollback and recovery

Responsibilities:
- Track file operations
- Rollback failed operations
- Restore from backups
- Maintain operation history
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class RollbackManager:
    """Manages file operation rollback"""
    
    def __init__(self, backup_dir: str = ".backups"):
        """
        Initialize rollback manager
        
        Args:
            backup_dir: Directory for backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.operation_history = []
        self.rollback_history = []
    
    def track_operation(
        self,
        operation_id: str,
        operation_type: str,
        file_path: str,
        backup_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Track file operation
        
        Args:
            operation_id: Unique operation ID
            operation_type: Type of operation (write, delete, edit)
            file_path: File being operated on
            backup_path: Path to backup (if created)
            metadata: Additional metadata
            
        Returns:
            Operation tracking result
        """
        if metadata is None:
            metadata = {}
        
        operation = {
            'id': operation_id,
            'type': operation_type,
            'file_path': file_path,
            'backup_path': backup_path,
            'timestamp': datetime.now().isoformat(),
            'status': 'tracked',
            'metadata': metadata
        }
        
        self.operation_history.append(operation)
        
        logger.info(f"Operation tracked: {operation_id} ({operation_type} on {file_path})")
        
        return {
            'success': True,
            'operation_id': operation_id,
            'tracked': True
        }
    
    async def rollback_operation(
        self,
        operation_id: str,
        file_executor
    ) -> Dict:
        """
        Rollback file operation
        
        Args:
            operation_id: Operation ID to rollback
            file_executor: FileExecutor instance for restore
            
        Returns:
            Rollback result
        """
        # Find operation
        operation = None
        for op in self.operation_history:
            if op['id'] == operation_id:
                operation = op
                break
        
        if not operation:
            logger.error(f"Operation {operation_id} not found")
            return {
                'success': False,
                'error': f'Operation {operation_id} not found'
            }
        
        try:
            operation_type = operation['type']
            file_path = operation['file_path']
            backup_path = operation['backup_path']
            
            if operation_type == 'write' and backup_path:
                # Restore from backup
                result = file_executor.restore_backup(backup_path)
                
                if result['success']:
                    logger.info(f"Operation {operation_id} rolled back successfully")
                    
                    # Track rollback
                    self.rollback_history.append({
                        'operation_id': operation_id,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'success'
                    })
                    
                    return {
                        'success': True,
                        'operation_id': operation_id,
                        'file_path': file_path,
                        'message': 'Operation rolled back'
                    }
                else:
                    logger.error(f"Failed to restore backup: {result.get('error')}")
                    return {
                        'success': False,
                        'error': f"Failed to restore backup: {result.get('error')}"
                    }
            
            elif operation_type == 'delete' and backup_path:
                # Restore deleted file
                result = file_executor.restore_backup(backup_path)
                
                if result['success']:
                    logger.info(f"Deleted file restored: {file_path}")
                    
                    self.rollback_history.append({
                        'operation_id': operation_id,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'success'
                    })
                    
                    return {
                        'success': True,
                        'operation_id': operation_id,
                        'file_path': file_path,
                        'message': 'Deleted file restored'
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Failed to restore deleted file: {result.get('error')}"
                    }
            
            else:
                logger.warning(f"Cannot rollback operation type: {operation_type}")
                return {
                    'success': False,
                    'error': f'Cannot rollback operation type: {operation_type}'
                }
        
        except Exception as e:
            logger.error(f"Error rolling back operation: {str(e)}")
            
            self.rollback_history.append({
                'operation_id': operation_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': str(e)
            }
    
    async def rollback_all_operations(
        self,
        file_executor,
        since_timestamp: Optional[str] = None
    ) -> Dict:
        """
        Rollback all operations (or since timestamp)
        
        Args:
            file_executor: FileExecutor instance
            since_timestamp: ISO timestamp to rollback from
            
        Returns:
            Rollback result
        """
        operations_to_rollback = self.operation_history.copy()
        
        if since_timestamp:
            operations_to_rollback = [
                op for op in operations_to_rollback
                if op['timestamp'] >= since_timestamp
            ]
        
        # Rollback in reverse order (LIFO)
        operations_to_rollback.reverse()
        
        results = []
        for operation in operations_to_rollback:
            result = await self.rollback_operation(operation['id'], file_executor)
            results.append(result)
        
        successful = len([r for r in results if r['success']])
        
        logger.info(f"Rolled back {successful}/{len(results)} operations")
        
        return {
            'success': True,
            'total_operations': len(results),
            'successful_rollbacks': successful,
            'results': results
        }
    
    def get_operation_history(self) -> List[Dict]:
        """Get operation history"""
        return self.operation_history.copy()
    
    def get_rollback_history(self) -> List[Dict]:
        """Get rollback history"""
        return self.rollback_history.copy()
    
    def get_stats(self) -> Dict:
        """Get rollback statistics"""
        total_operations = len(self.operation_history)
        total_rollbacks = len(self.rollback_history)
        successful_rollbacks = len([r for r in self.rollback_history if r['status'] == 'success'])
        
        return {
            'total_operations': total_operations,
            'total_rollbacks': total_rollbacks,
            'successful_rollbacks': successful_rollbacks,
            'failed_rollbacks': total_rollbacks - successful_rollbacks
        }
