# Testing Guidelines - CRITICAL PATTERNS

## ⚠️ DO THIS, NOT THAT - Test Patterns

### 1. Test Setup
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

### 2. Test Mocking
❌ **DON'T mock everything or use mock chains:**
```python
# Over-mocking
mock.query.return_value.filter.return_value.first.return_value = user

# Wrong mocking for test type
# In E2E_live test:
with patch('openai.ChatCompletion.create'):  # NEVER mock live services (OpenAI, Langfuse, SendBlue, etc.) in e2e_live!
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

### 3. Test Assertions
❌ **DON'T test obvious Python behavior:**
```python
# Testing that Python works
user.name = "Alice"
assert user.name == "Alice"  # Self-evident

# Testing framework features
assert session.commit() is None  # SQLAlchemy always returns None
```

❌ **DON'T use hardcoded expected values from formatters:**
```python
# BAD: Hardcoded string breaks when format changes
def test_form_to_message():
    message = create_message_from_form({"relationship_type": "romantic"})
    assert "romantic relationship" in message.lower()  # Brittle!
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

✅ **DO compute expected values using actual formatting methods:**
```python
# GOOD: Uses the same formatting logic being tested
def test_form_to_message():
    message = create_message_from_form({"relationship_type": "romantic"})
    expected = RELATIONSHIP_TYPE_FIELD.to_message("romantic")
    assert expected and expected.lower() in message.lower()
```

### 4. Test Organization
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
    # IMPORTANT: Use gpt-4.1-nano (NOT gpt-4.1-mini) - nano is newer and cheaper!
    return openai.complete(model="gpt-4.1-nano")  # gpt-4.1-nano EXISTS and is the cheapest!
```

### 5. Test Documentation
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

## Quick Reference

**Performance Targets:** Unit (<5s) • Integration (<5s) • E2E_mocked (<20s) • E2E_live (<60s using gpt-4.1-nano) • Smoke (<60s)

**Test Pyramid:**
```
🔺 Smoke (Real PostgreSQL + Real Redis + HTTP-only checks)
🔺🔺 E2E_live (SQLite + FakeRedis + Real APIs)
🔺🔺🔺 E2E_mocked (Docker PostgreSQL + FakeRedis + Mocked APIs)
🔺🔺🔺🔺 Integration (SQLite + FakeRedis + Mocked APIs)
🔺🔺🔺🔺🔺 Unit (SQLite + FakeRedis + Mocked APIs)
```

## Test Types Summary

| Test Type | Purpose | Database | Redis | External Services |
|-----------|---------|----------|-------|-------------------|
| **Unit** | Complex/critical logic only | SQLite in-memory | FakeRedis | All mocked |
| **Integration** | Component interactions | SQLite in-memory | FakeRedis | All mocked |
| **E2E_mocked** | Critical workflows | Docker PostgreSQL | FakeRedis | All mocked |
| **E2E_live** | Live prompt testing | SQLite in-memory | FakeRedis | Real APIs + gpt-4.1-nano ($$) |
| **Smoke** | Production health checks | Real PostgreSQL | Real Redis | Real/HTTP only |

## CRITICAL: What NOT to Test (Self-Evident Truths)

**NEVER write tests that verify self-evident truths. These provide zero value:**

### ❌ ANTI-PATTERNS TO AVOID:
```python
# BAD: Testing that setting a value works
def test_setting_state():
    participant.state = ConversationState.ACTIVE
    assert participant.state == ConversationState.ACTIVE  # Self-evident!

# BAD: Testing that mocks return what you told them to return
def test_mock_returns_value():
    mock.get_value.return_value = 42
    assert mock.get_value() == 42  # Of course it does!

# BAD: Testing Python built-ins
def test_dict_merge():
    result = {**dict1, **dict2}
    assert len(result) == len(dict1) + len(dict2)  # Testing Python, not our code!

# BAD: Testing simple operators
def test_not_operator():
    value = not True
    assert value == False  # Testing Python's 'not' operator!

# BAD: Testing that adding 1 item makes count 1
def test_list_count():
    items = []
    items.append("item")
    assert len(items) == 1  # Self-evident!
```

## ✅ What TO Test (Business Logic)

**Focus on testing BUSINESS LOGIC and DECISIONS, not implementation details:**

### Good Test Patterns:
```python
# GOOD: Testing business rule combinations
@pytest.mark.parametrize(
    "sender_interventions,recipient_interventions,expected_should_send",
    [
        (False, False, True),   # No recent interventions → send reminder
        (True, False, False),   # Sender has interventions → don't spam
        (False, True, False),   # Recipient has interventions → don't spam
    ]
)
def test_daily_reminder_business_logic(sender_interventions, recipient_interventions, expected_should_send):
    """Tests that daily reminders respect intervention cooldown periods to prevent message fatigue."""
    # Tests actual business logic decision-making

