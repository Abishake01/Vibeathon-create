from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models import Project
from app.schemas import (
    ChatMessage,
    AIProjectCreate,
    AIProjectResponse,
    TodoItem,
    TokenInfo,
    ProjectResponse
)
from app.ai_service import (
    generate_todo_list,
    generate_project_description,
    generate_code_from_prompt,
    get_remaining_tokens,
    estimate_tokens
)
from app.file_handler import (
    create_project_directory,
    save_file,
    ALLOWED_FILES
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/create-project", response_model=AIProjectResponse)
async def create_project_with_ai(
    project_data: AIProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a project using AI based on user prompt.
    Generates todo list, description, and code files.
    No authentication required.
    """
    try:
        # Generate todo list first
        todo_list_data = generate_todo_list(project_data.prompt)
        todo_list = [
            TodoItem(id=item.get("id", idx), task=item.get("task", ""), completed=False)
            for idx, item in enumerate(todo_list_data, 1)
        ]
        
        # Generate project description
        description = generate_project_description(project_data.prompt)
        
        # Create project in database (no user required)
        project_name = project_data.name or project_data.prompt[:50]
        project = Project(
            user_id=str(uuid.uuid4()),  # Use dummy user ID
            name=project_name,
            description=description
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create project directory
        create_project_directory(project.id)
        
        # Generate code for each completed task (simulate progress)
        # In a real implementation, you might want to stream this
        completed_todos = []
        for todo in todo_list:
            # Simulate task completion and code generation
            # For now, generate all code at once, but you could do it incrementally
            pass
        
        # Generate all code files
        code_files = generate_code_from_prompt(project_data.prompt, todo_list_data)
        
        # Save files
        save_file(project.id, "index.html", code_files["html"])
        save_file(project.id, "style.css", code_files["css"])
        save_file(project.id, "script.js", code_files["js"])
        
        # Mark all todos as completed
        completed_todos = [
            TodoItem(id=todo.id, task=todo.task, completed=True)
            for todo in todo_list
        ]
        
        # Estimate token usage
        total_text = project_data.prompt + description + code_files["html"] + code_files["css"] + code_files["js"]
        estimated_tokens = estimate_tokens(total_text)
        token_info = get_remaining_tokens()
        remaining = token_info["limit"] - estimated_tokens if token_info["limit"] else None
        
        return AIProjectResponse(
            project_id=project.id,
            todo_list=completed_todos,
            description=description,
            remaining_tokens=remaining
        )
    
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating project: {error_details}")  # Log full error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}"
        )


@router.get("/tokens", response_model=TokenInfo)
async def get_token_info():
    """Get remaining token information. No authentication required."""
    return get_remaining_tokens()

