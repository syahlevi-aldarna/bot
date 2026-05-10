"""
Network Retry Manager - Handles network error retry logic

Responsibilities:
- Retry failed network requests
- Exponential backoff
- Circuit breaker pattern
- Track retry statistics
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class NetworkRetryManager:
    """Manages network error retry logic"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0
    ):
        """
        Initialize network retry manager
        
        Args:
            max_retries: Maximum retry attempts
            initial_delay: Initial retry delay in seconds
            backoff_multiplier: Exponential backoff multiplier
            max_delay: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        
        self.retry_history = []
        self.circuit_breakers = {}  # endpoint -> circuit state
    
    async def execute_with_retry(
        self,
        func: Callable,
        endpoint: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute function with retry logic
        
        Args:
            func: Async function to execute
            endpoint: Endpoint identifier
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Execution result
        """
        # Check circuit breaker
        if not self._check_circuit_breaker(endpoint):
            return {
                'success': False,
                'error': f'Circuit breaker open for {endpoint}',
                'endpoint': endpoint
            }
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries + 1} for {endpoint}")
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Success - reset circuit breaker
                self._reset_circuit_breaker(endpoint)
                
                # Track successful retry
                self.retry_history.append({
                    'endpoint': endpoint,
                    'attempt': attempt + 1,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'result': result,
                    'endpoint': endpoint,
                    'attempt': attempt + 1
                }
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # Track failed attempt
                self.retry_history.append({
                    'endpoint': endpoint,
                    'attempt': attempt + 1,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
                # Check if we should retry
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    # All retries exhausted - open circuit breaker
                    self._open_circuit_breaker(endpoint)
                    
                    return {
                        'success': False,
                        'error': f'Max retries exceeded: {str(e)}',
                        'endpoint': endpoint,
                        'attempts': attempt + 1
                    }
        
        return {
            'success': False,
            'error': 'Unknown error',
            'endpoint': endpoint
        }
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay)
    
    def _check_circuit_breaker(self, endpoint: str) -> bool:
        """Check if circuit breaker allows request"""
        if endpoint not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[endpoint]
        
        if breaker['state'] == CircuitState.CLOSED:
            return True
        
        elif breaker['state'] == CircuitState.OPEN:
            # Check if timeout expired
            timeout = timedelta(seconds=60)
            if datetime.now() - breaker['opened_at'] > timeout:
                # Try half-open
                breaker['state'] = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker half-open for {endpoint}")
                return True
            else:
                return False
        
        elif breaker['state'] == CircuitState.HALF_OPEN:
            return True
        
        return True
    
    def _open_circuit_breaker(self, endpoint: str) -> None:
        """Open circuit breaker"""
        self.circuit_breakers[endpoint] = {
            'state': CircuitState.OPEN,
            'opened_at': datetime.now(),
            'failure_count': self.circuit_breakers.get(endpoint, {}).get('failure_count', 0) + 1
        }
        logger.warning(f"Circuit breaker opened for {endpoint}")
    
    def _reset_circuit_breaker(self, endpoint: str) -> None:
        """Reset circuit breaker"""
        if endpoint in self.circuit_breakers:
            self.circuit_breakers[endpoint]['state'] = CircuitState.CLOSED
            logger.info(f"Circuit breaker closed for {endpoint}")
    
    def get_retry_stats(self, endpoint: Optional[str] = None) -> Dict:
        """Get retry statistics"""
        history = self.retry_history
        
        if endpoint:
            history = [h for h in history if h['endpoint'] == endpoint]
        
        successful = len([h for h in history if h['status'] == 'success'])
        failed = len([h for h in history if h['status'] == 'failed'])
        
        return {
            'total_attempts': len(history),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(history) if history else 0,
            'recent_attempts': history[-10:] if history else []
        }
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict]:
        """Get circuit breaker status for all endpoints"""
        return {
            endpoint: {
                'state': breaker['state'].value,
                'opened_at': breaker.get('opened_at', '').isoformat() if breaker.get('opened_at') else None,
                'failure_count': breaker.get('failure_count', 0)
            }
            for endpoint, breaker in self.circuit_breakers.items()
        }
    
    def reset_all_circuit_breakers(self) -> Dict:
        """Reset all circuit breakers"""
        count = len(self.circuit_breakers)
        self.circuit_breakers.clear()
        
        logger.info(f"Reset {count} circuit breakers")
        
        return {
            'success': True,
            'circuit_breakers_reset': count
        }
