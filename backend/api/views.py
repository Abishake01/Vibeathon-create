"""
Django views for the API endpoints.
"""
import json
import asyncio
import re
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project, User
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer, ProjectUpdateSerializer,
    ProjectFilesResponseSerializer, FileContentSerializer, FileResponseSerializer,
    FileUpdateSerializer, AIProjectCreateSerializer, TokenInfoSerializer
)
from .utils import (
    create_project_directory, save_file, get_file, get_all_files,
    delete_project_files, ALLOWED_FILES
)
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).resolve().parent.parent / 'app'
sys.path.insert(0, str(app_dir))

from ai_service_v2 import (
    detect_user_intent, generate_todo_list, generate_project_description,
    extract_project_requirements, generate_code_with_streaming, estimate_tokens
)
from design_references import (
    get_design_reference, detect_design_type_from_prompt
)
from ai_providers import get_provider
from ai_service import get_remaining_tokens


# Projects endpoints
@api_view(['POST'])
def create_project(request):
    """Create a new project. No authentication required."""
    serializer = ProjectCreateSerializer(data=request.data)
    if serializer.is_valid():
        project = Project.objects.create(
            user_id=None,
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description')
        )
        
        # Create project directory and initialize empty files
        create_project_directory(project.id)
        for filename in ALLOWED_FILES.keys():
            save_file(project.id, filename, "")
        
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_projects(request):
    """List all projects. No authentication required."""
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_project(request, project_id):
    """Get a specific project by ID. No authentication required."""
    import time
    
    # Try up to 3 times with increasing delays (handles race conditions)
    project = None
    for attempt in range(3):
        try:
            project = Project.objects.get(id=project_id)
            break
        except Project.DoesNotExist:
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    
    if not project:
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ProjectSerializer(project)
    return Response(serializer.data)


@api_view(['PATCH'])
def update_project(request, project_id):
    """Update project metadata. No authentication required."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ProjectUpdateSerializer(data=request.data)
    if serializer.is_valid():
        if 'name' in serializer.validated_data:
            project.name = serializer.validated_data['name']
        if 'description' in serializer.validated_data:
            project.description = serializer.validated_data['description']
        project.save()
        
        return Response(ProjectSerializer(project).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_project(request, project_id):
    """Delete a project and all its files. No authentication required."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Delete project files
    delete_project_files(project_id)
    
    # Delete project from database
    project.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_project_files(request, project_id):
    """Get all files (HTML, CSS, JS) for a project. No authentication required."""
    import time
    
    # Try up to 3 times with increasing delays (handles race conditions)
    project = None
    for attempt in range(3):
        try:
            project = Project.objects.get(id=project_id)
            break
        except Project.DoesNotExist:
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    
    # Even if project not found in DB, try to get files if they exist on disk
    files = get_all_files(project_id)
    
    # If we have files, return them even if project not in DB yet (race condition)
    if files and any(files.values()):
        file_list = [
            {"filename": filename, "content": content}
            for filename, content in files.items()
        ]
        
        return Response({
            "project_id": project_id,
            "files": file_list
        })
    
    # If no project and no files, return 404
    if not project:
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Project exists but no files yet - return empty files
    file_list = [
        {"filename": filename, "content": content}
        for filename, content in files.items()
    ]
    
    return Response({
        "project_id": project_id,
        "files": file_list
    })


