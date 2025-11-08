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
from app.ai_service_v2 import (
    detect_user_intent,
    generate_todo_list,
    generate_project_description,
    extract_project_requirements,
    generate_html_code,
    generate_css_code,
    generate_js_code,
    estimate_tokens
)
from app.ai_providers import get_provider
from app.file_handler import (
    create_project_directory,
    save_file,
    ALLOWED_FILES
)

router = APIRouter(prefix="/ai", tags=["ai"])


async def stream_project_creation(prompt: str, project_name: str, provider_name: str, db: Session):
    """Stream project creation with step-by-step updates - each task uses separate tokens."""
    project_id = None
    total_tokens_used = 0
    
    try:
        # Get AI provider
        try:
            provider = get_provider(provider_name)
        except Exception as provider_error:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to initialize {provider_name} provider: {str(provider_error)}'})}\n\n"
            return
        
        # Step 0: Detect user intent - separate token call
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Understanding your request...'})}\n\n"
        
        intent_result = detect_user_intent(prompt, provider)
        usage = intent_result.get("usage", {})
        total_tokens_used += usage.get("total_tokens", estimate_tokens(prompt))
        
        # If user doesn't want to create a webpage, return conversation/ideas response
        if intent_result.get("intent") != "create_webpage":
            yield f"data: {json.dumps({'type': 'conversation', 'message': intent_result.get('response', 'How can I help you?'), 'intent': intent_result.get('intent')})}\n\n"
            return
        
        # Step 1: Generate project description - separate token call
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Generating project description...'})}\n\n"
        
        description = generate_project_description(prompt, provider)
        total_tokens_used += estimate_tokens(prompt + description)
        
        yield f"data: {json.dumps({'type': 'description', 'description': description})}\n\n"
        
        # Step 2: Generate todo list - separate token call
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Creating detailed plan...'})}\n\n"
        
        todo_list_data = generate_todo_list(prompt, provider)
        total_tokens_used += estimate_tokens(prompt + str(todo_list_data))
        
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
        
        # Ensure project is fully committed before proceeding
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'type': 'project_created', 'project_id': project_id})}\n\n"
        
        # Create project directory
        create_project_directory(project_id)
        
        # Small delay to ensure directory is created
        await asyncio.sleep(0.2)
        
        # Mark "Project structure setup" task as complete
        if todo_list:
            todo_list[0]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[0]['id'], 'completed_count': 1, 'total_tasks': len(todo_list)})}\n\n"
        
        # Step 4: Extract project requirements - separate token call
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Analyzing design requirements...'})}\n\n"
        
        project_requirements = extract_project_requirements(prompt, provider)
        total_tokens_used += estimate_tokens(prompt)
        
        # Step 5: Generate HTML code - separate token call with delay
        yield f"data: {json.dumps({'type': 'task_start', 'task_id': 2, 'task': 'Creating HTML structure'})}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Analyzing requirements and generating HTML structure...'})}\n\n"
        await asyncio.sleep(2)  # Give time for analysis
        
        html_code = generate_html_code(prompt, project_requirements, provider)
        total_tokens_used += estimate_tokens(prompt + html_code)
        save_file(project_id, "index.html", html_code)
        
        if len(todo_list) > 1:
            todo_list[1]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[1]['id'], 'completed_count': 2, 'total_tasks': len(todo_list)})}\n\n"
        await asyncio.sleep(1)  # Delay before next task
        
        # Step 6: Generate CSS code - separate token call with delay
        yield f"data: {json.dumps({'type': 'task_start', 'task_id': 3, 'task': 'Designing CSS styling'})}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Creating beautiful, responsive CSS with animations and modern design...'})}\n\n"
        await asyncio.sleep(2)  # Give time for analysis
        
        css_code = generate_css_code(prompt, project_requirements, html_code, provider)
        total_tokens_used += estimate_tokens(prompt + css_code)
        save_file(project_id, "style.css", css_code)
        
        if len(todo_list) > 2:
            todo_list[2]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[2]['id'], 'completed_count': 3, 'total_tasks': len(todo_list)})}\n\n"
        await asyncio.sleep(1)  # Delay before next task
        
        # Step 7: Generate JavaScript code - separate token call with delay
        yield f"data: {json.dumps({'type': 'task_start', 'task_id': 4, 'task': 'Adding JavaScript functionality'})}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Implementing interactive JavaScript features...'})}\n\n"
        await asyncio.sleep(2)  # Give time for analysis
        
        js_code = generate_js_code(prompt, project_requirements, html_code, provider)
        total_tokens_used += estimate_tokens(prompt + js_code)
        save_file(project_id, "script.js", js_code)
        
        if len(todo_list) > 3:
            todo_list[3]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[3]['id'], 'completed_count': 4, 'total_tasks': len(todo_list)})}\n\n"
        
        # Mark remaining tasks as complete
        for idx in range(4, len(todo_list)):
            todo_list[idx]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[idx]['id'], 'completed_count': idx + 1, 'total_tasks': len(todo_list)})}\n\n"
        
        yield f"data: {json.dumps({'type': 'code_generated', 'message': 'All code files generated and saved successfully'})}\n\n"
        
        # Step 8: Calculate token info
        try:
            from app.ai_service import get_remaining_tokens
            token_info = get_remaining_tokens()
            token_limit = token_info.get("limit", 30000)
            remaining_tokens = token_limit - total_tokens_used if token_limit else None
        except:
            token_limit = 30000
            remaining_tokens = token_limit - total_tokens_used
        
        # Final response
        yield f"data: {json.dumps({'type': 'complete', 'project_id': project_id, 'todo_list': todo_list, 'description': description, 'tokens_used': total_tokens_used, 'token_limit': token_limit, 'remaining_tokens': remaining_tokens})}\n\n"
        
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
    provider_name = project_data.provider or "groq"
    
    return StreamingResponse(
        stream_project_creation(project_data.prompt, project_name, provider_name, db),
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
