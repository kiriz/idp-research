#!/usr/bin/env python3
"""Download P0+P1 PDFs from PingIdentity archive CDN."""
import json
import os
import subprocess
import sys
from pathlib import Path

BASE_URL = "https://cdn-docs.pingidentity.com/archive/pdf/"
ARCHIVE_DIR = Path("/Users/kirane/projects/idp/docs/archive")
CATALOG = ARCHIVE_DIR / "catalog.json"

TARGETS = {
    ("pingam", "openam"), ("pingam", "am"),
    ("pingds", "ds"),
    ("pinggateway", "ig"), ("pinggateway", "openig"),
    ("pingidm", "idm"), ("pingidm", "openidm"),
}

def should_download(product, version):
    if product in ("openam", "am"):
        return True
    if product == "ds":
        try:
            return float(version) >= 6.5
        except ValueError:
            return False
    if product in ("ig", "openig", "idm", "openidm"):
        return True
    return False

def main():
    with open(CATALOG) as f:
        data = json.load(f)

    to_download = []
    for item in data:
        key = (item["family"], item["product"])
        if key not in TARGETS:
            continue
        for pdf in item["pdflist"]:
            v = pdf.get("version", "")
            if not v:
                parts = pdf["path"].split("/")
                v = parts[1] if len(parts) > 1 else ""
            if not should_download(item["product"], v):
                continue
            if "javadoc" in pdf["path"].lower() or pdf["path"].endswith(".zip"):
                continue
            to_download.append((item["product"], v, pdf["path"], pdf["title"]))

    print(f"Downloading {len(to_download)} PDFs...")

    success = 0
    failures = []
    p0_missing = []
    total_bytes = 0

    for i, (product, version, path, title) in enumerate(to_download, 1):
        url = BASE_URL + path
        dest = ARCHIVE_DIR / path
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists() and dest.stat().st_size > 0:
            total_bytes += dest.stat().st_size
            success += 1
            continue

        result = subprocess.run(
            ["curl", "-sS", "-f", "-L", "-o", str(dest), url],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0 and dest.exists():
            sz = dest.stat().st_size
            total_bytes += sz
            success += 1
            if i % 25 == 0:
                print(f"  [{i}/{len(to_download)}] OK ({sz//1024}KB)")
        else:
            err = result.stderr.strip()[:100]
            failures.append((product, version, path, err))
            if product in ("openam", "am"):
                p0_missing.append(path)
            print(f"  [{i}/{len(to_download)}] WARN: {path} - {err}")

    # Write manifest
    manifest = ARCHIVE_DIR / "manifest.md"
    with open(manifest, "w") as f:
        f.write("# PDF Archive Manifest\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total PDFs attempted:** {len(to_download)}\n")
        f.write(f"- **Successful downloads:** {success}\n")
        f.write(f"- **Failures:** {len(failures)}\n")
        f.write(f"- **Total size:** {total_bytes / (1024*1024):.1f} MB\n\n")

        if failures:
            f.write("## Failures\n\n")
            f.write("| Product | Version | Path | Error |\n")
            f.write("|---------|---------|------|-------|\n")
            for prod, ver, path, err in failures:
                f.write(f"| {prod} | {ver} | `{path}` | {err} |\n")
            f.write("\n")

        if p0_missing:
            f.write("## P0 MISSING (CRITICAL)\n\n")
            for p in p0_missing:
                f.write(f"- `{p}`\n")
            f.write("\n")

        f.write("## Downloaded Files\n\n")
        for prod, ver, path, title in to_download:
            status = "FAIL" if path in [x[2] for x in failures] else "OK"
            f.write(f"- [{status}] `{path}` - {title}\n")

    print(f"\nDone: {success}/{len(to_download)} downloaded, {len(failures)} failures")
    print(f"Total: {total_bytes / (1024*1024):.1f} MB")
    print(f"Manifest: {manifest}")

    if p0_missing:
        print(f"\nCRITICAL: {len(p0_missing)} P0 PDFs missing!")
        sys.exit(1)

if __name__ == "__main__":
    main()