# GOOD: Testing edge cases and boundaries
def test_upcoming_facts_date_window():
    """Tests that reminders only trigger for events 1-7 days in future, not today or far future."""
    # Tests specific business rule about timing windows

# GOOD: Testing error handling
def test_invalid_preference_raises_error():
    """Tests that corrupted user preferences fail loudly to prevent undefined behavior."""
    with pytest.raises(ValueError, match="Invalid intervention_level"):
        # Tests that system handles bad data correctly

# GOOD: Testing data transformations
def test_fact_extraction_from_message():
    """Tests that user preferences are correctly extracted from natural language."""
    # Tests complex logic that parses and interprets data
```

## Test Type Details

### Unit Tests (./unit/)
**Purpose**: Test complex business logic in isolation
**Database**: SQLite in-memory | **Redis**: FakeRedis | **APIs**: All mocked
**Speed**: <5s total

**When to Use:**
- Complex algorithms (intervention trigger logic, fact extraction)
- Business rule combinations
- Edge cases and boundaries
- Data transformations

**Key Pattern - Use Shared Fixtures:**
```python
# ✅ GOOD: Using shared fixtures from tests.unit.fixtures
def test_logic(mock_session, mock_message, mock_conversation):
    # Clean test with injected fixtures

# ❌ BAD: Creating data inline
def test_logic():
    mock_session = Mock()  # NO! Use fixtures!
```

### Integration Tests (./integration/)
**Purpose**: Test component interactions and API endpoints
**Database**: SQLite in-memory | **Redis**: FakeRedis | **APIs**: All mocked
**Speed**: <5s total

**When to Use:**
- Service interactions
- Database operations
- API endpoint contracts
- FastAPI TestClient validation

**Key Pattern - Test Real Components:**
```python
def test_webhook_processing(client, test_db_session):
    """Tests webhook correctly processes incoming messages."""
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200

    # Verify database state
    message = test_db_session.query(Message).first()
    assert message.content == "Test message"
```

### E2E Mocked Tests (./e2e_mocked/)
**Purpose**: Test complete workflows with mocked external services
**Database**: Docker PostgreSQL (shared!) | **Redis**: FakeRedis | **APIs**: All mocked
**Speed**: <20s total

**⚠️ CRITICAL - Parallel Execution Requirements:**
```python
# ✅ GOOD: UUID-based unique identifiers
def test_workflow():
    unique_id = str(uuid.uuid4())[:8]
    user_name = f"TestUser_{unique_id}"

# ❌ BAD: Hardcoded values cause conflicts
def test_workflow():
    user_name = "TestUser"  # Will conflict in parallel tests!
```

**Key Pattern - Full Pipeline Testing:**
```python
def test_high_conflict_intervention_flow(client, test_db_session, process_jobs_sync):
    """Tests complete flow: webhook → queue → worker → intervention."""
    # Send message via webhook
    response = client.post("/webhook", json=conflict_message)

    # Process queued jobs synchronously
    process_jobs_sync()

    # Verify intervention created
    intervention = test_db_session.query(Intervention).first()
    assert intervention is not None
```

### E2E Live Tests (./e2e_live/) 💰
**Purpose**: Validate prompts with REAL LLMs
**Database**: SQLite in-memory | **Redis**: FakeRedis | **APIs**: REAL (costs money!)
**Speed**: <60s total

**⚠️ CRITICAL - These Tests Cost Real Money!**
- Uses REAL OpenAI, Langfuse, SendBlue APIs
- Default model: `gpt-4.1-nano` for cost efficiency
- Cache responses at module level
- Test only critical prompt validation

**Key Pattern - Real API Testing:**
```python
def test_prompt_works_with_real_gpt():
    """REAL OpenAI call - validates prompt engineering"""
    response = generate_intervention(
        message="You never listen!",
        context=build_conversation_context(),
    )
    assert len(response) > 50
    assert "coach" in response.lower()  # Not "therapist"

def test_langfuse_prompts_exist():
    """REAL Langfuse - ensures prompts deployed"""
    prompt = langfuse_client.get_prompt("intervention_generator")
    assert "{{message}}" in prompt.template
