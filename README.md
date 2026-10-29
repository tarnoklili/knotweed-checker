# Knotweed Checker — spot invasive Japanese knotweed from a phone photo

**What it does.** You take or upload a photo of a plant. A Roboflow image-classification model says whether it is invasive knotweed (*Reynoutria*: Japanese, giant or Bohemian knotweed) or a different plant. It says "likely knotweed" only at 70% confidence or more; below that it says "maybe" and asks for a closer photo. If it is likely knotweed, the app tells you not to cut it and where to report it.

**Who it is for.** Residents, park volunteers and municipal green-space workers in the Netherlands who see a suspicious plant and want a quick first check before reporting it.

**SDG 15 — Life on Land.** Target 15.8 asks countries to stop invasive alien species and control their impact on ecosystems. Japanese knotweed is a well-known invasive plant in the Netherlands. It pushes out native plants, can damage river banks, paving and drainage, and spreads from tiny root or stem pieces. Removal works best when patches are found early, and most people cannot recognise the plant. This app helps more eyes find patches sooner.

**How we built it.**
1. Dataset: 832 photos taken in the Netherlands, scraped from iNaturalist (`scrape_inaturalist.py`): 302 knotweed and 530 look-alike and neighbour plants. Only research-grade observations (identity confirmed by the community) with Creative Commons licences. Credits per photo: `dataset/sources.csv`.
2. Roboflow: classification project, folder name = label. We split by plant, not by photo: the 302 knotweed photos come from only 185 plants, so all photos of one plant go in the same split (587/172/73 train/valid/test). Otherwise the model could be tested on a plant it already saw. Training photos were doubled with flips, small rotations and brightness changes (`train_roboflow.py`). Model: Roboflow's ViT classifier (`vit-base-patch16-224-in21k`), version `knotweed-nl/1`.
3. **Result on the 73 test photos it never saw (`evaluate.py`, same 70% rule as the app): 95% right. It found 24 of the 26 knotweed photos and wrongly flagged 2 of the 47 other plants.** Accuracy alone flatters it: always answering "not knotweed" would already score 64%.
4. App: `app.py` (Streamlit) sends the photo to our hosted Roboflow model.

**How to run.**
```
pip install -r requirements.txt
export ROBOFLOW_API_KEY="paste-your-key-here"
export ROBOFLOW_MODEL=knotweed-nl/1
streamlit run app.py
```
Then open the link it prints (on a phone in the same Wi-Fi, use the "Network URL"). The model lives in our private Roboflow workspace, so it needs our key: we demo it live, or ask us for a demo key. Example: `examples/test-knotweed.jpg`, a test photo the model never saw, gives "Likely knotweed (98% sure)" (`examples/app-screenshot.jpg`).

**Data card and ethical reflection:** see [`DATA_CARD.md`](DATA_CARD.md).
