"""
Synthetic Content Detector — Dual Engine + Auto Video Compression
Images  → OpenAI GPT-4o Vision
Videos  → NVIDIA (with GPT-4o frame fallback)

USAGE:
    py detect_synthetic.py model_comparison
    py detect_synthetic.py photo.jpg
    py detect_synthetic.py video.mp4
"""

import os, sys, base64, requests, time, io, json, subprocess, tempfile
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image as PILImage

load_dotenv()
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

IMAGES       = {".png", ".jpg", ".jpeg", ".webp"}
VIDEOS       = {".mp4", ".mov", ".avi", ".mkv"}
ALL_EXT      = IMAGES | VIDEOS
MAX_RETRIES  = 3
RETRY_DELAY  = 5
RESIZE_STEPS = [1024, 768, 512]

NVIDIA_MAX_MB       = 5
NVIDIA_MAX_DURATION = 30
NVIDIA_MAX_WIDTH    = 1280
NVIDIA_MAX_HEIGHT   = 720
NVIDIA_CRF_STEPS    = [28, 32, 36, 40]

# Forced verdict prompt — no waffling allowed
IMAGE_PROMPT = """You are a forensic AI content analyst. You MUST give a definitive verdict.
Analyse this image and respond EXACTLY in this format with no other text before the verdict:

VERDICT: AI-Generated
CONFIDENCE: [0-100]%
INDICATORS:
- [indicator 1]
- [indicator 2]
- [indicator 3]

OR if real:

VERDICT: Real
CONFIDENCE: [0-100]%
INDICATORS:
- [indicator 1]
- [indicator 2]
- [indicator 3]

You MUST choose one. Do not say you cannot determine. Every image has detectable characteristics.
Look for: perfect gradients, uniform bokeh, smooth skin, missing pores, symmetry artifacts,
unnatural lighting, dreamlike backgrounds, or conversely natural imperfections, consistent shadows,
realistic textures. Make a decision and commit to it."""

VIDEO_FRAME_PROMPT = """You are a forensic AI content analyst examining a video frame.
You MUST give a definitive verdict on whether this video is AI-generated or real footage.
Respond EXACTLY in this format:

VERDICT: AI-Generated
CONFIDENCE: [0-100]%
NOTE: Frame-based analysis
INDICATORS:
- [indicator 1]
- [indicator 2]
- [indicator 3]

OR:

VERDICT: Real
CONFIDENCE: [0-100]%
NOTE: Frame-based analysis
INDICATORS:
- [indicator 1]
- [indicator 2]
- [indicator 3]

You MUST choose one. Look for: motion blur artifacts, temporal inconsistencies visible in frame,
AI texture patterns, synthetic lighting, over-smooth surfaces, or natural film grain,
authentic movement blur, real-world imperfections."""


# ── ffmpeg helpers ─────────────────────────────────────────────────────────

def get_video_info(path):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
           "-show_streams", "-show_format", path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                           shell=(os.name == "nt"))
        data   = json.loads(r.stdout)
        fmt    = data.get("format", {})
        vstream = next((s for s in data.get("streams", [])
                        if s.get("codec_type") == "video"), {})
        return {
            "duration": float(fmt.get("duration", 0)),
            "size_mb":  os.path.getsize(path) / (1024*1024),
            "width":    vstream.get("width", 0),
            "height":   vstream.get("height", 0),
            "codec":    vstream.get("codec_name", "unknown"),
        }
    except Exception:
        return {"duration": 0, "size_mb": 0, "width": 0, "height": 0, "codec": "unknown"}


def compress_video(input_path, crf=28):
    out = os.path.join(tempfile.gettempdir(), f"nvidia_tmp_{os.getpid()}_{crf}.mp4")
    info = get_video_info(input_path)
    cmd  = ["ffmpeg", "-y", "-i", input_path]
    if info["duration"] > NVIDIA_MAX_DURATION:
        cmd += ["-t", str(NVIDIA_MAX_DURATION)]
    scale = (f"scale='if(gt(iw,{NVIDIA_MAX_WIDTH}),{NVIDIA_MAX_WIDTH},iw)':"
             f"'if(gt(ih,{NVIDIA_MAX_HEIGHT}),{NVIDIA_MAX_HEIGHT},ih)':"
             f"force_original_aspect_ratio=decrease")
    cmd += ["-vf", scale, "-c:v", "libx264", "-crf", str(crf),
            "-preset", "fast", "-c:a", "aac", "-b:a", "64k",
            "-movflags", "+faststart", out]
    subprocess.run(cmd, capture_output=True, timeout=120, shell=(os.name == "nt"))
    return out


