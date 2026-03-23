import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

# Suppress TF logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

MODEL_PATH  = "dl/saved_model/final_body_model.keras"
IMG_SIZE    = (224, 224)
CLASS_NAMES = ['ectomorph', 'endomorph', 'mesomorph']

# Load model once at startup
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"⚠️  Error loading model: {e}")
    model = None


def predict_body_type(img_path: str):
    """
    Classify body type from an image file.
    Returns: (class_name: str, confidence: float, all_probs: dict)
    """
    if model is None:
        return "Model not loaded", 0.0, {}

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
