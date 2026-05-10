"""
Tests for logging and observability

Tests:
- Structured logging
- Agent action logging
- Memory operation logging
- Security event logging
- Log analysis and retrieval
"""

import pytest
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta

from src.logging.logger_factory import LoggerFactory, StructuredFormatter
from src.logging.agent_action_logger import AgentActionLogger, AgentAction
from src.logging.memory_operation_logger import MemoryOperationLogger, MemoryOperation
from src.logging.security_event_logger import SecurityEventLogger, SecurityEventType, SecuritySeverity
from src.logging.log_analyzer import LogAnalyzer


# ============================================================================
# LOGGER FACTORY TESTS
# ============================================================================

def test_logger_factory_create_logger():
    """Test logger factory creates logger"""
    factory = LoggerFactory()
    logger = factory.get_logger("test_logger")
    
    assert logger is not None
    assert logger.name == "test_logger"


def test_logger_factory_get_agent_logger():
    """Test logger factory get agent logger"""
    factory = LoggerFactory()
    logger = factory.get_agent_logger("agent_123")
    
    assert logger is not None
    assert "agent.agent_123" in logger.name


def test_logger_factory_get_memory_logger():
    """Test logger factory get memory logger"""
    factory = LoggerFactory()
    logger = factory.get_memory_logger()
    
    assert logger is not None
    assert "memory" in logger.name


def test_logger_factory_get_security_logger():
    """Test logger factory get security logger"""
    factory = LoggerFactory()
    logger = factory.get_security_logger()
    
    assert logger is not None
    assert "security" in logger.name


def test_logger_factory_get_error_logger():
    """Test logger factory get error logger"""
    factory = LoggerFactory()
    logger = factory.get_error_logger()
    
    assert logger is not None
    assert "error" in logger.name


def test_logger_factory_list_log_files():
    """Test logger factory list log files"""
    factory = LoggerFactory()
    
    # Create some loggers with files
    factory.get_logger("test1", log_file="test1.log")
    factory.get_logger("test2", log_file="test2.log")
    
    files = factory.list_log_files()
    
    assert len(files) >= 2


# ============================================================================
# AGENT ACTION LOGGER TESTS
# ============================================================================

def test_agent_action_logger_spawn():
    """Test agent action logger spawn"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    result = action_logger.log_spawn("agent_123", "coder", {"description": "test task"})
    
    assert result['action'] == AgentAction.SPAWN.value
    assert result['agent_id'] == "agent_123"
    assert result['agent_type'] == "coder"


def test_agent_action_logger_kill():
    """Test agent action logger kill"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    result = action_logger.log_kill("agent_123", "timeout")
    
    assert result['action'] == AgentAction.KILL.value
    assert result['agent_id'] == "agent_123"
    assert result['reason'] == "timeout"


def test_agent_action_logger_state_change():
    """Test agent action logger state change"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    result = action_logger.log_state_change("agent_123", "spawning", "running")
    
    assert result['action'] == AgentAction.STATE_CHANGE.value
    assert result['old_state'] == "spawning"
    assert result['new_state'] == "running"


def test_agent_action_logger_task_complete():
    """Test agent action logger task complete"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    result = action_logger.log_task_complete(
        "agent_123",
        "task_456",
        {"status": "success"},
        2.5
    )
    
    assert result['action'] == AgentAction.TASK_COMPLETE.value
    assert result['execution_time'] == 2.5


def test_agent_action_logger_task_failed():
    """Test agent action logger task failed"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    result = action_logger.log_task_failed(
        "agent_123",
        "task_456",
        "Connection timeout",
        1.5
    )
    
    assert result['action'] == AgentAction.TASK_FAILED.value
    assert result['error'] == "Connection timeout"


def test_agent_action_logger_message_sent():
    """Test agent action logger message sent"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    result = action_logger.log_message_sent("coder", "reviewer", "msg_123", 1024)
    
    assert result['action'] == AgentAction.MESSAGE_SENT.value
    assert result['from_agent'] == "coder"
    assert result['to_agent'] == "reviewer"


def test_agent_action_logger_get_stats():
    """Test agent action logger get stats"""
    logger = logging.getLogger("test")
    action_logger = AgentActionLogger(logger)
    
    action_logger.log_spawn("agent_123", "coder", {"description": "test"})
    action_logger.log_task_complete("agent_123", "task_1", {}, 1.0)
    action_logger.log_task_complete("agent_123", "task_2", {}, 2.0)
    action_logger.log_task_failed("agent_123", "task_3", "error", 0.5)
    
    stats = action_logger.get_agent_stats("agent_123")
    
    assert stats['agent_id'] == "agent_123"
    assert stats['tasks_completed'] == 2
    assert stats['tasks_failed'] == 1
    assert stats['success_rate'] == 2/3


# ============================================================================
# MEMORY OPERATION LOGGER TESTS
# ============================================================================

def test_memory_operation_logger_store():
    """Test memory operation logger store"""
    logger = logging.getLogger("test")
    mem_logger = MemoryOperationLogger(logger)
    
    result = mem_logger.log_store("task_123", "coding", 100)
    
    assert result['operation'] == MemoryOperation.STORE.value
    assert result['task_id'] == "task_123"
    assert result['embedding_size'] == 100


def test_memory_operation_logger_search():
    """Test memory operation logger search"""
    logger = logging.getLogger("test")
    mem_logger = MemoryOperationLogger(logger)
    
    result = mem_logger.log_search("create function", 5, 0.95, 0.123)
    
    assert result['operation'] == MemoryOperation.SEARCH.value
    assert result['results_count'] == 5
    assert result['top_similarity'] == 0.95


