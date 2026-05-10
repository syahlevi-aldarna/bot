"""
Agent Action Logger - Logs all agent actions and state changes

Responsibilities:
- Log agent spawn/kill events
- Log agent state changes
- Log agent task execution
- Track agent performance metrics
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AgentAction(Enum):
    """Agent action types"""
    SPAWN = "spawn"
    KILL = "kill"
    STATE_CHANGE = "state_change"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    ERROR = "error"


class AgentActionLogger:
    """Logs agent actions and state changes"""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize agent action logger
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.action_history = []
    
    def log_spawn(self, agent_id: str, agent_type: str, task: Dict) -> Dict:
        """Log agent spawn"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.SPAWN.value,
            'agent_id': agent_id,
            'agent_type': agent_type,
            'task': task.get('description', 'unknown')
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Agent spawned: {agent_id} ({agent_type})",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_kill(self, agent_id: str, reason: str) -> Dict:
        """Log agent kill"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.KILL.value,
            'agent_id': agent_id,
            'reason': reason
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Agent killed: {agent_id} ({reason})",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_state_change(
        self,
        agent_id: str,
        old_state: str,
        new_state: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Log agent state change"""
        if metadata is None:
            metadata = {}
        
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.STATE_CHANGE.value,
            'agent_id': agent_id,
            'old_state': old_state,
            'new_state': new_state,
            'metadata': metadata
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Agent state changed: {agent_id} {old_state} → {new_state}",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_task_start(self, agent_id: str, task_id: str, task_desc: str) -> Dict:
        """Log task start"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.TASK_START.value,
            'agent_id': agent_id,
            'task_id': task_id,
            'task_description': task_desc
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Task started: {task_id} by {agent_id}",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_task_complete(
        self,
        agent_id: str,
        task_id: str,
        result: Dict,
        execution_time: float
    ) -> Dict:
        """Log task completion"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.TASK_COMPLETE.value,
            'agent_id': agent_id,
            'task_id': task_id,
            'result': result,
            'execution_time': execution_time
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Task completed: {task_id} by {agent_id} ({execution_time:.2f}s)",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_task_failed(
        self,
        agent_id: str,
        task_id: str,
        error: str,
        execution_time: float
    ) -> Dict:
        """Log task failure"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.TASK_FAILED.value,
            'agent_id': agent_id,
            'task_id': task_id,
            'error': error,
            'execution_time': execution_time
        }
        
        self.action_history.append(action)
        self.logger.error(
            f"Task failed: {task_id} by {agent_id} - {error}",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_message_sent(
        self,
        from_agent: str,
        to_agent: str,
        message_id: str,
        content_size: int
    ) -> Dict:
        """Log message sent"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.MESSAGE_SENT.value,
            'from_agent': from_agent,
            'to_agent': to_agent,
            'message_id': message_id,
            'content_size': content_size
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Message sent: {from_agent} → {to_agent} ({message_id})",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_message_received(
        self,
        agent_id: str,
        from_agent: str,
        message_id: str,
        content_size: int
    ) -> Dict:
        """Log message received"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.MESSAGE_RECEIVED.value,
            'agent_id': agent_id,
            'from_agent': from_agent,
            'message_id': message_id,
            'content_size': content_size
        }
        
        self.action_history.append(action)
        self.logger.info(
            f"Message received: {agent_id} ← {from_agent} ({message_id})",
            extra={'extra_data': action}
        )
        
        return action
    
    def log_error(self, agent_id: str, error: str, context: Optional[Dict] = None) -> Dict:
        """Log agent error"""
        if context is None:
            context = {}
        
        action = {
            'timestamp': datetime.now().isoformat(),
            'action': AgentAction.ERROR.value,
            'agent_id': agent_id,
            'error': error,
            'context': context
        }
        
        self.action_history.append(action)
        self.logger.error(
            f"Agent error: {agent_id} - {error}",
            extra={'extra_data': action}
        )
        
        return action
    
    def get_action_history(self, agent_id: Optional[str] = None) -> list:
        """Get action history with optional filtering"""
        history = self.action_history
        
        if agent_id:
            history = [
                a for a in history
                if a.get('agent_id') == agent_id or a.get('from_agent') == agent_id
            ]
        
        return history
    
    def get_agent_stats(self, agent_id: str) -> Dict:
        """Get statistics for specific agent"""
        agent_actions = [a for a in self.action_history if a.get('agent_id') == agent_id]
        
        task_complete = len([a for a in agent_actions if a['action'] == AgentAction.TASK_COMPLETE.value])
        task_failed = len([a for a in agent_actions if a['action'] == AgentAction.TASK_FAILED.value])
        errors = len([a for a in agent_actions if a['action'] == AgentAction.ERROR.value])
        
        total_execution_time = sum(
            a.get('execution_time', 0)
            for a in agent_actions
            if a['action'] in [AgentAction.TASK_COMPLETE.value, AgentAction.TASK_FAILED.value]
        )
        
        return {
            'agent_id': agent_id,
            'total_actions': len(agent_actions),
            'tasks_completed': task_complete,
            'tasks_failed': task_failed,
            'errors': errors,
            'total_execution_time': total_execution_time,
            'success_rate': task_complete / (task_complete + task_failed) if (task_complete + task_failed) > 0 else 0
        }
