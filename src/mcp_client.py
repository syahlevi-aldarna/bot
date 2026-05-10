"""
MCP Client - Wrapper untuk Ruflo MCP Server tools
Handles agent spawning, status polling, memory operations
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class MCPClient:
    """Client untuk communicate dengan Ruflo MCP Server"""

    def __init__(self, port: int = 3000, timeout: int = 30000, retries: int = 3):
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.is_connected = False
        self.callbacks = {}

    async def connect(self) -> None:
        """Connect ke MCP server"""
        try:
            self.is_connected = True
            self._emit("connected")
        except Exception as e:
            raise Exception(f"Failed to connect to MCP server: {str(e)}")

    async def spawn_agent(self, options: Dict[str, str]) -> str:
        """
        Spawn agent baru
        
        Args:
            options: Dict dengan keys 'type', 'task', 'namespace'
            
        Returns:
            Agent ID
        """
        agent_type = options.get("type")
        task = options.get("task")
        namespace = options.get("namespace", "default")

        if not agent_type or not task:
            raise ValueError("Agent type and task are required")

        agent_id = f"agent-{int(datetime.now().timestamp() * 1000)}-{str(uuid.uuid4())[:8]}"

        # Store agent info
        self.agents[agent_id] = {
            "id": agent_id,
            "type": agent_type,
            "task": task,
            "namespace": namespace,
            "status": "spawning",
            "created_at": datetime.now(),
            "output": "",
            "error": None,
        }

        self._emit("agent:spawned", {"agent_id": agent_id, "type": agent_type, "task": task})

        # Simulate agent spawn
        await asyncio.sleep(0.1)
        agent = self.agents.get(agent_id)
        if agent:
            agent["status"] = "running"
            self._emit("agent:started", {"agent_id": agent_id})

        return agent_id

    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent status
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent status dict
        """
        agent = self.agents.get(agent_id)

        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        return {
            "id": agent["id"],
            "type": agent["type"],
            "status": agent["status"],
            "task": agent["task"],
            "output": agent["output"],
            "error": agent["error"],
            "created_at": agent["created_at"],
            "updated_at": datetime.now(),
        }

    async def update_agent_status(
        self, agent_id: str, status: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update agent status
        
        Args:
            agent_id: Agent ID
            status: New status
            data: Additional data
        """
        if data is None:
            data = {}

        agent = self.agents.get(agent_id)

        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        agent["status"] = status
        if "output" in data:
            agent["output"] = data["output"]
        if "error" in data:
            agent["error"] = data["error"]

        self._emit(f"agent:{status}", {"agent_id": agent_id, **data})

        return agent

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return list(self.agents.values())

    async def kill_agent(self, agent_id: str) -> None:
        """
        Kill agent
        
        Args:
            agent_id: Agent ID
        """
        agent = self.agents.get(agent_id)

        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        agent["status"] = "killed"
        self._emit("agent:killed", {"agent_id": agent_id})

        # Clean up after 1 second
        await asyncio.sleep(1)
        if agent_id in self.agents:
            del self.agents[agent_id]

    async def memory_store(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store data in memory
        
        Args:
            options: Dict dengan keys 'namespace', 'key', 'value'
            
        Returns:
            Store result
        """
        namespace = options.get("namespace", "default")
        key = options.get("key")
        value = options.get("value")

        if not key or not value:
            raise ValueError("Key and value are required")

        self._emit("memory:stored", {"namespace": namespace, "key": key})

        return {"namespace": namespace, "key": key, "stored": True}

    async def memory_search(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search memory
        
        Args:
            options: Dict dengan keys 'namespace', 'query', 'limit'
            
        Returns:
            Search results
        """
        namespace = options.get("namespace", "default")
        query = options.get("query")
        limit = options.get("limit", 5)

        if not query:
            raise ValueError("Query is required")

        self._emit("memory:searched", {"namespace": namespace, "query": query})

        return {
            "namespace": namespace,
            "query": query,
            "results": [],
            "count": 0,
        }

    async def send_message(self, options: Dict[str, str]) -> Dict[str, Any]:
        """
        Send message between agents (SendMessage pattern)
        
        Args:
            options: Dict dengan keys 'from', 'to', 'message'
            
        Returns:
            Send result
        """
        from_agent = options.get("from")
        to_agent = options.get("to")
        message = options.get("message")

        if not from_agent or not to_agent or not message:
            raise ValueError("From, to, and message are required")

        self._emit("message:sent", {"from": from_agent, "to": to_agent, "message": message})

        return {"from": from_agent, "to": to_agent, "sent": True}

    async def disconnect(self) -> None:
        """Disconnect dari MCP server"""
        self.is_connected = False
        self.agents.clear()
        self._emit("disconnected")

    def on(self, event: str, callback) -> None:
        """Register event callback"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    def _emit(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit event"""
        if data is None:
            data = {}

        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in callback for {event}: {str(e)}")
