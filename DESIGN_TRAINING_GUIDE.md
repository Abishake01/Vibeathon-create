# Design Training Guide - How to Feed Designs and Train the AI

## Overview
This guide explains different approaches to improve the AI's design generation by feeding it design examples and references.

## Method 1: Prompt Enhancement with Design References (Easiest)

### Current Implementation
The system already uses detailed prompts. You can enhance them by:

1. **Adding Design Examples to Prompts**
   - Include example HTML/CSS snippets in the system prompts
   - Add design pattern descriptions
   - Reference specific design styles

2. **Using Design Reference System**
   ```python
   from app.design_references import get_design_reference, add_design_reference_to_prompt
   
   # Get design reference
   design_ref = get_design_reference("coffee_shop")
   
   # Enhance prompt
   enhanced_prompt = add_design_reference_to_prompt(user_prompt, design_ref)
   ```

## Method 2: Few-Shot Learning (Recommended)

### How It Works
Include example designs in the AI's context so it learns patterns:

```python
# In ai_service_v2.py, add to context:
example_designs = """
EXAMPLE DESIGN 1 - Coffee Shop:
- Layout: Two-column hero with image on right
- Colors: Warm browns (#8B4513, #D2691E)
- Features: Card grid, rounded corners, warm gradients

EXAMPLE DESIGN 2 - Tech Startup:
- Layout: Centered hero with gradient background
- Colors: Dark theme (#1a1a1a, #4a9eff)
- Features: Bold typography, card hover effects
"""

context = f"{user_prompt}\n\n{example_designs}"
```

## Method 3: Design Pattern Library (Best for Production)

### Implementation Steps

1. **Create Design Pattern Database**
   ```python
   # Store in database or JSON file
   design_patterns = {
       "coffee_shop": {
           "html_structure": "...",
           "css_styles": "...",
           "color_palette": [...],
           "layout_type": "two_column"
       }
   }
   ```

2. **Auto-detect Design Type**
   ```python
   def detect_design_type(prompt: str) -> str:
       if "coffee" in prompt.lower():
           return "coffee_shop"
       elif "tech" in prompt.lower():
           return "tech_startup"
       # ... more patterns
   ```

3. **Inject Design Patterns into Prompts**
   - Automatically add relevant design patterns to context
   - Let AI learn from these examples

## Method 4: User-Provided Design References

### Frontend Feature
Allow users to:
- Upload design images
- Paste design URLs
- Select from design templates

### Backend Implementation
```python
# In schemas.py
class AIProjectCreate(BaseModel):
    prompt: str
    design_reference_url: Optional[str] = None  # URL to design example
    design_image_url: Optional[str] = None  # Image of design

# In ai_service_v2.py
def analyze_design_reference(image_url: str) -> Dict:
    """Use vision API to analyze design and extract patterns"""
    # Use OpenAI Vision or similar to analyze design
    # Extract: colors, layout, typography, spacing
    pass
```

## Method 5: Fine-Tuning (Advanced)

### For Custom Models (OpenAI, etc.)

1. **Prepare Training Data**
   ```json
   {
     "messages": [
       {"role": "system", "content": "You are a web designer..."},
       {"role": "user", "content": "Create a coffee shop page"},
       {"role": "assistant", "content": "<html>...</html>"}
     ]
   }
   ```

2. **Fine-tune Model**
   - Use OpenAI fine-tuning API
   - Train on high-quality design examples
   - Deploy custom model

### For Local Models (Ollama)
- Create custom model with design examples
- Use model merging techniques
- Train on design-specific dataset

## Method 6: Design Component Library

### Create Reusable Components
```python
DESIGN_COMPONENTS = {
    "hero_section": {
        "two_column": """
        <div class="hero">
          <div class="hero-text">...</div>
          <div class="hero-image">...</div>
        </div>
        """,
        "centered": """
        <div class="hero-centered">
          <h1>...</h1>
          <p>...</p>
        </div>
        """
    },
    "card_grid": {
        "three_column": "...",
        "four_column": "..."
    }
}
```

## Quick Start: Add Design Examples Now

### Step 1: Update `design_references.py`
Add more design patterns:
```python
DESIGN_PATTERNS["ecommerce"] = {
    "description": "Modern e-commerce with product cards",
    "color_scheme": ["#ffffff", "#000000", "#ff6b6b"],
    "layout": "product_grid",
    "features": ["product_cards", "shopping_cart", "filters"]
}
```

### Step 2: Use in Generation
```python
# In ai_service_v2.py
from app.design_references import get_design_reference, create_design_context

design_type = detect_design_type_from_prompt(prompt)
design_ref = get_design_reference(design_type)
enhanced_context = create_design_context(prompt, design_ref)
```

### Step 3: Test and Iterate
- Generate pages with different design references
- Collect feedback
- Refine design patterns
- Add more examples

## Best Practices

1. **Start Small**: Add 3-5 high-quality design examples
2. **Be Specific**: Include exact HTML/CSS snippets
3. **Iterate**: Test and refine based on results
4. **Document**: Keep track of what works
5. **Diversify**: Cover different design styles

## Next Steps

1. ✅ Design reference system created (`design_references.py`)
2. ⏳ Integrate into generation pipeline
3. ⏳ Add frontend UI for design selection
4. ⏳ Collect and analyze design patterns
5. ⏳ Build design pattern database

