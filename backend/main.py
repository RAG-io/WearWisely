from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, uuid, base64, httpx
from gradio_client import Client, handle_file

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

@app.post("/try-on")
async def try_on(user_image: UploadFile = File(...), garm_url: str = Form(...)):
    # ── Validate user image ─────────────────────────────────────────────
    if user_image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported user image type.")
        
    user_bytes = await user_image.read()
    if len(user_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large.")

    # ── Save files to temp path ──────────────────────────────────────────
    ext = os.path.splitext(user_image.filename)[-1] or ".jpg"
    user_path = os.path.join(UPLOAD_FOLDER, f"vton_user_{uuid.uuid4().hex}{ext}")
    garm_path = os.path.join(UPLOAD_FOLDER, f"vton_garm_{uuid.uuid4().hex}.jpg")
    
    with open(user_path, "wb") as f:
        f.write(user_bytes)
    
    try:
        # ── Download Garment ─────────────────────────────────────────────
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as http_client:
            resp = await http_client.get(garm_url)
            resp.raise_for_status()
            with open(garm_path, "wb") as f:
                f.write(resp.content)
        
        # ── Perform Virtual Try-On via IDM-VTON API ─────────────────────
        hf_token = os.getenv("HF_TOKEN")
        try:
            client = Client("yisol/IDM-VTON", token=hf_token) if hf_token else Client("yisol/IDM-VTON")
        except Exception as api_err:
            raise HTTPException(status_code=503, detail="HuggingFace API space is busy or unavailable. Please try again later or provide an HF_TOKEN.")
        
        import time
        
        # The specific parameter signature for the IDM-VTON gradio space
        # We wrap this in a retry loop because Hugging Face ZeroGPUs often fail
        # with "No GPU was available" during peak global traffic.
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result_tuple = client.predict(
                    dict(background=handle_file(user_path), layers=[], composite=None),
                    handle_file(garm_path),
                    "Garment on upper body", 
                    True,   # is_checked (use auto mask)
                    False,  # is_checked_crop (False preserves full body/head)
                    30,     # denoise_steps
                    42,     # seed
                    api_name="/tryon"
                )
                break # Success!
            except Exception as e:
                if "No GPU was available" in str(e) and attempt < max_retries - 1:
                    print(f"ZeroGPU busy. Retrying attempt {attempt + 1}/{max_retries} in 5 seconds...")
                    time.sleep(5)
                else:
                    raise e # Re-raise if it's a different error or we're out of retries
        
        # Result tuple is (output_filepath, masked_image_output_filepath)
        output_filepath = result_tuple[0]
        
        # Convert generated image to base64 for easy transport to frontend
        with open(output_filepath, "rb") as final_img:
            encoded_str = base64.b64encode(final_img.read()).decode("utf-8")
        
        return {"image_base64": f"data:image/webp;base64,{encoded_str}"}
        
    except httpx.HTTPError as he:
        raise HTTPException(status_code=400, detail=f"Failed to fetch garment image from Amazon: {str(he)}")
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="HuggingFace ZeroGPU quota exceeded. Please configure an HF_TOKEN in the environment variables.")
        raise HTTPException(status_code=500, detail=f"Virtual Try-On processing failed: {error_msg}")
    finally:
        if os.path.exists(user_path): os.remove(user_path)
        if os.path.exists(garm_path): os.remove(garm_path)
