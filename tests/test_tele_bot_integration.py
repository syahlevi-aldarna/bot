"""
Tests untuk Telegram Bot + MCP Integration
"""

import asyncio
import pytest
from src.mcp_client import MCPClient


@pytest.mark.asyncio
async def test_mcp_client_spawn_agent():
    """Test spawning agent via MCP client"""
    client = MCPClient(port=3000)
    await client.connect()

    agent_id = await client.spawn_agent({
        "type": "coder",
        "task": "Create email validator function",
        "namespace": "telegram-tasks"
    })

    assert agent_id is not None
    assert agent_id.startswith("agent-")

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_get_agent_status():
    """Test getting agent status"""
    client = MCPClient(port=3000)
    await client.connect()

    agent_id = await client.spawn_agent({
        "type": "coder",
        "task": "Test task",
        "namespace": "test"
    })

    status = await client.get_agent_status(agent_id)

    assert status["id"] == agent_id
    assert status["type"] == "coder"
    assert status["task"] == "Test task"
    assert status["status"] in ["spawning", "running"]

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_update_agent_status():
    """Test updating agent status"""
    client = MCPClient(port=3000)
    await client.connect()

    agent_id = await client.spawn_agent({
        "type": "coder",
        "task": "Test task",
    })

    await client.update_agent_status(agent_id, "running", {
        "output": "Agent is working..."
    })

    status = await client.get_agent_status(agent_id)
    assert status["status"] == "running"
    assert status["output"] == "Agent is working..."

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_memory_store():
    """Test storing data in memory"""
    client = MCPClient(port=3000)
    await client.connect()

    result = await client.memory_store({
        "namespace": "test",
        "key": "email-validator",
        "value": {"pattern": "^[^@]+@[^@]+$"}
    })

    assert result["stored"] is True
    assert result["key"] == "email-validator"

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_memory_search():
    """Test searching memory"""
    client = MCPClient(port=3000)
    await client.connect()

    result = await client.memory_search({
        "namespace": "test",
        "query": "email validator",
        "limit": 5
    })

    assert result["query"] == "email validator"
    assert isinstance(result["results"], list)

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_send_message():
    """Test SendMessage pattern"""
    client = MCPClient(port=3000)
    await client.connect()

    result = await client.send_message({
        "from": "agent-1",
        "to": "reviewer",
        "message": "Here is the code I wrote"
    })

    assert result["sent"] is True
    assert result["from"] == "agent-1"
    assert result["to"] == "reviewer"

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_list_agents():
    """Test listing agents"""
    client = MCPClient(port=3000)
    await client.connect()

    agent1_id = await client.spawn_agent({
        "type": "coder",
        "task": "Task 1"
    })

    agent2_id = await client.spawn_agent({
        "type": "reviewer",
        "task": "Task 2"
    })

    agents = await client.list_agents()

    assert len(agents) >= 2
    agent_ids = [a["id"] for a in agents]
    assert agent1_id in agent_ids
    assert agent2_id in agent_ids

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_kill_agent():
    """Test killing agent"""
    client = MCPClient(port=3000)
    await client.connect()

    agent_id = await client.spawn_agent({
        "type": "coder",
        "task": "Test task"
    })

    await client.kill_agent(agent_id)

    # Wait for cleanup
    await asyncio.sleep(1.5)

    agents = await client.list_agents()
    agent_ids = [a["id"] for a in agents]
    assert agent_id not in agent_ids

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_error_handling():
    """Test error handling"""
    client = MCPClient(port=3000)
    await client.connect()

    # Test missing type
    with pytest.raises(ValueError):
        await client.spawn_agent({"task": "Some task"})

    # Test missing task
    with pytest.raises(ValueError):
        await client.spawn_agent({"type": "coder"})

    # Test non-existent agent
    with pytest.raises(ValueError):
        await client.get_agent_status("non-existent")

    await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_client_events():
    """Test event callbacks"""
    client = MCPClient(port=3000)
    await client.connect()

    events_received = []

    def on_spawned(data):
        events_received.append(("spawned", data))

    def on_started(data):
        events_received.append(("started", data))

    client.on("agent:spawned", on_spawned)
    client.on("agent:started", on_started)

    agent_id = await client.spawn_agent({
        "type": "coder",
        "task": "Test task"
    })

    # Wait for events
    await asyncio.sleep(0.2)

    assert len(events_received) >= 1
    assert events_received[0][0] == "spawned"

    await client.disconnect()
