# Knotweed Checker — spot invasive Japanese knotweed from a phone photo

**What it does.** You take or upload a photo of a plant. Our Roboflow model says whether it is invasive knotweed (*Reynoutria*: Japanese, giant or Bohemian) or another plant. If the model picks knotweed with 70% confidence or more, the app says "likely knotweed: don't cut it, report it"; if it picks knotweed with less, it says "maybe" and asks for a closer photo; otherwise it says "probably not".

**The problem.** Knotweed pushes out native plants, can damage river banks and paving, and regrows from tiny root pieces. Amsterdam set aside €8.2 million to fight it, and municipalities such as Ameland and Heusden ask residents to report where it grows ([gemeente.nu, 2019](https://gemeente.nu/ruimte-milieu/strijdplan-japanse-duizendknoop-samen-met-inwoners)). Patches are cheapest to remove when found early, but most residents cannot tell knotweed from look-alikes such as bindweed.

**Who it is for.** Residents and park volunteers in the Netherlands who see a suspicious plant and want to know in seconds whether to report it. **Not for:** municipal staff or contractors deciding whether to remove a plant (that needs an expert on site), or identifying other species.

**SDG 15 — Life on Land.** Target 15.8: prevent invasive alien species and reduce their impact on ecosystems. More correct, earlier reports mean patches get removed while they are small.

**How it works.** (1) The user takes or uploads a photo. (2) The app sends it to our **Roboflow** model, the step that decides "knotweed or not"; without it there is no answer. (3) The app turns the answer into advice. **Why not a general AI model?** We tested one: CLIP, a general image model we used as is, without training it on our photos (`clip_baseline.py`). It finds knotweed as often as ours, but raises **four times as many false alarms** (21 vs 5 below). False alarms could lead to unnecessary checks or harmless plants being cut.

**Result.** Two tests on photos it never saw (`evaluate.py`):

| Test set | Our model | General model (CLIP) |
|---|---|---|
| 73 Dutch photos | 95% right · knotweed found 24/26 · false alarms 2/47 | 85% · 23/26 · 8/47 |
| 168 photos from Belgium and Germany, all seasons | 93% right · knotweed found 77/83 · false alarms 5/85 | 84% · 77/83 · 21/85 |

How we collected the data, trained the model and tested it: [`DATA_CARD.md`](DATA_CARD.md). Slides: [`slides.pdf`](slides.pdf).

**How to run.**
```
pip install -r requirements.txt
export ROBOFLOW_API_KEY="paste-your-key-here"
export ROBOFLOW_MODEL=knotweed-nl/1
streamlit run app.py
```
Open the link it prints (on a phone in the same Wi-Fi, use the "Network URL"). The model is in our private Roboflow workspace, so it needs our key: we demo it live, or ask us for a demo key. Example: `examples/test-knotweed.jpg` gives "Likely knotweed (98% sure)" (`examples/app-screenshot.jpg`).

**Data card and ethical reflection:** [`DATA_CARD.md`](DATA_CARD.md).
