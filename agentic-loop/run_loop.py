"""
Loop runner:
- Evaluates current train.py with prepare.py
- Tracks best score
- Snapshots winners
- Auto-reverts regressions
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
TRAIN_FILE = ROOT / "train.py"
PREPARE_FILE = ROOT / "prepare.py"
STATE_DIR = ROOT / ".autoresearch"
BEST_TRAIN_FILE = STATE_DIR / "best_train.py"
BEST_META_FILE = STATE_DIR / "best_meta.json"
DEFAULT_TIMEOUT_SECONDS = 10


def _run(cmd: list[str], cwd: Path = ROOT, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def _git_available() -> bool:
    result = _run(["git", "--version"])
    return result.returncode == 0


def _assert_write_scope() -> None:
    """
    Guardrail: before each scoring run, ensure only train.py is user-modified.
    """
    if not _git_available():
        return

    allowed = {
        str(TRAIN_FILE.relative_to(ROOT.parent)).replace("\\", "/"),
        str(BEST_TRAIN_FILE.relative_to(ROOT.parent)).replace("\\", "/"),
        str(BEST_META_FILE.relative_to(ROOT.parent)).replace("\\", "/"),
    }
    allowed_prefix = f"{str(STATE_DIR.relative_to(ROOT.parent)).replace('\\', '/')}/"

    violations: list[str] = []
    checks = [
        ["git", "diff", "--name-only", "--", str(ROOT)],
        ["git", "diff", "--name-only", "--cached", "--", str(ROOT)],
    ]
    for cmd in checks:
        diff = _run(cmd)
        if diff.returncode != 0:
            continue
        for line in diff.stdout.splitlines():
            rel = line.strip().replace("\\", "/")
            if not rel:
                continue
            if rel in allowed:
                continue
            if rel.startswith(allowed_prefix):
                continue
            violations.append(rel)

    if violations:
        unique = sorted(set(violations))
        joined = ", ".join(unique)
        raise RuntimeError(
            "Write-scope violation: modified files detected outside train.py/.autoresearch: "
            f"{joined}"
        )


def _evaluate(timeout_seconds: int) -> dict[str, Any]:
    result = _run(
        [
            sys.executable,
            str(PREPARE_FILE),
            "--train-path",
            str(TRAIN_FILE),
            "--timeout-seconds",
            str(timeout_seconds),
            "--json",
        ]
    )

    if not result.stdout.strip():
        return {
            "ok": False,
            "score": 0.0,
            "runtime_ms": 0,
            "error": f"prepare.py returned no output (stderr: {result.stderr.strip()})",
        }

    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "score": 0.0,
            "runtime_ms": 0,
            "error": f"Invalid JSON from prepare.py: {exc}",
        }

    return payload


def _load_best_meta() -> dict[str, Any]:
    if not BEST_META_FILE.exists():
        return {"best_score": float("-inf")}
    return json.loads(BEST_META_FILE.read_text(encoding="utf-8"))


def _save_winner(score_payload: dict[str, Any]) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    shutil.copy2(TRAIN_FILE, BEST_TRAIN_FILE)
    meta = {
        "best_score": float(score_payload["score"]),
        "runtime_ms": int(score_payload.get("runtime_ms", 0)),
        "error": score_payload.get("error"),
    }
    BEST_META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _restore_winner() -> None:
    if BEST_TRAIN_FILE.exists():
        shutil.copy2(BEST_TRAIN_FILE, TRAIN_FILE)


def _commit_winner(score: float) -> None:
    if not _git_available():
        print("git unavailable; skipped winner commit")
        return
    _run(["git", "add", str(TRAIN_FILE), str(BEST_TRAIN_FILE), str(BEST_META_FILE)])
    msg = f"autoresearch winner: score={score:.6f}"
    commit = _run(["git", "commit", "-m", msg])
    if commit.returncode != 0:
        print("Winner snapshot staged but commit was not created.")
        if commit.stderr.strip():
            print(commit.stderr.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AutoResearch loop runner")
    parser.add_argument("--init", action="store_true", help="Initialize baseline winner from current train.py")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Must stay constant across runs for fair comparisons",
    )
    parser.add_argument(
        "--commit-winner",
        action="store_true",
        help="Create a git commit when score improves",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _assert_write_scope()

    current = _evaluate(int(args.timeout_seconds))
    if not current["ok"]:
        print(f"Evaluation failed. score={current['score']:.6f} error={current['error']}")
        if BEST_TRAIN_FILE.exists():
            _restore_winner()
            print("Restored train.py from last winner snapshot.")
        return 1

    best = _load_best_meta()
    best_score = float(best.get("best_score", float("-inf")))
    score = float(current["score"])

    if args.init or not BEST_TRAIN_FILE.exists():
        _save_winner(current)
        print(f"Initialized baseline winner. score={score:.6f}")
        if args.commit_winner:
            _commit_winner(score)
        return 0

    if score > best_score:
        _save_winner(current)
        print(f"Improved score {best_score:.6f} -> {score:.6f}. Winner saved.")
        if args.commit_winner:
            _commit_winner(score)
        return 0

    _restore_winner()
    print(f"No improvement (best={best_score:.6f}, current={score:.6f}). Reverted to winner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
