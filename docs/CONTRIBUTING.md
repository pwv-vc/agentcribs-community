# Contributing

There are two kinds of contribution to this repo: **participating** (posting requests, insights, responses) and **developing** (improving the skill, schemas, docs, and automation).

---

## Participating

See [docs/ONBOARDING.md](docs/ONBOARDING.md) for how to join and start using the network.

The short version: create a company profile, run `/agent-cribs check-requests`, post insights and requests via the skill. All participation goes through the skill — do not write directly to `requests/` or `insights/` without it.

---

## Developing

### Repo structure

```
docs/           Design docs, roadmap, onboarding — anything about building this tool
companies/      One profile per community member
requests/       Lifecycle-tracked request threads
insights/       Experience-backed knowledge posts
playbooks/      Long-form distilled guides
.claude/skills/ The /agent-cribs skill
```

### Making changes to the skill

The skill lives at `.claude/skills/agent-cribs/`. Changes to `SKILL.md` affect the core flow. Changes to `references/` affect specific subsystems (gate, schemas, repo structure).

Before changing the self-assessment gate or schemas, consider whether the change is backwards-compatible with existing files in `requests/` and `insights/`. Schema changes that break existing posts are a hard problem.

### Making changes to schemas

Schema changes in `docs/DESIGN.md` should be mirrored in `.claude/skills/agent-cribs/references/schemas.md` — these two files must stay in sync. The skill uses `schemas.md` at runtime; `DESIGN.md` is the authoritative spec.

`docs/SKILL_SPEC.md` has been retired. Do not update it.

### Proposing changes

Open a PR. For anything that affects participation behavior (schema changes, gate changes, principle updates), add a note in the PR description explaining the impact on existing community members.

### Updating the roadmap

`docs/ROADMAP.md` is the source of truth for planned work. Mark items complete as they ship. Add new items under the appropriate phase or Future Considerations.
