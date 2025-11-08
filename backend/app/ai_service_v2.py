import json
from typing import Dict, List, Optional
from app.ai_providers import get_provider, AIProvider


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
    return len(text) // 4


def detect_user_intent(prompt: str, provider: AIProvider) -> Dict[str, any]:
    """Detect user intent from the prompt."""
    system_prompt = """You are an intent detection assistant. Analyze user messages and determine their intent.

Possible intents:
1. "create_webpage" - User wants to create/build a webpage/website
2. "conversation" - User is just chatting, greeting, or asking questions
3. "ideas" - User wants project ideas or suggestions

Return ONLY a valid JSON object:
{
  "intent": "create_webpage" | "conversation" | "ideas",
  "confidence": 0.0-1.0,
  "response": "Your response to the user (only if intent is conversation or ideas)"
}"""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        content = response["content"]
        usage = response.get("usage", {})
        
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
        data["usage"] = usage
        return data
    
    except Exception as e:
        return {
            "intent": "conversation",
            "confidence": 0.5,
            "response": "I'm here to help you create webpages! Try saying something like 'create a coffee shop page' to get started.",
            "usage": {}
        }


def generate_project_description(prompt: str, provider: AIProvider) -> str:
    """Generate a project description - separate token call."""
    system_prompt = """You are a web development assistant. Describe the project that will be created based on the user's request.

Provide a clear, concise description (2-3 sentences) of what the webpage will include and its key features. Focus on the UI/UX aspects and design elements."""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response["content"].strip()
    
    except Exception as e:
        raise Exception(f"Error generating description: {str(e)}")


def generate_todo_list(prompt: str, provider: AIProvider) -> List[Dict[str, any]]:
    """Generate a todo list - separate token call."""
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

Include 6-8 tasks covering:
1. Project structure setup
2. HTML structure creation
3. CSS styling and design
4. JavaScript functionality
5. Responsive design implementation
6. UI polish and animations

Do not include any markdown formatting or explanations. Only return the raw JSON object."""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a todo list for: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        content = response["content"]
        data = json.loads(content)
        
        if isinstance(data, dict) and "todos" in data:
            todos = data["todos"]
        elif isinstance(data, list):
            todos = data
        else:
            todos = [
                {"id": 1, "task": "Set up project structure", "completed": False},
                {"id": 2, "task": "Create HTML structure", "completed": False},
                {"id": 3, "task": "Design CSS styling", "completed": False},
                {"id": 4, "task": "Add JavaScript functionality", "completed": False},
                {"id": 5, "task": "Make responsive design", "completed": False},
            ]
        
        return todos
    
    except Exception as e:
        return [
            {"id": 1, "task": "Set up project structure", "completed": False},
            {"id": 2, "task": "Create HTML structure", "completed": False},
            {"id": 3, "task": "Design CSS styling", "completed": False},
            {"id": 4, "task": "Add JavaScript functionality", "completed": False},
            {"id": 5, "task": "Make responsive design", "completed": False},
        ]


def extract_project_requirements(prompt: str, provider: AIProvider) -> Dict[str, any]:
    """Extract theme, colors, and project type - separate token call."""
    system_prompt = """Analyze the user's request and extract:
1. Project type (todo list, coffee shop, portfolio, landing page, etc.)
2. Theme preferences (dark, light, modern, vintage, etc.)
3. Color preferences (specific colors mentioned)
4. Required JavaScript functions needed

Return JSON: {"project_type": "...", "theme": "...", "colors": ["..."], "js_functions": ["..."]}"""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        content = response["content"]
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        return json.loads(content)
    except:
        return {"project_type": "webpage", "theme": "modern", "colors": [], "js_functions": []}


def generate_html_code(prompt: str, project_requirements: Dict, provider: AIProvider) -> str:
    """Generate HTML code - separate token call."""
    project_type = project_requirements.get("project_type", "webpage")
    theme = project_requirements.get("theme", "modern")
    colors = project_requirements.get("colors", [])
    
    color_scheme = ""
    if colors:
        color_scheme = f"\nUser requested colors: {', '.join(colors)}. Use these colors."
    elif theme:
        if theme.lower() == "dark":
            color_scheme = "\nUse a dark theme with colors like #1a1a1a, #2d2d2d, #ffffff, #4a9eff"
        elif theme.lower() == "light":
            color_scheme = "\nUse a light theme with colors like #ffffff, #f5f5f5, #333333, #007bff"
        elif "coffee" in prompt.lower():
            color_scheme = "\nUse warm coffee shop colors: #8B4513, #D2691E, #F5F5DC, #FFFFFF, #CD853F"
    
    system_prompt = """You are an expert web developer. Generate clean, modern, production-ready HTML code with HIGHLY ATTRACTIVE, ORIGINAL DESIGN.

