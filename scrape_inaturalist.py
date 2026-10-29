"""Download Dutch iNaturalist photos for a knotweed / not-knotweed classifier.

Output: dataset/<class>/<photo_id>.jpg plus dataset/sources.csv (who took each
photo, its licence and the observation link), ready to drag into Roboflow as a
classification project (folder name = label).

Run: python3 scrape_inaturalist.py
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request

API = "https://api.inaturalist.org/v1/observations"
NETHERLANDS = 7506
LICENSES = "cc0,cc-by,cc-by-nc,cc-by-sa,cc-by-nc-sa"

# All three invasive knotweeds (Japanese, giant, Bohemian) are genus Reynoutria;
# Dutch municipalities treat them the same way.
CLASSES = {
    "knotweed": [("Reynoutria", 600)],
    # Plants people confuse with knotweed or that grow in the same spots.
    "not_knotweed": [
        ("Calystegia sepium", 120),   # haagwinde: heart-shaped leaves
        ("Persicaria", 120),          # duizendknoop relatives, native
        ("Rubus", 100),               # braam
        ("Urtica dioica", 100),       # brandnetel
        ("Hedera helix", 80),         # klimop
        ("Fallopia", 40),             # bindweed knotweeds
    ],
}

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")


def fetch(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "hhs-ai-for-good-hackathon"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def photos_for(taxon, limit):
    found, page = [], 1
    while len(found) < limit:
        data = fetch({
            "taxon_name": taxon, "place_id": NETHERLANDS, "quality_grade": "research",
            "photos": "true", "photo_license": LICENSES, "per_page": 200, "page": page,
            "order_by": "id",
        })
        for obs in data["results"]:
            if obs["taxon"].get("iconic_taxon_name") != "Plantae":
                continue  # e.g. rust fungus filed under its host plant
            for p in obs["photos"]:
                if p.get("license_code") and len(found) < limit:
                    found.append({
                        "photo_id": p["id"],
                        "url": p["url"].replace("square", "medium"),
                        "license": p["license_code"],
                        "attribution": p.get("attribution", ""),
                        "observation": obs["uri"],
                        "taxon": obs["taxon"]["name"],
                        "observed_on": obs.get("observed_on") or "",
                    })
        if page * 200 >= data["total_results"]:
            break
        page += 1
        time.sleep(1)
    return found


def main():
    rows, seen = [], set()
    for label in CLASSES:
        os.makedirs(os.path.join(OUT, label), exist_ok=True)
    for taxa in CLASSES.values():
        for taxon, limit in taxa:
            photos = photos_for(taxon, limit)
            print(f"{taxon:20} {len(photos)} photos")
            for p in photos:
                if p["photo_id"] in seen:
                    continue
                seen.add(p["photo_id"])
                # iNaturalist's name search mixes Reynoutria and Fallopia, so the
                # label comes from the confirmed species, not from the query.
                label = "knotweed" if p["taxon"].startswith("Reynoutria") else "not_knotweed"
                path = os.path.join(OUT, label, f"{p['photo_id']}.jpg")
                if not os.path.exists(path):
                    try:
                        urllib.request.urlretrieve(p["url"], path)
                    except Exception as e:  # one broken photo should not stop the run
                        print("  skip", p["photo_id"], e)
                        continue
                    time.sleep(0.3)
                rows.append({"label": label, **p})
    with open(os.path.join(OUT, "sources.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"done: {len(rows)} photos in {OUT}")


if __name__ == "__main__":
    main()
