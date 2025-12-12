"""
FastAPI web application for Letter Banner Generator service
"""

import os
import uuid
import asyncio
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel, validator

# Import our existing letter banner logic
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from letter_banner import config
from letter_banner.color_palettes import COLOR_PALETTES
from letter_banner.image_generator import generate_stylized_letter
from letter_banner.layout import create_banner_layout, create_pdf_with_all_letters
from letter_banner.utils import load_api_key
from letter_banner.theme_generator import generate_theme_variations
from letter_banner.image_editor import edit_letter_image

# Initialize FastAPI app
app = FastAPI(
    title="Letter Banner Generator",
    description="Create stylized letter banners where each letter is shaped like objects",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Global storage for job status and results
jobs_storage: Dict[str, Dict[str, Any]] = {}
executor = ThreadPoolExecutor(max_workers=10)  # Allow parallel letter generation

# Cleanup old jobs periodically
CLEANUP_INTERVAL = 3600  # 1 hour
MAX_JOB_AGE = 24 * 3600  # 24 hours

class LetterRequest(BaseModel):
    letter: str
    object: str
    
    @validator('letter')
    def validate_letter(cls, v):
        if len(v) != 1 or not v.isalpha():
            raise ValueError('Letter must be a single alphabetic character')
        return v.upper()
    
    @validator('object')
    def validate_object(cls, v):
        if not v.strip():
            raise ValueError('Object description cannot be empty')
        return v.strip()

class BannerGenerationRequest(BaseModel):
    name: str
    letters: List[LetterRequest]
    color_palette: str = "earthy_vintage"
    model: str = "gemini-3-pro-image-preview"
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        # Check if name matches letters
        name_letters = [c.upper() for c in v.strip() if c.isalpha()]
        return v.strip()
    
    @validator('letters')
    def validate_letters(cls, v):
        if not v:
            raise ValueError('At least one letter is required')
        if len(v) > 20:  # Reasonable limit
            raise ValueError('Maximum 20 letters allowed')
        return v
    
    @validator('color_palette')
    def validate_palette(cls, v):
        if v not in COLOR_PALETTES and v != "custom":
            raise ValueError(f'Invalid color palette. Must be one of: {list(COLOR_PALETTES.keys())} or "custom"')
        return v
    
    @validator('model')
    def validate_model(cls, v):
        if v not in config.SUPPORTED_MODELS:
            raise ValueError(f'Invalid model. Must be one of: {list(config.SUPPORTED_MODELS.keys())}')
        return v

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    current_step: str
    total_letters: int
    completed_letters: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    files: Optional[Dict[str, str]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    print("🚀 Starting Letter Banner Generator Web Service")
    
    # Load API key
    if not load_api_key():
        print("❌ Failed to load OpenAI API key. Service may not function properly.")
    
    # Create output directory
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Start cleanup task
    asyncio.create_task(cleanup_old_jobs())
    
    print("✅ Service initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "color_palettes": COLOR_PALETTES
    })

@app.get("/api/palettes")
async def get_color_palettes():
    """Get available color palettes."""
    return {"palettes": COLOR_PALETTES}

@app.get("/api/models")
async def get_available_models():
    """Get available image generation models with pricing and features."""
    return {
        "models": config.SUPPORTED_MODELS,
        "default_model": config.DEFAULT_MODEL
    }

class ThemeVariationRequest(BaseModel):
    name: str
    theme: str
    model: str = "gemini-2.0-flash-exp"
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('theme')
    def validate_theme(cls, v):
        if not v.strip():
            raise ValueError('Theme cannot be empty')
        return v.strip()

@app.post("/api/generate-theme-variations")
async def generate_theme_variations_api(request: ThemeVariationRequest):
    """Generate creative theme variations for each letter from a single overarching theme."""
    try:
        variations = generate_theme_variations(
            name=request.name,
            theme=request.theme,
            model=request.model
        )
        
        if variations:
            return {
                "success": True,
                "variations": variations,
                "name": request.name,
                "theme": request.theme
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate theme variations")
            
    except Exception as e:
        print(f"❌ Error in theme variation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-banner")
async def generate_banner(
    request: BannerGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Start banner generation process."""
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    job_status = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "current_step": "Initializing...",
        "total_letters": len(request.letters),
        "completed_letters": 0,
        "error_message": None,
        "created_at": datetime.now(),
        "completed_at": None,
        "files": None,
        "request_data": request.dict()
    }
    
    jobs_storage[job_id] = job_status
    
    # Start background generation
    background_tasks.add_task(process_banner_generation, job_id, request)
    
    return {"job_id": job_id, "status": "pending", "message": "Banner generation started"}

@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the current status of a banner generation job."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    
    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        total_letters=job["total_letters"],
        completed_letters=job["completed_letters"],
        error_message=job.get("error_message"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        files=job.get("files")
    )

@app.get("/api/download/{job_id}/{file_type}")
async def download_file(job_id: str, file_type: str):
    """Download generated banner files."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if not job.get("files") or file_type not in job["files"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = job["files"][file_type]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File no longer exists")
    
    # Determine the appropriate filename for download
    if file_type == "banner":
        filename = f"{job['request_data']['name']}_banner.png"
    elif file_type == "pdf":
        filename = f"{job['request_data']['name']}_letters.pdf"
    else:
        filename = os.path.basename(file_path)
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

class EditLetterRequest(BaseModel):
    edit_prompt: str
    model: str = "gemini-3-pro-image-preview"
    
    @validator('edit_prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Edit prompt cannot be empty')
        return v.strip()

@app.post("/api/edit-letter/{job_id}/{letter_index}")
async def edit_letter(job_id: str, letter_index: int, request: EditLetterRequest, background_tasks: BackgroundTasks):
    """Edit a specific letter with an image-to-image prompt."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before editing")
    
    if not job.get("files"):
        raise HTTPException(status_code=400, detail="No files available to edit")
    
    # Get the letter file
    letter_key = f"letter_{letter_index}"
    if letter_key not in job["files"]:
        raise HTTPException(status_code=404, detail=f"Letter {letter_index} not found")
    
    original_path = job["files"][letter_key]
    
    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Original image file not found")
    
    # Create edited filename
    base_dir = os.path.dirname(original_path)
    base_name = os.path.basename(original_path)
    name_without_ext = os.path.splitext(base_name)[0]
    edited_path = os.path.join(base_dir, f"{name_without_ext}_edited.png")
    
    # Perform the edit
    try:
        result_path = await asyncio.get_event_loop().run_in_executor(
            executor,
            edit_letter_image,
            original_path,
            request.edit_prompt,
            edited_path,
            request.model
        )
        
        if result_path:
            # Update job storage with edited image
            job["files"][letter_key] = result_path
            
            # Track edit history
            if "edit_history" not in job:
                job["edit_history"] = {}
            if letter_key not in job["edit_history"]:
                job["edit_history"][letter_key] = []
            
            job["edit_history"][letter_key].append({
                "prompt": request.edit_prompt,
                "model": request.model,
                "timestamp": datetime.now().isoformat(),
                "original_path": original_path,
                "edited_path": result_path
            })
            
            return {
                "success": True,
                "message": "Letter edited successfully",
                "edited_path": result_path,
                "letter_index": letter_index
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to edit image")
            
    except Exception as e:
        print(f"❌ Error editing letter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-pdf/{job_id}")
async def generate_pdf_endpoint(job_id: str):
    """Generate PDF with current letters after user approval."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before generating PDF")
    
    if not job.get("files"):
        raise HTTPException(status_code=400, detail="No files available")
    
    try:
        # Get current letter paths (may include edited versions)
        letter_paths = []
        for i in range(job["total_letters"]):
            letter_key = f"letter_{i}"
            if letter_key in job["files"]:
                letter_paths.append(job["files"][letter_key])
        
        if not letter_paths:
            raise HTTPException(status_code=400, detail="No letter files found")
        
        # Get timestamp and name from request data
        request_data = job.get("request_data", {})
        name = request_data.get("name", "BANNER")
        
        # Extract timestamp from existing files
        import re
        first_file = os.path.basename(letter_paths[0])
        timestamp_match = re.search(r'_(\d{8}_\d{6})', first_file)
        run_timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate PDF with current images
        pdf_path = await asyncio.get_event_loop().run_in_executor(
            executor,
            create_pdf_with_all_letters,
            letter_paths,
            config.OUTPUT_DIR,
            run_timestamp,
            name
        )
        
        if pdf_path:
            # Update job storage with PDF path
            job["files"]["pdf"] = pdf_path
            
            return {
                "success": True,
                "message": "PDF generated successfully",
                "pdf_path": pdf_path
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_banner_generation(job_id: str, request: BannerGenerationRequest):
    """Process banner generation in the background."""
    job = jobs_storage[job_id]
    
    try:
        job["status"] = "processing"
        job["current_step"] = "Setting up generation..."
        
        # Create timestamp for this run
        run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get color palette
        if request.color_palette in COLOR_PALETTES:
            color_palette = COLOR_PALETTES[request.color_palette]
        else:
            # For now, default to earthy_vintage if custom is selected
            # TODO: Handle custom palettes from frontend
            color_palette = COLOR_PALETTES["earthy_vintage"]
        
        job["current_step"] = f"Using color palette: {color_palette['name']}"
        
        # Get model info
        model_info = config.SUPPORTED_MODELS.get(request.model, config.SUPPORTED_MODELS[config.DEFAULT_MODEL])
        job["current_step"] = f"Using model: {model_info['name']}"
        
        # Generate all letters in parallel
        job["current_step"] = f"Generating all {len(request.letters)} letters simultaneously with {model_info['name']}..."
        job["progress"] = 10
        
        # Create tasks for all letters
        loop = asyncio.get_event_loop()
        letter_tasks = []
        
        for i, letter_req in enumerate(request.letters):
            task = loop.run_in_executor(
                executor,
                generate_stylized_letter,
                letter_req.letter,
                letter_req.object,
                config.OUTPUT_DIR,
                run_timestamp,
                color_palette,
                request.model
            )
            letter_tasks.append((i, letter_req.letter, task))
        
        # Wait for letters to complete and update progress in real-time
        generated_letter_paths = []
        completed_count = 0
        
        # Wait for all tasks to complete and collect results
        results = await asyncio.gather(*[task for _, _, task in letter_tasks], return_exceptions=True)
        
        # Process results and update progress
        for (i, letter, _), result in zip(letter_tasks, results):
            try:
                if isinstance(result, Exception):
                    print(f"⚠️ Error generating letter '{letter}': {result}")
                    continue
                
                if result:  # result is the letter_path
                    generated_letter_paths.append(result)
                    completed_count += 1
                    job["completed_letters"] = completed_count
                    job["progress"] = 10 + int((completed_count / len(request.letters)) * 70)  # 10-80%
                    job["current_step"] = f"Generated letter '{letter}' ({completed_count}/{len(request.letters)} complete)"
                    print(f"✅ Completed letter '{letter}' ({completed_count}/{len(request.letters)})")
                else:
                    print(f"⚠️ Failed to generate letter '{letter}'")
            except Exception as e:
                print(f"⚠️ Error processing letter '{letter}': {e}")
                continue
        
        if not generated_letter_paths:
            raise Exception("Failed to generate any letters")
        
        job["current_step"] = "Creating banner layout..."
        job["progress"] = 85
        
        # Create printable banner layout
        banner_path = await loop.run_in_executor(
            executor,
            create_banner_layout,
            generated_letter_paths,
            config.OUTPUT_DIR,
            run_timestamp,
            None  # Auto-calculate letters per row
        )
        
        job["current_step"] = "Creating PDF compilation..."
        job["progress"] = 95
        
        # Create PDF with all letters
        pdf_path = await loop.run_in_executor(
            executor,
            create_pdf_with_all_letters,
            generated_letter_paths,
            config.OUTPUT_DIR,
            run_timestamp,
            request.name
        )
        
        # Store file paths
        files = {}
        if banner_path:
            files["banner"] = banner_path
        if pdf_path:
            files["pdf"] = pdf_path
        
        # Add individual letter files
        for i, letter_path in enumerate(generated_letter_paths):
            files[f"letter_{i}"] = letter_path
        
        # Calculate estimated cost based on selected model
        model_info = config.SUPPORTED_MODELS.get(request.model, config.SUPPORTED_MODELS[config.DEFAULT_MODEL])
        cost_per_image = model_info["cost_per_image"]
        estimated_cost = len(generated_letter_paths) * cost_per_image
        
        job["files"] = files
        job["status"] = "completed"
        job["progress"] = 100
        job["current_step"] = "Banner generation completed!"
        job["completed_at"] = datetime.now()
        job["model_used"] = request.model
        job["cost_info"] = {
            "letters_generated": len(generated_letter_paths),
            "cost_per_letter": cost_per_image,
            "estimated_total_cost": estimated_cost,
            "currency": "USD",
            "model": model_info["name"]
        }
        
        print(f"✅ Banner generation completed for job {job_id}")
        print(f"💰 Estimated cost: ${estimated_cost:.2f} USD ({len(generated_letter_paths)} letters × ${cost_per_image})")
        
    except Exception as e:
        print(f"❌ Banner generation failed for job {job_id}: {e}")
        job["status"] = "failed"
        job["error_message"] = str(e)
        job["current_step"] = f"Generation failed: {str(e)}"

async def cleanup_old_jobs():
    """Periodically clean up old jobs and their files."""
    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL)
            
            current_time = datetime.now()
            jobs_to_remove = []
            
            for job_id, job in jobs_storage.items():
                job_age = current_time - job["created_at"]
                
                if job_age.total_seconds() > MAX_JOB_AGE:
                    # Clean up files
                    if job.get("files"):
                        for file_path in job["files"].values():
                            try:
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                            except Exception as e:
                                print(f"Failed to remove file {file_path}: {e}")
                    
                    jobs_to_remove.append(job_id)
            
            # Remove old jobs from storage
            for job_id in jobs_to_remove:
                del jobs_storage[job_id]
                print(f"🧹 Cleaned up old job: {job_id}")
                
        except Exception as e:
            print(f"Error in cleanup task: {e}")

@app.get("/api/docs")
async def api_documentation():
    """API documentation endpoint."""
    return {
        "title": "Letter Banner Generator API",
        "version": "1.0.0",
        "description": "Create stylized letter banners where each letter is shaped like objects",
        "endpoints": {
            "POST /api/generate-banner": {
                "description": "Start banner generation process",
                "body": {
                    "name": "string - Name for the banner",
                    "letters": "array - List of {letter, object} pairs",
                    "color_palette": "string - Color palette name"
                },
                "response": {"job_id": "string", "status": "string"}
            },
            "GET /api/status/{job_id}": {
                "description": "Check generation progress",
                "response": "JobStatus object with progress info"
            },
            "GET /api/download/{job_id}/{file_type}": {
                "description": "Download generated files",
                "file_types": ["banner", "pdf", "letter_0", "letter_1", "..."]
            },
            "GET /api/palettes": {
                "description": "Get available color palettes",
                "response": {"palettes": "object"}
            },
            "GET /health": {
                "description": "Health check endpoint",
                "response": {"status": "string", "active_jobs": "number"}
            }
        },
        "color_palettes": list(COLOR_PALETTES.keys()),
        "limits": {
            "max_letters": 20,
            "max_name_length": 20,
            "file_retention": "24 hours"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_jobs": len([j for j in jobs_storage.values() if j["status"] in ["pending", "processing"]]),
        "total_jobs": len(jobs_storage)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)
