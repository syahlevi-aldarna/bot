"""
Logger Factory - Creates and manages structured loggers

Responsibilities:
- Create loggers for different components
- Configure log levels
- Setup log handlers (file, console)
- Manage log rotation
"""

import logging
import logging.handlers
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class LoggerFactory:
    """Factory for creating structured loggers"""
    
    def __init__(self, log_dir: str = ".claude-flow/logs"):
        """
        Initialize logger factory
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.loggers = {}
        self.log_files = {}
    
    def get_logger(
        self,
        name: str,
        level: int = logging.INFO,
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """
        Get or create logger
        
        Args:
            name: Logger name
            level: Log level
            log_file: Optional log file name
            
        Returns:
            Configured logger
        """
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = self.log_dir / log_file
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(level)
            file_formatter = StructuredFormatter()
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            self.log_files[name] = str(log_path)
        
        self.loggers[name] = logger
        return logger
    
    def get_agent_logger(self, agent_id: str) -> logging.Logger:
        """Get logger for specific agent"""
        log_file = f"agent_{agent_id}.log"
        return self.get_logger(f"agent.{agent_id}", log_file=log_file)
    
    def get_memory_logger(self) -> logging.Logger:
        """Get logger for memory operations"""
        return self.get_logger("memory", log_file="memory.log")
    
    def get_security_logger(self) -> logging.Logger:
        """Get logger for security events"""
        return self.get_logger("security", log_file="security.log")
    
    def get_error_logger(self) -> logging.Logger:
        """Get logger for errors"""
        return self.get_logger("error", log_file="error.log")
    
    def get_coordination_logger(self) -> logging.Logger:
        """Get logger for agent coordination"""
        return self.get_logger("coordination", log_file="coordination.log")
    
    def get_all_loggers(self) -> Dict[str, logging.Logger]:
        """Get all created loggers"""
        return self.loggers.copy()
    
    def get_log_files(self) -> Dict[str, str]:
        """Get all log file paths"""
        return self.log_files.copy()
    
    def list_log_files(self) -> list:
        """List all log files in log directory"""
        if not self.log_dir.exists():
            return []
        
        return [str(f) for f in self.log_dir.glob("*.log")]
