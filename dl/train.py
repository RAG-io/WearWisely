"""Train the final classifier head and save it as a Keras model.

Run from inside dl/ (after augment.py and cross_validate.py):

    python3 train.py --mode holdout   # trains on train+val photos only -> head_holdout.keras
                                      # then score it on the 23 test photos:
                                      # python3 evaluate.py --model saved_model/head_holdout.keras --loader app
    python3 train.py --mode final     # trains on ALL 126 photos -> head_final.keras
                                      # (the file to upload to Hugging Face; never score it on the test photos)

MobileNetV2 stays frozen. Only a small linear layer (logistic regression on the saved features)
is trained, with the regularization strength C chosen by cross_validate.py (cv_best.json).
The result is saved as a Keras model the web app loads with no code changes, plus a .json record.
"""
import argparse
import json
import os
from datetime import datetime

import numpy as np
import sklearn
import tensorflow as tf
from sklearn.linear_model import LogisticRegression
from tensorflow.keras import layers, models, applications

# ==============================
# 1️⃣ CONFIGURATION
# ==============================
CLASS_NAMES = ["ectomorph", "endomorph", "mesomorph"]   # same order as backend/predict.py
IMG_SIZE = (224, 224)

FEATURES_PATH = "features.npz"      # made by augment.py
CV_PATH = "cv_best.json"            # made by cross_validate.py
SAVE_DIR = "saved_model"

DEFAULT_C = 0.01                    # only used if neither --C nor cv_best.json is available
MAX_ITER = 3000
CHECK_PHOTOS = 8                    # photos used to check the Keras model against the head
CHECK_TOLERANCE = 2e-3

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["holdout", "final"], required=True,
                    help="holdout = train+val photos only, final = all photos")
parser.add_argument("--C", type=float, default=None,
                    help="regularization strength (default: from cv_best.json, else 0.01)")
args = parser.parse_args()
MODE = args.mode

MODEL_SAVE_PATH = f"{SAVE_DIR}/head_{MODE}.keras"
META_SAVE_PATH = f"{SAVE_DIR}/head_{MODE}.json"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==============================
# 2️⃣ LOAD FEATURES
# ==============================
data = np.load(FEATURES_PATH)
feats, group, is_aug, y = data["feats"], data["group"], data["is_aug"], data["y"]
splits, paths = data["splits"], data["paths"]
print(f"Loaded features for {len(y)} photos ({len(feats)} rows including augmented copies)")

# ==============================
# 3️⃣ CHOOSE THE RECIPE
# ==============================
cv = None
if os.path.exists(CV_PATH):
    with open(CV_PATH) as f:
        cv = json.load(f)

if args.C is not None:
    C, use_aug, source = args.C, True, "--C option"
    if not (cv and float(cv["C"]) == C):
        cv = None                   # the cross-validation result belongs to a different C
elif cv is not None:
    C, use_aug, source = float(cv["C"]), bool(cv["aug"]), f"{CV_PATH} (chosen by cross_validate.py)"
else:
    C, use_aug, source = DEFAULT_C, True, f"default {DEFAULT_C} (run cross_validate.py to choose it)"
print(f"Mode: {MODE}")
print(f"Recipe: C={C}, augmented rows {'used' if use_aug else 'not used'}   [{source}]")

# ==============================
# 4️⃣ SELECT TRAINING PHOTOS
# ==============================
if MODE == "holdout":
    photos = np.where(np.isin(splits, ["train", "val"]))[0]     # the test photos stay unseen
else:
    photos = np.arange(len(y))

rows = np.isin(group, photos)
if not use_aug:
    rows &= ~is_aug

per_class = {CLASS_NAMES[c]: int((y[photos] == c).sum()) for c in range(len(CLASS_NAMES))}
print(f"Training on {len(photos)} photos {per_class}; {int(rows.sum())} rows including augmented copies")

# ==============================
# 5️⃣ TRAIN THE HEAD
# ==============================
clf = LogisticRegression(C=C, class_weight="balanced", max_iter=MAX_ITER)
clf.fit(feats[rows], y[group[rows]])
assert list(clf.classes_) == [0, 1, 2], "unexpected class set"

