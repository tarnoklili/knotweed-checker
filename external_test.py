"""Collect a second, fully unseen test set: Belgian and German iNaturalist photos,
one photo per observation, grouped by season. None of these were in training.

Output: external_test/<season>/<label>/<photo_id>.jpg and external_test/sources.csv
Run: python3 external_test.py
"""
import csv
import os
import time
import urllib.request

from scrape_inaturalist import LICENSES, fetch

PLACES = {"Belgium": 7008, "Germany": 7207}
SEASONS = {"spring": "3,4,5", "summer": "6,7,8", "autumn_winter": "9,10,11,12,1,2"}
TAXA = {
    "knotweed": [("Reynoutria", 15)],
    "not_knotweed": [("Calystegia sepium", 3), ("Persicaria", 3), ("Rubus", 3),
                     ("Urtica dioica", 2), ("Hedera helix", 2), ("Fallopia", 2)],
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "external_test")


def main():
    rows = []
    for country, place in PLACES.items():
        for season, months in SEASONS.items():
            for taxa in TAXA.values():
                for taxon, n in taxa:
                    data = fetch({"taxon_name": taxon, "place_id": place, "month": months,
                                  "quality_grade": "research", "photos": "true",
                                  "photo_license": LICENSES, "per_page": 60, "order_by": "votes"})
                    got = 0
                    for obs in data["results"]:
                        if got >= n:
                            break
                        if obs["taxon"].get("iconic_taxon_name") != "Plantae" or not obs["photos"]:
                            continue
                        p = obs["photos"][0]
                        label = "knotweed" if obs["taxon"]["name"].startswith("Reynoutria") else "not_knotweed"
                        folder = os.path.join(OUT, season, label)
                        os.makedirs(folder, exist_ok=True)
                        path = os.path.join(folder, f"{p['id']}.jpg")
                        if not os.path.exists(path):
                            try:
                                urllib.request.urlretrieve(p["url"].replace("square", "medium"), path)
                            except Exception as e:
                                print("  skip", p["id"], e)
                                continue
                            time.sleep(0.3)
                        rows.append({"country": country, "season": season, "label": label,
                                     "photo_id": p["id"], "taxon": obs["taxon"]["name"],
                                     "observed_on": obs.get("observed_on") or "",
                                     "license": p.get("license_code"), "attribution": p.get("attribution", ""),
                                     "observation": obs["uri"]})
                        got += 1
                    print(f"{country:8} {season:14} {taxon:18} {got}")
                    time.sleep(1)
    with open(os.path.join(OUT, "sources.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("done:", len(rows))


if __name__ == "__main__":
    main()
