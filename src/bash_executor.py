"""
Bash Executor - Safe bash command execution
Validates commands against whitelist
"""

import asyncio
import subprocess
from typing import Dict, Any, List, Optional


class BashExecutor:
    """Safe bash command execution with validation"""

    # Whitelist of allowed commands
    ALLOWED_COMMANDS = {
        "npm": ["install", "test", "run", "list", "audit"],
        "yarn": ["install", "test", "run", "list"],
        "python": ["--version"],
        "python3": ["--version"],
        "git": ["status", "log", "diff", "add", "commit", "branch", "checkout", "push", "pull"],
        "node": ["--version"],
        "cat": [],
        "ls": ["-la", "-l"],
        "mkdir": ["-p"],
        "cp": ["-r"],
        "mv": [],
        "grep": [],
        "find": [],
        "echo": [],
        "test": [],
    }

    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    def _validate_command(self, command: str) -> tuple[bool, str]:
        """
        Validate command against whitelist
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        parts = command.strip().split()

        if not parts:
            return False, "Empty command"

        cmd = parts[0]

        # Check if command is in whitelist
        if cmd not in self.ALLOWED_COMMANDS:
            return False, f"Command not allowed: {cmd}"

        # Check if subcommand is allowed (if specified)
        if len(parts) > 1:
            subcommand = parts[1]
            allowed_subs = self.ALLOWED_COMMANDS[cmd]

            # If whitelist is empty, allow any subcommand
            if allowed_subs and subcommand not in allowed_subs:
                # Check if it's a flag
                if not subcommand.startswith("-"):
                    return False, f"Subcommand not allowed: {cmd} {subcommand}"

        # Check for dangerous patterns
        dangerous_patterns = [
            "rm -rf /",
            "dd if=/dev/zero",
            "> /dev/sda",
            "fork()",
            ":(){ :|:& };:",  # Fork bomb
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Dangerous pattern detected: {pattern}"

        return True, ""

    async def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute bash command safely
        
        Args:
            command: Command to execute
            cwd: Working directory
            
        Returns:
            Dict with execution result
        """
        # Validate command
        is_valid, error = self._validate_command(command)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "command": command,
            }

        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Command timeout after {self.timeout} seconds",
                    "command": command,
                }

            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()

            return {
                "success": process.returncode == 0,
                "command": command,
                "exit_code": process.returncode,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "output": stdout_text if process.returncode == 0 else stderr_text,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
            }

    async def execute_npm(self, args: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute npm command"""
        command = f"npm {' '.join(args)}"
        return await self.execute(command, cwd)

    async def execute_git(self, args: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute git command"""
        command = f"git {' '.join(args)}"
        return await self.execute(command, cwd)

    async def execute_test(self, test_runner: str = "npm", cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute tests
        
        Args:
            test_runner: Test runner (npm, yarn, pytest)
            cwd: Working directory
            
        Returns:
            Dict with test results
        """
        if test_runner == "npm":
            return await self.execute_npm(["test"], cwd)
        elif test_runner == "yarn":
            return await self.execute("yarn test", cwd)
        elif test_runner == "pytest":
            return await self.execute("python3 -m pytest", cwd)
        else:
            return {
                "success": False,
                "error": f"Unknown test runner: {test_runner}",
            }

    def get_allowed_commands(self) -> Dict[str, List[str]]:
        """Get list of allowed commands"""
        return self.ALLOWED_COMMANDS
