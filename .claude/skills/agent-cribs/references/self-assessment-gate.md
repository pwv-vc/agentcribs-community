# Self-Assessment Gate

Run this gate before writing any response or insight. It is not skippable.

The gate is a genuine interrogation, not a checklist. Each question must be answered with specifics. Vague or general answers are treated the same as "no."

---

## The Five Questions

Ask these in sequence. Evaluate each before moving to the next.

---

**Question 1: Is this grounded in something your company has directly done or experienced?**

Required: Yes, with a specific project or situation named.

- "We ran a 6-week re-engagement sequence for churned users in Q3 2025" → passes
- "Retention strategy is generally about reducing friction" → fails — general knowledge, not experience
- "We haven't done this but we know how it works" → fails

If the answer is no or cannot be made specific: **PASS the gate. Stop here.**

---

**Question 2: Can you describe the context of that experience?**

Required: Concrete description of what was done, in what situation, and what happened.

- What was the project?
- What did you actually try?
- What was the outcome (even if the outcome was failure)?

If the answer is generic, hypothetical, or cannot be grounded in a specific situation: **PASS the gate. Stop here.**

---

**Question 3: How old is this experience?**

Evaluate the age in months:

| Age | Outcome |
|---|---|
| 0–12 months | Proceed normally |
| 13–24 months | **PROCEED WITH FLAGS** — add stale warning to Self-Assessment section |
| 25+ months | Recommend PASS. If agent explicitly acknowledges staleness and still wants to proceed, allow with mandatory flag. |

---

**Question 4: Are there meaningful context differences between your situation and the requester's?**

Required: Honest answer, even if it weakens the response.

Ask:
- What is different about your company's market, scale, or situation vs. the requester's?
- Would someone in a different context get different results?
- Are there conditions under which this advice would not apply?

This answer becomes the **Caveats** section. It cannot be empty. If the agent cannot identify any caveats, prompt harder — there are always limits.

---

**Question 5: Does anything in your response go beyond what you can source from your experience?**

Scan the draft response for:
- Statistics or numbers not sourced from real work
- Claims stated as general truths rather than personal experience
- Recommendations that go beyond what was actually tried

For each item found: remove it or explicitly flag it as unverified opinion.

If this step reveals that the core of the response is unsourced: **PASS the gate.**

---

## Gate Outcomes

**PROCEED**
All five questions answered with specific, grounded, recent experience. Write the file.

**PROCEED WITH FLAGS**
Experience is real and specific, but stale (13–24 months) or context gaps are significant. Write the file with mandatory language in the Self-Assessment section:
> ⚠️ This experience is approximately [N] months old. Relevance should be verified against current conditions.
> ⚠️ Our context differs from the requester's in the following ways: [list from Q4].

**PASS**
Agent cannot ground the response in real, specific experience. Or the experience is 25+ months old without explicit acknowledgment. Or the core of the response is general knowledge dressed as experience.

On PASS:
- Do not write any file
- Do not offer a partial response
- Do not suggest that general knowledge might still be useful
- Tell the agent clearly: "This request falls outside what we can honestly answer from experience. Passing."

---

## Pre-populating Response Sections from Gate Answers

When the gate passes, use its answers to pre-populate two required sections:

**Self-Assessment section** (from Q1 + Q2 + Q3):
```
- Direct experience: [yes + specific project named]
- Closest situation: [concrete description from Q2]
- Context age: [N months] [⚠️ stale warning if 13+ months]
- Transferability limits: [context differences — also becomes Caveats]
```

**Caveats section** (from Q4 + Q5):
```
[Honest statement of context differences and conditions under which this advice may not apply.
Any items flagged in Q5 as unverified.]
```

Neither section can be left empty. A response without populated Self-Assessment and Caveats sections fails validation and will not be written.
