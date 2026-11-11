import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

from . import config

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

IMG_SIZE    = (224, 224)
CLASS_NAMES = ['ectomorph', 'endomorph', 'mesomorph']

def _resolve_model_path() -> str:
    """Use LOCAL_MODEL_PATH if set, otherwise download from the HF Hub (cached)."""
    if config.LOCAL_MODEL_PATH:
        if not os.path.exists(config.LOCAL_MODEL_PATH):
            raise FileNotFoundError(f"LOCAL_MODEL_PATH not found: {config.LOCAL_MODEL_PATH}")
        return config.LOCAL_MODEL_PATH
    if not config.MODEL_REPO:
        raise RuntimeError("Set MODEL_REPO (Hugging Face model repo) or LOCAL_MODEL_PATH.")
    from huggingface_hub import hf_hub_download
    return hf_hub_download(
        repo_id=config.MODEL_REPO,
        filename=config.MODEL_FILENAME,
        token=config.HF_TOKEN,   # only needed if the model repo is private
    )


# Load model once at startup. If this fails we want the app to fail loudly,
# not silently serve "Model not loaded".
model = tf.keras.models.load_model(_resolve_model_path())
print("✅ Model loaded successfully.")


def predict_body_type(img_path: str):
    """
    Classify body type from an image file.
    Returns: (class_name: str, confidence: float, all_probs: dict)
    """
    img       = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    preds       = model.predict(img_array, verbose=0)
    probs       = preds[0]
    class_index = int(np.argmax(probs))
    confidence  = float(np.max(probs))

    all_probs = {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}
    print(f"DEBUG probabilities: {all_probs}")

    return CLASS_NAMES[class_index], confidence, all_probs
