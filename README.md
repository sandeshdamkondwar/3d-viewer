# Animal Kingdom — 3D Explorer

An interactive 3D animal encyclopedia powered by Google's `<model-viewer>`. Browse 30+ animals across 5 categories, inspect each one in a full 3D viewer, and launch AR on supported mobile devices.

**Live preview → [sandeshdamkondwar.github.io/3d-viewer](https://sandeshdamkondwar.github.io/3d-viewer/)**

---

## Features

- **3D viewer** — rotate, zoom, and pan every animal model with mouse or touch
- **AR mode** — view animals in your physical space on iOS / Android
- **Category filter** — browse Mammals, Birds, Reptiles, Aquatic, and Insects separately
- **Search** — live search across all 30+ animals
- **Custom models** — drag & drop any `.glb` / `.gltf` file or paste a URL to add your own
- **Animal info panel** — scientific name, habitat, weight, lifespan, and conservation status for each animal
- **Responsive** — works on desktop, tablet, and mobile (collapsible sidebar on small screens)

## Animals Included

| Category | Examples |
|---|---|
| Mammals | Lion, Elephant, Tiger, Gorilla, Panda, Wolf, Bear, Giraffe, Zebra, Horse … |
| Birds | Eagle, Owl, Flamingo, Parrot, Penguin |
| Reptiles | Crocodile, Sea Turtle, Snake, T-Rex, Triceratops |
| Aquatic | Blue Whale, Great White Shark, Octopus, Dolphin, Jellyfish |
| Insects | Monarch Butterfly, Honey Bee |

## Running Locally

```bash
# Python (built-in)
python3 -m http.server 8000
# then open http://localhost:8000
```

> A local server is required because browsers block loading `.glb` files from `file://` URLs.

## Adding More Models

**Option 1 — Drag & drop**
Click **+ Add Model** in the header and drop any `.glb` or `.gltf` file onto the modal.

**Option 2 — URL**
Click **+ Add Model → From URL** and paste a direct link to a `.glb` file.

**Option 3 — Download script**
```bash
python3 download_animal_models.py
```

**Free model sources (CC0 license)**
- [Quaternius Ultimate Animal Pack](https://quaternius.itch.io/ultimate-animal-pack) — 100+ low-poly animals
- [Poly.pizza](https://poly.pizza) — search and download individual GLB files
- [KhronosGroup glTF Sample Assets](https://github.com/KhronosGroup/glTF-Sample-Assets)

## Tech Stack

| Layer | Technology |
|---|---|
| 3D rendering | [Google model-viewer](https://modelviewer.dev/) v4.0 |
| AR | WebXR / Scene Viewer / Quick Look |
| Fonts | Bebas Neue + DM Sans (Google Fonts) |
| Models | GLB / glTF binary format |
| Hosting | GitHub Pages |

## Project Structure

```
3d-viewer/
├── index.html                 # entire app (HTML + CSS + JS)
├── models/                    # GLB model files (48 animals)
│   ├── lion.glb
│   ├── elephant.glb
│   └── ...
└── download_animal_models.py  # helper script to fetch additional models
```
