"""
Tests for File Executor
"""

import pytest
import tempfile
from pathlib import Path
from src.file_executor import FileExecutor


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_read_file(temp_project):
    """Test reading file"""
    executor = FileExecutor(temp_project)

    # Create test file
    test_file = Path(temp_project) / "test.txt"
    test_file.write_text("Hello, World!")

    result = executor.read_file("test.txt")

    assert result["success"] is True
    assert result["content"] == "Hello, World!"
    assert result["size"] == 13


def test_write_file(temp_project):
    """Test writing file"""
    executor = FileExecutor(temp_project)

    result = executor.write_file("new_file.txt", "Test content")

    assert result["success"] is True
    assert Path(temp_project, "new_file.txt").exists()
    assert Path(temp_project, "new_file.txt").read_text() == "Test content"


def test_write_file_with_backup(temp_project):
    """Test writing file with backup"""
    executor = FileExecutor(temp_project)

    # Create original file
    test_file = Path(temp_project) / "test.txt"
    test_file.write_text("Original content")

    # Write new content
    result = executor.write_file("test.txt", "New content", create_backup=True)

    assert result["success"] is True
    assert "Backup created" in result["backup"]
    assert test_file.read_text() == "New content"


def test_edit_file(temp_project):
    """Test editing file"""
    executor = FileExecutor(temp_project)

    # Create test file
    test_file = Path(temp_project) / "test.txt"
    test_file.write_text("Hello, World!")

    result = executor.edit_file("test.txt", {"World": "Python"})

    assert result["success"] is True
    assert test_file.read_text() == "Hello, Python!"


def test_delete_file(temp_project):
    """Test deleting file"""
    executor = FileExecutor(temp_project)

    # Create test file
    test_file = Path(temp_project) / "test.txt"
    test_file.write_text("Test content")

    result = executor.delete_file("test.txt", create_backup=True)

    assert result["success"] is True
    assert not test_file.exists()


def test_list_files(temp_project):
    """Test listing files"""
    executor = FileExecutor(temp_project)

    # Create test files
    Path(temp_project, "file1.py").write_text("# Python")
    Path(temp_project, "file2.py").write_text("# Python")
    Path(temp_project, "file3.txt").write_text("Text")

    result = executor.list_files(".", pattern="*.py")

    assert result["success"] is True
    assert len(result["files"]) == 2
    assert "file1.py" in result["files"]
    assert "file2.py" in result["files"]


def test_path_validation_outside_project(temp_project):
    """Test path validation prevents access outside project"""
    executor = FileExecutor(temp_project)

    with pytest.raises(ValueError):
        executor._validate_path("../../etc/passwd")


def test_read_nonexistent_file(temp_project):
    """Test reading non-existent file"""
    executor = FileExecutor(temp_project)

    result = executor.read_file("nonexistent.txt")

    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_edit_file_text_not_found(temp_project):
    """Test editing file with text not found"""
    executor = FileExecutor(temp_project)

    # Create test file
    test_file = Path(temp_project) / "test.txt"
    test_file.write_text("Hello, World!")

    result = executor.edit_file("test.txt", {"NotFound": "Replacement"})

    assert result["success"] is False
    assert "not found" in result["error"].lower()


def test_create_nested_directories(temp_project):
    """Test creating nested directories"""
    executor = FileExecutor(temp_project)

    result = executor.write_file("src/nested/deep/file.py", "# Python code")

    assert result["success"] is True
    assert Path(temp_project, "src/nested/deep/file.py").exists()
