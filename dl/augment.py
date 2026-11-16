"""Step 1: augment + extract features (needs TensorFlow; run from inside dl/):

    python3 augment.py

Turns every ORIGINAL photo (train + val + test, never the aug_ files) into a 1280-number
MobileNetV2 feature vector, using the frozen ImageNet weights and exactly the same
preprocessing as the web app. For each photo it also stores N_AUG lightly augmented
versions, so the head can later be trained on variety without re-running the CNN.
Output: features.npz (a few MB). Takes about a minute or two on CPU.
"""
import os
import numpy as np

CLASS_NAMES = ["ectomorph", "endomorph", "mesomorph"]   # same order as backend/predict.py
ROOT = "dataset"
SPLITS = ["train", "val", "test"]
EXT = (".jpg", ".jpeg", ".png")
N_AUG = 10
SEED = 42
OUT = "features.npz"


def collect():
    items = []
    for split in SPLITS:
        for ci, cls in enumerate(CLASS_NAMES):
            d = os.path.join(ROOT, split, cls)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.lower().endswith(EXT) and not f.startswith("aug_"):
                    items.append((os.path.join(d, f), ci, split))
    return items


def main():
    import tensorflow as tf
    from tensorflow.keras import applications, layers

    tf.keras.utils.set_random_seed(SEED)
    items = collect()
    n = len(items)
    print(f"Original photos found: {n}")
    for ci, cls in enumerate(CLASS_NAMES):
        print(f"  {cls}: {sum(1 for _, c, _ in items if c == ci)}")

    X = np.stack([
        tf.keras.utils.img_to_array(tf.keras.utils.load_img(p, target_size=(224, 224)))
        for p, _, _ in items
    ]).astype("float32")
    y = np.array([c for _, c, _ in items])

    base = applications.MobileNetV2(weights="imagenet", include_top=False,
                                    pooling="avg", input_shape=(224, 224, 3))
    aug = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.06),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.15),
    ])

    def features(images, augment):
        out = []
        for i in range(0, len(images), 32):
            b = tf.convert_to_tensor(images[i:i + 32])
            if augment:
                b = aug(b, training=True)
            b = applications.mobilenet_v2.preprocess_input(b)
            out.append(base(b, training=False).numpy())      # frozen: training=False
        return np.concatenate(out)

    feats, groups, is_aug = [], [], []
    for r in range(N_AUG + 1):                                # r = 0 is the untouched original
        print(f"  extracting round {r}/{N_AUG}...", flush=True)
        feats.append(features(X, augment=(r > 0)))
        groups.append(np.arange(n))
        is_aug.append(np.full(n, r > 0))
    np.savez_compressed(
        OUT,
        feats=np.concatenate(feats).astype("float32"),
        group=np.concatenate(groups),
        is_aug=np.concatenate(is_aug),
        y=y,
        paths=np.array([p for p, _, _ in items]),
        splits=np.array([s for _, _, s in items]),
    )
    print(f"Saved {OUT}: {n} photos x {N_AUG + 1} versions = {n * (N_AUG + 1)} rows")


if __name__ == "__main__":
    main()
