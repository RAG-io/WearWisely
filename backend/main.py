from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, uuid

from .predict import predict_body_type
from .reccomender import get_recommendations

app = FastAPI(title="WearWisely API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER   = "temp"
ALLOWED_TYPES   = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_SIZE_BYTES  = 15 * 1024 * 1024   # 15 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # ── Validate content type ─────────────────────────────────────────────
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{file.content_type}'. Please upload a JPEG, PNG, or WEBP image."
        )

    # ── Read & size-check ─────────────────────────────────────────────────
    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Please upload an image smaller than 15 MB."
        )

    # ── Save to unique temp path ──────────────────────────────────────────
    ext       = os.path.splitext(file.filename)[-1] or ".jpg"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)

    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        body_type, confidence, all_probs = predict_body_type(file_path)
        recommendation_data = get_recommendations(body_type)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    finally:
        # Always clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)

    return {
        "body_type":       body_type,
        "confidence":      confidence,
        "all_probabilities": all_probs,
        "description":     recommendation_data.get("description", []),
        "recommendations": recommendation_data.get("recommendations", {}),
    }
