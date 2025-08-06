from fastapi import Header, HTTPException

VALID_API_KEY = "my_secure_api_key"  # Ensure this matches your frontend

def validate_api_key(x_api_key: str = Header(None)):
    if x_api_key is None or x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    return x_api_key
