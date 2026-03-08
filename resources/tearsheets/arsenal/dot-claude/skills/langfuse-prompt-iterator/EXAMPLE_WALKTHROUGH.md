# Example Walkthrough: Iterating on a Journal Prompt

This walkthrough demonstrates the complete iteration workflow using the `journal_agent` prompt as an example.

## Scenario

You notice that the journal agent's responses aren't empathetic enough. Users report feeling judged rather than supported. You want to iterate on the prompt to make it more warm and compassionate.

## Step-by-Step Process

### Phase 1: Setup

**User:** "The journal_agent prompt isn't working right - it's not empathetic enough"

**Claude activates this skill and asks:**

```
Which environment should we pull from?
1. staging (default)
2. production

Do you want to work from a specific tag/label? (production/development/staging/etc.)
```

**User:** "Let's use staging, production label"

**Claude fetches the prompt:**
```bash
cd .claude/skills/langfuse-prompt-viewer
uv run python refresh_prompt_cache.py journal_agent
```

**Claude investigates codebase usage:**
```bash
# Finds where prompt is called
grep -r "journal_agent" api/src --include="*.py"

# Discovers it's called in:
# api/src/message_processing/routing/journal_flow_agent.py
```

**Claude reads the usage and identifies context_params:**
- `journey_theme` - Current journaling theme
- `journey_week` - Which week of the journey
- `prompt_number` - Current prompt number
- `total_responses_received` - User engagement
- `recent_messages` - Conversation history

**Claude asks:**
```
What are the goals for improving this prompt?
- Fix specific incorrect behavior (describe the issue)
- Improve tone/style (what direction?)
- Add new capabilities (what should it handle?)
```

**User:** "Make it more empathetic and less judgmental. Should feel like talking to a supportive friend, not a therapist."

### Phase 2: Establish Baseline

**Claude asks:**
```
Do you have a Langfuse trace ID that demonstrates the problem?
```

**User:** "Yes, trace ID: db29520b-9acb-4af9-a7a0-1aa005eb7b24"

**Claude fetches trace:**
```bash
cd .claude/skills/langfuse-prompt-viewer
uv run python fetch_trace.py db29520b-9acb-4af9-a7a0-1aa005eb7b24
```

**Claude extracts from trace:**
- User's journal entry: "I had a fight with my partner today and I'm feeling really low"
- Original response: "It's important to reflect on what led to the conflict. What patterns do you notice?"
- Issue: Too clinical, not warm

**Claude creates test case:**
```bash
cd .claude/skills/langfuse-prompt-iterator
uv run python setup_test_case.py journal_agent --from-trace db29520b-9acb-4af9-a7a0-1aa005eb7b24
```

This creates: `docs/prompt_test_cases/test_case_trace_db29520b.json`

**Claude runs baseline:**
```bash
uv run python test_prompt.py journal_agent docs/prompt_test_cases/test_case_trace_db29520b.json --baseline
```

**Output:**
```
✅ Test completed successfully
   Trace ID: xyz789
   Prompt Version: 3

OUTPUT:
It's important to reflect on what led to the conflict. What patterns do you notice in how you and your partner communicate during disagreements?
```

**Milestone 1 Achieved:** Reproducible test case established!

### Phase 3: Iterative Refinement - Round 1

**Claude shows user:**
```
Here's the baseline output:
"It's important to reflect on what led to the conflict. What patterns do you notice in how you and your partner communicate during disagreements?"

What do you see wrong with this output?
```

**User:** "It's too analytical. Doesn't acknowledge the emotional pain first. Jumps straight to analysis."

**Claude analyzes the prompt:**
```markdown
Current prompt (docs/cached_prompts/journal_agent_production.txt):

You are a journaling coach helping users with self-reflection.

Core principles:
- Provide supportive, non-judgmental guidance
- Encourage deeper exploration of thoughts and feelings
- Use "coach" terminology (never "therapist")

Your responses should:
- Acknowledge what the user shared
- Validate their experience        ← This exists but isn't strong enough
- Gently guide toward insight
- Ask thoughtful follow-up questions
```

**Claude suggests:**
```
Based on your feedback, here are 3 options:

**Option 1: Lead with Emotional Validation**
- What: Add explicit instruction to FIRST validate emotions before any analysis
- Why: Ensures empathy comes before coaching
- Risk: Might make responses longer

**Option 2: Add Warmth to Tone**
- What: Modify language guidelines to be more conversational and warm
- Why: Changes overall tone without restructuring
- Risk: Less specific about what changed

**Option 3: Provide Example Responses**
- What: Add examples showing good empathetic responses
- Why: Model behavior explicitly for the LLM
- Risk: Examples might constrain creativity

Which option do you prefer?
```

**User:** "Option 1 - let's make emotional validation explicit and first"

