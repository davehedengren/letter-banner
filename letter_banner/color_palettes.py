# Color palette definitions for letter banner generation

COLOR_PALETTES = {
    "earthy_vintage": {
        "name": "Earthy Vintage",
        "description": "Warm beige, deep forest greens, rich browns, orange sunset, charcoal black, and cream white",
        "colors": ["warm beige", "deep forest green", "rich brown", "warm orange", "charcoal black", "cream white"],
        "mood": "organic, vintage illustration style with earthy tones"
    },
    "ocean_breeze": {
        "name": "Ocean Breeze", 
        "description": "Deep navy, seafoam green, sandy beige, coral pink, white",
        "colors": ["deep navy blue", "seafoam green", "sandy beige", "coral pink", "crisp white"],
        "mood": "coastal, fresh, maritime style"
    },
    "autumn_harvest": {
        "name": "Autumn Harvest",
        "description": "Burnt orange, golden yellow, deep red, warm brown, cream",
        "colors": ["burnt orange", "golden yellow", "deep burgundy red", "warm chestnut brown", "cream"],
        "mood": "cozy autumn harvest style with warm fall colors"
    },
    "spring_garden": {
        "name": "Spring Garden",
        "description": "Soft pink, sage green, lavender, butter yellow, white",
        "colors": ["soft blush pink", "sage green", "gentle lavender", "butter yellow", "pure white"],
        "mood": "fresh spring garden style with soft pastels"
    },
    "modern_minimal": {
        "name": "Modern Minimal",
        "description": "Charcoal gray, soft blue, warm white, accent black",
        "colors": ["charcoal gray", "soft slate blue", "warm white", "deep black"],
        "mood": "clean, modern, minimalist style"
    },
    "sunset_desert": {
        "name": "Sunset Desert",
        "description": "Terracotta, dusty rose, sage green, golden yellow, cream",
        "colors": ["terracotta orange", "dusty rose", "desert sage green", "golden yellow", "warm cream"],
        "mood": "southwestern desert sunset style"
    },
    "bright_blue": {
        "name": "Bright Blue",
        "description": "Vibrant electric blue, bright yellow, lime green, orange, white",
        "colors": ["vibrant electric blue", "bright sunny yellow", "lime green", "vibrant orange", "crisp white"],
        "mood": "energetic, bright, and youthful with electric blue focus"
    }
}

def display_color_palettes():
    """Display available color palettes for user selection."""
    print("\n🎨 Available Color Palettes:")
    print("=" * 50)
    
    for i, (key, palette) in enumerate(COLOR_PALETTES.items(), 1):
        print(f"\n{i}. {palette['name']}")
        print(f"   Colors: {palette['description']}")
        print(f"   Style: {palette['mood']}")
    
    return COLOR_PALETTES

def select_color_palette():
    """Interactive color palette selection."""
    palettes = display_color_palettes()
    
    print(f"\nChoose a palette (1-{len(palettes)}) or 'custom':")
    
    while True:
        try:
            choice = input("Enter your choice: ").strip().lower()
            
            if choice == 'custom':
                print("\nCreate a custom palette:")
                colors = input("Enter colors separated by commas (e.g., 'red, blue, green, yellow'): ").strip()
                mood = input("Describe the style/mood (e.g., 'bright and playful'): ").strip()
                
                custom_palette = {
                    "name": "Custom",
                    "description": colors,
                    "colors": [c.strip() for c in colors.split(',')],
                    "mood": mood if mood else "custom color scheme"
                }
                return custom_palette
            
            # Try to parse as number
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(palettes):
                    palette_key = list(palettes.keys())[choice_num - 1]
                    selected = palettes[palette_key]
                    print(f"✅ Selected: {selected['name']}")
                    return selected
                else:
                    print(f"Please enter a number between 1 and {len(palettes)}, or 'custom'")
            except ValueError:
                print(f"Please enter a number between 1 and {len(palettes)}, or 'custom'")
                
        except (KeyboardInterrupt, EOFError):
            print("\nUsing default Earthy Vintage palette...")
            return palettes["earthy_vintage"]
