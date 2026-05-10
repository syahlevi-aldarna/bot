"""
Security Event Logger - Logs all security-related events

Responsibilities:
- Log security violations
- Log access control events
- Log authentication events
- Track security statistics
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SecurityEventType(Enum):
    """Security event types"""
    VIOLATION = "violation"
    BLOCKED = "blocked"
    ALLOWED = "allowed"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    AUDIT = "audit"


class SecuritySeverity(Enum):
    """Security event severity"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class SecurityEventLogger:
    """Logs security-related events"""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize security event logger
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.event_history = []
    
    def log_violation(
        self,
        violation_type: str,
        agent_id: str,
        details: str,
        severity: SecuritySeverity = SecuritySeverity.CRITICAL
    ) -> Dict:
        """Log security violation"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': SecurityEventType.VIOLATION.value,
            'violation_type': violation_type,
            'agent_id': agent_id,
            'details': details,
            'severity': severity.value
        }
        
        self.event_history.append(event)
        
        log_method = self.logger.critical if severity == SecuritySeverity.CRITICAL else self.logger.warning
        log_method(
            f"Security violation: {violation_type} by {agent_id} - {details}",
            extra={'extra_data': event}
        )
        
        return event
    
    def log_blocked(
        self,
        agent_id: str,
        action: str,
        reason: str,
        severity: SecuritySeverity = SecuritySeverity.WARNING
    ) -> Dict:
        """Log blocked action"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': SecurityEventType.BLOCKED.value,
            'agent_id': agent_id,
            'action': action,
            'reason': reason,
            'severity': severity.value
        }
        
        self.event_history.append(event)
        self.logger.warning(
            f"Action blocked: {agent_id} attempted {action} - {reason}",
            extra={'extra_data': event}
        )
        
        return event
    
    def log_allowed(
        self,
        agent_id: str,
        action: str,
        resource: str
    ) -> Dict:
        """Log allowed action"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': SecurityEventType.ALLOWED.value,
            'agent_id': agent_id,
            'action': action,
            'resource': resource,
            'severity': SecuritySeverity.INFO.value
        }
        
        self.event_history.append(event)
        self.logger.info(
            f"Action allowed: {agent_id} {action} {resource}",
            extra={'extra_data': event}
        )
        
        return event
    
    def log_authentication(
        self,
        agent_id: str,
        success: bool,
        method: str,
        details: Optional[str] = None
    ) -> Dict:
        """Log authentication event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': SecurityEventType.AUTHENTICATION.value,
            'agent_id': agent_id,
            'success': success,
            'method': method,
            'details': details or ''
        }
        
        self.event_history.append(event)
        
        status = 'successful' if success else 'failed'
        log_method = self.logger.info if success else self.logger.warning
        log_method(
            f"Authentication {status}: {agent_id} via {method}",
            extra={'extra_data': event}
        )
        
        return event
    
    def log_authorization(
        self,
        agent_id: str,
        resource: str,
        permission: str,
        granted: bool
    ) -> Dict:
        """Log authorization event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': SecurityEventType.AUTHORIZATION.value,
            'agent_id': agent_id,
            'resource': resource,
            'permission': permission,
            'granted': granted
        }
        
        self.event_history.append(event)
        
        status = 'granted' if granted else 'denied'
        log_method = self.logger.info if granted else self.logger.warning
        log_method(
            f"Authorization {status}: {agent_id} {permission} on {resource}",
            extra={'extra_data': event}
        )
        
        return event
    
    def log_audit(
        self,
        agent_id: str,
        action: str,
        resource: str,
        result: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Log audit event"""
        if metadata is None:
            metadata = {}
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': SecurityEventType.AUDIT.value,
            'agent_id': agent_id,
            'action': action,
            'resource': resource,
            'result': result,
            'metadata': metadata
        }
        
        self.event_history.append(event)
        self.logger.info(
            f"Audit: {agent_id} {action} {resource} - {result}",
            extra={'extra_data': event}
        )
        
        return event
    
    def get_event_history(
        self,
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> list:
        """Get event history with optional filtering"""
        history = self.event_history
        
        if event_type:
            history = [e for e in history if e['event_type'] == event_type]
        
        if agent_id:
            history = [e for e in history if e.get('agent_id') == agent_id]
        
        if severity:
            history = [e for e in history if e.get('severity') == severity]
        
        return history
    
    def get_violations(self) -> list:
        """Get all violations"""
        return self.get_event_history(event_type=SecurityEventType.VIOLATION.value)
    
    def get_critical_events(self) -> list:
        """Get all critical events"""
        return self.get_event_history(severity=SecuritySeverity.CRITICAL.value)
    
    def get_agent_events(self, agent_id: str) -> list:
        """Get all events for specific agent"""
        return self.get_event_history(agent_id=agent_id)
    
    def get_stats(self) -> Dict:
        """Get security event statistics"""
        total_events = len(self.event_history)
        
        violations = len(self.get_violations())
        blocked_actions = len(self.get_event_history(event_type=SecurityEventType.BLOCKED.value))
        critical_events = len(self.get_critical_events())
        
        # Get unique agents with violations
        agents_with_violations = set()
        for v in self.get_violations():
            agents_with_violations.add(v.get('agent_id'))
        
        return {
            'total_events': total_events,
            'violations': violations,
            'blocked_actions': blocked_actions,
            'critical_events': critical_events,
            'agents_with_violations': len(agents_with_violations),
            'violation_rate': violations / total_events if total_events > 0 else 0
        }
