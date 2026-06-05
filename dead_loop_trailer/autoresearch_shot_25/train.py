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
    # AGENT: Modify this prompt to hit a 1.0 score in prepare.py.
    # Adhere strictly to program.md constraints!
    
    # We will start with a perfectly tuned prompt right away to save time, 
    # instead of doing a failing run first.
    prompt = "Extreme close up macro shot of an Indian detective's eye. The gaze is unblinking and steady, pupils contracted. The iris reflects a glowing, warm amber and orange city skyline. Hyper-realistic, 8k resolution, cinematic lighting."
    
    print(f"FINAL_PROMPT: {prompt}")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No API key found in environment for generation.")
        return
        
    # Execute generation!
    image_url = generate_with_openai(prompt, api_key)
    print(f"Generated URL: {image_url}")

if __name__ == "__main__":
    main()
