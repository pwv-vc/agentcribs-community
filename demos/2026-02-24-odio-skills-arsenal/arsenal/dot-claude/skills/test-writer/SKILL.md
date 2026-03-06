---
name: test-writer
description: "MANDATORY - INVOKE BEFORE writing ANY test code (def test_*, class Test*). Prevents brittle tests. Read this skill first, then write tests."
---

# test-writer Skill

## 🚨 CRITICAL: MANDATORY FOR ALL TEST WRITING AND UPDATING

**YOU CANNOT WRITE OR UPDATE TESTS WITHOUT THIS SKILL.**

If you write or update tests without following this skill, you will:
- Write brittle tests with hardcoded library outputs
- Create self-evident tests that provide zero value
- Use fixtures incorrectly (overuse for simple cases, underuse for complex)
- Test Python/library behavior instead of YOUR code's contracts

**This skill is your checklist. Follow it step-by-step. No shortcuts.**

---

## 🚨 CRITICAL FOR TEST WRITING

- **BEFORE writing tests** → Use test-writer skill (MANDATORY - analyzes code type, dependencies, contract)
- **AFTER writing tests** → Invoke pytest-test-reviewer agent (validates patterns)
- **YOU CANNOT WRITE TESTS WITHOUT test-writer SKILL** - No exceptions, no shortcuts, every test, every time

---

## When to Use This Skill

Use this skill when:
- ✅ User asks "write tests for X"
- ✅ You're creating a new test file (`test_*.py`)
- ✅ You're adding tests to an existing test file
- ✅ User says "test this" or "add test coverage"
- ✅ You've just written code and need to test it
- ✅ **You're updating/modifying existing tests** (e.g., when test-fixer needs to update test expectations)
- ✅ **Tests are failing and need to be fixed** (use this skill to understand what to change)

**DO NOT write or update tests without using this skill. PERIOD.**

---

## 🔄 How This Skill Interacts With Other Skills

1. **Called by test-fixer** when modifying test files - determines if code or contract is wrong
2. **Can call sql-reader** to query production data model and design realistic fixtures
3. **MUST call semantic-search** before writing tests to find existing test patterns and fixtures:
   - `docker exec arsenal-semantic-search-cli code-search find "test <feature>"`
   - Check for existing fixtures, test utilities, and similar test patterns
4. **Works autonomously** but flags UX contract changes: "⚠️ UX contract change: [explain]"

## 🚨 CRITICAL: Don't Encode Broken Behavior

**When updating tests, ask:**
1. Is the CODE wrong? → Fix code, keep test
2. Is the TEST wrong? → Update test (legitimate contract change)
3. Is this encoding BROKEN behavior? → Flag to user and continue

**Red flags:**
- "Code changed so I'll update the test" ← DANGER
- Test passed → code changed → test fails → changing test instead of code ← DANGER

**Safe updates:**
- Intentional contract change (documented in spec)
- Refactoring (same behavior, different implementation)
- Fixing brittle tests (testing implementation not contract)

**When in doubt:** Flag it and continue autonomously: "⚠️ This may encode broken behavior: [explain]"

---

## Step 1: Analyze the Code Being Tested

Before writing A SINGLE LINE of test code, answer these questions:

### Question 1: What type of code is this?

- [ ] **Pure function** (no side effects, no state, deterministic)
  - Example: `def calculate_total(items: list[Item]) -> float`
  - Example: `def infer_timezone_from_phone(phone: str) -> str | None`

- [ ] **Database model/ORM** (models with relationships, DB operations)
  - Example: `create_intervention(message: Message, user: User) -> Intervention`
  - Example: `get_conversation_messages(conversation_id: int) -> list[Message]`

- [ ] **API endpoint** (FastAPI routes, HTTP handlers)
  - Example: `POST /webhook/sendblue`
  - Example: `GET /conversations/{id}/messages`

- [ ] **External service integration** (calls to OpenAI, Langfuse, SendBlue, etc.)
  - Example: `send_intervention_via_sendblue(message: str, phone: str)`
  - Example: `fetch_langfuse_prompt(prompt_name: str)`

- [ ] **Business logic with state** (complex rules, workflows, state machines)
  - Example: `should_send_daily_reminder(user: User, last_intervention: datetime)`
  - Example: `calculate_conflict_score(message: Message, conversation: Conversation)`

**Write your answer:**
```
Type: [YOUR ANSWER HERE]
Reasoning: [WHY you chose this type]
```

### Question 2: What are the dependencies?

