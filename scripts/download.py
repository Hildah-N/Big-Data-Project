"""
download.py
TSV-first PatentsView downloader (production-safe, idempotent)

Key design:
- .tsv files are the source of truth
- ZIPs are temporary transport only
- No fragile ZIP validation
"""

import requests
import zipfile
import json
import time
from pathlib import Path

# ── Configuration ───────────────────────────────────────────
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://s3.amazonaws.com/data.patentsview.org/download/"

FILES = [
    "g_patent.tsv",
    "g_inventor_disambiguated.tsv",
    "g_assignee_disambiguated.tsv",
    "g_patent_abstract.tsv",
    "g_location_disambiguated.tsv",
    "g_application.tsv",
]

MAX_RETRIES = 3
MIN_VALID_SIZE_MB = 5   # threshold to consider TSV “real”


# ── Helpers ─────────────────────────────────────────────────

def tsv_exists(tsv_path: Path) -> bool:
    """Check if TSV already exists and looks valid."""
    return tsv_path.exists() and tsv_path.stat().st_size > MIN_VALID_SIZE_MB * 1024 * 1024


# ── Download ────────────────────────────────────────────────

def download_zip(url: str, dest: Path) -> bool:
    """Download ZIP with retry (no strict content-type checks)."""

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  [↓] Downloading {dest.name} (Attempt {attempt})...")

        try:
            response = requests.get(url, stream=True, timeout=120)
            response.raise_for_status()

            # Only reject obvious failure
            if "text/html" in response.headers.get("Content-Type", ""):
                print("  [ERROR] Got HTML instead of file")
                return False

            total = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total:
                            pct = downloaded / total * 100
                            mb_dl = downloaded // (1024**2)
                            mb_total = total // (1024**2)
                            print(f"\r    {pct:.1f}% ({mb_dl}/{mb_total} MB)", end="", flush=True)

            print(f"\r  [✓] Saved: {dest.name} ({dest.stat().st_size // (1024**2)} MB)")
            return True

        except Exception as e:
            print(f"\n  [ERROR] {e}")
            time.sleep(2)

    return False


# ── Extraction ──────────────────────────────────────────────

def extract_zip(zip_path: Path, expected_tsv: Path) -> bool:
    """Extract ZIP and ensure TSV is produced."""

    print(f"  [⇒] Extracting {zip_path.name} ...")

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(RAW_DIR)

        if not tsv_exists(expected_tsv):
            print("  [ERROR] Extraction failed: TSV not found or too small")
            return False

        print(f"  [✓] Extracted → {expected_tsv.name}")
        return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


# ── Main ───────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  PATENTSVIEW DOWNLOADER (TSV-FIRST FINAL)")
    print("=" * 60)

    print(f"\nData directory: {RAW_DIR.resolve()}")

    manifest = {}
    failed = []

    for tsv_name in FILES:
        print(f"\nProcessing: {tsv_name}")
        print("-" * 40)

        tsv_path = RAW_DIR / tsv_name
        zip_name = tsv_name + ".zip"
        zip_path = RAW_DIR / zip_name
        url = BASE_URL + zip_name

        # ✅ PRIMARY CHECK — TSV exists → skip everything
        if tsv_exists(tsv_path):
            print(f"  [SKIP] TSV already exists: {tsv_name}")
            manifest[tsv_name] = {
                "path": str(tsv_path),
                "size_mb": tsv_path.stat().st_size // (1024**2),
                "status": "existing"
            }
            continue

        # ⬇️ Download ZIP
        if not download_zip(url, zip_path):
            failed.append(tsv_name)
            continue

        # ⬇️ Extract
        if not extract_zip(zip_path, tsv_path):
            failed.append(tsv_name)
            continue

        # 🧹 Optional: remove ZIP after success
        try:
            zip_path.unlink()
            print(f"  [CLEAN] Removed ZIP: {zip_name}")
        except:
            pass

        manifest[tsv_name] = {
            "path": str(tsv_path),
            "size_mb": tsv_path.stat().st_size // (1024**2),
            "status": "downloaded"
        }

    # ── Save manifest ────────────────────────────────────────
    manifest_path = RAW_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ Success: {len(manifest)} files")
    if failed:
        print(f"❌ Failed: {len(failed)} files")

    print(f"\nManifest: {manifest_path}")

    if manifest:
        print("\n✓ Next step: run clean.py")


# ── Entry ──────────────────────────────────────────────────

if __name__ == "__main__":
    main()