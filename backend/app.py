import os
import sys
import shutil
import json
from pathlib import Path

# Add the parent folder of app.py to sys.path to ensure local imports resolve correctly
sys.path.insert(0, str(Path(__file__).parent))

from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import AppConfig, is_placeholder
from platforms import PostPayload, FacebookPlatform, InstagramPlatform, LinkedInPlatform
from utils import validate_image, prepare_image, ImageValidationError

app = FastAPI(title="One-Click Social Media Poster API")

# Enable CORS for React frontend (runs on 5173 or 3000 by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development, allow all.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path(__file__).parent / "temp_uploads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/api/config")
def get_config_status():
    """Verify which .env credentials are present (similar to check-config)."""
    import os
    from dotenv import load_dotenv
    # Reload env variables just in case they changed
    _ENV_PATH = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=_ENV_PATH, override=True)
    
    keys = {
        "facebook": ["FACEBOOK_PAGE_ID", "FACEBOOK_ACCESS_TOKEN"],
        "instagram": ["INSTAGRAM_ACCOUNT_ID", "INSTAGRAM_ACCESS_TOKEN"],
        "linkedin": ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_AUTHOR_URN"],
    }
    
    status = {}
    details = {}
    
    for platform, env_keys in keys.items():
        all_present = True
        platform_details = {}
        for key in env_keys:
            val = os.getenv(key, "").strip()
            present = not is_placeholder(val)
            if not present:
                all_present = False
            
            # Mask value
            masked = val[:6] + "..." + val[-4:] if len(val) > 12 and present else "****" if present else None
            platform_details[key] = {
                "present": present,
                "masked": masked
            }
        status[platform] = all_present
        details[platform] = platform_details
        
    return {
        "status": status,
        "details": details
    }


def _build_platform_adapters(cfg: AppConfig, platforms: list[str]) -> dict:
    adapters = {}
    for name in platforms:
        raw_cfg = getattr(cfg, name, None)
        if isinstance(raw_cfg, Exception) or raw_cfg is None:
            continue
        if name == "facebook":
            adapters[name] = FacebookPlatform(raw_cfg)
        elif name == "instagram":
            adapters[name] = InstagramPlatform(raw_cfg)
        elif name == "linkedin":
            adapters[name] = LinkedInPlatform(raw_cfg)
    return adapters


@app.post("/api/post")
async def post_content(
    caption: str = Form(...),
    platforms: str = Form(...),  # Expecting JSON list or comma separated string
    image_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    # Parse platforms
    try:
        if platforms.startswith("["):
            selected_platforms = json.loads(platforms)
        else:
            selected_platforms = [p.strip() for p in platforms.split(",") if p.strip()]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid platforms format. Must be JSON array or comma-separated string.")
        
    if not selected_platforms:
        raise HTTPException(status_code=400, detail="At least one platform must be selected.")
        
    # Check config for selected platforms
    try:
        cfg = AppConfig.from_env(selected_platforms)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

    # Check if any selected platforms are missing credentials
    for platform in selected_platforms:
        raw_cfg = getattr(cfg, platform, None)
        if isinstance(raw_cfg, Exception) or raw_cfg is None:
            raise HTTPException(status_code=400, detail=f"Platform '{platform}' is selected but credentials are not configured or invalid.")

    temp_image_path = None
    prepared_path = None
    
    try:
        # Handle file upload
        if image:
            # Generate a temporary file path
            file_extension = Path(image.filename).suffix or ".jpg"
            temp_image_path = TEMP_DIR / f"upload_{os.urandom(8).hex()}{file_extension}"
            
            with temp_image_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
                
            # Prepare image (e.g. convert to JPEG)
            prepared_path = prepare_image(temp_image_path, TEMP_DIR)

            # Perform validation
            validation_errors = {}
            for p in selected_platforms:
                try:
                    validate_image(prepared_path, p)
                except ImageValidationError as e:
                    validation_errors[p] = str(e)
            
            if validation_errors:
                # If there are validation errors, return them
                raise HTTPException(status_code=400, detail={
                    "message": "Image validation failed for one or more platforms.",
                    "errors": validation_errors
                })
            
        payload_base = {
            "image_path": prepared_path,
            "image_url": image_url,
            "caption": caption
        }
        
        adapters = _build_platform_adapters(cfg, selected_platforms)
        results = []
        
        for platform, adapter in adapters.items():
            payload = PostPayload(**payload_base)
            res = adapter._safe_publish(payload)
            results.append({
                "platform": res.platform,
                "success": res.success,
                "post_id": res.post_id,
                "url": res.url,
                "error": res.error
            })
            
        return {
            "success": any(r["success"] for r in results) if results else False,
            "results": results
        }

    finally:
        # Cleanup temp files
        if temp_image_path and temp_image_path.exists():
            try:
                temp_image_path.unlink()
            except Exception:
                pass
        if prepared_path and prepared_path.exists() and prepared_path != temp_image_path:
            try:
                prepared_path.unlink()
            except Exception:
                pass

@app.get("/health")
def health_check():
    """Simple health check endpoint for monitoring."""
    return {"status": "ok"}

# Serve frontend static assets if the production build exists
dist_path = Path(__file__).parent.parent / "frontend" / "dist"

if dist_path.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")
else:
    @app.api_route("/", methods=["GET", "HEAD"])
    def root():
        return {"message": "One-Click Social Poster API is running! Frontend is not built yet (run npm run build in frontend). API docs at /docs."}