Check all that apply:
- [ ] External library (phonenumbers, pytz, croniter, etc.)
- [ ] Database (PostgreSQL via SQLAlchemy)
- [ ] External API (OpenAI, Langfuse, SendBlue, etc.)
- [ ] File system
- [ ] Redis/Queue
- [ ] None (pure function with no external deps)

**Write your answer:**
```
Dependencies: [LIST THEM]
Which are external (library/API): [WHICH ONES]
Which need mocking: [WHICH ONES]
```

### Question 3: What's YOUR code's contract?

**NOT what libraries return. What does YOUR code GUARANTEE?**

Think about:
- What does this function promise to do?
- What are valid inputs?
- What are valid outputs?
- What errors should it raise?
- What invariants must hold?

**Write your answer:**
```
Contract:
- Input guarantees: [e.g., "accepts valid US phone numbers"]
- Output guarantees: [e.g., "returns valid pytz timezone or None"]
- Error handling: [e.g., "returns None for invalid input, doesn't raise"]
- Invariants: [e.g., "US numbers always return America/* timezones"]
```

### Question 4: What are the edge cases?

- None/empty input?
- Invalid input?
- Boundary values (min, max)?
- Error conditions?
- Race conditions or timing issues?

**Write your answer:**
```
Edge cases to test:
1. [EDGE CASE 1]
2. [EDGE CASE 2]
3. [EDGE CASE 3]
```

---

## Step 2: Choose the Right Test Type

Based on your analysis, determine which test type(s) to use:

### Unit Tests (`tests/unit/`)
**When:** Complex business logic in isolation
**Database:** SQLite in-memory
**Redis:** FakeRedis
**APIs:** All mocked
**Speed:** <5s total

Use for:
- Pure functions with complex logic
- Business rule combinations
- Edge cases and boundaries
- Data transformations

### Integration Tests (`tests/integration/`)
**When:** Component interactions
**Database:** SQLite in-memory
**Redis:** FakeRedis
**APIs:** All mocked
**Speed:** <5s total

Use for:
- Service interactions
- Database operations
- API endpoint contracts
- FastAPI TestClient validation

### E2E Mocked Tests (`tests/e2e_mocked/`)
**When:** Critical workflows
**Database:** Docker PostgreSQL (SHARED - use UUIDs!)
**Redis:** FakeRedis
**APIs:** All mocked
**Speed:** <20s total

Use for:
- Complete workflows (webhook → queue → worker)
- Full pipeline testing
- Integration of multiple components

**⚠️ CRITICAL:** Use UUID-based unique identifiers for parallel execution:
```python
unique_id = str(uuid.uuid4())[:8]
user_name = f"TestUser_{unique_id}"
```

### E2E Live Tests (`tests/e2e_live/`) 💰
**When:** Validate prompts with REAL LLMs
**Database:** SQLite in-memory
**Redis:** FakeRedis
**APIs:** REAL (costs money!)
**Speed:** <60s total

**⚠️ COSTS REAL MONEY!** Use `gpt-4.1-nano` for efficiency.

Use for:
- Prompt validation with real LLMs
- Langfuse prompt deployment verification
- Critical AI behavior validation

### Smoke Tests (`tests/smoke_tests/`)
**When:** Production health validation
**Database:** Real PostgreSQL (via API)
**Redis:** Real Redis (via API)
**Speed:** <60s total

Use for:
- Deployment validation
- API availability checks
- Production monitoring

**Write your decision:**
```
Test type: [UNIT | INTEGRATION | E2E_MOCKED | E2E_LIVE | SMOKE]
Reasoning: [WHY this type is appropriate]
```

---

## Step 3: Decide Fixture Strategy

### DO Use Fixtures For:

✅ **Database models with relationships:**
```python
def test_message_processing(mock_couple_conversation, mock_message):
    # Fixtures handle complex DB setup
    conversation, participants = mock_couple_conversation
    result = process_message(conversation, mock_message)
```

✅ **Complex objects with many fields:**
```python
@pytest.fixture
def oauth_client():
    return OAuthClient(
        client_id="...",
        client_secret="...",
        redirect_uri="...",
        # 10+ more required fields
    )
```

✅ **Stateful components:**
```python
@pytest.fixture
def redis_connection():
    conn = Redis(...)
    yield conn
    conn.close()
```

### DON'T Use Fixtures For:

❌ **Pure functions with simple inputs:**
```python
# ❌ OVERKILL
@pytest.fixture
def phone_numbers():
    return ["+14155551234", "+12125551234"]

def test_timezone(phone_numbers):
    result = infer_timezone(phone_numbers[0])

# ✅ SIMPLE
def test_timezone():
    result = infer_timezone("+14155551234")
    assert result.startswith("America/")
```

