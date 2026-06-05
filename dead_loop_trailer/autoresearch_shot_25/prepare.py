import sys
import subprocess
import time

def evaluate():
    print("--- PREPARE.PY: Locked Oracle Evaluation ---")
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, "train.py"], capture_output=True, text=True, timeout=5)
        output = result.stdout
    except subprocess.TimeoutExpired:
        print("Score: 0.0 (Timeout: Exceeded SLA)")
        return
    except Exception as e:
        print(f"Score: 0.0 (Execution Error: {e})")
        return

    latency = time.time() - start_time
    score = 0.0
    
    if "FINAL_PROMPT:" not in output:
        print("Score: 0.0 (Did not find FINAL_PROMPT in output)")
        return
        
    prompt_line = [line for line in output.split('\n') if line.startswith("FINAL_PROMPT:")][0]
    prompt_lower = prompt_line.lower()
    
    # Check 1: Level 3 Performance constraints (No emotion labels)
    emotion_labels = ['fearless', 'confident', 'brave', 'fear', 'determined']
    has_emotion = any(word in prompt_lower for word in emotion_labels)
    if has_emotion:
        print("Penalty: -0.5 (Contains Level 1 emotion labels instead of physical action)")
    else:
        score += 0.4
        
    # Check 2: Lighting constraints
    if 'amber' in prompt_lower or 'orange' in prompt_lower:
        score += 0.3
    else:
        print("Penalty: -0.3 (Missing required color reflection: amber/orange)")
        
    # Check 3: Camera awareness (ECU / macro)
    if 'macro' in prompt_lower or 'extreme close up' in prompt_lower or 'ecu' in prompt_lower:
        score += 0.3
    else:
        print("Penalty: -0.3 (Missing macro or ECU camera specifications)")
        
    print(f"Latency: {latency:.2f}s")
    print(f"Final Score: {score:.1f} / 1.0")

if __name__ == "__main__":
    evaluate()
