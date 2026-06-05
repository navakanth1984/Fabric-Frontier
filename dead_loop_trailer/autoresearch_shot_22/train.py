import os
import sys

# Append the root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from nthdimensionacademy.test_ai import generate_with_flux_1  # pyrefly: ignore [missing-import]
except ImportError as e:
    print(f"Could not import BFL generator. Error: {e}")
    sys.exit(1)

def main():
    # AGENT: Modify this prompt to hit a 1.0 score in prepare.py.
    # Adhere strictly to program.md constraints!
    
    prompt = "Low angle tracking shot, 50mm lens. Arjun stands up slowly, jaw clenched, shoulders pulled back, eyes locked forward. The environment is lit with a high-contrast clash between terminal green cyan flares and analog amber practical lights."
    
    print(f"FINAL_PROMPT: {prompt}")
    
    # Use mock key if none in environment
    api_key = os.environ.get("OPENAI_API_KEY", "mock_key_123")
    
    image_url = generate_with_flux_1(prompt, api_key)
    print(f"Generated URL: {image_url}")

if __name__ == "__main__":
    main()
