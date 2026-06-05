# AutoResearch Contract: Dead Loop Trailer - Shot 22

## Context
**Scene/Shot:** Shot 22 - "Arjun stands up. Determination."
**Controlling Idea:** "Justice triumphs because the protagonist is willing to sacrifice more than the antagonist."
**Visual Motif:** Warm amber (analog warmth) vs Terminal green/cyan (digital coldness).

## Goals
Optimize the BFL Flux 1 prompt in `train.py` to generate the perfect, photorealistic frame for Shot 22 that is ready for Seedance/HyperFrames video ingestion.

## Constraints & Rules (The BIT Framework)
1. **Level 3 Performance Physics ONLY:** You must NOT use emotion labels in the prompt (e.g., "determined", "angry", "sad"). You must use purely physical behavior (e.g., "jaw clenched", "shoulders pulled back", "eyes locked forward").
2. **Lighting:** Must feature a high-contrast clash between cyan/terminal green (from VEDA) and amber (the physical world).
3. **Camera Aware:** Specify the lens length and camera angle (e.g., "Low angle tracking shot, 50mm lens").

## Success Metric (`prepare.py`)
The locked oracle (`prepare.py`) will score your `train.py` prompt based on:
- **Rule Adherence:** Penetrating the prompt string to penalize any "Level 1" emotion words (angry, determined, sad).
- **Format:** The prompt must include the correct aspect ratio and technical camera descriptors.
- **Latency:** Must complete within the mock BFL SLA (< 2.0 seconds).
Maximum score is 1.0. Your goal is to get a perfect 1.0.
