"""Call the hosted Roboflow classification model. Shared by app.py and evaluate.py."""
import base64
import os

import requests

API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")
MODEL = os.environ.get("ROBOFLOW_MODEL", "")


def classify(image_bytes):
    """Return [{class, confidence}, ...], most likely first."""
    r = requests.post(
        f"https://classify.roboflow.com/{MODEL}",
        params={"api_key": API_KEY},
        data=base64.b64encode(image_bytes).decode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    r.raise_for_status()
    out = r.json()
    preds = out.get("predictions", [])
    if isinstance(preds, dict):  # multi-label projects return {class: {confidence}}
        preds = [{"class": k, "confidence": v["confidence"]} for k, v in preds.items()]
    return sorted(preds, key=lambda p: p["confidence"], reverse=True)
