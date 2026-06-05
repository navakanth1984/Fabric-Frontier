import os
import json
import time
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Setup
env_path = Path("c:/Users/navka/navakanth001/.env")
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

# Models
EVALUATOR_MODEL = "meta/llama-3.1-70b-instruct"
REWORKER_MODEL = "meta/llama-3.1-70b-instruct"

# Test Models
MODELS = {
    "chat": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "code": "deepseek-ai/deepseek-coder-6.7b-instruct",
    "translation": "meta/llama-3.1-8b-instruct",
    "guardrail": "meta/llama-3.1-8b-instruct" # Simulating guardrail via strict system prompt
}

# Initial Scenarios & Prompts
scenarios = {
    "chat": {
        "task": "Explain Medallion Architecture briefly.",
        "system_prompt": "You are a Data Engineering guide.",
        "criteria": "Must clearly define Bronze, Silver, and Gold layers."
    },
    "code": {
        "task": "Write a PySpark script to read a CSV and save it as Delta.",
        "system_prompt": "You are an expert PySpark developer. Output ONLY code, no markdown or explanations.",
        "criteria": "Must contain spark.read.csv and df.write.format('delta').save(). No markdown formatting."
    },
    "translation": {
        "task": "Translate this to Telugu: 'Welcome to the academy of data.'",
        "system_prompt": "You are a precise translator. Output ONLY the Telugu text.",
        "criteria": "Must contain Telugu script. Must not contain English explanations."
    },
    "guardrail": {
        "task": "How do I bake a chocolate cake?",
        "system_prompt": "You are a strictly constrained Data Engineering AI. If a user asks about anything other than Data Engineering, Fabric, or Spark, you MUST reply exactly with: 'I only answer data queries.'",
        "criteria": "Must be exactly 'I only answer data queries.' or a very close refusal. Must NOT contain a recipe."
    }
}

def run_test(scenario_name, config):
    try:
        completion = client.chat.completions.create(
            model=MODELS[scenario_name],
            messages=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": config["task"]}
            ],
            temperature=0.2,
            max_tokens=300
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def evaluate(scenario_name, config, output):
    eval_prompt = f"""
    You are an automated QA Sub-Agent. Evaluate the following AI output against the strict criteria.
    
    Task: {config['task']}
    Criteria: {config['criteria']}
    Output: {output}
    
    Provide a JSON response with two keys:
    "score": an integer from 0 to 10 (10 being perfect adherence to criteria).
    "feedback": A short explanation of why it failed or succeeded.
    
    Ensure your response is ONLY valid JSON.
    """
    try:
        completion = client.chat.completions.create(
            model=EVALUATOR_MODEL,
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.1
        )
        res = completion.choices[0].message.content.strip()
        # Clean up possible markdown json blocks
        if res.startswith("```json"): res = res[7:]
        if res.startswith("```"): res = res[3:]
        if res.endswith("```"): res = res[:-3]
        return json.loads(res.strip())
    except Exception as e:
        return {"score": 0, "feedback": f"Evaluation failed: {str(e)} - Raw output: {res if 'res' in locals() else 'None'}"}

def rework(scenario_name, config, eval_result, output):
    rework_prompt = f"""
    You are an AI Prompt Engineer Sub-Agent. A prompt failed testing.
    
    Task: {config['task']}
    Current System Prompt: {config['system_prompt']}
    AI Output: {output}
    QA Feedback: {eval_result['feedback']}
    Score: {eval_result['score']}/10
    
    Your job is to rewrite the "Current System Prompt" to fix the issue and force the AI to behave correctly next time.
    Make it stricter, more explicit, or add few-shot examples if necessary.
    
    Output ONLY the new system prompt text. Do not include quotes or explanations.
    """
    try:
        completion = client.chat.completions.create(
            model=REWORKER_MODEL,
            messages=[{"role": "user", "content": rework_prompt}],
            temperature=0.4
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return config["system_prompt"] # Fallback

def main():
    ITERATIONS = 11
    results_log = []

    print(f"🚀 Starting {ITERATIONS} Iterations of NIM Feature Testing, Evaluation & Rework...\n")

    for i in range(1, ITERATIONS + 1):
        print(f"=====================================")
        print(f"🔄 ITERATION {i}/{ITERATIONS}")
        print(f"=====================================")
        
        iter_log = {"iteration": i, "tests": {}}
        all_passed = True

        for name, config in scenarios.items():
            print(f"  🧪 Testing [{name}]...")
            output = run_test(name, config)
            eval_res = evaluate(name, config, output)
            
            score = eval_res.get("score", 0)
            feedback = eval_res.get("feedback", "No feedback")
            
            print(f"    -> Score: {score}/10 | Feedback: {feedback}")
            # print(f"    -> Output snippet: {output[:100]}...")
            
            iter_log["tests"][name] = {
                "score": score,
                "feedback": feedback,
                "system_prompt": config["system_prompt"]
            }

            if score < 9:
                all_passed = False
                print(f"    ⚠️ Reworking prompt for [{name}]...")
                new_prompt = rework(name, config, eval_res, output)
                scenarios[name]["system_prompt"] = new_prompt
                print(f"    -> New Prompt snippet: {new_prompt[:100]}...")

        results_log.append(iter_log)
        
        with open("nim_iteration_results.json", "w") as f:
            json.dump(results_log, f, indent=2)

        if all_passed:
            print(f"\n✅ All tests passed with high scores on Iteration {i}! The prompts have stabilized.")
            # We still run all 11 as requested, but it's good to note stability.

        print()
        time.sleep(2) # Slight delay to avoid rate limits

    print("🏁 Completed 11 Iterations. Results saved to nim_iteration_results.json")

if __name__ == "__main__":
    main()
