"""
Utility functions for letter banner generation
"""

import os
from dotenv import load_dotenv


def load_api_key():
    """Load the OpenAI API key from .env file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Look for .env in the parent directory (project root)
    project_root = os.path.dirname(script_dir)
    dotenv_path = os.path.join(project_root, ".env")
    
    loaded_successfully = load_dotenv(dotenv_path=dotenv_path, override=True)
    
    if not loaded_successfully:
        print(f"Warning: Could not load .env file from {dotenv_path}.")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found.")
        print(f"Please ensure '{dotenv_path}' exists and contains OPENAI_API_KEY='your_key'.")
        return False
    
    print("API key loaded successfully.")
    return True


def interactive_letter_input():
    """
    Interactive function to get letters, objects, and color palette from user.
    
    Returns:
        tuple: (list of (letter, object_description) tuples, color_palette dict)
    """
    from .color_palettes import select_color_palette
    
    print("\n🎨 Letter Banner Creator - Interactive Mode")
    print("=" * 50)
    
    # First, select color palette
    print("Step 1: Choose your color palette for consistent styling across all letters.")
    color_palette = select_color_palette()
    
    print(f"\n✅ Using color palette: {color_palette['name']}")
    print(f"   Style: {color_palette['mood']}")
    
    print("\nStep 2: Enter letters and what objects you'd like them shaped like.")
    print("Examples: A=apple, B=butterfly, C=cat, etc.")
    print("Type 'done' when finished, or 'quit' to exit.\n")
    
    letters_and_objects = []
    
    while True:
        try:
            user_input = input(f"Letter {len(letters_and_objects) + 1} (or 'done'/'quit'): ").strip()
            
            if user_input.lower() in ['done', 'quit', 'exit']:
                break
            
            if '=' in user_input:
                # Parse "A=apple" format
                letter, object_desc = user_input.split('=', 1)
                letter = letter.strip().upper()
                object_desc = object_desc.strip()
            else:
                # Ask separately
                letter = user_input.upper()
                if len(letter) != 1 or not letter.isalpha():
                    print("Please enter a single letter.")
                    continue
                
                object_desc = input(f"What should letter '{letter}' be shaped like? ").strip()
            
            if len(letter) == 1 and letter.isalpha() and object_desc:
                letters_and_objects.append((letter, object_desc))
                print(f"✅ Added: {letter} = {object_desc}")
            else:
                print("Invalid input. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return [], None
        except EOFError:
            break
    
    return letters_and_objects, color_palette
