"""
API Diagnostic Script
Tests Gemini and OpenAI keys — connectivity, tier, and image generation access.

SETUP:
Add these to your .env file:
    GEMINI_API_KEY=your-gemini-key-here
    OPENAI_API_KEY=your-openai-key-here

RUN:
    py check_apis.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

SEP = "─" * 50

# ── Gemini ────────────────────────────────────────────────────────────────────

def check_gemini():
    print(f"\n{'='*50}")
    print("  GEMINI API CHECK")
    print(f"{'='*50}")

    if not GEMINI_KEY:
        print("  [SKIP] GEMINI_API_KEY not found in .env")
        return

    print(f"  Key found : ...{GEMINI_KEY[-6:]}")

    # 1. List available models
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_KEY}"
        r = requests.get(url, timeout=15)

        if r.status_code == 401:
            print("  [FAIL] Invalid API key")
            return
        elif r.status_code == 403:
            print("  [FAIL] Key exists but access denied — check billing/quota")
            return
        elif r.status_code != 200:
            print(f"  [FAIL] Unexpected error {r.status_code}: {r.text[:200]}")
            return

        print("  [OK]   Connected successfully")

        models = r.json().get("models", [])
        image_models = [
            m for m in models
            if any(x in m.get("name", "").lower()
                   for x in ["imagen", "gemini-2.0", "gemini-exp"])
        ]

        print(f"\n  Total models available : {len(models)}")
        print(f"  Image-capable models   :")

        IMAGE_CAPABLE = [
            "imagen-3.0-generate",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-preview-image-generation",
        ]

        found_any = False
        for m in models:
            name = m.get("name", "")
            short = name.replace("models/", "")
            if any(x in short for x in ["imagen", "image-generation"]):
                print(f"    ✓ {short}")
                found_any = True

        if not found_any:
            print("    ✗ No Imagen models found on this key")
            print("      → Free tier may not include Imagen 3")
            print("      → Gemini 2.0 Flash can still generate images")

    except requests.exceptions.ConnectionError:
        print("  [FAIL] No internet connection")
        return
    except Exception as e:
        print(f"  [FAIL] {e}")
        return

    # 2. Quick image generation test (1 tiny request)
    print(f"\n  Testing image generation...")
    try:
        test_url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-2.0-flash-preview-image-generation:generateContent?key={GEMINI_KEY}"
        )
        payload = {
            "contents": [{"parts": [{"text": "a red circle, minimal"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        r = requests.post(test_url, json=payload, timeout=30)

        if r.status_code == 200:
            print("  [OK]   Image generation WORKS ✓")
            print("         Gemini 2.0 Flash image generation is live on your key")
        elif r.status_code == 429:
            print("  [WARN] Rate limited — key works but quota hit")
            print("         Free tier: 15 requests/minute, 1500/day")
        elif r.status_code == 400:
            data = r.json()
            print(f"  [INFO] {data.get('error', {}).get('message', r.text[:200])}")
        elif r.status_code == 403:
            print("  [FAIL] Image generation not enabled on this key")
            print("         → May need to enable Gemini API in Google Cloud Console")
        else:
            print(f"  [FAIL] {r.status_code}: {r.text[:300]}")

    except Exception as e:
        print(f"  [FAIL] {e}")


# ── OpenAI ────────────────────────────────────────────────────────────────────

def check_openai():
    print(f"\n{'='*50}")
    print("  OPENAI API CHECK")
    print(f"{'='*50}")

    if not OPENAI_KEY:
        print("  [SKIP] OPENAI_API_KEY not found in .env")
        return

    print(f"  Key found : ...{OPENAI_KEY[-6:]}")

    # 1. Connectivity + model list
    try:
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            timeout=15,
        )

        if r.status_code == 401:
            print("  [FAIL] Invalid API key")
            return
        elif r.status_code == 429:
            print("  [WARN] Rate limited — key valid but quota exceeded")
        elif r.status_code != 200:
            print(f"  [FAIL] {r.status_code}: {r.text[:200]}")
            return
        else:
            print("  [OK]   Connected successfully")

        models = r.json().get("data", [])
        image_models = [m for m in models if "dall-e" in m.get("id", "").lower() or "gpt-image" in m.get("id","").lower()]

        print(f"\n  Image models on your key:")
        if image_models:
            for m in image_models:
                print(f"    ✓ {m['id']}")
        else:
            print("    ✗ No DALL-E models found")

    except Exception as e:
        print(f"  [FAIL] {e}")
        return

    # 2. Check billing tier via usage
    try:
        r = requests.get(
            "https://api.openai.com/v1/organization/usage/images",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            timeout=15,
        )
        if r.status_code == 200:
            print("\n  [OK]   Billing access confirmed — paid tier active")
        elif r.status_code == 403:
            print("\n  [INFO] Free tier key — image generation costs ~$0.04/image (DALL-E 3)")
        else:
            print(f"\n  [INFO] Tier check returned {r.status_code}")

    except Exception as e:
        print(f"  [INFO] Could not verify tier: {e}")


# ── Summary ───────────────────────────────────────────────────────────────────

def summary():
    print(f"\n{'='*50}")
    print("  SUMMARY")
    print(f"{'='*50}")
    print("""
  Gemini free tier limits (if key works):
    • 15 requests/minute
    • 1,500 requests/day
    • No credit card needed

  OpenAI free tier:
    • $0 free credits (expired for most accounts)
    • DALL-E 3 = ~$0.04 per image (1024×1024)
    • Paid only for new accounts

  Recommendation for CapCut pipeline:
    → Use Gemini if image generation test passed
    → Use OpenAI only if you have paid credits
""")
    print(f"{'='*50}\n")


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    check_gemini()
    check_openai()
    summary()
