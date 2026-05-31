## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

---

## Usage Limit & Context Optimization Protocol (ULCOP v2.1)

### ULCOP Decision Order
To prevent optimization from leading to incomplete or incorrect implementations, all operations must be evaluated using this priority stack:
1. **Safety**: Ensure operations do not violate safety boundaries, create security vulnerabilities, or risk data loss.
2. **Correctness**: Maintain absolute code correctness, logic fidelity, and alignment with specifications.
3. **Task Completion**: Achieve all objectives fully, avoiding half-baked edits or skipping necessary details.
4. **Context Efficiency**: Keep the context window compact using smart truncation, graph-first lookups, and timely subagent delegation.
5. **Response Brevity**: Keep chat responses clean and focused, adjusting depth to match task complexity.

*If a higher-priority objective conflicts with a lower-priority objective, the higher-priority objective wins.*

### Core Operational Principles
- **Decision Hierarchy Override**: Apply ULCOP principles by default, unless doing so would reduce safety, correctness, or task completion quality.
- **Graph-First Search Preference**: Prefer graph-based discovery (`graphify`) and targeted searches when available. Use broader search techniques when required for correctness or completeness.
- **Reasoning Cost Management**: 
  1. **Complete Over Partial Investigations**: Prefer one thorough, high-fidelity investigation over multiple partial investigations.
  2. **No Redundant Planning**: Avoid repeated planning loops; formulate and execute a clean plan.
  3. **Evidence Reuse**: Reuse previously gathered evidence, logs, and files; do not re-read unmodified files.
  4. **Consolidated Edits**: Consolidate related code edits into a single multi-replace block.
  5. **No Redundant Subagents**: Avoid spawning duplicate subagents; consolidate tasks when executing background operations.
  6. **Targeted Verification**: Prefer targeted verification over running full-system tests unnecessarily.
- **Heuristic Delegation**: Prefer delegation when it improves context efficiency without reducing correctness or completeness, and when the expected investigation cost materially exceeds the cost of delegation and isolation.
- **Contextual Response**: Match explanation depth to task complexity and user expectations.

---

## Pre-commit hook scope
The Pyrefly type-check hook runs workspace-wide. When staging only
nthdimensionacademy/ frontend assets (HTML/CSS/JS), it is acceptable
to run `git commit --no-verify` ONLY IF:
- All staged files are confirmed non-Python
- The reason for hook failure is documented in the commit message body
Do NOT use --no-verify for Python file commits. Fix the dependency
issue in AutoGrade_Backend and dead_loop_trailer before the next
Python commit on any branch.

---

## Large Asset Tracking & Git LFS
To prevent repository bloating and push failures:
- Any single binary asset (e.g. `.mp4`, `.mov`, `.png`, `.jpeg`, `.zip`) with file size exceeding **50 MB** MUST be tracked using Git LFS (Large File Storage) instead of regular `git add`.
- Do not commit large generated media assets directly to standard Git history unless explicitly verified to be under the 50 MB threshold.

---

## Edit workflow — DELETE before INSERT
Before adding any new HTML element, CSS rule, or JS block that replaces
an existing one:
1. VIEW the full section (min 20 lines around the target).
2. Note the exact line numbers of ALL existing instances of that element.
3. DELETE the old instances first in one edit.
4. Verify deletion with Select-String before inserting the replacement.
Never use "append below" as an edit strategy for content that replaces
existing content. Append-without-delete has caused duplicate IDs,
duplicate nodes, duplicate tab buttons, and duplicate variable
declarations across multiple sessions.
