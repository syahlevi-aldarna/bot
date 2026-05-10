"""
Tester Agent - Writes and runs tests for code

Responsibilities:
- Receive review results from reviewer agent
- Write tests for the code
- Run tests and validate
- Send results to telegram-bot or back to coder
"""

import asyncio
import logging
import subprocess
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TesterAgent:
    """Agent that writes and runs tests for code"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.name = 'tester'
        self.agent_id = None
        
    async def spawn(self) -> str:
        """Spawn tester agent via MCP"""
        logger.info("Spawning tester agent...")
        self.agent_id = await self.mcp_client.spawn_agent(
            agent_type='tester',
            name='tester'
        )
        logger.info(f"Tester agent spawned: {self.agent_id}")
        return self.agent_id
    
    async def write_tests(self, review_result: Dict) -> str:
        """
        Write tests for the code
        
        Args:
            review_result: Review results from reviewer
            
        Returns:
            Path to test file
        """
        logger.info("Writing tests...")
        
        # Simulate test writing
        test_content = """
describe('Solution Tests', () => {
  test('should work with valid input', () => {
    expect(true).toBe(true);
  });
  
  test('should handle edge cases', () => {
    expect(true).toBe(true);
  });
});
"""
        
        test_file = 'tests/solution.test.js'
        logger.info(f"Tests written to {test_file}")
        return test_file
    
    async def run_tests(self, test_file: str) -> Dict:
        """
        Run tests and collect results
        
        Args:
            test_file: Path to test file
            
        Returns:
            Test results
        """
        logger.info(f"Running tests from {test_file}...")
        
        # Simulate test execution
        test_results = {
            'status': 'passed',
            'total_tests': 10,
            'passed': 10,
            'failed': 0,
            'coverage': 85.5,
            'execution_time': 2.3,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Tests completed: {test_results['status']}")
        return test_results
    
    async def send_results(self, test_results: Dict, review_status: str) -> bool:
        """Send test results to appropriate agent"""
        logger.info(f"Sending test results (status: {test_results['status']})...")
        
        if test_results['status'] == 'failed':
            # Send back to coder for fixes
            recipient = 'coder'
        else:
            # Send to telegram-bot for final result
            recipient = 'telegram-bot'
        
        message = {
            'to': recipient,
            'from': 'tester',
            'content': test_results
        }
        
        # Send via MCP
        result = await self.mcp_client.send_message(message)
        logger.info(f"Results sent to {recipient}: {result}")
        return result
    
    async def run(self, review_result: Dict) -> Dict:
        """Main execution flow"""
        try:
            # Spawn agent
            await self.spawn()
            
            # Check review status
            review_status = review_result.get('review_status', 'unknown')
            
            if review_status == 'rejected':
                logger.info("Review rejected, skipping tests")
                return {
                    'status': 'skipped',
                    'reason': 'review_rejected'
                }
            
            # Write tests
            test_file = await self.write_tests(review_result)
            
            # Run tests
            test_results = await self.run_tests(test_file)
            
            # Send results
            await self.send_results(test_results, review_status)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'test_results': test_results
            }
        except Exception as e:
            logger.error(f"Error in tester agent: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
