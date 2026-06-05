"""
Model Comparison Script
Generates one image from each available model using the same prompt.
Compare results visually to pick the best model for your pipeline.

USAGE:
    py compare_models.py
"""

import os, base64, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

OUTPUT_DIR = "model_comparison"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test prompt — same for all models
TEST_PROMPT = "soft pastel gradient studio background, warm peach to lavender, bokeh depth of field, clean minimal YouTube aesthetic, professional lighting, 8k"

MODELS = [
    # Gemini Imagen models
    {"name": "gemini_imagen4_standard", "api": "gemini", "model": "imagen-4.0-generate-001"},
    {"name": "gemini_imagen4_fast",     "api": "gemini", "model": "imagen-4.0-fast-generate-001"},
    {"name": "gemini_imagen4_ultra",    "api": "gemini", "model": "imagen-4.0-ultra-generate-001"},
    # OpenAI models
    {"name": "openai_gpt_image_1",      "api": "openai", "model": "gpt-image-1"},
    {"name": "openai_dalle3",           "api": "openai", "model": "dall-e-3"},
    {"name": "openai_gpt_image_2",      "api": "openai", "model": "gpt-image-2"},
]

def test_gemini(model_id):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict?key={GEMINI_KEY}"
    r = requests.post(url, json={
        "instances":  [{"prompt": TEST_PROMPT}],
        "parameters": {"sampleCount": 1, "aspectRatio": "16:9"},
    }, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    return r.json()["predictions"][0]["bytesBase64Encoded"]

def test_openai(model_id):
    payload = {"model": model_id, "prompt": TEST_PROMPT, "n": 1, "size": "1024x1024"}
    # dall-e-3 needs response_format
    if model_id == "dall-e-3":
        payload["response_format"] = "b64_json"
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        json=payload, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"{r.status_code}: {r.text[:200]}")
    item = r.json()["data"][0]
    if "b64_json" in item:
        return item["b64_json"]
    return base64.b64encode(requests.get(item["url"]).content).decode()

def save(b64, name):
    ts   = datetime.now().strftime("%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"{name}_{ts}.png")
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    size_kb = os.path.getsize(path) // 1024
    return path, size_kb

print(f"\n  Model Comparison Test")
print(f"  Prompt: {TEST_PROMPT[:60]}...")
print(f"  Output: ./{OUTPUT_DIR}/\n")
print(f"{'─'*55}")

results = []
for m in MODELS:
    api  = m["api"]
    key  = GEMINI_KEY if api == "gemini" else OPENAI_KEY
    if not key:
        print(f"  SKIP  {m['name']:<30} (no API key)")
        continue

    print(f"  Testing {m['name']:<35}", end=" ", flush=True)
    try:
        b64  = test_gemini(m["model"]) if api == "gemini" else test_openai(m["model"])
        path, kb = save(b64, m["name"])
        print(f"OK  ({kb} KB)")
        results.append({"model": m["name"], "path": path, "kb": kb})
    except RuntimeError as e:
        print(f"FAIL  {e}")

print(f"{'─'*55}")
print(f"\n  Results saved to ./{OUTPUT_DIR}/")
print(f"  Open folder and compare images visually.\n")
print(f"  {'Model':<35} {'Size':>8}")
print(f"  {'─'*43}")
for r in results:
    print(f"  {r['model']:<35} {r['kb']:>6} KB")

print(f"\n  Once you pick the best model, update PRIMARY_API")
print(f"  and GEMINI_MODEL/OPENAI_MODEL in run.py.\n")
