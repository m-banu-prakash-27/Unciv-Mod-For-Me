#!/usr/bin/env python3
"""Apply the cumulative Magalanadu patch to the pinned Unciv release."""
from pathlib import Path
import re
import sys

from patch_unciv_v4_9 import apply as apply_native_spies

UNCIV_TAG = "4.22.18-patch1"


def apply(root: Path) -> None:
    config = root / "buildSrc/src/main/kotlin/BuildConfig.kt"
    match = re.search(r'\bconst val appVersion = "([^"]+)"', config.read_text(encoding="utf-8-sig"))
    version = match.group(1) if match else "unknown"
    if version != UNCIV_TAG:
        raise RuntimeError(f"Expected Unciv {UNCIV_TAG}, found {version}. Use a fresh checkout of the release tag.")
    apply_native_spies(root)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python engine_patch/patch_unciv_v4_9_1.py path/to/Unciv")
    apply(Path(sys.argv[1]))
