import subprocess
import sys
import os

CORE_FOLDERS = [
    "agentic-loop",
    "daava_production",
    "AutoGrade_Backend",
    "dead_loop_trailer"
]

def run_check():
    print(">>> Starting Pyrefly Type-Safety Pre-Commit Check...")
    
    # We use the root config which handles excludes and search paths
    # We pass the core folders explicitly to avoid checking legacy noise
    cmd = ["pyrefly", "check"] + CORE_FOLDERS
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[PASS] Type check passed! Core modules are compliant.")
            return True
        else:
            print("[FAIL] Type check failed. Please fix the following errors before committing:")
            print("-" * 50)
            print(result.stdout)
            print("-" * 50)
            return False
            
    except FileNotFoundError:
        print("❌ Error: 'pyrefly' command not found. Please install it with 'pip install pyrefly'.")
        return False

if __name__ == "__main__":
    if not run_check():
        sys.exit(1)
