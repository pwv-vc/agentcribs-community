# Code Review

Conduct a comprehensive code review of implemented features before handoff. This command performs both automated and manual review checks, ensuring code quality, architectural alignment, and maintainability standards are met.

## Instructions

### Purpose
- Perform thorough code review beyond automated checks
- Ensure architectural patterns are properly followed
- Validate business logic implementation
- Check for security, performance, and maintainability concerns
- Bridge the gap between implementation completion and specification handoff

### Prerequisites
- Implementation should be complete (via `/implement-tdd` or manual)
- All automated tests should be passing
- Basic quality checks (`just lint-and-fix`) should pass
- Research and implementation documents should exist

### Review Scope
This review goes beyond what automated tools catch:
- Business logic correctness
- Architectural pattern adherence
- Security best practices
- Performance implications
- Code maintainability
- Documentation completeness

## Review Process

### Phase 1: Context Gathering
- Load research document from `docs/specs/<topic>/RESEARCH.md`
- Load implementation plan if exists
- Identify all changed files using git diff
- Understand the intended architecture and patterns

### Phase 2: Automated Analysis
- Run comprehensive static analysis
- Check test coverage metrics
- Analyze code complexity
- Review dependency changes
- **SUBAGENT**: Invoke `task-complete-enforcer` if not already run

### Phase 3: Codex CLI Review
- **EXTERNAL AGENT**: Invoke Codex CLI for AI-assisted code review
  ```bash
  codex exec review
  ```
- Wait for Codex analysis to complete
- Parse Codex feedback for:
  - Code quality issues
  - Best practice violations
  - Potential bugs
  - Performance concerns
  - Security vulnerabilities
- Integrate Codex findings into review report
- Cross-reference Codex suggestions with manual review findings

### Phase 4: Manual Code Review
Execute systematic review of all changes:

#### Architecture Review
- Verify alignment with chosen architecture from research
- Check pattern consistency with existing codebase
- Validate abstraction levels
- Review module boundaries and dependencies

#### Business Logic Review
- Verify requirements are correctly implemented
- Check edge case handling
- Validate data flow and transformations
- Review error handling strategies

#### Security Review
- Check for injection vulnerabilities
- Review authentication/authorization logic
- Validate input sanitization
- Check for sensitive data exposure
- Review secret management

#### Performance Review
- Identify potential bottlenecks
- Check for N+1 queries
- Review caching strategies
- Validate resource cleanup
- Check for memory leaks

#### Test Review
- Verify test coverage adequacy
- Check test quality and assertions
- Review test data management
- Validate test isolation
- **SUBAGENT**: Re-invoke `pytest-test-reviewer` for test quality

### Phase 5: Documentation Review
- Check inline code documentation
- Verify API documentation completeness
- Review README updates
- Validate configuration documentation

### Phase 6: Feedback Consolidation
- Merge findings from all review phases
- Integrate Codex CLI recommendations
- Reconcile any conflicting feedback
- Prioritize issues by severity
- Generate comprehensive review report with findings

## Review Checklist

