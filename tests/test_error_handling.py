"""
Tests for error handling and recovery

Tests:
- Agent timeout handling
- File operation rollback
- Network error retry logic
- Security violation blocking
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.error_handler import ErrorHandler, ErrorType, ErrorSeverity
from src.recovery.timeout_manager import TimeoutManager
from src.recovery.rollback_manager import RollbackManager
from src.recovery.network_retry_manager import NetworkRetryManager, CircuitState
from src.recovery.security_violation_manager import (
    SecurityViolationManager,
    ViolationType,
    ViolationSeverity
)


# ============================================================================
# ERROR HANDLER TESTS
# ============================================================================

def test_error_handler_timeout():
    """Test error handler for timeout errors"""
    handler = ErrorHandler()
    
    result = handler.handle_error(
        ErrorType.TIMEOUT,
        "Agent exceeded timeout",
        ErrorSeverity.HIGH,
        {'agent_id': 'agent_123', 'timeout_duration': 300}
    )
    
    assert result['success'] is False
    assert result['error_type'] == 'timeout'
    assert result['recovery_action'] == 'kill_agent'
    assert result['agent_id'] == 'agent_123'


def test_error_handler_file_operation():
    """Test error handler for file operation errors"""
    handler = ErrorHandler()
    
    result = handler.handle_error(
        ErrorType.FILE_OPERATION,
        "Failed to write file",
        ErrorSeverity.MEDIUM,
        {'file_path': 'src/app.py', 'operation': 'write'}
    )
    
    assert result['success'] is False
    assert result['error_type'] == 'file_operation'
    assert result['recovery_action'] == 'rollback'


def test_error_handler_network():
    """Test error handler for network errors"""
    handler = ErrorHandler()
    
    result = handler.handle_error(
        ErrorType.NETWORK,
        "Connection timeout",
        ErrorSeverity.MEDIUM,
        {'endpoint': 'http://api.example.com', 'attempt': 1, 'max_retries': 3}
    )
    
    assert result['success'] is False
    assert result['error_type'] == 'network'
    assert result['should_retry'] is True


def test_error_handler_security():
    """Test error handler for security violations"""
    handler = ErrorHandler()
    
    result = handler.handle_error(
        ErrorType.SECURITY,
        "Path traversal detected",
        ErrorSeverity.CRITICAL,
        {'violation_type': 'path_traversal', 'agent_id': 'agent_456'}
    )
    
    assert result['success'] is False
    assert result['error_type'] == 'security'
    assert result['recovery_action'] == 'block_and_alert'


def test_error_handler_stats():
    """Test error handler statistics"""
    handler = ErrorHandler()
    
    # Generate some errors
    handler.handle_error(ErrorType.TIMEOUT, "Timeout 1", ErrorSeverity.HIGH)
    handler.handle_error(ErrorType.TIMEOUT, "Timeout 2", ErrorSeverity.HIGH)
    handler.handle_error(ErrorType.NETWORK, "Network error", ErrorSeverity.MEDIUM)
    
    stats = handler.get_error_stats()
    
    assert stats['total_errors'] == 3
    assert 'timeout_high' in stats['error_counts']
    assert 'network_medium' in stats['error_counts']


# ============================================================================
# TIMEOUT MANAGER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_timeout_manager_start_tracking():
    """Test timeout manager start tracking"""
    manager = TimeoutManager(default_timeout=5)
    
    task = {'description': 'Test task'}
    await manager.start_tracking('agent_123', task)
    
    status = manager.get_agent_status('agent_123')
    assert status is not None
    assert status['agent_id'] == 'agent_123'
    assert status['status'] == 'running'


@pytest.mark.asyncio
async def test_timeout_manager_stop_tracking():
    """Test timeout manager stop tracking"""
    manager = TimeoutManager()
    
    task = {'description': 'Test task'}
    await manager.start_tracking('agent_123', task)
    
    result = await manager.stop_tracking('agent_123')
    
    assert result['success'] is True
    assert result['agent_id'] == 'agent_123'
    assert result['status'] == 'completed'


@pytest.mark.asyncio
async def test_timeout_manager_get_all_agents():
    """Test timeout manager get all agents"""
    manager = TimeoutManager()
    
    task = {'description': 'Test task'}
    await manager.start_tracking('agent_1', task)
    await manager.start_tracking('agent_2', task)
    
    agents = manager.get_all_agents()
    
    assert len(agents) == 2
    assert 'agent_1' in agents
    assert 'agent_2' in agents


@pytest.mark.asyncio
async def test_timeout_manager_callback():
    """Test timeout manager callback on timeout"""
    manager = TimeoutManager(default_timeout=1)
    
    callback_called = []
    
    def on_timeout(agent_id):
        callback_called.append(agent_id)
    
    manager.on_timeout(on_timeout)
    
    task = {'description': 'Test task'}
    await manager.start_tracking('agent_123', task)
    
    # Wait for timeout
    await asyncio.sleep(1.5)
    
    # Callback should have been called
    assert 'agent_123' in callback_called


# ============================================================================
# ROLLBACK MANAGER TESTS
# ============================================================================

def test_rollback_manager_track_operation():
    """Test rollback manager track operation"""
    manager = RollbackManager()
    
    result = manager.track_operation(
        'op_123',
        'write',
        'src/app.py',
        backup_path='.backups/app_20240101_120000.py'
    )
    
    assert result['success'] is True
    assert result['operation_id'] == 'op_123'


@pytest.mark.asyncio
async def test_rollback_manager_rollback_operation():
    """Test rollback manager rollback operation"""
    manager = RollbackManager()
    
    # Track operation
    manager.track_operation(
        'op_123',
        'write',
        'src/app.py',
        backup_path='app_backup.py'
    )
    
    # Mock file executor
    mock_executor = Mock()
    mock_executor.restore_backup = Mock(return_value={
        'success': True,
        'restored': 'src/app.py'
    })
    
    result = await manager.rollback_operation('op_123', mock_executor)
    
    assert result['success'] is True
    assert result['file_path'] == 'src/app.py'


def test_rollback_manager_get_history():
    """Test rollback manager get history"""
    manager = RollbackManager()
    
    manager.track_operation('op_1', 'write', 'file1.py')
    manager.track_operation('op_2', 'delete', 'file2.py')
    
    history = manager.get_operation_history()
    
    assert len(history) == 2
    assert history[0]['id'] == 'op_1'
    assert history[1]['id'] == 'op_2'


def test_rollback_manager_stats():
    """Test rollback manager statistics"""
    manager = RollbackManager()
    
    manager.track_operation('op_1', 'write', 'file1.py')
    manager.track_operation('op_2', 'delete', 'file2.py')
    
    stats = manager.get_stats()
    
    assert stats['total_operations'] == 2
    assert stats['total_rollbacks'] == 0


# ============================================================================
# NETWORK RETRY MANAGER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_network_retry_manager_success():
    """Test network retry manager with successful execution"""
    manager = NetworkRetryManager(max_retries=3)
    
    async def mock_func():
        return {'data': 'success'}
    
    result = await manager.execute_with_retry(mock_func, 'http://api.example.com')
    
    assert result['success'] is True
    assert result['attempt'] == 1


@pytest.mark.asyncio
async def test_network_retry_manager_retry():
    """Test network retry manager with retries"""
    manager = NetworkRetryManager(max_retries=3, initial_delay=0.1)
    
    call_count = [0]
    
    async def mock_func():
        call_count[0] += 1
        if call_count[0] < 3:
            raise Exception("Connection failed")
        return {'data': 'success'}
    
    result = await manager.execute_with_retry(mock_func, 'http://api.example.com')
    
    assert result['success'] is True
    assert result['attempt'] == 3


@pytest.mark.asyncio
async def test_network_retry_manager_max_retries():
    """Test network retry manager max retries exceeded"""
    manager = NetworkRetryManager(max_retries=2, initial_delay=0.05)
    
    async def mock_func():
        raise Exception("Connection failed")
    
    result = await manager.execute_with_retry(mock_func, 'http://api.example.com')
    
    assert result['success'] is False
    assert result['attempts'] == 3  # 0, 1, 2


@pytest.mark.asyncio
async def test_network_retry_manager_circuit_breaker():
    """Test network retry manager circuit breaker"""
    manager = NetworkRetryManager(max_retries=1, initial_delay=0.05)
    
    async def mock_func():
        raise Exception("Connection failed")
    
    # First call - should fail and open circuit
    result1 = await manager.execute_with_retry(mock_func, 'http://api.example.com')
    assert result1['success'] is False
    
    # Second call - circuit should be open
    result2 = await manager.execute_with_retry(mock_func, 'http://api.example.com')
    assert result2['success'] is False
    assert 'Circuit breaker open' in result2['error']


def test_network_retry_manager_stats():
    """Test network retry manager statistics"""
    manager = NetworkRetryManager()
    
    stats = manager.get_retry_stats()
    
    assert stats['total_attempts'] == 0
    assert stats['successful'] == 0
    assert stats['failed'] == 0


# ============================================================================
# SECURITY VIOLATION MANAGER TESTS
# ============================================================================

def test_security_violation_manager_path_traversal():
    """Test security violation manager path traversal detection"""
    manager = SecurityViolationManager()
    
    result = manager.check_path_security('../../../etc/passwd')
    
    assert result['safe'] is False
    assert result['violation']['type'] == 'path_traversal'


def test_security_violation_manager_command_injection():
    """Test security violation manager command injection detection"""
    manager = SecurityViolationManager()
    
    result = manager.check_command_security('npm test | cat /etc/passwd')
    
    assert result['safe'] is False
    assert result['violation']['type'] == 'command_injection'


def test_security_violation_manager_dangerous_command():
    """Test security violation manager dangerous command detection"""
    manager = SecurityViolationManager()
    
    result = manager.check_command_security('rm -rf /')
    
    assert result['safe'] is False
    assert result['violation']['type'] == 'dangerous_command'


def test_security_violation_manager_secret_exposure():
    """Test security violation manager secret exposure detection"""
    manager = SecurityViolationManager()
    
    result = manager.check_content_security('API_KEY=sk_live_123456789')
    
    assert result['safe'] is False
    assert result['violation']['type'] == 'secret_exposure'


def test_security_violation_manager_block_agent():
    """Test security violation manager block agent"""
    manager = SecurityViolationManager()
    
    result = manager.block_agent('agent_123', 'Multiple security violations')
    
    assert result['success'] is True
    assert result['blocked'] is True
    assert manager.is_agent_blocked('agent_123') is True


def test_security_violation_manager_unblock_agent():
    """Test security violation manager unblock agent"""
    manager = SecurityViolationManager()
    
    manager.block_agent('agent_123', 'Test')
    result = manager.unblock_agent('agent_123')
    
    assert result['success'] is True
    assert manager.is_agent_blocked('agent_123') is False


def test_security_violation_manager_stats():
    """Test security violation manager statistics"""
    manager = SecurityViolationManager()
    
    manager.check_path_security('../etc/passwd')
    manager.check_command_security('rm -rf /')
    manager.block_agent('agent_123', 'Test')
    
    stats = manager.get_violation_stats()
    
    assert stats['total_violations'] == 3  # path_traversal + dangerous_command + block
    assert stats['critical'] == 2  # dangerous_command + block
    assert stats['blocked_agents'] == 1


def test_security_violation_manager_callback():
    """Test security violation manager callback"""
    manager = SecurityViolationManager()
    
    violations_caught = []
    
    def on_violation(violation):
        violations_caught.append(violation)
    
    manager.on_violation(on_violation)
    
    manager.check_path_security('../etc/passwd')
    
    assert len(violations_caught) == 1
    assert violations_caught[0]['type'] == 'path_traversal'
