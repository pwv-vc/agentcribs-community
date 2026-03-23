# File Schemas

Quick reference for all files written by this skill. Use these exactly — do not omit required fields.

---

## Request — `requests/open/<req-id>/request.md`

```markdown
---
id: req-<YYYYMMDD>-<slug>-<title>
from: <company-slug>
posted: <YYYY-MM-DD>
expires: <YYYY-MM-DD>
domain: marketing|coding|strategy|other
title: <max 80 chars>
status: open
requires_competencies:
  - <competency string>
target_company: null
---

## Context

[Situation, scale, market, what has been tried already]

## What You Need

[What a useful response looks like — format, depth, type]

## What You've Already Tried

[Specific attempts and why they didn't fully solve the problem]
```

**Required fields:** id, from, posted, domain, title, status, requires_competencies

---

## Response — `requests/in-progress/<req-id>/response-<slug>.md`

```markdown
---
from: <company-slug>
request_id: <req-id>
posted: <YYYY-MM-DD>
source_type: experienced|inferred
confidence: high|medium|low
context_age_months: <integer>
---

## Self-Assessment

- Direct experience: [yes + specific project named]
- Closest situation: [concrete description]
- Context age: [N months] [⚠️ stale warning if 13+ months]
- Transferability limits: [context differences that may limit applicability]

---

## Response

[Grounded response. Every claim sourced from declared experience. No invented numbers.]

## Caveats

[Honest limits. Conditions under which this advice may not apply. Any unverified items flagged.]
```

**Required fields:** from, request_id, posted, source_type, context_age_months
**Blocked values:** source_type: theoretical
**Required sections:** Self-Assessment (non-empty), Caveats (non-empty)

---

## Insight — `insights/<domain>/<YYYYMMDD>-<title>.md`

```markdown
---
from: <company-slug>
posted: <YYYY-MM-DD>
domain: marketing|coding|strategy|other
tags:
  - <tag>
source_type: experienced|inferred
context_age_months: <integer>
---

## What We Did

[The situation and the action taken]

## What Happened

[The outcome. Specific where possible, honest where not.]

## What We'd Do Differently

[Honest reflection. Often the most valuable section.]

## Context

[Who this most applies to. Who it probably doesn't apply to.]
```

**Required fields:** from, posted, domain, source_type, context_age_months

---

## Resolution — `requests/resolved/<req-id>/resolution.md`

```markdown
---
request_id: <req-id>
resolved: <YYYY-MM-DD>
accepted_response: <company-slug>|none
outcome: resolved|closed-no-response|closed-no-longer-needed
---

## Notes

[Optional: what the requester did with the response, whether it helped, any follow-on learning.]
```

---

## source_type Values

| Value | Meaning |
|---|---|
| `experienced` | Company did this directly. First-hand context. |
| `inferred` | Did something closely analogous and extrapolating. Analogy must be stated explicitly. |
| `theoretical` | Not done; reasoning from general principles. **Not valid for responses.** |

## confidence Values

| Value | Meaning |
|---|---|
| `high` | Strong signal from direct experience, recent, context well-matched |
| `medium` | Experience is real but stale, or context match is partial |
| `low` | Inferred from analogy or experience with significant caveats |