def test_memory_operation_logger_learn_pattern():
    """Test memory operation logger learn pattern"""
    logger = logging.getLogger("test")
    mem_logger = MemoryOperationLogger(logger)
    
    result = mem_logger.log_learn_pattern("pattern_1", "coding", True, 0.85)
    
    assert result['operation'] == MemoryOperation.LEARN_PATTERN.value
    assert result['success'] is True
    assert result['confidence'] == 0.85


def test_memory_operation_logger_apply_pattern():
    """Test memory operation logger apply pattern"""
    logger = logging.getLogger("test")
    mem_logger = MemoryOperationLogger(logger)
    
    result = mem_logger.log_apply_pattern("pattern_1", "task_123", True)
    
    assert result['operation'] == MemoryOperation.APPLY_PATTERN.value
    assert result['applied'] is True


def test_memory_operation_logger_get_stats():
    """Test memory operation logger get stats"""
    logger = logging.getLogger("test")
    mem_logger = MemoryOperationLogger(logger)
    
    mem_logger.log_store("task_1", "coding", 100)
    mem_logger.log_store("task_2", "coding", 100)
    mem_logger.log_search("query", 3, 0.9, 0.1)
    mem_logger.log_learn_pattern("pattern_1", "coding", True, 0.8)
    
    stats = mem_logger.get_stats()
    
    assert stats['total_operations'] == 4
    assert stats['store_operations'] == 2
    assert stats['search_operations'] == 1
    assert stats['learn_operations'] == 1


# ============================================================================
# SECURITY EVENT LOGGER TESTS
# ============================================================================

def test_security_event_logger_violation():
    """Test security event logger violation"""
    logger = logging.getLogger("test")
    sec_logger = SecurityEventLogger(logger)
    
    result = sec_logger.log_violation(
        "path_traversal",
        "agent_123",
        "Attempted to access ../etc/passwd",
        SecuritySeverity.CRITICAL
    )
    
    assert result['event_type'] == SecurityEventType.VIOLATION.value
    assert result['severity'] == SecuritySeverity.CRITICAL.value


def test_security_event_logger_blocked():
    """Test security event logger blocked"""
    logger = logging.getLogger("test")
    sec_logger = SecurityEventLogger(logger)
    
    result = sec_logger.log_blocked(
        "agent_123",
        "rm -rf /",
        "Dangerous command"
    )
    
    assert result['event_type'] == SecurityEventType.BLOCKED.value
    assert result['action'] == "rm -rf /"


def test_security_event_logger_allowed():
    """Test security event logger allowed"""
    logger = logging.getLogger("test")
    sec_logger = SecurityEventLogger(logger)
    
    result = sec_logger.log_allowed("agent_123", "read", "src/app.py")
    
    assert result['event_type'] == SecurityEventType.ALLOWED.value
    assert result['action'] == "read"


def test_security_event_logger_authentication():
    """Test security event logger authentication"""
    logger = logging.getLogger("test")
    sec_logger = SecurityEventLogger(logger)
    
    result = sec_logger.log_authentication("agent_123", True, "token")
    
    assert result['event_type'] == SecurityEventType.AUTHENTICATION.value
    assert result['success'] is True


def test_security_event_logger_get_violations():
    """Test security event logger get violations"""
    logger = logging.getLogger("test")
    sec_logger = SecurityEventLogger(logger)
    
    sec_logger.log_violation("path_traversal", "agent_1", "test", SecuritySeverity.CRITICAL)
    sec_logger.log_violation("command_injection", "agent_2", "test", SecuritySeverity.CRITICAL)
    sec_logger.log_allowed("agent_3", "read", "file.py")
    
    violations = sec_logger.get_violations()
    
    assert len(violations) == 2


def test_security_event_logger_get_stats():
    """Test security event logger get stats"""
    logger = logging.getLogger("test")
    sec_logger = SecurityEventLogger(logger)
    
    sec_logger.log_violation("path_traversal", "agent_1", "test", SecuritySeverity.CRITICAL)
    sec_logger.log_blocked("agent_2", "rm -rf /", "dangerous")
    sec_logger.log_allowed("agent_3", "read", "file.py")
    
    stats = sec_logger.get_stats()
    
    assert stats['total_events'] == 3
    assert stats['violations'] == 1
    assert stats['blocked_actions'] == 1


# ============================================================================
# LOG ANALYZER TESTS
# ============================================================================

def test_log_analyzer_list_log_files():
    """Test log analyzer list log files"""
    analyzer = LogAnalyzer()
    files = analyzer.list_log_files()
    
    # Should return a list (may be empty if no logs yet)
    assert isinstance(files, list)


def test_log_analyzer_get_log_stats():
    """Test log analyzer get log stats"""
    analyzer = LogAnalyzer()
    
    # Try to get stats for a log file (may not exist)
    stats = analyzer.get_log_stats("nonexistent.log")
    
    assert stats['file'] == "nonexistent.log"
    assert stats['total_entries'] == 0


def test_log_analyzer_generate_report():
    """Test log analyzer generate report"""
    analyzer = LogAnalyzer()
    report = analyzer.generate_report()
    
    assert 'timestamp' in report
    assert 'total_log_files' in report
    assert 'files' in report


def test_log_analyzer_export_logs():
    """Test log analyzer export logs"""
    analyzer = LogAnalyzer()
    
    # Try to export (may fail if no logs)
    result = analyzer.export_logs("nonexistent.log", "/tmp/export.json")
    
    # Should return False for nonexistent file
    assert result is False