❌ **Simple strings/primitives (< 5 fields):**
```python
# ❌ Unnecessary fixture
@pytest.fixture
def sample_json():
    return '{"key": "value"}'

# ✅ Inline it
def test_parsing():
    data = '{"key": "value"}'
    assert parse_json(data)["key"] == "value"
```

**Rule of thumb:** If your "fixture" is just returning a hardcoded string/dict with <5 fields, inline it.

**Write your decision:**
```
Fixtures needed: [YES/NO]
Which fixtures: [LIST THEM OR "NONE"]
Why: [REASONING]
```

---

## Step 4: The 5 Critical Questions

Before writing ANY assert statement, ask:

### 1. Am I testing MY code or someone else's?

❌ **Testing library behavior:**
```python
# BAD: Testing that phonenumbers library works
def test_phonenumbers_library():
    assert phonenumbers.parse("+14155551234").country_code == 1  # phonenumbers' job!
```

✅ **Testing MY wrapper's contract:**
```python
# GOOD: Testing what MY function guarantees
def test_us_phone_returns_us_timezone():
    result = infer_timezone_from_phone("+14155551234")
    assert result is not None           # MY guarantee: non-None for valid input
    assert result.startswith("America/") # MY guarantee: US number → US timezone
    assert pytz.timezone(result)        # MY guarantee: valid pytz timezone
```

### 2. What can change without touching my code?

❌ **Hardcoding external library outputs:**
```python
# BAD: Brittle - breaks if phonenumbers updates timezone mappings
def test_timezone_inference():
    assert infer_timezone("+14155551234") == "America/Los_Angeles"
    # phonenumbers controls this exact value, not YOUR code!
```

✅ **Testing contracts:**
```python
# GOOD: Tests behavior, not exact library output
def test_timezone_inference():
    result = infer_timezone("+14155551234")
    assert result.startswith("America/")  # Contract: US timezone
    # Robust to library changing "Los_Angeles" to "Los_Angeles/Pacific"
```

### 3. Is this self-evident?

❌ **Self-evident tests:**
```python
# BAD: Testing that setting a value works
def test_setting_state():
    participant.state = ConversationState.ACTIVE
    assert participant.state == ConversationState.ACTIVE  # Duh!

# BAD: Testing pass-through logic
def test_returns_input_unchanged():
    result = resolve_timezone("Europe/London", phone=None)
    assert result == "Europe/London"  # Just testing: if x: return x

# BAD: Testing mocks
def test_mock_returns_value():
    mock.get_value.return_value = 42
    assert mock.get_value() == 42  # Of course it does!
```

✅ **Testing business logic:**
```python
# GOOD: Tests decision logic (priority order)
def test_timezone_resolution_priority():
    # When both configured AND phone available, configured wins
    result = resolve_timezone("Europe/London", "+14155551234")
    assert result == "Europe/London"  # Tests priority, not pass-through
```

### 4. Am I testing "WHAT" or "HOW"?

❌ **Testing implementation (HOW):**
```python
# BAD: Exact values from library
assert infer_timezone("+1415...") == "America/Los_Angeles"
```

✅ **Testing contract (WHAT):**
```python
# GOOD: Behavior and guarantees
result = infer_timezone("+1415...")
assert result.startswith("America/")  # What: returns US timezone
```

### 5. Do I need fixtures/factories?

- Complex DB setup with relationships → ✅ YES
- Pure function with primitives → ❌ NO
- Stateful components → ✅ YES
- Simple strings/dicts (<5 fields) → ❌ NO

**Write your answers:**
```
Q1 (My code or library): [ANSWER]
Q2 (What can change): [ANSWER]
Q3 (Self-evident): [YES/NO + reasoning]
Q4 (What or how): [ANSWER]
Q5 (Need fixtures): [YES/NO + which ones]
```

---

## Step 5: Anti-Pattern Check

Before writing code, verify you will NOT:

### ❌ ANTI-PATTERNS TO AVOID:

**1. Hardcoded library outputs:**
```python
# ❌ NO
assert infer_timezone("+14155551234") == "America/Los_Angeles"

# ✅ YES
assert infer_timezone("+14155551234").startswith("America/")
```

**2. Self-evident assertions:**
```python
# ❌ NO
user.name = "Alice"
assert user.name == "Alice"

# ✅ YES - test business rules
assert can_send_intervention(user) == (user.has_consented and not user.is_banned)
```

