"""
Banner layout utilities for letter banner generation
"""

import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter as letter_size
from reportlab.lib.utils import ImageReader

from . import config


def create_banner_layout(letter_paths, output_dir, run_timestamp, letters_per_row=None):
    """
    Create a printable banner layout from individual letters.
    
    Args:
        letter_paths (list): Paths to individual letter images
        output_dir (str): Output directory
        run_timestamp (str): Timestamp for this run
        letters_per_row (int): Number of letters per row (auto-calculate if None)
    
    Returns:
        str: Path to the banner layout file
    """
    if not letter_paths:
        print("No letter images to create banner from.")
        return None
    
    try:
        # Load all letter images
        letter_images = []
        for path in letter_paths:
            if os.path.exists(path):
                img = Image.open(path)
                letter_images.append(img)
        
        if not letter_images:
            print("No valid letter images found for banner creation.")
            return None
        
        num_letters = len(letter_images)
        
        # Auto-calculate layout if not specified
        if letters_per_row is None:
            if num_letters <= 4:
                letters_per_row = num_letters
            elif num_letters <= 8:
                letters_per_row = 4
            else:
                letters_per_row = min(6, num_letters)
        
        rows = (num_letters + letters_per_row - 1) // letters_per_row
        
        # Calculate letter size for the layout
        margin = 100  # pixels
        available_width = config.PRINT_WIDTH_PIXELS - (2 * margin)
        available_height = config.PRINT_HEIGHT_PIXELS - (2 * margin)
        
        letter_width = available_width // letters_per_row
        letter_height = available_height // rows
        
        # Use the smaller dimension to maintain aspect ratio
        letter_size = min(letter_width, letter_height)
        
        print(f"Creating banner layout: {letters_per_row} letters per row, {rows} rows")
        print(f"Letter size: {letter_size}x{letter_size} pixels")
        
        # Create banner canvas
        banner = Image.new('RGB', (config.PRINT_WIDTH_PIXELS, config.PRINT_HEIGHT_PIXELS), 'white')
        
        # Place letters on the banner
        for i, letter_img in enumerate(letter_images):
            row = i // letters_per_row
            col = i % letters_per_row
            
            # Resize letter to fit
            letter_resized = letter_img.resize((letter_size, letter_size), Image.Resampling.LANCZOS)
            
            # Calculate position (centered within available space)
            total_row_width = letters_per_row * letter_size
            start_x = (config.PRINT_WIDTH_PIXELS - total_row_width) // 2
            start_y = margin + (row * letter_size)
            
            x = start_x + (col * letter_size)
            y = start_y
            
            # Handle transparent images properly
            if letter_resized.mode in ('RGBA', 'LA') or (letter_resized.mode == 'P' and 'transparency' in letter_resized.info):
                # Use alpha channel for proper transparency blending
                banner.paste(letter_resized, (x, y), letter_resized)
            else:
                banner.paste(letter_resized, (x, y))
        
        # Save banner
        banner_output_dir = os.path.join(output_dir, f"letter_banner_{run_timestamp}")
        banner_filename = f"printable_banner_{run_timestamp}.png"
        banner_path = os.path.join(banner_output_dir, banner_filename)
        
        banner.save(banner_path, 'PNG', dpi=(300, 300))
        
        print(f"🖨️ Printable banner created: {banner_filename}")
        print(f"📐 Dimensions: {config.PRINT_WIDTH_PIXELS}x{config.PRINT_HEIGHT_PIXELS} pixels (8.5x11 inches at 300dpi)")
        
        return banner_path
        
    except Exception as e:
        print(f"Error creating banner layout: {e}")
        return None


def create_pdf_with_all_letters(letter_paths, output_dir, run_timestamp, name="BANNER"):
    """
    Create a PDF with all individual letters in order, one per page.
    
    Args:
        letter_paths (list): Paths to individual letter images
        output_dir (str): Output directory
        run_timestamp (str): Timestamp for this run
        name (str): Name being spelled out (for filename)
    
    Returns:
        str: Path to the created PDF file
    """
    if not letter_paths:
        print("No letter images to create PDF from.")
        return None
    
    try:
        # Create output directory
        banner_output_dir = os.path.join(output_dir, f"letter_banner_{run_timestamp}")
        os.makedirs(banner_output_dir, exist_ok=True)
        
        # Create PDF filename
        pdf_filename = f"{name.lower()}_letters_{run_timestamp}.pdf"
        pdf_path = os.path.join(banner_output_dir, pdf_filename)
        
        # Create PDF
        c = canvas.Canvas(pdf_path, pagesize=letter_size)
        page_width, page_height = letter_size
        
        print(f"Creating PDF with {len(letter_paths)} letters...")
        
        for i, letter_path in enumerate(letter_paths):
            if not os.path.exists(letter_path):
                print(f"Warning: Letter image not found: {letter_path}")
                continue
            
            try:
                # Open and process image for PDF
                with Image.open(letter_path) as img:
                    img_width, img_height = img.size
                    
                    # Calculate scaling to fit on page with margin
                    margin = 36  # 0.5 inch margin (36 points = 0.5 inches)
                    available_width = page_width - (2 * margin)
                    available_height = page_height - (2 * margin)
                    
                    scale_w = available_width / img_width
                    scale_h = available_height / img_height
                    scale = min(scale_w, scale_h)  # Use smaller scale to fit
                    
                    # Calculate final dimensions and position
                    final_width = img_width * scale
                    final_height = img_height * scale
                    x = (page_width - final_width) / 2
                    y = (page_height - final_height) / 2
                    
                    # Handle transparency properly for PDF
                    if img.mode in ('RGBA', 'LA') or 'transparency' in img.info:
                        # For transparent images, create a temporary image with white background
                        # This ensures the letter shows up clearly when printed
                        white_bg = Image.new('RGB', img.size, 'white')
                        if img.mode == 'RGBA':
                            white_bg.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                        else:
                            white_bg.paste(img, (0, 0))
                        
                        # Save temporary image
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            white_bg.save(temp_file.name, 'PNG')
                            temp_path = temp_file.name
                        
                        # Draw the processed image
                        c.drawImage(temp_path, x, y, width=final_width, height=final_height)
                        
                        # Clean up temp file
                        os.unlink(temp_path)
                    else:
                        # For non-transparent images, draw directly
                        c.drawImage(letter_path, x, y, width=final_width, height=final_height)
                    
                    # Extract letter name for logging (but don't print on PDF)
                    letter_name = os.path.basename(letter_path).split('_')[1]  # Extract letter from filename
                    print(f"Added letter {letter_name.upper()} to PDF (page {i + 1})")
                    
                    # Start new page if not the last letter
                    if i < len(letter_paths) - 1:
                        c.showPage()
                        
            except Exception as e:
                print(f"Error adding letter {letter_path} to PDF: {e}")
                continue
        
        # Save PDF
        c.save()
        
        print(f"📄 PDF created with all letters: {pdf_filename}")
        return pdf_path
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None
