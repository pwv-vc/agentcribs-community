---
name: brainstorming
description: "INVOKE when user says: 'brainstorm', 'design this', 'help me think through', 'what should we build'. Collaborative idea-to-spec workflow."
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- **Run semantic-search to find existing similar implementations** before designing new ones:
  - `docker exec arsenal-semantic-search-cli code-search find "<feature concept>"`
  - Check if something similar already exists (DRY principle)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After the Design

**Documentation:**
- Create folder: `spec/YYYY-MM-DD-<project-name>/`
- Split design into phase files:
  - `00-overview.md` - Summary, key decisions, tech stack, links to phases
  - `01-<phase-name>.md` - First implementation phase
  - `02-<phase-name>.md` - Second phase
  - ... (one file per logical phase)
- Each phase file must include:
  - Overview of the phase
  - Technical details / code samples
  - Acceptance criteria checklist

**Implementation (if continuing):**
- Ask: "Ready to set up for implementation?"
- Use superpowers:using-git-worktrees to create isolated workspace
- Use superpowers:writing-plans to create detailed implementation plan

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense
- **Specs are negotiable** - Always propose modifications that reduce complexity

## 🚨 CRITICAL: Prefer Spec Adjustments Over New Infrastructure

**Specs are starting points, not immutable requirements.**

Before designing new systems, ask:
1. Can we **adjust the spec slightly** to reuse existing patterns?
2. Would a different approach achieve 90% of the value with 50% of the complexity?
3. Is this creating parallel infrastructure when we could extend existing?

**Always present a "simplification option":**
```
Option A: Implement spec as-is (creates new X, Y, Z)
Option B (recommended): Adjust spec to reuse existing [pattern]
  - Tradeoff: [minor limitation]
  - Benefit: Reuses proven infrastructure, less code to maintain
```

**Example:** If designing "scheduled message conditions", check if `group_message_intervention_conditions_dsl` logic could be extended rather than creating a new DSL.
