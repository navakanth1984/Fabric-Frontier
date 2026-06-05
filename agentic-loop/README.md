# Agentic Loop Starter (Software 3.0 Discipline)

This folder is a minimal, opinionated scaffold for running AutoResearch-style optimization loops
with strict safety boundaries:

- `program.md` is the human-owned contract.
- `train.py` is the only agent-modifiable file.
- `prepare.py` is the locked evaluator with timeout + scalar score.
- `run_loop.py` runs the loop, snapshots winners, and auto-reverts regressions.

## Why this structure

The loop only works when:

- Success is a single scalar metric.
- Every run has the same time budget.
- The agent cannot rewrite or bypass the evaluator.
- Human review gates promotions even when the score improves.

## Quick start

```powershell
cd "C:\\Users\\navka\\navakanth001\\agentic-loop"
py -3 run_loop.py --init
```

Then iterate:

1. Modify `train.py` only.
2. Run:

```powershell
py -3 run_loop.py
```

Behavior:

- If score improves: winner is snapshotted in `.autoresearch\best_train.py`.
- If score regresses or fails: `train.py` is reset to the last winner.

## Optional winner commit

```powershell
py -3 run_loop.py --commit-winner
```

## Important production note

This starter keeps `prepare.py` in the same folder so you can inspect and adapt it.
For real deployments, treat evaluator logic, hidden datasets, and private tests as restricted assets
in a separate boundary the agent cannot read or write.

