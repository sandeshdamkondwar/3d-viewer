#!/usr/bin/env python3
"""
Animal Viewer — Local Dev Server
Serves index.html + ./models/ and exposes /api/models for auto-discovery.

Usage:
    python3 server.py           # default port 8000
    python3 server.py 3000      # custom port
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

MODELS_DIR = Path("./models")
MODELS_DIR.mkdir(exist_ok=True)

# Map filename stem → animal ID used in index.html ANIMALS array
# Allows auto-matching downloaded files to existing catalogue entries
FILENAME_TO_ID = {
    "horse": "horse", "parrot": "parrot", "flamingo": "flamingo", "stork": "stork",
    "fox": "fox", "duck": "duck", "dragon": "dragon",
    "lion": "lion", "tiger": "tiger", "elephant": "elephant", "giraffe": "giraffe",
    "zebra": "zebra", "bear": "bear", "wolf": "wolf", "gorilla": "gorilla",
    "panda": "panda", "deer": "deer", "rabbit": "rabbit", "pig": "pig",
    "cow": "cow", "chicken": "chicken", "dog": "dog", "cat": "cat",
    "shark": "shark", "whale": "whale", "dolphin": "dolphin", "octopus": "octopus",
    "turtle": "turtle", "penguin": "penguin", "eagle": "eagle", "owl": "owl",
    "crocodile": "crocodile", "snake": "snake", "frog": "frog", "jellyfish": "jellyfish",
    "butterfly": "butterfly", "bee": "bee", "trex": "trex",
    "kangaroo": "kangaroo", "koala": "koala", "camel": "camel", "llama": "llama",
    "rhino": "rhino", "hippo": "hippo", "cheetah": "cheetah", "monkey": "monkey",
    "moose": "moose", "sheep": "sheep", "goat": "goat", "squirrel": "squirrel",
    "raccoon": "raccoon", "hedgehog": "hedgehog", "bat": "bat", "toucan": "toucan",
    "stegosaurus": "stegosaurus", "mammoth": "mammoth", "narwhal": "narwhal",
    "axolotl": "axolotl", "lobster": "lobster", "chameleon": "chameleon",
    "crab": "crab", "fish": "fish", "seahorse": "seahorse", "bison": "bison",
    "donkey": "donkey", "spider": "spider", "scorpion": "scorpion",
}


def build_manifest() -> list[dict]:
    """Scan ./models/ and return a list of available model descriptors."""
    entries = []
    for f in sorted(MODELS_DIR.glob("*.glb")):
        stem = f.stem.lower()
        animal_id = FILENAME_TO_ID.get(stem, stem)
        entries.append({
            "id":       animal_id,
            "filename": f.name,
            "url":      f"/models/{f.name}",
            "size_kb":  round(f.stat().st_size / 1024),
        })
    return entries


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        # ── /api/models — return JSON manifest of available GLBs ──
        if parsed.path == "/api/models":
            manifest = build_manifest()
            body = json.dumps(manifest, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /api/reload — rescan models directory (for hot-reload) ──
        if parsed.path == "/api/reload":
            manifest = build_manifest()
            body = json.dumps({"reloaded": True, "count": len(manifest)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        # ── Everything else: serve static files ──
        super().do_GET()

    def log_message(self, fmt, *args):
        # Suppress .glb chunk-level noise; keep API and HTML requests
        msg = fmt % args
        if any(x in self.path for x in [".glb", ".js", ".css", ".ico"]) and "200" in msg:
            return
        print(f"  {self.address_string()}  {msg}")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("", port), Handler)

    glbs = list(MODELS_DIR.glob("*.glb"))

    print()
    print("═" * 54)
    print("  🦁  Animal Kingdom — Local Server")
    print("═" * 54)
    print(f"  http://localhost:{port}")
    print(f"  Models found: {len(glbs)} .glb files in ./models/")
    if not glbs:
        print()
        print("  No models yet. Run the downloader:")
        print("    export SKETCHFAB_TOKEN=\"your_token\"")
        print("    python3 download_animal_models.py")
        print()
        print("  Get your token: sketchfab.com/settings/password")
    print("  Press Ctrl+C to stop.")
    print("═" * 54)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")


if __name__ == "__main__":
    main()
