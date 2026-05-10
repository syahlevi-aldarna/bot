"""
E2E package - End-to-end testing

Modules:
- e2e_test_coordinator: Orchestrates full system tests
"""

from .e2e_test_coordinator import E2ETestCoordinator, TestStatus

__all__ = [
    'E2ETestCoordinator',
    'TestStatus'
]
