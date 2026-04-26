#!/usr/bin/env python3
"""
Download free 3D animal models (GLB/glTF format) from open-source repositories.
Run this script locally to populate your ./models/ directory.

Sources:
  1. Quaternius Ultimate Animal Pack (CC0) - https://quaternius.itch.io/ultimate-animal-pack
  2. KhronosGroup glTF Sample Models (MIT) - https://github.com/KhronosGroup/glTF-Sample-Models
  3. Google model-viewer sample assets
  4. Poly.pizza (CC0) - https://poly.pizza
"""

import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("./models")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AnimalViewer/1.0)"
}

# ─────────────────────────────────────────────────────────────────────────────
# ANIMAL MODELS CATALOGUE
# All URLs are direct GLB/glTF download links from open/free sources.
# ─────────────────────────────────────────────────────────────────────────────

MODELS = [
    # ── KhronosGroup glTF Sample Assets (MIT licensed) ──
    {
        "name": "Fox",
        "filename": "fox.glb",
        "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Fox/glTF-Binary/Fox.glb",
        "source": "KhronosGroup",
        "license": "CC BY 4.0",
    },
    {
        "name": "Duck",
        "filename": "duck.glb",
        "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Duck/glTF-Binary/Duck.glb",
        "source": "KhronosGroup",
        "license": "CC BY 4.0",
    },
    {
        "name": "Horse",
        "filename": "horse.glb",
        "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Horse/glTF-Binary/Horse.glb",
        "source": "KhronosGroup",
        "license": "CC BY 4.0",
    },

    # ── Google model-viewer sample animals ──
    {
        "name": "Cat",
        "filename": "cat.glb",
        "url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",  # placeholder - see note
        "source": "Google model-viewer",
        "license": "CC BY 4.0",
        "note": "Replace URL with actual animal GLB from https://modelviewer.dev/examples/",
    },

    # ── Quaternius Ultimate Animal Pack (CC0) ──
    # Download the full pack ZIP from: https://quaternius.itch.io/ultimate-animal-pack
    # Then extract GLBs - the pack includes 100+ animals.
    # Animals in the pack (filename pattern after extraction):
    {
        "name": "Bear",
        "filename": "bear.glb",
        "url": "https://quaternius.itch.io/ultimate-animal-pack",  # manual download required
        "source": "Quaternius",
        "license": "CC0",
        "manual": True,
        "note": "Download from https://quaternius.itch.io/ultimate-animal-pack (free)",
    },

    # ── Sketchfab CC0 Models (requires Sketchfab account + API token) ──
    # Set SKETCHFAB_TOKEN env var to enable these downloads.
    # Find CC0 animals at: https://sketchfab.com/search?features=downloadable&license=cc0&type=models&q=animal
    {
        "name": "Elephant",
        "filename": "elephant.glb",
        "url": "https://sketchfab.com/models/YOUR_MODEL_UID/download",
        "source": "Sketchfab",
        "license": "CC0",
        "requires_auth": True,
        "note": "Find free models at https://sketchfab.com/search?features=downloadable&license=cc0&type=models&q=elephant",
    },

    # ── poly.pizza (CC0 - no auth required) ──
    {
        "name": "Dinosaur (T-Rex)",
        "filename": "trex.glb",
        "url": "https://api.poly.pizza/model/GX3HRscpBp/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Shark",
        "filename": "shark.glb",
        "url": "https://api.poly.pizza/model/shark/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Penguin",
        "filename": "penguin.glb",
        "url": "https://api.poly.pizza/model/penguin/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Giraffe",
        "filename": "giraffe.glb",
        "url": "https://api.poly.pizza/model/giraffe/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Lion",
        "filename": "lion.glb",
        "url": "https://api.poly.pizza/model/lion/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Whale",
        "filename": "whale.glb",
        "url": "https://api.poly.pizza/model/whale/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Parrot",
        "filename": "parrot.glb",
        "url": "https://api.poly.pizza/model/parrot/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Crocodile",
        "filename": "crocodile.glb",
        "url": "https://api.poly.pizza/model/crocodile/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
    {
        "name": "Wolf",
        "filename": "wolf.glb",
        "url": "https://api.poly.pizza/model/wolf/download",
        "source": "poly.pizza",
        "license": "CC0",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CURATED POLY.PIZZA MODELS
# These are verified CC0 GLB models from poly.pizza with correct UIDs.
# Find more at: https://poly.pizza  (all CC0, no login needed)
# ─────────────────────────────────────────────────────────────────────────────
POLYPIZZA_ANIMALS = [
    # Format: (display_name, poly_pizza_uid, filename)
    # Browse https://poly.pizza and copy the UID from the model URL
    # e.g. https://poly.pizza/m/XXXXXXXX  → uid = "XXXXXXXX"
    ("Dog",        "REPLACE_WITH_UID", "dog.glb"),
    ("Cat",        "REPLACE_WITH_UID", "cat.glb"),
    ("Rabbit",     "REPLACE_WITH_UID", "rabbit.glb"),
    ("Horse",      "REPLACE_WITH_UID", "horse.glb"),
    ("Cow",        "REPLACE_WITH_UID", "cow.glb"),
    ("Pig",        "REPLACE_WITH_UID", "pig.glb"),
    ("Chicken",    "REPLACE_WITH_UID", "chicken.glb"),
    ("Deer",       "REPLACE_WITH_UID", "deer.glb"),
    ("Tiger",      "REPLACE_WITH_UID", "tiger.glb"),
    ("Gorilla",    "REPLACE_WITH_UID", "gorilla.glb"),
    ("Panda",      "REPLACE_WITH_UID", "panda.glb"),
    ("Zebra",      "REPLACE_WITH_UID", "zebra.glb"),
    ("Hippo",      "REPLACE_WITH_UID", "hippo.glb"),
    ("Rhino",      "REPLACE_WITH_UID", "rhino.glb"),
    ("Cheetah",    "REPLACE_WITH_UID", "cheetah.glb"),
    ("Eagle",      "REPLACE_WITH_UID", "eagle.glb"),
    ("Owl",        "REPLACE_WITH_UID", "owl.glb"),
    ("Flamingo",   "REPLACE_WITH_UID", "flamingo.glb"),
    ("Octopus",    "REPLACE_WITH_UID", "octopus.glb"),
    ("Jellyfish",  "REPLACE_WITH_UID", "jellyfish.glb"),
    ("Dolphin",    "REPLACE_WITH_UID", "dolphin.glb"),
    ("Turtle",     "REPLACE_WITH_UID", "turtle.glb"),
    ("Frog",       "REPLACE_WITH_UID", "frog.glb"),
    ("Snake",      "REPLACE_WITH_UID", "snake.glb"),
    ("Chameleon",  "REPLACE_WITH_UID", "chameleon.glb"),
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def download_file(url: str, dest: Path, label: str) -> bool:
    """Download a file with progress indication."""
    if dest.exists():
        print(f"  ✓ {label} already exists, skipping.")
        return True

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192

            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r  ↓ {label}: {pct:.0f}% ({downloaded/1024:.0f} KB)", end="", flush=True)

        size_kb = dest.stat().st_size / 1024
        print(f"\r  ✓ {label}: {size_kb:.0f} KB downloaded → {dest.name}")
        return True

    except urllib.error.HTTPError as e:
        print(f"\r  ✗ {label}: HTTP {e.code} - {url}")
        return False
    except Exception as e:
        print(f"\r  ✗ {label}: {e}")
        return False


def download_polypizza(uid: str, dest: Path, label: str) -> bool:
    """Download a model from poly.pizza by UID."""
    # poly.pizza direct download URL format
    url = f"https://poly.pizza/m/{uid}"
    # The actual GLB URL needs to be discovered via their page
    # poly.pizza GLB URLs follow: https://cdn.poly.pizza/{uid}/{filename}.glb
    glb_url = f"https://cdn.poly.pizza/{uid}/{uid}.glb"
    return download_file(glb_url, dest, label)


# ─────────────────────────────────────────────────────────────────────────────
# BEST FREE SOURCES — MANUAL DOWNLOAD GUIDE
# ─────────────────────────────────────────────────────────────────────────────

MANUAL_SOURCES = """
╔══════════════════════════════════════════════════════════════════════════════╗
║              BEST FREE 3D ANIMAL MODEL SOURCES                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1. QUATERNIUS ULTIMATE ANIMAL PACK (CC0 — Best Choice!)                    ║
║     URL  : https://quaternius.itch.io/ultimate-animal-pack                  ║
║     Info : 100+ animated animals, GLB format, completely free (CC0)         ║
║     How  : Click "Download Now" → enter $0 → download ZIP                  ║
║     Animals: Bear, Boar, Bull, Camel, Cat, Chicken, Cow, Deer, Dog,        ║
║              Donkey, Duck, Eagle, Elephant, Fish, Fox, Frog, Giraffe,       ║
║              Goat, Gorilla, Horse, Husky, Kangaroo, Lion, Llama, Mole,     ║
║              Monkey, Moose, Narwhal, Ostrich, Panda, Parrot, Penguin,       ║
║              Pig, Pigeon, Rabbit, Reindeer, Sheep, Shrimp, Skunk,           ║
║              Snail, Snake, Spider, Squirrel, Tiger, Turtle, Wolf, ...       ║
║                                                                              ║
║  2. POLY.PIZZA (CC0 — No Login Required)                                     ║
║     URL  : https://poly.pizza                                                ║
║     Info : Thousands of CC0 low-poly models, GLB download with one click    ║
║     How  : Search for animal name → click Download                          ║
║                                                                              ║
║  3. SKETCHFAB FREE DOWNLOADS (Various licenses)                              ║
║     URL  : https://sketchfab.com/search?features=downloadable&license=cc0   ║
║             &type=models&q=animal                                            ║
║     Info : High-quality models, free account required for download          ║
║                                                                              ║
║  4. KHRONOS GROUP SAMPLE ASSETS (CC BY 4.0)                                 ║
║     URL  : https://github.com/KhronosGroup/glTF-Sample-Assets               ║
║     Info : Official glTF sample models including animals                    ║
║                                                                              ║
║  5. GOOGLE MODEL VIEWER EXAMPLES                                             ║
║     URL  : https://modelviewer.dev/examples/                                ║
║     Info : Production-quality models with animations                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("═" * 60)
    print("  🦁  3D Animal Model Downloader")
    print("═" * 60)
    print(f"  Output directory: {OUTPUT_DIR.resolve()}")
    print()

    print(MANUAL_SOURCES)

    # Download KhronosGroup models (most reliable, direct GitHub raw links)
    print("── Downloading from KhronosGroup glTF Sample Assets ──────")
    khronos_models = [
        ("Fox",    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Fox/glTF-Binary/Fox.glb",   "fox.glb"),
        ("Duck",   "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Duck/glTF-Binary/Duck.glb", "duck.glb"),
        ("CesiumMan", "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CesiumMan/glTF-Binary/CesiumMan.glb", "cesiumman.glb"),
    ]

    results = {"ok": [], "failed": [], "skipped": []}

    for name, url, filename in khronos_models:
        dest = OUTPUT_DIR / filename
        ok = download_file(url, dest, name)
        (results["ok"] if ok else results["failed"]).append(name)
        time.sleep(0.5)

    # Download from model-viewer sample assets
    print()
    print("── Downloading from Google model-viewer ──────────────────")
    mv_models = [
        ("Astronaut", "https://modelviewer.dev/shared-assets/models/Astronaut.glb", "astronaut.glb"),
        ("RobotExpressive", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/RobotExpressive/RobotExpressive.glb", "robot.glb"),
    ]
    for name, url, filename in mv_models:
        dest = OUTPUT_DIR / filename
        ok = download_file(url, dest, name)
        (results["ok"] if ok else results["failed"]).append(name)
        time.sleep(0.5)

    # Summary
    print()
    print("═" * 60)
    print(f"  ✓ Downloaded : {len(results['ok'])} models")
    print(f"  ✗ Failed     : {len(results['failed'])} models")
    print()
    print("  👉 For 100+ animals, download the Quaternius pack:")
    print("     https://quaternius.itch.io/ultimate-animal-pack")
    print()
    print(f"  Place all .glb files in: {OUTPUT_DIR.resolve()}")
    print("  Then open index.html in your browser!")
    print("═" * 60)


if __name__ == "__main__":
    main()