@api_view(['GET'])
def get_file_content(request, project_id, filename):
    """Get a specific file content. No authentication required."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if filename not in ALLOWED_FILES:
        return Response(
            {"detail": f"Invalid filename. Allowed: {', '.join(ALLOWED_FILES.keys())}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    content = get_file(project_id, filename)
    if content is None:
        content = ""
    
    return Response({
        "filename": filename,
        "content": content,
        "project_id": project_id
    })


@api_view(['PUT'])
def update_file(request, project_id, filename):
    """Update a project file (HTML, CSS, or JS). No authentication required."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if filename not in ALLOWED_FILES:
        return Response(
            {"detail": f"Invalid filename. Allowed: {', '.join(ALLOWED_FILES.keys())}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = FileUpdateSerializer(data=request.data)
    if serializer.is_valid():
        content = serializer.validated_data['content']
        save_file(project_id, filename, content)
        
        return Response({
            "filename": filename,
            "content": content,
            "project_id": project_id
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@xframe_options_exempt
@api_view(['GET'])
def preview_project(request, project_id):
    """Render the project as a live preview (combine HTML, CSS, JS). No authentication required."""
    import time
    
    # Try up to 5 times with increasing delays
    project = None
    for attempt in range(5):
        try:
            project = Project.objects.get(id=project_id)
            break
        except Project.DoesNotExist:
            if attempt < 4:
                time.sleep(0.5 * (attempt + 1))
    
    if not project:
        # Even if project not found, try to serve files if they exist
        try:
            files = get_all_files(project_id)
            if files and any(files.values()):
                html_content = files.get("index.html", "")
                css_content = files.get("style.css", "")
                js_content = files.get("script.js", "")
                
                # Remove external CSS and JS links
                html_content = re.sub(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
                html_content = re.sub(r'<link[^>]*href=["\'][^"\']*\.css["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
                html_content = re.sub(r'<script[^>]*src=["\'][^"\']*\.js["\'][^>]*></script>', '', html_content, flags=re.IGNORECASE)
                html_content = re.sub(r'<script[^>]*src=["\'][^"\']*["\'][^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
                
                # Combine and serve
                if "<!DOCTYPE html>" not in html_content and "<html" not in html_content:
                    preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
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
                    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
                    if "</head>" in html_content:
                        html_content = html_content.replace("</head>", f"<style>\n{css_content}\n</style>\n</head>")
                    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
                    if "</body>" in html_content:
                        html_content = html_content.replace("</body>", f"<script>\n{js_content}\n</script>\n</body>")
                    preview_html = html_content
                
                response = HttpResponse(preview_html, content_type='text/html')
                response['Access-Control-Allow-Origin'] = '*'
                return response
        except:
            pass
        
        return Response(
            {"detail": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    files = get_all_files(project_id)
    
    html_content = files.get("index.html", "")
    css_content = files.get("style.css", "")
    js_content = files.get("script.js", "")
    
    # Remove external CSS and JS links
    html_content = re.sub(r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<link[^>]*href=["\'][^"\']*\.css["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<script[^>]*src=["\'][^"\']*\.js["\'][^>]*></script>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<script[^>]*src=["\'][^"\']*["\'][^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Combine HTML, CSS, and JS into a single HTML document
    if "<!DOCTYPE html>" not in html_content and "<html" not in html_content:
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
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", f"<style>\n{css_content}\n</style>\n</head>")
        elif "<head>" in html_content:
            html_content = html_content.replace("<head>", f"<head>\n<style>\n{css_content}\n</style>")
        else:
            html_content = f"<style>\n{css_content}\n</style>\n{html_content}"
        
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"<script>\n{js_content}\n</script>\n</body>")
        else:
            html_content = f"{html_content}\n<script>\n{js_content}\n</script>"
        
        preview_html = html_content
    
    response = HttpResponse(preview_html, content_type='text/html')
    response['Access-Control-Allow-Origin'] = '*'
    return response


# Health check
@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "healthy"})


# AI endpoints
async def stream_project_creation(prompt: str, project_name: str, provider_name: str):
    """Stream project creation with step-by-step updates."""
    from asgiref.sync import sync_to_async
    
    project_id = None
    total_tokens_used = 0
    
    try:
        # Get AI provider
        try:
            provider = get_provider(provider_name)
        except Exception as provider_error:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to initialize {provider_name} provider: {str(provider_error)}'})}\n\n"
            return
        
        # Step 0: Detect user intent
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Understanding your request...'})}\n\n"
        
        intent_result = detect_user_intent(prompt, provider)
        usage = intent_result.get("usage", {})
        total_tokens_used += usage.get("total_tokens", estimate_tokens(prompt))
        
        if intent_result.get("intent") != "create_webpage":
            yield f"data: {json.dumps({'type': 'conversation', 'message': intent_result.get('response', 'How can I help you?'), 'intent': intent_result.get('intent')})}\n\n"
            return
        
        # Step 1: Generate project description
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Generating project description...'})}\n\n"
        
        description = generate_project_description(prompt, provider)
        total_tokens_used += estimate_tokens(prompt + description)
        
        yield f"data: {json.dumps({'type': 'description', 'description': description})}\n\n"
        
        # Step 2: Generate todo list
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Creating detailed plan...'})}\n\n"
        
        todo_list_data = generate_todo_list(prompt, provider)
        total_tokens_used += estimate_tokens(prompt + str(todo_list_data))
        
        todo_list = []
        for idx, item in enumerate(todo_list_data, 1):
            todo_item = {
                "id": item.get("id", idx),
                "task": item.get("task", ""),
                "completed": False
            }
            todo_list.append(todo_item)
            
            task_text = todo_item["task"]
            for i in range(len(task_text) + 1):
                partial_task = task_text[:i]
                yield f"data: {json.dumps({'type': 'todo_typing', 'todo_id': todo_item['id'], 'partial_task': partial_task})}\n\n"
                await asyncio.sleep(0.03)
            
            yield f"data: {json.dumps({'type': 'todo_item', 'todo': todo_item})}\n\n"
        
        yield f"data: {json.dumps({'type': 'todo_complete'})}\n\n"
        
        # Step 3: Create project in database
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Setting up project structure...'})}\n\n"
        
        # Use sync_to_async to wrap Django ORM call
        def create_project_sync():
            return Project.objects.create(
                user_id=None,
                name=project_name,
                description=description
            )
        
        create_project_async = sync_to_async(create_project_sync)
        project = await create_project_async()
        project_id = project.id
        
        await asyncio.sleep(0.3)
        
        yield f"data: {json.dumps({'type': 'project_created', 'project_id': project_id})}\n\n"
        
        create_project_directory(project_id)
        await asyncio.sleep(0.2)
        
        if todo_list:
            todo_list[0]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[0]['id'], 'completed_count': 1, 'total_tasks': len(todo_list)})}\n\n"
        
        # Step 4: Extract project requirements
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Analyzing design requirements deeply...'})}\n\n"
        await asyncio.sleep(5)
        
        project_requirements = extract_project_requirements(prompt, provider)
        total_tokens_used += estimate_tokens(prompt)
        
        design_type = detect_design_type_from_prompt(prompt)
        if design_type:
            design_ref = get_design_reference(design_type)
            if design_ref:
                project_requirements["design_reference"] = design_type
                project_requirements["design_description"] = design_ref.get("description", "")
                project_requirements["design_colors"] = design_ref.get("color_scheme", [])
        
        # Step 5: Generate HTML code
        yield f"data: {json.dumps({'type': 'task_start', 'task_id': 2, 'task': 'Creating HTML structure'})}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Deeply analyzing requirements and generating beautiful HTML structure...'})}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps({'type': 'code_start', 'file': 'index.html'})}\n\n"
        await asyncio.sleep(0.3)
        html_code = ""
        async for line in generate_code_with_streaming(prompt, project_requirements, "", provider, "html"):
            html_code += line
            yield f"data: {json.dumps({'type': 'code_line', 'file': 'index.html', 'line': line})}\n\n"
        
        html_tokens = estimate_tokens(prompt + html_code)
        total_tokens_used += html_tokens
        try:
            token_info = get_remaining_tokens()
            token_limit = token_info.get("limit", 30000)
            remaining_tokens = token_limit - total_tokens_used if token_limit else None
            yield f"data: {json.dumps({'type': 'tokens_update', 'remaining_tokens': remaining_tokens, 'token_limit': token_limit})}\n\n"
        except:
            pass
        
        save_file(project_id, "index.html", html_code)
        yield f"data: {json.dumps({'type': 'code_complete', 'file': 'index.html', 'content': html_code, 'file_size': len(html_code)})}\n\n"
        
        wait_time = min(2 + (len(html_code) / 1000), 5)
        await asyncio.sleep(wait_time)
        
        if len(todo_list) > 1:
            todo_list[1]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[1]['id'], 'completed_count': 2, 'total_tasks': len(todo_list)})}\n\n"
        await asyncio.sleep(2)
        
        # Step 6: Generate CSS code
        yield f"data: {json.dumps({'type': 'task_start', 'task_id': 3, 'task': 'Designing CSS styling'})}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Creating beautiful, responsive CSS with animations and modern design...'})}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps({'type': 'code_start', 'file': 'style.css'})}\n\n"
        await asyncio.sleep(0.3)
        css_code = ""
        async for line in generate_code_with_streaming(prompt, project_requirements, html_code, provider, "css"):
            css_code += line
            yield f"data: {json.dumps({'type': 'code_line', 'file': 'style.css', 'line': line})}\n\n"
        
        css_tokens = estimate_tokens(prompt + css_code)
        total_tokens_used += css_tokens
        try:
            token_info = get_remaining_tokens()
            token_limit = token_info.get("limit", 30000)
            remaining_tokens = token_limit - total_tokens_used if token_limit else None
            yield f"data: {json.dumps({'type': 'tokens_update', 'remaining_tokens': remaining_tokens, 'token_limit': token_limit})}\n\n"
        except:
            pass
        
        save_file(project_id, "style.css", css_code)
        yield f"data: {json.dumps({'type': 'code_complete', 'file': 'style.css', 'content': css_code, 'file_size': len(css_code)})}\n\n"
        
        wait_time = min(2 + (len(css_code) / 1000), 5)
        await asyncio.sleep(wait_time)
        
        if len(todo_list) > 2:
            todo_list[2]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[2]['id'], 'completed_count': 3, 'total_tasks': len(todo_list)})}\n\n"
        await asyncio.sleep(2)
        
        # Step 7: Generate JavaScript code
        yield f"data: {json.dumps({'type': 'task_start', 'task_id': 4, 'task': 'Adding JavaScript functionality'})}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'message': 'Implementing interactive JavaScript features...'})}\n\n"
        await asyncio.sleep(8)
        
        yield f"data: {json.dumps({'type': 'code_start', 'file': 'script.js'})}\n\n"
        await asyncio.sleep(0.3)
        js_code = ""
        async for line in generate_code_with_streaming(prompt, project_requirements, html_code, provider, "js"):
            js_code += line
            yield f"data: {json.dumps({'type': 'code_line', 'file': 'script.js', 'line': line})}\n\n"
        
        js_tokens = estimate_tokens(prompt + js_code)
        total_tokens_used += js_tokens
        try:
            token_info = get_remaining_tokens()
            token_limit = token_info.get("limit", 30000)
            remaining_tokens = token_limit - total_tokens_used if token_limit else None
            yield f"data: {json.dumps({'type': 'tokens_update', 'remaining_tokens': remaining_tokens, 'token_limit': token_limit})}\n\n"
        except:
            pass
        
        save_file(project_id, "script.js", js_code)
        yield f"data: {json.dumps({'type': 'code_complete', 'file': 'script.js', 'content': js_code, 'file_size': len(js_code)})}\n\n"
        
        wait_time = min(2 + (len(js_code) / 1000), 5)
        await asyncio.sleep(wait_time)
        
        if len(todo_list) > 3:
            todo_list[3]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[3]['id'], 'completed_count': 4, 'total_tasks': len(todo_list)})}\n\n"
        
        for idx in range(4, len(todo_list)):
            todo_list[idx]["completed"] = True
            yield f"data: {json.dumps({'type': 'task_complete', 'task_id': todo_list[idx]['id'], 'completed_count': idx + 1, 'total_tasks': len(todo_list)})}\n\n"
        
        yield f"data: {json.dumps({'type': 'code_generated', 'message': 'All code files generated and saved successfully'})}\n\n"
        
        try:
            token_info = get_remaining_tokens()
            token_limit = token_info.get("limit", 30000)
            remaining_tokens = token_limit - total_tokens_used if token_limit else None
        except:
            token_limit = 30000
            remaining_tokens = token_limit - total_tokens_used
        
        yield f"data: {json.dumps({'type': 'complete', 'project_id': project_id, 'todo_list': todo_list, 'description': description, 'tokens_used': total_tokens_used, 'token_limit': token_limit, 'remaining_tokens': remaining_tokens})}\n\n"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in stream: {error_details}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@csrf_exempt