own = np.where(~is_aug & np.isin(group, photos))[0]
train_acc = float((clf.predict(feats[own]) == y[group[own]]).mean())
print(f"Accuracy on its own training photos: {train_acc:.3f}   <- NOT an estimate of real accuracy")
if cv:
    lo, hi = cv["interval_95"]
    print(f"Cross-validated accuracy of this recipe: {cv['cv_accuracy']:.3f} "
          f"(95% interval {lo:.2f} to {hi:.2f} on {cv['n_photos']} photos)   <- quote this one")

# ==============================
# 6️⃣ BUILD THE KERAS MODEL
# ==============================
base_model = applications.MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)
base_model.trainable = False        # frozen: the CNN is not trained

inputs = layers.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
outputs = layers.Dense(len(CLASS_NAMES), activation="softmax")(x)

model = models.Model(inputs, outputs)
model.layers[-1].set_weights([clf.coef_.T.astype("float32"), clf.intercept_.astype("float32")])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ==============================
# 7️⃣ CHECK THE KERAS MODEL
# ==============================
# The Keras model must give the same probabilities as the scikit-learn head on real photos,
# otherwise a transposed weight or different preprocessing would slip through unnoticed.
check_rows = np.where(~is_aug)[0][:CHECK_PHOTOS]
check_images = np.stack([
    tf.keras.utils.img_to_array(tf.keras.utils.load_img(paths[i], target_size=IMG_SIZE))
    for i in check_rows
]).astype("float32")

p_keras = model.predict(applications.mobilenet_v2.preprocess_input(check_images), verbose=0)
p_head = clf.predict_proba(feats[check_rows])
diff = float(np.abs(p_keras - p_head).max())
print(f"Check: Keras model vs scikit-learn head on {CHECK_PHOTOS} photos, largest probability difference = {diff:.5f}")
if diff > CHECK_TOLERANCE:
    raise SystemExit("MISMATCH: the exported model does not reproduce the head. Not saving. "
                     "Check that augment.py loads images the same way as backend/predict.py.")

# ==============================
# 8️⃣ SAVE
# ==============================
model.save(MODEL_SAVE_PATH)
print(f"✅ Saved {MODEL_SAVE_PATH}  ({os.path.getsize(MODEL_SAVE_PATH) / 1e6:.1f} MB)")

record = {
    "model_file": os.path.basename(MODEL_SAVE_PATH),
    "mode": MODE,
    "created": datetime.now().isoformat(timespec="seconds"),
    "classes": CLASS_NAMES,
    "architecture": "MobileNetV2 (ImageNet weights, frozen) + global average pooling + "
                    "Dense(3, softmax) whose weights come from a logistic-regression head",
    "recipe": {"C": C, "class_weight": "balanced", "augmented_rows_used": use_aug, "source": source},
    "trained_on": {"photos": int(len(photos)), "rows": int(rows.sum()), "per_class": per_class},
    "training_accuracy_on_own_photos": round(train_acc, 3),
    "cross_validation": cv,
    "preprocessing": "load_img(target_size=(224, 224)) (nearest-neighbour resize), then "
                     "mobilenet_v2.preprocess_input, exactly as backend/predict.py; "
                     "the model itself contains no preprocessing",
    "versions": {"tensorflow": tf.__version__, "scikit_learn": sklearn.__version__, "numpy": np.__version__},
    "note": ("Trained on ALL photos including the test split: do not score it on the test photos."
             if MODE == "final" else "Trained on the train+val photos only; evaluate it on the test split."),
}
with open(META_SAVE_PATH, "w") as f:
    json.dump(record, f, indent=2)
print(f"✅ Saved {META_SAVE_PATH}  (how this model was made)")

if MODE == "holdout":
    print(f"Next: python3 evaluate.py --model {MODEL_SAVE_PATH} --loader app")
else:
    print("Next: upload this file (and head_final.json, optional but handy) to your Hugging Face "
          "model repo, then set MODEL_FILENAME=head_final.keras in .env")