def prepare_video(path):
    info = get_video_info(path)
    print(f"\n    Original: {info['size_mb']:.1f} MB | "
          f"{info['width']}x{info['height']} | "
          f"{info['duration']:.1f}s | codec: {info['codec']}")

    if (info["size_mb"] <= NVIDIA_MAX_MB and
            info["duration"] <= NVIDIA_MAX_DURATION and
            info["codec"] == "h264"):
        print(f"    No compression needed.", end=" ", flush=True)
        return path, False

    print(f"    Compressing for NVIDIA API...", end=" ", flush=True)
    for crf in NVIDIA_CRF_STEPS:
        tmp  = compress_video(path, crf=crf)
        size = os.path.getsize(tmp) / (1024*1024)
        print(f"\n    CRF {crf} → {size:.1f} MB", end=" ", flush=True)
        if size <= NVIDIA_MAX_MB:
            print(f"✓ Fits!", end=" ", flush=True)
            return tmp, True
        os.remove(tmp)
    raise RuntimeError(
        f"Cannot compress below {NVIDIA_MAX_MB} MB — video may be too long.")


def extract_frame(video_path):
    """Extract middle frame from video as JPEG bytes."""
    info  = get_video_info(video_path)
    mid   = min(info["duration"] / 2, 15)
    frame = os.path.join(tempfile.gettempdir(), f"frame_{os.getpid()}.jpg")
    cmd   = ["ffmpeg", "-y", "-ss", str(mid), "-i", video_path,
             "-frames:v", "1", "-q:v", "2", frame]
    subprocess.run(cmd, capture_output=True, timeout=30, shell=(os.name == "nt"))
    return frame if os.path.exists(frame) else None


# ── Image encoding ──────────────────────────────────────────────────────────

def encode_image(path, max_px=1024):
    img = PILImage.open(path).convert("RGB")
    if img.width > max_px or img.height > max_px:
        img.thumbnail((max_px, max_px), PILImage.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


# ── OpenAI GPT-4o ───────────────────────────────────────────────────────────

def call_openai(b64, prompt):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                json={
                    "model": "gpt-4o",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url",
                             "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                            {"type": "text", "text": prompt}
                        ]
                    }],
                    "max_tokens": 600,
                },
                timeout=60,
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 20))
                print(f"\n    [RATE LIMIT] Waiting {wait}s...", end=" ", flush=True)
                time.sleep(wait); continue
            raise RuntimeError(f"OpenAI {r.status_code}: {r.text[:200]}")
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                print(f"\n    [TIMEOUT] Retry {attempt}...", end=" ", flush=True)
                time.sleep(RETRY_DELAY); continue
            raise RuntimeError("Timed out")
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                print(f"\n    [CONN ERR] Retry {attempt}...", end=" ", flush=True)
                time.sleep(RETRY_DELAY); continue
            raise RuntimeError("Connection failed")
    raise RuntimeError("All attempts failed")


def analyse_image_openai(path):
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY not in .env")
    size = RESIZE_STEPS[0]
    b64  = encode_image(path, max_px=size)
    return call_openai(b64, IMAGE_PROMPT)


# ── NVIDIA video ────────────────────────────────────────────────────────────