@api_view(['POST'])
def create_project_with_ai_stream(request):
    """Create a project using AI with streaming responses."""
    try:
        serializer = AIProjectCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = serializer.validated_data['prompt']
        if not prompt or not prompt.strip():
            return Response(
                {"detail": "Prompt is required and cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project_name = serializer.validated_data.get('name') or prompt[:50]
        provider_name = serializer.validated_data.get('provider', 'ollama')
    except Exception as e:
        print(f"Error parsing request: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {"detail": f"Error parsing request: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Use asyncio to run the async generator
    import asyncio
    
    def run_async_generator():
        """Run async generator in a new event loop."""
        # Create a new event loop for this thread
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            gen = stream_project_creation(prompt, project_name, provider_name)
            
            while True:
                try:
                    # Get next chunk from async generator
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
                except Exception as e:
                    print(f"Error in async generator: {e}")
                    import traceback
                    traceback.print_exc()
                    # Send error to client
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                    break
        except Exception as e:
            print(f"Error setting up async generator: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to start stream: {str(e)}'})}\n\n"
        finally:
            if loop:
                try:
                    loop.close()
                except:
                    pass
    
    response = StreamingHttpResponse(
        run_async_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    # Note: 'Connection: keep-alive' is not allowed in WSGI - removed
    response['X-Accel-Buffering'] = 'no'
    return response


@api_view(['GET'])
def get_token_info(request):
    """Get remaining token information. No authentication required."""
    token_info = get_remaining_tokens()
    serializer = TokenInfoSerializer(token_info)
    return Response(serializer.data)


@api_view(['GET'])
def test_imports(request):
    """Test if all imports work correctly."""
    try:
        # Add app directory to path
        app_dir = Path(__file__).resolve().parent.parent / 'app'
        sys.path.insert(0, str(app_dir))
        
        from ai_providers import get_provider
        from ai_service import get_remaining_tokens
        
        return Response({
            "status": "success",
            "message": "All imports successful",
            "app_dir": str(app_dir),
            "app_dir_exists": app_dir.exists()
        })
    except Exception as e:
        import traceback
        return Response({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

