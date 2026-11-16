"""Step 2: choose the regularization (no TensorFlow needed): cross-validate a small classifier on the saved features.

    python3 cross_validate.py

Uses ALL original photos (train+val+test merged) with stratified 5-fold cross-validation,
repeated 3 times. Every photo is scored exactly once per repeat by a model that never saw
it (or any augmented copy of it), so the result rests on ~126 photos, not 23.
It compares logistic-regression heads with different regularization strengths (C), with
and without the augmented rows, and reports accuracy, confidence and calibration.
Nothing here is saved as a model; this only tells us which recipe to trust.
"""
import argparse
import csv
import json
import math

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

CLASS_NAMES = ["ectomorph", "endomorph", "mesomorph"]
C_GRID = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def ece(conf, correct, bins=5):
    """Expected calibration error: gap between confidence and accuracy, averaged over bins."""
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            total += m.mean() * abs(conf[m].mean() - correct[m].mean())
    return total


def one_repeat(feats, group, is_aug, y_orig, C, use_aug, seed, folds=5):
    n = len(y_orig)
    oof = np.zeros((n, len(CLASS_NAMES)))
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for tr_g, te_g in skf.split(np.arange(n), y_orig):
        assert not set(tr_g) & set(te_g)                       # no photo on both sides
        tr = np.isin(group, tr_g) & (use_aug | ~is_aug)
        te = np.isin(group, te_g) & ~is_aug                    # test on clean photos only
        clf = LogisticRegression(C=C, class_weight="balanced", max_iter=3000)
        clf.fit(feats[tr], y_orig[group[tr]])
        oof[group[te]] = clf.predict_proba(feats[te])
    return oof


def metrics(oof, y):
    pred = oof.argmax(1)
    correct = (pred == y).astype(float)
    conf = oof.max(1)
    p_true = np.clip(oof[np.arange(len(y)), y], 1e-9, 1)
    top2 = np.sort(oof, axis=1)[:, -2:]
    close = (top2[:, 1] - top2[:, 0]) < 0.15
    recalls = [correct[y == c].mean() for c in range(len(CLASS_NAMES))]
    return dict(acc=correct.mean(), conf=conf.mean(), ece=ece(conf, correct),
                logloss=float(-np.log(p_true).mean()), close=float(close.mean()),
                recalls=recalls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="features.npz")
    ap.add_argument("--repeats", type=int, default=3)
    args = ap.parse_args()

    d = np.load(args.features)
    feats, group, is_aug, y_orig = d["feats"], d["group"], d["is_aug"], d["y"]
    n = len(y_orig)
    counts = np.bincount(y_orig, minlength=3)
    print(f"Photos: {n}  (" + ", ".join(f"{c}: {k}" for c, k in zip(CLASS_NAMES, counts)) + ")")
    print(f"Always guessing the biggest class would score {counts.max() / n:.3f}\n")

    rows = []
    for use_aug in (True, False):
        for C in C_GRID:
            ms = []
            for r in range(args.repeats):
                oof = one_repeat(feats, group, is_aug, y_orig, C, use_aug, seed=r)
                ms.append(metrics(oof, y_orig))
            acc = np.array([m["acc"] for m in ms])
            row = dict(
                aug="yes" if use_aug else "no", C=C,
                acc=acc.mean(), sd=acc.std(),
                conf=np.mean([m["conf"] for m in ms]),
                ece=np.mean([m["ece"] for m in ms]),
                logloss=np.mean([m["logloss"] for m in ms]),
                close=np.mean([m["close"] for m in ms]),
                recalls=np.mean([m["recalls"] for m in ms], axis=0),
            )
            rows.append(row)
            print(f"  done: aug={row['aug']:<3} C={C}", flush=True)

    print("\n aug      C    acc ± sd      conf   conf-acc   ECE   logloss   close  recall (ecto/endo/meso)")
    for r in rows:
        print(f" {r['aug']:<3} {r['C']:>7} {r['acc']:.3f} ± {r['sd']:.3f}  {r['conf']:.2f}   "
              f"{r['conf'] - r['acc']:+.2f}     {r['ece']:.2f}   {r['logloss']:.2f}     {r['close']:.2f}   "
              + " / ".join(f"{v:.2f}" for v in r["recalls"]))

    ok = [r for r in rows if r["conf"] - r["acc"] <= 0.05]
    pool = ok if ok else rows
    best = max(pool, key=lambda r: (round(r["acc"], 3), -r["C"])) if ok else min(rows, key=lambda r: r["logloss"])
    k = int(round(best["acc"] * n))
    lo, hi = wilson(k, n)
    print(f"\nSuggested recipe: aug={best['aug']}, C={best['C']}  "
          f"(accuracy {best['acc']:.3f}, 95% interval about {lo:.2f} to {hi:.2f} on {n} photos)")
    print("Rule used: highest accuracy among recipes whose average confidence is within 0.05 of "
          "their accuracy (not overconfident); ties go to the stronger regularization.")

    with open("cv_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["aug", "C", "acc", "sd", "conf", "ece", "logloss", "close", "rec_ecto", "rec_endo", "rec_meso"])
        for r in rows:
            w.writerow([r["aug"], r["C"], f"{r['acc']:.4f}", f"{r['sd']:.4f}", f"{r['conf']:.4f}",
                        f"{r['ece']:.4f}", f"{r['logloss']:.4f}", f"{r['close']:.4f}", *[f"{v:.4f}" for v in r["recalls"]]])
    print("Saved cv_results.csv")
    with open("cv_best.json", "w") as f:
        json.dump({"aug": best["aug"] == "yes", "C": best["C"],
                   "cv_accuracy": round(float(best["acc"]), 4),
                   "interval_95": [round(lo, 3), round(hi, 3)],
                   "mean_confidence": round(float(best["conf"]), 4),
                   "n_photos": int(n), "repeats": args.repeats}, f, indent=2)
    print("Saved cv_best.json (train.py reads the recipe from it)")


if __name__ == "__main__":
    main()
