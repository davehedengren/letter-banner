#!/usr/bin/env python3
"""
Main entry point for Letter Banner Generator Web Service
Optimized for Replit deployment
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web.app import app

def main():
    """Main function to start the web service."""
    print("🎨 Letter Banner Generator Web Service")
    print("=" * 50)
    print("Starting web server...")
    
    # Get port from environment (Replit sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🌐 Server will start at http://{host}:{port}")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "web.app:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

if __name__ == "__main__":
    main()
