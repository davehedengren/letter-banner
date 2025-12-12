"""
Image editing utilities using image-to-image APIs
"""

import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from google import genai
from google.genai import types


def edit_letter_image(image_path, edit_prompt, output_path, model="gemini-3-pro-image-preview"):
    """
    Edit a letter image using image-to-image API.
    
    Args:
        image_path (str): Path to the original letter image
        edit_prompt (str): Text prompt describing the desired edits
        output_path (str): Path to save the edited image
        model (str): Model to use for editing
    
    Returns:
        str: Path to the edited image, or None if failed
    """
    if model == "gemini-3-pro-image-preview":
        return _edit_with_gemini(image_path, edit_prompt, output_path, model)
    elif model == "gpt-image-1":
        return _edit_with_openai(image_path, edit_prompt, output_path)
    else:
        raise ValueError(f"Unsupported model for editing: {model}")


def _edit_with_gemini(image_path, edit_prompt, output_path, model="gemini-3-pro-image-preview"):
    """Edit image using Gemini image-to-image."""
    try:
        # Client automatically uses GEMINI_API_KEY environment variable
        client = genai.Client()
        
        # Load the original image
        original_image = Image.open(image_path)
        
        print(f"🖼️ Editing image with Gemini...")
        print(f"   Edit prompt: {edit_prompt}")
        
        # Use Gemini's image-to-image capability
        response = client.models.generate_content(
            model=model,
            contents=[edit_prompt, original_image],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                    image_size="1K"
                )
            )
        )
        
        # Extract the edited image
        for part in response.parts:
            if part.inline_data:
                edited_image = part.as_image()
                edited_image.save(output_path)
                print(f"✅ Image edited and saved to: {output_path}")
                return output_path
        
        print("❌ No image returned from Gemini edit")
        return None
        
    except Exception as e:
        print(f"❌ Error editing image with Gemini: {e}")
        return None


def _edit_with_openai(image_path, edit_prompt, output_path):
    """Edit image using OpenAI image editing."""
    try:
        client = OpenAI()
        
        print(f"🖼️ Editing image with OpenAI...")
        print(f"   Edit prompt: {edit_prompt}")
        
        # OpenAI's edit API requires the image as a file object
        with open(image_path, "rb") as image_file:
            response = client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt=edit_prompt,
                background="transparent",
                output_format="png"
            )
        
        # Get the edited image
        if response.data and len(response.data) > 0:
            if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                # Base64 response
                image_b64 = response.data[0].b64_json
                image_bytes = base64.b64decode(image_b64)
                
                # Save edited image
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"✅ Image edited and saved to: {output_path}")
                return output_path
            elif hasattr(response.data[0], 'url') and response.data[0].url:
                # URL response
                import requests
                image_url = response.data[0].url
                image_response = requests.get(image_url)
                
                if image_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    print(f"✅ Image edited and saved to: {output_path}")
                    return output_path
        
        print("❌ No image returned from OpenAI edit")
        return None
        
    except Exception as e:
        print(f"❌ Error editing image with OpenAI: {e}")
        return None

