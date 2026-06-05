"""
find_telugu_voice.py
Discover available Telugu/Hindi voices from ElevenLabs library
and test a sample sentence to compare them.

Run once to find the right voice for Arjun (Dead Loop),
Venkat (DAAVA), or any character.
"""

import os, json
from dotenv import load_dotenv
import requests

load_dotenv(r"C:\Users\navka\navakanth001\capcut_pipeline\.env")
KEY = os.getenv("ELEVENLABS_API_KEY")

# Test sentences for each character
CHARACTER_TESTS = {
    "arjun_deadloop": {
        "telugu": "VEDA, నా మాటలు వినలేవా? Sector 7 data చూపించు.",
        "hindi":  "VEDA, मेरी बात सुनो। Sector 7 का डेटा दिखाओ।",
        "profile": "Mid-30s, taut, controlled anger, Telugu educated professional",
    },
    "veda_deadloop": {
        "telugu": "Arjun, నీకు అర్థమవుతోందా? నేను ఇప్పటికే నిర్ణయం తీసుకున్నాను.",
        "profile": "AI entity: synthetic, slightly too-calm, no emotion — use a male deep voice",
    },
    "narrator_prem": {
        "telugu": "ఆమె చేతులు మాట్లాడతాయి. పదహారేళ్ళ కష్టం, ప్రేమ, నిరాశ.",
        "profile": "Mature female, reflective, soft, Ismail poetry register",
    },
}


def list_voices(language: str = "Telugu") -> list[dict]:
    """List voices from ElevenLabs library filtered by language."""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": KEY}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    all_voices = resp.json().get("voices", [])

    # Filter by language label (ElevenLabs uses labels)
    filtered = [
        v for v in all_voices
        if language.lower() in [l.lower() for l in v.get("labels", {}).values()]
        or language.lower() in v.get("name", "").lower()
    ]
    return filtered


def preview_voice(voice_id: str, text: str, output_path: str) -> None:
    """Generate a short preview clip with a given voice."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    resp = requests.post(url,
        headers={"xi-api-key": KEY, "Accept": "audio/wav"},
        json={"text": text[:100], "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.45, "similarity_boost": 0.8}},
        timeout=60)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"  Preview saved: {output_path}")


def find_best_voice(character_key: str, language: str = "Telugu") -> None:
    """Find and preview voices for a character profile."""
    if character_key not in CHARACTER_TESTS:
        print(f"Unknown character. Choose from: {list(CHARACTER_TESTS.keys())}")
        return

    char = CHARACTER_TESTS[character_key]
    text = char.get(language.lower(), char.get("telugu", ""))
    profile = char["profile"]

    print(f"\nFinding voices for: {character_key}")
    print(f"Profile: {profile}")
    print(f"Test text: {text}\n")

    voices = list_voices(language)
    if not voices:
        print(f"No voices found for language: {language}")
        print("Try searching ElevenLabs voice library manually at:")
        print("  https://elevenlabs.io/voice-library")
        return

    print(f"Found {len(voices)} voices. Generating previews...\n")
    import os; os.makedirs(f"./voice_previews/{character_key}", exist_ok=True)

    for v in voices[:5]:   # Preview top 5 only to save credits
        vid  = v["voice_id"]
        name = v["name"]
        out  = f"./voice_previews/{character_key}/{name}_{vid[:8]}.wav"
        print(f"  [{name}] {vid}")
        try:
            preview_voice(vid, text, out)
        except Exception as e:
            print(f"    Failed: {e}")

    print(f"\nPreviews in ./voice_previews/{character_key}/")
    print("Listen and pick the best one, then set:")
    print(f'  ELEVENLABS_VOICE_ID=<chosen_voice_id>  in your .env')


if __name__ == "__main__":
    import sys
    char = sys.argv[1] if len(sys.argv) > 1 else "arjun_deadloop"
    lang = sys.argv[2] if len(sys.argv) > 2 else "Telugu"
    find_best_voice(char, lang)

    # Usage:
    #   py find_telugu_voice.py arjun_deadloop Telugu
    #   py find_telugu_voice.py narrator_prem Telugu
    #   py find_telugu_voice.py arjun_deadloop Hindi
