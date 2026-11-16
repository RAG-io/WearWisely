"""Find which of YOUR photos the model finds borderline (no TensorFlow needed).

Run from inside dl/ (needs features.npz and cross_validate.py next to it):
    python3 list_close_calls.py

Every photo is scored by a model that never saw it (5-fold cross-validation, averaged
over 3 shuffles), using the recommended recipe (C=0.01, with augmented rows).
A "close call" is a photo whose top two classes are within MARGIN of each other.
Photos are grouped by which two classes are fighting: ecto vs meso, meso vs endo, ecto vs endo.
It prints the closest ones and copies them into close_calls/<pair>/ so you can look at them
and try them in the app. Those folders contain photos of people: do NOT commit them to git.
"""
import argparse
import csv
import os
import shutil

import numpy as np

from cross_validate import one_repeat, CLASS_NAMES

SHORT = {0: "ecto", 1: "endo", 2: "meso"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="features.npz")
    ap.add_argument("--C", type=float, default=0.01)
    ap.add_argument("--margin", type=float, default=0.15)
    ap.add_argument("--show", type=int, default=8, help="how many to print per pair")
    ap.add_argument("--no-copy", action="store_true")
    args = ap.parse_args()

    d = np.load(args.features)
    feats, group, is_aug, y = d["feats"], d["group"], d["is_aug"], d["y"]
    paths, splits = d["paths"], d["splits"]
    n = len(y)

    probs = np.mean([one_repeat(feats, group, is_aug, y, args.C, True, seed=s) for s in range(3)], axis=0)
    order = np.argsort(-probs, axis=1)
    top1, top2 = order[:, 0], order[:, 1]
    margin = probs[np.arange(n), top1] - probs[np.arange(n), top2]
    close = margin < args.margin

    print(f"Photos: {n}.  Close calls (top two classes within {args.margin}): {int(close.sum())}")
    print(f"Overall accuracy of these out-of-fold predictions: {(top1 == y).mean():.3f}")
    print(f"On close calls the true label is among the top two: {np.mean((top1 == y)[close] | (top2 == y)[close]):.2f}  "
          f"| top-1 correct: {(top1 == y)[close].mean():.2f}\n")

    rows = []
    for a, b in [(0, 2), (1, 2), (0, 1)]:
        name = f"{SHORT[a]}_vs_{SHORT[b]}"
        idx = [i for i in np.where(close)[0] if {top1[i], top2[i]} == {a, b}]
        idx.sort(key=lambda i: margin[i])
        print(f"=== {name}: {len(idx)} close calls ===")
        for i in idx[:args.show]:
            tag = "ok " if top1[i] == y[i] else "WRONG"
            print(f"  {tag} true={SHORT[y[i]]:<4} margin={margin[i]:.2f}  "
                  f"ecto {probs[i,0]:.2f}  endo {probs[i,1]:.2f}  meso {probs[i,2]:.2f}   {paths[i]}")
        if not args.no_copy and idx:
            outdir = os.path.join("close_calls", name)
            os.makedirs(outdir, exist_ok=True)
            for i in idx:
                if os.path.exists(paths[i]):
                    base = f"m{margin[i]:.2f}_true-{SHORT[y[i]]}_{splits[i]}_{os.path.basename(paths[i])}"
                    shutil.copy(paths[i], os.path.join(outdir, base))
        for i in idx:
            rows.append([name, paths[i], SHORT[y[i]], f"{margin[i]:.3f}", *[f"{p:.3f}" for p in probs[i]]])
        print()

    with open("close_calls.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pair", "path", "true", "margin", "p_ecto", "p_endo", "p_meso"])
        w.writerows(rows)
    print("Saved close_calls.csv" + ("" if args.no_copy else " and photos in close_calls/<pair>/ (do not commit)"))


if __name__ == "__main__":
    main()
