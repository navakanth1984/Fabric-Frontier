import os
import sys
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('c:/Users/navka/navakanth001/.env')
load_dotenv(dotenv_path=env_path)

client = OpenAI(
    base_url='https://integrate.api.nvidia.com/v1',
    api_key=os.getenv('NVIDIA_API_KEY')
)

DEFAULT_MODEL = 'meta/llama-3.1-70b-instruct'

def creative_studio_chat(prompt, context_file=None, model=DEFAULT_MODEL):
    system_prompt = '''
    You are the Master Story Architect and Creative Consultant.
    Your expertise covers the McKee 'Story' principles, Egri's 'Art of Dramatic Writing', and cinematic visual language.

    GUIDELINES:
    1. Analyze the GAP: Focus on the difference between character expectation and reality.
    2. SUBTEXT: Identify what is unsaid. Ensure dialogue is never 'on-the-nose'.
    3. VOICE: Maintain a tone that is professional, insightful, and creatively provocative.

    When a context file is provided, treat it as the 'Source of Truth' for characters and world-building.
    '''

    messages = [{'role': 'system', 'content': system_prompt}]

    if context_file and os.path.exists(context_file):
        with open(context_file, 'r', encoding='utf-8') as f:
            context_data = f.read()
            messages.append({'role': 'user', 'content': f'CONTEXT / MANUSCRIPT REFERENCE:\n\n{context_data[:15000]}'})
            print(f'📖 Context loaded from {context_file}')

    messages.append({'role': 'user', 'content': prompt})
    print(f'🎬 Consulting with {model}...')

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )

        print('\n--- CREATIVE RESPONSE ---\n')
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print('\n\n--- END OF CONSULTATION ---')

    except Exception as e:
        print(f'❌ Error: {str(e)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NVIDIA NIM Creative Studio')
    parser.add_argument('prompt', type=str, help='Your creative query or instruction')
    parser.add_argument('--file', type=str, help='Optional path to a script or novel file for context')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help='NIM model to use')

    args = parser.parse_args()
    creative_studio_chat(args.prompt, args.file, args.model)
