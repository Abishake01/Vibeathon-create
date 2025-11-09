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


def detect_user_intent(prompt: str) -> Dict[str, any]:
    """
    Detect user intent from the prompt.
    Returns: {
        "intent": "create_webpage" | "conversation" | "ideas",
        "confidence": float,
        "response": str (if conversation or ideas)
    }
    """
    system_prompt = """You are an intent detection assistant. Analyze user messages and determine their intent.

Possible intents:
1. "create_webpage" - User wants to create/build a webpage/website (e.g., "create a coffee shop page", "make a portfolio", "build a landing page")
2. "conversation" - User is just chatting, greeting, or asking questions (e.g., "hi", "hello", "how are you", "what can you do")
3. "ideas" - User wants project ideas or suggestions (e.g., "give me ideas", "what should I build", "suggest a project")

Return ONLY a valid JSON object:
{
  "intent": "create_webpage" | "conversation" | "ideas",
  "confidence": 0.0-1.0,
  "response": "Your response to the user (only if intent is conversation or ideas)"
}

If intent is "conversation", provide a friendly, helpful response.
If intent is "ideas", provide creative project ideas.
You are a webpage designer and developer, You will provide a better UI with responsive, modern, and clean design.
The design should be based on the user's request and the design reference provided. 
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
        
        data = json.loads(content)
        return data
    
    except Exception as e:
        # Default to conversation if detection fails
        return {
            "intent": "conversation",
            "confidence": 0.5,
            "response": "I'm here to help you create webpages! Try saying something like 'create a coffee shop page' to get started."
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


def extract_project_requirements(prompt: str) -> Dict[str, any]:
    """Extract theme, colors, and project type from user prompt."""
    system_prompt = """Analyze the user's request and extract:
1. Project type (todo list, coffee shop, portfolio, landing page, etc.)
2. Theme preferences (dark, light, modern, vintage, etc.)
3. Color preferences (specific colors mentioned)
4. Required JavaScript functions needed
5. Design with proper UI and responsive design. Like Bolt.new.

Return JSON: {"project_type": "...", "theme": "...", "colors": ["..."], "js_functions": ["..."]}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        return json.loads(content)
    except:
        return {"project_type": "webpage", "theme": "modern", "colors": [], "js_functions": []}


