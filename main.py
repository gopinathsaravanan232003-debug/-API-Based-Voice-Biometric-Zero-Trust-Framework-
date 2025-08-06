from fastapi import FastAPI, UploadFile, Form, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
from app.utils.feature_extraction import compare_voice_samples  
from app.secuirty.apikey import validate_api_key

# Define directories
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templets"
RECORDINGS_DIR = BASE_DIR / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/enroll")
async def enroll_user(
    user_id: str = Form(...), 
    audio: UploadFile = None, 
    api_key: str = Depends(validate_api_key)
):
    if not audio:
        return JSONResponse(status_code=400, content={"success": False, "message": "No audio file provided"})

    user_audio_path = RECORDINGS_DIR / f"{user_id}.wav"

    # Save user voice sample
    with open(user_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    return {"success": True, "message": f"User {user_id} enrolled successfully."}

@app.post("/authenticate")
async def authenticate_user(
    user_id: str = Form(...), 
    audio: UploadFile = None, 
    api_key: str = Depends(validate_api_key)
):
    if not audio:
        return JSONResponse(status_code=400, content={"success": False, "message": "No audio file provided"})

    enrolled_audio_path = RECORDINGS_DIR / f"{user_id}.wav"
    auth_audio_path = RECORDINGS_DIR / f"{user_id}_auth.wav"

    if not enrolled_audio_path.exists():
        return JSONResponse(status_code=404, content={"success": False, "message": "User not found. Please enroll first."})

    # Save authentication recording
    with open(auth_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # ✅ Convert file paths to `Path` objects before passing them
    is_match = compare_voice_samples(Path(enrolled_audio_path), Path(auth_audio_path))

    if is_match:
        return {"success": True, "message": "Authentication successful!"}
    else:
        return {"success": False, "message": "Authentication failed: Voice mismatch"}
