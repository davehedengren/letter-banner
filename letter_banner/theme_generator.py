"""
Theme variation generator using LLMs
Generates creative letter-specific themes from a single overarching theme
"""

import os
import json
from openai import OpenAI
from google import genai


def generate_theme_variations(name, theme, model="gemini-2.0-flash-exp"):
    """
    Generate creative theme variations for each letter in a name.
    
    Args:
        name (str): The name/word to generate themes for
        theme (str): The overarching theme (e.g., "mermaids", "space", "nature")
        model (str): Model to use - "gemini-2.0-flash-exp" or "gpt-4o"
    
    Returns:
        list: List of dicts with 'letter' and 'theme' keys, or None if failed
    """
    # Extract unique letters while preserving order
    letters = [c.upper() for c in name if c.isalpha()]
    
    if model.startswith("gemini"):
        return _generate_variations_gemini(letters, theme, model)
    elif model.startswith("gpt"):
        return _generate_variations_openai(letters, theme, model)
    else:
        raise ValueError(f"Unsupported model: {model}")


def _generate_variations_gemini(letters, theme, model="gemini-2.0-flash-exp"):
    """Generate theme variations using Gemini."""
    client = genai.Client()
    
    prompt = f"""For the letters {', '.join(letters)}, generate creative and specific theme variations based on the overarching theme '{theme}'.

IMPORTANT: The theme variation does NOT need to start with the same letter. For example, for letter 'A' with ocean theme, you could suggest "treasure chest" or "submarine" - it doesn't have to be "anchor" or "algae". Focus on variety and visual interest!

Each letter should have a unique object, concept, or element related to {theme}.
Make them diverse, interesting, and visually distinctive from each other.
The variations should work well as decorative letter designs.

Return ONLY a valid JSON array in this exact format, with no additional text:
[
  {{"letter": "{letters[0]}", "theme": "specific variation"}},
  {{"letter": "{letters[1]}", "theme": "specific variation"}},
  ...
]

Example for theme 'ocean' with letters A, B, C:
[
  {{"letter": "A", "theme": "coral reef"}},
  {{"letter": "B", "theme": "treasure chest"}},
  {{"letter": "C", "theme": "submarine periscope"}}
]

Notice how none of the themes start with their letter - this gives more creative freedom!

Now generate for the letters {', '.join(letters)} with theme '{theme}'."""

    try:
        print(f"🎨 Generating theme variations for '{theme}' with Gemini...")
        
        response = client.models.generate_content(
            model=model,
            contents=[prompt]
        )
        
        # Extract text response
        response_text = ""
        for part in response.parts:
            if part.text:
                response_text = part.text
                break
        
        # Parse JSON from response
        # Remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        variations = json.loads(response_text)
        
        print(f"✅ Generated {len(variations)} theme variations")
        for v in variations:
            print(f"   {v['letter']} → {v['theme']}")
        
        return variations
        
    except Exception as e:
        print(f"❌ Error generating theme variations with Gemini: {e}")
        return None


def _generate_variations_openai(letters, theme, model="gpt-4o"):
    """Generate theme variations using OpenAI."""
    client = OpenAI()
    
    prompt = f"""For the letters {', '.join(letters)}, generate creative and specific theme variations based on the overarching theme '{theme}'.

IMPORTANT: The theme variation does NOT need to start with the same letter. For example, for letter 'A' with ocean theme, you could suggest "treasure chest" or "submarine" - it doesn't have to be "anchor" or "algae". Focus on variety and visual interest!

Each letter should have a unique object, concept, or element related to {theme}.
Make them diverse, interesting, and visually distinctive from each other.
The variations should work well as decorative letter designs.

Return ONLY a valid JSON array in this exact format, with no additional text:
[
  {{"letter": "{letters[0]}", "theme": "specific variation"}},
  {{"letter": "{letters[1]}", "theme": "specific variation"}},
  ...
]

Example for theme 'ocean' with letters A, B, C:
[
  {{"letter": "A", "theme": "coral reef"}},
  {{"letter": "B", "theme": "treasure chest"}},
  {{"letter": "C", "theme": "submarine periscope"}}
]

Notice how none of the themes start with their letter - this gives more creative freedom!

Now generate for the letters {', '.join(letters)} with theme '{theme}'."""

    try:
        print(f"🎨 Generating theme variations for '{theme}' with OpenAI...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates theme variations for decorative letters. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        
        # Parse JSON - OpenAI might wrap it
        response_data = json.loads(response_text)
        
        # Handle different response formats
        if "variations" in response_data:
            variations = response_data["variations"]
        elif "letters" in response_data:
            variations = response_data["letters"]
        elif isinstance(response_data, list):
            variations = response_data
        else:
            # Try to find the array in the response
            variations = next(v for v in response_data.values() if isinstance(v, list))
        
        print(f"✅ Generated {len(variations)} theme variations")
        for v in variations:
            print(f"   {v['letter']} → {v['theme']}")
        
        return variations
        
    except Exception as e:
        print(f"❌ Error generating theme variations with OpenAI: {e}")
        return None