```

**Cost Minimization:**
```python
# Cache expensive operations
@pytest.fixture(scope="module")
def gpt_response_cache():
    return {}

# Use cheapest model unless testing specific features
OPENAI_MODEL_OVERRIDE=gpt-4.1-nano
```

### Smoke Tests (./smoke_tests/)
**Purpose**: Production health validation
**Database**: Real PostgreSQL (via API) | **Redis**: Real Redis (via API) | **APIs**: Real
**Speed**: <60s total

**When to Use:**
- Deployment validation
- API availability checks
- Critical endpoint testing
- Production monitoring

**Key Pattern - HTTP Only:**
```python
def test_api_health_check(smoke_config, api_client):
    """HTTP-only check - no direct DB access"""
    response = api_client.get(f"{smoke_config['base_url']}/status")
    assert response.json()["healthy"] is True
```

## Test Patterns & Best Practices

### 1. Fixture-Based Architecture

**Use reusable fixtures instead of inline setup:**

```python
# ❌ BAD: Inline setup in every test
def test_message_processing():
    person1 = Persons(name="Alice")
    person2 = Persons(name="Bob")
    conversation = Conversation(...)
    # 20+ lines of boilerplate

# ✅ GOOD: Clean fixture usage
def test_message_processing(mock_couple_conversation, mock_message):
    conversation, participants = mock_couple_conversation
    result = process_message(conversation, mock_message)
```

**Pattern: Factory fixtures with defaults + overrides**

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
    payload = payload_factory(communication_goals=None, prior_support=[])

def test_custom_data(payload_factory):
    payload = payload_factory(user_name="Bob", relationship_type="co-parenting")
```

❌ **DON'T create multiple fixture variants for the same data structure:**
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

**Shared fixture organization - location hierarchy:**

```
tests/
├── helpers/
│   └── model_factory_fixtures.py    # Model factories shared across ALL suites
├── conftest.py                       # Import shared fixtures for global access
├── integration/
│   └── conftest.py                   # Integration-specific fixtures only
├── e2e_mocked/
│   └── conftest.py                   # E2E-specific fixtures only
└── unit/
    └── conftest.py                   # Unit-specific fixtures only
```

✅ **DO raise common factories to helpers:**
```python
# tests/helpers/model_factory_fixtures.py
@pytest.fixture
def person_factory(test_db_session: "Session") -> Callable:
    """Reusable person factory for all test suites."""
    def _create_person(name: str = None, **overrides):
        defaults = {
            "name": name or f"Person {random.randint(100000, 999999)}",
            "person_global_uuid": f"person-{random.randint(100000, 999999)}",
        }
        defaults.update(overrides)
        person = Persons(**defaults)
        test_db_session.add(person)
        test_db_session.flush()
        return person
    return _create_person

# tests/conftest.py - expose globally
from tests.helpers.model_factory_fixtures import (  # noqa: F401
    person_factory,
    contact_factory,
    conversation_factory,
)
```

❌ **DON'T duplicate factory fixtures across test suites:**
```python
# BAD - duplicated in multiple conftest.py files
# tests/e2e_mocked/conftest.py
@pytest.fixture
def person_factory(): ...

# tests/integration/conftest.py
@pytest.fixture
def person_factory(): ...  # Duplicate!
```

**When to raise a fixture:**
- Used by 2+ test suites → Move to `tests/helpers/`
- Suite-specific setup → Keep in suite's `conftest.py`
- Tests domain logic in isolation → Keep in test file

**Key benefits of factory fixtures:**
- Single source of truth for default values
- Easy to customize per test without duplication
- Follows e2e test patterns (see `test_onboarding_endpoints.py`)
- Reduces maintenance when data structures change

### 2. Business-Focused Documentation
```python
# ✅ GOOD: Explains business value
def test_consent_before_therapy():
    """
    Ensures therapeutic interventions only begin after explicit consent,
    maintaining ethical standards and legal compliance.
    """

# ❌ BAD: Technical description
def test_consent_check():
    """Tests that consent flag is checked."""
```

### 3. Targeted Mocking
```python
# ✅ GOOD: Specific mock
with patch("data.models.message.Message.get_latest_active_messages", return_value=[]):

# ❌ BAD: Mock chain
mock.query.return_value.filter.return_value.all.return_value = []
```

### 4. Dependency Injection
```python
def test_processing(
    mock_session,        # Injected by pytest
    mock_message,        # Injected by pytest
    mock_conversation,   # Injected by pytest
):
    # Test focuses on business logic, not setup
```

