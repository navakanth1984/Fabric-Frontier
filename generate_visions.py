import os
import sys
import json
from pathlib import Path
from nvidia_nim_prototype import get_client, BudgetMonitor

def generate_vision(model, prompt, budget_threshold=10000):
    client = get_client()
    monitor = BudgetMonitor(threshold=budget_threshold)
    
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are the Director of the cinematic Indian Cyberpunk Noir film 'Dead Loop'. Expand the given storyboard shot into a detailed Director's Vision. Describe Mood, Camera Movement, Lighting, and Cybernetic elements in detail. Do not include any meta-commentary, just the Vision."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        top_p=0.9,
        max_tokens=1024,
    )
    
    response = completion.choices[0].message.content
    usage = completion.usage
    if usage:
        monitor.log_call(usage, model)
        
    return response

shots = [
    {"name": "Shot 2.1", "desc": "Extreme close-up on a vintage CRT monitor powering on. Amber phosphor text scrolls rapidly: 'INITIATING DEAD_LOOP'."},
    {"name": "Shot 2.2", "desc": "Over-the-shoulder shot. Arjun interfaces with a bulky, retro-futuristic terminal. Wires connect directly to a port on his neck."},
    {"name": "Shot 2.3", "desc": "Fast Dolly-in. The terminal screen erupts in bright neon green, illuminating Arjun's face in stark high-key lighting."},
    {"name": "Shot 3.1", "desc": "Action wide shot. Arjun sprints across a rooftop, leaping over a gap. The HITECCity skyline looms in the background, contrasting sleek glass with his gritty surroundings."},
    {"name": "Shot 3.2", "desc": "Tracking close-up on his boots splashing through deep water on the roof, sending neon-lit droplets flying in slow motion."},
    {"name": "Shot 3.3", "desc": "Dutch angle, medium shot. Arjun slides behind an aged copper ventilation unit as searchlights sweep the area."},
    {"name": "Shot 4.1", "desc": "Slow pan across a massive, abandoned server farm submerged in shallow water. Cables hang like vines."},
    {"name": "Shot 4.2", "desc": "Close-up on Arjun's face, bathed in a soft, ethereal amber light. He looks up in awe."},
    {"name": "Shot 4.3", "desc": "The camera pulls back rapidly to reveal a giant, holographic mandala floating above the servers. Smash to black. Title card: DEAD LOOP."}
]

model = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
output_file = Path("daava_production/dead_loop_directors_vision.md")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("# DEAD LOOP: Complete Director's Visions\n\n")

for shot in shots:
    print(f"Generating vision for {shot['name']}...")
    prompt = f"Expand {shot['name']} into a Director's Vision. Description: {shot['desc']}"
    vision = generate_vision(model, prompt)
    
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"## {shot['name']}\n\n")
        f.write(vision + "\n\n---\n\n")

print(f"All visions generated and saved to {output_file}")
