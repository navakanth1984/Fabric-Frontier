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
    # Shot 27 Context: "A single orange line of code appears."
    # We want a stark, minimalist composition reflecting the 'Dead Loop' theme.
    prompt = "A pitch black computer terminal screen. A single, glowing, vibrant orange line of code is typing itself out in the center of the screen. High contrast, cinematic, cyberpunk hacker aesthetic, glowing neon orange on pure black."
    
    print(f"FINAL_PROMPT: {prompt}")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No API key found in environment for generation.")
        return
        
    image_url = generate_with_openai(prompt, api_key)
    print(f"Generated URL: {image_url}")

if __name__ == "__main__":
    main()
