"""
Design Reference System - Allows feeding design examples to improve AI generation
"""

from typing import Dict, List, Optional
import json
import os

# Design pattern library - stores design examples
DESIGN_PATTERNS = {
    "coffee_shop": {
        "description": "Warm, inviting coffee shop design with earthy tones",
        "color_scheme": ["#8B4513", "#D2691E", "#F5F5DC", "#FFFFFF", "#CD853F"],
        "layout": "two_column_hero",
        "features": ["card_grid", "warm_gradients", "rounded_corners"],
        "example_html_snippet": """
        <div class="hero">
          <div class="hero-content">
            <h1>Welcome to Our Coffee Shop</h1>
            <p>Experience the finest coffee crafted with love</p>
            <button class="btn-primary">View Menu</button>
          </div>
          <div class="hero-image">
            <img src="..." alt="Coffee" style="width: 100%; max-width: 100%; height: auto;">
          </div>
        </div>
        """,
        "example_css_snippet": """
        .hero {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 4rem;
          align-items: center;
          padding: 4rem 2rem;
        }
        """
    },
    "tech_startup": {
        "description": "Modern tech startup with clean lines and bold typography",
        "color_scheme": ["#1a1a1a", "#4a9eff", "#ffffff", "#f5f5f5"],
        "layout": "centered_hero",
        "features": ["gradient_backgrounds", "bold_typography", "card_hover_effects"],
    },
    "portfolio": {
        "description": "Creative portfolio with showcase sections",
        "color_scheme": ["#ffffff", "#333333", "#007bff", "#f8f9fa"],
        "layout": "grid_portfolio",
        "features": ["image_galleries", "hover_overlays", "minimal_design"],
    }
}


def get_design_reference(design_type: str) -> Optional[Dict]:
    """Get design reference by type."""
    return DESIGN_PATTERNS.get(design_type.lower())


def add_design_reference_to_prompt(prompt: str, design_reference: Optional[Dict] = None) -> str:
    """Enhance prompt with design reference examples."""
    if not design_reference:
        return prompt
    
    reference_text = f"""
    
DESIGN REFERENCE:
- Description: {design_reference.get('description', '')}
- Color Scheme: {', '.join(design_reference.get('color_scheme', []))}
- Layout Style: {design_reference.get('layout', '')}
- Key Features: {', '.join(design_reference.get('features', []))}
"""
    
    if 'example_html_snippet' in design_reference:
        reference_text += f"\nExample HTML Structure:\n{design_reference['example_html_snippet']}"
    
    if 'example_css_snippet' in design_reference:
        reference_text += f"\nExample CSS Style:\n{design_reference['example_css_snippet']}"
    
    return prompt + reference_text


def detect_design_type_from_prompt(prompt: str) -> Optional[str]:
    """Detect design type from user prompt."""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["coffee", "cafe", "coffee shop"]):
        return "coffee_shop"
    elif any(word in prompt_lower for word in ["tech", "startup", "saas", "software"]):
        return "tech_startup"
    elif any(word in prompt_lower for word in ["portfolio", "showcase", "gallery"]):
        return "portfolio"
    
    return None


def create_design_context(prompt: str, design_reference: Optional[Dict] = None) -> str:
    """Create enhanced context with design reference."""
    context = f"Create a webpage for: {prompt}"
    
    if design_reference:
        context += f"\n\nFollow this design style: {design_reference.get('description', '')}"
        context += f"\nUse colors: {', '.join(design_reference.get('color_scheme', []))}"
        context += f"\nLayout: {design_reference.get('layout', '')}"
        context += f"\nInclude features: {', '.join(design_reference.get('features', []))}"
    
    return context

