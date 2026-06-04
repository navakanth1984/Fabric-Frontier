# 🧬 Meshy AI 3D Asset Generation Prompts

> **High-fidelity prompts and generation settings optimized for Nth Dimension Academy (NDA) 3D assets.**
> These prompts are tailored for Meshy AI (Text-to-3D / Image-to-3D) to produce web-friendly low-poly models (optimized for Spline AI, Dora AI, and Three.js loading).

---

## ⚙️ Universal Meshy AI Settings

To ensure the generated models load instantly in the browser and animate smoothly:
*   **Target Polycount:** **8,000 to 12,000 polygons** (Medium details, optimal balance between quality and file size).
*   **Topology:** **Triangles/Quads** (Clean layout for R3F canvas rendering).
*   **Texturing:** **PBR Metallic/Roughness** (Realistic reflections for glassmorphism and holographic sweeps).
*   **Export Format:** **GLB (glTF Binary)** (Self-contained format carrying mesh, materials, textures, and skeletal animations).

---

## 🪐 Course Assets Prompt Sets

### 1. Microsoft Fabric "Data Cube" (DP-700 Core)
*   **Concept:** A futuristic modular cube featuring multiple floating layers, glowing data grids, and digital connections.
*   **Meshy Text Prompt:** 
    > `Futuristic glowing data cube, modular tech design, multi-layered floating panels, holographic cyber grids, sci-fi server architecture, Microsoft Fabric colors cyan blue and gold, highly detailed micro-circuits, semi-transparent glass, glowing emissive lines, octane render style, clean geometry, 8k textures --no organic shapes`
*   **Spline/Three.js Interaction:** Continuous y-axis rotation loop; glowing core pulsing scale scroll-reactively.

### 2. Analytics Prism / Diamond (DP-600 Core)
*   **Concept:** A sharp crystalline prism with refraction properties representing clear analytics pipelines and dashboards.
*   **Meshy Text Prompt:**
    > `Sci-fi hexagonal glass prism, refracting crystalline geometry, neon purple and fuchsia core, glowing holographic details inside, pristine crystal sculpture, high-tech energy battery, sleek diagonal circuit engravings, raytraced glass material, emissive fuchsia glow, premium dark tech look --no dirt or scratches`
*   **Spline/Three.js Interaction:** Floating idle animation; tilts on cursor mouse-move hover.

### 3. Core Azure Shield / Node (DP-203 Core)
*   **Concept:** A metallic cloud sphere wrapped in protective orbital shield rings representing secure data engineering pipelines.
*   **Meshy Text Prompt:**
    > `Futuristic mechanical orb, detailed metallic plating, glowing circuit board engravings, orbiting neon-blue rings, cloud computing hardware node, dark gunmetal and bright cyan color scheme, industrial sci-fi device, emissive cyan energy channels, hard surface modeling --no rust --no dirt`
*   **Spline/Three.js Interaction:** Outer rings rotate on the Z-axis, inner sphere spins slowly on the Y-axis.

### 4. Database Fundamentals Sphere (DP-900 Core)
*   **Concept:** A simple, clean glowing energy sphere representing foundational database structures (relational and non-relational).
*   **Meshy Text Prompt:**
    > `Holographic wireframe energy sphere, neon gold grid lines, spinning concentric particle bands, clean simple topology, glowing yellow core, floating data nodes, soft particle glow, simple clean tech aesthetic, sci-fi UI element --no solid metal --no dark background`
*   **Spline/Three.js Interaction:** Standard planar concentric orbit around the main sun core.

---

## 🌀 Hero Section Masterpiece Asset

### 5. Nth Dimension Academy Crystalline Portal (Monolith Replacement)
*   **Concept:** A large interactive stargate/portal structure that replaces the static monolith.
*   **Meshy Text Prompt:**
    > `Sci-fi gateway portal, circular obsidian ring structure, hyper-detailed neon gold and cyan runes, swirling liquid-glass energy event horizon at the center, holographic console blocks floating on the sides, epic cinematic composition, cyberpunk gate, raytraced materials, highly reflective metallic ring --no organic plants --no ancient stone`
*   **Integration Workflow:**
    1.  Export GLB from Meshy AI.
    2.  Import to Spline, place an interactive light source at the center.
    3.  Configure Spline scroll events to zoom the camera *into* the portal as the user scrolls down the page.
    4.  Copy the Spline embed URL and paste it into the **CMS Console Dashboard** to launch.