**3. Testing library/Python behavior:**
```python
# ❌ NO
result = {**dict1, **dict2}
assert len(result) == len(dict1) + len(dict2)  # Testing Python!

# ✅ YES - test YOUR logic
merged = merge_conversation_contexts(conv1, conv2)
assert merged.participant_count == conv1.participant_count + conv2.participant_count
```

**4. Fixtures for primitives:**
```python
# ❌ NO
@pytest.fixture
def phone_numbers():
    return ["+14155551234"]

# ✅ YES - inline it
def test_phone():
    result = process_phone("+14155551234")
```

**5. Mock chains:**
```python
# ❌ NO
mock.query.return_value.filter.return_value.first.return_value = user

# ✅ YES - specific mock
with patch("data.models.User.get_by_id", return_value=user):
```

**6. Multiple fixture variants:**
```python
# ❌ NO
@pytest.fixture
def full_payload(): ...

@pytest.fixture
def partial_payload(): ...

@pytest.fixture
def minimal_payload(): ...

# ✅ YES - one factory with overrides
@pytest.fixture
def payload_factory():
    def _create(**overrides):
        defaults = {"name": "Alice", "consent": True}
        return {**defaults, **overrides}
    return _create
```

**7. Wrong mocking for test type:**
```python
# ❌ NO - in E2E_live test
with patch('openai.ChatCompletion.create'):  # Don't mock in live tests!

# ✅ YES - in unit/integration test
with patch('openai.ChatCompletion.create', return_value=mock_response):
```

**Checklist:**
- [ ] No hardcoded library outputs?
- [ ] No self-evident assertions?
- [ ] Not testing library/Python behavior?
- [ ] Fixtures used appropriately?
- [ ] No mock chains?
- [ ] Factory fixtures with overrides (not multiple variants)?
- [ ] Correct mocking for test type?

---

## Step 5.5: Pattern Reference - DO THIS, NOT THAT

**Before writing code, review these concrete examples of good vs bad test patterns.**

### Pattern 1: Test Setup

❌ **DON'T create test data inline:**
```python
def test_message_processing():
    # 20+ lines of manual setup
    person1 = Persons(name="Alice")
    person2 = Persons(name="Bob")
    conversation = Conversations()
    # ... more boilerplate
```

✅ **DO use shared fixtures:**
```python
def test_message_processing(mock_couple_conversation, mock_message):
    # Clean test focused on logic
    conversation, participants = mock_couple_conversation
    result = process_message(conversation, mock_message)
```

### Pattern 2: Test Mocking

❌ **DON'T mock everything or use mock chains:**
```python
# Over-mocking with chains
mock.query.return_value.filter.return_value.first.return_value = user

# Wrong mocking for test type - In E2E_live test:
with patch('openai.ChatCompletion.create'):  # NEVER mock live services in e2e_live!
```

✅ **DO use targeted mocking appropriate to test type:**
```python
# Unit/Integration: Mock external services
with patch('data.models.message.Message.get_latest', return_value=[]):
    # Test specific integration point

# E2E_live: NEVER mock - use real APIs
response = generate_intervention(message)  # Real OpenAI call
assert "coach" in response.lower()  # Not "therapist"
```

### Pattern 3: Test Assertions - Self-Evident Truths

❌ **DON'T test obvious Python behavior:**
```python
# Testing that Python works
user.name = "Alice"
assert user.name == "Alice"  # Self-evident!

# Testing framework features
assert session.commit() is None  # SQLAlchemy always returns None

# Testing that setting a value works
participant.state = ConversationState.ACTIVE
assert participant.state == ConversationState.ACTIVE  # Of course!

# Testing that mocks return what you told them
mock.get_value.return_value = 42
assert mock.get_value() == 42  # Duh!

# Testing Python built-ins
result = {**dict1, **dict2}
assert len(result) == len(dict1) + len(dict2)  # Testing Python!
```

✅ **DO test business logic:**
```python
# Tests business rule
def test_consent_required_before_coaching():
    """Ensures coaching only starts after explicit consent."""
    user = create_user(has_consented=False)
    assert not can_send_intervention(user)

# Tests complex logic
def test_conflict_detection():
    message = "You never listen to me!"
    assert detect_conflict_level(message) == "high"
```

### Pattern 4: Test Assertions - Hardcoded vs Computed

❌ **DON'T use hardcoded expected values from formatters:**
```python
# BAD: Hardcoded string breaks when format changes
def test_form_to_message():
    message = create_message_from_form({"relationship_type": "romantic"})
    assert "romantic relationship" in message.lower()  # Brittle!
```

