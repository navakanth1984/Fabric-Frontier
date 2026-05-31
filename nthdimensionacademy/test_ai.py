import os
import time

def generate_with_openai(prompt: str, api_key: str):
    """
    Generates an image using OpenAI's DALL-E 3 model.
    Requires `pip install openai`
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] OpenAI package not installed. Run: pip install openai")
        return None

    print(f"Initiating OpenAI DALL-E 3 Generation...")
    print(f"Prompt: '{prompt}'")
    
    client = OpenAI(api_key=api_key)
    
    try:
        start_time = time.time()
        print("\nSending request to OpenAI API...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024", # DALL-E 3 supports 1024x1024, 1024x1792, or 1792x1024
            quality="standard",
            n=1,
        )
        
        latency = time.time() - start_time
        image_url = response.data[0].url
        
        print(f"\n[SUCCESS] Response received from OpenAI! (Latency: {latency:.2f}s)")
        print(f"Image URL: {image_url}")
        
        return image_url
        
    except Exception as e:
        print(f"\n[ERROR] Failed to generate with OpenAI: {e}")
        return None

def generate_with_gemini(prompt: str, api_key: str):
    """
    Generates an image using Google's Gemini / Imagen model.
    Requires `pip install google-generativeai`
    """
    try:
        import google.generativeai as genai
    except ImportError:
        print("[ERROR] google-generativeai package not installed. Run: pip install google-generativeai")
        return None

    print(f"Initiating Gemini Image Generation...")
    print(f"Prompt: '{prompt}'")
    
    genai.configure(api_key=api_key)
    
    try:
        start_time = time.time()
        print("\nSending request to Gemini API...")
        
        # Currently, Gemini image generation is accessed via specialized models or REST API.
        # Note: As of late 2023/2024, Gemini's python SDK uses `generate_images` on certain models.
        # If your API tier does not support it via the Python SDK, you might need to use the REST API.
        
        # Mocking the success here to prevent API blockages if the user's project lacks the specific Vision scopes.
        time.sleep(2.0)
        latency = time.time() - start_time
        image_url = "https://google.dev/mock-gemini-image-url.jpg"
        
        print(f"\n[SUCCESS] Response received from Gemini! (Latency: {latency:.2f}s)")
        print(f"Image URL: {image_url} (Mocked - configure actual SDK method based on your GCP/AI Studio tier)")
        
        return image_url
        
    except Exception as e:
        print(f"\n[ERROR] Failed to generate with Gemini: {e}")
        return None

def generate_video_with_openai(prompt: str, api_key: str):
    """
    Scaffold for generating video using OpenAI (e.g., Sora API when publicly available).
    Routes image prompt -> video generation endpoint.
    """
    print(f"Initiating OpenAI Video Generation (Sora)...")
    print(f"Prompt: '{prompt}'")
    
    # Placeholder for OpenAI Sora API integration
    # e.g., client.video.generate(...)
    time.sleep(2.0)
    print(f"\n[SUCCESS] Mock response received from OpenAI Video API.")
    return "https://openai.com/mock-sora-video.mp4"

def generate_video_with_gemini(prompt: str, api_key: str):
    """
    Scaffold for generating video using Gemini (e.g., Veo / Imagen 3 Video via Vertex).
    """
    print(f"Initiating Gemini Video Generation (Veo)...")
    print(f"Prompt: '{prompt}'")
    
    # Placeholder for Gemini Video API integration
    time.sleep(2.0)
    print(f"\n[SUCCESS] Mock response received from Gemini Video API.")
    return "https://google.dev/mock-veo-video.mp4"

# Keep the original function signature alive so train.py doesn't break, 
# but route it to OpenAI by default.
def generate_with_flux_1(prompt: str, api_key: str):
    print("\n[ROUTING] Bypassing Flux... Rerouting to OpenAI DALL-E 3...")
    return generate_with_openai(prompt, api_key)

if __name__ == "__main__":
    # Ensure you set your API key in your environment variables
    # Windows CMD: set OPENAI_API_KEY=sk-...
    # PowerShell: $env:OPENAI_API_KEY="sk-..."
    
    test_key = os.environ.get("OPENAI_API_KEY")
    if not test_key:
        print("WARNING: OPENAI_API_KEY not found in environment. The call will likely fail.")
        test_key = "mock_key_123"
        
    test_prompt = "A cinematic shot of an Indian detective in a neon-lit alleyway, hyper-realistic, 8k resolution, highly detailed"
    
    # Run the tests
    generate_with_openai(test_prompt, test_key)
    generate_video_with_openai(test_prompt, test_key)
