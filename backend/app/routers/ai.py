from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
import json
import asyncio

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


async def stream_project_creation(prompt: str, project_name: str, db: Session):
    """Stream project creation with step-by-step updates."""
    project_id = None
    total_tokens_used = 0
    
    try:
        # Step 1: Generate todo list (streaming)
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Analyzing your request...'})}\n\n"
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Creating todo list...'})}\n\n"
        await asyncio.sleep(0.3)
        
        todo_list_data = generate_todo_list(prompt)
        todo_tokens = estimate_tokens(prompt + str(todo_list_data))
        total_tokens_used += todo_tokens
        
        # Stream todo list items one by one
        todo_list = []
        for idx, item in enumerate(todo_list_data, 1):
            todo_item = {
                "id": item.get("id", idx),
                "task": item.get("task", ""),
                "completed": False
            }
            todo_list.append(todo_item)
            
            # Stream each todo item
            yield f"data: {json.dumps({'type': 'todo_item', 'todo': todo_item})}\n\n"
            await asyncio.sleep(0.2)  # Typing delay
        
        yield f"data: {json.dumps({'type': 'todo_complete'})}\n\n"
        await asyncio.sleep(0.3)
        
        # Step 2: Generate project description
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Generating project description...'})}\n\n"
        await asyncio.sleep(0.3)
        
        description = generate_project_description(prompt)
        desc_tokens = estimate_tokens(prompt + description)
        total_tokens_used += desc_tokens
        
        yield f"data: {json.dumps({'type': 'description', 'description': description})}\n\n"
        await asyncio.sleep(0.3)
        
        # Step 3: Create project in database
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Setting up project structure...'})}\n\n"
        await asyncio.sleep(0.2)
        
        project = Project(
            user_id=None,
            name=project_name,
            description=description
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        project_id = project.id
        
        yield f"data: {json.dumps({'type': 'project_created', 'project_id': project_id})}\n\n"
        await asyncio.sleep(0.2)
        
        # Create project directory
        create_project_directory(project_id)
        
        # Step 4: Complete tasks one by one and generate code
        completed_count = 0
        for idx, todo in enumerate(todo_list, 1):
            yield f"data: {json.dumps({'type': 'task_start', 'task_id': todo['id'], 'task': todo['task']})}\n\n"
            await asyncio.sleep(0.3)
            
            # Generate code for this task (or all at once for now)
            if idx == len(todo_list):  # Last task - generate all code
                yield f"data: {json.dumps({'type': 'thinking', 'message': f'Generating code for: {todo["task"]}...'})}\n\n"
                await asyncio.sleep(0.3)
                
                code_files = generate_code_from_prompt(prompt, todo_list_data)
                code_tokens = estimate_tokens(prompt + code_files["html"] + code_files["css"] + code_files["js"])
                total_tokens_used += code_tokens
                
                # Save files
                yield f"data: {json.dumps({'type': 'thinking', 'message': 'Saving HTML file...'})}\n\n"
                await asyncio.sleep(0.2)
                save_file(project_id, "index.html", code_files["html"])
                
                yield f"data: {json.dumps({'type': 'thinking', 'message': 'Saving CSS file...'})}\n\n"
                await asyncio.sleep(0.2)
                save_file(project_id, "style.css", code_files["css"])
                
                yield f"data: {json.dumps({'type': 'thinking', 'message': 'Saving JavaScript file...'})}\n\n"
                await asyncio.sleep(0.2)
                save_file(project_id, "script.js", code_files["js"])
            
            # Mark todo as completed
            todo["completed"] = True
            completed_count += 1
            
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo['id'], 'completed_count': completed_count, 'total_tasks': len(todo_list)})}\n\n"
            await asyncio.sleep(0.3)
        
        # Step 5: Calculate remaining tokens
        token_info = get_remaining_tokens()
        remaining = token_info["limit"] - total_tokens_used if token_info["limit"] else None
        
        # Final response
        yield f"data: {json.dumps({'type': 'complete', 'project_id': project_id, 'todo_list': todo_list, 'description': description, 'remaining_tokens': remaining, 'tokens_used': total_tokens_used})}\n\n"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in stream: {error_details}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        if project_id:
            db.rollback()


@router.post("/create-project-stream")
async def create_project_with_ai_stream(
    project_data: AIProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a project using AI with streaming responses.
    Shows todo list generation, task completion, and code generation in real-time.
    """
    project_name = project_data.name or project_data.prompt[:50]
    
    return StreamingResponse(
        stream_project_creation(project_data.prompt, project_name, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/create-project", response_model=AIProjectResponse)
async def create_project_with_ai(
    project_data: AIProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a project using AI based on user prompt (non-streaming version).
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
            user_id=None,
            name=project_name,
            description=description
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Create project directory
        create_project_directory(project.id)
        
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
