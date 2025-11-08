import json
from typing import Dict, List, Optional, AsyncGenerator
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
        
        result = json.loads(content)
        result["usage"] = usage
        return result
    except Exception as e:
        return {"intent": "create_webpage", "confidence": 0.8, "response": "", "usage": {"total_tokens": estimate_tokens(prompt)}}


def generate_project_description(prompt: str, provider: AIProvider) -> str:
    """Generate project description - separate token call."""
    system_prompt = """You are a creative web developer. Generate a brief, engaging project description based on the user's request.
Keep it concise (2-3 sentences) and highlight the key features and design approach."""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a project description for: {prompt}"}
            ],
            temperature=0.8,
            max_tokens=300
        )
        return response["content"].strip()
    except Exception as e:
        return f"A beautiful, modern webpage based on: {prompt}"


def generate_todo_list(prompt: str, provider: AIProvider) -> List[Dict]:
    """Generate todo list - separate token call."""
    system_prompt = """You are a project planning assistant. Create a detailed todo list for building a webpage based on the user's request.
Return ONLY a valid JSON array of objects, each with "id" (number) and "task" (string) fields.
Example: [{"id": 1, "task": "Set up project structure"}, {"id": 2, "task": "Create HTML structure"}, ...]
Include 5-7 tasks covering: project setup, HTML structure, CSS styling, JavaScript functionality, and final touches."""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        content = response["content"]
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        
        data = json.loads(content)
        if isinstance(data, dict) and "tasks" in data:
            return data["tasks"]
        elif isinstance(data, list):
            return data
        else:
            # Fallback
            return [
                {"id": 1, "task": "Set up project structure"},
                {"id": 2, "task": "Create HTML structure"},
                {"id": 3, "task": "Design CSS styling"},
                {"id": 4, "task": "Add JavaScript functionality"},
                {"id": 5, "task": "Finalize and test"}
            ]
    except Exception as e:
        return [
            {"id": 1, "task": "Set up project structure"},
            {"id": 2, "task": "Create HTML structure"},
            {"id": 3, "task": "Design CSS styling"},
            {"id": 4, "task": "Add JavaScript functionality"},
            {"id": 5, "task": "Finalize and test"}
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


async def generate_code_with_streaming(prompt: str, project_requirements: Dict, html_code: str, provider: AIProvider, code_type: str) -> AsyncGenerator[str, None]:
    """Generate code with streaming - yields line by line for typing effect."""
    import asyncio
    
    if code_type == "html":
        system_prompt = """You are an expert web developer. Generate PREMIUM, PROFESSIONAL HTML code like Bolt.new with CARD-BASED LAYOUTS and MODERN STRUCTURE.

CRITICAL REQUIREMENTS FOR PREMIUM UI (LIKE BOLT.NEW):
1. HTML must be properly formatted with correct indentation (2 spaces per level)
2. Use semantic HTML5 elements (header, nav, main, section, footer, article, aside)
3. Include proper viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1.0">
4. Include Google Fonts: <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
5. Include Font Awesome: <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
6. If user requests Tailwind CSS: Include Tailwind CDN: <script src="https://cdn.tailwindcss.com"></script> in <head> and use Tailwind utility classes throughout HTML
7. STRUCTURE MUST BE SPLIT INTO CLEAR SECTIONS:
   - HEADER/NAVBAR (CRITICAL - MUST BE FULLY FUNCTIONAL):
     * <header><nav class="navbar"> with logo and navigation links</nav></header>
     * Navigation MUST work on all devices (desktop, tablet, mobile)
     * Include hamburger menu for mobile: <button class="menu-toggle"><i class="fas fa-bars"></i></button>
     * Navigation structure: <ul class="nav-menu"><li><a href="#section">Link</a></li></ul>
     * Include JavaScript for mobile menu toggle functionality
   - BODY/MAIN CONTENT: <main> with hero section, features, and other content sections</main>
   - FOOTER: <footer> with links, copyright, and additional information
   - Each section should be clearly separated and well-structured
7. MODERN LAYOUT PATTERNS:
   - HEADER (CRITICAL - MUST BE FUNCTIONAL): <header><nav class="navbar"> with logo, hamburger menu button (.menu-toggle), and navigation links in <ul class="nav-menu"></ul></nav></header>
   - BODY: <main> with hero section, features section with cards in grid
   - FOOTER: <footer> with links, social media, copyright
   - ALWAYS include REAL IMAGES: Use public image URLs from free image services
   - Image URLs must be RELATED to the content (e.g., coffee images for coffee shop, tech images for tech page)
   - Use proper image URLs from these free image sources:
     * Unsplash: https://images.unsplash.com/photo-... or https://unsplash.com/photos/...
     * Pexels: https://images.pexels.com/photos/... or https://www.pexels.com/photo/...
     * Pixabay: https://pixabay.com/photos/... or direct image URLs
     * LibreShot: https://libreshot.com/... or direct image URLs
     * Wikimedia Commons: https://commons.wikimedia.org/wiki/File:... or direct image URLs
     * Flickr Creative Commons: https://live.staticflickr.com/... or https://www.flickr.com/photos/...
   - CRITICAL - IMAGE SIZING: All images MUST have proper sizing attributes to prevent overflow:
     * Add style="width: 100%; max-width: 100%; height: auto; object-fit: cover;" to all <img> tags
     * Or use width="100%" and height="auto" attributes
     * This prevents images from overflowing the page and causing horizontal/vertical scrolling
   - NEVER use empty images, broken links, or placeholder.com
   - Include at least 2-3 images: hero image, feature images, or section images
   - Example URLs: https://images.unsplash.com/photo-1509042239860-f550ce710b93 (coffee), https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg (coffee)
8. DESIGN MUST BE PREMIUM QUALITY:
   - Include multiple card elements for features, testimonials, products
   - Use Font Awesome icons: <i class="fas fa-..."></i>
   - Proper heading hierarchy (h1 for hero, h2 for sections, h3 for cards)
   - Add badges, buttons with proper classes
   - Include stats cards or testimonials if relevant
9. CRITICAL: Do NOT include <link> tags for external CSS files
10. CRITICAL: Do NOT include <script src=""> tags for external JS files
11. All CSS and JS will be injected automatically - just provide the HTML structure

Return ONLY the HTML code as a string. Do not include markdown code blocks, backticks, or explanations."""
        
        project_type = project_requirements.get("project_type", "webpage")
        theme = project_requirements.get("theme", "modern")
        colors = project_requirements.get("colors", [])
        
        # Check if user wants Tailwind CSS
        use_tailwind = "tailwind" in prompt.lower() or "tailwind css" in prompt.lower()
        
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
        
        tailwind_note = ""
        if use_tailwind:
            tailwind_note = "\n\nCRITICAL: User requested Tailwind CSS. Include <script src=\"https://cdn.tailwindcss.com\"></script> in <head> and use Tailwind utility classes (flex, grid, p-4, m-2, bg-blue-500, text-white, rounded-lg, etc.) throughout the HTML instead of custom CSS classes."
        
        # Add design reference if provided
        design_reference_note = ""
        if "design_reference" in project_requirements and project_requirements.get("design_reference"):
            design_ref = project_requirements.get("design_reference")
            design_reference_note = f"\n\nDESIGN REFERENCE: Follow the design style of {design_ref}. Use similar layout patterns, color schemes, and visual elements."
        
        if "design_examples" in project_requirements and project_requirements.get("design_examples"):
            examples = project_requirements.get("design_examples", [])
            design_reference_note += f"\n\nDESIGN EXAMPLES TO FOLLOW:\n" + "\n".join([f"- {ex}" for ex in examples])
        
        context = f"""Create a PREMIUM, PROFESSIONAL HTML structure for: {prompt} - Design it like Bolt.new.

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}
{tailwind_note}
{design_reference_note}

CRITICAL UI REQUIREMENTS (LIKE BOLT.NEW):
- SPLIT INTO CLEAR SECTIONS:
  * HEADER/NAVBAR (CRITICAL - MUST BE FULLY FUNCTIONAL):
    - <header><nav class="navbar"> with logo and navigation links</nav></header>
    - Navigation MUST work on all devices (desktop, tablet, mobile)
    - Include hamburger menu button for mobile: <button class="menu-toggle"><i class="fas fa-bars"></i></button>
    - Navigation structure: <ul class="nav-menu"><li><a href="#home">Home</a></li><li><a href="#about">About</a></li></ul>
    - All navigation links must be clickable and functional
    - Mobile menu must toggle open/close with JavaScript
  * BODY/MAIN: <main> with hero section, features, content sections</main>
  * FOOTER: <footer> with links, social media, copyright</footer>
- CARD-BASED LAYOUTS: Create cards for features, testimonials, products (use .card, .feature-card classes)
- TWO-COLUMN HERO: Left column for text (headline, description, buttons), right column for REAL IMAGE
- PROPER ALIGNMENT: Use .container class, flexbox, and grid for perfect alignment
- ALWAYS INCLUDE REAL IMAGES:
  * Use public image URLs from free image services (all free for commercial use, no attribution required)
  * Images must be RELATED to the content (coffee images for coffee shop, tech images for tech page, etc.)
  * Use URLs from these free image sources:
    - Unsplash: https://images.unsplash.com/photo-... or https://unsplash.com/photos/...
    - Pexels: https://images.pexels.com/photos/... or https://www.pexels.com/photo/...
    - Pixabay: https://pixabay.com/photos/... or direct image URLs
    - LibreShot: https://libreshot.com/... or direct image URLs
    - Wikimedia Commons: https://commons.wikimedia.org/wiki/File:... or direct image URLs
    - Flickr Creative Commons: https://live.staticflickr.com/... or https://www.flickr.com/photos/...
  * Include at least 2-3 images: hero image, feature images, section images
  * NEVER use empty images, broken links, or placeholder.com
  * Example for coffee shop: https://images.unsplash.com/photo-1509042239860-f550ce710b93 or https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg
  * Example for tech: https://images.unsplash.com/photo-1518770660439-4636190af475 or https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg
- Use Font Awesome icons throughout
- Create multiple CTA buttons with different styles
- Add badges, stats cards, or testimonials if relevant
- Use semantic HTML5 with proper class names (navbar, hero, card, feature-card, container, section, footer, etc.)
- Make it look like a premium, modern website with professional layout and structure like Bolt.new creates"""
        
    elif code_type == "css":
        system_prompt = """You are an expert web developer. Generate PREMIUM, PROFESSIONAL CSS code like Bolt.new with CARD-BASED LAYOUTS, PERFECT ALIGNMENT, and MODERN DESIGN.

CRITICAL REQUIREMENTS FOR PREMIUM UI (LIKE BOLT.NEW):
1. CSS must be properly formatted with correct indentation
2. MUST BE FULLY RESPONSIVE - Mobile-first with media queries:
   - @media (max-width: 768px) for mobile
   - @media (max-width: 1024px) for tablet
   - @media (min-width: 1025px) for desktop
3. USE CSS VARIABLES: :root {{ --primary-color: #...; --secondary-color: #...; --spacing: 1rem; }}
4. CARD-BASED DESIGN (CRITICAL):
   - Style .card, .feature-card, .testimonial-card with:
     * box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
     * border-radius: 12px to 16px;
     * padding: 1.5rem to 2rem;
     * background: white or subtle gradient;
     * hover: transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.15);
   - Card grids: display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;
5. PERFECT ALIGNMENT AND LAYOUT (CRITICAL - MUST IMPLEMENT ALL):
   - .container {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; }}
   - Two-column hero: display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;
   - Navigation (CRITICAL - MUST BE RESPONSIVE AND FUNCTIONAL):
     * .navbar {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 1rem 2rem; position: relative; }}
     * .nav-menu {{ display: flex; list-style: none; gap: 2rem; margin: 0; padding: 0; }}
     * Mobile responsive: @media (max-width: 768px) {{
       .menu-toggle {{ display: block; background: none; border: none; font-size: 1.5rem; cursor: pointer; color: inherit; }}
       .nav-menu {{ display: none; position: absolute; top: 100%; left: 0; width: 100%; background: white; flex-direction: column; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; }}
       .nav-menu.active {{ display: flex; }}
     }}
     * Desktop: @media (min-width: 769px) {{ .menu-toggle {{ display: none; }} .nav-menu {{ display: flex; }} }}
     * Smooth transitions: .nav-menu {{ transition: all 0.3s ease; }}
   - Center headings: text-align: center; for h1, h2, h3 in hero and sections
   - Left align paragraphs: text-align: left; for body text and descriptions
   - Justify text: text-align: justify; for longer paragraphs if needed
   - Button groups: display: flex; gap: 1rem; justify-content: flex-start; or center;
   - Vertical centering: display: flex; align-items: center; for vertical alignment
   - Horizontal centering: justify-content: center; for horizontal alignment
   - Center containers: margin: 0 auto; width: 100%; max-width: 1200px;
   - Consistent spacing: 1rem, 1.5rem, 2rem, 3rem, 4rem, 6rem
   - ALWAYS use alignment: justify-content, align-items, text-align, margin: 0 auto;
6. MODERN COLOR SCHEMES:
   - Gradients: linear-gradient(135deg, #color1, #color2)
   - Mixed warm and cool colors
   - Proper contrast ratios
   - CSS variables for theming
7. TYPOGRAPHY:
   - Fonts: 'Poppins' for body, 'Playfair Display' for headings (if appropriate)
   - Hero headline: 3.5rem, font-weight: 700-800, line-height: 1.2
   - Section headings: 2.5rem, font-weight: 600-700
   - Body: 1.125rem, font-weight: 400, line-height: 1.7
8. BUTTONS:
   - Primary: gradient background, border-radius: 10px, padding: 1rem 2rem, hover: scale(1.05)
   - Secondary: border style, transparent background
   - Add icons with proper spacing
9. ANIMATIONS:
   - @keyframes fadeIn, slideInUp, pulse
   - Smooth transitions: transition: all 0.3s ease
   - Hover effects on cards, buttons, links
10. SPACING:
    - Section padding: 4rem to 6rem
    - Card gaps: 2rem in grids
    - Consistent margins between sections
11. RESPONSIVE:
    - Mobile: stack columns, reduce font sizes, adjust padding
    - Tablet: adjust grid columns, moderate spacing
    - Desktop: full layout with optimal spacing
12. MODERN EFFECTS:
    - Multiple shadow layers: box-shadow with rgba values
    - Rounded corners: 8px to 16px
    - Gradient backgrounds for hero sections
    - Overlay effects for images
13. IMAGE SIZING (CRITICAL - PREVENT OVERFLOW):
    - All images MUST have proper sizing to prevent overflow:
      * img {{ width: 100%; max-width: 100%; height: auto; object-fit: cover; }}
      * Or use specific dimensions: width: 600px; max-width: 100%; height: auto;
      * Prevent horizontal scrolling: body {{ max-width: 100vw; overflow-x: hidden; }}
      * Prevent vertical overflow: Use proper height constraints
    - Responsive images: Use max-width: 100%; height: auto; for all images
    - Hero images: Can use height: 500px; or height: 60vh; with object-fit: cover;
    - Container images: width: 100%; max-width: 100%; height: auto;

Return ONLY the CSS code as a string. Do not include markdown code blocks, backticks, or explanations."""
        
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
        
        context = f"""Create PREMIUM, PROFESSIONAL CSS for: {prompt} - Design it like Bolt.new with cards, perfect alignment, and modern UI.

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}

HTML Structure (for reference):
{html_code[:800]}

CRITICAL UI REQUIREMENTS (LIKE BOLT.NEW):
1. CARD-BASED LAYOUTS:
   - Style all .card, .feature-card elements with shadows, rounded corners (12px-16px), padding (1.5rem-2rem)
   - Create card grids: display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;
   - Add hover effects: transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.15);
   - Card backgrounds: white or subtle gradients
2. TWO-COLUMN HERO SECTION:
   - Left column: text content with proper typography (headline 3.5rem, description, buttons)
   - Right column: image/graphic with proper sizing
   - Use grid: display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;
   - Responsive: stack on mobile with @media query
3. PERFECT ALIGNMENT (CRITICAL - MUST IMPLEMENT ALL):
   - .container {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; }}
   - Center containers: margin: 0 auto; width: 100%; max-width: 1200px;
   - Center headings: text-align: center; for h1, h2, h3 in hero and sections
   - Left align paragraphs: text-align: left; for body text and descriptions
   - Justify text: text-align: justify; for longer paragraphs
   - Navigation (CRITICAL - MUST BE RESPONSIVE AND FUNCTIONAL):
     * .navbar {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 1rem 2rem; position: relative; }}
     * .nav-menu {{ display: flex; list-style: none; gap: 2rem; margin: 0; padding: 0; }}
     * Mobile responsive: @media (max-width: 768px) {{
       .menu-toggle {{ display: block; background: none; border: none; font-size: 1.5rem; cursor: pointer; color: inherit; }}
       .nav-menu {{ display: none; position: absolute; top: 100%; left: 0; width: 100%; background: white; flex-direction: column; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; }}
       .nav-menu.active {{ display: flex; }}
     }}
     * Desktop: @media (min-width: 769px) {{ .menu-toggle {{ display: none; }} .nav-menu {{ display: flex; }} }}
     * Smooth transitions: .nav-menu {{ transition: all 0.3s ease; }}
   - Hero alignment: display: flex; or grid with align-items: center; justify-content: space-between; or center;
   - Button alignment: display: flex; gap: 1rem; justify-content: flex-start; or center;
   - Flexbox centering: display: flex; justify-content: center; align-items: center; for perfect centering
   - Grid alignment: Use place-items: center; or align-items: center; justify-items: center;
   - Consistent spacing: Use rem units (1rem, 1.5rem, 2rem, 3rem, 4rem, 6rem) for all margins and padding
   - ALWAYS use alignment properties: justify-content, align-items, text-align, margin: 0 auto;
4. MODERN COLOR THEMES:
   - Use gradients: linear-gradient(135deg, #color1, #color2)
   - Mixed warm and cool colors
   - CSS variables: :root {{ --primary: #...; --secondary: #...; }}
   - Proper contrast for readability
5. TYPOGRAPHY:
   - Apply fonts: 'Poppins' for body, 'Playfair Display' for headings (if appropriate)
   - Hero headline: 3.5rem, font-weight: 700-800, line-height: 1.2
   - Section headings: 2.5rem, font-weight: 600-700
   - Body: 1.125rem, font-weight: 400, line-height: 1.7
6. BUTTONS:
   - Primary: gradient background, border-radius: 10px, padding: 1rem 2rem, hover: transform: scale(1.05)
   - Secondary: border style, transparent background
   - Add icons with proper spacing
7. RESPONSIVE:
   - Mobile-first approach
   - Breakpoints: 768px (mobile), 1024px (tablet)
   - Adjust font sizes, spacing, and layouts for each breakpoint
8. ANIMATIONS:
   - @keyframes fadeIn, slideInUp, pulse
   - Smooth transitions: transition: all 0.3s ease
   - Hover effects on all interactive elements
9. MODERN EFFECTS:
   - Multiple shadow layers for depth: box-shadow with rgba values
   - Rounded corners: 8px to 16px
   - Gradient backgrounds
   - Overlay effects

Make it look like a premium, professional website with card-based layouts, perfect alignment, and modern design like Bolt.new creates."""
        
    else:  # js
        system_prompt = """You are an expert JavaScript developer. Generate clean, modern, production-ready JavaScript code.

CRITICAL REQUIREMENTS:
1. JavaScript must be properly formatted with correct indentation
2. Use modern ES6+ syntax (const, let, arrow functions, template literals)
3. Add proper error handling
4. Make code modular and well-organized
5. Include comments for complex logic
6. Ensure all interactive elements work smoothly
7. Add smooth animations and transitions using JavaScript
8. Handle user interactions properly (click, hover, input events)
9. Use event delegation where appropriate
10. Make code efficient and performant
11. NAVBAR FUNCTIONALITY (CRITICAL - MUST IMPLEMENT):
    - Mobile menu toggle: Add event listener to menu toggle button
    - Toggle mobile menu: Show/hide navigation menu on mobile devices
    - Close menu on link click: Close mobile menu when navigation link is clicked
    - Smooth animations: Add smooth open/close animations for mobile menu
    - Example: document.querySelector('.menu-toggle').addEventListener('click', () => { nav.classList.toggle('active'); });
    - Always include navbar functionality even if project doesn't require other JS

Return ONLY the JavaScript code as a string. Do not include markdown code blocks, backticks, or explanations."""
        
        js_functions = project_requirements.get("js_functions", [])
        js_requirements = ""
        if js_functions:
            js_requirements = f"\nRequired functions: {', '.join(js_functions)}. Implement these functions."
        
        context = f"""Create JavaScript code for: {prompt}

PROJECT TYPE: {project_requirements.get('project_type', 'webpage')}
{js_requirements}

HTML Structure (for reference):
{html_code[:500]}

CRITICAL REQUIREMENTS:
- Modern ES6+ syntax
- Smooth interactions and animations
- Proper event handling
- Error handling
- Well-organized, modular code
- NAVBAR FUNCTIONALITY (CRITICAL - MUST IMPLEMENT):
  * Mobile menu toggle: Add click event to .menu-toggle button
  * Toggle navigation menu: Show/hide .nav-menu on mobile
  * Close menu on link click: Close mobile menu when nav links are clicked
  * Smooth animations: Add CSS transitions for menu open/close
  * Example code:
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    menuToggle.addEventListener('click', () => {{
      navMenu.classList.toggle('active');
    }});
    // Close menu when link is clicked
    document.querySelectorAll('.nav-menu a').forEach(link => {{
      link.addEventListener('click', () => {{
        navMenu.classList.remove('active');
      }});
    }});
- Add interactive features based on the project type"""
    
    # Generate code
    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=12000  # Significantly increased for better UI
        )
        
        code = response["content"].strip()
        
        # Remove markdown if present
        if f"```{code_type}" in code:
            code = code.split(f"```{code_type}")[1].split("```")[0].strip()
        elif "```" in code:
            parts = code.split("```")
            if len(parts) > 1:
                code = parts[1].strip()
                if code.startswith(code_type):
                    code = code[len(code_type):].strip()
        
        # Stream code line by line with typing effect
        lines = code.split('\n')
        for line in lines:
            yield line + '\n'
            await asyncio.sleep(0.01)  # Small delay for typing effect
        
    except Exception as e:
        raise Exception(f"Error generating {code_type.upper()}: {str(e)}")


