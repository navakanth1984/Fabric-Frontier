# /ship

Stage all changes, write a commit message, commit, and push to the current branch.

## Steps

1. Run `git status` and `git diff --stat` to summarize what changed.
2. Draft a concise commit message (imperative mood, ≤ 72 chars subject).
3. `git add` only the relevant files (never `.env` or secrets).
4. `git commit -m "<message>"`.
5. `git push -u origin <current-branch>`.
6. Report the pushed commit SHA and branch name.

## Rules

- Never commit `.env`, `*.key`, or files matching `.gitignore`.
- Never force-push without explicit user confirmation.
- If push fails, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).
