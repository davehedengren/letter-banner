"""
Model abstraction layer for image generation
Routes requests to appropriate provider (OpenAI or Gemini) based on model selection
"""

from .openai_client import generate_stylized_letter as generate_stylized_letter_openai
from .gemini_client import generate_stylized_letter_gemini


def generate_stylized_letter(letter, object_description, output_dir, run_timestamp, color_palette=None, model="gemini-3-pro-image-preview"):
    """
    Generate a stylized letter using the specified model.
    
    Args:
        letter (str): The letter to generate
        object_description (str): Interest/theme to inspire the letter design
        output_dir (str): Output directory
        run_timestamp (str): Timestamp for this run
        color_palette (dict): Color palette to use for consistent styling
        model (str): Model to use - "gemini-3-pro-image-preview" or "gpt-image-1"
    
    Returns:
        str: Path to the generated letter image, or None if failed
    """
    if model == "gemini-3-pro-image-preview":
        return generate_stylized_letter_gemini(
            letter=letter,
            object_description=object_description,
            output_dir=output_dir,
            run_timestamp=run_timestamp,
            color_palette=color_palette
        )
    elif model == "gpt-image-1":
        return generate_stylized_letter_openai(
            letter=letter,
            object_description=object_description,
            output_dir=output_dir,
            run_timestamp=run_timestamp,
            color_palette=color_palette
        )
    else:
        raise ValueError(f"Unsupported model: {model}. Supported models are 'gemini-3-pro-image' and 'gpt-image-1'")

