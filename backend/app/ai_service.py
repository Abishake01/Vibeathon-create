import json
import os
from typing import Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=GROQ_API_KEY)


def get_remaining_tokens() -> Dict[str, int]:
    """
    Get remaining tokens from Groq API.
    Note: Groq API doesn't provide direct token usage endpoint,
    so we'll track usage manually or return estimated limits.
    """
    # Groq free tier typically has limits, but no direct API to check
    # We'll return a placeholder structure that can be updated
    return {
        "remaining": None,  # Will be calculated based on usage
        "limit": 30000,  # Example limit, adjust based on your plan
        "used": 0
    }


def generate_todo_list(prompt: str) -> List[Dict[str, any]]:
    """
    Generate a todo list for project creation based on user prompt.
    Returns a list of tasks with descriptions.
    """
    system_prompt = """You are a project planning assistant. Based on a user's request to create a webpage, generate a detailed todo list of tasks needed to complete the project.

Return ONLY a valid JSON object with this structure:
{
  "todos": [
    {
      "id": 1,
      "task": "Task description",
      "completed": false
    }
  ]
}

Include 5-8 tasks covering:
1. Project structure setup
2. HTML structure creation
3. CSS styling and design
4. JavaScript functionality
5. Responsive design
6. Testing and refinement

Do not include any markdown formatting or explanations. Only return the raw JSON object."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a todo list for: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON
        data = json.loads(content)
        
        # Handle both array and object with array
        if isinstance(data, dict) and "todos" in data:
            todos = data["todos"]
        elif isinstance(data, list):
            todos = data
        else:
            # Default todo list if parsing fails
            todos = [
                {"id": 1, "task": "Set up project structure", "completed": False},
                {"id": 2, "task": "Create HTML structure", "completed": False},
                {"id": 3, "task": "Design CSS styling", "completed": False},
                {"id": 4, "task": "Add JavaScript functionality", "completed": False},
                {"id": 5, "task": "Make responsive design", "completed": False},
            ]
        
        return todos
    
    except Exception as e:
        # Return default todo list on error
        return [
            {"id": 1, "task": "Set up project structure", "completed": False},
            {"id": 2, "task": "Create HTML structure", "completed": False},
            {"id": 3, "task": "Design CSS styling", "completed": False},
            {"id": 4, "task": "Add JavaScript functionality", "completed": False},
            {"id": 5, "task": "Make responsive design", "completed": False},
        ]


def generate_project_description(prompt: str) -> str:
    """Generate a project description based on user prompt."""
    system_prompt = """You are a web development assistant. Describe the project that will be created based on the user's request.

Provide a clear, concise description (2-3 sentences) of what the webpage will include and its key features."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        raise Exception(f"Error generating description: {str(e)}")


def generate_code_from_prompt(prompt: str, todo_list: List[Dict] = None) -> Dict[str, str]:
    """
    Generate HTML, CSS, and JavaScript code from a user prompt using Groq API.
    
    Returns a dictionary with 'html', 'css', and 'js' keys with properly formatted code.
    """
    system_prompt = """You are an expert web developer. Generate clean, modern, production-ready HTML, CSS, and JavaScript code.

CRITICAL REQUIREMENTS:
1. HTML must be properly formatted with correct indentation (2 spaces per level)
2. CSS must be properly formatted with correct indentation
3. JavaScript must be properly formatted with correct indentation
4. All code must be complete and functional
5. For coffee shop pages or similar: Create beautiful, modern UI with:
   - Hero section with compelling headline and call-to-action
   - Menu/features section with attractive cards
   - About section with story
   - Contact section with form
   - Responsive navigation bar
   - Modern color scheme (warm browns, creams, whites for coffee shops)
   - Smooth animations and transitions
   - Professional typography
   - Attractive buttons and interactive elements
6. Code must NOT be in paragraph format - it must be properly structured with line breaks
7. Use proper escaping for JSON (escape quotes, newlines as \\n)

IMPORTANT: The code strings in JSON should use \\n for newlines, not actual newlines.

Return ONLY a valid JSON object with this exact structure:
{
  "html": "<!DOCTYPE html>\\n<html>\\n  <head>...</head>\\n  <body>...</body>\\n</html>",
  "css": "body {\\n  margin: 0;\\n  padding: 0;\\n}",
  "js": "console.log('Hello');"
}

Do not include markdown code blocks, backticks, or explanations. Only return raw JSON."""

    try:
        # Build enhanced context
        context = f"""Create a beautiful, modern, production-ready webpage based on this request: {prompt}

Requirements:
- The page must look professional and visually appealing
- Use modern design principles (clean layouts, good spacing, attractive colors)
- Make it responsive for mobile and desktop
- Include smooth animations and transitions
- Use semantic HTML5 elements
- Write clean, maintainable CSS with modern features
- Add interactive JavaScript features
- For coffee shops: Use warm colors, elegant typography, and inviting design

Generate complete, working code with proper formatting. The code should be production-ready and look amazing."""
        
        if todo_list:
            context += f"\n\nTasks to complete: {', '.join([t.get('task', '') for t in todo_list])}"
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            # Try to extract JSON from code blocks
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
        
        # Clean up content
        content = content.strip()
        
        # Parse JSON
        try:
            code_data = json.loads(content)
        except json.JSONDecodeError as json_err:
            # Try to fix common JSON issues
            print(f"JSON parse error, attempting to fix: {json_err}")
            print(f"Content preview: {content[:500]}")
            # Try to extract JSON object manually
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                content = content[start_idx:end_idx+1]
                code_data = json.loads(content)
            else:
                raise
        
        # Validate structure
        if not all(key in code_data for key in ["html", "css", "js"]):
            raise ValueError("AI response missing required keys: html, css, js")
        
        # Ensure proper formatting - replace escaped newlines with actual newlines
        html_code = code_data["html"].replace("\\n", "\n")
        css_code = code_data["css"].replace("\\n", "\n")
        js_code = code_data["js"].replace("\\n", "\n")
        
        return {
            "html": html_code,
            "css": css_code,
            "js": js_code
        }
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Groq API: {str(e)}")


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
    return len(text) // 4