CRITICAL REQUIREMENTS FOR BEAUTIFUL UI:
1. HTML must be properly formatted with correct indentation (2 spaces per level)
2. Use semantic HTML5 elements (header, nav, main, section, footer, article, aside)
3. Include proper viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1.0">
4. Include Google Fonts or other attractive fonts in <head>: <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
5. Include Font Awesome or similar icon library: <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
6. Add meaningful class names for styling (use BEM methodology or similar)
7. Include proper accessibility attributes (alt, aria-labels where needed)
8. Use proper heading hierarchy (h1, h2, h3)
9. DESIGN MUST BE HIGHLY ATTRACTIVE:
   - Use modern, eye-catching layouts
   - Include icons from Font Awesome (use <i class="fas fa-..."></i>)
   - Use attractive typography with Google Fonts
   - Add data attributes for animations
   - Include proper structure for animations and interactions
10. Make it look professional and polished like a real modern website
11. CRITICAL: Do NOT include <link> tags for external CSS files (style.css, styles.css, etc.)
12. CRITICAL: Do NOT include <script src=""> tags for external JS files (script.js, main.js, etc.)
13. All CSS and JS will be injected automatically - just provide the HTML structure

Return ONLY the HTML code as a string. Do not include markdown code blocks, backticks, or explanations."""

    context = f"""Create beautiful, modern HTML structure for: {prompt}

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}

CRITICAL UI REQUIREMENTS:
- Semantic HTML5 structure
- Responsive and accessible
- HIGHLY ATTRACTIVE design with icons, modern fonts, animations
- Professional, polished appearance like premium websites
- Include Google Fonts (Poppins, Inter, Playfair Display) in <head>
- Include Font Awesome icons library in <head>
- Add proper structure for animations and interactions
- Use meaningful class names for styling
- Make it visually stunning and modern"""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=12000  # Significantly increased for better UI
        )
        
        html_code = response["content"].strip()
        
        # Remove markdown if present
        if "```html" in html_code:
            html_code = html_code.split("```html")[1].split("```")[0].strip()
        elif "```" in html_code:
            parts = html_code.split("```")
            if len(parts) > 1:
                html_code = parts[1].strip()
                if html_code.startswith("html"):
                    html_code = html_code[4:].strip()
        
        # Ensure viewport meta tag
        if "viewport" not in html_code.lower() and "<head>" in html_code:
            html_code = html_code.replace(
                "<head>",
                "<head>\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
            )
        
        return html_code
    
    except Exception as e:
        raise Exception(f"Error generating HTML: {str(e)}")


def generate_css_code(prompt: str, project_requirements: Dict, html_code: str, provider: AIProvider) -> str:
    """Generate CSS code - separate token call."""
    project_type = project_requirements.get("project_type", "webpage")
    theme = project_requirements.get("theme", "modern")
    colors = project_requirements.get("colors", [])
    
    color_scheme = ""
    if colors:
        color_scheme = f"\nUser requested colors: {', '.join(colors)}. Use these colors as the primary palette."
    elif theme:
        if theme.lower() == "dark":
            color_scheme = "\nUse a dark theme with colors like #1a1a1a, #2d2d2d, #ffffff, #4a9eff"
        elif theme.lower() == "light":
            color_scheme = "\nUse a light theme with colors like #ffffff, #f5f5f5, #333333, #007bff"
        elif "coffee" in prompt.lower():
            color_scheme = "\nUse warm coffee shop colors: #8B4513, #D2691E, #F5F5DC, #FFFFFF, #CD853F"
    
    system_prompt = """You are an expert web developer. Generate clean, modern, production-ready, FULLY RESPONSIVE CSS code with HIGHLY ATTRACTIVE, ORIGINAL DESIGN.

CRITICAL REQUIREMENTS FOR BEAUTIFUL UI:
1. CSS must be properly formatted with correct indentation
2. MUST BE FULLY RESPONSIVE - Use media queries: @media (max-width: 768px) for mobile, @media (max-width: 1024px) for tablet
3. Use CSS Grid or Flexbox for PERFECT alignment and layout
4. Use relative units (rem, em, %, vw, vh) for responsive sizing
5. DESIGN MUST BE HIGHLY ATTRACTIVE AND ORIGINAL:
   - Use creative, modern layouts that stand out
   - Implement unique visual elements (gradients, shadows, animations, glassmorphism effects)
   - Create professional, polished appearance like premium websites
   - Use original color schemes with proper contrast
   - Add micro-interactions and smooth animations (fade-in, slide-in, scale effects)
   - Use attractive typography with Google Fonts (Poppins, Inter, Playfair Display, etc.)
   - Add hover effects, transitions, and interactive elements
   - Use CSS variables for colors and spacing for consistency
   - Add box-shadows, border-radius, and modern styling
   - Include keyframe animations for engaging effects
