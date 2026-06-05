import os
import sys

# Append the root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from nthdimensionacademy.test_ai import generate_with_openai  # pyrefly: ignore [missing-import]
except ImportError as e:
    print(f"Could not import OpenAI generator. Error: {e}")
    sys.exit(1)

def main():
    # Shot 28 Context: Title Card "DEAD LOOP"
    prompt = "A cinematic movie title card. The text 'DEAD LOOP' in bold, distressed, futuristic neon typography. Industrial cyberpunk noir aesthetic. Dark background with subtle fog and embers drifting through the frame."
    
    print(f"FINAL_PROMPT: {prompt}")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No API key found in environment for generation.")
        return
        
    image_url = generate_with_openai(prompt, api_key)
    print(f"Generated URL: {image_url}")

if __name__ == "__main__":
    main()
