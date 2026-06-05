# Telugu/Hindi Lip Reanimation Pipeline — Setup Guide

## What this solves

Seedance generates video with lip shapes calibrated for English phonemes.
If you add Telugu/Hindi audio over the top, lips and audio mismatch.

This pipeline does TRUE REANIMATION:
  - Audio drives new lip shapes matching Telugu phonemes
  - Composites back onto original video
  - Character identity preserved (face doesn't drift)

## Requirements

```
pip install requests python-dotenv --break-system-packages
```

For ffprobe-based eval (recommended):
```
# WSL/Ubuntu
sudo apt install ffmpeg
```

## .env additions required

Add to C:\Users\navka\navakanth001\capcut_pipeline\.env:

```
ELEVENLABS_API_KEY=your_key_here
SYNC_SO_API_KEY=your_key_here          # Get at https://sync.so
ELEVENLABS_VOICE_ID=your_voice_id     # From find_telugu_voice.py

# Optional: local GPU mode (skip Sync.so)
USE_LOCAL=false
```

## Two backend options

### Option A — Sync.so (recommended, no GPU needed)
- Sign up at https://sync.so
- Free tier: 10 credits/month (~5 clips)
- Paid: ~$0.05-0.15 per 10s clip
- No GPU required — works on your MSI laptop without CUDA
- Model: lipsync-2-pro (diffusion-based, best identity preservation)

### Option B — LatentSync local (free, needs CUDA GPU)
- Minimum: 6.8GB VRAM for inference
- Check your MSI GPU VRAM: run `nvidia-smi` in PowerShell
- Setup in WSL:
  ```bash
  git clone https://github.com/bytedance/LatentSync
  cd LatentSync
  pip install -r requirements.txt --break-system-packages
  # Download checkpoints per README
  huggingface-cli download ByteDance/LatentSync-1.6 \
      --local-dir checkpoints
  ```
- Set USE_LOCAL=true in .env to use this backend

## Quick start

```powershell
# Step 1: Find the right Telugu voice
py find_telugu_voice.py arjun_deadloop Telugu
# → Listen to previews, pick voice ID, add to .env

# Step 2: Run single scene test
py -c "
from pipeline import process_scene
process_scene(
    scene_id='TEST_01',
    dialogue_text='VEDA, నా మాటలు వినలేవా?',
    source_video='./seedance_clips/test.mp4',
    output_dir='./output'
)
"

# Step 3: Eval the result
py eval_sync.py

# Step 4: Run full Dead Loop trailer batch
py pipeline.py
```

## Pipeline flow

```
Telugu script text
      ↓
ElevenLabs multilingual TTS
  (eleven_multilingual_v2 model)
      ↓
Telugu WAV file
      ↓
Sync.so OR LatentSync
  INPUT:  original Seedance MP4 + Telugu WAV
  PROCESS: detect face → extract phonemes → map to visemes
           → render new mouth region → composite
  OUTPUT: MP4 with Telugu lip movements
      ↓
CapCut import + SFX + score = finished scene
```

## Success metric

SyncNet confidence score ≥ 0.85
Run: py eval_sync.py

If a clip scores below 0.85:
1. Check source video: face must be clearly visible, frontal preferred
2. Shorten dialogue: max 10 words per line gives best lip accuracy
3. Try Sync.so if using LatentSync (or vice versa)
4. Re-record ElevenLabs with slower delivery: add pauses in script

## Phoneme tip for Telugu

Telugu phonemes differ from English. For best results:
- Keep sentences short (5-10 Telugu words)
- Avoid words with heavy retroflex consonants (ట, డ, ణ) mid-sentence
  → break into two shorter lines instead
- Record at 80% of normal speaking speed in ElevenLabs
  (add pauses: "VEDA,... నా మాటలు వినలేవా?")
