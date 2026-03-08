# Create Linear Ticket Command

Create a well-structured Linear ticket for implementation tasks following our team's preferred format.

## Ticket Structure Guidelines

### 1. Title
- Clear, action-oriented title describing what will be implemented
- Include phase number if part of a multi-phase project

### 2. Objective
- One clear paragraph stating what will be implemented and why

### 3. Problem Being Solved
- Bullet points listing the specific issues this implementation addresses
- Focus on concrete technical problems, not abstract concepts

### 4. Solution Approach
- Brief technical description of the implementation approach
- Focus on the "how" at a high level

### 5. Implementation Tasks

**IMPORTANT: Always start with Step 0: Testing (TDD approach)**

Structure as numbered steps (not days or timeframes):
- **Step 0: Testing** - Write tests first
  - Unit tests for new functionality
  - Integration tests for system interactions
- **Step 1: Core Logic** - Main implementation
- **Step 2: Integration** - Connect with existing systems
- **Step 3: Observability** - Metrics, logging, feature flags
- **Step 4: Validation** - Dev testing and verification

Each step should have concrete, checkable subtasks using `- [ ]` format.

### 6. Success Metrics
- Specific, measurable outcomes
- Performance targets where applicable
- No subjective metrics

### 7. Deployment Plan
Keep it simple:
1. Deploy to staging with feature flag
2. Validate with test data
3. Ship to production with feature flag enabled

**DO NOT include:**
- Gradual rollout percentages
- Complex rollout strategies
- Load testing scenarios (unless specifically requested)

### 8. Documentation
- Attach planning docs and specs as Linear attachments
- DO NOT reference repo paths for specs (specs live in Linear, not the repo)
- Keep references minimal and relevant

### 9. Notes
- Brief context about broader project if applicable
- Key technical constraints or considerations
- Feature flag rollback capability

## Example Ticket Structure

```markdown
## Objective
[One paragraph describing what and why]

## Problem Being Solved
* [Specific technical problem 1]
* [Specific technical problem 2]

## Solution Approach
[Brief technical approach description]

## Implementation Tasks

### Step 0: Testing
- [ ] Unit tests for [core functionality]
- [ ] Integration tests for [system interactions]

### Step 1: Core Logic
- [ ] [Main implementation task 1]
- [ ] [Main implementation task 2]

### Step 2: Integration
- [ ] [Integration task 1]
- [ ] [Integration task 2]

### Step 3: Observability
- [ ] Add metrics: [list key metrics]
- [ ] Implement feature flag
- [ ] Add logging for [key events]

### Step 4: Validation
- [ ] Dev testing locally
- [ ] Verify [key behavior]
- [ ] Validate [performance requirement]

## Success Metrics
* [Specific measurable outcome 1]
* [Specific measurable outcome 2]

## Deployment Plan
1. Deploy to staging with feature flag
2. Validate with test data
3. Ship to production with feature flag enabled

## Notes
* [Key context or constraints]
* Feature flag allows quick rollback if needed
```

## When Creating Tickets

1. **Always start with tests** (Step 0)
2. **Use steps, not time-based organization**
3. **Keep deployment simple** - no complex rollout strategies
4. **Focus on implementation tasks** - avoid project management overhead
5. **Include feature flags** for safe rollback
6. **Minimize documentation references** - only what's essential

## Linear API Parameters to Use

When calling `mcp__linear__create_issue`:
- Set clear `title`
- Include `parentId` if it's a subtask
- Set appropriate `estimate` (points, not days)
- Add relevant `labels` (typically just "Engineering")
- Use `description` with the structured format above

## Important: Documentation Strategy

**Specs are created in `docs/specs` for working purposes but must ALSO be attached to Linear tickets for permanence.**

### Workflow for Specifications:

1. **Create specs as markdown files** in `docs/specs/` (organized by feature/project)
   - These are working documents during planning and research
   - They will NOT be merged to main (branch-specific artifacts)

2. **Attach specs to Linear tickets**
   - Copy the full content into the Linear ticket description, OR
   - Mention in the ticket that the spec document should be attached as a file
   - This ensures specs are available when working on implementation in new branches

3. **DO NOT reference repo paths** in Linear tickets
   - Don't use paths like `/docs/specs/...` in ticket descriptions
   - The Linear attachment IS the source of truth for future work

### Why This Approach:
- **During planning**: Specs in `docs/specs` are convenient for iteration and review
- **During implementation**: Specs from Linear can be pulled into any branch
- **Long-term**: Linear maintains the historical record, repo stays clean

The permanent repo contains:
- Code and tests
- Essential documentation (README, API docs, etc.)
- Configuration files

Planning artifacts (specs, research docs) are temporary in the repo but permanent in Linear.