def generate_html_code(prompt: str, project_requirements: Dict, provider: AIProvider) -> str:
    """Generate HTML code - separate token call."""
    project_type = project_requirements.get("project_type", "webpage")
    theme = project_requirements.get("theme", "modern")
    colors = project_requirements.get("colors", [])
    
    # Check if user wants Tailwind CSS
    use_tailwind = "tailwind" in prompt.lower() or "tailwind css" in prompt.lower()
    
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
    
    tailwind_note = ""
    if use_tailwind:
        tailwind_note = "\n\nCRITICAL: User requested Tailwind CSS. Include <script src=\"https://cdn.tailwindcss.com\"></script> in <head> and use Tailwind utility classes (flex, grid, p-4, m-2, bg-blue-500, text-white, rounded-lg, etc.) throughout the HTML instead of custom CSS classes."
    
    system_prompt = """You are an expert web developer. Generate PREMIUM, PROFESSIONAL HTML code like Bolt.new with CARD-BASED LAYOUTS and MODERN STRUCTURE.

CRITICAL REQUIREMENTS FOR PREMIUM UI (LIKE BOLT.NEW):
1. HTML must be properly formatted with correct indentation (2 spaces per level)
2. Use semantic HTML5 elements (header, nav, main, section, footer, article, aside)
3. Include proper viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1.0">
4. Include Google Fonts: <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
5. Include Font Awesome: <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
6. If user requests Tailwind CSS: Include Tailwind CDN: <script src="https://cdn.tailwindcss.com"></script> in <head> and use Tailwind utility classes throughout HTML
7. STRUCTURE MUST BE SPLIT INTO CLEAR SECTIONS:
   - HEADER/NAVBAR (CRITICAL - MUST BE FULLY FUNCTIONAL):
     * <header><nav class="navbar"> with logo and navigation links</nav></header>
     * Navigation MUST work on all devices (desktop, tablet, mobile)
     * Include hamburger menu for mobile: <button class="menu-toggle"><i class="fas fa-bars"></i></button>
     * Navigation structure: <ul class="nav-menu"><li><a href="#section">Link</a></li></ul>
     * Include JavaScript for mobile menu toggle functionality
   - BODY/MAIN CONTENT: <main> with hero section, features, and other content sections</main>
   - FOOTER: <footer> with links, copyright, and additional information
   - Each section should be clearly separated and well-structured
7. MODERN LAYOUT PATTERNS:
   - HEADER (CRITICAL - MUST BE FUNCTIONAL): <header><nav class="navbar"> with logo, hamburger menu button (.menu-toggle), and navigation links in <ul class="nav-menu"></ul></nav></header>
   - BODY: <main> with hero section, features section with cards in grid
   - FOOTER: <footer> with links, social media, copyright
   - ALWAYS include REAL IMAGES: Use public image URLs from free image services
   - Image URLs must be RELATED to the content (e.g., coffee images for coffee shop, tech images for tech page)
   - Use proper image URLs from these free image sources:
     * Unsplash: https://images.unsplash.com/photo-... or https://unsplash.com/photos/...
     * Pexels: https://images.pexels.com/photos/... or https://www.pexels.com/photo/...
     * Pixabay: https://pixabay.com/photos/... or direct image URLs
     * LibreShot: https://libreshot.com/... or direct image URLs
     * Wikimedia Commons: https://commons.wikimedia.org/wiki/File:... or direct image URLs
     * Flickr Creative Commons: https://live.staticflickr.com/... or https://www.flickr.com/photos/...
   - CRITICAL - IMAGE SIZING: All images MUST have proper sizing attributes to prevent overflow:
     * Add style="width: 100%; max-width: 100%; height: auto; object-fit: cover;" to all <img> tags
     * Or use width="100%" and height="auto" attributes
     * This prevents images from overflowing the page and causing horizontal/vertical scrolling
   - NEVER use empty images, broken links, or placeholder.com
   - Include at least 2-3 images: hero image, feature images, or section images
   - Example URLs: https://images.unsplash.com/photo-1509042239860-f550ce710b93 (coffee), https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg (coffee)
8. DESIGN MUST BE PREMIUM QUALITY:
   - Include multiple card elements for features, testimonials, products
   - Use Font Awesome icons: <i class="fas fa-..."></i>
   - Proper heading hierarchy (h1 for hero, h2 for sections, h3 for cards)
   - Add badges, buttons with proper classes
   - Include stats cards or testimonials if relevant
9. CRITICAL: Do NOT include <link> tags for external CSS files
10. CRITICAL: Do NOT include <script src=""> tags for external JS files
11. All CSS and JS will be injected automatically - just provide the HTML structure

Return ONLY the HTML code as a string. Do not include markdown code blocks, backticks, or explanations."""

    context = f"""Create a PREMIUM, PROFESSIONAL HTML structure for: {prompt} - Design it like Bolt.new.

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}
{tailwind_note}

CRITICAL UI REQUIREMENTS (LIKE BOLT.NEW):
- SPLIT INTO CLEAR SECTIONS:
  * HEADER/NAVBAR (CRITICAL - MUST BE FULLY FUNCTIONAL):
    - <header><nav class="navbar"> with logo and navigation links</nav></header>
    - Navigation MUST work on all devices (desktop, tablet, mobile)
    - Include hamburger menu button for mobile: <button class="menu-toggle"><i class="fas fa-bars"></i></button>
    - Navigation structure: <ul class="nav-menu"><li><a href="#home">Home</a></li><li><a href="#about">About</a></li></ul>
    - All navigation links must be clickable and functional
    - Mobile menu must toggle open/close with JavaScript
  * BODY/MAIN: <main> with hero section, features, content sections</main>
  * FOOTER: <footer> with links, social media, copyright</footer>
- CARD-BASED LAYOUTS: Create cards for features, testimonials, products (use .card, .feature-card classes)
- TWO-COLUMN HERO: Left column for text (headline, description, buttons), right column for REAL IMAGE
- PROPER ALIGNMENT: Use .container class, flexbox, and grid for perfect alignment
- ALWAYS INCLUDE REAL IMAGES:
  * Use public image URLs from free image services (all free for commercial use, no attribution required)
  * Images must be RELATED to the content (coffee images for coffee shop, tech images for tech page, etc.)
  * Use URLs from these free image sources:
    - Unsplash: https://images.unsplash.com/photo-... or https://unsplash.com/photos/...
    - Pexels: https://images.pexels.com/photos/... or https://www.pexels.com/photo/...
    - Pixabay: https://pixabay.com/photos/... or direct image URLs
    - LibreShot: https://libreshot.com/... or direct image URLs
    - Wikimedia Commons: https://commons.wikimedia.org/wiki/File:... or direct image URLs
    - Flickr Creative Commons: https://live.staticflickr.com/... or https://www.flickr.com/photos/...
  * Include at least 2-3 images: hero image, feature images, section images
  * NEVER use empty images, broken links, or placeholder.com
  * Example for coffee shop: https://images.unsplash.com/photo-1509042239860-f550ce710b93 or https://images.pexels.com/photos/2253275/pexels-photo-2253275.jpeg
  * Example for tech: https://images.unsplash.com/photo-1518770660439-4636190af475 or https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg
- Use Font Awesome icons throughout
- Create multiple CTA buttons with different styles
- Add badges, stats cards, or testimonials if relevant
- Use semantic HTML5 with proper class names (navbar, hero, card, feature-card, container, section, footer, etc.)
- Make it look like a premium, modern website with professional layout and structure like Bolt.new creates"""

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
    
    system_prompt = """You are an expert web developer. Generate PREMIUM, PROFESSIONAL CSS code like Bolt.new with CARD-BASED LAYOUTS, PERFECT ALIGNMENT, and MODERN DESIGN.

CRITICAL REQUIREMENTS FOR PREMIUM UI (LIKE BOLT.NEW):
1. CSS must be properly formatted with correct indentation
2. MUST BE FULLY RESPONSIVE - Mobile-first with media queries:
   - @media (max-width: 768px) for mobile
   - @media (max-width: 1024px) for tablet
   - @media (min-width: 1025px) for desktop
3. USE CSS VARIABLES: :root {{ --primary-color: #...; --secondary-color: #...; --spacing: 1rem; }}
4. CARD-BASED DESIGN (CRITICAL):
   - Style .card, .feature-card, .testimonial-card with:
     * box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
     * border-radius: 12px to 16px;
     * padding: 1.5rem to 2rem;
     * background: white or subtle gradient;
     * hover: transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.15);
   - Card grids: display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;
5. PERFECT ALIGNMENT AND LAYOUT (CRITICAL - MUST IMPLEMENT ALL):
   - .container {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; }}
   - Two-column hero: display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;
   - Navigation (CRITICAL - MUST BE RESPONSIVE AND FUNCTIONAL):
     * .navbar {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 1rem 2rem; position: relative; }}
     * .nav-menu {{ display: flex; list-style: none; gap: 2rem; margin: 0; padding: 0; }}
     * Mobile responsive: @media (max-width: 768px) {{
       .menu-toggle {{ display: block; background: none; border: none; font-size: 1.5rem; cursor: pointer; color: inherit; }}
       .nav-menu {{ display: none; position: absolute; top: 100%; left: 0; width: 100%; background: white; flex-direction: column; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; }}
       .nav-menu.active {{ display: flex; }}
     }}
     * Desktop: @media (min-width: 769px) {{ .menu-toggle {{ display: none; }} .nav-menu {{ display: flex; }} }}
     * Smooth transitions: .nav-menu {{ transition: all 0.3s ease; }}
   - Center headings: text-align: center; for h1, h2, h3 in hero and sections
   - Left align paragraphs: text-align: left; for body text and descriptions
   - Justify text: text-align: justify; for longer paragraphs if needed
   - Button groups: display: flex; gap: 1rem; justify-content: flex-start; or center;
   - Vertical centering: display: flex; align-items: center; for vertical alignment
   - Horizontal centering: justify-content: center; for horizontal alignment
   - Center containers: margin: 0 auto; width: 100%; max-width: 1200px;
   - Consistent spacing: 1rem, 1.5rem, 2rem, 3rem, 4rem, 6rem
   - ALWAYS use alignment: justify-content, align-items, text-align, margin: 0 auto;
6. MODERN COLOR SCHEMES:
   - Gradients: linear-gradient(135deg, #color1, #color2)
   - Mixed warm and cool colors
   - Proper contrast ratios
   - CSS variables for theming
7. TYPOGRAPHY:
   - Fonts: 'Poppins' for body, 'Playfair Display' for headings (if appropriate)
   - Hero headline: 3.5rem, font-weight: 700-800, line-height: 1.2
   - Section headings: 2.5rem, font-weight: 600-700
   - Body: 1.125rem, font-weight: 400, line-height: 1.7
8. BUTTONS:
   - Primary: gradient background, border-radius: 10px, padding: 1rem 2rem, hover: scale(1.05)
   - Secondary: border style, transparent background
   - Add icons with proper spacing
9. ANIMATIONS:
   - @keyframes fadeIn, slideInUp, pulse
   - Smooth transitions: transition: all 0.3s ease
   - Hover effects on cards, buttons, links
10. SPACING:
    - Section padding: 4rem to 6rem
    - Card gaps: 2rem in grids
    - Consistent margins between sections
11. RESPONSIVE:
    - Mobile: stack columns, reduce font sizes, adjust padding
    - Tablet: adjust grid columns, moderate spacing
    - Desktop: full layout with optimal spacing
12. MODERN EFFECTS:
    - Multiple shadow layers: box-shadow with rgba values
    - Rounded corners: 8px to 16px
    - Gradient backgrounds for hero sections
    - Overlay effects for images
13. IMAGE SIZING (CRITICAL - PREVENT OVERFLOW):
    - All images MUST have proper sizing to prevent overflow:
      * img {{ width: 100%; max-width: 100%; height: auto; object-fit: cover; }}
      * Or use specific dimensions: width: 600px; max-width: 100%; height: auto;
      * Prevent horizontal scrolling: body {{ max-width: 100vw; overflow-x: hidden; }}
      * Prevent vertical overflow: Use proper height constraints
    - Responsive images: Use max-width: 100%; height: auto; for all images
    - Hero images: Can use height: 500px; or height: 60vh; with object-fit: cover;
    - Container images: width: 100%; max-width: 100%; height: auto;

Return ONLY the CSS code as a string. Do not include markdown code blocks, backticks, or explanations."""

    context = f"""Create PREMIUM, PROFESSIONAL CSS for: {prompt} - Design it like Bolt.new with cards, perfect alignment, and modern UI.

PROJECT TYPE: {project_type}
THEME: {theme}
{color_scheme}

HTML Structure (for reference):
{html_code[:800]}

CRITICAL UI REQUIREMENTS (LIKE BOLT.NEW):
1. CARD-BASED LAYOUTS:
   - Style all .card, .feature-card elements with shadows, rounded corners (12px-16px), padding (1.5rem-2rem)
   - Create card grids: display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem;
   - Add hover effects: transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.15);
   - Card backgrounds: white or subtle gradients
2. TWO-COLUMN HERO SECTION:
   - Left column: text content with proper typography (headline 3.5rem, description, buttons)
   - Right column: image/graphic with proper sizing
   - Use grid: display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center;
   - Responsive: stack on mobile with @media query
3. PERFECT ALIGNMENT (CRITICAL - MUST IMPLEMENT ALL):
   - .container {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; }}
   - Center containers: margin: 0 auto; width: 100%; max-width: 1200px;
   - Center headings: text-align: center; for h1, h2, h3 in hero and sections
   - Left align paragraphs: text-align: left; for body text and descriptions
   - Justify text: text-align: justify; for longer paragraphs
   - Navigation (CRITICAL - MUST BE RESPONSIVE AND FUNCTIONAL):
     * .navbar {{ display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 1rem 2rem; position: relative; }}
     * .nav-menu {{ display: flex; list-style: none; gap: 2rem; margin: 0; padding: 0; }}
     * Mobile responsive: @media (max-width: 768px) {{
       .menu-toggle {{ display: block; background: none; border: none; font-size: 1.5rem; cursor: pointer; color: inherit; }}
       .nav-menu {{ display: none; position: absolute; top: 100%; left: 0; width: 100%; background: white; flex-direction: column; padding: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; }}
       .nav-menu.active {{ display: flex; }}
     }}
     * Desktop: @media (min-width: 769px) {{ .menu-toggle {{ display: none; }} .nav-menu {{ display: flex; }} }}
     * Smooth transitions: .nav-menu {{ transition: all 0.3s ease; }}
   - Hero alignment: display: flex; or grid with align-items: center; justify-content: space-between; or center;
   - Button alignment: display: flex; gap: 1rem; justify-content: flex-start; or center;
   - Flexbox centering: display: flex; justify-content: center; align-items: center; for perfect centering
   - Grid alignment: Use place-items: center; or align-items: center; justify-items: center;
   - Consistent spacing: Use rem units (1rem, 1.5rem, 2rem, 3rem, 4rem, 6rem) for all margins and padding
   - ALWAYS use alignment properties: justify-content, align-items, text-align, margin: 0 auto;
4. MODERN COLOR THEMES:
   - Use gradients: linear-gradient(135deg, #color1, #color2)
   - Mixed warm and cool colors
   - CSS variables: :root {{ --primary: #...; --secondary: #...; }}
   - Proper contrast for readability
5. TYPOGRAPHY:
   - Apply fonts: 'Poppins' for body, 'Playfair Display' for headings (if appropriate)
   - Hero headline: 3.5rem, font-weight: 700-800, line-height: 1.2
   - Section headings: 2.5rem, font-weight: 600-700
   - Body: 1.125rem, font-weight: 400, line-height: 1.7
6. BUTTONS:
   - Primary: gradient background, border-radius: 10px, padding: 1rem 2rem, hover: transform: scale(1.05)
   - Secondary: border style, transparent background
   - Add icons with proper spacing
7. RESPONSIVE:
   - Mobile-first approach
   - Breakpoints: 768px (mobile), 1024px (tablet)
   - Adjust font sizes, spacing, and layouts for each breakpoint
8. ANIMATIONS:
   - @keyframes fadeIn, slideInUp, pulse
   - Smooth transitions: transition: all 0.3s ease
   - Hover effects on all interactive elements
9. MODERN EFFECTS:
   - Multiple shadow layers for depth: box-shadow with rgba values
   - Rounded corners: 8px to 16px
   - Gradient backgrounds
   - Overlay effects

Make it look like a premium, professional website with card-based layouts, perfect alignment, and modern design like Bolt.new creates."""

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
        
        return css_code
    
    except Exception as e:
        raise Exception(f"Error generating CSS: {str(e)}")


