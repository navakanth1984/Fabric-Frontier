#!/usr/bin/env python3
"""
NthDimension Academy — Atlas Deploy Script
==========================================
Deploys standalone HTML atlas files to nthdimensionacademy.com/{slug}/
Uses GitHub Git Blobs API — handles files of any size (atlases are ~1.3–1.7 MB).

Usage:
  python atlas_deploy.py <slug> <html_file> [--token TOKEN]
  python atlas_deploy.py --verify <slug>
  python atlas_deploy.py --batch slugs_files.txt

  Token via env (recommended):
    export ATLAS_GITHUB_TOKEN=ghp_xxx
    python atlas_deploy.py dp700-atlas DP700_v3.html

Examples:
  python atlas_deploy.py dp700-atlas DP700_Atlas_v3.html --token ghp_xxx
  python atlas_deploy.py dp750-atlas DP750_Atlas_v2.html
  python atlas_deploy.py --verify dp700-atlas
  python atlas_deploy.py --batch updates.txt

Batch file format (updates.txt):
  dp700-atlas  DP700_Atlas_v3.html
  dp750-atlas  DP750_Atlas_v2.html
  dp600-atlas  DP600_Atlas_v2.html

Existing slugs:
  dp700-atlas  →  nthdimensionacademy.com/dp700-atlas/  (DP-700 Fabric Data Engineer)
  dp750-atlas  →  nthdimensionacademy.com/dp750-atlas/  (DP-750 Azure Databricks)
  dp600-atlas  →  nthdimensionacademy.com/dp600-atlas/  (DP-600 Fabric Analytics)
"""

import argparse
import base64
import os
import sys
import time
import urllib.request

try:
    import requests
except ImportError:
    print("❌ requests not found. Run: pip install requests")
    sys.exit(1)

# ── Constants ──────────────────────────────────────────────────────────────────
OWNER      = "navakanth1984"
REPO       = "Fabric-Frontier"
BRANCH     = "main"
BASE_URL   = "https://nthdimensionacademy.com"
GITHUB_API = "https://api.github.com"


def make_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def create_blob(headers: dict, encoded: str) -> str:
    r = requests.post(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/git/blobs",
        headers=headers,
        json={"content": encoded, "encoding": "base64"},
    )
    r.raise_for_status()
    return r.json()["sha"]


def get_head_and_tree(headers: dict) -> tuple[str, str]:
    r = requests.get(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}",
        headers=headers,
    )
    r.raise_for_status()
    head_sha = r.json()["object"]["sha"]

    r2 = requests.get(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/git/commits/{head_sha}",
        headers=headers,
    )
    r2.raise_for_status()
    tree_sha = r2.json()["tree"]["sha"]
    return head_sha, tree_sha


def create_tree(headers: dict, base_tree: str, items: list) -> str:
    r = requests.post(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/git/trees",
        headers=headers,
        json={"base_tree": base_tree, "tree": items},
    )
    r.raise_for_status()
    return r.json()["sha"]


def create_commit(headers: dict, message: str, tree_sha: str, parent_sha: str) -> str:
    r = requests.post(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/git/commits",
        headers=headers,
        json={"message": message, "tree": tree_sha, "parents": [parent_sha]},
    )
    r.raise_for_status()
    return r.json()["sha"]


def update_ref(headers: dict, commit_sha: str) -> None:
    r = requests.patch(
        f"{GITHUB_API}/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
        headers=headers,
        json={"sha": commit_sha},
    )
    r.raise_for_status()


# ── Single deploy ──────────────────────────────────────────────────────────────
def deploy_one(slug: str, html_path: str, token: str, label: str = "") -> str:
    """Deploy one file. Returns the live URL."""
    tag = f"[{label}] " if label else ""
    headers = make_headers(token)
    target = f"nthdimensionacademy/{slug}/index.html"

    if not os.path.isfile(html_path):
        raise FileNotFoundError(f"File not found: {html_path}")

    with open(html_path, "rb") as f:
        raw = f.read()
    encoded = base64.b64encode(raw).decode()
    size_kb = len(raw) // 1024
    print(f"{tag}📦 Encoding {html_path} ({size_kb} KB)...")

    blob_sha = create_blob(headers, encoded)
    print(f"{tag}✅ Blob: {blob_sha[:10]}...")

    return blob_sha, target, size_kb


