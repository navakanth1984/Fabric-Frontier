import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Setup
env_path = Path("c:/Users/navka/navakanth001/.env")
load_dotenv(dotenv_path=env_path)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

MODEL = "meta/llama-3.1-70b-instruct"

def creative_writer(prompt, context=''):
    print("✍️ WRITER: Drafting High-EQ Scene (Telugu/Telangana)...")
    system_prompt = """
    You are the CREATIVE WRITER. You are a master of the Telangana accent (Hyderabad/Nampally slang) and cinematic subtext.
    
    RULES:
    1. DIALOGUE: Must be in TELUGU with a heavy TELANGANA/HYDERABADI accent.
    2. MOTIVES: 
       - Suresh: Power is ownership. He owns the water, the beds, the votes. 
       - Arjun: Reliability is justice. He wants a system that doesn't need a 'boss'.
    3. NO EXPOSITION: Do not explain the past. Show it through the power dynamic.
    4. CHARACTER ELEVATION: Arjun starts suppressed but ends the scene by taking the psychological lead.
    5. FORMAT: INT./EXT. (BOLD ALL CAPS), Character Names (ALL CAPS), Action (Normal).
    """
    res = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nTASK: {prompt}"}
        ],
        temperature=0.8
    )
    return res.choices[0].message.content

def master_critic(draft):
    print("⚖️ CRITIC: Auditing Subtlety & Accent...")
    system_prompt = """
    You are the MASTER CRITIC. You are a native Telugu speaker from Hyderabad.
    
    AUDIT CHECKLIST:
    - Is the Telangana accent authentic (e.g., using 'emayindi', 'gadide', 'entira', 'cheptuna', 'vostundu')?
    - Is Arjun's elevation clear? Does he win the beat?
    - Is there any clunky exposition?
    
    Provide JSON:
    "score_accent": 1-10
    "score_subtlety": 1-10
    "score_elevation": 1-10
    "critique": "Identify any 'on-the-nose' dialogue."
    "rework_instructions": "Direct the writer to sharpen the Telangana slang and Arjun's final retort."
    """
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"DRAFT:\n{draft}"}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return json.loads(res.choices[0].message.content)

def run_factory(task, iterations=3):
    current_draft = ""
    for i in range(1, iterations + 1):
        print(f"\n--- 🔄 ITERATION {i} ---")
        current_draft = creative_writer(task if i == 1 else audit["rework_instructions"])
        audit = master_critic(current_draft)
        print(f"⭐ ACCENT: {audit['score_accent']}/10 | SUBTLETY: {audit['score_subtlety']}/10 | ELEVATION: {audit['score_elevation']}/10")
        if audit["score_accent"] >= 9 and audit["score_elevation"] >= 9:
            print("✅ MASTERPIECE ACHIEVED.")
            break
    
    with open("factory_output_telugu.md", "w", encoding="utf-8") as f: f.write(current_draft)

if __name__ == "__main__":
    task = "Arjun and Suresh Yadav in the interrogation room. Suresh eating a mango. Dialogues in Telangana accent. Arjun elevates at the end."
    run_factory(task)
