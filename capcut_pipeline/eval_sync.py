"""
BIT Stage 3: Tune — eval loop for lip sync quality
Scalar metric: SyncNet confidence score (0.0 – 1.0)
Target: >= 0.85 for production use

Karpathy principle: "You can't improve what you can't measure."
This script reads pipeline outputs, scores them, and flags failures
for human review before the clip goes to CapCut.

SETUP: pip install syncnet-python --break-system-packages
       OR use LatentSync's built-in SyncNet evaluator
"""

import json, subprocess, os
from pathlib import Path


SCORE_THRESHOLD = 0.85   # Below this → flag for human review or re-run
LATENTSYNC_DIR  = "./LatentSync"


def score_with_latentsync_syncnet(video_path: str) -> float:
    """
    Run SyncNet confidence scoring on a reanimated clip.
    LatentSync ships a SyncNet evaluator — no extra install needed
    if LatentSync is already set up locally.
    Returns confidence score 0.0 – 1.0
    """
    score_output = Path(video_path).with_suffix(".score.json")

    cmd = [
        "python", "evaluation/eval_sync.py",
        "--video", os.path.abspath(video_path),
        "--output_json", str(score_output),
    ]
    result = subprocess.run(cmd, cwd=LATENTSYNC_DIR,
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  SyncNet scoring failed: {result.stderr[:200]}")
        return 0.0

    with open(score_output) as f:
        data = json.load(f)
    return data.get("sync_confidence", 0.0)


def score_simple(video_path: str, audio_path: str) -> dict:
    """
    Simpler quality check when SyncNet isn't available.
    Checks file exists, non-zero size, duration roughly matches audio.
    Returns a dict with pass/fail and reason.
    """
    vp = Path(video_path)
    ap = Path(audio_path)

    if not vp.exists():
        return {"pass": False, "reason": "output video missing"}
    if vp.stat().st_size < 50_000:
        return {"pass": False, "reason": "output video too small (<50KB)"}
    if not ap.exists():
        return {"pass": False, "reason": "audio file missing"}

    # Use ffprobe to check durations match within 1 second
    try:
        vdur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(vp)],
            text=True).strip())
        adur = float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(ap)],
            text=True).strip())
        drift = abs(vdur - adur)
        if drift > 1.0:
            return {"pass": False,
                    "reason": f"audio/video duration drift: {drift:.2f}s"}
        return {"pass": True, "reason": "ok", "video_dur": vdur, "audio_dur": adur}
    except Exception as e:
        return {"pass": False, "reason": f"ffprobe error: {e}"}


def eval_batch(batch_summary_json: str, use_syncnet: bool = False) -> dict:
    """
    Read pipeline batch_summary.json, score each clip, flag failures.

    Args:
        batch_summary_json: Path to batch_summary.json from pipeline.py
        use_syncnet: True = use LatentSync SyncNet scoring (needs local GPU)
                     False = use simple file-based checks

    Returns:
        dict with per-scene scores and overall pass/fail
    """
    with open(batch_summary_json, encoding="utf-8") as f:
        summary = json.load(f)

    report = {"passed": [], "review_needed": [], "failed_pipeline": []}

    # Report pipeline failures immediately
    for fail in summary.get("failed", []):
        report["failed_pipeline"].append(fail)

    # Score each successfully generated clip
    for scene in summary.get("succeeded", []):
        scene_id = scene["scene_id"]
        video    = scene["output_video"]
        audio    = scene["audio"]

        print(f"\nScoring [{scene_id}]...")

        if use_syncnet:
            score = score_with_latentsync_syncnet(video)
            passed = score >= SCORE_THRESHOLD
            result = {
                "scene_id": scene_id,
                "syncnet_confidence": round(score, 3),
                "threshold": SCORE_THRESHOLD,
                "passed": passed,
                "video": video,
            }
            if passed:
                print(f"  PASS — SyncNet: {score:.3f}")
                report["passed"].append(result)
            else:
                print(f"  REVIEW — SyncNet: {score:.3f} < {SCORE_THRESHOLD}")
                report["review_needed"].append(result)
        else:
            check = score_simple(video, audio)
            result = {"scene_id": scene_id, **check, "video": video}
            if check["pass"]:
                print(f"  PASS — {check['reason']}")
                report["passed"].append(result)
            else:
                print(f"  REVIEW — {check['reason']}")
                report["review_needed"].append(result)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Eval summary:")
    print(f"  Passed:          {len(report['passed'])}")
    print(f"  Needs review:    {len(report['review_needed'])}")
    print(f"  Pipeline failed: {len(report['failed_pipeline'])}")

    if report["review_needed"]:
        print("\nScenes needing review (re-run or human check):")
        for s in report["review_needed"]:
            print(f"  {s['scene_id']}: {s.get('syncnet_confidence', s.get('reason'))}")

    # Save eval report next to batch summary
    report_path = Path(batch_summary_json).parent / "eval_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nEval report → {report_path}")

    return report


def suggest_reruns(eval_report: dict, pipeline_scenes: list[dict]) -> list[dict]:
    """
    BIT Tune: Given eval failures, produce a re-run list.
    Agents can call this to automatically retry failed scenes.
    Human oversight: review the re-run list before executing.
    """
    failed_ids = {s["scene_id"] for s in eval_report.get("review_needed", [])}
    reruns = [s for s in pipeline_scenes if s["scene_id"] in failed_ids]
    if reruns:
        print(f"\n{len(reruns)} scenes queued for re-run:")
        for r in reruns:
            print(f"  {r['scene_id']}: {r['text'][:50]}")
    return reruns


if __name__ == "__main__":
    report = eval_batch(
        "./output/dead_loop_trailer/batch_summary.json",
        use_syncnet=False,   # Set True if LatentSync is installed locally
    )
