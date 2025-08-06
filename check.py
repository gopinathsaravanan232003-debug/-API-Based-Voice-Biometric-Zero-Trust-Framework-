import librosa

audio_path = "C:/Users/gopinath/Documents/finaproject/recordings/sorry.wav"  # Use an existing .wav file

try:
    y, sr = librosa.load(audio_path, sr=16000)
    print("Librosa loaded the file successfully!")
    print("Sample Rate:", sr)
    print("Audio Data Shape:", y.shape)
except Exception as e:
    print(f"Error loading audio: {e}")
