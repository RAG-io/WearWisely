"""Central place for all environment-based settings.

Locally: copy .env.example to .env and fill it in (.env is gitignored).
On a host (Hugging Face Space, Render, etc.): set these as environment
variables / secrets in the host's dashboard. Never commit real values.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env if present; harmless if it isn't


def _list(value: str):
    return [v.strip() for v in value.split(",") if v.strip()]


# Hugging Face token (optional but recommended: raises try-on quota).
HF_TOKEN = os.getenv("HF_TOKEN") or None

# Where the trained classifier lives on the Hugging Face Hub.
MODEL_REPO = os.getenv("MODEL_REPO", "")                      # e.g. "username/wearwisely-model"
MODEL_FILENAME = os.getenv("MODEL_FILENAME", "final_body_model.keras")

# Optional: use a local file instead of downloading (handy for development).
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "")

# Frontend origins allowed to call this API (comma-separated).
ALLOWED_ORIGINS = _list(os.getenv("ALLOWED_ORIGINS", "http://localhost:5173"))

# Temp folder for uploaded photos (deleted after each request).
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "temp")
