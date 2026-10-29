"""Send every held-out test photo (upload/test/<class>/) to the hosted model and
count right and wrong answers per class, using the same 0.7 rule as the app.

Run: ROBOFLOW_API_KEY=... ROBOFLOW_MODEL=knotweed-nl/1 .venv/bin/python evaluate.py
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app_core import classify  # noqa: E402

counts = collections.Counter()
for truth in ("knotweed", "not_knotweed"):
    folder = os.path.join("upload", "test", truth)
    for name in sorted(os.listdir(folder)):
        with open(os.path.join(folder, name), "rb") as f:
            top = classify(f.read())[0]
        said = "knotweed" if top["class"] == "knotweed" and top["confidence"] >= 0.7 else "not_knotweed"
        counts[(truth, said)] += 1

k_total = counts[("knotweed", "knotweed")] + counts[("knotweed", "not_knotweed")]
n_total = counts[("not_knotweed", "not_knotweed")] + counts[("not_knotweed", "knotweed")]
right = counts[("knotweed", "knotweed")] + counts[("not_knotweed", "not_knotweed")]
print(f"test photos: {k_total + n_total}  accuracy: {right / (k_total + n_total):.0%}")
print(f"knotweed found: {counts[('knotweed', 'knotweed')]} of {k_total}")
print(f"other plants wrongly flagged as knotweed: {counts[('not_knotweed', 'knotweed')]} of {n_total}")
