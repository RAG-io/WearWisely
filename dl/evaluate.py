"""Evaluation for the body-type classifier: one script, detailed statistics.

Run from inside dl/:
    python3 evaluate.py --model saved_model/head_holdout.keras --loader app
    python3 evaluate.py --split val
    python3 evaluate.py --model ~/old_final_body_model.keras

--loader dataset (default) resizes like train.py did (bilinear).
--loader app resizes exactly like the web app (backend/predict.py: load_img, nearest),
              so it shows what the deployed app will really predict. Quote this one.

Always applies mobilenet_v2.preprocess_input (the old evaluation.py skipped it and gave
nonsense). Only meaningful on photos the model has NOT seen: never score head_final.keras
on the 23 test photos, it was trained on them.

With only 23 photos the calibration numbers (ECE, Brier, log loss) are rough indications,
not precise measurements. Read them together with the accuracy interval.
"""
import argparse
import math
import os

import numpy as np

CLASS_NAMES = ["ectomorph", "endomorph", "mesomorph"]   # same order as backend/predict.py
IMG_SIZE = (224, 224)


def wilson(k, n, z=1.96):
    """95% confidence interval for k correct out of n (safe for small n)."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def expected_calibration_error(y_true, probs, bins=5):
    """Average gap between confidence and accuracy, over confidence bins."""
    pred, conf = probs.argmax(1), probs.max(1)
    correct = (pred == y_true).astype(float)
    edges = np.linspace(0, 1, bins + 1)
    ece = 0.0
    for i in range(bins):
        hi_ok = conf <= edges[i + 1] if i == bins - 1 else conf < edges[i + 1]
        m = (conf >= edges[i]) & hi_ok
        if m.any():
            ece += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return ece


def brier_score(y_true, probs):
    return float(np.mean(np.sum((probs - np.eye(len(CLASS_NAMES))[y_true]) ** 2, axis=1)))


def log_loss_value(y_true, probs):
    p = np.clip(probs[np.arange(len(y_true)), y_true], 1e-9, 1.0)
    return float(-np.log(p).mean())


def report(y_true, probs, file_paths=None, class_names=CLASS_NAMES):
    from sklearn.metrics import classification_report, confusion_matrix
    y_true, probs = np.asarray(y_true), np.asarray(probs)
    y_pred = probs.argmax(axis=1)
    conf = probs.max(axis=1)
    n = len(y_true)
    correct = y_pred == y_true
    k = int(correct.sum())
    lo, hi = wilson(k, n)
    labels = list(range(len(class_names)))

    print(f"\nImages evaluated: {n}")
    print(f"Accuracy: {k}/{n} = {k / max(n, 1):.3f}   (95% interval {lo:.2f} to {hi:.2f})")
    print("\nPer-class results:")
    print(classification_report(y_true, y_pred, labels=labels, target_names=class_names, zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print("Confusion matrix (rows = true class, columns = predicted):")
    print(" " * 12 + "".join(f"{c[:6]:>8}" for c in class_names))
    for name, row in zip(class_names, cm):
        print(f"{name:<12}" + "".join(f"{v:>8}" for v in row))

    print("\nCalibration (rough with small n):")
    print(f"  Average confidence:  {conf.mean():.3f}   (compare with accuracy {k / max(n, 1):.3f})")
    print(f"  Confidence when right: {conf[correct].mean():.3f}" if correct.any() else "  No correct predictions")
    print(f"  Confidence when wrong: {conf[~correct].mean():.3f}" if (~correct).any() else "  No wrong predictions")
    print(f"  Expected calibration error (5 bins): {expected_calibration_error(y_true, probs):.3f}")
    print(f"  Brier score: {brier_score(y_true, probs):.3f}   Log loss: {log_loss_value(y_true, probs):.3f}")

    top2 = np.sort(probs, axis=1)[:, -2:]
    close = (top2[:, 1] - top2[:, 0]) < 0.15
    print(f"\nClose calls (top two classes within 0.15): {int(close.sum())} of {n}")
    if close.any():
        print(f"  accuracy on close calls:     {correct[close].mean():.2f}")
    if (~close).any():
        print(f"  accuracy on confident calls: {correct[~close].mean():.2f}")

    print("\nIf you only accept predictions above a confidence threshold:")
    print("  threshold | accepted | coverage | accuracy")
    for t in (0.5, 0.6, 0.7, 0.8, 0.9):
        acc = conf >= t
        txt = f"{correct[acc].mean():.3f}" if acc.any() else "  n/a"
        print(f"  {t:>9.2f} | {int(acc.sum()):>8} | {acc.mean():>7.0%} | {txt}")

    wrong = np.where(~correct)[0]
    print("\nWrong predictions:")
    if len(wrong) == 0:
        print("  none")
    for i in wrong:
        order = np.argsort(probs[i])[::-1]
        name = file_paths[i] if file_paths is not None else f"image {i}"
        print(f"  {name}\n     actual {class_names[y_true[i]]}, predicted {class_names[y_pred[i]]} "
              f"({conf[i]:.2f}), second choice {class_names[order[1]]} ({probs[i, order[1]]:.2f})")


def load_like_app(split):
    """Load test photos with the exact calls backend/predict.py uses."""
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    X, y, paths = [], [], []
    for ci, cls in enumerate(CLASS_NAMES):
        d = os.path.join("dataset", split, cls)
        for f in sorted(os.listdir(d)):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                p = os.path.join(d, f)
                X.append(preprocess_input(tf.keras.utils.img_to_array(tf.keras.utils.load_img(p, target_size=IMG_SIZE))))
                y.append(ci)
                paths.append(p)
    print(f"Found {len(y)} files (loaded like the app)")
    return np.stack(X), np.array(y), paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="saved_model/final_body_model.keras")
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--loader", default="dataset", choices=["dataset", "app"])
    args = ap.parse_args()

    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    model = tf.keras.models.load_model(args.model)
    path = f"dataset/{args.split}"
    if args.loader == "app":
        X, y_true, paths = load_like_app(args.split)
        probs = model.predict(X, batch_size=8, verbose=0)
    else:
        ds = tf.keras.utils.image_dataset_from_directory(
            path, image_size=IMG_SIZE, batch_size=8, shuffle=False, class_names=CLASS_NAMES)
        paths = list(ds.file_paths)
        y_true, probs = [], []
        for images, labels in ds:
            probs.append(model.predict(preprocess_input(images), verbose=0))   # the step the old script missed
            y_true.extend(labels.numpy())
        probs = np.concatenate(probs)
    print(f"\nModel:  {args.model}\nData:   {path}\nLoader: {args.loader}")
    report(y_true, probs, paths)


if __name__ == "__main__":
    main()
