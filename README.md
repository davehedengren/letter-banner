# Letter Banner Generator Web Service

A beautiful web service that creates stylized letter banners where each letter is shaped like objects of your choice. Perfect for creating personalized name banners, educational materials, or decorative prints.

## 🌟 Features

- **Custom Letter Objects**: Each letter can be shaped like any object (A=Apple, B=Butterfly, etc.)
- **Color Palette Selection**: Choose from curated color palettes or create custom ones
- **Print-Ready Output**: Generates high-quality 300dpi images optimized for 8.5x11" printing
- **Multiple Formats**: Individual letters, combined banner layout, and PDF compilation
- **Real-Time Progress**: Track generation progress as letters are being created
- **Web Interface**: Easy-to-use web UI for non-technical users

## 🚀 Quick Start

### For Replit Deployment

1. **Clone/Fork this repository to Replit**
2. **Set up environment variables**:
   - Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```

### For Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd streamlit-letter-banner
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**:
   - Create `.env` file with your OpenAI API key
   
5. **Run the application**:
   ```bash
   python main.py
   ```

## 🎨 How It Works

1. **Enter a Name**: Type the name you want to create a banner for
2. **Choose Objects**: For each letter, specify what object it should be shaped like
3. **Select Colors**: Pick from beautiful pre-made color palettes or create your own
4. **Generate**: Watch as AI creates each stylized letter
5. **Download**: Get your print-ready banner files

## 📁 Project Structure

```
streamlit-letter-banner/
├── letter_banner/              # Core letter generation logic
│   ├── main.py                # Original CLI interface
│   ├── openai_client.py       # OpenAI API integration
│   ├── color_palettes.py      # Color palette definitions
│   ├── config.py              # Configuration settings
│   ├── layout.py              # Banner layout creation
│   └── utils.py               # Utility functions
├── web/                       # Web service components
│   ├── app.py                 # Flask/FastAPI web application
│   ├── static/                # CSS, JavaScript, images
│   └── templates/             # HTML templates
├── main.py                    # Web service entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎨 Available Color Palettes

- **Earthy Vintage**: Warm beige, forest greens, browns, orange sunset
- **Ocean Breeze**: Deep navy, seafoam green, sandy beige, coral pink
- **Autumn Harvest**: Burnt orange, golden yellow, deep red, chestnut
- **Spring Garden**: Soft pink, sage green, lavender, butter yellow
- **Modern Minimal**: Charcoal gray, soft blue, warm white
- **Sunset Desert**: Terracotta, dusty rose, sage green, golden yellow
- **Bright Blue**: Electric blue, bright yellow, lime green, orange
- **Custom**: Create your own color combination

## 🔧 API Endpoints

### POST `/api/generate-banner`
Start banner generation process
```json
{
  "name": "HELLO",
  "letters": [
    {"letter": "H", "object": "house"},
    {"letter": "E", "object": "elephant"},
    {"letter": "L", "object": "lion"},
    {"letter": "L", "object": "leaf"},
    {"letter": "O", "object": "octopus"}
  ],
  "color_palette": "earthy_vintage"
}
```

### GET `/api/status/{job_id}`
Check generation progress

### GET `/api/download/{job_id}/{file_type}`
Download generated files (banner, pdf, individual letters)

## 🛠️ Technical Details

- **Image Generation**: Uses OpenAI's DALL-E for creating stylized letters
- **Output Format**: 1024x1024 PNG images at 300dpi
- **Print Optimization**: Designed for 8.5x11" paper printing
- **File Management**: Automatic cleanup of temporary files
- **Progress Tracking**: Real-time updates during generation process

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Modern web browser
- Internet connection for AI generation

## 🚀 Deployment

### Replit
- Simply fork this repository to Replit
- Add your OpenAI API key to the secrets/environment
- Click "Run" - Replit handles the rest!

### Other Platforms
- Works on any platform supporting Python web applications
- Ensure environment variables are properly configured
- May need to adjust file paths for different hosting environments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your preferred license here]

## ⚠️ Important Notes

- Requires valid OpenAI API key with image generation access
- Generation time varies based on complexity (typically 30-60 seconds per letter)
- Large names (8+ letters) may take several minutes to complete
- Files are automatically cleaned up after download

## 🆘 Support

If you encounter issues:
1. Check that your OpenAI API key is valid and has sufficient credits
2. Ensure all dependencies are installed correctly
3. Check the console logs for detailed error messages
4. [Create an issue](link-to-issues) for persistent problems

---

*Created with ❤️ for making beautiful, personalized letter banners*
