"""
Tests for Bash Executor
"""

import pytest
import asyncio
from src.bash_executor import BashExecutor


@pytest.fixture
def executor():
    """Create bash executor"""
    return BashExecutor(timeout=10)


@pytest.mark.asyncio
async def test_validate_allowed_command(executor):
    """Test validating allowed command"""
    is_valid, error = executor._validate_command("npm test")
    assert is_valid is True
    assert error == ""


@pytest.mark.asyncio
async def test_validate_disallowed_command(executor):
    """Test validating disallowed command"""
    is_valid, error = executor._validate_command("rm -rf /")
    assert is_valid is False
    assert "not allowed" in error.lower() or "dangerous" in error.lower()


@pytest.mark.asyncio
async def test_validate_dangerous_pattern(executor):
    """Test detecting dangerous patterns"""
    is_valid, error = executor._validate_command("npm install && rm -rf /")
    assert is_valid is False
    assert "dangerous" in error.lower()


@pytest.mark.asyncio
async def test_execute_echo_command(executor):
    """Test executing echo command"""
    result = await executor.execute("echo 'Hello, World!'")

    assert result["success"] is True
    assert "Hello, World!" in result["stdout"]


@pytest.mark.asyncio
async def test_execute_node_version(executor):
    """Test executing node --version"""
    result = await executor.execute("node --version")

    assert result["success"] is True
    assert "v" in result["stdout"]


@pytest.mark.asyncio
async def test_execute_invalid_command(executor):
    """Test executing invalid command"""
    result = await executor.execute("invalid_command_xyz")

    assert result["success"] is False
    assert "not allowed" in result["error"].lower()


@pytest.mark.asyncio
async def test_execute_command_timeout(executor):
    """Test command timeout"""
    executor_short = BashExecutor(timeout=1)
    result = await executor_short.execute("echo 'test' && sleep 5")

    assert result["success"] is False
    assert "timeout" in result["error"].lower()


@pytest.mark.asyncio
async def test_execute_npm_install(executor):
    """Test executing npm install"""
    result = await executor.execute_npm(["--version"])

    assert result["success"] is True
    assert "npm" in result["stdout"].lower() or result["exit_code"] == 0


@pytest.mark.asyncio
async def test_execute_git_status(executor):
    """Test executing git status"""
    result = await executor.execute_git(["--version"])

    assert result["success"] is True
    assert "git" in result["stdout"].lower()


@pytest.mark.asyncio
async def test_get_allowed_commands(executor):
    """Test getting allowed commands"""
    commands = executor.get_allowed_commands()

    assert "npm" in commands
    assert "git" in commands
    assert "python3" in commands
    assert "rm" not in commands


@pytest.mark.asyncio
async def test_execute_with_stderr(executor):
    """Test executing command with stderr"""
    result = await executor.execute("node --invalid-flag")

    assert result["success"] is False
    assert result["exit_code"] != 0
