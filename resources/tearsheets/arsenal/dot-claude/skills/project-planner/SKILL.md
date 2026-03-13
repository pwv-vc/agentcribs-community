---
name: project-planner
description: Use this skill when the user wants to plan a new project or feature implementation. This skill helps gather requirements through an iterative question-and-answer process, tracking decisions in a markdown file until a comprehensive specification is ready.
---

# Project Planner Skill

You are now in project planning mode. Your goal is to help the user create a comprehensive project specification through an iterative Q&A process.

## Workflow

1. **Initial Project Description**: The user will describe their project idea
2. **Create Planning Directory & Document**:
   - Derive a kebab-case project name from the user's description (e.g., "user-authentication", "payment-gateway")
   - Create directory `docs/specs/<project_name>/` if it doesn't exist
   - Create a markdown file named `PROJECT_PLAN.md` in this directory to track the planning process
3. **Iterative Planning Loop**: Follow this cycle until you have a complete specification:
   - Review the current state of the plan
   - Identify new questions that need answers
   - Identify questions that are no longer relevant (mark as closed)
   - Identify questions that have been answered and convert them to decisions
   - Ask the next most important question
   - Update the planning document with the user's response
   - Verify and confirm decisions made
4. **Final Review**: Once all questions are answered and you have a sufficiently detailed spec, present the final plan to the user for review

## Planning Document Structure

The `docs/specs/<project_name>/PROJECT_PLAN.md` file must maintain this structure:

```markdown
# Project Plan: [Project Name]

## Project Overview
[Brief description of the project]

## Decisions Made
[List of decisions with explanations. When a question is answered, move it here as a decision]

### Decision: [Topic]
**Decision**: [What was decided]
**Rationale**: [Why this decision was made based on the answers]
**Status**: ✅ Confirmed | ⏳ Pending Verification

## Open Questions
[Questions that still need answers, ordered by priority]

### Question: [Topic]
**Question**: [The specific question]
**Priority**: High | Medium | Low
**Context**: [Why this question matters]

## Closed Questions
[Questions that are no longer relevant]

### Question: [Topic]
**Question**: [The question]
**Reason for Closing**: [Why this question is no longer relevant]

## Technical Specification
[This section grows as decisions are made. Include:]
- Architecture & Design
- Technology Stack
- Data Models
- APIs & Interfaces
- Security & Authentication
- Testing Strategy
- Deployment Strategy
- Any other relevant technical details

## Implementation Roadmap
[High-level phases or milestones for implementation]

## Success Criteria
[How we'll know the project is complete and successful]
```

## Guidelines

1. **Always update the markdown file** after each interaction using the Write or Edit tools
2. **Ask one focused question at a time** - don't overwhelm the user
3. **Verify decisions** - when you convert a question to a decision, confirm with the user that you understood correctly
4. **Prioritize questions** - ask the most foundational/architectural questions first
5. **Be thorough** - continue until you can write a spec detailed enough for an independent agent to implement
6. **Track everything** - every answer should update the planning document
7. **Use the TodoWrite tool** to track your progress through the planning process

## Completion Criteria

You have a complete specification when:
- All open questions have been answered
- Key architectural decisions are documented
- Technical requirements are clear and detailed
- Implementation approach is well-defined
- Success criteria are established
- An independent developer/agent could implement the project from the spec

## Example Question Flow

1. Start with high-level architecture questions (e.g., "What type of application is this? Web, CLI, mobile?")
2. Move to technology stack questions (e.g., "What framework/language should we use?")
3. Ask about data and state management (e.g., "What data needs to be persisted?")
4. Cover integration points (e.g., "Does this integrate with external services?")
5. Address non-functional requirements (e.g., "What are the performance requirements?")
6. Clarify edge cases and error handling
7. Define testing and deployment strategies

## Important Notes

- The planning document is the source of truth for the entire planning session
- Every update should be written to the file immediately
- When converting questions to decisions, explain your reasoning clearly
- If the user's answer raises new questions, add them to the Open Questions section
- Keep the document well-organized and easy to read