def generate_code_from_prompt(prompt: str, todo_list: List[Dict] = None, project_requirements: Dict = None) -> Dict[str, str]:
    """
    Generate HTML, CSS, and JavaScript code from a user prompt using Groq API.
    
    Returns a dictionary with 'html', 'css', and 'js' keys with properly formatted code.
    """
    # Extract project requirements
    if not project_requirements:
        project_requirements = extract_project_requirements(prompt)
    
    project_type = project_requirements.get("project_type", "webpage")
    theme = project_requirements.get("theme", "modern")
    colors = project_requirements.get("colors", [])
    js_functions = project_requirements.get("js_functions", [])
    
    # Determine required JS functions based on project type
    if "todo" in project_type.lower() or "task" in project_type.lower():
        js_functions.extend(["addTask", "deleteTask", "toggleCheckbox", "saveToLocalStorage", "loadFromLocalStorage"])
    elif "calculator" in project_type.lower():
        js_functions.extend(["calculate", "clear", "handleInput"])
    elif "form" in project_type.lower() or "contact" in project_type.lower():
        js_functions.extend(["validateForm", "submitForm", "resetForm"])
    
    # Build color scheme
    color_scheme = ""
    if colors:
        color_scheme = f"\nUser requested colors: {', '.join(colors)}. Use these colors as the primary palette."
    elif theme:
        if theme.lower() == "dark":
            color_scheme = "\nUse a dark theme with colors like #1a1a1a, #2d2d2d, #ffffff, #4a9eff"
        elif theme.lower() == "light":
            color_scheme = "\nUse a light theme with colors like #ffffff, #f5f5f5, #333333, #007bff"
        elif "coffee" in prompt.lower():
            color_scheme = "\nUse warm coffee shop colors: #8B4513 (saddle brown), #D2691E (chocolate), #F5F5DC (beige), #FFFFFF (white), #CD853F (peru)"
    
    system_prompt = """You are an expert web developer. Generate clean, modern, production-ready, FULLY RESPONSIVE HTML, CSS, and JavaScript code with ATTRACTIVE, ORIGINAL DESIGN.

CRITICAL REQUIREMENTS FOR PERFECT DESIGN:
1. HTML must be properly formatted with correct indentation (2 spaces per level)
2. CSS must be properly formatted with correct indentation and MUST BE FULLY RESPONSIVE
3. JavaScript must be properly formatted with correct indentation
4. All code must be complete, functional, and WORKING
5. DESIGN MUST BE ATTRACTIVE AND ORIGINAL - NOT GENERIC:
   - Use creative, modern layouts that stand out
   - Implement unique visual elements (gradients, shadows, animations)
   - Create professional, polished appearance like real websites
   - Use original color schemes and typography combinations
   - Add micro-interactions and smooth animations
6. RESPONSIVE DESIGN IS MANDATORY - MUST WORK PERFECTLY ON ALL DEVICES:
   - Use CSS media queries: @media (max-width: 768px) for mobile, @media (max-width: 1024px) for tablet
   - Use flexbox or CSS Grid for layouts (prefer Grid for complex layouts)
   - Make sure all elements scale properly on different screen sizes
   - Use relative units (rem, em, %, vw, vh) where appropriate
   - Navigation must work on mobile (hamburger menu if needed)
   - Images must be responsive (max-width: 100%, height: auto)
7. PERFECT ALIGNMENT AND LAYOUT:
   - Use CSS Grid or Flexbox for perfect alignment
   - Center content properly (use margin: 0 auto, or flexbox justify-content: center)
   - Use consistent spacing (padding, margin) throughout
   - Ensure text is readable and properly aligned
   - Use proper line-height and letter-spacing
7. BEAUTIFUL UI DESIGN:
   - For coffee shop pages: Use warm colors (#8B4513, #D2691E, #F5F5DC, #FFFFFF)
   - Use modern typography (Google Fonts: Playfair Display, Lato, Poppins, or similar)
   - Add smooth animations and transitions (hover effects, fade-ins, slide-ins)
   - Use shadows and borders for depth (box-shadow, border-radius)
   - Create attractive buttons with hover effects
   - Use gradients for backgrounds where appropriate
   - Ensure proper contrast for readability
9. JAVASCRIPT FUNCTIONALITY:
   - Implement ALL required functions based on project type
   - For todo list projects: addTask(), deleteTask(), toggleCheckbox(), saveToLocalStorage(), loadFromLocalStorage()
   - Make functions work seamlessly with the UI
   - Add event listeners properly
   - Handle user interactions smoothly
10. STRUCTURE:
   - Hero section with compelling headline, subheading, and call-to-action buttons
   - Menu/features section with attractive cards in a responsive grid
   - About section with story and proper spacing
   - Contact section with form and location details
   - Responsive navigation bar that works on mobile
   - Footer with social links
11. Code must NOT be in paragraph format - it must be properly structured with line breaks
12. Include viewport meta tag in HTML head
13. Make sure CSS includes mobile-first responsive breakpoints
14. FOLLOW USER'S THEME AND COLOR PREFERENCES EXACTLY

IMPORTANT: The code strings in JSON should use \\n for newlines, not actual newlines.

Return ONLY a valid JSON object with this exact structure:
{
  "html": "<!DOCTYPE html>\\n<html lang=\\"en\\">\\n<head>\\n  <meta charset=\\"UTF-8\\">\\n  <meta name=\\"viewport\\" content=\\"width=device-width, initial-scale=1.0\\">\\n  <title>...</title>\\n</head>\\n<body>...</body>\\n</html>",
  "css": "* {\\n  margin: 0;\\n  padding: 0;\\n  box-sizing: border-box;\\n}\\n\\nbody {\\n  font-family: Arial, sans-serif;\\n}\\n\\n@media (max-width: 768px) {\\n  /* Mobile styles */\\n}",
  "js": "// JavaScript code here"
}

Do not include markdown code blocks, backticks, or explanations. Only return raw JSON."""

    try:
        # Build enhanced context with requirements
        js_functions_text = ""
        if js_functions:
            js_functions_text = f"\n\nREQUIRED JAVASCRIPT FUNCTIONS (MUST IMPLEMENT ALL):\n" + "\n".join([f"- {func}()" for func in js_functions])
        
        context = f"""Create a beautiful, modern, production-ready, FULLY RESPONSIVE webpage based on this request: {prompt}

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}
{js_functions_text}

MANDATORY REQUIREMENTS FOR PERFECT DESIGN:
- The page MUST be fully responsive (mobile, tablet, desktop) - test all breakpoints
- Use CSS Grid or Flexbox for perfect alignment and layout
- All content must be properly centered and aligned
- Use consistent spacing throughout (use CSS variables for spacing if possible)
- The page must look professional and visually appealing on ALL screen sizes
- Use modern design principles (clean layouts, good spacing, attractive colors, proper typography)
- Include smooth animations and transitions for interactive elements
- Use semantic HTML5 elements (header, nav, main, section, footer)
- Write clean, maintainable CSS with modern features
- Add interactive JavaScript features
- For coffee shops: Use warm colors (#8B4513, #D2691E, #F5F5DC), elegant typography, and inviting design
- Include a responsive navigation menu (hamburger menu for mobile)
- Make sure all images and content scale properly
- Use relative units (rem, em, %) for responsive sizing
- Include proper viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1.0">
- Ensure perfect alignment: center content, align text properly, use consistent margins/padding
- Make it look professional and polished - this is production code

Generate complete, working, RESPONSIVE code with PERFECT alignment and BEAUTIFUL design. The code should be production-ready and look amazing on all devices."""
        
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
        
        # Validate code is not empty
        if not html_code or len(html_code.strip()) < 50:
            raise ValueError("Generated HTML code is too short or empty")
        if not css_code or len(css_code.strip()) < 20:
            raise ValueError("Generated CSS code is too short or empty")
        
        # Ensure HTML has viewport meta tag for responsiveness
        if "viewport" not in html_code.lower() and "<head>" in html_code:
            # Add viewport meta tag if missing
            html_code = html_code.replace(
                "<head>",
                "<head>\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
            )
        
        # Ensure CSS has responsive media queries and proper alignment
        if "@media" not in css_code and "max-width" not in css_code:
            # Add basic responsive styles with proper alignment
            css_code += "\n\n/* Responsive Design */\n@media (max-width: 768px) {\n  body {\n    font-size: 14px;\n  }\n  .container {\n    padding: 1rem;\n  }\n}\n"
        
        # Ensure CSS has proper alignment utilities
        if "text-align" not in css_code.lower() and "justify-content" not in css_code.lower():
            # Add basic alignment
            css_code = "* {\n  margin: 0;\n  padding: 0;\n  box-sizing: border-box;\n}\n\n" + css_code
        
        print(f"Generated code - HTML: {len(html_code)} chars, CSS: {len(css_code)} chars, JS: {len(js_code)} chars")
        
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
