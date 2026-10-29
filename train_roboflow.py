"""Upload upload/<split>/<class>/*.jpg to Roboflow, make a version and train it.

The split folders were made per iNaturalist observation, so photos of the same
plant never end up in both training and test.

Run: ROBOFLOW_API_KEY=... .venv/bin/python train_roboflow.py
"""
import os

from roboflow import Roboflow

PROJECT = "knotweed-nl"

rf = Roboflow(api_key=os.environ["ROBOFLOW_API_KEY"])
ws = rf.workspace()
ws.upload_dataset("upload", PROJECT, project_type="single-label-classification", num_workers=8, num_retries=2)

project = ws.project(PROJECT)
version_no = project.generate_version({
    "preprocessing": {"auto-orient": True, "resize": {"width": 224, "height": 224, "format": "Stretch to"}},
    "augmentation": {"image": {"versions": 2}, "flip": {"horizontal": True}, "rotate": {"degrees": 15}, "brightness": {"brighten": True, "darken": True, "percent": 20}},
})
print("version", version_no)
model = project.version(version_no).train()
print("model ready:", f"{ws.url}/{PROJECT}/{version_no}")
