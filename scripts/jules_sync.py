#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import subprocess

# Colors for stunning CLI aesthetics
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Config
REPO_OWNER = "navakanth1984"
REPO_NAME = "kqlbridge"
WORKSPACE_ROOT = r"c:\Users\navka\navakanth001"
KQLBRIDGE_PATH = os.path.join(WORKSPACE_ROOT, "kqlbridge")
WORKTREE_DIR = os.path.join(WORKSPACE_ROOT, "kqlbridge-worktrees")

def print_header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}\n")

def run_git(args, cwd=KQLBRIDGE_PATH):
    try:
        result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Git Error running {args}: {e.stderr.strip()}{RESET}")
        return None

def fetch_jules_prs():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {"User-Agent": "Antigravity-Jules-Bridge-v1.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            # Filter for Jules PRs (checking title, body, or user login)
            jules_prs = []
            for pr in data:
                body = pr.get("body") or ""
                user = pr.get("user", {}).get("login") or ""
                if "Jules" in body or "google-labs-jules" in user:
                    jules_prs.append(pr)
            return jules_prs
    except Exception as e:
        print(f"{RED}Error fetching PRs from GitHub: {e}{RESET}")
        return []

def get_local_worktrees():
    stdout = run_git(["worktree", "list"])
    worktrees = []
    if stdout:
        for line in stdout.split("\n"):
            parts = line.split()
            if len(parts) >= 3:
                path = parts[0]
                commit = parts[1]
                # Branch is inside brackets, e.g., [my-branch]
                branch = parts[2].strip("[]")
                worktrees.append({"path": path, "commit": commit, "branch": branch})
    return worktrees

def display_dashboard():
    print(f"{BOLD}{MAGENTA}🌌 JULES + ANTIGRAVITY + GITHUB INTEGRATION BRIDGE{RESET}")
    print(f"{BOLD}{CYAN}------------------------------------------------------------{RESET}")
    
    print(f"{BOLD}Fetching latest upstream Pull Requests from GitHub...{RESET}")
    prs = fetch_jules_prs()
    worktrees = get_local_worktrees()
    
    if not prs:
        print(f"\n{YELLOW}No active Pull Requests found from Jules on {REPO_OWNER}/{REPO_NAME}.{RESET}")
        print("Tip: Start a new task on the Jules upstream dashboard or open a PR.")
        return
        
    print(f"\n{BOLD}{GREEN}Found {len(prs)} active PRs created by Jules Bot:{RESET}")
    print(f"{BOLD}{'-'*90}{RESET}")
    print(f"{BOLD}{'PR #':<6} | {'Title':<45} | {'Branch':<20} | {'Worktree Status':<15}{RESET}")
    print(f"{BOLD}{'-'*90}{RESET}")
    
    for pr in prs:
        number = pr.get("number")
        title = pr.get("title")
        branch = pr.get("head", {}).get("ref")
        
        # Limit title size
        if len(title) > 42:
            title = title[:39] + "..."
            
        # Match with worktrees
        matched_wt = None
        for wt in worktrees:
            if wt["branch"] == branch:
                matched_wt = wt
                break
                
        if matched_wt:
            wt_status = f"{GREEN}Allocated{RESET}"
        else:
            wt_status = f"{YELLOW}Available{RESET}"
            
        print(f"{BOLD}{f'#{number}':<6}{RESET} | {title:<45} | {branch:<20} | {wt_status:<15}")
        
    print(f"{BOLD}{'-'*90}{RESET}")
    
    print(f"\n{BOLD}Available Options:{RESET}")
    print(f"  {GREEN}[1]{RESET} Sync & update local branches from upstream")
    print(f"  {GREEN}[2]{RESET} Allocate a new Git Worktree for a Jules PR")
    print(f"  {GREEN}[3]{RESET} Run test suite inside an allocated worktree")
    print(f"  {GREEN}[4]{RESET} Push modifications back to Jules PR")
    print(f"  {GREEN}[5]{RESET} Exit")
    
    choice = input(f"\n{BOLD}{CYAN}Select an action (1-5): {RESET}").strip()
    
    if choice == "1":
        print(f"\n{BOLD}Fetching remote updates...{RESET}")
        run_git(["fetch", "origin"])
        print(f"{GREEN}Fetch completed successfully.{RESET}")
    elif choice == "2":
        allocate_worktree(prs, worktrees)
    elif choice == "3":
        run_tests(worktrees)
    elif choice == "4":
        push_updates(worktrees)
    elif choice == "5":
        print("Goodbye!")
        sys.exit(0)

def allocate_worktree(prs, worktrees):
    pr_num = input(f"\n{BOLD}Enter PR Number to allocate (e.g. 14): {RESET}").strip()
    selected_pr = None
    for pr in prs:
        if str(pr.get("number")) == pr_num:
            selected_pr = pr
            break
            
    if not selected_pr:
        print(f"{RED}PR #{pr_num} not found in the list.{RESET}")
        return
        
    branch = selected_pr.get("head", {}).get("ref")
    wt_folder_name = branch.replace("/", "-")
    wt_path = os.path.join(WORKTREE_DIR, wt_folder_name)
    
    # Check if already exists
    if os.path.exists(wt_path):
        print(f"{RED}Worktree directory already exists at: {wt_path}{RESET}")
        return
        
    print(f"\n{BOLD}Creating Git Worktree for branch '{branch}'...{RESET}")
    # Run fetch to ensure local repo knows the branch
    run_git(["fetch", "origin", f"{branch}:{branch}"])
    
    # Add worktree
    stdout = run_git(["worktree", "add", wt_path, branch])
    if stdout:
        print(f"\n{GREEN}Success! Worktree allocated successfully at:{RESET}")
        print(f"{BOLD}{wt_path}{RESET}")
        print(f"\nYou can now pair-program with Antigravity directly inside this folder!")

def run_tests(worktrees):
    print(f"\n{BOLD}Allocated local worktrees:{RESET}")
    for i, wt in enumerate(worktrees):
        if "kqlbridge-worktrees" in wt["path"]:
            print(f"  [{i}] {GREEN}{wt['branch']}{RESET} -> {wt['path']}")
            
    wt_idx = input(f"\n{BOLD}Select worktree index to run tests: {RESET}").strip()
    try:
        wt = worktrees[int(wt_idx)]
    except Exception:
        print(f"{RED}Invalid selection.{RESET}")
        return
        
    print(f"\n{BOLD}Running pytest suite in {wt['branch']}...{RESET}")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest"],
            cwd=wt["path"],
            env=env
        )
    except Exception as e:
        print(f"{RED}Error running tests: {e}{RESET}")

