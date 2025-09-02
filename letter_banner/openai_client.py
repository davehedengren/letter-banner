"""
OpenAI API client for letter banner generation
"""

import os
import time
from io import BytesIO
from PIL import Image

from openai import OpenAI

from . import config



def generate_stylized_letter(letter, object_description, output_dir, run_timestamp, color_palette=None):
    """
    Generate a stylized letter inspired by the specified interest using OpenAI.
    
    Args:
        letter (str): The letter to generate
        object_description (str): Interest/theme to inspire the letter design
        output_dir (str): Output directory
        run_timestamp (str): Timestamp for this run
        color_palette (dict): Color palette to use for consistent styling
    
    Returns:
        str: Path to the generated letter image, or None if failed
    """
    print(f"\n--- Generating Letter '{letter.upper()}' inspired by {object_description} ---")
    
    # Build color guidance for the prompt
    color_guidance = ""
    if color_palette:
        colors_str = ", ".join(color_palette["colors"])
        color_guidance = f" Use this specific color palette: {colors_str}. Style it with {color_palette['mood']}."
    
    # Create prompt for stylized letter based on interest/theme
    prompt = f"Create a large, bold letter '{letter.upper()}' that is creatively designed and inspired by the interest/theme of {object_description}. The letter should be clearly recognizable as '{letter.upper()}' but artistically decorated with visual elements, symbols, textures, and motifs that represent {object_description}. Make it bold, artistic, and perfect for a decorative banner.{color_guidance} Keep it centered on a clean white background with no other elements. Think about what objects, patterns, or imagery would represent this interest and incorporate them into the letter design."
    
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
    Generate image with retry logic for moderation blocks.
    """
    client = OpenAI()
    
    # Retry logic for moderation blocks
    for retry_attempt in range(config.MAX_RETRIES_PER_LETTER):
        try:
            if retry_attempt > 0:
                print(f"Retry attempt {retry_attempt + 1}/{config.MAX_RETRIES_PER_LETTER}")
                print(f"Waiting {config.RETRY_DELAY_SECONDS} seconds before retry...")
                time.sleep(config.RETRY_DELAY_SECONDS)
            
            print(f"Attempting image generation for letter '{letter.upper()}'...")
            
            # Use OpenAI image generation (create new image, don't edit)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=config.DEFAULT_IMAGE_SIZE,
                quality="standard"
            )

            if response.data and len(response.data) > 0 and response.data[0].url:
                # Download image from URL
                import requests
                image_url = response.data[0].url
                print(f"Image URL received for letter '{letter.upper()}'.")
                
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_bytes = image_response.content
                    
                    # Save the generated image
                    return _save_generated_image(
                        image_bytes, letter, object_description, output_dir, run_timestamp
                    )
                else:
                    print(f"❌ Failed to download image for letter '{letter.upper()}'")
                    continue
            else:
                print(f"❌ No image data received for letter '{letter.upper()}'")
                continue

        except Exception as e:
            # Check if this is a moderation error
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    if error_data.get('error', {}).get('code') == 'moderation_blocked':
                        print(f"🚫 Letter '{letter.upper()}' blocked by moderation (attempt {retry_attempt + 1}/{config.MAX_RETRIES_PER_LETTER})")
                        if retry_attempt < config.MAX_RETRIES_PER_LETTER - 1:
                            print(f"   Will retry in {config.RETRY_DELAY_SECONDS} seconds...")
                            continue  # Try again
                        else:
                            print(f"   Max retries exceeded for letter '{letter.upper()}'")
                            return None
                except:
                    pass
            
            print(f"❌ Error generating letter '{letter.upper()}': {e}")
            return None
    
    # If we get here, all retries failed
    print(f"❌ All {config.MAX_RETRIES_PER_LETTER} retry attempts failed for letter '{letter.upper()}'")
    return None



def _save_generated_image(image_bytes, letter, object_description, output_dir, run_timestamp):
    """Save the generated image with appropriate naming."""
    import shutil
    
    # Create output directory
    banner_output_dir = os.path.join(output_dir, f"letter_banner_{run_timestamp}")
    os.makedirs(banner_output_dir, exist_ok=True)
    
    # Create filename
    letter_basename = f"letter_{letter.upper()}_{object_description.replace(' ', '_').replace(',', '')}"
    new_letter_name = f"{letter_basename}_{run_timestamp}.png"
    new_letter_path = os.path.join(banner_output_dir, new_letter_name)
    
    # Save image
    img_from_bytes = Image.open(BytesIO(image_bytes))
    img_from_bytes.save(new_letter_path, format="PNG")
    
    print(f"✅ Letter '{letter.upper()}' saved: {new_letter_name}")
    return new_letter_path
