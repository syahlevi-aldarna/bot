"""
Reviewer Agent - Reviews code for quality and security

Responsibilities:
- Receive code from coder agent
- Review for quality, security, best practices
- Send review results to tester agent
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ReviewerAgent:
    """Agent that reviews code for quality and security"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.name = 'reviewer'
        self.agent_id = None
        
    async def spawn(self) -> str:
        """Spawn reviewer agent via MCP"""
        logger.info("Spawning reviewer agent...")
        self.agent_id = await self.mcp_client.spawn_agent(
            agent_type='reviewer',
            name='reviewer'
        )
        logger.info(f"Reviewer agent spawned: {self.agent_id}")
        return self.agent_id
    
    async def review_code(self, code_changes: Dict) -> Dict:
        """
        Review code for quality and security
        
        Args:
            code_changes: Code changes from coder
            
        Returns:
            Review results with status and issues
        """
        logger.info("Reviewing code...")
        
        # Simulate code review
        issues = []
        
        # Check for common issues
        code_diff = code_changes.get('code_diff', '')
        
        if 'console.log' in code_diff:
            issues.append({
                'severity': 'medium',
                'message': 'console.log found in production code'
            })
        
        if 'eval(' in code_diff:
            issues.append({
                'severity': 'critical',
                'message': 'eval() is dangerous'
            })
        
        review_status = 'approved' if len(issues) == 0 else 'needs_changes'
        
        review_result = {
            'review_status': review_status,
            'issues': issues,
            'approved_files': code_changes.get('files_changed', []),
            'files_needing_changes': [],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Review complete: {review_status} ({len(issues)} issues)")
        return review_result
    
    async def send_to_tester(self, review_result: Dict) -> bool:
        """Send review to tester agent"""
        logger.info("Sending review to tester...")
        
        message = {
            'to': 'tester',
            'from': 'reviewer',
            'content': review_result
        }
        
        # Send via MCP
        result = await self.mcp_client.send_message(message)
        logger.info(f"Review sent to tester: {result}")
        return result
    
    async def run(self, code_changes: Dict) -> Dict:
        """Main execution flow"""
        try:
            # Spawn agent
            await self.spawn()
            
            # Review code
            review_result = await self.review_code(code_changes)
            
            # Send to tester
            await self.send_to_tester(review_result)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'review_result': review_result
            }
        except Exception as e:
            logger.error(f"Error in reviewer agent: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
