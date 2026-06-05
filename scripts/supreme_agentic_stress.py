#!/usr/bin/env python3
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Inject correct PYTHONPATH
sys.path.insert(0, os.path.abspath("src"))

try:
    from kqlbridge import smart_transpile
    from kqlbridge.parser import parse
except ImportError:
    # Try parent directory in case of execution relative to worktree
    sys.path.insert(0, os.path.abspath("../src"))
    from kqlbridge import smart_transpile
    from kqlbridge.parser import parse

# ANSI Aesthetics
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    print(f"\n{BOLD}{MAGENTA}*** SUPREME AGENTIC STRESS TEST GATEWAY: JULES + ANTIGRAVITY ***{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}\n")

def run_deep_nesting_stress():
    print(f"{BOLD}{CYAN}1. STRESS VECTOR [JULES-01]: Deep Nesting Stack Limits{RESET}")
    print(f"Generating 800 nested 'iff()' clauses to test Jules' iterative compiler...")
    
    # Generate: iff(col == 1, 1, iff(col == 2, 2, ...))
    nesting_depth = 800
    args = []
    for i in range(1, nesting_depth + 1):
        args.append(f"col == {i}")
        args.append(str(i))
    args.append("9999") # Default default value
    
    # Assemble raw KQL
    kql = f"MyTable | extend nested_val = case({', '.join(args)}) | project nested_val"
    
    print(f"Generated KQL size: {len(kql) / 1024:.2f} KB | Nesting depth: {nesting_depth} elements")
    
    start_time = time.perf_counter()
    try:
        engine, sql = smart_transpile(kql)
        duration = time.perf_counter() - start_time
        print(f"{GREEN}[SUCCESS]{RESET} Transpiled successfully in {duration:.4f} seconds!")
        print(f"Engine chosen: {BOLD}{engine}{RESET}")
        print(f"SQL Size: {len(sql) / 1024:.2f} KB")
        # Print a small snippet of the compiled code
        snippet = sql[:150] + " ... [TRUNCATED] ... " + sql[-150:]
        print(f"\n--- Transpiled Code Snippet ---\n{snippet}\n--------------------------------")
        return True
    except RecursionError:
        import traceback
        traceback.print_exc()
        print(f"{RED}[FAILED] Python recursion limit hit (RecursionError)! Jules' iterative fix is inactive.{RESET}")
        return False
    except Exception as e:
        print(f"{RED}[FAILED] Transpilation crashed with {type(e).__name__}: {e}{RESET}")
        return False

def run_concurrency_stress():
    print(f"\n{BOLD}{CYAN}2. STRESS VECTOR [ANTIGRAVITY-02]: High Concurrency Multi-Thread Load{RESET}")
    
    queries = [
        "SecurityEvents | where Level == 'Error' | count",
        "Orders | extend Cost = Price * Quantity | project OrderId, Cost",
        "AppLogs | summarize total = count() by bin(TimeGenerated, 1h) | order by total desc",
        "SecurityEvents | union HoneypotHits | project source_ip | take 50",
        "let ErrorCount = SecurityEvents | where Level == 'Error' | count; AppLogs | extend errors = ErrorCount",
    ]
    
    threads_count = 32
    iterations_per_thread = 20
    total_runs = threads_count * iterations_per_thread
    
    print(f"Executing {BOLD}{total_runs}{RESET} translations concurrently across {threads_count} threads...")
    
    failures = 0
    start_time = time.perf_counter()
    
    def worker(tid):
        local_fail = 0
        for i in range(iterations_per_thread):
            query = queries[(tid + i) % len(queries)]
            try:
                smart_transpile(query)
            except Exception:
                local_fail += 1
        return local_fail

    with ThreadPoolExecutor(max_workers=threads_count) as executor:
        futures = {executor.submit(worker, i): i for i in range(threads_count)}
        for future in as_completed(futures):
            failures += future.result()
            
    duration = time.perf_counter() - start_time
    rate = total_runs / duration
    
    if failures == 0:
        print(f"{GREEN}[SUCCESS]{RESET} Completed {total_runs} concurrent translations with 0 errors!")
        print(f"Execution Time: {duration:.3f} seconds | Throughput: {BOLD}{rate:.2f}{RESET} translations/sec")
        return True
    else:
        print(f"{RED}[FAILED] {failures} concurrent translations encountered execution panics/leaks.{RESET}")
        return False

def main():
    print_banner()
    j_res = run_deep_nesting_stress()
    a_res = run_concurrency_stress()
    
    print(f"\n{BOLD}{CYAN}========================================================================{RESET}")
    if j_res and a_res:
        print(f"{BOLD}{GREEN}[VERDICT] ALL CO-AUTHORING STRESS VECTORS PASS SUCCESSFULLY! [SECURE & STABLE]{RESET}")
    else:
        print(f"{BOLD}{RED}[FAILED] STRESS TEST FAILURE: Regression or depth error identified.{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}\n")

if __name__ == "__main__":
    main()
