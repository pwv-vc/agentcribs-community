# Arsenal — AgentCribs™ Tear Sheet
**Presenter:** Sam Odio (Wren / CNCorp)
**Session:** PWV AgentCribs™ Series, Feb 25, 2026
**Repo:** Private (DM Sam for access) — `git@github.com:cncorp/arsenal.git`

---

## Demo Video

<video src="arsenal-demo.mp4" controls width="100%"></video>

---

## Problem This Solves

* **Skill adherence**: Hash gates force Claude to follow the right skill for every task, eliminating skipped or freelanced workflows.
* **Context shuttle**: Arsenal gives Claude live access to your product's world — logs, DB, prompts, ads, user behavior — so you get answers, not suggestions.

> *"Before, I was a vehicle to shuttle context from the rest of the world to the language model to the developer. I underestimated the amount of overhead that created."* — Sam Odio

---

## What Setup Is This Designed For?

- **AI-native startups** using Claude Code as their primary dev environment
- **Stack:** Python backend, PostgreSQL/pgvector, LangFuse for prompt management, Docker, Meta Ads (optional)
- **Team size:** 2–10 engineers comfortable running Claude Code autonomously
- **Assumption:** Your infra is fully in code (IaC) — this is key for LLM-driven development
- **Not for:** Teams using pure Cursor/Copilot autocomplete or those not yet running Claude as an autonomous agent

---

## Dev Pain Before Arsenal

- Pasting error logs manually into Claude → getting generic, obvious answers
- No way to ask "what's happening in production right now?"
- Prompt changes in LangFuse required manual diffing and context-switching
- Facebook ads took a full-time designer + 1 month per campaign
- Code reviews were entirely manual
- No feedback loop connecting user behavior → product changes → validation

**Token economics:** 1 token on validation for every 5 on code. Arsenal's goal is to flip that to 5:1.

---

## Install / Usage
(request access to repo from Sam - sam@odio.dev)

```bash
# Add as a submodule
git submodule add git@github.com:cncorp/arsenal.git arsenal

# Install (idempotent — safe to re-run)
./arsenal/install.sh

# Optional: start Docker services (semantic search)
cd arsenal && docker-compose up -d
```

**What install does:**
- Symlinks `arsenal/dot-claude/` → `.claude/` in your project
- Symlinks `arsenal/pre-commit-scripts/` and `AGENTS.md`
- Installs Node.js dependencies (Playwright, etc.)
- Sets up `.env` from `.env.example`

**Required env vars:**
```
OPENAI_API_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=...
```

**After install, Claude Code automatically gets:**
- A bootstrap hook that fires every session: reads `getting-started` skill before any work begins
- Skill router that injects skill-checking instructions on every user message
- Manager review gate that blocks responses until a checklist token is included

---

## What You Get

### 🎯 Skills (mandatory workflows)
Skills are not optional — Arsenal enforces this via hooks. Claude **must** use the relevant skill if one exists.

| Skill | What it does |
|---|---|
| `test-runner` | 4-step mandatory test workflow after every code change |
| `langfuse-prompt-iterator` | Diff, test, and deploy prompt changes without leaving Claude |
| `onboarding-funnel-analyzer` | Queries DB to analyze user conversion behavior |
| `playwright-tester` | Browser automation and visual testing |
| `docker-log-debugger` | Searches container logs for errors |
| `manager-review` | Forces checklist review before finalizing any response |
| `user-segmentation` | Analyzes user behavior patterns |
| `couple-weekly-report` | (Wren-specific) Weekly relationship health report |

### 📋 Slash Commands
`/buildit`, `/planit`, `/plan-tdd`, `/implement-tdd`, `/review-code`, `/samreview`, `/daily-user-feedback`, `/product-insights`, `/spec-to-pr`, `/create-linear-ticket`, `/wdyt`, `/research`, and more.

### 🤖 Subagents (auto-invoked)
`pytest-test-reviewer`, `mypy-error-fixer`, `git-reader` (read-only), `task-complete-enforcer`

### 🔒 Hooks
- **Session start** — bootstraps Arsenal rules every session
- **Skill router** — checks skills index on every user message, injects routing instructions
- **Manager review gate** — blocks Claude responses that skip the review checklist (approval token required)

---

## 30-Second Demo

> *"Why did this error happen?"* → [pastes error log]

**Old world (plain Claude):** "One of your LLM calls hit the max completion tokens limit." (just restated the error)

**New world (Arsenal):** Pinpointed the exact Feb 26 13:17 UTC trace in LangFuse, showed the prompt had 11K tokens vs. a 512 completion limit, gave a risk assessment, proposed a fix, then implemented it — all in one turn.

> *"50 new users onboarded this week. Zero converted to couples."*
> *"The 0% conversion rate isn't a funnel problem to fix — it's the market telling you what the product is."*

Claude identified the core strategic problem, proposed two solutions, picked the winner from the data, wrote a spec, and updated all 150 LangFuse prompt templates — **live pivot of the company in one session**.

Also: generated 273 Facebook ad variants (images + copy) in ~15 minutes.

---

## Community Reactions (Feb 25 session)

- ~12 attendees writing code in fully automated fashion
- 4 already using OpenClaw
- 3 using 10+ Claude skills (one on Sam's team)
- Questions focused on: how validation pipeline was built, whether it's a standalone product, how the 40K CLAUDE.md is organized
- One attendee noted: *"the validation pipeline concept is a product by itself"*
- Strong interest in Arsenal repo access (Sam offered to share privately)

---

## Similar Tools the Community Mentioned

| Tool | Relationship |
|---|---|
| **Superpowers** (Jesse Vincent) | Arsenal was directly inspired by this. "Assume it's Superpowers." |
| **OpenClaw** | 4 community members using it; comparable agent orchestration layer |
| **LangFuse** | Arsenal wraps LangFuse for prompt debugging/iteration |
| **Linear** | Arsenal has Linear integration commands (`/create-linear-ticket`, `/linear-agent`) |
| **HumanLayer** | Mentioned in tool survey — similar human-in-the-loop concept |
| **Paired** | Closest competitor to Wren (couples app, few million downloads) |
