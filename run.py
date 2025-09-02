#!/usr/bin/env python3
"""
Development run script for Letter Banner Generator
Alternative to main.py with more development-friendly settings
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the development server with hot reload."""
    print("🎨 Letter Banner Generator - Development Mode")
    print("=" * 50)
    
    # Set development environment
    os.environ.setdefault("ENVIRONMENT", "development")
    
    # Get port from environment or default
    port = int(os.environ.get("PORT", 8000))
    host = "127.0.0.1"  # Local development
    
    print(f"🌐 Development server starting at http://{host}:{port}")
    print("🔄 Hot reload enabled")
    print("=" * 50)
    
    # Start the development server with reload
    uvicorn.run(
        "web.app:app",
        host=host,
        port=port,
        reload=True,  # Enable hot reload for development
        log_level="debug",
        reload_dirs=[str(project_root)]
    )

if __name__ == "__main__":
    main()
