"""
Google Gemini API client for letter banner generation
"""

import os
import time
import base64
from io import BytesIO
from PIL import Image

from google import genai
from google.genai import types

from . import config


def generate_stylized_letter_gemini(letter, object_description, output_dir, run_timestamp, color_palette=None):
    """
    Generate a stylized letter inspired by the specified interest using Google Gemini.
    
    Args:
        letter (str): The letter to generate
        object_description (str): Interest/theme to inspire the letter design
        output_dir (str): Output directory
        run_timestamp (str): Timestamp for this run
        color_palette (dict): Color palette to use for consistent styling
    
    Returns:
        str: Path to the generated letter image, or None if failed
    """
    print(f"\n--- Generating Letter '{letter.upper()}' inspired by {object_description} (Gemini) ---")
    
    # Build color guidance for the prompt
    color_guidance = ""
    if color_palette:
        colors_str = ", ".join(color_palette["colors"])
        color_guidance = f" Use this specific color palette: {colors_str}. Style it with {color_palette['mood']}."
    
    # Create prompt for stylized letter based on interest/theme
    prompt = f"Create ONLY the letter '{letter.upper()}' as a decorative design inspired by {object_description}. The letter should be clearly recognizable as '{letter.upper()}' with artistic decorations, patterns, and motifs that represent {object_description}.{color_guidance} CRITICAL: The background must be completely transparent (alpha channel = 0). Do not include any background colors, shapes, frames, borders, or environmental elements. Only generate the letter itself with decorative elements integrated into the letter shape. The letter should appear to float with no background whatsoever - suitable for cutting out and placing on any surface. Think of it as a sticker or decal of just the letter."
    
    print(f"Prompt: {prompt}")
    
    # Generate the stylized letter
    generated_path = _generate_image_with_retry(
        prompt=prompt,
        output_dir=output_dir,
        letter=letter,
        object_description=object_description,
        run_timestamp=run_timestamp
    )
    
    return generated_path


def _generate_image_with_retry(prompt, output_dir, letter, object_description, run_timestamp):
    """
    Generate image with retry logic for failures.
    """
    # Initialize Gemini client - it will automatically use GEMINI_API_KEY from environment
    # The Client() constructor automatically reads from GEMINI_API_KEY env var
    client = genai.Client()
    
    # Retry logic for failures
    for retry_attempt in range(config.MAX_RETRIES_PER_LETTER):
        try:
            if retry_attempt > 0:
                print(f"Retry attempt {retry_attempt + 1}/{config.MAX_RETRIES_PER_LETTER}")
                print(f"Waiting {config.RETRY_DELAY_SECONDS} seconds before retry...")
                time.sleep(config.RETRY_DELAY_SECONDS)
            
            print(f"Attempting image generation for letter '{letter.upper()}' with Gemini...")
            
            # Use Gemini image generation with gemini-3-pro-image-preview model (Nano Banana Pro)
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE'],  # Only request image output
                    image_config=types.ImageConfig(
                        aspect_ratio="1:1",  # Square format for letters
                        image_size="1K"  # 1024x1024 - Options: 1K, 2K, 4K
                    )
                )
            )
            
            print(f"API request sent to Gemini for letter '{letter.upper()}'")
            
            # Process the response
            if response.candidates and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        print(f"Image data received for letter '{letter.upper()}'.")
                        
                        # Use the as_image() method to get PIL Image directly
                        image = part.as_image()
                        
                        # Save the image directly
                        return _save_gemini_image(
                            image, letter, object_description, output_dir, run_timestamp
                        )
                    elif part.text is not None:
                        print(f"Text response: {part.text}")
                
                print(f"❌ No image data received for letter '{letter.upper()}'")
                continue
            else:
                print(f"❌ No response data received for letter '{letter.upper()}'")
                continue

        except Exception as e:
            print(f"❌ Error generating letter '{letter.upper()}' with Gemini: {e}")
            if retry_attempt < config.MAX_RETRIES_PER_LETTER - 1:
                print(f"   Will retry in {config.RETRY_DELAY_SECONDS} seconds...")
                continue
            else:
                print(f"   Max retries exceeded for letter '{letter.upper()}'")
                return None
    
    # If we get here, all retries failed
    print(f"❌ All {config.MAX_RETRIES_PER_LETTER} retry attempts failed for letter '{letter.upper()}'")
    return None


def _save_generated_image(image_bytes, letter, object_description, output_dir, run_timestamp):
    """Save the generated image with appropriate naming (for OpenAI)."""
    import shutil
    
    # Create output directory
    banner_output_dir = os.path.join(output_dir, f"letter_banner_{run_timestamp}")
    os.makedirs(banner_output_dir, exist_ok=True)
    
    # Create filename
    letter_basename = f"letter_{letter.upper()}_{object_description.replace(' ', '_').replace(',', '')}"
    new_letter_name = f"{letter_basename}_{run_timestamp}.png"
    new_letter_path = os.path.join(banner_output_dir, new_letter_name)
    
    # Save image and check transparency
    img_from_bytes = Image.open(BytesIO(image_bytes))
    
    # Debug: Check if image has transparency
    has_transparency = img_from_bytes.mode in ('RGBA', 'LA') or 'transparency' in img_from_bytes.info
    print(f"🔍 Image mode: {img_from_bytes.mode}, Has transparency: {has_transparency}")
    
    # Ensure we save with transparency if available
    if has_transparency:
        img_from_bytes.save(new_letter_path, format="PNG", optimize=True)
    else:
        print(f"⚠️ Warning: Letter '{letter.upper()}' does not have transparency!")
        img_from_bytes.save(new_letter_path, format="PNG")
    
    print(f"✅ Letter '{letter.upper()}' saved: {new_letter_name}")
    return new_letter_path


def _save_gemini_image(image, letter, object_description, output_dir, run_timestamp):
    """Save the Gemini PIL Image with appropriate naming."""
    # Create output directory
    banner_output_dir = os.path.join(output_dir, f"letter_banner_{run_timestamp}")
    os.makedirs(banner_output_dir, exist_ok=True)
    
    # Create filename
    letter_basename = f"letter_{letter.upper()}_{object_description.replace(' ', '_').replace(',', '')}"
    new_letter_name = f"{letter_basename}_{run_timestamp}.png"
    new_letter_path = os.path.join(banner_output_dir, new_letter_name)
    
    # Save the image directly - as_image() returns a ready-to-save image object
    try:
        image.save(new_letter_path)
        print(f"✅ Letter '{letter.upper()}' saved: {new_letter_name}")
        return new_letter_path
    except Exception as e:
        print(f"⚠️ Error saving image: {e}")
        raise

