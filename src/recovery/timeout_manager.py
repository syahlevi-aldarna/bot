"""
Timeout Manager - Handles agent timeout and cleanup

Responsibilities:
- Track agent execution time
- Kill agents that exceed timeout
- Notify user of timeout
- Clean up resources
"""

import asyncio
import logging
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TimeoutManager:
    """Manages agent timeouts and cleanup"""
    
    def __init__(self, default_timeout: int = 300):
        """
        Initialize timeout manager
        
        Args:
            default_timeout: Default timeout in seconds (5 minutes)
        """
        self.default_timeout = default_timeout
        self.active_agents = {}  # agent_id -> {start_time, timeout, task}
        self.timeout_callbacks = []
    
    async def start_tracking(
        self,
        agent_id: str,
        task: Dict,
        timeout: Optional[int] = None
    ) -> None:
        """
        Start tracking agent execution time
        
        Args:
            agent_id: Agent ID
            task: Task being executed
            timeout: Custom timeout (uses default if None)
        """
        timeout = timeout or self.default_timeout
        
        self.active_agents[agent_id] = {
            'start_time': datetime.now(),
            'timeout': timeout,
            'task': task,
            'status': 'running'
        }
        
        logger.info(f"Started tracking agent {agent_id} (timeout: {timeout}s)")
        
        # Start timeout monitor
        asyncio.create_task(self._monitor_timeout(agent_id))
    
    async def stop_tracking(self, agent_id: str) -> Dict:
        """
        Stop tracking agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Execution stats
        """
        if agent_id not in self.active_agents:
            return {'success': False, 'error': f'Agent {agent_id} not tracked'}
        
        agent_info = self.active_agents[agent_id]
        elapsed = (datetime.now() - agent_info['start_time']).total_seconds()
        
        del self.active_agents[agent_id]
        
        logger.info(f"Stopped tracking agent {agent_id} (elapsed: {elapsed}s)")
        
        return {
            'success': True,
            'agent_id': agent_id,
            'elapsed_time': elapsed,
            'timeout': agent_info['timeout'],
            'status': 'completed'
        }
    
    async def _monitor_timeout(self, agent_id: str) -> None:
        """
        Monitor agent timeout
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self.active_agents:
            return
        
        agent_info = self.active_agents[agent_id]
        timeout = agent_info['timeout']
        
        # Wait for timeout duration
        await asyncio.sleep(timeout)
        
        # Check if agent is still running
        if agent_id in self.active_agents:
            logger.warning(f"Agent {agent_id} exceeded timeout ({timeout}s)")
            
            # Mark as timed out
            agent_info['status'] = 'timeout'
            
            # Call timeout callbacks
            await self._trigger_timeout_callbacks(agent_id)
            
            # Clean up
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
    
    async def _trigger_timeout_callbacks(self, agent_id: str) -> None:
        """Trigger timeout callbacks"""
        for callback in self.timeout_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(agent_id)
                else:
                    callback(agent_id)
            except Exception as e:
                logger.error(f"Error in timeout callback: {str(e)}")
    
    def on_timeout(self, callback: Callable) -> None:
        """
        Register timeout callback
        
        Args:
            callback: Callback function (can be async)
        """
        self.timeout_callbacks.append(callback)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get agent status"""
        if agent_id not in self.active_agents:
            return None
        
        agent_info = self.active_agents[agent_id]
        elapsed = (datetime.now() - agent_info['start_time']).total_seconds()
        
        return {
            'agent_id': agent_id,
            'status': agent_info['status'],
            'elapsed_time': elapsed,
            'timeout': agent_info['timeout'],
            'time_remaining': max(0, agent_info['timeout'] - elapsed)
        }
    
    def get_all_agents(self) -> Dict[str, Dict]:
        """Get all tracked agents"""
        result = {}
        
        for agent_id, info in self.active_agents.items():
            elapsed = (datetime.now() - info['start_time']).total_seconds()
            result[agent_id] = {
                'status': info['status'],
                'elapsed_time': elapsed,
                'timeout': info['timeout'],
                'time_remaining': max(0, info['timeout'] - elapsed)
            }
        
        return result
    
    async def kill_agent(self, agent_id: str, mcp_client) -> Dict:
        """
        Kill agent and clean up
        
        Args:
            agent_id: Agent ID
            mcp_client: MCP client for killing agent
            
        Returns:
            Kill result
        """
        if agent_id not in self.active_agents:
            return {'success': False, 'error': f'Agent {agent_id} not found'}
        
        try:
            # Kill via MCP
            await mcp_client.kill_agent(agent_id)
            
            # Stop tracking
            await self.stop_tracking(agent_id)
            
            logger.info(f"Agent {agent_id} killed successfully")
            
            return {
                'success': True,
                'agent_id': agent_id,
                'message': 'Agent killed'
            }
        except Exception as e:
            logger.error(f"Error killing agent {agent_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
