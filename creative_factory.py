import os
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("c:/Users/navka/navakanth001/.env")
load_dotenv(dotenv_path=env_path)
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

MODEL = "meta/llama-3.1-70b-instruct"

def creative_writer(prompt, context=''):
    print("✍️ WRITER: Drafting Fountain-Strict Scene...")
    system_prompt = """
    You are the CREATIVE WRITER. You MUST follow FOUNTAIN-STRICT formatting.
    
    RULES:
    1. NO BOLDING. NO ITALICS. NO MARKDOWN FORMATTING.
    2. Scene Headings start with INT. or EXT. and must be in ALL CAPS.
    3. Action lines are plain text.
    4. Character names must be on their own line in ALL CAPS.
    5. Dialogue must follow immediately on the next line.
    6. Parentheticals must be in (parens) on their own line between Character and Dialogue.
    7. Transitions must be in ALL CAPS followed by a colon (e.g. FADE OUT:).
    
    GOAL: Elevate the EQ (Emotional Quotient). Focus on the RAGE, the MONSOON, and the MANGO.
    """
    res = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nTASK: {prompt}"}
        ],
        temperature=0.7
    )
    return res.choices[0].message.content

def master_critic(draft):
    print("⚖️ CRITIC: Auditing Strict Formatting...")
    system_prompt = """
    You are the MASTER CRITIC. You are a formatting tyrant.
    
    AUDIT CHECKLIST:
    - IS THERE ANY BOLDING? (If yes, Fail)
    - ARE SCENE HEADINGS ALL CAPS?
    - ARE CHARACTER NAMES ALONE ON THEIR OWN LINE?
    - IS THE DIALOGUE DIRECTLY UNDER THE CHARACTER?
    
    Provide JSON:
    "score_formatting": 1-10
    "score_eq": 1-10
    "critique": "Identify every formatting violation."
    "rework_instructions": "Tell the writer to remove bolding and fix the layout."
    """
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"DRAFT:\n{draft}"}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return json.loads(res.choices[0].message.content)

def run_factory(task, iterations=5):
    current_draft = ""
    for i in range(1, iterations + 1):
        print(f"\n--- 🔄 ITERATION {i} ---")
        current_draft = creative_writer(task if i == 1 else audit["rework_instructions"])
        audit = master_critic(current_draft)
        print(f"⭐ FORMAT: {audit['score_formatting']}/10 | EQ: {audit['score_eq']}/10")
        if audit["score_formatting"] >= 9 and audit["score_eq"] >= 8:
            print("✅ MASTERPIECE ACHIEVED.")
            break
    
    with open("factory_output.md", "w", encoding="utf-8") as f: f.write(current_draft)
    os.system("py screenplay_formatter.py")

if __name__ == "__main__":
    task = "Arjun is trapped in a small, windowless interrogation room with Suresh Yadav. Monsoon storm outside. Yadav eats a mango. Theme: RAGE."
    run_factory(task)
