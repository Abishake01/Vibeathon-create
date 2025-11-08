import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

PROJECTS_DIR = os.getenv("PROJECTS_DIR", "./projects")

# Allowed file types
ALLOWED_FILES = {
    "index.html": "html",
    "style.css": "css",
    "script.js": "js"
}


def ensure_projects_dir():
    """Ensure the projects directory exists."""
    Path(PROJECTS_DIR).mkdir(parents=True, exist_ok=True)


def get_project_dir(project_id: str) -> Path:
    """Get the directory path for a specific project."""
    ensure_projects_dir()
    return Path(PROJECTS_DIR) / project_id


def create_project_directory(project_id: str) -> Path:
    """Create a directory for a project."""
    project_dir = get_project_dir(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def save_file(project_id: str, filename: str, content: str) -> None:
    """
    Save a file for a project.
    
    Args:
        project_id: Unique project identifier
        filename: Name of the file (index.html, style.css, or script.js)
        content: File content
    """
    if filename not in ALLOWED_FILES:
        raise ValueError(f"Invalid filename. Allowed: {', '.join(ALLOWED_FILES.keys())}")
    
    project_dir = create_project_directory(project_id)
    file_path = project_dir / filename
    file_path.write_text(content, encoding="utf-8")


def get_file(project_id: str, filename: str) -> Optional[str]:
    """
    Read a project file.
    
    Returns:
        File content or None if file doesn't exist
    """
    if filename not in ALLOWED_FILES:
        raise ValueError(f"Invalid filename. Allowed: {', '.join(ALLOWED_FILES.keys())}")
    
    project_dir = get_project_dir(project_id)
    file_path = project_dir / filename
    
    if not file_path.exists():
        return None
    
    return file_path.read_text(encoding="utf-8")


def get_all_files(project_id: str) -> Dict[str, str]:
    """
    Read all project files and return their content.
    
    Returns:
        Dictionary with filename as key and content as value
    """
    files = {}
    for filename in ALLOWED_FILES.keys():
        content = get_file(project_id, filename)
        files[filename] = content if content is not None else ""
    return files


def delete_project_files(project_id: str) -> None:
    """Delete all files for a project."""
    project_dir = get_project_dir(project_id)
    if project_dir.exists():
        import shutil
        shutil.rmtree(project_dir)


def file_exists(project_id: str, filename: str) -> bool:
    """Check if a file exists for a project."""
    if filename not in ALLOWED_FILES:
        return False
    
    project_dir = get_project_dir(project_id)
    file_path = project_dir / filename
    return file_path.exists()

