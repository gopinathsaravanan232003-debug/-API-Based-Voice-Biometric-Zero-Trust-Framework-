from fastapi import FastAPI, UploadFile, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
import librosa
import numpy as np
import shutil
from scipy.spatial.distance import euclidean
from pathlib import Path
from datetime import datetime
import os
import hashlib

# Define directories
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = "C:/finaproject/templets"
RECORDINGS_DIR = Path("C:/finaproject/recordings/")
RECORDINGS_DIR.mkdir(exist_ok=True)  # Create recordings directory if not exists

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Function to extract voice features using MFCC
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)  # Load audio
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # Extract MFCC features
    return np.mean(mfcc, axis=1)  # Return averaged MFCCs

# Function to hash audio files for replay attack prevention
def hash_audio(file_path):
    """ Hashes audio file to prevent replay attacks. """
    with open(file_path, "rb") as file:
        audio_data = file.read()
        return hashlib.sha256(audio_data).hexdigest()

# Function to validate the recording timestamp (anti-replay)
def validate_timestamp(file_path):
    """ Ensure the audio is recorded within an acceptable time window. """
    creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
    current_time = datetime.now()
    time_diff = (current_time - creation_time).seconds
    max_age = 3600  # Maximum age for voice samples (1 hour)
    if time_diff > max_age:
        raise HTTPException(status_code=400, detail="Audio is too old. Please record again.")
    return True

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/enroll")
async def enroll_user(user_id: str = Form(...), audio: UploadFile = None):
    if not audio:
        return {"success": False, "message": "No audio file provided"}

    user_audio_path = RECORDINGS_DIR / f"{user_id}.wav"

    # Save user voice sample
    with open(user_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # Validate the audio file (timestamp and replay)
    try:
        validate_timestamp(user_audio_path)
    except HTTPException as e:
        return {"success": False, "message": str(e.detail)}

    # Hash the audio to store a unique signature
    audio_hash = hash_audio(user_audio_path)
    return {"success": True, "message": f"User {user_id} enrolled successfully.", "audio_hash": audio_hash}

@app.post("/authenticate")
async def authenticate_user(user_id: str = Form(...), audio: UploadFile = None):
    if not audio:
        return {"success": False, "message": "No audio file provided"}

    enrolled_audio_path = RECORDINGS_DIR / f"{user_id}.wav"

    if not enrolled_audio_path.exists():
        return {"success": False, "message": "User not found. Please enroll first."}

    auth_audio_path = RECORDINGS_DIR / f"{user_id}_auth.wav"

    # Save authentication recording
    with open(auth_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # Validate the authentication recording (timestamp and replay)
    try:
        validate_timestamp(auth_audio_path)
    except HTTPException as e:
        return {"success": False, "message": str(e.detail)}

    # Extract features for both enrolled and authentication audio
    enrolled_features = extract_features(str(enrolled_audio_path))
    auth_features = extract_features(str(auth_audio_path))

    # Compare voice samples using Euclidean distance
    distance = euclidean(enrolled_features, auth_features)
    threshold = 50  # Adjust threshold as needed

    if distance < threshold:
        # Check for replay attack by comparing the hash of the new audio
        audio_hash = hash_audio(auth_audio_path)
        enrolled_audio_hash = hash_audio(enrolled_audio_path)

        if audio_hash == enrolled_audio_hash:
            return {"success": False, "message": "Replay attack detected. Voice sample reused."}

        return {"success": True, "message": "Authentication successful!"}
    else:
        return {"success": False, "message": "Authentication failed. Voice does not match."}