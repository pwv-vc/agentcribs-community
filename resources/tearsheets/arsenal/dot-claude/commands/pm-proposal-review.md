---
description: Review feature proposal with data validation and infrastructure analysis
---

# PM Proposal Review Command

**Purpose:** Add critical review comments to feature proposals, validating data support and infrastructure design.

## Usage

```bash
# Review a specific proposal
/pm-proposal-review user-feedback-2025-11-18

# Search and review
/pm-proposal-review "direct suggestions"
```

## Workflow

### Step 1: Find Proposal

Search `docs/temp/proposals/` for the proposal file:
- **If no filename provided:** Auto-select the most recent proposal (by modification time)
  ```bash
  ls -t docs/temp/proposals/*.md | head -1
  ```
- **If exact filename provided:** Use `{topic}-YYYY-MM-DD.md`
- **If search term provided:** Find matching proposal by content/title
- **If multiple matches:** Ask user to clarify

### Step 2: Read Proposal

Read the proposal to understand:
- **User Insight:** What data/behavior justifies it?
- **Infrastructure:** What systems will change?
- **The Change:** What will be built?
- **User Outcome:** Expected impact

### Step 3: Data Validation (Use sql-reader skill)

**Question 1: Does the data support the claimed impact?**

Validate each data claim in the proposal:
1. **Verify metrics cited:** Re-query the database to confirm numbers
   - Example: "All 5 Loved reactions went to scripts" → Query reactions to verify
2. **Check assumptions:** Are usage patterns as described?
   - Example: "Users get scripts in 3-5 messages" → Query message counts in relevant conversations
3. **Validate impact projections:** Are they realistic?
   - Example: "50% reduction in messages" → Check current baseline data

**Use sql-reader skill:**
```bash
# Example queries to run
arsenal/dot-claude/skills/sql-reader/connect.sh "
-- Verify reaction patterns
SELECT ... FROM message WHERE ...
"

# Check conversation patterns
arsenal/dot-claude/skills/sql-reader/connect.sh "
-- Analyze message counts
SELECT ... FROM message WHERE ...
"
```

**Output for Question 1:**
- ✅ **Supported:** List confirmed data points
- ⚠️ **Questionable:** List assumptions that need validation
- ❌ **Contradicted:** List claims that don't match data

### Step 4: Infrastructure Brittleness Analysis

**Question 2: Is the infrastructure design brittle?**

Analyze the proposed infrastructure changes for brittleness:

**Brittleness indicators:**
- ❌ Hard-coded patterns (e.g., "if message contains 'help me'...")
- ❌ Single point of failure (e.g., one prompt handles all cases)
- ❌ No fallback logic (e.g., what if detection fails?)
- ❌ Assumes user behavior (e.g., "users will always select an option")
- ❌ No error handling for edge cases

