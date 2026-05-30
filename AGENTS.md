# AGENTS.md — Fabric-Frontier

> Microsoft Fabric training and course content repository

---

## Project Overview

Fabric-Frontier is a large HTML-based repository (~235 MB) housing course content,
labs, demos, and learning materials for Microsoft Fabric Data Engineering. It is
authored and maintained by an MCT (Microsoft Certified Trainer) for use in corporate
training, self-paced learning, and Microsoft Learning Partner delivery.

This is **content-first** — structure, accuracy, and learner experience matter more
than code elegance.

---

## Intended Audience

- Microsoft Learning Partner facilitators (NIIT, Koenig, Vinsys, Simplilearn)
- Corporate IT and data teams learning Microsoft Fabric
- Individual certification candidates (DP-700, DP-600, PL-300)

---

## Content Domains Covered

Based on Microsoft Fabric exam objectives:
- Lakehouse architecture and Delta Lake
- Data Factory pipelines and dataflows
- Spark notebooks and SQL analytics endpoints
- Power BI semantic models and Direct Lake mode
- Microsoft Fabric Data Warehouse
- Real-Time Intelligence (Eventhouse, KQL databases)
- Data Activator and Reflex
- Microsoft Fabric governance and admin
- Certification prep: DP-700, DP-600, PL-300

---

## Tech Stack

- **Primary format**: HTML (hand-authored or generated course pages)
- **Assets**: Images, diagrams, screenshots, lab guides
- **No build system** — files are served directly or packaged for delivery

---

## Content Standards

### Accuracy
- All technical claims must match the **latest Microsoft Learn documentation**.
- Fabric is fast-moving — flag any content referencing Preview features vs GA.
- When in doubt, link to: `https://learn.microsoft.com/fabric`

### Terminology (always use current terms)
- **Lakeflow** (not "Dataflows Gen3" for pipeline orchestration)
- **Declarative Automation Bundles** (DABs) — new automation packaging
- **Unity Catalog ABAC** — attribute-based access control in Fabric
- **Liquid clustering** (not manual `OPTIMIZE` partitioning)
- **Deletion vectors** (not file-level deletes in Delta)
- **Direct Lake mode** (not "Import" or "DirectQuery" for Fabric semantic models)

### HTML Conventions
- Use semantic HTML5 (`<section>`, `<article>`, `<aside>`, `<figure>`).
- All images need `alt` text with technical descriptions.
- Lab steps must be numbered `<ol>` lists, never `<ul>`.
- Code samples inside `<pre><code class="language-xxx">` blocks.
- KQL samples: `language-kql`. T-SQL: `language-sql`. Python: `language-python`.

### Lab Guides
- Every lab must have: **Objective**, **Prerequisites**, **Steps**, **Validation**, **Cleanup**.
- Cleanup steps are mandatory — learners share tenants; always include workspace/resource deletion.
- Screenshots must be current (retake when Fabric UI changes).

---

## File Organisation

```
/                 Root — index pages, navigation
/labs/            Hands-on lab HTML guides
/slides/          Slide companion pages or exported HTML decks
/demos/           Instructor demo scripts
/assessments/     Quiz and knowledge check pages
/assets/          Images, icons, CSS, JS
/resources/       Reference PDFs, cheat sheets, study guides
```

---

## Jules-Specific Guidance

- This repo is **content-heavy, not code-heavy**. Prefer content edits over structural refactors.
- When adding new labs, follow the existing lab template structure exactly.
- When updating terminology (e.g., Preview → GA, renamed features), do a global find-replace
  across all `.html` files, not just the currently open file.
- Do not introduce JavaScript frameworks or build tooling — keep it static HTML.
- The repo is large (~235 MB); avoid git operations that re-process all assets.
- When creating new content, check `https://learn.microsoft.com/fabric` for the latest UI state.
- Prioritise DP-700 and DP-600 exam objective coverage — these are the active beta exams.
