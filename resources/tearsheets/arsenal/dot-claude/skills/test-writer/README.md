# test-writer Skill

## 🚨 CRITICAL: MANDATORY FOR ALL TEST WRITING

**YOU CANNOT WRITE TESTS WITHOUT THIS SKILL.**

## Quick Reference

**When to use:** Before writing ANY test code
**Where:** `.claude/skills/test-writer/SKILL.md`
**Always invoke:** `pytest-test-reviewer` agent after writing tests

## What This Skill Does

Prevents you from writing:
- ❌ Brittle tests with hardcoded library outputs
- ❌ Self-evident tests (x = y; assert x == y)
- ❌ Tests that verify Python/library behavior instead of YOUR code
- ❌ Wrong fixture usage (overuse for simple, underuse for complex)

Ensures you write:
- ✅ Contract-based tests (robust to library changes)
- ✅ Business-focused tests with clear value
- ✅ Appropriate fixture usage
- ✅ Tests for YOUR code's guarantees, not library behavior

## The 12-Step Workflow

1. **Analyze code type** (pure function vs database model vs API etc.)
2. **Identify dependencies** (external libraries, DB, APIs)
3. **Define YOUR contract** (what YOUR code guarantees)
4. **List edge cases**
5. **Choose test type** (unit, integration, e2e, etc.)
6. **Decide fixture strategy** (complex setup only!)
7. **Answer 5 critical questions**
8. **Anti-pattern check**
9. **Pattern reference** - 10 concrete DO THIS / NOT THAT examples
10. **Write test structure**
11. **Write business-focused docstrings**
12. **Golden Rule check** ("If this fails, what broke?")
13. **Invoke pytest-test-reviewer**

## Pattern Reference (Step 5.5)

The full skill includes **10 concrete pattern examples** with before/after code:
- Pattern 1: Test Setup (inline vs fixtures)
- Pattern 2: Test Mocking (over-mocking vs targeted)
- Pattern 3: Self-Evident Truths (what NOT to test)
- Pattern 4: Hardcoded vs Computed (formatter outputs)
- Pattern 5: Fixture Factories (variants vs overrides)
- Pattern 6: Parallel Execution (hardcoded vs UUID)
- Pattern 7: Test Documentation (technical vs business)
- Pattern 8: Parametrization (repetitive vs DRY)
- Pattern 9: Contract Testing (library outputs vs YOUR contract)
- Pattern 10: Test Types (wrong vs correct fixtures)

## Examples

### ✅ GOOD: Contract Test (Pure Function)

```python
def test_us_phone_returns_us_timezone(self):
    """
    Valid US phone numbers should return a US timezone.

    Contract test: validates that US numbers map to America/* timezones
    without depending on exact phonenumbers library output that could change.
    """
    result = infer_timezone_from_phone("+14155551234")

    # Test YOUR contract, not library internals
    assert result is not None
    assert result.startswith("America/")
    assert pytz.timezone(result)  # Valid timezone
```

### ❌ BAD: Hardcoded Library Output

```python
def test_timezone_inference(self):
    """Tests timezone inference."""
    # BAD: Brittle - breaks if phonenumbers updates mappings
    assert infer_timezone_from_phone("+14155551234") == "America/Los_Angeles"
```

### ✅ GOOD: Business Logic (Database)

```python
def test_create_intervention_requires_consent(
    self,
    test_db_session: Session,
    mock_message,
    mock_user,
):
    """
    Interventions should not be created for users without consent.

    Enforces ethical boundary - ensures we only coach users who
    explicitly opted in, maintaining trust and legal compliance.
    """
    message = mock_message()
    user = mock_user(has_consented=False)

    with pytest.raises(ValueError, match="User has not consented"):
        create_intervention(message, user)
```

## The Golden Rule

**"If this test fails, what business requirement did we break?"**

If you can't answer clearly → don't write the test.

## Violations

**ABSOLUTELY BANNED:**
- Writing tests without using test-writer skill
- Hardcoding external library outputs
- Self-evident tests
- Testing library behavior
- Fixtures for simple primitives
- Technical docstrings

**THERE IS NO EXCEPTION. EVERY TEST. EVERY TIME.**

## Full Skill

Read the complete workflow: `.claude/skills/test-writer/SKILL.md`
