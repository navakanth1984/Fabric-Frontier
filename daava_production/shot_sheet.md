# DEAD LOOP: Cinematic Storyboard Shot Sheet

This **Shot Sheet** serves as the intermediate layer of the **Flow Visual Pipeline (FVP)**. It structures the visual parameters, camera work, durations, and physical simulation cues for all 12 storyboard shots, ensuring a clear technical guide for video generation and NLE editor timeline assembly.

---

## 🎞️ PRODUCTION TIMELINE SHOT SHEET

| Shot ID | Seq | Framing | Target Duration | Camera Lens & Movement | Physics & VFX Simulation Cues | Narrative/Dramatic Objective | Naming Code |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **S01.01** | 1 | Extreme Wide | 5.0 seconds | 18mm Lens; dynamic downward vertical drone dive. | Soft slow-motion rain; amber/cyan puddle reflections; rising mist. | Reveal the suffocating Old City setting. | `DL_SC01_SH01_FLOW` |
| **S01.02** | 1 | Medium Shot | 5.0 seconds | 50mm Lens; steady forward push-in tracking shot. | Slow crowd movements; rain droplets impacting wet duster coat fabric. | Establish Arjun's alert state in the bazaar. | `DL_SC01_SH02_FLOW` |
| **S01.03** | 1 | Close-Up | 5.0 seconds | 35mm Lens; low-angle static camera looking at floor. | Water ripples distorting reflection; glowing cybernetic overlay glitches. | Reveal Arjun's neural cybernetic connection. | `DL_SC01_SH03_FLOW` |
| **S02.01** | 2 | Extreme CU | 5.0 seconds | 50mm Lens; deliberate mechanical slow push-in. | Phosphor amber CRT monitor flicker; vertical data lines scrolling. | Wake up the sleeping obsolete terminal. | `DL_SC02_SH01_FLOW` |
| **S02.02** | 2 | Over-Shoulder | 5.0 seconds | 35mm Lens; slow dolly over-the-shoulder push. | Low-frequency red pulse in neck ports; finger typing; vent steam. | Connect Arjun physically to the terminal. | `DL_SC02_SH02_FLOW` |
| **S02.03** | 2 | Close-Up | 5.0 seconds | 85mm Lens; fast accelerating dolly-in. | Erupting neon-green glare flattens lighting; rapid pupil dilation/blinking. | Capture Arjun's raw panic and data surge. | `DL_SC02_SH03_FLOW` |
| **S03.01** | 3 | Action Wide | 5.0 seconds | 24mm Anamorphic; low tracking, upward drone pan. | Rooftop water splashes; swinging cables in wind; landing whip-pan. | Illustrate the high-stakes escape beat. | `DL_SC03_SH01_FLOW` |
| **S03.02** | 3 | Wide Shot | 5.0 seconds | 28mm Lens; lateral slow camera slide. | Heavy rain falling; concentric ripples propagating across water mirror. | Set a moment of quiet, rain-slicked isolation. | `DL_SC03_SH02_FLOW` |
| **S03.03** | 3 | Medium Shot | 5.0 seconds | 50mm Lens; 45° Dutch angle static medium. | Volumetric searchlights sweep, casting dynamic, sharp metallic shadows. | Trap Arjun in a claustrophobic hiding spot. | `DL_SC03_SH03_FLOW` |
| **S04.01** | 4 | Wide Shot | 7.0 seconds | 21mm Lens; slow dolly pan skimming water surface. | Submerged light panels flickering; mossy cables swaying, dripping water. | Reveal the graveyard scale of the server core. | `DL_SC04_SH01_FLOW` |
| **S04.02** | 4 | Profile CU | 5.0 seconds | 85mm Lens; slow, hypnotic dolly-in to Arjun's eye. | Amber glow wraps around face; scrolling data code inside iris reflection. | Emphasize Arjun's silent awe and realization. | `DL_SC04_SH02_FLOW` |
| **S04.03** | 4 | Widescreen | 3.0 seconds | 24mm Lens; intense rapid whip-dolly zoom. | Prismatic countersensing rings spinning; particles; smash cut to black. | Deliver the climactic title card transition. | `DL_SC04_SH03_FLOW` |

---

## 📦 EDITING & POST-PRODUCTION ASSEMBLY INSTRUCTIONS

### 1. The Multi-Take Selector (Cherry-Picking)
Because Flow Omni computes fluid physics and lighting dynamically:
*   Render exactly **3 takes** per Shot ID.
*   Isolate the exact window of **motion peak** (usually between seconds 1.5 and 4.0 of a 5.0s clip).
*   Discard frames where facial features morph or cybernetic textures stretch unnaturally.

### 2. Splicing Rules
*   **Sequences 1 & 2:** Soft, fluid dissolve transitions matching the steady tempo of the dialogue.
*   **Sequence 3 (The Chase):** Hard, rapid action cuts aligned with the low-frequency drone soundtrack beats.
*   **Sequence 4 (The Revelation):** Match-cut on the amber glow, transitioning instantly from a slow dolly to a violent zoom-out and screen crash.