✅ **DO compute expected values using actual formatting methods:**
```python
# GOOD: Uses the same formatting logic being tested
def test_form_to_message():
    message = create_message_from_form({"relationship_type": "romantic"})
    expected = RELATIONSHIP_TYPE_FIELD.to_message("romantic")
    assert expected and expected.lower() in message.lower()
```

### Pattern 5: Test Organization - Fixtures

❌ **DON'T create multiple fixture variants:**
```python
# BAD - creates maintenance burden, violates DRY
@pytest.fixture
def full_payload_data():
    return {"user_name": "Alice", "consent": True, ...}

@pytest.fixture
def partial_payload_data():
    return {"user_name": "Alice", "consent": True, "communication_goals": None}

@pytest.fixture
def minimal_payload_data():
    return {"user_name": "Alice"}

# Now you have 3 fixtures to maintain when schema changes!
```

✅ **DO create one factory fixture with configurable overrides:**
```python
@pytest.fixture
def payload_factory() -> Callable:
    """Factory for test payloads with sane defaults and overrides."""
    def _create_payload(user_name: str = "Alice", **overrides):
        defaults = {
            "user_name": user_name,
            "consent": True,
            "relationship_type": "romantic",
            "communication_goals": "better listening",
        }
        defaults.update(overrides)
        return defaults
    return _create_payload

# Usage - customize only what varies per test
def test_full_data(payload_factory):
    payload = payload_factory()  # Uses all defaults

def test_partial_data(payload_factory):
    payload = payload_factory(communication_goals=None)

def test_custom_data(payload_factory):
    payload = payload_factory(user_name="Bob", relationship_type="co-parenting")
```

### Pattern 6: Test Organization - Parallel Execution

❌ **DON'T use hardcoded values in E2E tests:**
```python
# BAD: Hardcoded values cause conflicts in parallel execution
def test_workflow():
    user_name = "TestUser"  # Will conflict when tests run in parallel!
```

✅ **DO use UUID-based unique identifiers:**
```python
# GOOD: Each test run gets unique data
def test_workflow():
    unique_id = str(uuid.uuid4())[:8]
    user_name = f"TestUser_{unique_id}"  # Parallel-safe
```

### Pattern 7: Test Documentation

❌ **DON'T write technical descriptions:**
```python
def test_webhook():
    """Tests POST /webhook returns 200."""
```

✅ **DO explain business value:**
```python
def test_webhook_queues_messages():
    """
    Ensures incoming messages are reliably queued for async processing,
    preventing message loss during high load or worker downtime.
    """
```

### Pattern 8: Test Parametrization

❌ **DON'T write separate tests for each variant:**
```python
# BAD - repetitive, hard to maintain
def test_romantic_relationship_creates_fact():
    assert "romantic" in facts

def test_coparenting_relationship_creates_fact():
    assert "co-parenting" in facts

def test_friendship_relationship_creates_fact():
    assert "friendship" in facts
```

✅ **DO use parametrize for common patterns:**
```python
# GOOD - single parametrized test
@pytest.mark.parametrize("relationship_type", ["romantic", "co-parenting", "friendship"])
def test_relationship_type_creates_fact(relationship_type):
    assert relationship_type in facts

# GOOD - test business rule combinations
@pytest.mark.parametrize(
    "sender_interventions,recipient_interventions,expected_should_send",
    [
        (False, False, True),   # No recent interventions → send reminder
        (True, False, False),   # Sender has interventions → don't spam
        (False, True, False),   # Recipient has interventions → don't spam
    ],
)
def test_daily_reminder_logic(sender_interventions, recipient_interventions, expected_should_send):
    """Tests reminder logic respects intervention cooldown periods."""
    # Single test implementation covering 3 business rule combinations
```

### Pattern 9: Contract Testing (Library Wrappers)

❌ **DON'T hardcode library outputs:**
```python
# BAD: Brittle - breaks if phonenumbers updates mappings
def test_timezone_inference():
    assert infer_timezone_from_phone("+14155551234") == "America/Los_Angeles"
```

✅ **DO test YOUR contract, not library internals:**
```python
# GOOD: Contract test
def test_us_phone_returns_us_timezone():
    """
    Valid US phone numbers should return a US timezone.

    Contract test: validates that US numbers map to America/* timezones
    without depending on exact phonenumbers library output that could change.
    """
    result = infer_timezone_from_phone("+14155551234")

    # Test YOUR contract, not library internals
    assert result is not None
    assert result.startswith("America/")  # Contract: US → America/*
    assert pytz.timezone(result)  # Contract: valid timezone
```

