"""
PROMPT LIBRARY — Edit this file to control what gets generated.

Each category maps to a folder in capcut_assets/.
Add, remove, or edit prompts freely.
Negative prompts apply to every image in that category.
"""

STUDIO_BACKGROUNDS = {
    "dimensions": (1024, 576),   # 16:9 horizontal
    "variations": 2,             # images generated per prompt
    "negative": "text, watermark, people, faces, logo, harsh shadows, noise, ugly",
    "prompts": [
        "soft pastel gradient studio background, warm peach to lavender, bokeh, clean minimal YouTube aesthetic, professional photography lighting, 8k",
        "dark cinematic studio background, deep navy blue with subtle teal accent light, dramatic side lighting, premium content creator setup, 8k",
        "bright airy studio background, pure white walls, natural window light, soft shadows, clean modern minimal, lifestyle photography, 8k",
        "warm terracotta studio background, earthy tones, subtle texture, golden hour warm light, cozy professional feel, 8k",
    ],
}

THUMBNAILS = {
    "dimensions": (1024, 576),   # 16:9
    "variations": 2,
    "negative": "blurry, low quality, text, watermark, ugly, deformed",
    "prompts": [
        "bold dynamic thumbnail background, dramatic split lighting, electric blue and orange gradient, high contrast, YouTube clickbait energy, cinematic, 8k",
        "clean professional thumbnail background, soft gradient from white to light grey, subtle vignette, premium minimal, modern business feel, 8k",
        "vibrant tech thumbnail, glowing neon accents on dark background, futuristic grid lines, deep purple and cyan, cyberpunk aesthetic, 8k",
        "warm motivational thumbnail background, golden sunrise gradient, lens flare, epic cinematic feel, aspirational mood, 8k",
    ],
}

LOWER_THIRDS = {
    "dimensions": (1024, 576),
    "variations": 2,
    # NOTE: background is auto-removed by rembg after generation
    # Prompt for the graphic element only — simple shapes work best
    "negative": "text, letters, words, numbers, watermark, people, faces, complex background",
    "prompts": [
        "minimalist lower third graphic element, sleek horizontal bar, frosted glass morphism, white glow edges, isolated on solid black background",
        "modern lower third accent shape, thin elegant line with geometric diamond, silver metallic finish, isolated on solid black background",
        "bold lower third badge shape, rounded rectangle, gradient blue to purple, glowing border, isolated on solid black background",
        "clean lower third tab element, flat design, soft pastel peach tone, subtle drop shadow, isolated on solid black background",
    ],
}

SHORTS_VERTICALS = {
    "dimensions": (576, 1024),   # 9:16 vertical
    "variations": 2,
    "negative": "text, watermark, people, faces, logo, ugly, low quality",
    "prompts": [
        "vertical short-form video background, vibrant gradient purple to pink, dynamic energy, mobile first design, 9:16 aspect ratio, 8k",
        "vertical Reels background, minimalist white gradient, clean lifestyle aesthetic, bright airy mood, 9:16, 8k",
        "vertical TikTok style background, dark moody cinematic, neon accent lighting, deep blacks, 9:16, 8k",
        "vertical content background, warm terracotta to cream gradient, earthy organic feel, soft texture, 9:16, 8k",
    ],
}

# Master registry — pipeline reads this automatically
ALL_CATEGORIES = {
    "studio_backgrounds": STUDIO_BACKGROUNDS,
    "thumbnails":         THUMBNAILS,
    "lower_thirds":       LOWER_THIRDS,
    "shorts_verticals":   SHORTS_VERTICALS,
}