def analyse_video_nvidia(path):
    if not NVIDIA_KEY:
        raise RuntimeError("NVIDIA_API_KEY not in .env")

    video_path, is_temp = prepare_video(path)
    try:
        ext  = os.path.splitext(video_path)[1].lower()[1:]
        size = os.path.getsize(video_path) / (1024*1024)
        print(f"\n    Sending {size:.1f} MB to NVIDIA...", end=" ", flush=True)
        with open(video_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = requests.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {NVIDIA_KEY}",
                             "Content-Type": "application/json"},
                    json={
                        "model": "nvidia/ai-synthetic-video-detector",
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "video_url",
                                 "video_url": {"url": f"data:video/{ext};base64,{b64}"}},
                                {"type": "text", "text":
                                    "Is this video AI-generated or synthetic? "
                                    "Provide VERDICT, CONFIDENCE, and INDICATORS."}
                            ]
                        }],
                        "max_tokens": 512,
                    },
                    timeout=120,
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                if r.status_code == 429:
                    wait = int(r.headers.get("Retry-After", 30))
                    time.sleep(wait); continue
                if r.status_code == 500:
                    if attempt < MAX_RETRIES:
                        print(f"\n    [RETRY {attempt}] Server error...",
                              end=" ", flush=True)
                        time.sleep(RETRY_DELAY); continue
                    # Exhausted retries — signal fallback needed
                    raise RuntimeError("NVIDIA_NEEDS_FALLBACK")
                raise RuntimeError(f"NVIDIA {r.status_code}: {r.text[:200]}")

            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES:
                    print(f"\n    [TIMEOUT] Retry {attempt}...", end=" ", flush=True)
                    time.sleep(RETRY_DELAY); continue
                raise RuntimeError("NVIDIA_NEEDS_FALLBACK")
            except requests.exceptions.ConnectionError:
                if attempt < MAX_RETRIES:
                    print(f"\n    [CONN ERR] Retry {attempt}...", end=" ", flush=True)
                    time.sleep(RETRY_DELAY); continue
                raise RuntimeError("NVIDIA_NEEDS_FALLBACK")

        raise RuntimeError("NVIDIA_NEEDS_FALLBACK")

    finally:
        if is_temp and os.path.exists(video_path):
            os.remove(video_path)


def analyse_video_frame_fallback(path):
    """Extract a frame and analyse with GPT-4o."""
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY not in .env for fallback")
    print(f"\n    [FALLBACK] NVIDIA unavailable → extracting frame for GPT-4o...",
          end=" ", flush=True)
    frame = extract_frame(path)
    if not frame:
        raise RuntimeError("Could not extract frame from video")
    try:
        b64 = encode_image(frame, max_px=1024)
        return call_openai(b64, VIDEO_FRAME_PROMPT)
    finally:
        if os.path.exists(frame):
            os.remove(frame)


# ── Router ──────────────────────────────────────────────────────────────────

