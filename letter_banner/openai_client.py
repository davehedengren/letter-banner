"""
OpenAI API client for letter banner generation
"""

import os
import sys
import base64
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from openai import OpenAI

from . import config


def create_letter_template(letter, size=(1024, 1024)):
    """
    Create a simple letter template image for OpenAI to transform.
    
    Args:
        letter (str): The letter to create
        size (tuple): Image size (width, height)
    
    Returns:
        str: Path to the created template image
    """
    # Create a white background with black letter
    img = Image.new('RGB', size, config.TEMPLATE_BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Try to use a large font, fall back to default if not available
    try:
        # Try to find a system font
        if sys.platform == "darwin":  # macOS
            font_path = "/System/Library/Fonts/Arial.ttf"
        elif sys.platform == "win32":  # Windows
            font_path = "C:/Windows/Fonts/arial.ttf"
        else:  # Linux and others
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, config.TEMPLATE_FONT_SIZE)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Get text dimensions and center the letter
    bbox = draw.textbbox((0, 0), letter.upper(), font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2 - bbox[1]  # Adjust for baseline
    
    # Draw the letter in black
    draw.text((x, y), letter.upper(), fill=config.TEMPLATE_TEXT_COLOR, font=font)
    
    # Save template
    template_path = f"temp_letter_{letter.upper()}_template.png"
    img.save(template_path)
    return template_path


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
    
    # Create letter template
    template_path = create_letter_template(letter)
    
    try:
        # Build color guidance for the prompt
        color_guidance = ""
        if color_palette:
            colors_str = ", ".join(color_palette["colors"])
            color_guidance = f" Use this specific color palette: {colors_str}. Style it with {color_palette['mood']}."
        
        # Create prompt for stylized letter based on interest/theme
        prompt = f"Transform this letter '{letter.upper()}' to be creatively designed and inspired by the interest/theme of {object_description}. The letter should be clearly recognizable as '{letter.upper()}' but artistically decorated with visual elements, symbols, textures, and motifs that represent {object_description}. Make it bold, artistic, and perfect for a decorative banner.{color_guidance} Keep it centered on a clean white background with no other elements. Think about what objects, patterns, or imagery would represent this interest and incorporate them into the letter design."
        
        print(f"Prompt: {prompt}")
        
        # Generate the stylized letter
        generated_path = _generate_image_with_retry(
            template_path=template_path,
            prompt=prompt,
            output_dir=output_dir,
            letter=letter,
            object_description=object_description,
            run_timestamp=run_timestamp
        )
        
        return generated_path
            
    finally:
        # Clean up template
        if os.path.exists(template_path):
            os.remove(template_path)
    
    return None


def _generate_image_with_retry(template_path, prompt, output_dir, letter, object_description, run_timestamp):
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
            
            # Use OpenAI image generation
            with open(template_path, "rb") as image_file:
                response = client.images.edit(
                    model="dall-e-2",
                    image=image_file,
                    mask=_create_full_mask(template_path),
                    prompt=prompt,
                    n=1,
                    size=config.DEFAULT_IMAGE_SIZE
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


def _create_full_mask(image_path):
    """Create a fully opaque mask for image editing."""
    with Image.open(image_path) as img:
        width, height = img.size
        # Create an RGBA mask (important for alpha channel)
        mask_image = Image.new("RGBA", (width, height), (255, 255, 255, 255))  # White, fully opaque
        
        mask_bytes_io = BytesIO()
        mask_image.save(mask_bytes_io, format="PNG")
        mask_bytes_io.seek(0)  # Reset stream position
        return ("mask.png", mask_bytes_io, "image/png")


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
