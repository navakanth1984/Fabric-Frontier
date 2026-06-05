import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("c:/Users/navka/navakanth001/.env"))
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY"))

MODEL = "meta/llama-3.1-70b-instruct"

def draft_masterpiece():
    system_prompt = """
    You are a Telugu Film Writer specialized in Raw, Telangana-based political thrillers (like 'Arjun Reddy' or 'Dasara' in tone but political).
    
    SCENE: INT. INTERROGATION ROOM - NIGHT. 
    Arjun (idealist, grieving) vs Suresh Yadav (predatory MLA).
    
    STRICT RULES:
    1. DIALOGUE: Use ONLY Telugu with a raw Telangana/Hyderabadi street accent. No translations.
    2. ACCENT CUES: Use 'emayindi', 'gadide', 'endira', 'em cheptunav', 'motham', 'katam', 'paaye'.
    3. SUBTEXT: Arjun doesn't explain his grief. He talks about 'reliability' and 'claims'. 
    4. YADAV: He is eating a mango. Sticky hands. He treats people like the fruit—peel them, eat them, throw the seed.
    5. ELEVATION: Arjun ends the scene by making Yadav stop eating.
    
    FORMAT:
    INT. INTERROGATION ROOM - NIGHT
    Action...
    CHARACTER
    Dialogue...
    """
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": "Write the scene now."}],
        temperature=0.7
    )
    with open("factory_output_telugu_v2.md", "w", encoding="utf-8") as f: f.write(res.choices[0].message.content)

if __name__ == "__main__":
    draft_masterpiece()
