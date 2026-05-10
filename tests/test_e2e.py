"""
End-to-End Tests - Full system integration tests

Tests:
- Simple coding task
- Code review workflow
- Test generation and execution
- Memory learning from past tasks
- Error recovery scenarios
- Security validations
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime

from src.e2e.e2e_test_coordinator import E2ETestCoordinator, TestStatus
from src.error_handler import ErrorHandler, ErrorType, ErrorSeverity
from src.recovery.timeout_manager import TimeoutManager
from src.recovery.rollback_manager import RollbackManager
from src.recovery.security_violation_manager import SecurityViolationManager
from src.memory.agent_db import AgentDB
from src.memory.task_embedder import TaskEmbedder
from src.memory.sona_learner import SONALearner


# ============================================================================
# MOCK OBJECTS
# ============================================================================

class MockMCPClient:
    """Mock MCP client for testing"""
    
    async def spawn_agent(self, options):
        return f"agent_{options.get('type', 'unknown')}_test"
    
    async def get_agent_status(self, agent_id):
        return {'status': 'running', 'agent_id': agent_id}
    
    async def kill_agent(self, agent_id):
        return True


class MockFileExecutor:
    """Mock file executor for testing"""
    
    def write_file(self, path, content):
        return {'success': True, 'path': path, 'size': len(content)}
    
    def read_file(self, path):
        return {'success': True, 'content': 'test content'}


class MockBashExecutor:
    """Mock bash executor for testing"""
    
    async def execute(self, command, cwd=None):
        return {'success': True, 'command': command, 'output': 'test output'}


# ============================================================================
# E2E TEST COORDINATOR TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_e2e_coordinator_simple_coding_task():
    """Test simple coding task"""
    coordinator = E2ETestCoordinator()
    mcp_client = MockMCPClient()
    file_executor = MockFileExecutor()
    
    result = await coordinator.run_simple_coding_task(
        mcp_client,
        file_executor,
        "Create email validator"
    )
    
    assert result['status'] == TestStatus.PASSED.value
    assert result['test_name'] == 'simple_coding_task'
    assert 'elapsed_time' in result
    assert result['details']['code_file'] == 'src/email_validator.py'


@pytest.mark.asyncio
async def test_e2e_coordinator_code_review_workflow():
    """Test code review workflow"""
    coordinator = E2ETestCoordinator()
    mcp_client = MockMCPClient()
    file_executor = MockFileExecutor()
    
    result = await coordinator.run_code_review_workflow(
        mcp_client,
        file_executor
    )
    
    assert result['status'] == TestStatus.PASSED.value
    assert result['test_name'] == 'code_review_workflow'
    assert result['details']['issues_found'] == 2


@pytest.mark.asyncio
async def test_e2e_coordinator_test_generation():
    """Test test generation"""
    coordinator = E2ETestCoordinator()
    mcp_client = MockMCPClient()
    bash_executor = MockBashExecutor()
    
    result = await coordinator.run_test_generation(
        mcp_client,
        bash_executor
    )
    
    assert result['status'] == TestStatus.PASSED.value
    assert result['test_name'] == 'test_generation'
    assert result['details']['tests_generated'] == 3


@pytest.mark.asyncio
async def test_e2e_coordinator_memory_learning():
    """Test memory learning"""
    coordinator = E2ETestCoordinator()
    
    agent_db = AgentDB()
    task_embedder = TaskEmbedder()
    sona_learner = SONALearner()
    
    result = await coordinator.run_memory_learning_test(
        agent_db,
        task_embedder,
        sona_learner
    )
    
    assert result['status'] == TestStatus.PASSED.value
    assert result['test_name'] == 'memory_learning'
    assert result['details']['tasks_stored'] == 1


@pytest.mark.asyncio
async def test_e2e_coordinator_error_recovery():
    """Test error recovery"""
    coordinator = E2ETestCoordinator()
    
    error_handler = ErrorHandler()
    timeout_manager = TimeoutManager()
    rollback_manager = RollbackManager()
    mcp_client = MockMCPClient()
    
    result = await coordinator.run_error_recovery_test(
        error_handler,
        timeout_manager,
        rollback_manager,
        mcp_client
    )
    
    assert result['status'] == TestStatus.PASSED.value
    assert result['test_name'] == 'error_recovery'


@pytest.mark.asyncio
async def test_e2e_coordinator_security_validation():
    """Test security validation"""
    coordinator = E2ETestCoordinator()
    security_manager = SecurityViolationManager()
    
    result = await coordinator.run_security_validation_test(
        security_manager
    )
    
    assert result['status'] == TestStatus.PASSED.value
    assert result['test_name'] == 'security_validation'
    assert result['details']['path_traversal_tests'] == 1


# ============================================================================
# TEST SUMMARY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_e2e_coordinator_record_results():
    """Test recording test results"""
    coordinator = E2ETestCoordinator()
    
    result1 = {
        'test_name': 'test_1',
        'status': TestStatus.PASSED.value,
        'elapsed_time': 1.5
    }
    
    result2 = {
        'test_name': 'test_2',
        'status': TestStatus.PASSED.value,
        'elapsed_time': 2.0
    }
    
    coordinator.record_test_result(result1)
    coordinator.record_test_result(result2)
    
    results = coordinator.get_test_results()
    assert len(results) == 2


@pytest.mark.asyncio
async def test_e2e_coordinator_test_summary():
    """Test test summary"""
    coordinator = E2ETestCoordinator()
    
    coordinator.record_test_result({
        'test_name': 'test_1',
        'status': TestStatus.PASSED.value,
        'elapsed_time': 1.0
    })
    
    coordinator.record_test_result({
        'test_name': 'test_2',
        'status': TestStatus.PASSED.value,
        'elapsed_time': 2.0
    })
    
    coordinator.record_test_result({
        'test_name': 'test_3',
        'status': TestStatus.FAILED.value,
        'elapsed_time': 0.5
    })
    
    summary = coordinator.get_test_summary()
    
    assert summary['total_tests'] == 3
    assert summary['passed'] == 2
    assert summary['failed'] == 1
    assert summary['pass_rate'] == 2/3
    assert summary['total_time'] == 3.5


# ============================================================================
# CORRECTNESS PROPERTY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_property_agent_isolation():
    """Property: Each agent operates independently"""
    coordinator = E2ETestCoordinator()
    mcp_client = MockMCPClient()
    
    # Spawn multiple agents
    agent1 = await mcp_client.spawn_agent({'type': 'coder'})
    agent2 = await mcp_client.spawn_agent({'type': 'reviewer'})
    agent3 = await mcp_client.spawn_agent({'type': 'tester'})
    
    # Verify all agents are independent
    status1 = await mcp_client.get_agent_status(agent1)
    status2 = await mcp_client.get_agent_status(agent2)
    status3 = await mcp_client.get_agent_status(agent3)
    
    assert status1['agent_id'] != status2['agent_id']
    assert status2['agent_id'] != status3['agent_id']
    assert status1['status'] == 'running'
    assert status2['status'] == 'running'
    assert status3['status'] == 'running'


@pytest.mark.asyncio
async def test_property_memory_consistency():
    """Property: Stored tasks can be retrieved with same content"""
    agent_db = AgentDB()
    task_embedder = TaskEmbedder()
    
    # Store task
    task_data = {
        'description': 'Create validator',
        'solution': 'regex pattern',
        'success': True
    }
    
    embedding = task_embedder.embed_task(task_data['description'])
    agent_db.store_task('task_1', task_data, embedding)
    
    # Retrieve task
    retrieved = agent_db.retrieve_task('task_1')
    
    assert retrieved is not None
    assert retrieved['description'] == task_data['description']
    assert retrieved['solution'] == task_data['solution']


@pytest.mark.asyncio
async def test_property_code_safety():
    """Property: No file operations outside project directory"""
    security_manager = SecurityViolationManager()
    
    # Test various path traversal attempts
    dangerous_paths = [
        '../../../etc/passwd',
        '../../sensitive_file',
        '/etc/passwd',
        '~/private_key'
    ]
    
    for path in dangerous_paths:
        result = security_manager.check_path_security(path)
        assert result['safe'] is False, f"Path {path} should be blocked"


@pytest.mark.asyncio
async def test_property_command_safety():
    """Property: Only whitelisted bash commands can execute"""
    security_manager = SecurityViolationManager()
    
    # Test dangerous commands
    dangerous_commands = [
        'rm -rf /',
        'dd if=/dev/zero of=/dev/sda',
        'fork()',
        ':(){ :|:& };:'
    ]
    
    for cmd in dangerous_commands:
        result = security_manager.check_command_security(cmd)
        assert result['safe'] is False, f"Command {cmd} should be blocked"


@pytest.mark.asyncio
async def test_property_secret_protection():
    """Property: .env secrets never appear in logs"""
    security_manager = SecurityViolationManager()
    
    # Test secret patterns
    secrets = [
        'API_KEY=sk_live_123456',
        'PASSWORD=secret123',
        'TOKEN=eyJhbGc...',
        '.env file content'
    ]
    
    for secret in secrets:
        result = security_manager.check_content_security(secret)
        assert result['safe'] is False, f"Secret pattern should be detected"


@pytest.mark.asyncio
async def test_property_timeout_enforcement():
    """Property: Agents timeout after 5 minutes"""
    timeout_manager = TimeoutManager(default_timeout=300)
    
    # Start tracking agent
    await timeout_manager.start_tracking('agent_123', {'task': 'test'})
    
    # Get status
    status = timeout_manager.get_agent_status('agent_123')
    
    assert status is not None
    assert status['timeout'] == 300
    assert status['time_remaining'] <= 300


@pytest.mark.asyncio
async def test_property_learning_effectiveness():
    """Property: Agent retrieves similar past solutions"""
    agent_db = AgentDB()
    task_embedder = TaskEmbedder()
    
    # Store similar tasks
    task1 = {
        'id': 'task_1',
        'description': 'Create email validator',
        'solution': 'regex'
    }
    
    task2 = {
        'id': 'task_2',
        'description': 'Create phone validator',
        'solution': 'regex'
    }
    
    emb1 = task_embedder.embed_task(task1['description'])
    emb2 = task_embedder.embed_task(task2['description'])
    
    agent_db.store_task('task_1', task1, emb1)
    agent_db.store_task('task_2', task2, emb2)
    
    # Search for similar
    query_emb = task_embedder.embed_task('Create email validator')
    results = agent_db.search_similar(query_emb, top_k=2)
    
    assert len(results) > 0
    assert results[0]['similarity_score'] > 0.5
