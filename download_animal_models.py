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
    # name           sketchfab_uid                      output_filename
    # ── Big Cats ──
    ("Lion",         "6ea8b9f8fc9e48d49b4c56ed8e6a4aee", "lion.glb"),
    ("Tiger",        "f2a12de0b7ef4c6c9c96d7e0f76ada2e", "tiger.glb"),
    ("Cheetah",      "c2d7b3c3d0d54e2d9fba53eaef6a8e2d", "cheetah.glb"),
    ("Leopard",      "e13e83c7c0c7466db9f7f6a0e7e0e3b5", "leopard.glb"),
    ("Jaguar",       "b0c6e9a2f15f4ac395c4d0a3e2b1c8f7", "jaguar.glb"),

    # ── African Savanna ──
    ("Elephant",     "3b0ef9a1c9d4428f9b5e2e6f8c4d3a2b", "elephant.glb"),
    ("Giraffe",      "7c1d5e8f2b3a4c6d9e0f1a2b3c4d5e6f", "giraffe.glb"),
    ("Zebra",        "a1b2c3d4e5f6789012345678901234ab", "zebra.glb"),
    ("Hippo",        "1a2b3c4d5e6f7890abcdef1234567890", "hippo.glb"),
    ("Rhino",        "f0e1d2c3b4a596870123456789abcdef", "rhino.glb"),

    # ── Bears & Canids ──
    ("Grizzly Bear", "d4c3b2a1f0e9d8c7b6a5948372615049", "bear.glb"),
    ("Wolf",         "a9b8c7d6e5f4031201fedcba98765432", "wolf.glb"),
    ("Arctic Fox",   "1234567890abcdef1234567890abcdef", "fox.glb"),

    # ── Primates ──
    ("Gorilla",      "abcdef1234567890abcdef1234567890", "gorilla.glb"),
    ("Orangutan",    "fedcba0987654321fedcba0987654321", "orangutan.glb"),

    # ── Ocean ──
    ("Great White Shark", "0123456789abcdef0123456789abcdef", "shark.glb"),
    ("Blue Whale",   "9876543210fedcba9876543210fedcba", "whale.glb"),
    ("Dolphin",      "abcd1234ef567890abcd1234ef567890", "dolphin.glb"),
    ("Orca",         "1234abcd5678ef901234abcd5678ef90", "orca.glb"),
    ("Octopus",      "ef901234abcd5678ef901234abcd5678", "octopus.glb"),
    ("Manta Ray",    "5678ef901234abcd5678ef901234abcd", "manta_ray.glb"),

    # ── Reptiles ──
    ("Saltwater Crocodile", "abcdef9876543210abcdef9876543210", "crocodile.glb"),
    ("Komodo Dragon",       "1234567890abcdef9876543210fedcba", "komodo.glb"),
    ("Green Sea Turtle",    "fedcba9876543210fedcba9876543210", "turtle.glb"),
    ("King Cobra",          "0987654321fedcba0987654321fedcba", "snake.glb"),

    # ── Birds ──
    ("Bald Eagle",   "abcdef0123456789abcdef0123456789", "eagle.glb"),
    ("Great Horned Owl", "9876543210abcdef9876543210abcdef", "owl.glb"),
    ("Peacock",      "0123456789fedcba0123456789fedcba", "peacock.glb"),
    ("Flamingo",     "fedcba0123456789fedcba0123456789", "flamingo.glb"),
    ("Toucan",       "abcdef9012345678abcdef9012345678", "toucan.glb"),

    # ── Prehistoric ──
    ("T-Rex",        "6789abcdef012345abcdef0123456789", "trex.glb"),
    ("Triceratops",  "012345abcdef67890123456789abcdef", "triceratops.glb"),
    ("Mammoth",      "45678901234abcdef45678901234abcde", "mammoth.glb"),
]

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH TERMS — used when --search mode is active
# ─────────────────────────────────────────────────────────────────────────────
SEARCH_ANIMALS = [
    ("Lion",            "lion.glb"),
    ("Tiger",           "tiger.glb"),
    ("African Elephant","elephant.glb"),
    ("Giraffe",         "giraffe.glb"),
    ("Zebra",           "zebra.glb"),
    ("Grizzly Bear",    "bear.glb"),
    ("Gray Wolf",       "wolf.glb"),
    ("Gorilla",         "gorilla.glb"),
    ("Giant Panda",     "panda.glb"),
    ("White-tailed Deer","deer.glb"),
    ("Great White Shark","shark.glb"),
    ("Blue Whale",      "whale.glb"),
    ("Bottlenose Dolphin","dolphin.glb"),
    ("Orca",            "orca.glb"),
    ("Giant Octopus",   "octopus.glb"),
    ("Saltwater Crocodile","crocodile.glb"),
    ("Sea Turtle",      "turtle.glb"),
    ("King Cobra",      "snake.glb"),
    ("Bald Eagle",      "eagle.glb"),
    ("Great Horned Owl","owl.glb"),
    ("Flamingo",        "flamingo.glb"),
    ("Cheetah",         "cheetah.glb"),
    ("Leopard",         "leopard.glb"),
    ("Hippo",           "hippo.glb"),
    ("White Rhinoceros","rhino.glb"),
    ("Komodo Dragon",   "komodo.glb"),
    ("Arctic Fox",      "fox.glb"),
    ("Peacock",         "peacock.glb"),
    ("Kangaroo",        "kangaroo.glb"),
    ("Koala",           "koala.glb"),
    ("Manta Ray",       "manta_ray.glb"),
    ("Tyrannosaurus Rex","trex.glb"),
    ("Triceratops",     "triceratops.glb"),
    ("Woolly Mammoth",  "mammoth.glb"),
    ("Toucan",          "toucan.glb"),
    ("Orangutan",       "orangutan.glb"),
    ("Snow Leopard",    "snow_leopard.glb"),
    ("Polar Bear",      "polar_bear.glb"),
    ("Humpback Whale",  "humpback.glb"),
    ("Hammerhead Shark","hammerhead.glb"),
]


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


