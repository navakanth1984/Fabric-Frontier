"""
Telugu/Hindi Lip Reanimation Pipeline
BIT Stage 1: Build — single-scene atomic pipeline
Applies Karpathy principle: minimal scope, explicit assumptions, clear success metric.

ASSUMPTIONS (verify before running):
  - .env has ELEVENLABS_API_KEY and SYNC_SO_API_KEY
  - Input videos are MP4, 720p+, 10-15s (Seedance output)
  - ElevenLabs voice_id is for a Telugu/Hindi voice
  - Sync.so is the default backend (no GPU needed)
  - For LatentSync local: set USE_LOCAL=true in .env, needs 6.8GB VRAM

SUCCESS METRIC: SyncNet confidence score >= 0.85 (see eval_sync.py)
"""

import os, time, json
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(r"C:\Users\navka\navakanth001\capcut_pipeline\.env")

ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
SYNC_SO_KEY    = os.getenv("SYNC_SO_API_KEY")
USE_LOCAL      = os.getenv("USE_LOCAL", "false").lower() == "true"

# Telugu voice IDs from ElevenLabs — replace with your selected voice
# Find yours at: https://elevenlabs.io/voice-library (search "Telugu")
# Or use voice clone after recording 30s sample
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")


def generate_telugu_voice(text: str, output_wav: str,
                          voice_id: str = DEFAULT_VOICE_ID) -> str:
    """
    Stage 1: Text → Telugu/Hindi WAV via ElevenLabs.

    Model: eleven_multilingual_v2 (supports Telugu, Hindi, Tamil, Kannada)
    Best practices:
      - Keep text under 80 words for clean prosody
      - Add commas for natural pauses
      - Avoid compound sentences — break into two calls if needed
    """
    if not ELEVENLABS_KEY:
        raise EnvironmentError("ELEVENLABS_API_KEY missing from .env")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/wav",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,        # Lower = more expressive (good for drama)
            "similarity_boost": 0.80, # Higher = voice stays on-character
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }

    print(f"  Generating voice for: '{text[:50]}...'")
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()

    Path(output_wav).parent.mkdir(parents=True, exist_ok=True)
    with open(output_wav, "wb") as f:
        f.write(resp.content)
    print(f"  Voice saved → {output_wav}")
    return output_wav


def reanimate_lips_syncso(video_mp4: str, audio_wav: str,
                           output_mp4: str) -> str:
    """
    Stage 2A: Video + Telugu audio → reanimated video (Sync.so cloud).

    No GPU needed. Works on any machine.
    Cost: ~$0.05-0.15 per 10s clip depending on plan.
    Model: lipsync-2-pro (diffusion-based, preserves identity better than 1.x)

    What it does internally:
      - Detects face region frame-by-frame
      - Extracts phoneme sequence from Telugu audio
      - Maps Telugu phonemes → mouth shapes (visemes)
      - Renders new mouth region using diffusion super-resolution
      - Composites back onto original video
    """
    if not SYNC_SO_KEY:
        raise EnvironmentError("SYNC_SO_API_KEY missing from .env")

    base_url = "https://api.sync.so/v2/generate"
    headers = {"x-api-key": SYNC_SO_KEY}

    print(f"  Uploading to Sync.so...")
    with open(video_mp4, "rb") as vf, open(audio_wav, "rb") as af:
        resp = requests.post(
            base_url,
            headers=headers,
            files={
                "video": (Path(video_mp4).name, vf, "video/mp4"),
                "audio": (Path(audio_wav).name, af, "audio/wav"),
            },
            data={"model": "lipsync-2-pro", "sync_mode": "bounce"},
            timeout=120,
        )
    resp.raise_for_status()
    job = resp.json()
    job_id = job["id"]
    print(f"  Job created: {job_id}")

    # Poll — Sync.so takes ~30-90s per 15s clip
    for attempt in range(72):  # 6-minute max timeout
        time.sleep(5)
        poll = requests.get(f"{base_url}/{job_id}", headers=headers, timeout=30)
        data = poll.json()
        status = data.get("status")

        if attempt % 6 == 0:
            print(f"  [{attempt*5}s] Status: {status}")

        if status == "completed":
            out_url = data["output_url"]
            print(f"  Downloading result...")
            result = requests.get(out_url, timeout=120)
            Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
            with open(output_mp4, "wb") as f:
                f.write(result.content)
            print(f"  Reanimated → {output_mp4}")
            return output_mp4

        if status in ("failed", "error"):
            raise RuntimeError(f"Sync.so failed: {json.dumps(data, indent=2)}")

    raise TimeoutError(f"Sync.so job {job_id} timed out after 6 minutes")


