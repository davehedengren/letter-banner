# Configuration settings for the Letter Banner Generator

# Print dimensions at 300dpi
PRINT_WIDTH_PIXELS = 2550  # 8.5 inches * 300 dpi
PRINT_HEIGHT_PIXELS = 3300  # 11 inches * 300 dpi

# Individual letter size for generation
LETTER_SIZE = "1024x1024"

# OpenAI API settings
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_FORMAT = "png"

# Retry settings for API calls
MAX_RETRIES_PER_LETTER = 3
RETRY_DELAY_SECONDS = 10

# Default output directory for letter banners
OUTPUT_DIR = "output"

# Template settings
TEMPLATE_FONT_SIZE = 600
TEMPLATE_BACKGROUND_COLOR = "white"
TEMPLATE_TEXT_COLOR = "black"

# Model configurations
DEFAULT_MODEL = "gemini-3-pro-image-preview"

SUPPORTED_MODELS = {
    "gemini-3-pro-image-preview": {
        "name": "Gemini 3 Pro Image Preview",
        "nickname": "Nano Banana Pro",
        "provider": "Google",
        "description": "Advanced image generation with up to 4K resolution, Google Search grounding, and multi-turn editing",
        "cost_per_image": 0.0336,  # $30 per 1M tokens, 1120 tokens per image
        "resolution": "1024x1024 (1K), 2048x2048 (2K), or 4096x4096 (4K)",
        "max_resolution": "4096x4096",
        "features": ["Multi-turn editing", "Google Search grounding", "4K support", "Transparent backgrounds"],
        "speed": "Medium"
    },
    "gpt-image-1": {
        "name": "OpenAI GPT-Image-1",
        "nickname": "GPT-Image-1",
        "provider": "OpenAI",
        "description": "High-quality image generation with transparent backgrounds",
        "cost_per_image": 0.17,  # $0.17 per image
        "resolution": "1024x1024",
        "max_resolution": "1024x1024",
        "features": ["Transparent backgrounds", "High quality"],
        "speed": "Fast"
    }
}