**AI/LLM-Specific Brittleness (RED FLAGS):**
- ❌ **Regex/keyword detection for semantic intent** (use LLM classification instead)
- ❌ **Hard-coded prompts in code** (use Langfuse for iteration)
- ❌ **No confidence scoring** on LLM decisions (can't detect uncertainty)
- ❌ **Single-shot prompts** for complex decisions (use chain-of-thought or structured outputs)
- ❌ **No few-shot examples** in prompts (LLMs need examples to understand edge cases)
- ❌ **Brittle output parsing** (use OpenAI structured outputs / JSON mode)

**Robustness indicators:**
- ✅ Pattern detection with confidence scoring
- ✅ Graceful degradation (falls back to existing behavior)
- ✅ Multiple prompts for different scenarios
- ✅ User can exit/override the flow
- ✅ Error handling and logging

**AI/LLM-Specific Robustness (BEST PRACTICES):**
- ✅ **LLM-based intent classification** (few-shot examples in prompt)
- ✅ **Structured outputs** (OpenAI JSON schema for reliable parsing)
- ✅ **Chain-of-thought reasoning** (LLM explains its decision)
- ✅ **Confidence scoring** (LLM rates certainty 0-1)
- ✅ **Prompt versioning** (Langfuse tracks iterations, A/B tests)
- ✅ **Fallback prompts** (if primary fails, use simpler backup)
- ✅ **Context window management** (handles long conversations)

**Review process:**
1. List each infrastructure component from proposal
2. Identify potential failure modes
3. Check if design handles edge cases
4. Assess impact if component fails

**Output for Question 2:**
- **Brittleness Score:** Low/Medium/High
- **Failure Modes:** List potential breaking points
- **Mitigation:** Suggestions to make design more robust

### Step 5: Infrastructure Extensibility Analysis

**Question 3: Is the infrastructure design extensible/scalable?**

Analyze how easily the design can support future features:

**Extensibility indicators:**
- ✅ Modular design (components can be swapped/extended)
- ✅ Configuration-driven (easy to add new patterns/prompts)
- ✅ Reusable components (can be used by other features)
- ✅ Clear interfaces/contracts
- ✅ Supports A/B testing and experimentation

**Scalability indicators:**
- ✅ Performance considerations addressed
- ✅ Works with increasing data volume
- ✅ No tight coupling between components
- ✅ Easy to add new option types/formats

**Review process:**
1. Identify future feature requests this could enable
2. Check if new scenarios require infrastructure changes
3. Assess coupling between proposed components
4. Evaluate configuration vs. code changes needed

**Output for Question 3:**
- **Extensibility Score:** Low/Medium/High
- **Future Features Enabled:** What this unlocks
- **Limitations:** What would require re-architecture
- **Recommendations:** How to improve extensibility

### Step 6: Add Review to Proposal

Append concise review (≤100 words) to the bottom of the proposal file:

```markdown
{original proposal content}

---

## PM REVIEW ({YYYY-MM-DD})

**Data Support:** {Strong/Okay/Weak/Very Weak} - {1 sentence validation summary}

**Brittleness:** {Strong/Okay/Weak/Very Weak} - {1 sentence on key risks}

**Extensibility:** {Strong/Okay/Weak/Very Weak} - {1 sentence on future capabilities}
```

**Total: ≤75 words. Be specific and actionable. No recommendation on whether to implement.**

### Step 7: Output Summary

```
✅ Review complete: {proposal file}

📊 Data Support: {Strong/Okay/Weak/Very Weak}
🏗️ Brittleness: {Strong/Okay/Weak/Very Weak}
📈 Extensibility: {Strong/Okay/Weak/Very Weak}

📄 Updated: docs/temp/proposals/{filename}
```

## Example Usage

```bash
$ /pm-proposal-review user-feedback-2025-11-18

Reading proposal: docs/temp/proposals/user-feedback-2025-11-18.md

Using sql-reader skill to validate data claims...
[Queries reactions, message patterns, conversation flows]

Analyzing infrastructure design...
[Reviews: intervention_logic.py, langfuse_client.py, response_generator.py, person_facts.py]

✅ Review complete: user-feedback-2025-11-18.md

📊 Data Support: STRONG (95% of claims validated)
🏗️ Brittleness: MEDIUM (needs fallback logic)
📈 Extensibility: HIGH (modular design, easy to add options)

💡 Overall: Approve with mitigations (add error handling)

📄 Updated: docs/temp/proposals/user-feedback-2025-11-18.md
```

## Skills Used

1. **sql-reader** - Validate data claims against production database
2. **product-analytics** (optional) - Deep analysis of usage patterns
3. **Code review** - Analyze infrastructure design for brittleness/extensibility

## Notes

- Review is prepended to proposal (original content preserved)
- Multiple reviews accumulate (shows evolution of thinking)
- Data validation is critical - re-run queries to confirm claims
- Infrastructure analysis requires understanding of codebase architecture
- Be specific with recommendations (not just "needs improvement")