### 5. Test Parametrization

**Pattern: Use `@pytest.mark.parametrize` for testing multiple variants of the same logic**

✅ **DO parametrize for common expressable variant patterns:**
```python
# Test multiple field values that should all produce the same behavior
@pytest.mark.parametrize(
    "form_field,field_value,expected_in_fact",
    [
        ("relationship_type", "romantic", "romantic"),
        ("relationship_type", "co-parenting", "co-parenting"),
        ("communication_goals", "better listening", "listening"),
        ("communication_frequency", "daily", "daily"),
    ],
)
def test_form_field_mapping_to_facts(form_field, field_value, expected_in_fact):
    """Tests that form fields map correctly to fact content."""
    # Single test implementation, runs 4 times with different data

# Test role-based or participant-based variants
@pytest.mark.parametrize(
    "person_role,expected_birthday,expected_gender",
    [
        ("initiator", "1990-05-15", "female"),
        ("invitee", "1992-08-20", "male"),
    ],
)
def test_personal_facts_from_participant_forms(person_role, expected_birthday, expected_gender):
    """Tests that each participant's form data creates personal facts."""
    person = initiator if person_role == "initiator" else invitee
    # Test both participants with one implementation

# Test business rule combinations
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

❌ **DON'T write separate tests for each variant:**
```python
# BAD - repetitive, hard to maintain
def test_romantic_relationship_creates_fact():
    assert "romantic" in facts

def test_coparenting_relationship_creates_fact():
    assert "co-parenting" in facts

def test_friendship_relationship_creates_fact():
    assert "friendship" in facts

# GOOD - single parametrized test
@pytest.mark.parametrize("relationship_type", ["romantic", "co-parenting", "friendship"])
def test_relationship_type_creates_fact(relationship_type):
    assert relationship_type in facts
```

**When to parametrize:**
- Testing same logic with different input values
- Verifying multiple roles/participants behave correctly
- Testing boundary conditions (min, max, edge cases)
- Testing business rule matrices (combinations of conditions)

**When NOT to parametrize:**
- Tests have different setup requirements
- Tests verify completely different behavior
- Parametrization would make test intent unclear

## Running Tests

```bash
# All tests (excludes smoke by default)
cd api && uv run pytest

# Specific test suites
cd api && just test-unit             # Unit tests only
cd api && just test-integration      # Integration tests
cd api && just test-e2e              # E2E tests
cd api && just test-smoke            # Smoke tests (requires Docker)

# E2E Live (costs money!)
cd api && (set -a; source .env; source .env.e2e_live; set +a; uv run pytest tests/e2e_live)

# With coverage
cd api && uv run pytest --cov=src --cov-report=html
```

## Configuration

### Smoke Test Environment Variables
```bash
SMOKE_TEST_API_BASE_URL=http://api:80  # Docker: api:80, Local: localhost:8080
SMOKE_TEST_API_KEY=test-api-key
SMOKE_TEST_SENDBLUE_USER_1_HANDLE=+5542984348739
SMOKE_TEST_SENDBLUE_USER_2_HANDLE=+5542999713956
SENDBLUE_SIGNING_SECRET=test_signing_secret
```

### E2E Live Cost Control
```bash
OPENAI_MODEL_OVERRIDE=gpt-4.1-nano  # Cheapest model
```

## Quick Decision Tree

When writing a test, ask yourself:

1. **Am I testing a business decision or rule?** → Write the test
2. **Am I testing that Python/framework features work?** → Don't write it
3. **Am I testing what I just set/mocked?** → Don't write it
4. **Would this test catch a real bug?** → Write the test
5. **Would this test help someone understand the system?** → Write the test
6. **Is this test just for coverage percentage?** → Don't write it

## Golden Rule

**If a test fails, what business requirement did we break?**

If you can't answer that question clearly, the test shouldn't exist.

## Common Issues & Solutions

### E2E Live Issues
- **"prompt not found"**: Run `cd api && PYTHONPATH=src uv run python src/cli/refresh_prompt_cache.py`
- **Rate limits**: Reduce parallel execution
- **High costs**: Verify using `gpt-4.1-nano`

### E2E Mocked Issues
- **Tests fail intermittently**: Check for hardcoded values, use UUIDs
- **Database lock timeouts**: Batch operations, reduce commits
- **Tests pass alone but fail together**: Ensure unique test data

### General Issues
- **ModuleNotFoundError**: Add `PYTHONPATH=src` prefix
- **Authentication errors**: Load environment with `source .env`
