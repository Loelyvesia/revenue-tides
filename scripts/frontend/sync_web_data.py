from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "data" / "web").resolve()
PUBLIC_ROOT = (ROOT / "public").resolve()
TARGET = (PUBLIC_ROOT / "data").resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Missing source web data: {SOURCE}")
    if TARGET.parent != PUBLIC_ROOT or TARGET.name != "data":
        raise SystemExit(f"Unsafe public-data target: {TARGET}")

    manifest = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))
    for record in manifest["files"]:
        source_file = SOURCE / record["path"]
        if not source_file.is_file() or sha256(source_file) != record["sha256"]:
            raise SystemExit(f"Frozen public-data hash mismatch: {record['path']}")

    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, TARGET)

    source_files = sorted(path.relative_to(SOURCE) for path in SOURCE.rglob("*") if path.is_file())
    target_files = sorted(path.relative_to(TARGET) for path in TARGET.rglob("*") if path.is_file())
    if source_files != target_files:
        raise SystemExit("Public-data sync file inventory mismatch")
    for relative in source_files:
        if sha256(SOURCE / relative) != sha256(TARGET / relative):
            raise SystemExit(f"Public-data sync hash mismatch: {relative.as_posix()}")

    print(f"SYNC PASS: {len(source_files)} files copied byte-identically to public/data")


if __name__ == "__main__":
    main()
