## Session Continuity Protocol (Cross-Tool)
All AI agents (Antigravity CLI, Antigravity IDE, Claude Code, etc.) MUST follow this protocol.

### On Session Start
When the user says "continue", "restart", "pick up", or "resume":
1. Read `obsidian-vault/Obsidian Vault/01-Projects/Antigravity Sessions/SESSION_REGISTRY.md`
2. List the **Active Sessions** table to the user
3. If only one active session exists, auto-resume it; otherwise ask which to resume
4. Read the linked handoff note for full context and follow its **Resume Instructions**

### On Session End
Before ending any session that involved code changes:
1. Create or update a handoff note using `_HANDOFF_TEMPLATE.md` in the same folder
2. Update `SESSION_REGISTRY.md` — add new sessions, move completed ones to the Completed table
3. Use naming: `S-{NNN}_{YYYY-MM-DD}_{slug}.md` (next ID is in the registry)

---

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
