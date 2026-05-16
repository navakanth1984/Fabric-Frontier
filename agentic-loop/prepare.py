"""
Locked evaluator for the AutoResearch loop.

In production setups, keep evaluator logic and private data in a restricted boundary
that the optimizing agent cannot read or modify.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT_SECONDS = 10
FAIL_SCORE = 0.0

# In production, treat private evaluation data as restricted.
EVAL_CASES: list[tuple[str, str]] = [
    ("The app feels fast and very helpful", "positive"),
    ("This update is excellent and I love it", "positive"),
    ("Great support and good user experience", "positive"),
    ("The flow is broken and painfully slow", "negative"),
    ("Awful quality, I hate the new interface", "negative"),
    ("Terrible bug, bad release", "negative"),
    ("Helpful docs but slow onboarding", "positive"),
    ("Good concept but broken checkout", "negative"),
]


def _load_candidate(train_path: Path):
    spec = importlib.util.spec_from_file_location("candidate_train", train_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load candidate module: {train_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    predictor = getattr(module, "predict_label", None)
    if predictor is None or not callable(predictor):
        raise RuntimeError("train.py must define callable predict_label(text: str) -> str")
    return predictor


def _check_types(train_path: Path) -> bool:
    """Run pyrefly check and return True if 0 errors found."""
    try:
        # Run pyrefly check on the specific file to ensure type safety.
        cmd = ["pyrefly", "check", str(train_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Pyrefly output contains "0 errors" when successful.
        return "0 errors" in result.stdout or "0 errors" in result.stderr
    except Exception:
        return False


def _score_candidate(train_path: Path) -> float:
    # Karpathy Mandate: Reproducible, verifiable goals.
    # Enforce type safety before even running the logic.
    if not _check_types(train_path):
        return FAIL_SCORE

    predict_label = _load_candidate(train_path)
    total = len(EVAL_CASES)
    correct = 0

    for text, expected in EVAL_CASES:
        predicted = str(predict_label(text)).strip().lower()
        if predicted == expected:
            correct += 1

    return correct / total if total else FAIL_SCORE


def _evaluate_once(train_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        score = _score_candidate(train_path)
        return {
            "ok": True,
            "score": float(score),
            "runtime_ms": int((time.perf_counter() - started) * 1000),
            "error": None,
        }
    except Exception as exc:  # pragma: no cover
        return {
            "ok": False,
            "score": FAIL_SCORE,
            "runtime_ms": int((time.perf_counter() - started) * 1000),
            "error": str(exc),
        }


def evaluate_with_timeout(train_path: Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.perf_counter()
    cmd = [sys.executable, str(Path(__file__)), "--worker", "--train-path", str(train_path)]
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "score": FAIL_SCORE,
            "runtime_ms": int((time.perf_counter() - started) * 1000),
            "error": f"Timeout after {timeout_seconds}s",
        }

    stdout = result.stdout.strip()
    if not stdout:
        return {
            "ok": False,
            "score": FAIL_SCORE,
            "runtime_ms": int((time.perf_counter() - started) * 1000),
            "error": f"No result returned by evaluator process (stderr: {result.stderr.strip()})",
        }

    try:
        payload = json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "score": FAIL_SCORE,
            "runtime_ms": int((time.perf_counter() - started) * 1000),
            "error": f"Invalid worker JSON: {exc}",
        }

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Locked evaluator")
    parser.add_argument(
        "--train-path",
        default=str(Path(__file__).with_name("train.py")),
        help="Path to candidate train.py",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Hard timeout applied equally to each run",
    )
    parser.add_argument(
        "--worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.worker:
        result = _evaluate_once(Path(args.train_path))
        print(json.dumps(result))
        return 0 if result["ok"] else 1

    result = evaluate_with_timeout(Path(args.train_path), int(args.timeout_seconds))

    if args.json:
        print(json.dumps(result))
    else:
        print(f"ok={result['ok']} score={result['score']:.6f} runtime_ms={result['runtime_ms']}")
        if result["error"]:
            print(f"error={result['error']}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
