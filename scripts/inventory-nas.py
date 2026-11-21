#!/usr/bin/env python3
"""Walk the NAS model roots and print a JSON inventory to stdout.

Run on the NAS (or via SSH from the MacBook Pro):

    ssh ian@192.168.12.66 python3 -s - < scripts/inventory-nas.py

Does not read tokens, env files, or credentials. Excludes .cache, .git,
.hf-home, AppleDouble, and the .download-complete marker from sizes.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

ARCH = Path("/volume3/cold-archive/models/2026-11-hf-archive")
WD = Path("/mnt/@usb/sdd1/2026-11-hf-media")
DEVICE = Path("/mnt/@usb/sdd1/2026-11-device-models")

SKIP_DIRS = {".cache", ".git", ".hf-home"}
SKIP_NAMES = {".download-complete", "DOWNLOAD_COMPLETE", "CACHEDIR.TAG"}
WEIGHT_SUFFIX = {
    ".gguf", ".safetensors", ".bin", ".pt", ".pth", ".onnx",
    ".npz", ".mlx", ".msgpack", ".pickle", ".ckpt",
}


def is_skipped_file(name: str) -> bool:
    if name.startswith("._"):
        return True
    if name in SKIP_NAMES or name.startswith("DOWNLOAD_") and name.endswith("_COMPLETE"):
        return True
    return False


def walk_folder(root: Path) -> dict:
    size = 0
    files = 0
    incomplete = 0
    has_weights = False
    download_complete = (root / ".download-complete").is_file()
    if not download_complete:
        # some older jobs wrote DOWNLOAD_COMPLETE or a sibling marker
        for marker in root.glob("DOWNLOAD*COMPLETE"):
            if marker.is_file():
                download_complete = True
                break
    if not root.is_dir():
        return {
            "exists": False,
            "size_bytes": 0,
            "files": 0,
            "download_complete": False,
            "incomplete_files": 0,
            "has_weights": False,
        }
    # Count in-progress Hugging Face downloads inside .cache, but never
    # add cache bytes to the published size.
    cache = root / ".cache"
    if cache.is_dir():
        for dirpath, dirnames, filenames in os.walk(cache):
            for fn in filenames:
                if fn.endswith(".incomplete"):
                    incomplete += 1
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("._")]
        for fn in filenames:
            if is_skipped_file(fn):
                continue
            fp = Path(dirpath) / fn
            if fn.endswith(".incomplete") or fn.endswith(".lock"):
                if fn.endswith(".incomplete"):
                    incomplete += 1
                continue
            try:
                st = fp.stat()
            except OSError:
                continue
            size += st.st_size
            files += 1
            suffix = fp.suffix.lower()
            if suffix in WEIGHT_SUFFIX or st.st_size >= 8 * 1024 * 1024:
                has_weights = True
    return {
        "exists": True,
        "size_bytes": size,
        "files": files,
        "download_complete": download_complete,
        "incomplete_files": incomplete,
        "has_weights": has_weights,
    }


def area_children(area: str, root: Path) -> list:
    out = []
    if not root.is_dir():
        return out
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        rec = walk_folder(child)
        rec.update({
            "key": f"{area}/{child.name}",
            "area": area,
            "name": child.name,
            "path": str(child),
        })
        out.append(rec)
    return out


def read_device_status() -> dict:
    copy_log = DEVICE / "devmodels-copy.log"
    verify_log = DEVICE / "devmodels-verify.log"
    text_copy = copy_log.read_text(errors="replace") if copy_log.is_file() else ""
    text_verify = verify_log.read_text(errors="replace") if verify_log.is_file() else ""
    verified = text_verify.count("VERIFIED |")
    mismatches = sum(
        1 for line in text_verify.splitlines()
        if any(tok in line for tok in ("MISMATCH", "FAIL", "MISSING", "ERROR"))
        and "VERIFIED" not in line
    )
    return {
        "root": str(DEVICE),
        "exists": DEVICE.is_dir(),
        "copy_log_all_done": "ALL-DONE" in text_copy,
        "verify_done": "VERIFY-DONE" in text_verify,
        "verify_verified": verified,
        "verify_mismatches": mismatches,
        "copy_log": str(copy_log) if copy_log.is_file() else None,
        "verify_log": str(verify_log) if verify_log.is_file() else None,
    }


def main() -> None:
    folders = []
    folders += area_children("official", ARCH / "official")
    folders += area_children("abliterated", ARCH / "abliterated")
    folders += area_children("media", ARCH / "media")
    folders += area_children("extras", ARCH / "extras")
    folders += area_children("usb-media/image", WD / "image")
    folders += area_children("usb-media/video", WD / "video")
    folders += area_children("usb-media/audio", WD / "audio")
    inv = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "roots": {"archive": str(ARCH), "media": str(WD), "device": str(DEVICE)},
        "folders": folders,
        "device": read_device_status(),
    }
    print(json.dumps(inv, indent=2))


if __name__ == "__main__":
    main()