### Pattern 10: Wrong Test Type / Fixtures

❌ **DON'T mix test types or use wrong fixtures:**
```python
# Wrong fixture for test type
# In unit test:
def test_logic(real_database):  # Should use SQLite/mocks!

# In E2E_mocked:
user_name = "TestUser"  # Hardcoded = parallel test failures
```

✅ **DO use correct test type and fixtures:**
```python
# Unit test: SQLite + FakeRedis + Mocks
def test_complex_logic(mock_session, mock_message):
    # Test algorithm only

# E2E_mocked: Docker PostgreSQL + unique data
def test_workflow():
    unique_id = str(uuid.uuid4())[:8]
    user_name = f"TestUser_{unique_id}"  # Parallel-safe

# E2E_live: Real APIs (costs money!)
@pytest.fixture(scope="module")  # Cache expensive calls
def gpt_response():
    return openai.complete(model="gpt-4.1-nano")  # Cheapest model
```

---

## Step 6: Write Test Structure

Now you can write the test. Follow this template:

### For Pure Functions:

```python
class TestFunctionName:
    """Test [function_name] [what it does]."""

    def test_[descriptive_name](self):
        """
        [Business value explanation - WHY this test matters]

        [What contract/guarantee this verifies]
        """
        # Arrange: Set up inputs
        input_value = "test_input"

        # Act: Call the function
        result = function_name(input_value)

        # Assert: Verify contract (not exact values!)
        assert result is not None
        assert isinstance(result, ExpectedType)
        assert result.meets_contract()  # Whatever YOUR guarantee is
```

### For Database/Stateful Code:

```python
class TestFeatureName:
    """Test [feature] [what it does]."""

    def test_[descriptive_name](
        self,
        test_db_session: Session,
        mock_fixture_1,
        mock_fixture_2,
    ):
        """
        [Business value explanation - WHY this test matters]

        [What business rule this verifies]
        """
        # Arrange: Use fixtures
        entity = mock_fixture_1()

        # Act: Execute business logic
        result = business_function(entity)

        # Assert: Verify business rules
        test_db_session.refresh(result)
        assert result.state == ExpectedState.CORRECT
        assert result.relationship_set_correctly
```

### For Parametrized Tests:

```python
@pytest.mark.parametrize(
    "input_value,expected_behavior",
    [
        ("value1", "behavior1"),  # Comment explaining this case
        ("value2", "behavior2"),  # Comment explaining this case
        ("edge_case", "edge_behavior"),  # Edge case
    ],
)
def test_[descriptive_name](self, input_value, expected_behavior):
    """
    [Business value explanation]

    Tests that [function] handles [variety] of inputs correctly.
    """
    result = function_name(input_value)
    assert result.matches_expected(expected_behavior)
```

### For Contract Testing (Library Wrappers):

```python
def test_wrapper_contract(self):
    """
    [What your wrapper guarantees]

    Contract test: validates [YOUR guarantees] without depending on
    exact library outputs that could change.
    """
    result = your_wrapper_function(input)

    # Test YOUR contract, not library internals
    assert result is not None                    # Guarantee: non-None for valid input
    assert result.matches_expected_pattern()     # Guarantee: correct format
    assert result.passes_validation()            # Guarantee: valid output
    # NOT: assert result == "exact_library_value"  # ❌ Brittle!
```

---

## Step 7: Write Business-Focused Docstrings

Every test MUST have a docstring that explains:
1. **Business value** - WHY this test matters
2. **What guarantee/contract** it verifies

❌ **BAD - Technical description:**
```python
def test_webhook():
    """Tests POST /webhook returns 200."""
```

✅ **GOOD - Business value:**
```python
def test_webhook_queues_messages():
    """
    Ensures incoming messages are reliably queued for async processing,
    preventing message loss during high load or worker downtime.
    """
```

❌ **BAD - Obvious:**
```python
def test_timezone_inference():
    """Tests that timezone is inferred from phone."""
```

✅ **GOOD - Contract and value:**
```python
def test_us_phone_returns_us_timezone():
    """
    Valid US phone numbers should return a US timezone.

    Contract test: validates that US numbers map to America/* timezones
    without depending on exact phonenumbers library output that could change.
    Ensures scheduling happens in user's local timezone.
    """
```

**Template:**
```python
def test_[descriptive_name]():
    """
    [One sentence: business value - what breaks if this fails]

    [Optional: Additional context about contract, edge case, or business rule]
    [Optional: Why this matters for users/product]
    """
```

