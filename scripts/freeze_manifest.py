# -*- coding: utf-8 -*-
"""Freeze manifest: SHA256 of every project file (excluding __pycache__ / .git)."""
import hashlib, json, os, datetime

ROOT = os.path.abspath(os.getcwd())
OUT = os.path.join(ROOT, "FREEZE_MANIFEST.json")
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", ".pytest_cache"}


def main():
    items = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if f == "FREEZE_MANIFEST.json" or f == ".env":
                continue
            fp = os.path.join(dp, f)
            rel = os.path.relpath(fp, ROOT).replace("\\", "/")
            h = hashlib.sha256()
            with open(fp, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            items.append({"path": rel, "sha256": h.hexdigest(), "size": os.path.getsize(fp)})
    doc = {
        "frozen_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "root": ROOT,
        "file_count": len(items),
        "files": items,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("FREEZE_OK files=%d -> %s" % (len(items), OUT))
    for it in items:
        print("  %s %s" % (it["sha256"][:16], it["path"]))


if __name__ == "__main__":
    main()
