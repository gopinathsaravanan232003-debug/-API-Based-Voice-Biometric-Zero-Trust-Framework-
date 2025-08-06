from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
import os

app = FastAPI()
RECORDINGS_DIR = "C:/Users/gopinath/Documents/finaproject/recordings/"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# API Key Authentication
API_KEY = "your_secure_api_key"  # Change this to a strong, secret key

def verify_api_key(api_key: str = Form(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/enroll")
async def enroll_user(
    user_id: str = Form(...), 
    audio: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    if not user_id or not audio:
        return {"success": False, "message": "User ID and audio file required!"}

    file_location = os.path.join(RECORDINGS_DIR, f"{user_id}.wav")
    with open(file_location, "wb") as f:
        f.write(await audio.read())

    return {"success": True, "message": "User enrolled successfully!"}