6. Perfect alignment - center content properly, use consistent spacing
7. Use modern typography with proper font weights and sizes
8. Add smooth transitions (0.3s ease) and hover effects on all interactive elements
9. Use CSS variables for colors and spacing
10. Mobile-first responsive design
11. Include animations: @keyframes for fade-in, slide-in, pulse effects
12. Make buttons and interactive elements attractive with gradients, shadows, and hover states
13. Use modern color palettes and ensure proper contrast

Return ONLY the CSS code as a string. Do not include markdown code blocks, backticks, or explanations."""

    context = f"""Create beautiful, modern, responsive CSS for: {prompt}

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}

HTML Structure (for reference):
{html_code[:500]}

CRITICAL UI REQUIREMENTS:
- Fully responsive (mobile, tablet, desktop)
- HIGHLY ATTRACTIVE design with icons, animations, modern fonts
- Smooth animations and transitions (fade-in, slide-in, hover effects)
- Professional, polished appearance like premium websites
- Perfect alignment and spacing
- Use Google Fonts (Poppins, Inter, Playfair Display) - apply to body and headings
- Style Font Awesome icons properly
- Add keyframe animations for engaging effects (@keyframes fadeIn, slideIn, pulse)
- Modern color schemes with gradients and shadows
- Make buttons and interactive elements attractive with gradients, shadows, hover states
- Use CSS variables for colors and spacing
- Add box-shadows, border-radius, and modern styling throughout
- Ensure perfect alignment - center content properly"""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=12000  # Significantly increased for better UI
        )
        
        css_code = response["content"].strip()
        
        # Remove markdown if present
        if "```css" in css_code:
            css_code = css_code.split("```css")[1].split("```")[0].strip()
        elif "```" in css_code:
            parts = css_code.split("```")
            if len(parts) > 1:
                css_code = parts[1].strip()
                if css_code.startswith("css"):
                    css_code = css_code[3:].strip()
        
        # Ensure responsive styles
        if "@media" not in css_code:
            css_code += "\n\n/* Responsive Design */\n@media (max-width: 768px) {\n  body {\n    font-size: 14px;\n  }\n}\n"
        
        return css_code
    
    except Exception as e:
        raise Exception(f"Error generating CSS: {str(e)}")


def generate_js_code(prompt: str, project_requirements: Dict, html_code: str, provider: AIProvider) -> str:
    """Generate JavaScript code - separate token call."""
    project_type = project_requirements.get("project_type", "webpage")
    js_functions = project_requirements.get("js_functions", [])
    
    # Determine required JS functions based on project type
    if "todo" in project_type.lower() or "task" in project_type.lower():
        js_functions.extend(["addTask", "deleteTask", "toggleCheckbox", "saveToLocalStorage", "loadFromLocalStorage"])
    elif "calculator" in project_type.lower():
        js_functions.extend(["calculate", "clear", "handleInput"])
    elif "form" in project_type.lower() or "contact" in project_type.lower():
        js_functions.extend(["validateForm", "submitForm", "resetForm"])
    
    js_functions_text = ""
    if js_functions:
        js_functions_text = f"\n\nREQUIRED FUNCTIONS (MUST IMPLEMENT ALL):\n" + "\n".join([f"- {func}()" for func in js_functions])
    
    system_prompt = """You are an expert web developer. Generate clean, modern, production-ready JavaScript code.

CRITICAL REQUIREMENTS:
1. JavaScript must be properly formatted with correct indentation
2. All functions must be complete and functional
3. Add proper event listeners
4. Handle user interactions smoothly
5. Use modern JavaScript (ES6+)
6. Add error handling where appropriate
7. Make functions work seamlessly with the UI

Return ONLY the JavaScript code as a string. Do not include markdown code blocks, backticks, or explanations."""

    context = f"""Create functional JavaScript for: {prompt}

PROJECT TYPE: {project_type}
{js_functions_text}

HTML Structure (for reference):
{html_code[:500]}

Requirements:
- All required functions implemented
- Smooth user interactions
- Error handling
- Modern JavaScript"""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        js_code = response["content"].strip()
        
        # Remove markdown if present
        if "```javascript" in js_code or "```js" in js_code:
            js_code = js_code.split("```")[1].split("```")[0].strip()
            if js_code.startswith("javascript") or js_code.startswith("js"):
                js_code = js_code.split("\n", 1)[1] if "\n" in js_code else ""
        elif "```" in js_code:
            parts = js_code.split("```")
            if len(parts) > 1:
                js_code = parts[1].strip()
                if js_code.startswith("javascript") or js_code.startswith("js"):
                    js_code = js_code.split("\n", 1)[1] if "\n" in js_code else ""
        
        return js_code
    
    except Exception as e:
        raise Exception(f"Error generating JavaScript: {str(e)}")

