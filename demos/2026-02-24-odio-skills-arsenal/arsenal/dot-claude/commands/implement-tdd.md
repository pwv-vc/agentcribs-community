# TDD Implementation

Execute a Test-Driven Development plan from `specs/*.md` or create implementation from scratch following TDD principles. This command guides systematic implementation with automated quality checks at each phase.

## Instructions

### Prerequisites
- If a TDD plan exists in `specs/*.md`, load and follow it exactly
- If no plan exists, create an ad-hoc TDD approach based on the task
- MANDATORY: Read `AGENTS.md` for codebase patterns and standards
- MANDATORY: Read `api/tests/AGENTS.md` for testing patterns and fixture guidelines

### Execution Protocol
1. **Phase-based execution**: Work through each phase methodically
2. **Subagent integration**: Automatically invoke reviewers at checkpoints
3. **Quality gates**: Must pass before proceeding to next phase
4. **Documentation updates**: Keep specs and docs current throughout
5. **AUTO-PROCEED**: After successful phase completion, automatically continue to next phase unless:
   - Critical issues found requiring user decisions
   - User explicitly requests to pause
   - Implementation encounters blocking errors

### Implementation Phases

#### Phase 1: Test Setup & Validation
- Create or load test specifications
- Use **test-writer skill** to write factory-style pytest fixtures following `api/tests/AGENTS.md` patterns
- Implement test scenarios with proper parametrization
- **CHECKPOINT**: Use **test-runner skill** to ensure tests FAIL (not ERROR)
- **SUBAGENT**: Invoke `test-fixture-reviewer` for fixture validation
- **SUBAGENT**: Invoke `pytest-test-reviewer` for test quality
- Fix any issues identified by subagents
- **GATE**: All tests must FAIL properly before proceeding
- **AUTO-PROCEED**: If all reviews pass and tests FAIL correctly, continue to Phase 2

#### Phase 2: Iterative Implementation (Strangler-Fig Pattern)
For each iteration defined in the plan:
- Implement minimal code to make target tests pass
- Use **test-runner skill** to run only the target tests for this iteration
- Refactor if needed while keeping tests green
- **CHECKPOINT**: Verify target tests pass, others still fail
- **AUTO-PROCEED**: Continue to next iteration automatically until all iterations complete

#### Phase 3: Integration & Refinement
- Use **test-runner skill** to run full test suite
- If tests fail, use **test-fixer skill** to iterate until all pass
- Refactor for code quality while maintaining green tests
- Add error handling and edge cases as needed
- **CHECKPOINT**: All tests must pass (verified by test-runner)
- **AUTO-PROCEED**: If all tests pass, continue to Phase 4

#### Phase 4: Quality Enforcement
- **SUBAGENT**: Invoke `task-complete-enforcer` for repository compliance
  - Runs: `just lint-and-fix`, `just test-all-mocked`
- Fix any quality issues identified
- **GATE**: Must pass all quality checks before completion
- **AUTO-PROCEED**: If all quality checks pass, continue to Phase 5

#### Phase 5: Documentation & Handoff
- Update `specifications/CURRENT_SPEC.md` with completion notes
- Document any architectural decisions made
- Create PR description if requested
- Provide implementation summary

## Quality Checks

### Automated Checks (via task-complete-enforcer)
```bash
just lint-and-fix    # Auto-fix + type checking
just test-all-mocked # Full test suite
```

### Manual Verification
- Tests follow parametrization patterns from `api/tests/AGENTS.md`
- Fixtures are composable and factory-style
- Implementation follows existing codebase patterns
- No regression in existing functionality

## Implementation Tracking

Use TodoWrite tool to track progress through phases:
- Create todos for each phase and iteration
- Mark as `in_progress` when starting
- Mark as `completed` only after passing quality gates
- Add new todos for issues discovered during implementation

## Error Recovery

### Test Failures
- If tests ERROR instead of FAIL: Use **test-fixer skill** to investigate and fix
- If wrong tests pass: Use **test-writer skill** to review test logic
- If all tests pass initially: Tests aren't testing the right thing - use **test-writer skill** to fix

### Quality Failures
- **Mypy errors**: Invoke `mypy-error-fixer` subagent
- **Ruff failures**: Fix formatting issues
- **Test failures**: Debug and fix implementation

### Blocked States
- Document blockers in todos
- Ask user for clarification on ambiguous requirements
- Create separate research task if architecture unclear

## When to Pause vs Auto-Proceed

### Pause and Request User Input When:
- Critical issues found by review agents (>3 major issues requiring rework)
- Architectural decisions needed (module structure, API design, data models)
- Tests ERROR instead of FAIL (indicates test implementation problem)
- Implementation encounters unexpected blocking errors
- User explicitly says "stop" or "wait"

### Auto-Proceed When:
- Review agents approve with only minor suggestions
- Tests FAIL as expected (correct TDD state)
- All tests pass after implementation
- Quality checks pass (ruff, lint, test-all-mocked)
- Standard implementation of well-defined specifications

## Success Criteria
- All planned tests pass
- No regression in existing tests
- Quality checks pass (ruff, lint, test-all-mocked)
- Subagent reviews approved
- Documentation updated
- Code follows codebase patterns

## Command Parameters

### With Existing Plan
```
/implement-tdd specs/PLAN-NAME.md
```

### Ad-hoc Implementation
```
/implement-tdd "Brief description of what to implement with TDD approach"
```

## Notes
- This command executes implementation, not planning
- Always follows TDD: tests first, then implementation
- Subagents are invoked automatically at checkpoints
- Quality gates are mandatory - no skipping
- Update specifications throughout, not just at the end

## Task
$ARGUMENTS