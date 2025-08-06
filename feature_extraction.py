import librosa
import numpy as np
import subprocess
from pathlib import Path
import soundfile as sf
from scipy.spatial.distance import cosine

def check_wav_validity(file_path):
    """Check if a WAV file is readable with soundfile."""
    try:
        with sf.SoundFile(file_path) as f:
            print(f"File {file_path} is a valid WAV file.")
    except Exception as e:
        print(f"Invalid WAV file: {e}")

def convert_to_wav(audio_path):
    """Convert any audio file to WAV format with PCM encoding."""
    audio_path = Path(audio_path)
    converted_path = audio_path.with_name(audio_path.stem + "_converted.wav")  # Avoid overwriting

    if converted_path.exists():  # Remove if exists to prevent FFmpeg error
        converted_path.unlink()

    try:
        command = [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-acodec", "pcm_s16le", "-ar", "16000", str(converted_path)
        ]
        subprocess.run(command, check=True, capture_output=True)
        return converted_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")
        return None

def extract_features(audio_path):
    """Extract normalized MFCC features from audio."""
    audio_path = Path(audio_path)

    # Convert to WAV using FFmpeg
    converted_path = audio_path.with_name(audio_path.stem + "_converted.wav")
    command = ["ffmpeg", "-y", "-i", str(audio_path), "-acodec", "pcm_s16le", "-ar", "16000", str(converted_path)]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio: {e.stderr.decode()}")
        return None

    try:
        y, sr = librosa.load(str(converted_path), sr=16000)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # ✅ Normalize MFCC values (fixes inconsistent feature scaling)
        mfccs = (mfccs - np.mean(mfccs)) / np.std(mfccs)

        return np.mean(mfccs, axis=1)  # Take mean across time
    except Exception as e:
        print(f"Error extracting features: {str(e)}")
        return None

def compare_voice_samples(enrolled_audio, auth_audio):
    """Compare two voice samples using Euclidean Distance with strict thresholding."""
    enrolled_features = extract_features(enrolled_audio)
    auth_features = extract_features(auth_audio)

    if enrolled_features is None or auth_features is None:
        print("❌ Error: Feature extraction failed.")
        return False

    # ✅ Euclidean Distance (Strict)
    distance = np.linalg.norm(enrolled_features - auth_features)

    # ✅ Strict Threshold: Use 95th Percentile (Rejects outliers)
    strict_threshold = np.percentile(enrolled_features, 95) * 0.75  # Adjusted for real-world variation

    print(f"📏 Distance Between Samples: {distance:.4f}")
    print(f"🎯 Adaptive Threshold: {strict_threshold:.4f}")

    # 🔥 **Super Strict Authentication Logic**
    if distance <= strict_threshold * 0.85:  # Ensure only strong matches
        print("✅ Voice Match! Authentication Successful.")
        return True
    elif distance > strict_threshold * 1.15:
        print("❌ Voice Mismatch! Authentication Failed.")
        return False
    else:
        print("⚠️ Uncertain Match! Re-authentication Required.")
        return False  # Forces retry if it's too close to threshold