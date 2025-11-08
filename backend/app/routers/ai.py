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
    detect_user_intent,
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
        # Step 0: Detect user intent
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Understanding your request...'})}\n\n"
        
        intent_result = detect_user_intent(prompt)
        intent_tokens = estimate_tokens(prompt)
        total_tokens_used += intent_tokens
        
        # If user doesn't want to create a webpage, return conversation/ideas response
        if intent_result["intent"] != "create_webpage":
            yield f"data: {json.dumps({'type': 'conversation', 'message': intent_result.get('response', 'How can I help you?'), 'intent': intent_result['intent']})}\n\n"
            return
        
        # Step 1: Generate todo list
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Analyzing requirements and creating plan...'})}\n\n"
        
        todo_list_data = generate_todo_list(prompt)
        todo_tokens = estimate_tokens(prompt + str(todo_list_data))
        total_tokens_used += todo_tokens
        
        # Stream todo list items one by one with typing effect
        todo_list = []
        for idx, item in enumerate(todo_list_data, 1):
            todo_item = {
                "id": item.get("id", idx),
                "task": item.get("task", ""),
                "completed": False
            }
            todo_list.append(todo_item)
            
            # Stream each todo item with typing animation
            task_text = todo_item["task"]
            for i in range(len(task_text) + 1):
                partial_task = task_text[:i]
                yield f"data: {json.dumps({'type': 'todo_typing', 'todo_id': todo_item['id'], 'partial_task': partial_task})}\n\n"
                await asyncio.sleep(0.03)  # Natural typing speed
            
            # Send complete todo item
            yield f"data: {json.dumps({'type': 'todo_item', 'todo': todo_item})}\n\n"
        
        yield f"data: {json.dumps({'type': 'todo_complete'})}\n\n"
        
        # Step 2: Generate project description
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Generating project description...'})}\n\n"
        
        description = generate_project_description(prompt)
        desc_tokens = estimate_tokens(prompt + description)
        total_tokens_used += desc_tokens
        
        yield f"data: {json.dumps({'type': 'description', 'description': description})}\n\n"
        
        # Step 3: Create project in database
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Setting up project structure...'})}\n\n"
        
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
        
        # Create project directory
        create_project_directory(project_id)
        
        # Step 4: Extract project requirements
        from app.ai_service import extract_project_requirements
        project_requirements = extract_project_requirements(prompt)
        req_tokens = estimate_tokens(prompt)
        total_tokens_used += req_tokens
        
        # Step 5: Complete tasks one by one and generate code per task
        completed_count = 0
        code_files = {"html": "", "css": "", "js": ""}
        
        for idx, todo in enumerate(todo_list, 1):
            yield f"data: {json.dumps({'type': 'task_start', 'task_id': todo['id'], 'task': todo['task']})}\n\n"
            
            # Generate code for each task separately
            if idx == len(todo_list):  # Last task - generate all code
                yield f"data: {json.dumps({'type': 'thinking', 'message': f'Generating beautiful, responsive code...'})}\n\n"
                
                try:
                    code_files = generate_code_from_prompt(prompt, todo_list_data, project_requirements)
                    
                    # Validate code was generated
                    if not code_files.get("html") or not code_files.get("css"):
                        raise ValueError("Code generation returned empty files")
                    
                    code_tokens = estimate_tokens(prompt + code_files["html"] + code_files["css"] + code_files["js"])
                    total_tokens_used += code_tokens
                    
                    # Save files
                    yield f"data: {json.dumps({'type': 'thinking', 'message': 'Saving files...'})}\n\n"
                    if code_files["html"]:
                        save_file(project_id, "index.html", code_files["html"])
                    if code_files["css"]:
                        save_file(project_id, "style.css", code_files["css"])
                    if code_files["js"]:
                        save_file(project_id, "script.js", code_files["js"])
                    
                    yield f"data: {json.dumps({'type': 'code_generated', 'message': 'Code files generated and saved successfully'})}\n\n"
                    
                except Exception as code_error:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Error generating code: {error_details}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Code generation failed: {str(code_error)}'})}\n\n"
                    raise
            
            # Mark todo as completed
            todo["completed"] = True
            completed_count += 1
            
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo['id'], 'completed_count': completed_count, 'total_tasks': len(todo_list)})}\n\n"
        
        # Step 6: Calculate efficiency
        # Estimate baseline tokens (what it would take without optimization)
        baseline_estimate = estimate_tokens(prompt) * 10  # Rough estimate
        efficiency_saved = max(0, baseline_estimate - total_tokens_used)
        efficiency_percent = (efficiency_saved / baseline_estimate * 100) if baseline_estimate > 0 else 0
        
        # Final response
        yield f"data: {json.dumps({'type': 'complete', 'project_id': project_id, 'todo_list': todo_list, 'description': description, 'efficiency_saved': int(efficiency_saved), 'efficiency_percent': round(efficiency_percent, 1), 'tokens_used': total_tokens_used})}\n\n"
        
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