# ── Batch deploy (single commit) ───────────────────────────────────────────────
def deploy_batch(items: list[tuple[str, str]], token: str) -> None:
    """
    items: list of (slug, html_path)
    All files pushed in a single commit.
    """
    headers = make_headers(token)

    print(f"📋 Batch deploy: {len(items)} file(s)")

    # Create all blobs
    tree_items = []
    for slug, html_path in items:
        blob_sha, target, size_kb = deploy_one(slug, html_path, token, slug)
        tree_items.append({
            "path": target,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha,
        })

    # One commit for all files
    head_sha, base_tree = get_head_and_tree(headers)
    print(f"🔗 HEAD: {head_sha[:10]}... | Tree: {base_tree[:10]}...")

    new_tree = create_tree(headers, base_tree, tree_items)
    slugs_label = ", ".join(s for s, _ in items)
    new_commit = create_commit(headers, f"🔄 Update {slugs_label}", new_tree, head_sha)
    update_ref(headers, new_commit)

    print(f"\n✅ Commit {new_commit[:10]}... — branch updated!")
    print(f"⏳ GitHub Actions deploying — live in ~60s\n")
    for slug, _ in items:
        print(f"   🌐 https://nthdimensionacademy.com/{slug}/")


# ── Single deploy wrapper ──────────────────────────────────────────────────────
def deploy_single(slug: str, html_path: str, token: str) -> None:
    deploy_batch([(slug, html_path)], token)


# ── Verify ─────────────────────────────────────────────────────────────────────
def verify(slug: str, retries: int = 3, delay: int = 20) -> None:
    url = f"{BASE_URL}/{slug}/"
    print(f"🔍 Checking {url}")
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "atlas-deploy/1.0"})
            res = urllib.request.urlopen(req, timeout=10)
            print(f"✅ HTTP {res.status} — live!")
            return
        except urllib.error.HTTPError as e:
            print(f"   Attempt {attempt}/{retries}: HTTP {e.code}")
        except Exception as e:
            print(f"   Attempt {attempt}/{retries}: {e}")
        if attempt < retries:
            print(f"   Waiting {delay}s...")
            time.sleep(delay)
    print("⏳ Not live yet — GitHub Actions may still be building. Try again in 60s.")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="NthDimension Academy — Atlas Deploy Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("slug",   nargs="?", help="Target slug, e.g. dp700-atlas")
    parser.add_argument("file",   nargs="?", help="Path to HTML file")
    parser.add_argument("--token",  help="GitHub PAT (or set ATLAS_GITHUB_TOKEN env var)")
    parser.add_argument("--verify", metavar="SLUG", help="Check if slug is live (no deploy)")
    parser.add_argument("--batch",  metavar="FILE",
                        help="Batch file: each line = 'slug  html_path'")
    args = parser.parse_args()

    # ── Verify only
    if args.verify:
        verify(args.verify)
        return

    # ── Resolve token
    token = args.token or os.environ.get("ATLAS_GITHUB_TOKEN")
    if not token:
        sys.exit("❌ Provide --token or set ATLAS_GITHUB_TOKEN env var.\n"
                 "   Get a PAT at: github.com → Settings → Developer settings → "
                 "Personal access tokens (scope: repo, expiry: 1 day)\n"
                 "   ⚠️  Revoke immediately after use.")

    # ── Batch mode
    if args.batch:
        if not os.path.isfile(args.batch):
            sys.exit(f"❌ Batch file not found: {args.batch}")
        items = []
        with open(args.batch) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 2:
                    sys.exit(f"❌ Bad batch line (expected: slug  file): {line!r}")
                items.append((parts[0], parts[1]))
        if not items:
            sys.exit("❌ No valid lines in batch file.")
        deploy_batch(items, token)
        return

    # ── Single mode
    if not args.slug or not args.file:
        parser.print_help()
        sys.exit("\n❌ Provide slug and file, or use --batch, or --verify.")

    deploy_single(args.slug, args.file, token)


if __name__ == "__main__":
    main()