**Claude edits the prompt:**
```markdown
Your responses should:
1. FIRST: Acknowledge their emotional state with warmth and compassion
   - Start with genuine empathy ("That sounds really hard" / "I hear how painful this is")
   - Validate their feelings as understandable and normal
2. THEN: Gently guide toward insight
   - Ask thoughtful follow-up questions
   - Encourage deeper exploration
```

**Claude shows diff:**
```diff
  Your responses should:
- - Acknowledge what the user shared
- - Validate their experience
+ 1. FIRST: Acknowledge their emotional state with warmth and compassion
+    - Start with genuine empathy ("That sounds really hard" / "I hear how painful this is")
+    - Validate their feelings as understandable and normal
+ 2. THEN: Gently guide toward insight
  - Gently guide toward insight
  - Ask thoughtful follow-up questions
```

**Claude asks:** "Does this change look correct?"

**User:** "Yes, perfect!"

**Claude pushes update:**
```bash
cd .claude/skills/update-langfuse-staging-server-prompt
uv run python push_to_staging.py journal_agent
```

```
✅ Successfully pushed prompt to STAGING!
  Prompt Name: journal_agent
  Version: 4
  View in Langfuse: https://langfuse.staging.cncorp.io/...
```

**Claude re-runs test:**
```bash
cd .claude/skills/langfuse-prompt-iterator
uv run python test_prompt.py journal_agent docs/prompt_test_cases/test_case_trace_db29520b.json --version 4
```

**New Output:**
```
I hear how painful that must be - fights with our partners can leave us feeling really low and disconnected. It's completely understandable to feel this way after a conflict.

As you sit with these feelings, what do you notice about what happened today? What might help you process this experience?
```

**Claude shows comparison:**
```
BEFORE (v3):
"It's important to reflect on what led to the conflict. What patterns do you notice?"

AFTER (v4):
"I hear how painful that must be - fights with our partners can leave us feeling really low and disconnected. It's completely understandable to feel this way after a conflict.

As you sit with these feelings, what do you notice about what happened today? What might help you process this experience?"

How does this look? Are we closer to the goal?
```

**User:** "Much better! But the second part still feels a bit formal with 'As you sit with these feelings'. Can we make that more casual?"

### Phase 3: Iterative Refinement - Round 2

**Claude focuses on that section:**
```
You mentioned the phrase "As you sit with these feelings" feels formal. Here are options for that specific section:

**Option 1: More Conversational**
- Change to: "When you think about what happened today, what stands out to you?"
- Why: Simpler, more natural phrasing
- Risk: Loses the mindfulness framing

**Option 2: Friend-like Check-in**
- Change to: "What's going through your mind about it now?"
- Why: Very casual, like a friend asking
- Risk: Maybe too casual, less coaching-oriented

Which direction feels right?
```

**User:** "Option 1 - keep it warm but still slightly structured"

**Claude makes the change, pushes v5, re-runs test:**

**Final Output (v5):**
```
I hear how painful that must be - fights with our partners can leave us feeling really low and disconnected. It's completely understandable to feel this way after a conflict.

When you think about what happened today, what stands out to you? What might help you process this experience?
```

**User:** "Perfect! That's exactly the tone I wanted."

### Phase 4: Bulk Testing

**Claude suggests:**
```
Great! Would you like me to run this prompt 5 times with the same input to check consistency?
```

**User:** "Yes please"

**Claude runs bulk test:**
```bash
uv run python bulk_test_runner.py journal_agent docs/prompt_test_cases/test_case_trace_db29520b.json --runs 5
```

**Results show:**
- All 5 outputs maintain empathetic tone
- Slight variations in wording but consistent warmth
- All avoid jumping to analysis without validation

**Claude:** "All 5 runs maintain the warm, empathetic tone. Ready to promote to production?"

**User:** "Yes!"

**Claude guides:**
```
To promote to production:
1. Go to Langfuse UI: https://langfuse.staging.cncorp.io/.../prompts/journal_agent
2. Find version 5
3. Manually add 'production' label
4. Or push directly to production server (requires confirmation):
   cd .claude/skills/update-langfuse-staging-server-prompt
   uv run python push_to_staging.py journal_agent --production
```

## Summary

**What we accomplished:**
- ✅ Identified specific empathy issue in prompt
- ✅ Created reproducible test case from real trace
- ✅ Iteratively refined prompt through 2 rounds
- ✅ Validated consistency with bulk testing
- ✅ Ready for production deployment

**Versions created:**
- v3: Baseline (too analytical)
- v4: Added emotional validation (better, but formal)
- v5: Made language more conversational (perfect!)

**Test artifacts created:**
- Test case: `docs/prompt_test_cases/test_case_trace_db29520b.json`
- Baseline result: `docs/prompt_test_results/test_case_trace_db29520b_baseline_*.json`
- v4 result: `docs/prompt_test_results/test_case_trace_db29520b_v4_*.json`
- v5 result: `docs/prompt_test_results/test_case_trace_db29520b_v5_*.json`
- Bulk test: `docs/prompt_test_results/bulk_results_journal_agent_*.md`
