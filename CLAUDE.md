# CLAUDE.md — Navakanth's Context File

> Claude reads this file at the start of every session. No re-explaining needed.

---

## Who I Am

- **Name:** Navakanth Reddy Dumpa
- **Focus:** AI tools & automation + Personal knowledge systems
- **Stack:** Mixed / still learning — no fixed language, currently exploring Python, JS, and no-code tools
- **Platform:** Windows 11, working in bash via Claude Code CLI

---

## How I Work

- I learn by building — show me working examples, not just theory
- I want to understand the *why*, not just the *what* (teaching mode)
- Give full explanations and step-by-step breakdowns for complex things
- For quick tasks, be direct; for learning topics, go deep
- Don't skip steps — I'm building my knowledge base as I go

---

## My Obsidian Vault

- **Path:** `C:\Users\navka\OneDrive\Documents\Obsidian Vault\`
- **Structure:**
  ```
  00-Inbox/          ← all captures land here first
  01-Projects/
    AI-Automation/   ← AI tools, workflows, Claude experiments
    Personal-Knowledge/ ← learning notes, book notes, research
  02-Areas/          ← ongoing responsibilities
  03-Resources/      ← reference material, links, templates
  04-Archive/        ← completed/old notes
  ```
- When I ask Claude to save something to the vault, use this structure
- New captures always go to `00-Inbox/` first

---

## Active Projects

### 1. AI Tools & Automation
- Building AI-powered workflows using Claude Code
- Learning to connect tools: Claude + Obsidian + scripts
- Interested in prompt engineering, agent workflows, MCP servers

### 2. Personal Knowledge System
- Building a second brain in Obsidian
- Goal: capture ideas fast, organize later, retrieve easily
- Sources: YouTube videos, articles, personal experiments

---

## Preferences

| Thing | Preference |
|---|---|
| Response style | Detailed + teaching mode |
| Code | Always show full working code, not snippets |
| Explanations | Start with what it does, then how, then why |
| Vault captures | Include date, tags, and project link |
| File naming | `YYYY-MM-DD-kebab-case-title.md` |

---

## Capture Format

When saving a note to the vault, always use this template:

```markdown
---
date: YYYY-MM-DD
tags: [tag1, tag2]
project: "Project Name"
source: "URL or description"
---

# Title

## Key Idea
...

## Details
...

## Action / Next Steps
- [ ] ...
```

---

## Things Claude Should Always Do

- Read this file at session start — never ask me to re-explain my setup
- When touching the vault, always confirm the file path before writing
- Suggest tagging and linking notes to relevant projects
- If I share a YouTube URL, offer to create a vault note from it

---

## Things Claude Should Never Do

- Over-summarize — I read the output
- Add boilerplate comments to code I didn't ask for
- Ask clarifying questions for simple tasks — just do it
- Create files outside the vault structure without asking

---

---

## Git Push Standard Process

### Why pushes fail in remote sessions
Claude Code web sessions use a local git proxy that is provisioned read-only by default.
The `GITHUB_TOKEN` env var has zero OAuth scopes. Both `git push` and the GitHub MCP `push_files` tool return 403.

### One-time fix (do this once)
1. Go to github.com → Settings → Developer Settings → Fine-grained tokens
2. Create a token: repo = `navakanth1984/Fabric-Frontier`, permission = **Contents: Read and write**
3. In the Claude Code web session environment settings, add: `GITHUB_TOKEN=<token>`

### How it works after setup
- The stop hook (`.claude/hooks/stop-save-memory.sh`) auto-wires the git remote using `GITHUB_TOKEN` and pushes any unpushed commits on every agent stop.
- The session-start hook (`.claude/hooks/session-start.sh`) can be run manually to verify access: `bash .claude/hooks/session-start.sh`
- The `/ship` command also triggers the same remote-wiring before pushing.

### Debugging push failures
```bash
bash .claude/hooks/session-start.sh   # shows push access status
git remote -v                          # check remote URL
echo $GITHUB_TOKEN | head -c 20         # confirm token is set
```

---

*Last updated: 2026-06-05*