def reanimate_lips_latentsync(video_mp4: str, audio_wav: str,
                               output_mp4: str,
                               latentsync_dir: str = "./LatentSync") -> str:
    """
    Stage 2B: Video + Telugu audio → reanimated video (LatentSync local).

    Requires: CUDA GPU with 6.8GB+ VRAM, LatentSync installed (see SETUP.md)
    Free to run. Multilingual — works on Telugu phonemes natively.
    Quality on par with Sync.so for standard clips.

    SETUP (WSL, one-time):
      git clone https://github.com/bytedance/LatentSync
      cd LatentSync && pip install -r requirements.txt --break-system-packages
      # Download checkpoints (see LatentSync README)
    """
    import subprocess
    cmd = [
        "python", "inference.py",
        "--video_path", os.path.abspath(video_mp4),
        "--audio_path", os.path.abspath(audio_wav),
        "--video_out_path", os.path.abspath(output_mp4),
        "--inference_steps", "20",   # 20 = good quality/speed balance
        "--guidance_scale", "1.5",
    ]
    print(f"  Running LatentSync locally (GPU)...")
    result = subprocess.run(cmd, cwd=latentsync_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"LatentSync failed:\n{result.stderr}")
    print(f"  Reanimated → {output_mp4}")
    return output_mp4


def process_scene(scene_id: str, dialogue_text: str,
                  source_video: str, output_dir: str = "./output",
                  voice_id: str = DEFAULT_VOICE_ID) -> dict:
    """
    Full pipeline for one scene: script → voice → reanimate.

    Args:
        scene_id:      Unique ID e.g. "DL_S01" (Dead Loop Scene 01)
        dialogue_text: Telugu/Hindi text for this scene
        source_video:  Path to Seedance-generated video (face must be visible)
        output_dir:    Where to write outputs (CapCut imports from here)
        voice_id:      ElevenLabs voice ID for the character

    Returns:
        dict with paths and metadata for downstream assembly
    """
    scene_dir = Path(output_dir) / scene_id
    scene_dir.mkdir(parents=True, exist_ok=True)

    audio_path  = str(scene_dir / "dialogue.wav")
    output_path = str(scene_dir / "lipsync.mp4")
    meta_path   = str(scene_dir / "meta.json")

    print(f"\n[{scene_id}] Starting pipeline")
    print(f"  Text: {dialogue_text[:60]}{'...' if len(dialogue_text) > 60 else ''}")
    t0 = time.time()

    # Stage 1: Voice generation
    generate_telugu_voice(dialogue_text, audio_path, voice_id)

    # Stage 2: Lip reanimation
    if USE_LOCAL:
        reanimate_lips_latentsync(source_video, audio_path, output_path)
    else:
        reanimate_lips_syncso(source_video, audio_path, output_path)

    elapsed = round(time.time() - t0, 1)
    meta = {
        "scene_id": scene_id,
        "text": dialogue_text,
        "source_video": source_video,
        "output_video": output_path,
        "audio": audio_path,
        "backend": "latentsync_local" if USE_LOCAL else "syncso_cloud",
        "elapsed_seconds": elapsed,
        "ready_for_capcut": True,
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[{scene_id}] Done in {elapsed}s → {output_path}")
    return meta


def process_batch(scenes: list[dict], output_dir: str = "./output") -> list[dict]:
    """
    BIT Integrate: Process multiple scenes, collect results.
    Failures are isolated — one bad clip doesn't kill the batch.

    scenes format:
        [{"scene_id": "DL_S01", "text": "VEDA...", "video": "scene01.mp4",
          "voice_id": "xxx"}, ...]
    """
    results = []
    failed  = []

    for scene in scenes:
        try:
            result = process_scene(
                scene_id      = scene["scene_id"],
                dialogue_text = scene["text"],
                source_video  = scene["video"],
                output_dir    = output_dir,
                voice_id      = scene.get("voice_id", DEFAULT_VOICE_ID),
            )
            results.append(result)
        except Exception as e:
            print(f"[{scene['scene_id']}] FAILED: {e}")
            failed.append({"scene_id": scene["scene_id"], "error": str(e)})

    # Summary
    print(f"\nBatch complete: {len(results)} succeeded, {len(failed)} failed")
    if failed:
        print("Failed scenes:", [f["scene_id"] for f in failed])

    summary_path = Path(output_dir) / "batch_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"succeeded": results, "failed": failed}, f,
                  ensure_ascii=False, indent=2)

    return results


# ─── Example usage ────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Dead Loop — Conversation Trailer scenes
    # Replace video paths with actual Seedance output files
    DEAD_LOOP_SCENES = [
        {
            "scene_id": "DL_S01",
            "text": "VEDA, Sector 7 data చూపించు. ఇప్పుడే.",
            # Translation: "VEDA, show me the Sector 7 data. Right now."
            "video": "./seedance_clips/arjun_terminal_01.mp4",
            "voice_id": DEFAULT_VOICE_ID,  # Replace with Arjun's cloned voice
        },
        {
            "scene_id": "DL_S02",
            "text": "నేను ఆగను. నువ్వు నన్ను ఆపలేవు.",
            # Translation: "I won't stop. You can't stop me."
            "video": "./seedance_clips/arjun_confrontation_02.mp4",
            "voice_id": DEFAULT_VOICE_ID,
        },
    ]

    process_batch(DEAD_LOOP_SCENES, output_dir="./output/dead_loop_trailer")
