import requests
import json
import re
import os
import time
import csv


# ── Config ──────────────────────────────────────────────────────────────────
PHOTOS_JS_URL = "https://raw.githubusercontent.com/hankmt/Artemis-Timeline/main/photos.js"
BASE_IMAGE_URL = "https://artemistimeline.com/web/"
DOWNLOAD_DIR = "data/photos"

# ── Step 1: Fetch and parse photos.js ───────────────────────────────────────
def get_photo_list():
    response = requests.get(PHOTOS_JS_URL)
    js_text = response.text

    # Strip the JS wrapper to get pure JSON
    json_str = re.search(r'const PHOTO_DATA = ({.*})', js_text, re.DOTALL).group(1)
    data = json.loads(json_str)

    # Keep full dicts, skip videos
    photos = [p for p in data["photos"] if p["file"].endswith(".jpg")]
    print(f"Found {len(photos)} photos")
    return photos

# Also saving metadata for further analysis
def save_metadata(photo_data):
    fields = ["file", "time", "photographer", "location", "camera", 
              "settings", "spacecraft", "batch", "title", "flickr_desc"]
    
    os.makedirs("data", exist_ok=True)
    
    with open("data/metadata.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in photo_data:
            writer.writerow({field: p.get(field, "") for field in fields})
    
    print(f"Saved metadata for {len(photo_data)} photos")

# ── Step 2: Download photos ──────────────────────────────────────────────────
def download_photos(photo_list):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for i, filename in enumerate(photo_list):
        dest = os.path.join(DOWNLOAD_DIR, filename)

        if os.path.exists(dest):
            print(f"[{i+1}/{len(photo_list)}] Already exists, skipping: {filename}")
            continue

        url = BASE_IMAGE_URL + filename
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[{i+1}/{len(photo_list)}] Downloaded: {filename}")
        else:
            print(f"[{i+1}/{len(photo_list)}] FAILED ({response.status_code}): {filename}")

        time.sleep(0.5)  # Be polite to the server

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    photos = get_photo_list()
    save_metadata(photos)
    download_photos([p["file"] for p in photos])
    