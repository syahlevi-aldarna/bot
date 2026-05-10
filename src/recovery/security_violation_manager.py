"""
Security Violation Manager - Handles security violation detection and blocking

Responsibilities:
- Detect security violations
- Block dangerous operations
- Log security events
- Alert on violations
"""

import logging
from typing import Dict, Optional, List, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Security violation types"""
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DANGEROUS_COMMAND = "dangerous_command"
    SECRET_EXPOSURE = "secret_exposure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    UNKNOWN = "unknown"


class ViolationSeverity(Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityViolationManager:
    """Manages security violation detection and blocking"""
    
    def __init__(self):
        self.violations = []
        self.blocked_agents = set()
        self.violation_callbacks = []
        
        # Dangerous patterns
        self.dangerous_patterns = {
            'path_traversal': ['../', '..\\', '~/', '/etc/', '/root/', '/home/'],
            'command_injection': [';', '|', '&', '`', '$', '$(', '&&', '||'],
            'secret_exposure': ['.env', 'SECRET', 'PASSWORD', 'API_KEY', 'TOKEN'],
            'dangerous_commands': ['rm -rf', 'dd if=', 'fork()', ':(){ :|:& };:']
        }
    
    def check_path_security(self, file_path: str) -> Dict:
        """
        Check if file path is safe
        
        Args:
            file_path: File path to check
            
        Returns:
            Security check result
        """
        for pattern in self.dangerous_patterns['path_traversal']:
            if pattern in file_path:
                violation = self._create_violation(
                    ViolationType.PATH_TRAVERSAL,
                    ViolationSeverity.HIGH,
                    f"Path traversal detected: {pattern}",
                    {'file_path': file_path}
                )
                return {
                    'safe': False,
                    'violation': violation
                }
        
        return {'safe': True}
    
    def check_command_security(self, command: str) -> Dict:
        """
        Check if command is safe
        
        Args:
            command: Command to check
            
        Returns:
            Security check result
        """
        # Check for dangerous commands
        for pattern in self.dangerous_patterns['dangerous_commands']:
            if pattern in command:
                violation = self._create_violation(
                    ViolationType.DANGEROUS_COMMAND,
                    ViolationSeverity.CRITICAL,
                    f"Dangerous command detected: {pattern}",
                    {'command': command}
                )
                return {
                    'safe': False,
                    'violation': violation
                }
        
        # Check for command injection
        for pattern in self.dangerous_patterns['command_injection']:
            if pattern in command:
                violation = self._create_violation(
                    ViolationType.COMMAND_INJECTION,
                    ViolationSeverity.HIGH,
                    f"Command injection detected: {pattern}",
                    {'command': command}
                )
                return {
                    'safe': False,
                    'violation': violation
                }
        
        return {'safe': True}
    
    def check_content_security(self, content: str) -> Dict:
        """
        Check if content contains secrets
        
        Args:
            content: Content to check
            
        Returns:
            Security check result
        """
        for pattern in self.dangerous_patterns['secret_exposure']:
            if pattern in content:
                violation = self._create_violation(
                    ViolationType.SECRET_EXPOSURE,
                    ViolationSeverity.CRITICAL,
                    f"Secret exposure detected: {pattern}",
                    {'content_length': len(content)}
                )
                return {
                    'safe': False,
                    'violation': violation
                }
        
        return {'safe': True}
    
    def block_agent(self, agent_id: str, reason: str) -> Dict:
        """
        Block agent from further operations
        
        Args:
            agent_id: Agent ID
            reason: Reason for blocking
            
        Returns:
            Block result
        """
        self.blocked_agents.add(agent_id)
        
        violation = self._create_violation(
            ViolationType.UNAUTHORIZED_ACCESS,
            ViolationSeverity.CRITICAL,
            f"Agent blocked: {reason}",
            {'agent_id': agent_id}
        )
        
        logger.critical(f"Agent {agent_id} blocked: {reason}")
        
        return {
            'success': True,
            'agent_id': agent_id,
            'blocked': True,
            'reason': reason
        }
    
    def is_agent_blocked(self, agent_id: str) -> bool:
        """Check if agent is blocked"""
        return agent_id in self.blocked_agents
    
    def unblock_agent(self, agent_id: str) -> Dict:
        """Unblock agent"""
        if agent_id in self.blocked_agents:
            self.blocked_agents.remove(agent_id)
            logger.info(f"Agent {agent_id} unblocked")
            return {'success': True, 'agent_id': agent_id}
        
        return {'success': False, 'error': f'Agent {agent_id} not blocked'}
    
    def _create_violation(
        self,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        message: str,
        context: Dict
    ) -> Dict:
        """Create violation record"""
        violation = {
            'timestamp': datetime.now().isoformat(),
            'type': violation_type.value,
            'severity': severity.value,
            'message': message,
            'context': context
        }
        
        self.violations.append(violation)
        
        # Trigger callbacks
        self._trigger_violation_callbacks(violation)
        
        logger.warning(f"[{severity.value.upper()}] {violation_type.value}: {message}")
        
        return violation
    
    def _trigger_violation_callbacks(self, violation: Dict) -> None:
        """Trigger violation callbacks"""
        for callback in self.violation_callbacks:
            try:
                callback(violation)
            except Exception as e:
                logger.error(f"Error in violation callback: {str(e)}")
    
    def on_violation(self, callback: Callable) -> None:
        """
        Register violation callback
        
        Args:
            callback: Callback function
        """
        self.violation_callbacks.append(callback)
    
    def get_violations(
        self,
        violation_type: Optional[ViolationType] = None,
        severity: Optional[ViolationSeverity] = None
    ) -> List[Dict]:
        """Get violations with optional filtering"""
        violations = self.violations
        
        if violation_type:
            violations = [v for v in violations if v['type'] == violation_type.value]
        
        if severity:
            violations = [v for v in violations if v['severity'] == severity.value]
        
        return violations
    
    def get_violation_stats(self) -> Dict:
        """Get violation statistics"""
        total_violations = len(self.violations)
        critical_violations = len([v for v in self.violations if v['severity'] == 'critical'])
        high_violations = len([v for v in self.violations if v['severity'] == 'high'])
        
        violation_types = {}
        for v in self.violations:
            vtype = v['type']
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        return {
            'total_violations': total_violations,
            'critical': critical_violations,
            'high': high_violations,
            'by_type': violation_types,
            'blocked_agents': len(self.blocked_agents)
        }
    
    def get_blocked_agents(self) -> List[str]:
        """Get list of blocked agents"""
        return list(self.blocked_agents)