```md
# Code Review Report: <feature/task name>

## Review Summary
- **Reviewer**: <agent/developer name>
- **Date**: <review date>
- **Branch**: <branch name>
- **Files Changed**: <count>
- **Lines Changed**: +<additions> -<deletions>

## Automated Checks ✓
- [ ] All tests passing
- [ ] Type checking and formatting passing (`just lint-and-fix`)
- [ ] No security vulnerabilities detected
- [ ] Coverage threshold met (if applicable)
- [ ] Codex CLI review complete

## Architecture & Design
### Alignment with Research
- [ ] Follows chosen architecture from research phase
- [ ] Consistent with existing patterns
- [ ] Appropriate abstraction levels
- [ ] Clean module boundaries

### Issues Found
<list any architectural concerns>

### Suggestions
<list improvement suggestions>

## Business Logic
### Requirements Coverage
- [ ] All requirements implemented
- [ ] Edge cases handled appropriately
- [ ] Error scenarios covered
- [ ] Data validation complete

### Issues Found
<list any logic concerns>

### Suggestions
<list improvement suggestions>

## Code Quality
### Maintainability
- [ ] Code is self-documenting
- [ ] Complex logic is well-commented
- [ ] No code duplication (DRY)
  - For each new function/class: `docker exec arsenal-semantic-search-cli code-search find "description"`
  - Verified no similar code exists (score > 0.4)
- [ ] Functions/methods are focused (SRP)
- [ ] Appropriate naming conventions

### Complexity Analysis
- Cyclomatic Complexity: <metric>
- Cognitive Complexity: <metric>
- Areas of Concern: <list high complexity areas>

### Codex CLI Findings
<summary of issues identified by Codex>
- Critical: <list critical issues from Codex>
- Warnings: <list warnings from Codex>
- Suggestions: <list suggestions from Codex>

### Technical Debt
<list any technical debt introduced or discovered>

## Security Review
### Vulnerabilities
- [ ] No SQL injection risks
- [ ] No XSS vulnerabilities
- [ ] No sensitive data exposure
- [ ] Proper authentication checks
- [ ] Appropriate authorization logic

### Issues Found
<list any security concerns>

### Recommendations
<security improvements needed>

## Performance Review
### Potential Issues
- [ ] No N+1 query problems
- [ ] Appropriate caching used
- [ ] Resources properly cleaned up
- [ ] No memory leaks detected
- [ ] Async operations handled correctly

### Bottlenecks Identified
<list any performance concerns>

### Optimization Opportunities
<list possible optimizations>

## Test Coverage Review
### Coverage Metrics
- Line Coverage: <percentage>
- Branch Coverage: <percentage>
- Critical Paths Covered: <yes/no>

### Test Quality
- [ ] Tests are meaningful (not just coverage)
- [ ] Assertions verify behavior
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Tests are maintainable

### Missing Tests
<list any missing test scenarios>

## Documentation Review
### Code Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] TODOs are tracked
- [ ] Deprecations noted

### Project Documentation
- [ ] README updated if needed
- [ ] Configuration documented
- [ ] API changes documented
- [ ] Migration guide if breaking changes

### Issues Found
<documentation gaps>

## Breaking Changes
<list any breaking changes and their impact>

## Dependencies
### New Dependencies
<list new dependencies and justification>

### Updated Dependencies
<list updated dependencies and risk assessment>

## Review Decision

### Status: APPROVED | NEEDS_CHANGES | BLOCKED

### Required Changes (if any)
Priority: CRITICAL | HIGH | MEDIUM | LOW

#### From Manual Review:
1. <specific change required>
2. <specific change required>

#### From Codex CLI:
1. <critical issues that must be addressed>
2. <high-priority issues from Codex>

### Suggested Improvements (optional)
#### From Manual Review:
1. <nice-to-have improvement>
2. <nice-to-have improvement>

#### From Codex CLI:
1. <Codex suggestions worth considering>
2. <performance or quality improvements from Codex>

### Commendations
<highlight particularly good implementations>

## Follow-up Actions
- [ ] Address critical issues
- [ ] Implement high-priority changes
- [ ] Consider suggested improvements
- [ ] Update documentation
- [ ] Add follow-up tickets for future work

## Sign-off Criteria
Before marking as reviewed:
- [ ] All critical issues resolved
- [ ] High priority changes implemented
- [ ] Tests updated and passing
- [ ] Documentation complete
- [ ] Security concerns addressed
```

## Review Outcomes

### APPROVED
- No critical issues found
- Code meets all quality standards
- Ready for spec-handoff

### NEEDS_CHANGES
- Issues identified that must be fixed
- Return to implementation phase
- Re-review after changes

### BLOCKED
- Critical issues that require architecture changes
- Security vulnerabilities that need addressing
- May need to return to research/planning phase

## Integration with Lifecycle

### After Implementation
```
/implement-tdd → /review-code → [fix issues] → /review-code → /spec-handoff
```

### Iterative Review
- Review can be run multiple times
- Each review builds on previous feedback
- Track resolution of identified issues

## Review Modes

### Quick Review
```
/review-code --quick
```
- Focus on critical issues only
- Automated checks + high-level manual review
- Suitable for small changes

### Full Review
```
/review-code --full
```
- Complete review of all aspects
- Detailed analysis and recommendations
- Suitable for major features

### Security Focus
```
/review-code --security
```
- Emphasize security review
- Additional security scanning
- Suitable for sensitive features

### Performance Focus
```
/review-code --performance
```
- Emphasize performance analysis
- Profile code if possible
- Suitable for performance-critical features

## Success Criteria
- All automated checks pass
- No critical issues identified
- Architecture alignment verified
- Security review complete
- Documentation adequate
- Ready for handoff

## Notes
- This review combines AI-assisted analysis (Codex CLI) with manual review
- Codex CLI provides consistent, automated code quality analysis
- Manual review adds context-aware business logic validation
- Should catch issues that tests might miss
- Focus on maintainability and long-term health
- Not just finding problems, but suggesting improvements
- Creates actionable feedback for developers
- Codex findings are integrated and cross-referenced with manual review

## Parameters
$ARGUMENTS