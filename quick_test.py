import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path("c:/Users/navka/navakanth001/.env"))
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

def test_model(model_name):
    print(f"Testing {model_name}...")
    try:
        res = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        print("SUCCESS:", res.choices[0].message.content)
    except Exception as e:
        print("FAILED:", str(e))

test_model("nvidia/llama-3.3-nemotron-super-49b-v1.5")
test_model("deepseek-ai/deepseek-coder-6.7b-instruct")
test_model("meta/llama-3.1-8b-instruct")
