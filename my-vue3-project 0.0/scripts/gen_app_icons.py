# -*- coding: utf-8 -*-
"""从 static/07.icon.jpg 生成 uni-app 规范尺寸图标（真 PNG、RGB、无 alpha）。"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "static" / "07.icon.jpg"
OUT = ROOT / "src" / "static" / "icons"

SIZES = {
    # Android
    "72x72.png": 72,
    "96x96.png": 96,
    "144x144.png": 144,
    "192x192.png": 192,
    # iOS
    "20x20.png": 20,
    "29x29.png": 29,
    "40x40.png": 40,
    "58x58.png": 58,
    "60x60.png": 60,
    "76x76.png": 76,
    "80x80.png": 80,
    "87x87.png": 87,
    "120x120.png": 120,
    "152x152.png": 152,
    "167x167.png": 167,
    "180x180.png": 180,
    "1024x1024.png": 1024,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    orig = Image.open(SRC).convert("RGB")
    print("source", orig.size, orig.mode)

    for name, side in SIZES.items():
        im = orig.resize((side, side), Image.Resampling.LANCZOS).convert("RGB")
        path = OUT / name
        im.save(path, "PNG", optimize=True)
        check = Image.open(path)
        print(f"{name}: {check.size[0]}x{check.size[1]} mode={check.mode} bytes={path.stat().st_size}")


if __name__ == "__main__":
    main()
