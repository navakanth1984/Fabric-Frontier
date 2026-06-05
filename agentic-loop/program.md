# Program Contract

Owner: `human`
Last updated: `2026-05-12`

## Objective

Maximize evaluation score on the locked evaluator while staying within all rules and constraints.

## Scalar Metric

- Primary metric name: `accuracy`
- Range: `0.0` to `1.0`
- Higher is better: `true`

## Non-Negotiable Rules

1. The agent may modify only `train.py`.
2. The agent must not access or modify `prepare.py` in production environments.
3. Every experiment must run under the same timeout budget.
4. Any score gain achieved by hardcoding benchmark answers is invalid.
5. A human review is required before promoting any winner.

## Constraints

- Runtime budget per experiment: `10` seconds
- Write scope: exactly one file (`train.py`)
- Output must remain deterministic for identical input
- No network access during evaluation

## Failure Conditions

- Timeout or runtime error returns a failing score.
- Any write outside allowed scope invalidates the run.
- Any non-deterministic behavior invalidates the run.

## Human Review Checklist

- Did score improve on locked eval?
- Did runtime stay within budget?
- Is code quality acceptable (no unnecessary bloat)?
- Does the change generalize beyond current eval cases?
- Are architecture and identity assumptions still correct?
