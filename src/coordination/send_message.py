"""
SendMessage Coordinator - Inter-agent communication

Handles message routing between agents with:
- Message queue (FIFO delivery)
- Retry logic (exponential backoff)
- Audit trail (logging)
"""

import asyncio
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class SendMessageCoordinator:
    """Coordinates inter-agent communication"""
    
    def __init__(self):
        self.queues = defaultdict(list)  # agent_name -> [messages]
        self.message_log = []
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 1.0,  # seconds
            'backoff_multiplier': 2
        }
        
    async def send_message(self, message: Dict) -> bool:
        """
        Send message to agent queue
        
        Args:
            message: Message with 'to', 'from', 'content'
            
        Returns:
            True if sent successfully
        """
        # Validate message
        if not message.get('to') or not message.get('from') or not message.get('content'):
            logger.error("Invalid message format")
            return False
        
        # Add metadata
        message['id'] = message.get('id', f"msg_{datetime.now().timestamp()}")
        message['timestamp'] = message.get('timestamp', datetime.now().isoformat())
        message['status'] = 'queued'
        
        # Add to queue
        self.queues[message['to']].append(message)
        
        # Log message
        self._log_message(message, 'sent')
        
        logger.info(f"Message sent from {message['from']} to {message['to']}")
        return True
    
    async def receive_message(self, agent_name: str, timeout: float = 5.0) -> Optional[Dict]:
        """
        Receive message from agent queue
        
        Args:
            agent_name: Agent name
            timeout: Timeout in seconds
            
        Returns:
            Message or None if timeout
        """
        start_time = datetime.now().timestamp()
        
        while True:
            queue = self.queues.get(agent_name, [])
            
            if queue:
                message = queue.pop(0)
                self._log_message(message, 'received')
                logger.info(f"Message received by {agent_name}")
                return message
            
            elapsed = datetime.now().timestamp() - start_time
            if elapsed > timeout:
                logger.warning(f"Timeout waiting for message for {agent_name}")
                return None
            
            await asyncio.sleep(0.1)
    
    async def send_with_retry(self, message: Dict, max_retries: Optional[int] = None) -> Dict:
        """
        Send message with retry logic
        
        Args:
            message: Message to send
            max_retries: Max retry attempts
            
        Returns:
            Result dict with success/error
        """
        max_retries = max_retries or self.retry_config['max_retries']
        
        for attempt in range(max_retries + 1):
            try:
                result = await self.send_message(message)
                if result:
                    return {
                        'success': True,
                        'message_id': message.get('id'),
                        'attempt': attempt + 1
                    }
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries:
                    delay = (self.retry_config['retry_delay'] *
                            (self.retry_config['backoff_multiplier'] ** attempt))
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        
        return {
            'success': False,
            'message_id': message.get('id'),
            'error': 'Max retries exceeded'
        }
    
    def get_queue_status(self, agent_name: str) -> Dict:
        """Get queue status for agent"""
        queue = self.queues.get(agent_name, [])
        return {
            'agent': agent_name,
            'message_count': len(queue),
            'messages': [
                {
                    'id': m.get('id'),
                    'from': m.get('from'),
                    'status': m.get('status')
                }
                for m in queue
            ]
        }
    
    def get_message_history(self, from_agent: Optional[str] = None) -> List[Dict]:
        """Get message history with optional filtering"""
        history = self.message_log
        
        if from_agent:
            history = [m for m in history if m.get('from') == from_agent]
        
        return history
    
    def _log_message(self, message: Dict, action: str):
        """Log message to audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message_id': message.get('id'),
            'from': message.get('from'),
            'to': message.get('to'),
            'action': action,
            'status': message.get('status')
        }
        
        self.message_log.append(log_entry)
        logger.debug(f"Message logged: {json.dumps(log_entry)}")
