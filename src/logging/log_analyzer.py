"""
Log Analyzer - Analyzes and retrieves logs

Responsibilities:
- Read log files
- Parse structured logs
- Search logs
- Generate reports
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class LogAnalyzer:
    """Analyzes and retrieves logs"""
    
    def __init__(self, log_dir: str = ".claude-flow/logs"):
        """
        Initialize log analyzer
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger(__name__)
    
    def read_log_file(self, log_file: str) -> List[Dict]:
        """
        Read and parse log file
        
        Args:
            log_file: Log file name
            
        Returns:
            List of parsed log entries
        """
        log_path = self.log_dir / log_file
        
        if not log_path.exists():
            self.logger.warning(f"Log file not found: {log_file}")
            return []
        
        entries = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        entries.append(entry)
                    except json.JSONDecodeError:
                        # Skip non-JSON lines
                        continue
        except Exception as e:
            self.logger.error(f"Error reading log file: {str(e)}")
        
        return entries
    
    def search_logs(
        self,
        log_file: str,
        query: str,
        field: Optional[str] = None
    ) -> List[Dict]:
        """
        Search logs for specific query
        
        Args:
            log_file: Log file name
            query: Search query
            field: Optional field to search in
            
        Returns:
            Matching log entries
        """
        entries = self.read_log_file(log_file)
        results = []
        
        for entry in entries:
            if field:
                # Search in specific field
                if field in entry and query.lower() in str(entry[field]).lower():
                    results.append(entry)
            else:
                # Search in all fields
                entry_str = json.dumps(entry).lower()
                if query.lower() in entry_str:
                    results.append(entry)
        
        return results
    
    def get_logs_by_level(self, log_file: str, level: str) -> List[Dict]:
        """Get logs by level"""
        return self.search_logs(log_file, level, field='level')
    
    def get_logs_by_agent(self, log_file: str, agent_id: str) -> List[Dict]:
        """Get logs for specific agent"""
        return self.search_logs(log_file, agent_id, field='agent_id')
    
    def get_logs_by_time_range(
        self,
        log_file: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Get logs within time range"""
        entries = self.read_log_file(log_file)
        results = []
        
        for entry in entries:
            try:
                entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                if start_time <= entry_time <= end_time:
                    results.append(entry)
            except (ValueError, TypeError):
                continue
        
        return results
    
    def get_recent_logs(self, log_file: str, minutes: int = 60) -> List[Dict]:
        """Get logs from last N minutes"""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes)
        return self.get_logs_by_time_range(log_file, start_time, end_time)
    
    def list_log_files(self) -> List[str]:
        """List all log files"""
        if not self.log_dir.exists():
            return []
        
        return [f.name for f in self.log_dir.glob("*.log")]
    
    def get_log_stats(self, log_file: str) -> Dict[str, Any]:
        """Get statistics for log file"""
        entries = self.read_log_file(log_file)
        
        if not entries:
            return {
                'file': log_file,
                'total_entries': 0,
                'levels': {},
                'agents': []
            }
        
        # Count by level
        levels = {}
        for entry in entries:
            level = entry.get('level', 'UNKNOWN')
            levels[level] = levels.get(level, 0) + 1
        
        # Get unique agents
        agents = set()
        for entry in entries:
            if 'agent_id' in entry:
                agents.add(entry['agent_id'])
        
        # Get time range
        first_entry = entries[0]
        last_entry = entries[-1]
        
        return {
            'file': log_file,
            'total_entries': len(entries),
            'levels': levels,
            'agents': list(agents),
            'first_timestamp': first_entry.get('timestamp'),
            'last_timestamp': last_entry.get('timestamp')
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive log report"""
        log_files = self.list_log_files()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_log_files': len(log_files),
            'files': {}
        }
        
        for log_file in log_files:
            report['files'][log_file] = self.get_log_stats(log_file)
        
        return report
    
    def export_logs(
        self,
        log_file: str,
        output_file: str,
        format: str = 'json'
    ) -> bool:
        """
        Export logs to file
        
        Args:
            log_file: Source log file
            output_file: Output file path
            format: Export format (json, csv)
            
        Returns:
            Success status
        """
        entries = self.read_log_file(log_file)
        
        if not entries:
            self.logger.warning(f"No entries to export from {log_file}")
            return False
        
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(entries, f, indent=2)
            elif format == 'csv':
                import csv
                with open(output_path, 'w', newline='') as f:
                    if entries:
                        writer = csv.DictWriter(f, fieldnames=entries[0].keys())
                        writer.writeheader()
                        writer.writerows(entries)
            else:
                self.logger.error(f"Unknown export format: {format}")
                return False
            
            self.logger.info(f"Logs exported to {output_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting logs: {str(e)}")
            return False
