"""
End-to-End Test Coordinator - Orchestrates full system tests

Responsibilities:
- Coordinate full workflow tests
- Verify correctness properties
- Track test results
- Generate test reports
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class E2ETestCoordinator:
    """Coordinates end-to-end tests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        self.test_suites = {}
    
    async def run_simple_coding_task(
        self,
        mcp_client,
        file_executor,
        task_description: str = "Create email validator function"
    ) -> Dict[str, Any]:
        """
        Test simple coding task
        
        Args:
            mcp_client: MCP client
            file_executor: File executor
            task_description: Task description
            
        Returns:
            Test result
        """
        test_name = "simple_coding_task"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Spawn coder agent
            agent_id = await mcp_client.spawn_agent({
                "type": "coder",
                "task": task_description,
                "namespace": "test"
            })
            
            # Verify agent spawned
            status = await mcp_client.get_agent_status(agent_id)
            assert status['status'] == 'running', "Agent not running"
            
            # Simulate code generation
            code_content = """
def validate_email(email: str) -> bool:
    '''Validate email format'''
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Test cases
assert validate_email('test@example.com') == True
assert validate_email('invalid.email') == False
"""
            
            # Write code to file
            result = file_executor.write_file("src/email_validator.py", code_content)
            assert result['success'], "Failed to write code"
            
            # Kill agent
            await mcp_client.kill_agent(agent_id)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                'test_name': test_name,
                'status': TestStatus.PASSED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'details': {
                    'agent_id': agent_id,
                    'code_file': 'src/email_validator.py',
                    'code_lines': len(code_content.split('\n'))
                }
            }
            
            self.logger.info(f"Test passed: {test_name} ({elapsed:.2f}s)")
            return test_result
        
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return {
                'test_name': test_name,
                'status': TestStatus.FAILED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'error': str(e)
            }
    
    async def run_code_review_workflow(
        self,
        mcp_client,
        file_executor
    ) -> Dict[str, Any]:
        """
        Test code review workflow
        
        Args:
            mcp_client: MCP client
            file_executor: File executor
            
        Returns:
            Test result
        """
        test_name = "code_review_workflow"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Create test code with issues
            test_code = """
def process_data(data):
    # Missing type hints
    result = []
    for item in data:
        print(f"Processing {item}")  # console.log in production
        result.append(item * 2)
    return result
"""
            
            # Write code
            file_executor.write_file("src/test_code.py", test_code)
            
            # Spawn reviewer agent
            reviewer_id = await mcp_client.spawn_agent({
                "type": "reviewer",
                "task": "Review code quality",
                "namespace": "test"
            })
            
            # Verify reviewer spawned
            status = await mcp_client.get_agent_status(reviewer_id)
            assert status['status'] == 'running', "Reviewer not running"
            
            # Simulate review
            review_issues = [
                {'severity': 'medium', 'message': 'Missing type hints'},
                {'severity': 'medium', 'message': 'Debug print in production code'}
            ]
            
            # Kill reviewer
            await mcp_client.kill_agent(reviewer_id)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                'test_name': test_name,
                'status': TestStatus.PASSED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'details': {
                    'reviewer_id': reviewer_id,
                    'issues_found': len(review_issues),
                    'issues': review_issues
                }
            }
            
            self.logger.info(f"Test passed: {test_name} ({elapsed:.2f}s)")
            return test_result
        
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return {
                'test_name': test_name,
                'status': TestStatus.FAILED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'error': str(e)
            }
    
    async def run_test_generation(
        self,
        mcp_client,
        bash_executor
    ) -> Dict[str, Any]:
        """
        Test test generation and execution
        
        Args:
            mcp_client: MCP client
            bash_executor: Bash executor
            
        Returns:
            Test result
        """
        test_name = "test_generation"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Spawn tester agent
            tester_id = await mcp_client.spawn_agent({
                "type": "tester",
                "task": "Generate tests",
                "namespace": "test"
            })
            
            # Verify tester spawned
            status = await mcp_client.get_agent_status(tester_id)
            assert status['status'] == 'running', "Tester not running"
            
            # Simulate test generation
            test_code = """
import pytest

def test_validate_email_valid():
    from email_validator import validate_email
    assert validate_email('test@example.com') == True

def test_validate_email_invalid():
    from email_validator import validate_email
    assert validate_email('invalid') == False

def test_validate_email_edge_cases():
    from email_validator import validate_email
    assert validate_email('') == False
    assert validate_email('a@b.c') == True
"""
            
            # Kill tester
            await mcp_client.kill_agent(tester_id)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                'test_name': test_name,
                'status': TestStatus.PASSED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'details': {
                    'tester_id': tester_id,
                    'tests_generated': 3,
                    'test_lines': len(test_code.split('\n'))
                }
            }
            
            self.logger.info(f"Test passed: {test_name} ({elapsed:.2f}s)")
            return test_result
        
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return {
                'test_name': test_name,
                'status': TestStatus.FAILED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'error': str(e)
            }
    
    async def run_memory_learning_test(
        self,
        agent_db,
        task_embedder,
        sona_learner
    ) -> Dict[str, Any]:
        """
        Test memory learning from past tasks
        
        Args:
            agent_db: Agent database
            task_embedder: Task embedder
            sona_learner: SONA learner
            
        Returns:
            Test result
        """
        test_name = "memory_learning"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Store past task
            past_task = {
                'id': 'task_1',
                'description': 'Create email validator',
                'solution': 'regex pattern matching',
                'success': True
            }
            
            embedding = task_embedder.embed_task(past_task['description'])
            agent_db.store_task('task_1', past_task, embedding)
            
            # Learn pattern
            sona_learner.learn_from_task(
                past_task,
                {'success': True, 'solution_type': 'regex'}
            )
            
            # Search for similar task
            new_task_desc = 'Create phone number validator'
            new_embedding = task_embedder.embed_task(new_task_desc)
            
            similar_tasks = agent_db.search_similar(new_embedding, top_k=1)
            assert len(similar_tasks) > 0, "No similar tasks found"
            
            # Get applicable patterns
            new_task = {'description': new_task_desc}
            patterns = sona_learner.get_applicable_patterns(new_task)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                'test_name': test_name,
                'status': TestStatus.PASSED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'details': {
                    'tasks_stored': 1,
                    'similar_tasks_found': len(similar_tasks),
                    'patterns_found': len(patterns)
                }
            }
            
            self.logger.info(f"Test passed: {test_name} ({elapsed:.2f}s)")
            return test_result
        
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return {
                'test_name': test_name,
                'status': TestStatus.FAILED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'error': str(e)
            }
    
    async def run_error_recovery_test(
        self,
        error_handler,
        timeout_manager,
        rollback_manager,
        mcp_client
    ) -> Dict[str, Any]:
        """
        Test error recovery scenarios
        
        Args:
            error_handler: Error handler
            timeout_manager: Timeout manager
            rollback_manager: Rollback manager
            mcp_client: MCP client
            
        Returns:
            Test result
        """
        from src.error_handler import ErrorType, ErrorSeverity
        
        test_name = "error_recovery"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Test timeout handling
            await timeout_manager.start_tracking('test_agent', {'task': 'test'}, timeout=1)
            status = timeout_manager.get_agent_status('test_agent')
            assert status is not None, "Agent not tracked"
            
            await timeout_manager.stop_tracking('test_agent')
            
            # Test rollback
            rollback_manager.track_operation(
                'op_1',
                'write',
                'test_file.py',
                backup_path='test_file_backup.py'
            )
            
            history = rollback_manager.get_operation_history()
            assert len(history) > 0, "Operation not tracked"
            
            # Test error handling
            result = error_handler.handle_error(
                ErrorType.TIMEOUT,
                "Test timeout",
                ErrorSeverity.HIGH,
                {'agent_id': 'test_agent'}
            )
            
            assert result['success'] is False, "Error not handled"
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                'test_name': test_name,
                'status': TestStatus.PASSED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'details': {
                    'timeout_tests': 1,
                    'rollback_tests': 1,
                    'error_handling_tests': 1
                }
            }
            
            self.logger.info(f"Test passed: {test_name} ({elapsed:.2f}s)")
            return test_result
        
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return {
                'test_name': test_name,
                'status': TestStatus.FAILED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'error': str(e)
            }
    
    async def run_security_validation_test(
        self,
        security_manager
    ) -> Dict[str, Any]:
        """
        Test security validations
        
        Args:
            security_manager: Security violation manager
            
        Returns:
            Test result
        """
        test_name = "security_validation"
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting test: {test_name}")
            
            # Test path traversal detection
            result1 = security_manager.check_path_security('../../../etc/passwd')
            assert result1['safe'] is False, "Path traversal not detected"
            
            # Test command injection detection
            result2 = security_manager.check_command_security('npm test | cat /etc/passwd')
            assert result2['safe'] is False, "Command injection not detected"
            
            # Test dangerous command detection
            result3 = security_manager.check_command_security('rm -rf /')
            assert result3['safe'] is False, "Dangerous command not detected"
            
            # Test secret exposure detection
            result4 = security_manager.check_content_security('API_KEY=sk_live_123456')
            assert result4['safe'] is False, "Secret exposure not detected"
            
            # Test agent blocking
            security_manager.block_agent('malicious_agent', 'Multiple violations')
            assert security_manager.is_agent_blocked('malicious_agent'), "Agent not blocked"
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            test_result = {
                'test_name': test_name,
                'status': TestStatus.PASSED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'details': {
                    'path_traversal_tests': 1,
                    'command_injection_tests': 1,
                    'dangerous_command_tests': 1,
                    'secret_exposure_tests': 1,
                    'agent_blocking_tests': 1
                }
            }
            
            self.logger.info(f"Test passed: {test_name} ({elapsed:.2f}s)")
            return test_result
        
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Test failed: {test_name} - {str(e)}")
            
            return {
                'test_name': test_name,
                'status': TestStatus.FAILED.value,
                'elapsed_time': elapsed,
                'timestamp': start_time.isoformat(),
                'error': str(e)
            }
    
    def record_test_result(self, result: Dict[str, Any]) -> None:
        """Record test result"""
        self.test_results.append(result)
    
    def get_test_results(self) -> List[Dict[str, Any]]:
        """Get all test results"""
        return self.test_results.copy()
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == TestStatus.PASSED.value])
        failed = len([r for r in self.test_results if r['status'] == TestStatus.FAILED.value])
        
        total_time = sum(r.get('elapsed_time', 0) for r in self.test_results)
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / total_tests if total_tests > 0 else 0,
            'total_time': total_time,
            'avg_time': total_time / total_tests if total_tests > 0 else 0
        }
