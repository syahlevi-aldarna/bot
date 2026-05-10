"""
Coder Agent - Writes code based on task description

Responsibilities:
- Receive task from Telegram via MCP
- Write code to solve the task
- Send code to reviewer agent
- Receive feedback and iterate
"""

import asyncio
import json
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CoderAgent:
    """Agent that writes code based on task description"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.name = 'coder'
        self.agent_id = None
        
    async def spawn(self) -> str:
        """Spawn coder agent via MCP"""
        logger.info("Spawning coder agent...")
        self.agent_id = await self.mcp_client.spawn_agent(
            agent_type='coder',
            name='coder'
        )
        logger.info(f"Coder agent spawned: {self.agent_id}")
        return self.agent_id
    
    async def write_code(self, task: Dict) -> Dict:
        """
        Write code based on task description
        
        Args:
            task: Task description with requirements
            
        Returns:
            Code changes with files and diff
        """
        logger.info(f"Writing code for task: {task.get('description', 'unknown')}")
        
        # Simulate code writing
        code_changes = {
            'files_changed': ['src/solution.js'],
            'code_diff': 'function solve() { /* implementation */ }',
            'task_description': task.get('description', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Code written: {len(code_changes['code_diff'])} chars")
        return code_changes
    
    async def send_to_reviewer(self, code_changes: Dict) -> bool:
        """Send code to reviewer agent"""
        logger.info("Sending code to reviewer...")
        
        message = {
            'to': 'reviewer',
            'from': 'coder',
            'content': code_changes
        }
        
        # Send via MCP
        result = await self.mcp_client.send_message(message)
        logger.info(f"Code sent to reviewer: {result}")
        return result
    
    async def run(self, task: Dict) -> Dict:
        """Main execution flow"""
        try:
            # Spawn agent
            await self.spawn()
            
            # Write code
            code_changes = await self.write_code(task)
            
            # Send to reviewer
            await self.send_to_reviewer(code_changes)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'code_changes': code_changes
            }
        except Exception as e:
            logger.error(f"Error in coder agent: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
