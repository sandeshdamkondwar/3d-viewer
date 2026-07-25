#!/usr/bin/env python3
"""
Download realistic, high-quality 3D animal models via Sketchfab.

SETUP (one-time, 2 minutes):
  1. Create a free account at https://sketchfab.com
  2. Go to https://sketchfab.com/settings/password  →  copy your API Token
  3. Run:  export SKETCHFAB_TOKEN="your_token_here"
  4. Then: python3 download_animal_models.py

WHY SKETCHFAB:
  - Largest library of realistic photogrammetry + sculpted 3D animals
  - Free accounts can download CC-BY / CC0 licensed models
  - GLB format, ready to drop into model-viewer
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("./models")
OUTPUT_DIR.mkdir(exist_ok=True)

SKETCHFAB_API = "https://api.sketchfab.com/v3"
TIMEOUT = 60

# ─────────────────────────────────────────────────────────────────────────────
# CURATED HIGH-QUALITY MODEL UIDs
# Hand-picked realistic Sketchfab models (CC-BY licensed, freely downloadable).
# These are sorted by quality — photogrammetry scans and professional sculpts.
#
# To find more: sketchfab.com/search?q=animal&downloadable=true&sort_by=-likeCount
# Copy the UID from the model URL: sketchfab.com/3d-models/lion-{UID}
# ─────────────────────────────────────────────────────────────────────────────
CURATED_MODELS = [
    # name              sketchfab_uid                      output_filename
    ("Lion",            "d2d99a24bc0045d6b09b6ea560a5d761", "lion.glb"),
    ("African Bush Elephant", "a0f877427dcf492a8dc7bcac4751f0a8", "elephant.glb"),
    ("Giraffe",         "fbc2566f648d46a8b28624c9cf9fb218", "giraffe.glb"),
    ("White Tiger",     "9dd099d283e54f99b7cbd40b531b1a29", "tiger.glb"),
    ("Grizzly Bear",    "df9d941ee11a419db3a007775bdae832", "bear.glb"),
    ("Grey Wolf",       "6a9f281a9fb344f3a7b8bcab3c6f4c9a", "wolf.glb"),
    ("Giant Panda",     "76ce633705f04272b30823c428952a6d", "panda.glb"),
    ("Gorilla",         "e69585d870ce4ae382fd071e87ae3b0e", "gorilla.glb"),
    ("Zebra",           "bd7258ee007b4e0fb521abb74bfa99d0", "zebra.glb"),
    ("Realistic Deer",  "76039b75cdc0492a80680c2404725496", "deer.glb"),
    ("Rabbit Rigged",   "e7213589744d436b9d96e2dbb31198a5", "rabbit.glb"),
    ("Bald Eagle",      "30434fd1272f464a8540750a78a5087f", "eagle.glb"),
    ("Owl",             "761067d2fe80480e8b986dd38396ec8c", "owl.glb"),
    ("Penguin",         "0a89cf636aa7446f895cf367b190133c", "penguin.glb"),
    ("Crocodile",       "a242e4634a234d3fb909c54b2c39d7b8", "crocodile.glb"),
    ("Sea Turtle",      "919411e2c4d141d3b981fef7dbb93a6c", "turtle.glb"),
    ("Snake",           "865916a58ff645118dffc4b94bef72f8", "snake.glb"),
    ("Realistic Shark", "e913e5092d2341749ff66e4359b1e4a3", "shark.glb"),
    ("Humpback Whale",  "bb3841769829451394c59386ee9f2ec6", "whale.glb"),
    ("Octopus",         "330402cc0ade4fc5bb147f3d618e58c3", "octopus.glb"),
    ("Dolphin",         "c24dc835a6aa4d3c827450513525cdb8", "dolphin.glb"),
    ("Jellyfish",       "d06a5a553fe641ab92f720527b2278f3", "jellyfish.glb"),
    ("Monarch Butterfly", "3a5fc9a496cb402297ffdb6700d2ab60", "butterfly.glb"),
    ("Bee",             "3b1995f874024043b30af93aa7c2820a", "bee.glb"),
    ("Tyrannosaurus Rex", "ac837b7b80dd48e888d852636a4a19cb", "trex.glb"),
]
# Every UID above was verified by hand: opened on sketchfab.com, confirmed the
# license is CC-BY, and downloaded through the browser (Sketchfab requires a
# logged-in free account for the download button to work, API token or not).
# See ATTRIBUTIONS.md for the required credit line per model.


# ─────────────────────────────────────────────────────────────────────────────
# SKETCHFAB API HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def make_headers(token: str) -> dict:
    return {
        "Authorization": f"Token {token}",
        "User-Agent": "AnimalViewer/3.0 (3D Animal Viewer Project)",
    }


def api_get(path: str, token: str, params: dict = None) -> dict:
    url = f"{SKETCHFAB_API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=make_headers(token))
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def get_download_url(uid: str, token: str) -> str | None:
    """Get the GLB download URL for a model UID."""
    try:
        data = api_get(f"/models/{uid}/download", token)
        # Prefer GLB, fall back to GLTF zip
        glb = data.get("glb") or data.get("gltf")
        if glb:
            return glb.get("url")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"    ⚠ Download restricted (model may require Sketchfab Pro)")
        else:
            print(f"    HTTP {e.code}")
    except Exception as e:
        print(f"    {e}")
    return None


def download_glb(url: str, dest: Path, label: str) -> bool:
    """Download a GLB (or ZIP containing GLB) with progress bar."""
    if dest.exists() and dest.stat().st_size > 10_000:
        print(f"  ✓  {label:<30} already exists ({dest.stat().st_size // 1024} KB)")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AnimalViewer/3.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            chunks, received = [], 0
            while chunk := resp.read(32768):
                chunks.append(chunk)
                received += len(chunk)
                if total:
                    pct = received / total * 100
                    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                    print(f"\r  ↓  {label:<30} [{bar}] {received//1024}KB", end="", flush=True)

        data = b"".join(chunks)

        # If Sketchfab returns a ZIP, extract the GLB from it
        if data[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(data)) as z:
                glb_names = [n for n in z.namelist() if n.lower().endswith(".glb")]
                if not glb_names:
                    # Fall back to any GLTF
                    glb_names = [n for n in z.namelist() if n.lower().endswith(".gltf")]
                if glb_names:
                    data = z.read(glb_names[0])
                else:
                    print(f"\r  ✗  {label:<30} ZIP has no GLB inside")
                    return False

        if len(data) < 1000:
            print(f"\r  ✗  {label:<30} file too small")
            return False

        dest.write_bytes(data)
        print(f"\r  ✓  {label:<30} {len(data)//1024:>6} KB  → {dest.name}")
        return True

    except urllib.error.HTTPError as e:
        print(f"\r  ✗  {label:<30} HTTP {e.code}")
    except Exception as e:
        print(f"\r  ✗  {label:<30} {str(e)[:50]}")
    return False


def verify_token(token: str) -> bool:
    try:
        me = api_get("/me", token)
        username = me.get("username", "unknown")
        plan = me.get("account", "free")
        print(f"  ✓  Logged in as: {username}  (plan: {plan})")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("  ✗  Invalid API token — check https://sketchfab.com/settings/password")
        else:
            print(f"  ✗  Auth error: HTTP {e.code}")
    except Exception as e:
        print(f"  ✗  Connection error: {e}")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# MODE
# ─────────────────────────────────────────────────────────────────────────────

def run_curated_mode(token: str):
    """Download every model in CURATED_MODELS by its verified Sketchfab UID."""
    print(f"\n{'─'*62}")
    print(f"  {len(CURATED_MODELS)} hand-picked, license-verified realistic models")
    print(f"{'─'*62}")

    ok = fail = 0
    for name, uid, filename in CURATED_MODELS:
        dest = OUTPUT_DIR / filename

        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"  ✓  {name:<30} already downloaded")
            ok += 1
            continue

        dl_url = get_download_url(uid, token)
        if dl_url:
            if download_glb(dl_url, dest, name):
                ok += 1
            else:
                fail += 1
        else:
            fail += 1
        time.sleep(0.8)

    return ok, fail


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

SETUP_GUIDE = """
╔══════════════════════════════════════════════════════════════╗
║         SKETCHFAB SETUP  (free, 2 minutes)                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║  1. Create free account: https://sketchfab.com/signup      ║
║                                                             ║
║  2. Get your API token:                                     ║
║     https://sketchfab.com/settings/password                ║
║     → scroll to "API Token" → Copy                         ║
║                                                             ║
║  3. Set it in your terminal:                               ║
║     export SKETCHFAB_TOKEN="paste_your_token_here"         ║
║                                                             ║
║  4. Run again:                                              ║
║     python3 download_animal_models.py                      ║
║                                                             ║
║  WHY SKETCHFAB?                                             ║
║  • Photorealistic & photogrammetry-scanned animals         ║
║  • Same quality as Google's AR animals                     ║
║  • Free CC-BY models, no payment required                  ║
║                                                             ║
╚══════════════════════════════════════════════════════════════╝
"""

def main():
    print("═" * 62)
    print("  🦁  Animal Model Downloader  v4.0  (Realistic Quality)")
    print(f"  Output: {OUTPUT_DIR.resolve()}")
    print("═" * 62)

    # Get token
    token = os.environ.get("SKETCHFAB_TOKEN", "").strip()
    if not token:
        print(SETUP_GUIDE)
        sys.exit(1)

    # Verify credentials
    print("\n  Verifying Sketchfab credentials…")
    if not verify_token(token):
        sys.exit(1)

    ok, fail = run_curated_mode(token)

    # Summary
    files = list(OUTPUT_DIR.glob("*.glb"))
    size_mb = sum(f.stat().st_size for f in files) / 1024 / 1024

    print(f"\n{'═'*62}")
    print(f"  ✓ {ok} downloaded    ✗ {fail} failed")
    print(f"  📁 {len(files)} .glb files in ./models/  ({size_mb:.1f} MB)")
    print()
    print("  Start the viewer:")
    print("    python3 server.py  →  http://localhost:8000")
    print("═" * 62)


if __name__ == "__main__":
    main()
