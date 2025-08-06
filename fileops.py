import os
import re
from fastapi import HTTPException

def save_file(user_id: str, audio_file, purpose: str) -> str:
    """
    Saves the uploaded audio file in the appropriate directory.

    Args:
        user_id (str): The ID of the user.
        audio_file (UploadFile): The uploaded audio file.
        purpose (str): The purpose of the file (e.g., 'enroll', 'authenticate').

    Returns:
        str: The full path of the saved file.

    Raises:
        HTTPException: If any issue occurs while saving the file.
    """
    try:
        # Validate user_id
        if not user_id.strip():
            raise ValueError("User ID cannot be empty.")

        # Sanitize user_id and filename to avoid unsafe characters
        sanitized_user_id = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
        sanitized_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", audio_file.filename)

        # Ensure filename is not empty after sanitization
        if not sanitized_filename:
            raise ValueError("Invalid audio file name.")

        # Define file path
        directory = os.path.join("recordings", purpose, sanitized_user_id)
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, sanitized_filename)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(audio_file.file.read())

        return file_path

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save file: {str(e)}"
        )