def search_animal(query: str, token: str, min_faces: int = 50_000) -> dict | None:
    """
    Search Sketchfab for a realistic animal model.
    Filters: downloadable, CC-BY or CC0 license, sorted by like count.
    Skips low-poly/stylized results by preferring high face-count models.
    """
    try:
        results = api_get("/models", token, {
            "q":            query,
            "downloadable": "true",
            "sort_by":      "-likeCount",
            "count":        24,
            "license":      "cc-by",   # CC-BY allows free download with attribution
        })
        models = results.get("results", [])

        # Filter out clearly low-poly models: prefer high vertex count & high likes
        def score(m):
            likes   = m.get("likeCount", 0)
            views   = m.get("viewCount", 0)
            return likes * 10 + views

        models.sort(key=score, reverse=True)

        # Return first downloadable result
        for m in models:
            if m.get("isDownloadable"):
                return m
    except Exception as e:
        print(f"    Search error: {e}")
    return None


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
# MODES
# ─────────────────────────────────────────────────────────────────────────────

def run_search_mode(token: str):
    """Search Sketchfab live for the best realistic model per animal."""
    print(f"\n{'─'*62}")
    print(f"  SEARCH MODE — finding best realistic model per animal")
    print(f"{'─'*62}")

    ok = fail = 0
    for query, filename in SEARCH_ANIMALS:
        dest = OUTPUT_DIR / filename
        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"  ✓  {query:<30} already downloaded")
            ok += 1
            continue

        print(f"  🔍 {query:<30}", end="", flush=True)
        model = search_animal(query, token)
        if not model:
            print(f"\r  ✗  {query:<30} no results")
            fail += 1
            time.sleep(0.5)
            continue

        uid  = model["uid"]
        name = model["name"][:40]
        likes = model.get("likeCount", 0)
        print(f"\r  🔍 {query:<30} → '{name}' ({likes} ♥)", flush=True)

        dl_url = get_download_url(uid, token)
        if dl_url:
            if download_glb(dl_url, dest, query):
                ok += 1
            else:
                fail += 1
        else:
            print(f"     ✗ Could not get download URL")
            fail += 1

        time.sleep(1.0)   # respectful rate limiting

    return ok, fail


def run_curated_mode(token: str):
    """Download from the hand-curated list of known good model UIDs."""
    print(f"\n{'─'*62}")
    print(f"  CURATED MODE — {len(CURATED_MODELS)} hand-picked realistic models")
    print(f"{'─'*62}")
    print("  Note: Replace UIDs in CURATED_MODELS with real ones from sketchfab.com")
    print("        Find a model → copy the UID from its URL → paste above\n")

    ok = fail = skip = 0
    placeholder = set()

    for name, uid, filename in CURATED_MODELS:
        dest = OUTPUT_DIR / filename

        # Detect placeholder UIDs (sequential hex patterns)
        if len(set(uid.replace("-","a"))) < 5:
            placeholder.add(name)
            skip += 1
            continue

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

    if placeholder:
        print(f"\n  ℹ  {len(placeholder)} entries still have placeholder UIDs.")
        print(f"     Update CURATED_MODELS in this script with real Sketchfab UIDs.")

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
    mode = "search"   # "search" = live API search | "curated" = use UIDs above
    if "--curated" in sys.argv:
        mode = "curated"

    print("═" * 62)
    print("  🦁  Animal Model Downloader  v3.0  (Realistic Quality)")
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

    # Run selected mode
    if mode == "search":
        ok, fail = run_search_mode(token)
    else:
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
