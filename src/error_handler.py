"""
Error Handler - Centralized error handling and recovery

Handles:
- Agent timeout errors
- File operation errors
- Network errors
- Security violations
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error type enumeration"""
    TIMEOUT = "timeout"
    FILE_OPERATION = "file_operation"
    NETWORK = "network"
    SECURITY = "security"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.error_log = []
        self.error_counts = {}
        self.recovery_strategies = {
            ErrorType.TIMEOUT: self._handle_timeout,
            ErrorType.FILE_OPERATION: self._handle_file_operation,
            ErrorType.NETWORK: self._handle_network,
            ErrorType.SECURITY: self._handle_security,
        }
    
    def handle_error(
        self,
        error_type: ErrorType,
        error_message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle error with appropriate recovery strategy
        
        Args:
            error_type: Type of error
            error_message: Error message
            severity: Error severity
            context: Additional context
            
        Returns:
            Recovery result
        """
        if context is None:
            context = {}
        
        # Log error
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type.value,
            'severity': severity.value,
            'message': error_message,
            'context': context
        }
        
        self.error_log.append(error_entry)
        
        # Update error count
        error_key = f"{error_type.value}_{severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        logger.error(
            f"[{severity.value.upper()}] {error_type.value}: {error_message}",
            extra={'context': context}
        )
        
        # Get recovery strategy
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            return strategy(error_message, context)
        else:
            return self._handle_unknown(error_message, context)
    
    def _handle_timeout(self, error_message: str, context: Dict) -> Dict[str, Any]:
        """Handle timeout error"""
        agent_id = context.get('agent_id')
        timeout_duration = context.get('timeout_duration', 300)
        
        logger.warning(f"Agent {agent_id} timed out after {timeout_duration}s")
        
        return {
            'success': False,
            'error_type': 'timeout',
            'recovery_action': 'kill_agent',
            'agent_id': agent_id,
            'message': f"Agent killed due to timeout ({timeout_duration}s)"
        }
    
    def _handle_file_operation(self, error_message: str, context: Dict) -> Dict[str, Any]:
        """Handle file operation error"""
        file_path = context.get('file_path')
        operation = context.get('operation', 'unknown')
        
        logger.warning(f"File operation failed: {operation} on {file_path}")
        
        return {
            'success': False,
            'error_type': 'file_operation',
            'recovery_action': 'rollback',
            'file_path': file_path,
            'operation': operation,
            'message': f"File operation rolled back: {error_message}"
        }
    
    def _handle_network(self, error_message: str, context: Dict) -> Dict[str, Any]:
        """Handle network error"""
        endpoint = context.get('endpoint', 'unknown')
        attempt = context.get('attempt', 1)
        max_retries = context.get('max_retries', 3)
        
        logger.warning(f"Network error to {endpoint} (attempt {attempt}/{max_retries})")
        
        should_retry = attempt < max_retries
        
        return {
            'success': False,
            'error_type': 'network',
            'recovery_action': 'retry' if should_retry else 'fail',
            'endpoint': endpoint,
            'attempt': attempt,
            'max_retries': max_retries,
            'should_retry': should_retry,
            'message': f"Network error: {error_message}"
        }
    
    def _handle_security(self, error_message: str, context: Dict) -> Dict[str, Any]:
        """Handle security violation"""
        violation_type = context.get('violation_type', 'unknown')
        agent_id = context.get('agent_id')
        
        logger.critical(f"Security violation: {violation_type} by agent {agent_id}")
        
        return {
            'success': False,
            'error_type': 'security',
            'recovery_action': 'block_and_alert',
            'violation_type': violation_type,
            'agent_id': agent_id,
            'message': f"Security violation blocked: {error_message}"
        }
    
    def _handle_unknown(self, error_message: str, context: Dict) -> Dict[str, Any]:
        """Handle unknown error"""
        logger.error(f"Unknown error: {error_message}")
        
        return {
            'success': False,
            'error_type': 'unknown',
            'recovery_action': 'log_and_continue',
            'message': error_message
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': len(self.error_log),
            'error_counts': self.error_counts,
            'recent_errors': self.error_log[-10:] if self.error_log else []
        }
    
    def get_error_history(self, error_type: Optional[ErrorType] = None) -> list:
        """Get error history with optional filtering"""
        history = self.error_log
        
        if error_type:
            history = [e for e in history if e['type'] == error_type.value]
        
        return history