def push_updates(worktrees):
    print(f"\n{BOLD}Active worktrees:{RESET}")
    for i, wt in enumerate(worktrees):
        if "kqlbridge-worktrees" in wt["path"]:
            print(f"  [{i}] {GREEN}{wt['branch']}{RESET} -> {wt['path']}")
            
    wt_idx = input(f"\n{BOLD}Select worktree index to push changes: {RESET}").strip()
    try:
        wt = worktrees[int(wt_idx)]
    except Exception:
        print(f"{RED}Invalid selection.{RESET}")
        return
        
    # Check status first
    status = run_git(["status", "--porcelain"], cwd=wt["path"])
    if not status:
        print(f"\n{YELLOW}No uncommitted changes in this worktree. Checking if commits need to be pushed...{RESET}")
    else:
        print(f"\n{YELLOW}Uncommitted changes detected:{RESET}\n{status}")
        commit_msg = input(f"\n{BOLD}Enter commit message (e.g. 'fix: resolve recursion edge case'): {RESET}").strip()
        if commit_msg:
            run_git(["add", "."], cwd=wt["path"])
            run_git(["commit", "-m", commit_msg], cwd=wt["path"])
            print(f"{GREEN}Changes committed successfully.{RESET}")
            
    print(f"\n{BOLD}Pushing commits to branch origin/{wt['branch']}...{RESET}")
    run_git(["push", "origin", wt["branch"]], cwd=wt["path"])
    print(f"\n{GREEN}Success! Upstream Jules bot notified of the changes. Check GitHub for the updated review!{RESET}")

if __name__ == "__main__":
    try:
        display_dashboard()
    except KeyboardInterrupt:
        print("\nExited.")
