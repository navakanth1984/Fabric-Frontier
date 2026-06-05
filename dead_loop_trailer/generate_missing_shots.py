import os
import sys
import requests

# Append root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nthdimensionacademy.test_ai import generate_with_openai  # pyrefly: ignore [missing-import]
except ImportError as e:
    print(f"Error importing OpenAI generator: {e}")
    sys.exit(1)

def download_image(url, filename):
    print(f"Downloading {filename}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Saved {filename}")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found in environment.")
        sys.exit(1)

    shots = {
        "01": "Extreme Close Up (ECU) of an Indian man's eye. A glowing cyan digital pulse reflects in his dark pupil. Cinematic, cyberpunk noir.",
        "02": "Wide Shot of HITECCity Hyderabad at night. Rain falling in slow motion. Neon lights reflecting on wet asphalt. Industrial Cyberpunk.",
        "03": "Close up of a dark server rack. Glowing orange status lights blinking in a rhythmic heartbeat pattern. High contrast, moody.",
        "04": "An Indian man standing on a high-tech balcony, looking over a sprawling cyberpunk city in the rain.",
        "05": "A grid of grainy, distorted black and white surveillance footage showing abstract motion. Hacker aesthetic.",
        "06": "A man moving stealthily through a dark, rain-slicked alleyway lit by flickering neon. Shadows obscure his face.",
        "07": "A global team of hackers in a dim underground room. Faces illuminated only by the blue light of multiple monitors.",
        "08": "A massive digital interface glitching across giant holographic billboards in a rainy cyberpunk city. Cybernetic corruption.",
        "09": "Extreme Close Up of a man's hand clenched tightly into a fist in the rain. Drops splashing off his knuckles.",
        "11": "Close up of a motherboard burning out, orange sparks and smoke, high contrast cinematic lighting.",
        "13": "VEDA manifesting as a holographic figure of ethereal blue light in a dark brutalist room. Indian cyberpunk.",
        "17": "The VedaCore room: massive, cold, brutalist architecture, glowing cyan lines on dark concrete.",
        "18": "Extreme Close Up of a single drop of rain hitting a glowing digital circuit board. Macro photography.",
        "21": "An intense cyan light surge, a blinding digital flare in a dark cyberpunk server room.",
        "action": "Intense cyberpunk action scene. A digital explosion of orange code and shards of glass in a neon-lit server room. High speed motion blur."
    }

    for shot_id, prompt in shots.items():
        filename = f"placeholder_shot_{shot_id}.jpg"
        if os.path.exists(filename):
            print(f"Skipping {shot_id}, file already exists.")
            continue
            
        print(f"\nGenerating Shot {shot_id}: {prompt}")
        try:
            image_url = generate_with_openai(prompt, api_key)
            if image_url:
                download_image(image_url, filename)
        except Exception as e:
            print(f"Failed to generate Shot {shot_id}: {e}")

if __name__ == "__main__":
    main()