def generate_js_code(prompt: str, project_requirements: Dict, html_code: str, provider: AIProvider) -> str:
    """Generate JavaScript code - separate token call."""
    js_functions = project_requirements.get("js_functions", [])
    project_type = project_requirements.get("project_type", "webpage")
    
    js_requirements = ""
    if js_functions:
        js_requirements = f"\nRequired functions: {', '.join(js_functions)}. Implement these functions with full functionality."
    elif project_type.lower() == "todo list":
        js_requirements = "\nRequired functions: addTask, deleteTask, toggleTask, clearCompleted. Implement these functions with full functionality."
    
    system_prompt = """You are an expert JavaScript developer. Generate clean, modern, production-ready JavaScript code.

CRITICAL REQUIREMENTS:
1. JavaScript must be properly formatted with correct indentation
2. Use modern ES6+ syntax (const, let, arrow functions, template literals)
3. Add proper error handling
4. Make code modular and well-organized
5. Include comments for complex logic
6. Ensure all interactive elements work smoothly
7. Add smooth animations and transitions using JavaScript
8. Handle user interactions properly (click, hover, input events)
9. Use event delegation where appropriate
10. Make code efficient and performant

Return ONLY the JavaScript code as a string. Do not include markdown code blocks, backticks, or explanations."""

    context = f"""Create JavaScript code for: {prompt}

PROJECT TYPE: {project_type}
{js_requirements}

HTML Structure (for reference):
{html_code[:500]}

CRITICAL REQUIREMENTS:
- Modern ES6+ syntax
- Smooth interactions and animations
- Proper event handling
- Error handling
- Well-organized, modular code
- Add interactive features based on the project type"""

    try:
        response = provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=12000  # Significantly increased for better UI
        )
        
        js_code = response["content"].strip()
        
        # Remove markdown if present
        if "```javascript" in js_code:
            js_code = js_code.split("```javascript")[1].split("```")[0].strip()
        elif "```js" in js_code:
            js_code = js_code.split("```js")[1].split("```")[0].strip()
        elif "```" in js_code:
            parts = js_code.split("```")
            if len(parts) > 1:
                js_code = parts[1].strip()
                if js_code.startswith("javascript") or js_code.startswith("js"):
                    js_code = js_code[10:].strip() if js_code.startswith("javascript") else js_code[2:].strip()
        
        return js_code
    
    except Exception as e:
        raise Exception(f"Error generating JavaScript: {str(e)}")
