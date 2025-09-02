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
