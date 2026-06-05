#!/usr/bin/env python3
"""
Atlas Watcher — NthDimension Academy
=====================================
Drop an HTML file into the pending/ folder → auto-deploys to nthdimensionacademy.com
No Claude needed. Runs as a background process on Windows.

Folder layout (auto-created on first run):
  atlas-publisher/
  ├── .env             ← ATLAS_GITHUB_TOKEN here
  ├── atlas_watch.py   ← this file
  ├── atlas_deploy.py  ← deploy engine
  ├── pending/         ← DROP HTML FILES HERE
  └── deployed/        ← moved here after success

Filename → slug mapping (auto-detected):
  dp700-atlas.html              → dp700-atlas
  dp700-atlas_v3.html           → dp700-atlas
  DP700_Atlas_NthDimension.html → dp700-atlas
  DP600_Atlas_v2.html           → dp600-atlas
  DP750_Atlas.html              → dp750-atlas
  ai102-atlas.html              → ai102-atlas  (new exam)

Start: python atlas_watch.py
Stop:  Ctrl+C
"""

import importlib.util
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent
PENDING_DIR  = BASE_DIR / "pending"
DEPLOYED_DIR = BASE_DIR / "deployed"
FAILED_DIR   = BASE_DIR / "failed"
ENV_FILE     = BASE_DIR / ".env"
DEPLOY_SCRIPT = BASE_DIR / "atlas_deploy.py"

POLL_INTERVAL = 5   # seconds between folder scans

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "atlas_watcher.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("atlas-watcher")


# ── .env loader (no python-dotenv needed) ─────────────────────────────────────
def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ── Slug detection ─────────────────────────────────────────────────────────────
KNOWN_SLUGS = {
    "dp700": "dp700-atlas",
    "dp600": "dp600-atlas",
    "dp750": "dp750-atlas",
    "dp500": "dp500-atlas",
    "ai102": "ai102-atlas",
    "ai103": "ai103-atlas",
    "ai900": "ai900-atlas",
    "dp900": "dp900-atlas",
    "az900": "az900-atlas",
    "az104": "az104-atlas",
}


def detect_slug(filename: str) -> str | None:
    """
    Detect deployment slug from filename.
    Returns slug string or None if unrecognised.
    """
    stem = Path(filename).stem.lower()
    # Normalise separators
    stem = re.sub(r"[_\s]+", "-", stem)
    # Strip trailing version tags: -v3, -v3-1, -2, __2__
    stem = re.sub(r"-v\d+[\d\-]*$", "", stem)
    stem = re.sub(r"-\d+$", "", stem)

    # Check known exam codes
    for code, slug in KNOWN_SLUGS.items():
        if code in stem:
            return slug

    # If filename already matches slug pattern exactly (e.g. "ai102-atlas")
    if re.match(r"^[a-z]{2}\d{3,4}-[a-z]+$", stem):
        return stem

    return None


# ── Deploy engine ──────────────────────────────────────────────────────────────
def load_deploy_module():
    """Dynamically load atlas_deploy.py so we don't subprocess."""
    if not DEPLOY_SCRIPT.exists():
        raise FileNotFoundError(
            f"atlas_deploy.py not found at {DEPLOY_SCRIPT}\n"
            "Download it from Claude and place it next to atlas_watch.py."
        )
    spec = importlib.util.spec_from_file_location("atlas_deploy", DEPLOY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def deploy_file(html_path: Path, slug: str, token: str, deploy_mod) -> bool:
    """Returns True on success."""
    try:
        deploy_mod.deploy_batch([(slug, str(html_path))], token)
        return True
    except Exception as exc:
        log.error("Deploy failed for %s → %s: %s", html_path.name, slug, exc)
        return False


# ── File routing ───────────────────────────────────────────────────────────────
def archive_file(src: Path, target_dir: Path, slug: str) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dest = target_dir / f"{ts}_{slug}{src.suffix}"
    # Avoid collisions
    counter = 1
    while dest.exists():
        dest = target_dir / f"{ts}_{slug}_{counter}{src.suffix}"
        counter += 1
    shutil.move(str(src), str(dest))
    log.info("Archived → %s", dest.name)


# ── Main watcher loop ──────────────────────────────────────────────────────────
def watch():
    # Create folders
    for d in (PENDING_DIR, DEPLOYED_DIR, FAILED_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # Load env
    env = load_env(ENV_FILE)
    token = env.get("ATLAS_GITHUB_TOKEN") or os.environ.get("ATLAS_GITHUB_TOKEN")
    if not token or token == "ghp_your_token_here":
        log.error("No ATLAS_GITHUB_TOKEN found in .env — aborting.")
        log.error("Edit .env and set ATLAS_GITHUB_TOKEN=ghp_xxx")
        sys.exit(1)

    # Load deploy module
    try:
        deploy_mod = load_deploy_module()
    except FileNotFoundError as e:
        log.error(str(e))
        sys.exit(1)

    log.info("=" * 60)
    log.info("Atlas Watcher started")
    log.info("Watching: %s", PENDING_DIR)
    log.info("Drop HTML files there — they deploy automatically.")
    log.info("Stop with Ctrl+C")
    log.info("=" * 60)

    processed = set()   # avoid re-processing the same file in one poll cycle

    while True:
        try:
            html_files = sorted(PENDING_DIR.glob("*.html"))

            for html_path in html_files:
                if html_path.name in processed:
                    continue

                slug = detect_slug(html_path.name)
                if slug is None:
                    log.warning(
                        "⚠  Cannot detect slug for '%s' — skipping.\n"
                        "   Rename to include exam code: dp700, dp600, dp750, ai102…",
                        html_path.name,
                    )
                    processed.add(html_path.name)   # skip on next scan too
                    continue

                size_kb = html_path.stat().st_size // 1024
                log.info("📦 Detected: %s (%d KB) → slug: %s", html_path.name, size_kb, slug)

                # Re-read token each cycle (in case .env was updated)
                env = load_env(ENV_FILE)
                token = env.get("ATLAS_GITHUB_TOKEN") or os.environ.get("ATLAS_GITHUB_TOKEN")

                success = deploy_file(html_path, slug, token, deploy_mod)

                if success:
                    log.info("✅ Deployed: https://nthdimensionacademy.com/%s/", slug)
                    archive_file(html_path, DEPLOYED_DIR, slug)
                else:
                    log.error("❌ Failed: %s → moved to failed/", html_path.name)
                    archive_file(html_path, FAILED_DIR, slug)

                processed.add(html_path.name)

            # Reset processed set each cycle so new files with same name work
            if not html_files:
                processed.clear()

        except KeyboardInterrupt:
            log.info("Watcher stopped.")
            break
        except Exception as exc:
            log.exception("Unexpected error: %s", exc)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    watch()
