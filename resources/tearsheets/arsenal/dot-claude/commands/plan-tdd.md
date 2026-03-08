# TDD Planning

Create a new Test-Driven Development implementation plan for the `Task` using the exact specified markdown `Plan Format`. Follow the `Instructions` to analyze the task and create a comprehensive TDD plan.

## Instructions

- You're creating a TDD implementation plan that will be executed by another agent or developer
- **IMPORTANT: Always write the plan to a file named `TDD_PLAN.md`**
  - If the task references a spec or research file, save `TDD_PLAN.md` in the same directory
  - Otherwise, save it in an appropriate location based on the task context
  - Always confirm the file was created successfully
- Analyze the task to determine the appropriate testing strategy (E2E, Integration, Unit)
- Follow outside-in testing principles: start with the outermost layer and work inward
- Plan for factory-style pytest fixtures and parametrized tests
- Use the strangler-fig pattern for iterative implementation

## Test Scenario Requirements

**CRITICAL: For each test scenario, you MUST provide:**
1. **Test Name**: A clear, descriptive name for the test
2. **Rationale**: One sentence explaining WHY this test is necessary
3. **Variants**: Specify parametrized variants (e.g., "5 time gaps: 0s, 30s, 5m, 10m, 30m") or "None" if single test

Use expandable `<details>` blocks to organize test scenarios by category for easy review and updates.

## Fixture Evaluation Process

**CRITICAL: Before finalizing the fixtures section, you MUST:**
1. Search the project for existing test fixtures that match your needs
2. Check these locations:
   - `api/tests/conftest.py` - Global fixtures
   - `api/tests/integration/conftest.py` - Integration test fixtures
   - `api/tests/unit/` - Unit test fixtures
   - `api/tests/fixtures_*.py` - Dedicated fixture files
   - `api/tests/helpers/` - Helper functions and test data factories
3. Identify which fixtures can be reused vs. what needs to be created
4. Update the "Required Fixtures" section to clearly separate:
   - **Existing Fixtures to Reuse** - List with their locations
   - **New Fixtures to Create** - Only list what doesn't exist

## Required Subagent Invocations

Plan must include invocation of these subagents at appropriate stages:
- `test-fixture-reviewer`: After writing fixtures to ensure they follow composable factory patterns
- `pytest-test-reviewer`: After writing tests to ensure quality and standards compliance
- `task-complete-enforcer`: After implementation to validate repository standards

## Final Steps

- IMPORTANT: Replace every <placeholder> in the `Plan Format` with specific, actionable details
- Reference testing guidance in CLAUDE.md and AGENTS.md files within the tests directory
- Verify validation commands match the project's actual command structure (e.g., `just` commands)
- This command ONLY creates the plan file - it does NOT execute any implementation

## Plan Format

```md
# TDD Plan: <task name>

## Task Description
<describe the task in detail, including its purpose and expected outcomes>

## Problem Statement
<clearly define the specific problem or requirement this task addresses>

## Testing Strategy

### Test Level Determination
<analyze and justify which testing levels are needed based on task scope:
- E2E Tests: needed if [explain why/why not]
- Integration Tests: needed if [explain why/why not]
- Unit Tests: needed if [explain why/why not]>

### Test Scenarios

<details>
<summary><strong>Happy Path Scenarios</strong></summary>

- **Test Name**: <brief description>
  - **Rationale**: <one sentence explaining why this test is needed>
  - **Variants**: <list any parametrized variants, e.g., "3 message types, 2 user roles">

- **Test Name**: <brief description>
  - **Rationale**: <one sentence explaining why this test is needed>
  - **Variants**: <list any parametrized variants or "None" if single test>

</details>

<details>
<summary><strong>Edge Cases and Boundary Conditions</strong></summary>

- **Test Name**: <brief description>
  - **Rationale**: <one sentence explaining why this test is needed>
  - **Variants**: <list any parametrized variants, e.g., "boundary values: 0, 1, MAX, MAX+1">

</details>

<details>
<summary><strong>Error Handling Scenarios</strong></summary>

- **Test Name**: <brief description>
  - **Rationale**: <one sentence explaining why this test is needed>
  - **Variants**: <list any parametrized variants, e.g., "3 error types, 2 recovery strategies">

</details>

<details>
<summary><strong>Performance Considerations</strong> (if applicable)</summary>

- **Test Name**: <brief description>
  - **Rationale**: <one sentence explaining why this test is needed>
  - **Variants**: <list any parametrized variants, e.g., "load levels: 10, 100, 1000 messages">

</details>

## Test Implementation Plan

### Required Fixtures

**Existing Fixtures to Reuse:**
<list existing fixtures found in the project with their locations>
```python
# Example format:
- fixture_name  # From path/to/file.py - Description
```

**New Fixtures to Create:**
<list only the fixtures that need to be created>
```python
# Example format:
@pytest.fixture
def new_fixture_name()
    """Description of what this fixture does"""
