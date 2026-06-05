# AutoResearch Contract: Dead Loop Trailer - Shot 25

## Context
**Scene/Shot:** Shot 25 - "ECU of Arjun's eyes. No more fear."
**Controlling Idea:** "Justice triumphs because the protagonist is willing to sacrifice more than the antagonist."
**Visual Motif:** The analog warmth (amber) fully overtakes the digital coldness (cyan).

## Goals
Optimize the DALL-E 3 prompt in `train.py` to generate the perfect, photorealistic frame for Shot 25.

## Constraints & Rules (The BIT Framework)
1. **Level 3 Performance Physics ONLY:** You must NOT use emotion labels in the prompt (e.g., "fearless", "confident", "brave", "no fear"). You must describe the physical state of the eye (e.g., "unblinking", "steady pupil", "focused").
2. **Lighting/Color:** The reflection in the eye must clearly show warm amber/orange light, signaling the shift in power.
3. **Camera Aware:** Must specify an Extreme Close Up (ECU) macro shot.

## Success Metric (`prepare.py`)
The locked oracle (`prepare.py`) will score your `train.py` prompt based on:
- **Rule Adherence:** Penetrating the prompt string to penalize any "Level 1" emotion words.
- **Format:** The prompt must include "macro", "amber", and physical eye descriptions.
Maximum score is 1.0. Your goal is to get a perfect 1.0.
