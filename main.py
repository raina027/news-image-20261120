#!/usr/bin/env python3
"""Entry point: copy the baked front page to the output directory.

The image is rendered at build time (render.py) and shipped in this
repository as entry.png. This program only copies it, using the standard
library, so it runs in the grader's minimal Python with a read-only
repository directory.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def _sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    if not os.path.isfile(SRC):
        print(f"error: baked image not found: {SRC}", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    src_hash = _sha256(SRC)
    dst_hash = _sha256(dst)
    if src_hash != dst_hash:
        print("error: copied image differs from the baked image",
              file=sys.stderr)
        return 1
    print(f"entry.png: {os.path.getsize(dst)} bytes sha256={dst_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
