"""
Tests for agent coordination pipeline

Tests:
- Agent spawning and communication
- Message sending and receiving
- Retry logic with exponential backoff
- Full pipeline: coder → reviewer → tester
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Mock imports
class MockMCPClient:
    async def spawn_agent(self, agent_type, name):
        return f"agent_{agent_type}_{name}"
    
    async def send_message(self, message):
        return True


@pytest.mark.asyncio
async def test_coder_agent_spawn():
    """Test coder agent spawning"""
    from src.agents.coder_agent import CoderAgent
    
    mcp_client = MockMCPClient()
    coder = CoderAgent(mcp_client)
    
    agent_id = await coder.spawn()
    assert agent_id is not None
    assert 'coder' in agent_id


@pytest.mark.asyncio
async def test_coder_agent_write_code():
    """Test coder agent writing code"""
    from src.agents.coder_agent import CoderAgent
    
    mcp_client = MockMCPClient()
    coder = CoderAgent(mcp_client)
    
    task = {'description': 'Create email validator'}
    code_changes = await coder.write_code(task)
    
    assert code_changes['files_changed']
    assert code_changes['code_diff']
    assert code_changes['task_description'] == task['description']


@pytest.mark.asyncio
async def test_reviewer_agent_spawn():
    """Test reviewer agent spawning"""
    from src.agents.reviewer_agent import ReviewerAgent
    
    mcp_client = MockMCPClient()
    reviewer = ReviewerAgent(mcp_client)
    
    agent_id = await reviewer.spawn()
    assert agent_id is not None
    assert 'reviewer' in agent_id


@pytest.mark.asyncio
async def test_reviewer_agent_review_code():
    """Test reviewer agent reviewing code"""
    from src.agents.reviewer_agent import ReviewerAgent
    
    mcp_client = MockMCPClient()
    reviewer = ReviewerAgent(mcp_client)
    
    code_changes = {
        'files_changed': ['src/app.js'],
        'code_diff': 'function test() { console.log("test"); }'
    }
    
    review_result = await reviewer.review_code(code_changes)
    
    assert review_result['review_status'] in ['approved', 'needs_changes']
    assert 'issues' in review_result
    assert 'approved_files' in review_result


@pytest.mark.asyncio
async def test_tester_agent_spawn():
    """Test tester agent spawning"""
    from src.agents.tester_agent import TesterAgent
    
    mcp_client = MockMCPClient()
    tester = TesterAgent(mcp_client)
    
    agent_id = await tester.spawn()
    assert agent_id is not None
    assert 'tester' in agent_id


@pytest.mark.asyncio
async def test_tester_agent_write_tests():
    """Test tester agent writing tests"""
    from src.agents.tester_agent import TesterAgent
    
    mcp_client = MockMCPClient()
    tester = TesterAgent(mcp_client)
    
    review_result = {'review_status': 'approved'}
    test_file = await tester.write_tests(review_result)
    
    assert test_file is not None
    assert '.test.' in test_file or '_test' in test_file


@pytest.mark.asyncio
async def test_tester_agent_run_tests():
    """Test tester agent running tests"""
    from src.agents.tester_agent import TesterAgent
    
    mcp_client = MockMCPClient()
    tester = TesterAgent(mcp_client)
    
    test_results = await tester.run_tests('tests/solution.test.js')
    
    assert test_results['status'] in ['passed', 'failed']
    assert 'total_tests' in test_results
    assert 'passed' in test_results
    assert 'failed' in test_results


@pytest.mark.asyncio
async def test_send_message_coordinator_send():
    """Test SendMessage coordinator sending"""
    from src.coordination.send_message import SendMessageCoordinator
    
    coordinator = SendMessageCoordinator()
    
    message = {
        'to': 'reviewer',
        'from': 'coder',
        'content': {'code': 'test'}
    }
    
    result = await coordinator.send_message(message)
    assert result is True


@pytest.mark.asyncio
async def test_send_message_coordinator_receive():
    """Test SendMessage coordinator receiving"""
    from src.coordination.send_message import SendMessageCoordinator
    
    coordinator = SendMessageCoordinator()
    
    message = {
        'to': 'reviewer',
        'from': 'coder',
        'content': {'code': 'test'}
    }
    
    await coordinator.send_message(message)
    received = await coordinator.receive_message('reviewer', timeout=1.0)
    
    assert received is not None
    assert received['from'] == 'coder'


@pytest.mark.asyncio
async def test_send_message_coordinator_retry():
    """Test SendMessage coordinator retry logic"""
    from src.coordination.send_message import SendMessageCoordinator
    
    coordinator = SendMessageCoordinator()
    
    message = {
        'to': 'reviewer',
        'from': 'coder',
        'content': {'code': 'test'}
    }
    
    result = await coordinator.send_with_retry(message, max_retries=2)
    
    assert result['success'] is True
    assert result['attempt'] >= 1


@pytest.mark.asyncio
async def test_send_message_coordinator_queue_status():
    """Test SendMessage coordinator queue status"""
    from src.coordination.send_message import SendMessageCoordinator
    
    coordinator = SendMessageCoordinator()
    
    message = {
        'to': 'reviewer',
        'from': 'coder',
        'content': {'code': 'test'}
    }
    
    await coordinator.send_message(message)
    status = coordinator.get_queue_status('reviewer')
    
    assert status['agent'] == 'reviewer'
    assert status['message_count'] == 1


@pytest.mark.asyncio
async def test_full_pipeline_coder_to_reviewer_to_tester():
    """Test full pipeline: coder → reviewer → tester"""
    from src.agents.coder_agent import CoderAgent
    from src.agents.reviewer_agent import ReviewerAgent
    from src.agents.tester_agent import TesterAgent
    from src.coordination.send_message import SendMessageCoordinator
    
    mcp_client = MockMCPClient()
    coordinator = SendMessageCoordinator()
    
    # Coder writes code
    coder = CoderAgent(mcp_client)
    task = {'description': 'Create email validator'}
    code_changes = await coder.write_code(task)
    
    # Send to reviewer
    message = {
        'to': 'reviewer',
        'from': 'coder',
        'content': code_changes
    }
    await coordinator.send_message(message)
    
    # Reviewer receives and reviews
    reviewer_msg = await coordinator.receive_message('reviewer', timeout=1.0)
    assert reviewer_msg is not None
    
    reviewer = ReviewerAgent(mcp_client)
    review_result = await reviewer.review_code(reviewer_msg['content'])
    
    # Send to tester
    message = {
        'to': 'tester',
        'from': 'reviewer',
        'content': review_result
    }
    await coordinator.send_message(message)
    
    # Tester receives and tests
    tester_msg = await coordinator.receive_message('tester', timeout=1.0)
    assert tester_msg is not None
    
    tester = TesterAgent(mcp_client)
    test_results = await tester.run_tests('tests/solution.test.js')
    
    assert test_results['status'] in ['passed', 'failed']


@pytest.mark.asyncio
async def test_message_history_tracking():
    """Test message history tracking"""
    from src.coordination.send_message import SendMessageCoordinator
    
    coordinator = SendMessageCoordinator()
    
    # Send multiple messages
    msg1 = {'to': 'reviewer', 'from': 'coder', 'content': {'id': 1}}
    msg2 = {'to': 'tester', 'from': 'reviewer', 'content': {'id': 2}}
    
    await coordinator.send_message(msg1)
    await coordinator.send_message(msg2)
    
    # Get history
    history = coordinator.get_message_history()
    assert len(history) >= 2
    
    # Filter by sender
    coder_history = coordinator.get_message_history(from_agent='coder')
    assert any(m['from'] == 'coder' for m in coder_history)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
