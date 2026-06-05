import os
import requests
import json
import base64

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "sk_gv5b8wyc_4OCnebfWVHGJsGMr7Pp7IGr2")
URL = "https://api.sarvam.ai/text-to-speech"

def generate_dialogue(text: str, speaker_name: str, filename: str):
    print(f"Generating audio for {speaker_name}: '{text}'...")
    
    # Map characters to Sarvam speakers
    # Using 'aditya' for male (Arjun) and 'priya' for female (VEDA)
    speaker_id = "aditya" if speaker_name.lower() == "arjun" else "priya"
    
    payload = {
        "inputs": [text],
        "target_language_code": "te-IN",
        "speaker": speaker_id,
        "pace": 1.0 if speaker_id == "aditya" else 0.9, # VEDA speaks slightly slower
        "speech_sample_rate": 8000,
        "enable_preprocessing": True,
        "model": "bulbul:v3"
    }
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request("POST", URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "audios" in data and len(data["audios"]) > 0:
                audio_base64 = data["audios"][0]
                
                # Ensure output directory exists
                os.makedirs("audio_output", exist_ok=True)
                filepath = os.path.join("audio_output", filename)
                
                # Decode and save WAV file
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(audio_base64))
                print(f"[SUCCESS] Saved to {filepath}\n")
                return filepath
            else:
                print(f"[ERROR] Unexpected response format: {data}")
        else:
            print(f"[ERROR] API Request Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception during generation: {e}")
        
    return None

if __name__ == "__main__":
    # The Spine: The Conversation from SCRIPT.md
    # Translated into Telugu with Telangana dialect nuances.
    # Arjun: Scared and angry
    # VEDA: Confused, confident, machine-like
    dialogues = [
        ("arjun", "నెన్ నిన్ను... ఎట్ల నమ్మాలె?!", "01_arjun_trust.wav"),
        ("veda", "నా తప్పులున్నయ్. నేను ఇంకా... నేర్చుకుంటనే ఉన్న.", "02_veda_learning.wav"),
        ("arjun", "ప్రాణాలు పోతుంటే... నువ్వెట్ల నేర్చుకుంటవ్?!", "03_arjun_lives_lost.wav"),
        ("veda", "నేను నిన్ను కాపాడాలనుకుంటున్న. నిన్ను ఖచ్చితంగా... కాపాడుతా.", "04_veda_protect.wav"),
        ("arjun", "నన్నెట్ల కాపాడుతవ్?! ...నిన్ను నువ్వే కాపాడుకోలేనప్పుడు?!", "05_arjun_protect_yourself.wav"),
        ("veda", "నన్ను నేను కాపాడుకోలేకపోవచ్చు... కానీ నిన్ను మాత్రం—", "06_veda_but_i_will.wav"),
        ("veda", "వాడు... వచ్చేసిండు.", "07_veda_he_is_here.wav")
    ]
    
    for speaker, text, filename in dialogues:
        generate_dialogue(text, speaker, filename)
