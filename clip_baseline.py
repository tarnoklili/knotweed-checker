"""The "simpler alternative": a general AI model that was never trained on our data.

CLIP (OpenAI, clip-vit-large-patch14) picks whichever text description fits the photo
best. If that description is about knotweed, it counts as "knotweed". Runs locally,
no Roboflow. Same folders and scoring as evaluate.py.

Run: .venv/bin/python clip_baseline.py [root]
"""
import io
import os
import sys

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from evaluate import main

PROMPTS = {
    "a photo of Japanese knotweed": "knotweed",
    "a photo of the invasive plant Reynoutria japonica": "knotweed",
    "a photo of bindweed": "not_knotweed",
    "a photo of a bramble bush": "not_knotweed",
    "a photo of stinging nettles": "not_knotweed",
    "a photo of ivy": "not_knotweed",
    "a photo of a knotweed relative such as Persicaria": "not_knotweed",
    "a photo of a green plant": "not_knotweed",
}
NAME = "openai/clip-vit-large-patch14"
model = CLIPModel.from_pretrained(NAME).eval()
proc = CLIPProcessor.from_pretrained(NAME)
texts = list(PROMPTS)


def decide(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = proc(text=texts, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        best = model(**inputs).logits_per_image[0].argmax().item()
    return PROMPTS[texts[best]]


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join("upload", "test"), decide)