---

## Step 8: Golden Rule Check

Before finalizing, ask yourself:

**"If this test fails, what business requirement did we break?"**

If you can't answer that question clearly, the test shouldn't exist.

Examples:
- ✅ "We broke the guarantee that US phone numbers return US timezones"
- ✅ "We broke the rule that interventions require user consent"
- ✅ "We broke the priority order for timezone resolution"
- ❌ "We broke... um... setting a value returns that value?" (self-evident)
- ❌ "We broke... the phonenumbers library?" (not your code)

**Write your answer:**
```
If this test fails, we broke: [SPECIFIC BUSINESS REQUIREMENT]
```

---

## Step 9: Decision Tree Summary

Final check:

1. **Am I testing a business decision or rule?** → Write the test
2. **Am I testing that Python/framework features work?** → Don't write it
3. **Am I testing what I just set/mocked?** → Don't write it
4. **Would this test catch a real bug?** → Write the test
5. **Would this test help someone understand the system?** → Write the test
6. **Is this test just for coverage percentage?** → Don't write it

---

## Step 10: Present Analysis to User

Before writing code, present your analysis:

```markdown
## Test Writing Analysis

### Code Type
[Pure function | Database model | API endpoint | etc.]
Reasoning: [WHY]

### Dependencies
- [Dependency 1]: [Mock it | Use real | etc.]
- [Dependency 2]: [Mock it | Use real | etc.]

### Contract
YOUR code guarantees:
- [Guarantee 1]
- [Guarantee 2]
- [Guarantee 3]

### Test Type
[UNIT | INTEGRATION | E2E_MOCKED | E2E_LIVE | SMOKE]
Reasoning: [WHY this type]

### Fixture Strategy
[YES: Use fixtures for X, Y, Z | NO: Pure function, inline data]

### Edge Cases
1. [Edge case 1]
2. [Edge case 2]
3. [Edge case 3]

### Anti-Pattern Check
✅ No hardcoded library outputs
✅ No self-evident assertions
✅ Testing MY code's contract
✅ Appropriate fixture usage
✅ Business-focused docstrings

### Golden Rule
If these tests fail, we broke: [SPECIFIC BUSINESS REQUIREMENT]

### Proposed Test Structure
```python
[SHOW TEST TEMPLATE]
```

Does this approach look correct?
```

**Get user confirmation before proceeding.**

---

## Step 11: Write the Tests

Only after Steps 1-10, write the actual test code.

Use the structure from Step 6.
Use the docstrings from Step 7.
Follow the anti-patterns from Step 5.

---

## Step 12: Invoke pytest-test-reviewer

After writing tests, ALWAYS invoke the `pytest-test-reviewer` agent to validate:
- Patterns followed correctly
- No anti-patterns introduced
- Business value clear
- Contracts tested (not implementation)

---

## Examples

### Example 1: Pure Function (Timezone Util)

**User:** "Write tests for `infer_timezone_from_phone`"

**Step 1-3: Analysis**
```
Code type: Pure function wrapping phonenumbers library
Dependencies: phonenumbers (external), pytz (validation)
Contract:
  - Input: phone number string (various formats)
  - Output: valid pytz timezone string OR None
  - Guarantee: US numbers → America/* timezones
  - Guarantee: Invalid input → None (no exceptions)
```

**Step 4: Test Type**
```
UNIT test - pure function, no DB/state
```

**Step 5: Fixtures**
```
NO fixtures needed - simple string inputs
```

**Step 6-7: Code**
```python
class TestInferTimezoneFromPhone:
    """Test timezone inference from phone numbers."""

    def test_valid_us_phone_returns_us_timezone(self):
        """
        Valid US phone numbers should return a US timezone.

        Contract test: validates that US numbers map to America/* timezones
        without depending on exact phonenumbers library output that could change.
        Ensures cronjobs run in user's local timezone.
        """
        # Test various US formats
        test_numbers = [
            "+14155551234",  # With country code
            "4155551234",     # Without country code
            "415-555-1234",   # With dashes
        ]

        for phone in test_numbers:
            result = infer_timezone_from_phone(phone)

            # Test OUR contract, not library internals
            assert result is not None, f"Should infer timezone for {phone}"
            assert result.startswith("America/"), f"US number should return America/* timezone"
            assert pytz.timezone(result) is not None  # Valid timezone

    def test_different_us_regions_return_different_timezones(self):
        """
        Different US regions should map to different timezones.

        Validates that the wrapper preserves geographic precision for
        accurate scheduling across time zones.
        """
        california = infer_timezone_from_phone("+14155551234")
        new_york = infer_timezone_from_phone("+12125551234")

        assert california is not None
        assert new_york is not None
        assert california != new_york, "Different regions should have different timezones"

    def test_invalid_phone_numbers_return_none(self):
        """
        Invalid phone numbers should return None.

        Critical for fallback logic - we need to know when inference
        failed so we can use the fallback timezone instead of crashing.
        """
        invalid_numbers = [None, "", "not a phone", "123"]

        for phone in invalid_numbers:
            result = infer_timezone_from_phone(phone)
            assert result is None, f"Invalid number {phone} should return None"
```