def detect(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGES:
        if not OPENAI_KEY:
            raise RuntimeError("OPENAI_API_KEY not in .env")
        return analyse_image_openai(path), "GPT-4o"

    elif ext in VIDEOS:
        try:
            result = analyse_video_nvidia(path)
            return result, "NVIDIA"
        except RuntimeError as e:
            if "NVIDIA_NEEDS_FALLBACK" in str(e):
                result = analyse_video_frame_fallback(path)
                return result, "GPT-4o[frame]"
            raise

    raise ValueError(f"Unsupported: {ext}")


# ── Verdict parser ──────────────────────────────────────────────────────────

def parse_verdict(text):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("VERDICT"):
            val = stripped.split(":", 1)[-1].strip().lower()
            if any(x in val for x in ["ai", "synthetic", "generated", "artificial"]):
                return "AI"
            if any(x in val for x in ["real", "authentic", "genuine", "photograph"]):
                return "REAL"
    return "?"


# ── Single file ─────────────────────────────────────────────────────────────

def run_single(path, index=None, total=None):
    fname   = os.path.basename(path)
    size_kb = os.path.getsize(path) // 1024
    ext     = os.path.splitext(path)[1].lower()
    engine  = "GPT-4o" if ext in IMAGES else "NVIDIA"
    prefix  = f"  [{index}/{total}]" if index else "  "

    print(f"\n{prefix} {fname}  ({size_kb} KB)  [{engine}]")
    print(f"    Analysing...", end=" ", flush=True)

    try:
        result, engine_used = detect(path)
        verdict = parse_verdict(result)
        print(f"✓  [{engine_used}]")
        print(f"\n    {result}\n")
        return {"file": fname, "result": result, "verdict": verdict,
                "engine": engine_used, "error": None}

    except (RuntimeError, ValueError) as e:
        print(f"✗")
        print(f"    [SKIPPED] {e}\n")
        return {"file": fname, "result": None, "verdict": "ERR",
                "engine": engine, "error": str(e)}

    except Exception as e:
        print(f"✗")
        print(f"    [UNEXPECTED] {type(e).__name__}: {e}\n")
        return {"file": fname, "result": None, "verdict": "ERR",
                "engine": engine, "error": str(e)}


# ── Folder ──────────────────────────────────────────────────────────────────

def run_folder(folder_path):
    files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in ALL_EXT
    ])
    if not files:
        print(f"\n  No supported files in: {folder_path}\n"); sys.exit(1)

    img_c = sum(1 for f in files if os.path.splitext(f)[1].lower() in IMAGES)
    vid_c = sum(1 for f in files if os.path.splitext(f)[1].lower() in VIDEOS)

    print(f"\n  {'='*57}")
    print(f"  Synthetic Content Detector — Dual Engine")
    print(f"  Folder  : {folder_path}")
    print(f"  Images  : {img_c}  (GPT-4o forced verdict)")
    print(f"  Videos  : {vid_c}  (NVIDIA → GPT-4o frame fallback)")
    print(f"  Started : {datetime.now().strftime('%H:%M:%S')}")
    print(f"  {'='*57}")

    results = []
    try:
        for i, path in enumerate(files, 1):
            results.append(run_single(path, index=i, total=len(files)))
    except KeyboardInterrupt:
        print(f"\n\n  [STOPPED] Saving partial results...\n")
    finally:
        if results:
            save_log(results, folder_path)
            print_summary(results)


# ── Summary ─────────────────────────────────────────────────────────────────

def print_summary(results):
    ai   = sum(1 for r in results if r["verdict"] == "AI")
    real = sum(1 for r in results if r["verdict"] == "REAL")
    unk  = sum(1 for r in results if r["verdict"] == "?")
    err  = sum(1 for r in results if r["verdict"] == "ERR")

    print(f"  {'='*57}")
    print(f"  FINAL SUMMARY")
    print(f"  {'─'*57}")
    print(f"  {'File':<36} {'Engine':<14} {'Verdict':>7}")
    print(f"  {'─'*57}")
    for r in results:
        icon = ("🤖 AI"   if r["verdict"] == "AI"   else
                "📷 REAL" if r["verdict"] == "REAL" else
                "? UNK"   if r["verdict"] == "?"    else "✗ ERR")
        print(f"  {r['file'][:36]:<36} {r['engine']:<14} {icon:>7}")
    print(f"  {'─'*57}")
    print(f"  AI:{ai}  Real:{real}  Unknown:{unk}  Errors:{err}")
    print(f"  {'='*57}\n")


def save_log(results, folder_path):
    log = os.path.join(folder_path, "_detection_log.txt")
    with open(log, "w", encoding="utf-8") as f:
        f.write(f"Synthetic Content Detection\n")
        f.write(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*57}\n\n")
        for r in results:
            f.write(f"FILE    : {r['file']}\n")
            f.write(f"ENGINE  : {r['engine']}\n")
            f.write(f"VERDICT : {r['verdict']}\n")
            f.write(f"DETAIL  :\n{r['result'] or r['error']}\n")
            f.write(f"{'─'*57}\n\n")
    print(f"  Log → {log}\n")


# ── Entry ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n  USAGE:")
        print("    py detect_synthetic.py model_comparison")
        print("    py detect_synthetic.py photo.jpg")
        print("    py detect_synthetic.py clip.mp4\n")
        sys.exit(1)

    target = sys.argv[1]
    if not os.path.exists(target):
        print(f"\n  [ERROR] Not found: {target}\n"); sys.exit(1)

    if os.path.isdir(target):
        run_folder(target)
    else:
        ext = os.path.splitext(target)[1].lower()
        if ext not in ALL_EXT:
            print(f"\n  [ERROR] Unsupported: {ext}\n"); sys.exit(1)
        run_single(target)