```

### Test Structure
<describe how tests will be organized:
- Which behaviors get separate tests
- Which variants use parametrization
- Test file organization>

### Step 1: Write Failing Tests
<detailed steps for implementing all test scenarios>

### Step 2: Validate Test Quality
- Run tests to ensure they FAIL (not ERROR)
- Invoke `test-fixture-reviewer` subagent for fixture validation
- Invoke `pytest-test-reviewer` subagent for test quality assessment
- Address any feedback
- Re-run tests to confirm they still FAIL
- **AUTO-PROCEED**: If reviews pass and tests FAIL correctly, continue to implementation phase

## Implementation Plan (Strangler-Fig Pattern)

### Iteration 1: <first slice name>
**Target Tests:** <list specific tests this iteration will make pass>
**Implementation:** <what minimal code will be written>
**Validation:** <how to verify these tests now pass>
**AUTO-PROCEED:** Continue to Iteration 2 after tests pass

### Iteration 2: <second slice name>
**Target Tests:** <list specific tests this iteration will make pass>
**Implementation:** <what minimal code will be written>
**Validation:** <how to verify these tests now pass>
**AUTO-PROCEED:** Continue to next iteration after tests pass

### Iteration N: <final slice name>
**Target Tests:** <list remaining tests to make pass>
**Implementation:** <what final code will be written>
**Validation:** <how to verify all tests now pass>
**AUTO-PROCEED:** Continue to quality validation after all tests pass

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Phase 1: Test Development
- Analyze task requirements and determine testing strategy
- Design test scenarios for <specific feature/component>
- Create factory-style fixtures for <test data needs>
- Implement parametrized tests for <behavior group 1>
- Implement parametrized tests for <behavior group 2>
- Run tests to ensure FAIL (not ERROR) status

### Phase 2: Test Review
- Invoke `test-fixture-reviewer` subagent to validate fixture patterns
- Invoke `pytest-test-reviewer` subagent to assess test quality
- Address test review feedback from subagents
- Re-run tests to confirm FAIL status
- **AUTO-PROCEED**: If all reviews pass and tests FAIL correctly, continue to Phase 3

### Phase 3: Iterative Implementation
- [Iteration 1] Implement <specific functionality> to pass <test subset>
- [Iteration 2] Implement <specific functionality> to pass <test subset>
- [Iteration N] Implement <final functionality> to pass remaining tests
- **AUTO-PROCEED**: Continue through iterations automatically until all tests pass

### Phase 4: Quality Validation
- Run full test suite to verify all tests pass
- Invoke `task-complete-enforcer` subagent for repository compliance
- Address any quality issues identified
- **AUTO-PROCEED**: If all quality checks pass, task is complete

## Validation Commands
<list specific commands to validate the implementation:>
- `just lint-and-fix` - Auto-fix + type checking
- `just test-all-mocked` - Run full test suite
- <any task-specific validation commands>

## Success Criteria
<list specific, measurable criteria that indicate successful task completion:>
- All tests pass
- No regressions in existing tests
- Code passes all quality checks
- <task-specific success criteria>

## Notes

### Existing Test Infrastructure
<document what you found in the project that can be leveraged>
- Test environment configuration (e.g., FakeRedis, SQLite)
- Helper utilities and test data factories
- Mocking patterns already in use
- Common test patterns in similar test files

### Implementation Considerations
<specific technical considerations for this task>

### When to Pause vs Auto-Proceed

**Pause and request user input when:**
- Critical issues found by review agents (>3 major issues requiring rework)
- Architectural decisions needed (module structure, API design, data models)
- Tests ERROR instead of FAIL (indicates test implementation problem)
- Implementation encounters unexpected blocking errors
- User explicitly says "stop" or "wait"

**Auto-proceed when:**
- Review agents approve with only minor suggestions
- Tests FAIL as expected (correct TDD state)
- All tests pass after implementation
- Quality checks pass (ruff, lint, test-all-mocked)
- Standard implementation of well-defined specifications

### Future Enhancements
<optional: potential improvements or extensions>
```

## Task
$ARGUMENTS