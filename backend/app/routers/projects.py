from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project
from app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectFilesResponse,
    FileContent,
    FileUpdate,
    FileResponse
)
from app.file_handler import (
    create_project_directory,
    save_file,
    get_file,
    get_all_files,
    delete_project_files,
    ALLOWED_FILES
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project. No authentication required."""
    project = Project(
        user_id=None,
        name=project_data.name,
        description=project_data.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Create project directory and initialize empty files
    create_project_directory(project.id)
    for filename in ALLOWED_FILES.keys():
        save_file(project.id, filename, "")
    
    return project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db)
):
    """List all projects. No authentication required."""
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific project by ID. No authentication required."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update project metadata. No authentication required."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Delete a project and all its files. No authentication required."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete project files
    delete_project_files(project_id)
    
    # Delete project from database
    db.delete(project)
    db.commit()
    
    return None


@router.get("/{project_id}/files", response_model=ProjectFilesResponse)
async def get_project_files(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get all files (HTML, CSS, JS) for a project. No authentication required."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    files = get_all_files(project_id)
    
    file_list = [
        FileContent(filename=filename, content=content)
        for filename, content in files.items()
    ]
    
    return ProjectFilesResponse(
        project_id=project_id,
        files=file_list
    )


@router.get("/{project_id}/files/{filename}", response_model=FileResponse)
async def get_file_content(
    project_id: str,
    filename: str,
    db: Session = Depends(get_db)
):
    """Get a specific file content. No authentication required."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if filename not in ALLOWED_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filename. Allowed: {', '.join(ALLOWED_FILES.keys())}"
        )
    
    content = get_file(project_id, filename)
    if content is None:
        content = ""
    
    return FileResponse(
        filename=filename,
        content=content,
        project_id=project_id
    )


@router.put("/{project_id}/files/{filename}", response_model=FileResponse)
async def update_file(
    project_id: str,
    filename: str,
    file_data: FileUpdate,
    db: Session = Depends(get_db)
):
    """Update a project file (HTML, CSS, or JS). No authentication required."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if filename not in ALLOWED_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filename. Allowed: {', '.join(ALLOWED_FILES.keys())}"
        )
    
    # Save the file
    save_file(project_id, filename, file_data.content)
    
    return FileResponse(
        filename=filename,
        content=file_data.content,
        project_id=project_id
    )


@router.get("/{project_id}/preview", response_class=HTMLResponse)
async def preview_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Render the project as a live preview (combine HTML, CSS, JS). No authentication required."""
    # Verify project exists - retry once if not found (handles race conditions)
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        # Retry once after a short delay (handles database commit timing)
        import asyncio
        await asyncio.sleep(0.2)
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    files = get_all_files(project_id)
    
    html_content = files.get("index.html", "")
    css_content = files.get("style.css", "")
    js_content = files.get("script.js", "")
    
    # Combine HTML, CSS, and JS into a single HTML document
    if "<!DOCTYPE html>" not in html_content and "<html" not in html_content:
        # Create a complete HTML document if HTML is just a fragment
        preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project.name}</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    {html_content}
    <script>
        {js_content}
    </script>
</body>
</html>"""
    else:
        # Inject CSS and JS into existing HTML
        # Try to inject CSS in head
        if "<style>" not in html_content and "</head>" in html_content:
            html_content = html_content.replace("</head>", f"<style>\n{css_content}\n</style>\n</head>")
        elif "<head>" in html_content:
            html_content = html_content.replace("<head>", f"<head>\n<style>\n{css_content}\n</style>")
        else:
            html_content = f"<style>\n{css_content}\n</style>\n{html_content}"
        
        # Try to inject JS before closing body tag
        if "<script>" not in html_content and "</body>" in html_content:
            html_content = html_content.replace("</body>", f"<script>\n{js_content}\n</script>\n</body>")
        elif "</body>" in html_content:
            html_content = html_content.replace("</body>", f"<script>\n{js_content}\n</script>\n</body>")
        else:
            html_content = f"{html_content}\n<script>\n{js_content}\n</script>"
        
        preview_html = html_content
    
    return HTMLResponse(content=preview_html)
