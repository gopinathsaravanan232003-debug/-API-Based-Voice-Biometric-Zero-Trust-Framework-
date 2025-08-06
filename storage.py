import os
import numpy as np
import json

FEATURES_DIR = "features"
os.makedirs(FEATURES_DIR, exist_ok=True)

def save_features(user_id, features):
    """Saves extracted features to a JSON file"""
    file_path = os.path.join(FEATURES_DIR, f"{user_id}.json")
    with open(file_path, "w") as f:
        json.dump(features.tolist(), f)

def load_features(user_id):
    """Loads stored features from a JSON file"""
    file_path = os.path.join(FEATURES_DIR, f"{user_id}.json")
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "r") as f:
        return np.array(json.load(f))
