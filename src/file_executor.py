"""
File Executor - Safe file read/write operations
Validates paths, permissions, and creates backups
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class FileExecutor:
    """Safe file operations with validation and backup"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / ".backups"
        self.backup_dir.mkdir(exist_ok=True)

    def _validate_path(self, file_path: str) -> Path:
        """
        Validate file path is within project directory
        
        Args:
            file_path: File path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If path is outside project directory
        """
        # Resolve the path
        resolved = (self.project_root / file_path).resolve()

        # Check if path is within project root
        try:
            resolved.relative_to(self.project_root)
        except ValueError:
            raise ValueError(f"Path {file_path} is outside project directory")

        return resolved

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file safely
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with content and metadata
        """
        try:
            path = self._validate_path(file_path)

            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if not path.is_file():
                raise ValueError(f"Not a file: {file_path}")

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "success": True,
                "path": str(path.relative_to(self.project_root)),
                "content": content,
                "size": len(content),
                "lines": len(content.split("\n")),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": file_path,
            }

    def write_file(self, file_path: str, content: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Write file safely with backup
        
        Args:
            file_path: Path to file
            content: File content
            create_backup: Whether to backup existing file
            
        Returns:
            Dict with operation result
        """
        try:
            path = self._validate_path(file_path)

            # Create backup if file exists
            if path.exists() and create_backup:
                backup_path = self._create_backup(path)
                backup_info = f"Backup created: {backup_path}"
            else:
                backup_info = "No backup needed"

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "path": str(path.relative_to(self.project_root)),
                "size": len(content),
                "lines": len(content.split("\n")),
                "backup": backup_info,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": file_path,
            }

    def edit_file(self, file_path: str, replacements: Dict[str, str]) -> Dict[str, Any]:
        """
        Edit file by replacing content
        
        Args:
            file_path: Path to file
            replacements: Dict of {old_text: new_text}
            
        Returns:
            Dict with operation result
        """
        try:
            # Read file
            read_result = self.read_file(file_path)
            if not read_result["success"]:
                return read_result

            content = read_result["content"]

            # Apply replacements
            for old_text, new_text in replacements.items():
                if old_text not in content:
                    return {
                        "success": False,
                        "error": f"Text not found: {old_text[:50]}...",
                        "path": file_path,
                    }
                content = content.replace(old_text, new_text)

            # Write file with backup
            return self.write_file(file_path, content, create_backup=True)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": file_path,
            }

    def delete_file(self, file_path: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Delete file safely with backup
        
        Args:
            file_path: Path to file
            create_backup: Whether to backup before deleting
            
        Returns:
            Dict with operation result
        """
        try:
            path = self._validate_path(file_path)

            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Create backup if requested
            if create_backup:
                backup_path = self._create_backup(path)
                backup_info = f"Backup created: {backup_path}"
            else:
                backup_info = "No backup created"

            # Delete file
            path.unlink()

            return {
                "success": True,
                "path": str(path.relative_to(self.project_root)),
                "backup": backup_info,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": file_path,
            }

    def list_files(self, directory: str = ".", pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in directory
        
        Args:
            directory: Directory to list
            pattern: Optional glob pattern (e.g., "*.py")
            
        Returns:
            Dict with file list
        """
        try:
            path = self._validate_path(directory)

            if not path.is_dir():
                raise ValueError(f"Not a directory: {directory}")

            files = []
            if pattern:
                for file_path in path.glob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path.relative_to(self.project_root)))
            else:
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        files.append(str(file_path.relative_to(self.project_root)))

            return {
                "success": True,
                "directory": directory,
                "files": sorted(files),
                "count": len(files),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory,
            }

    def _create_backup(self, file_path: Path) -> str:
        """Create backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        return str(backup_path.relative_to(self.project_root))

    def restore_backup(self, backup_file: str) -> Dict[str, Any]:
        """
        Restore file from backup
        
        Args:
            backup_file: Backup file name
            
        Returns:
            Dict with operation result
        """
        try:
            backup_path = self.backup_dir / backup_file

            if not backup_path.exists():
                raise FileNotFoundError(f"Backup not found: {backup_file}")

            # Extract original filename
            parts = backup_file.split("_")
            if len(parts) < 3:
                raise ValueError(f"Invalid backup filename: {backup_file}")

            original_name = "_".join(parts[:-2]) + parts[-1]
            original_path = self.project_root / original_name

            # Restore
            shutil.copy2(backup_path, original_path)

            return {
                "success": True,
                "restored": str(original_path.relative_to(self.project_root)),
                "from_backup": backup_file,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backup_file": backup_file,
            }
