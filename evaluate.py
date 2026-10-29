"""Send test photos to the hosted model and count right and wrong answers per class,
using the same 0.7 rule as the app.

Folder layout: <root>/<label>/*.jpg, or <root>/<group>/<label>/*.jpg (e.g. per season).

Run: ROBOFLOW_API_KEY=... ROBOFLOW_MODEL=knotweed-nl/1 .venv/bin/python evaluate.py [root]
     root defaults to upload/test (the held-out Dutch test set).
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app_core import classify  # noqa: E402

LABELS = ("knotweed", "not_knotweed")


def decide(image_bytes):
    top = classify(image_bytes)[0]
    return "knotweed" if top["class"] == "knotweed" and top["confidence"] >= 0.7 else "not_knotweed"


def score(folder, decide_fn=decide):
    counts = collections.Counter()
    for truth in LABELS:
        path = os.path.join(folder, truth)
        if not os.path.isdir(path):
            continue
        for name in sorted(os.listdir(path)):
            with open(os.path.join(path, name), "rb") as f:
                counts[(truth, decide_fn(f.read()))] += 1
    return counts


def report(title, c):
    k = c[("knotweed", "knotweed")] + c[("knotweed", "not_knotweed")]
    n = c[("not_knotweed", "not_knotweed")] + c[("not_knotweed", "knotweed")]
    right = c[("knotweed", "knotweed")] + c[("not_knotweed", "not_knotweed")]
    print(f"{title}: {k + n} photos, {right / (k + n):.0%} right, "
          f"knotweed found {c[('knotweed', 'knotweed')]} of {k}, "
          f"others wrongly flagged {c[('not_knotweed', 'knotweed')]} of {n}")


def main(root, decide_fn=decide):
    if os.path.isdir(os.path.join(root, LABELS[0])):
        report(root, score(root, decide_fn))
        return
    total = collections.Counter()
    for group in sorted(os.listdir(root)):
        if os.path.isdir(os.path.join(root, group)):
            c = score(os.path.join(root, group), decide_fn)
            report(group, c)
            total += c
    report("all", total)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join("upload", "test"))
