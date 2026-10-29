"""Knotweed checker: upload or take a photo, the Roboflow model says if it is knotweed.

Run:
    pip install -r requirements.txt
    export ROBOFLOW_API_KEY=...        # Roboflow > Settings > API Keys (private key)
    export ROBOFLOW_MODEL=knotweed-nl/1   # <project-id>/<version>, from the Deploy tab
    streamlit run app.py
"""
import streamlit as st

from app_core import API_KEY, MODEL, classify

REPORT_URL = "https://waarneming.nl"  # national species-sighting platform


st.set_page_config(page_title="Knotweed checker", page_icon="🌿")
st.title("🌿 Is this Japanese knotweed?")
st.write(
    "Japanese knotweed (Japanse duizendknoop) is an invasive plant that pushes out "
    "native plants and can damage river banks and paving. Take a photo of a plant and this "
    "model gives a first guess. It is a hint, not a final answer."
)

if not API_KEY or not MODEL:
    st.error("Set ROBOFLOW_API_KEY and ROBOFLOW_MODEL first (see the top of app.py).")
    st.stop()

photo = st.camera_input("Take a photo") or st.file_uploader("…or upload one", type=["jpg", "jpeg", "png"])
if photo:
    data = photo.getvalue()
    st.image(data, use_container_width=True)
    with st.spinner("Checking…"):
        preds = classify(data)
    top = preds[0]
    conf = top["confidence"]
    if top["class"] == "knotweed" and conf >= 0.7:
        st.success(f"Likely knotweed ({conf:.0%} sure).")
        st.write(f"Do not cut or pull it: small pieces regrow. Report the location on {REPORT_URL} or to your municipality.")
    elif top["class"] == "knotweed":
        st.warning(f"Maybe knotweed ({conf:.0%} sure). Take a closer photo of the leaves and stem.")
    else:
        st.info(f"Probably not knotweed ({conf:.0%} sure).")
    with st.expander("All scores"):
        for p in preds:
            st.write(f"{p['class']}: {p['confidence']:.1%}")
    st.caption("Trained on ~830 Dutch iNaturalist photos. Can be wrong, especially in winter, "
               "on young shoots, or on plants it never saw. Check with an expert before removing anything.")