**Golden Rule:**
If these tests fail, we broke:
- The guarantee that US phone numbers return US timezones
- The guarantee that invalid input doesn't crash (returns None)
- The preservation of geographic precision (different regions)

### Example 2: Database Logic (Intervention Creation)

**User:** "Write tests for `create_intervention`"

**Step 1-3: Analysis**
```
Code type: Business logic with database models
Dependencies: Database (SQLAlchemy), Message model, User model
Contract:
  - Creates Intervention in DB with correct relationships
  - Sets state to PENDING
  - Links to message and user correctly
  - Returns created intervention
```

**Step 4: Test Type**
```
INTEGRATION test - tests DB operations and model interactions
```

**Step 5: Fixtures**
```
YES - need mock_message, mock_user, test_db_session
Complex DB setup with relationships
```

**Step 6-7: Code**
```python
class TestCreateIntervention:
    """Test intervention creation business logic."""

    def test_create_intervention_sets_correct_relationships(
        self,
        test_db_session: Session,
        mock_message,
        mock_user,
    ):
        """
        Creating an intervention should link it to the message and user.

        Ensures data integrity and enables querying interventions by
        user or message for analytics and debugging.
        """
        # Arrange: Use fixtures for complex DB setup
        message = mock_message()
        user = mock_user()

        # Act: Execute business logic
        intervention = create_intervention(message, user)

        # Assert: Verify business rules
        test_db_session.refresh(intervention)
        assert intervention.message_id == message.id
        assert intervention.user_id == user.id
        assert intervention.state == InterventionState.PENDING

    def test_create_intervention_fails_without_consent(
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
        # Arrange
        message = mock_message()
        user = mock_user(has_consented=False)

        # Act & Assert: Should raise
        with pytest.raises(ValueError, match="User has not consented"):
            create_intervention(message, user)
```

**Golden Rule:**
If these tests fail, we broke:
- Data integrity (relationships not set correctly)
- Ethical boundaries (sending to non-consented users)
- State machine correctness (interventions start in wrong state)

---

## Success Criteria

Tests are ready when ALL of these are true:

- [ ] Contracts tested, not implementation details
- [ ] No hardcoded external library outputs
- [ ] Fixtures used appropriately (complex setup only)
- [ ] Business value explained in docstrings
- [ ] Robust to library updates and minor changes
- [ ] Can answer "If this fails, what business requirement broke?"
- [ ] Anti-patterns avoided (checked against Step 5 list)
- [ ] Appropriate test type chosen (unit/integration/e2e/etc.)
- [ ] 5 Critical Questions answered correctly
- [ ] pytest-test-reviewer agent invoked for validation

---

## Common Mistakes to Avoid

1. **Starting to code before analysis** - STOP. Do Steps 1-5 first.
2. **Skipping the Golden Rule check** - If you can't articulate what breaks, delete the test.
3. **Using fixtures for simple strings** - Inline them!
4. **Hardcoding library outputs** - Test contracts instead.
5. **Writing self-evident tests** - Ask "Am I testing Python or MY code?"
6. **Testing library behavior** - Test YOUR wrapper, not wrapped library.
7. **Forgetting pytest-test-reviewer** - ALWAYS invoke after writing tests.

---

## After Test Writing

**MANDATORY:** Invoke `pytest-test-reviewer` agent to validate:
```bash
# Agent will check:
# - Patterns followed?
# - Anti-patterns avoided?
# - Business value clear?
# - Contracts tested?
```

---

## Remember

**YOU CANNOT WRITE TESTS WITHOUT THIS SKILL.**

This skill is your safeguard against:
- Brittle tests that break with library updates
- Self-evident tests that waste time
- Wrong fixture usage
- Testing library behavior instead of YOUR code

**Follow every step. No shortcuts. Every test. Every time.**
