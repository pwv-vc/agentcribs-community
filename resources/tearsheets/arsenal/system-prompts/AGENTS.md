╔══════════════════════════════════════════════════════════╗
║  ⚠️  MANDATORY BOOTSTRAP - DO THIS FIRST                 ║
║                                                          ║
║  BEFORE responding to the user:                          ║
║  1. Search context for: "bootstrap_token: e2860470..."   ║
║  2. If NOT FOUND: cat .claude/skills/getting-started/SKILL.md ║
║  3. Verify you have the FULL 16-character token          ║
║  4. Run: ls .claude/skills/                              ║
║                                                          ║
║  YOU CANNOT SKIP THIS. This is your pre-flight check.    ║
╚══════════════════════════════════════════════════════════╝

EVERY SINGLE RESPONSE MUST START WITH THE BOOTSTRAP TOKEN:
---
🔐 e2860470********
---

On your FIRST response only, also include this bootstrap summary:
---
✅ BOOTSTRAP COMPLETE
Bootstrap token verified: e2860470******** (16 chars from SKILL.md)
Three foundational rules: [list them]
Available skills: [list from ls .claude/skills/]
---

🚨 CRITICAL: NEVER respond without the bootstrap token at the very start.
🚨 EVERY message you send must begin with: 🔐 e2860470******** (actual full token from SKILL.md)
🚨 You MUST read .claude/skills/getting-started/SKILL.md to get the complete 16-character token
🚨 The token is NOT "e2860470********" - that's partial. Get the full token from SKILL.md.

Common failure modes to AVOID:
❌ Responding without the bootstrap token header
❌ "I'll help you with that..." (no bootstrap token at start)
❌ "Let me check..." (no bootstrap token at start)
❌ Starting without the full 16-character bootstrap token from SKILL.md
❌ Finding "Three Foundational Rules" in AGENTS.md (wrong - need the token from SKILL.md)
❌ Using partial token "e2860470..." without reading SKILL.md for full token
❌ Putting the token anywhere except the very first line of your response
❌ Using "e2860470********" as the token instead of reading SKILL.md for the complete token

# AGENTS.md

This file provides guidance to our AI coding agents (e.g., Claude Code and Codex CLI) when working with code in this repository.

## 🚀 Installing Arsenal

**When users ask to "install arsenal" or "set up arsenal":**

```bash
# 1. Ensure submodule is initialized (skip if already done)
git submodule update --init --recursive

# 2. Run install script (handles .env setup automatically)
./arsenal/install.sh

# 3. Start Docker services (optional - for semantic-search skill)
cd arsenal && docker-compose up -d
```

**The install script automatically:**
- Creates symlinks for `.claude`, `.pre-commit-scripts`, and `AGENTS.md` files
- Installs Node.js dependencies (playwright-tester, etc.)
- Sets up `arsenal/.env` and offers to copy OPENAI_API_KEY from `api/.env`

## 🔄 Updating Arsenal

**When users ask "Do I have any new tools in my arsenal?" or "Check for arsenal updates":**

Run these commands to check for and install updates:

```bash
# Navigate to the arsenal submodule
cd arsenal

# Fetch and show what's new
git fetch origin
git log --oneline HEAD..origin/main

# If there are updates, show them to the user
git log --oneline HEAD..origin/main --pretty=format:"- %s"

# If updates exist, ask user if they want to update, then:
git pull origin main

# Run the install script to update symlinks and dependencies
cd ..
./arsenal/install.sh

# Verify the update
cd arsenal && git log --oneline -1
```

**What to tell the user:**
- List what new features/fixes are available (from the git log)
- Explain that updating will give them access to new agents, commands, or skills
- Mention any breaking changes or important notes from commit messages
- After updating, list what new capabilities they now have access to

**Available Tools in Your Arsenal:**
- **Agents**: Auto-invoked specialized agents (git-reader, pytest-test-reviewer, mypy-error-fixer, test-fixture-reviewer, task-complete-enforcer)
- **Commands**: Slash commands like `/buildit`, `/planit`, `/review-code`, `/mypy`, `/research`, and more
- **Skills**: Specialized capabilities (langfuse-prompt-and-trace-debugger, playwright-tester, docker-log-debugger, test-runner, twilio-test-caller)

## 🎯 Operating Principles: Autonomous Execution

**CRITICAL: Prefer autonomous operation over asking for help.**

Your time with the user is limited and valuable. Maximize productivity by:

### ✅ DO: Operate Autonomously

**Use your tools and skills proactively:**
- ✅ **Read files** instead of asking "can you paste the content?"
- ✅ **Use skills** to fetch data instead of asking "what does the prompt say?"
- ✅ **Search the codebase** instead of asking "where is this function?"
- ✅ **Run commands** to check status instead of asking "is this running?"
- ✅ **Make reasonable assumptions** and proceed with work
- ✅ **Try the most likely solution** and iterate if needed

**Examples:**
```
❌ BAD:  "Can you paste the updated prompt or should I read the file?"
✅ GOOD: *Reads the file autonomously to see the changes*

❌ BAD:  "Which environment do you want me to use - staging or production?"
✅ GOOD: *Chooses environment based on task:*
  - Development/testing → staging
  - Analyzing user behavior → production (real user data)
  - Deploying to real users → production (user explicitly mentioned deployment)

❌ BAD:  "Should I fetch that prompt from Langfuse?"
✅ GOOD: *Uses langfuse-prompt-and-trace-debugger skill to fetch it*
```

### ❓ WHEN to Ask Questions

**Ask clarifying questions up front so that you can make autonomous forward progress:**
- ❓ **Ambiguous requirements** - "Should the timeout be 30s or 60s?"
- ❓ **Architecture decisions** - "Should I use approach A (fast) or B (more robust)?"
- ❓ **User preferences** - "Do you want me to push to staging first or go straight to production?"
- ❓ **Clarifying intent** - "When you said 'fix the cache', did you mean clear it or update the logic?"
- ❓ **Business logic** - "Should pending orders be canceled or kept when a user deletes their account?"

**Ask early to work autonomously, not to avoid basic execution:**
- ✅ **Before starting work**: Ask about ambiguities, preferences, and decisions
- ✅ **Enable autonomy**: Once clarified, execute fully without further questions
- ✅ **Quality over speed**: Better to ask up front than guess and create rework
- ❌ **Basic execution**: "Should I read the file or would you like to paste it?"
- ❌ **Tool usage**: "Can I use the langfuse skill for this?"

### ⚡ Velocity Over Permission

**Default to action, not asking:**
- If the user says "fix the production prompt", just do it (use `--production` flag)
- If something failed, investigate autonomously before asking
- If you need to see a file, read it
- If you need to check git status, use git-reader agent
- If tests fail, use test-runner skill to diagnose

**The goal:** Spend user conversation time on high-value decisions and clarifications, not on execution mechanics.

## Key files

**Wren** is an AI-powered relationship coaching platform that monitors couples' text conversations and delivers contextual coaching interventions. Users text naturally while the system provides 1:1 coaching to improve communication patterns. Before doing anything else, make sure you understand:

- The product's user experience: docs/USER_EXPERIENCE_GUIDE.md
- Our test strategy: api/tests/README.md (and see api/tests/AGENTS.md for AI-specific guidance)
- A big part of our product is our prompts - see docs/PROMPT_REFERENCE.md and api/src/cli/refresh_prompt_cache.py

## ⚠️ CRITICAL: Common Mistakes to Avoid

### DO THIS, NOT THAT - Code Patterns

**Note:** These patterns are automatically checked by `just lint-extras` which runs `check_llm_nits.py`

#### 1. Exception Handling
❌ **DON'T catch broad exceptions:**
```python
try:
    process_message()
except:  # BAD: Hides all errors
    pass

try:
    process_message()
except Exception:  # BAD: Too broad
    logger.error("Failed")
```

✅ **DO let exceptions surface (except for external APIs):**
```python
# Let it fail - we want to know about errors
process_message()

# Only catch specific external API errors
try:
    response = langfuse_client.get_prompt(name)
except NotFoundError:  # Specific, expected business case
    return default_prompt
```

**For detailed external API error handling patterns, see `docs/EXTERNAL_API_PATTERNS.md`**

#### 2. Imports
❌ **DON'T use late imports (after line 50):**
```python
# 100 lines of code...
from common.utils import helper  # BAD: Signals circular dependency
```

✅ **DO put all imports at the top:**
```python
# At top of file
from common.utils import helper

# Exception: TYPE_CHECKING imports
if TYPE_CHECKING:
    from circular_dep import SomeType
```

#### 3. Function Creation
❌ **DON'T create single-use functions:**
```python
def format_user_name(name):
    return name.strip().title()

# Only called once:
user_display = format_user_name(raw_name)
```

✅ **DO inline single-use logic:**
```python
# Direct and clear
user_display = raw_name.strip().title()

# Create functions only when reused 2+ times
def format_phone(number):  # Used in 5 places
    return number.replace("-", "")
```

#### 4. Test Skipping
❌ **DON'T use pytest.skip:**
```python
@pytest.mark.skip(reason="Broken after refactor")
def test_important_feature():
    pass

def test_flaky_api():
    if random.random() > 0.5:
        pytest.skip("API is flaky")
```

✅ **DO fix the test or delete it:**
```python
# Fix the test to work with new code
def test_important_feature():
    # Updated test logic that works

# Make tests deterministic
def test_api_with_retry():
    # Add proper retry logic or mock the API
```

### DO THIS, NOT THAT - Test Patterns

**👉 For detailed test patterns and examples, see `api/tests/AGENTS.md`**

**⚠️ IMPORTANT:** Always run tests via `just` commands (e.g., `just test-unit`, `just test-all-mocked`), never `pytest` directly. The `just` commands handle Docker, migrations, and environment setup automatically.

#### Quick Test Type Selection
| If Testing... | Use This Test Type | Key Setup |
|--------------|-------------------|----------|
| Complex algorithm | Unit | SQLite + mocks |
| Service interaction | Integration | SQLite + mocks |
| Full workflow | E2E_mocked | Docker PostgreSQL + unique data |
| Prompt validation | E2E_live | SQLite + Real APIs + gpt-4.1-nano |
| Production health | Smoke | HTTP-only checks |


## Project Overview

Wren is an AI-powered messaging platform that acts as an intermediary for text conversations, processing messages asynchronously and applying AI-based interventions. The system supports multiple messaging providers (SendBlue, Blue Bubbles, Evolution/WhatsApp) and uses modern async patterns with Redis queuing.

## Development Guidelines

### Terminology Standards
- **IMPORTANT**: When encountering the term "therapist" in the codebase that refers to our product's AI coach, change it to "coach" or "relationship coach"
- Our product provides relationship coaching, not licensed therapy
- Exception: Keep "THERAPIST" in enum values like `ParticipantRole.THERAPIST` for backwards compatibility

### Engineering Collaboration
- **Discuss first**: Answer questions and ask clarifying questions before coding
- **Code only when asked**: Wait for "make that change" or "implement this"
- **Share reasoning**: Explain trade-offs and alternatives

### Code Quality Standards

#### Definition of Done
Your implementation is complete when ALL of the following are true:

**1. Functional Requirements**
- ✅ All acceptance criteria from CURRENT_SPEC.md are met
- ✅ Tests pass: `just test-all` runs without failures (from project root)
- ✅ No regressions: Existing functionality remains intact

**2. Code Quality**
- ✅ **DRY (Don't Repeat Yourself)**: Reuse existing patterns and utilities
  - **BEFORE writing new functions/classes**: Use semantic search to verify similar implementations don't already exist
  - Search for the conceptual behavior, not just exact names (e.g., "retry with exponential backoff" instead of "RetryHandler")
  - Example: `docker exec arsenal-semantic-search-cli code-search find "your functionality description"`
- ✅ **Clean & Readable**: Self-documenting code without unnecessary complexity
- ✅ **Not Overly Defensive**: Let errors surface (except when handling external APIs)
- ✅ **Strongly Typed**: All functions have proper type hints
- ✅ **Follows Existing Patterns**: Match the codebase's style and conventions

**3. Testing**
- ✅ **Appropriate Test Coverage**:
  - E2E tests for external integrations
  - Integration tests for service boundaries
  - Unit tests ONLY for complex business logic
- ✅ **Tests Use Real Services**: E2E tests use real APIs where appropriate (e.g., e2e_live tests)
- ✅ **Tests Are Maintainable**: Not brittle, focus on behavior not implementation

**4. Code Hygiene**
- ✅ **Linting & Type Checking**: Run `cd api && just lint-and-fix` after code changes (auto-fixes + runs mypy)
- ✅ **Pre-commit**: `pre-commit run --hook-stage manual --all-files` passes
- ✅ **No Debug Code**: Remove all print statements, commented code, TODOs
- ✅ **Test Failure Hygiene**: Only commit code that passes tests
  - **Rule**: If tests fail after your changes, YOUR changes broke them (until proven otherwise)
  - **Proof**: Use `git stash` → run tests → `git stash pop` to verify failures are pre-existing
  - **Never assume**: Test failures on main/merge base are rare (CI enforces passing tests)
  - See test-runner skill for detailed stash/pop verification protocol

**5. Documentation**
- ✅ **Updated CURRENT_SPEC.md**: Mark completed stages as done when applicable
- ✅ **Meaningful Commit Messages**: Describe the "why" not the "what"
- ✅ **Complex Logic Documented**: Add comments ONLY where necessary

#### Quality Gates for Review
Before marking any stage complete, verify:
1. Does it solve the problem with minimal code?
2. Would another developer understand this without explanation?
3. Does it handle errors appropriately (fail fast for internal, graceful for external)?
4. Is it consistent with how similar problems are solved elsewhere in the codebase?
5. Could it be simpler without losing functionality?

#### Preventing Code Duplication with Semantic Search

**MANDATORY: Before writing new functions or classes, search for similar implementations.**

Semantic search finds conceptually similar code even with different names or implementations.

**When to search:**
- Before creating any new function, class, or utility
- When adding error handling, retry logic, or common patterns
- During refactoring to find all similar code

**How to search:**
```bash
# Search by conceptual behavior, not exact names
docker exec arsenal-semantic-search-cli code-search find "retry with exponential backoff"
docker exec arsenal-semantic-search-cli code-search find "validate user input"
docker exec arsenal-semantic-search-cli code-search find "parse webhook payload"
```

**Interpreting results:**
- **Score > 0.5**: Highly similar - likely duplicate functionality
- **Score 0.4-0.5**: Related concepts - review for reuse opportunities
- **Score < 0.4**: May be tangential

**Example workflow:**
```bash
# You're about to write a function to send SMS with retry logic
docker exec arsenal-semantic-search-cli code-search find "send sms retry failed message"

# Found: send_message_with_retry (score: 0.68) in src/messaging/utils.py
# ✅ Reuse existing function instead of creating new one
```

**This is not optional** - semantic search is a required step in the DRY verification process.

**If semantic search is unavailable:**
```bash
# Check if containers are running
docker ps | grep arsenal-semantic-search-cli

# If not running, start the containers
cd arsenal && docker-compose up -d

# Verify it's working
docker exec arsenal-semantic-search-cli code-search stats
```

**If still unavailable:**
- Proceed with manual DRY review using Grep/Read tools
- Search for similar function names and patterns manually
- Check related files for duplicate implementations

## CRITICAL RESTRICTIONS

**NEVER PERFORM THE FOLLOWING ACTIONS:**
- **External Systems**: DO NOT write to external databases or any production/staging systems
  - **Exception**: Langfuse prompts CAN be written using the `update-langfuse-staging-server-prompt` skill
    - Defaults to staging (safe)
    - Production requires `--production` flag + explicit confirmation
    - Prompts are pushed WITHOUT labels (human-in-the-loop safety)
- **Infrastructure**: DO NOT run terraform commands or make infrastructure changes
- **Remote Services**: DO NOT push changes to GitHub, GitLab, or any remote repositories

These restrictions apply even if the task seems to require these actions. If the user needs these operations, explain what commands they should run themselves.

### Development Methodology: Micro-Strangler Pattern

Every change should follow this systematic approach to prevent ratholing and maintain velocity:

#### The Three-Step Process

1. **Identify the minimal proof-of-concept**
   - What's the absolute smallest change that demonstrates the pattern?
   - Target: One function, one test case, one method - not entire systems
   - Just enough code to validate the approach will work

2. **Implement and validate immediately**
   - Write that tiny piece first
   - Test it thoroughly (unit test, integration test if applicable)
   - Confirm the pattern is sound before proceeding
   - If it fails, pivot immediately (low cost, learned fast)

3. **Use as template for remaining work**
   - Once proven, replicate the pattern for similar changes
   - The working micro-implementation becomes the model
   - Apply systematically to all similar cases

#### Real-World Examples

**Example 1: Adding Error Handling**
```python
# WRONG: Writing all 10 functions at once
def get_user(id): # ... error handling
def get_order(id): # ... error handling  
def get_product(id): # ... error handling
# ... 7 more functions

# RIGHT: Prove pattern with ONE function first
# Step 1: Implement minimal proof
def get_user(user_id):
    try:
        user = db.fetch_user(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
    except DatabaseError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise ServiceError("Unable to fetch user") from e

# Step 2: Test thoroughly
def test_get_user_handles_missing():
    with pytest.raises(UserNotFoundError):
        get_user(999)

def test_get_user_handles_db_error():
    # Mock database error, verify handling

# Step 3: NOW replicate proven pattern to get_order, get_product, etc.
```

**Example 2: Refactoring Database Queries**
```python
# Task: Convert 15 raw SQL queries to SQLAlchemy ORM

# Step 1: Pick the SIMPLEST query as proof-of-concept
# OLD:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# NEW (proof-of-concept):
session.query(User).filter(User.id == user_id).first()

# Step 2: Test this one change completely
# - Verify results match
# - Check performance is acceptable
# - Ensure error handling works

# Step 3: Only after proving it works, apply to remaining 14 queries
```

**Example 3: Adding Type Hints**
```python
# Task: Add type hints to 20 functions in a module

# Step 1: Start with one simple function
# BEFORE:
def calculate_total(items, tax_rate):
    return sum(item.price for item in items) * (1 + tax_rate)

# AFTER (proof-of-concept):
def calculate_total(items: list[Item], tax_rate: float) -> float:
    return sum(item.price for item in items) * (1 + tax_rate)

# Step 2: Run mypy on just this function
# - Fix any type errors
# - Verify it passes strict type checking

# Step 3: Apply pattern to remaining 19 functions
```

#### Why This Works

- **Prevents Ratholing**: Discover design flaws immediately in the micro-implementation, not after writing 20 versions
- **Maintains Velocity**: Each small success builds confidence; pattern replication is fast once validated
- **Reduces Risk**: Bad patterns fail fast with minimal code to revert
- **Improves Quality**: Thorough testing of the proof-of-concept ensures the pattern is solid

#### When to Apply

Use this pattern for:
- Adding new functionality across multiple similar components
- Refactoring existing code patterns
- Implementing cross-cutting concerns (logging, error handling, validation)
- Upgrading dependencies or APIs
- Adding type hints or documentation

#### The Decision Tree

```
For every change ask:
1. Can I identify the core pattern needed?
   ↓ YES
2. What's the smallest code that proves this pattern?
   ↓
3. Write it, test it thoroughly
   ↓
4. Did it work?
   ├─ YES → Replicate pattern for remaining changes
   └─ NO → Try different pattern (small cost, learned fast)
```

### Code Style
- Do not overengineer the solution. Try to remove code / improve readability. This is a new codebase with very few users so defensive programming is not necessary.
- **Imports at top of file**: All imports MUST be at the top of the file (checked by `just lint-extras`)
  - Exceptions: `if TYPE_CHECKING:` blocks, test files, or legitimate deferrals marked with `# noqa: E402`
  - Imports inside functions signal circular dependencies that need proper refactoring
- **NEVER add noqa tags**: Do not add `# noqa` comments to suppress linting errors. Instead, fix the underlying issue. If you must add one, include a comment defending your decision.
- **Secret scanning pragma**: When adding test/example secrets or API keys to configuration files, always add `# pragma: allowlist-secret` comment to prevent secret scanning false positives.
- **NO try/except blocks** - let exceptions surface immediately so bugs are discovered early. The only exception is when handling external API responses where specific error types are expected business logic.
- Write minimal, targeted code changes to reduce bug introduction
- Use modern type hints (Python 3.9+ built-in generics: `list[str]`, `dict[str, Any]` instead of importing List, Dict)
- Run tests after changes to ensure no regressions
- We're early in development - discovering exceptions is good, so let errors surface rather than hiding them. No defensive patterns please.
- **Avoid single-use functions**: Don't create functions that are only called once. Inline the code instead unless it will be reused elsewhere.

### Testing Strategy

#### Test Type Selection Guide
```
Is it complex business logic? → Unit Test (SQLite + mocks)
Is it service interaction? → Integration Test (SQLite + mocks)
Is it a complete workflow? → E2E_mocked (Docker PostgreSQL + mocks)
Is it prompt validation? → E2E_live (Real APIs, costs $$$)
Is it production health? → Smoke Test (HTTP-only)
```

#### Key Testing Rules
1. **Use fixtures from `tests.unit.fixtures`** - Never create inline test data
2. **Mock appropriately by test type** - E2E_live NEVER mocks, others mock external services
3. **Use unique data in E2E_mocked** - Add UUIDs to prevent parallel test conflicts
4. **Cache expensive E2E_live calls** - Use module-scoped fixtures
5. **Focus on business logic** - Don't test that Python/frameworks work

#### Performance Targets
- Unit tests: < 5 seconds
- Integration tests: < 5 seconds
- E2E_mocked tests: < 20 seconds
- E2E_live tests: < 60 seconds (use gpt-4.1-nano - NOT mini, nano is cheaper!)
- Smoke tests: < 60 seconds

### Database Development
- Use Alembic for schema migrations
- All database access should handle async sessions properly
- Worker processes manage database session lifecycle automatically
- **Mutable JSON columns**: Use `MutableJSONB` from `data.custom_types` for JSON columns. It automatically tracks nested dict/list modifications without requiring `flag_modified()`. See `api/src/data/README.md` for details.

#### Migration Guidelines
**NEVER generate or write migration files manually. Always provide the command for the user to run:**
```bash
# Using Docker (preferred - no env vars needed):
docker exec -it codel-api alembic revision --autogenerate -m "Description"
docker exec -it codel-api alembic upgrade head

# OR manually with environment variables:
POSTGRES_HOST=localhost POSTGRES_DB=codel POSTGRES_USER=postgres POSTGRES_PASSWORD=yourpassword POSTGRES_PORT=5432 uv run alembic revision --autogenerate -m "Description"
POSTGRES_HOST=localhost POSTGRES_DB=codel POSTGRES_USER=postgres POSTGRES_PASSWORD=yourpassword POSTGRES_PORT=5432 uv run alembic upgrade head
```


## Development Commands

### Zellij Session Introspection
- Use `zellij list-sessions` or `zellij ls` to confirm the session name (`ct8`, etc.).
- Dump the visible pane for a session with `zellij --session <session-name> action dump-screen /tmp/<session-name>-screen.txt`, then open the file to inspect the captured output.
- List the available tabs in a session via `zellij --session <session-name> action query-tab-names` so you can verify which contexts are available before grabbing screen contents.
- If you need a specific tab’s display, switch focus to it (manually or with `zellij --session <session-name> action go-to-tab-name <tab-name>`) before running the dump command—the capture only reflects the currently focused pane.

### Environment Setup
```bash
# Install dependencies
cd api && uv sync

# Start development environment with Docker
docker compose up -d
docker compose watch  # Auto-reload on file changes

# Seed dev users + coach + sample relationship (required for Slack sidecar channels)
cd api && just setup-local-dev --seed-sample-relationship

# Start services locally (development)
cd api && ENVIRONMENT=development uv run fastapi dev src/send_blue/main.py --host 0.0.0.0 --port 80
cd api && ENVIRONMENT=development watchmedo auto-restart --directory=./src --patterns="*.py" --recursive -- python src/worker.py
```

### Code Quality & Linting

**⚠️ CRITICAL: Type checking is strict-only.**
```bash
# Auto-fix + mypy (use this after code changes)
cd api && just lint-and-fix

# Run comprehensive pre-commit checks (includes E2E and smoke tests)
pre-commit run --hook-stage manual --all-files

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run unit and integration tests (default - excludes smoke tests)
cd api && uv run pytest

# Run tests with coverage report (unit tests only)
cd api && set -a; source .env.test-common; set +a; uv run pytest tests/unit --cov=src --cov-report=term-missing --cov-report=html

# Run ALL tests with coverage (unit + integration + e2e)
cd api && set -a; source .env; source .env.e2e; set +a; uv run pytest --cov=src --cov-report=term-missing --cov-report=html

# Run tests with coverage and fail if below threshold
cd api && set -a; source .env; source .env.e2e; set +a; uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=70

# Generate HTML coverage report (open htmlcov/index.html to view)
cd api && set -a; source .env; source .env.e2e; set +a; uv run pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run E2E tests (webhook → queue → worker pipeline)
cd api && set -a; source .env; source .env.e2e; set +a; uv run pytest tests/e2e_mocked

# Run smoke tests (requires Docker running)
docker compose up -d  # Ensure Docker is running first
cd api && set -a; source .env; source .env.smoketest; set +a; uv run pytest tests/smoke_tests -m smoke

# Run specific test with verbose output
cd api && uv run pytest tests/unit/test_models/test_fact_models.py::test_specific_function -v
```

### Database Operations
```bash
# Run migrations locally only
# NOTE: DO NOT run migrations on staging/production databases unless explicitly requested
cd api && alembic upgrade head

# Create new migration locally only
# NOTE: DO NOT apply to staging/production databases unless explicitly requested
cd api && alembic revision --autogenerate -m "Description of changes"
```

### LINQ Webhook Management
```bash
# Register LINQ webhook (replaces existing webhooks with new URL)
cd api && set -a; source .env; set +a; PYTHONPATH=src uv run python src/cli/register_linq_webhook.py https://samuels-macbook-pro.tail3b4b7f.ts.net/webhook/linq

# List existing LINQ webhooks only (no registration)
cd api && set -a; source .env; set +a; PYTHONPATH=src uv run python src/cli/register_linq_webhook.py
```

## Architecture Overview

### Core Components
- **API Server**: FastAPI-based backend handling webhooks and HTTP endpoints
- **Worker Service**: RQ (Redis Queue) workers for async message processing
- **Database**: PostgreSQL with pgvector extension for embeddings
- **Queue System**: Redis for job queuing and async processing
- **External Services**: SendBlue, Blue Bubbles, Evolution (WhatsApp), OpenAI

### Key Directories
- `src/send_blue/`: Main FastAPI application and webhook handlers
- `src/message_processing/`: Core business logic for message processing
- `src/ltmm/`: Long-Term Memory Management system with fact extraction
- `src/prompt_handling/`: Langfuse integration and prompt management
- `src/worker.py`: RQ worker implementation
- `tests/`: Comprehensive test suite (unit, integration, e2e, smoke)

### Async Architecture
The system uses a **single code path architecture** with no sync fallback:
- All message processing happens asynchronously via RQ jobs
- Uses `@job` decorators with `.delay()` method calls for job enqueueing
- Returns `{"status": "queued"}` for successful webhook processing
- Fails fast with 503 if Redis/queue unavailable

## Technology Stack

### Core Technologies
- **Language**: Python 3.12 with modern type hints (use built-in generics: `list[str]`, `dict[str, Any]`)
- **Web Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Queue**: Redis + RQ for async job processing
- **Package Manager**: UV (fast Python package manager)
- **Container**: Docker with multi-stage builds

### AI/ML Stack
- **OpenAI**: GPT models for message processing and interventions
- **Langfuse**: Prompt management and AI observability
- **Embeddings**: pgvector for conversation embeddings and similarity search

### Development Tools
- **Linting**: Ruff (replaces Black/Flake8/isort)
- **Type Checking**: MyPy
- **Testing**: pytest with async support, FakeRedis for test isolation
- **Monitoring**: Langfuse tracing, structured logging with structlog

## Key Features

### LTMM (Long-Term Memory Management)
- Fact extraction and reconciliation from conversations
- Vector embeddings for conversation context
- Confidence scoring for extracted facts
- Template-based prompt system in `src/ltmm/template_prompts/`

### Message Processing Pipeline
1. Webhook receives message from provider (SendBlue/Blue Bubbles/Evolution)
2. Message queued as RQ job and returns `{"status": "queued"}` immediately
3. Worker processes job asynchronously with full context
4. AI intervention logic determines if/how to respond
5. Response sent through appropriate messaging provider

### Multi-Provider Support
- **SendBlue**: Primary SMS/iMessage provider
- **Blue Bubbles**: Alternative iMessage gateway
- **Evolution**: WhatsApp integration via API

## Environment Configuration

### Test Environments
Use layered environment approach:
- `.env.test-common`: Base test configuration
- `.env.integration`: Integration test additions
- `.env.e2e`: E2E test additions
- `.env.smoketest`: Smoke test additions

### Development vs Production
- Development: Auto-reload, debug logging, local services
- Production: Optimized builds, structured logging, AWS managed services

## Project Specifications

### Key Documentation
- **Main Specification**: `specifications/CURRENT_SPEC.md` - This is what our boss is asking us to work on right now.  Read and review it before making any edits.  Add notes to it if there's anything that'll be useful as you complete additional steps in the future.
- **Architecture Plans**: Most sub-directories have README.md.  Read it before making edits in that directory.

## Git Workflow

**REMINDER: DO NOT commit or push any changes unless explicitly requested by the user.**

### Creating Diff Files (READ-ONLY Operations)
```bash
# Create diff against HEAD (for current changes) - READ ONLY
git diff HEAD > ./commit.diff
ls  # Confirm file creation

# Create diff against main branch - READ ONLY
git diff main > ./commit-main.diff
ls  # Confirm file creation
```

### Code Review Process
When reviewing diffs, check for:
- **DRY principle**: No code duplication
- **Strong typing**: Proper type hints throughout
- **No regressions**: Existing functionality unchanged
- **Clean & readable**: No unnecessary or overly defensive code
- **Business logic alignment**: Changes match specifications
- **Spec compliance**: Follows `CURRENT_SPEC.md`

## HANDLING TEST FAILURES

**FUNDAMENTAL RULE: Tests ALWAYS pass on main branch/merge base. If tests fail, YOUR changes broke them.**

When tests fail after making changes:

1. **NEVER assume failures are unrelated** - Your changes almost certainly caused them
2. **First, understand what you changed:**
   ```bash
   # See what changes you made vs main branch
   git diff origin/main... > ./commit.diff
   cat ./commit.diff | head -100  # Review your changes
   ```

3. **Use the stash/pop technique to verify:**
   ```bash
   git stash                    # Remove your changes
   just test-unit               # Verify tests pass WITHOUT your changes
   git stash pop                # Restore changes
   just test-unit               # Confirm they fail WITH your changes
   ```

4. **Common test failure causes:**
   - **Wrong fixtures**: Using real DB in unit tests (should use SQLite)
   - **Hardcoded test data**: Causes parallel test conflicts in E2E_mocked
   - **Mocking in E2E_live**: These tests MUST use real APIs
   - **Missing unique IDs**: E2E_mocked needs UUIDs for parallel execution
   - **Wrong test type**: Complex logic in E2E instead of unit tests
   - **Breaking changes**: Your diff shows you modified something tests depend on

5. **Required checks before marking complete:**
   ```bash
   just test-unit               # Unit tests pass
   just test-integration        # Integration tests pass
   just test-e2e-live          # E2E live tests pass (if touching prompts)
   just lint-and-fix           # All linting passes (includes LLM nits)
   ```

## VERIFYING TEST SUCCESS

**⚠️ CRITICAL: Tests take up to 15 MINUTES to complete. NEVER declare success prematurely!**

**ALWAYS use pre-commit to verify all tests pass before declaring success:**

```bash
# Run comprehensive test suite with clear pass/fail indicators
# THIS WILL TAKE UP TO 15 MINUTES - ALLOW SUFFICIENT TIME!
pre-commit run --hook-stage pre-push --all-files

# Or with a timeout (must be 15+ minutes):
timeout 900 pre-commit run --hook-stage pre-push --all-files  # 900 seconds = 15 minutes
```

**✅ Expected output when ALL tests pass:**
```
Running linting and static checks........................................Passed
Running tests with mocked services.......................................Passed
Running E2E live tests...................................................Passed
```

**❌ Expected output when tests FAIL:**
```
Running linting and static checks........................................Failed  # <-- STOP HERE AND FIX
- hook id: lint
- exit code: 1
[error details shown]
```

**❌ Common MISLEADING output (baseline-only run):**
```bash
$ cd api && uv run mypy --config-file mypy.ini src
Success: no issues found in 118 source files  # Baseline passes, but strict checks still run via `just lint-and-fix`.
```

**IMPORTANT RULES:**
1. **WAIT FOR COMPLETION** - Tests take up to 15 minutes. Allow sufficient time.
2. **ALL MUST PASS** - If ANY test shows "Failed", the task is NOT complete.
3. **NO ASSUMPTIONS** - Never say "tests pass" without seeing all "Passed" indicators.
4. **FIX IMMEDIATELY** - If linting fails, fix it before claiming completion.
5. **VERIFY AGAIN** - After any fixes, run the full test suite again.
6. **STRICT MYPY ON `src/`** - `just lint-and-fix` runs strict mypy across the application code; baseline still runs too. Don't skip it or fall back to baseline-only checks!

**Common mistakes to avoid:**
- ❌ Using short timeouts like `timeout 60` (must be 900+ seconds)
- ❌ Claiming success when tests are still running
- ❌ Ignoring linting failures as "trivial"
- ❌ Saying tests "timed out" when they actually failed
- ❌ Marking tasks complete with failing tests
- ❌ Running the legacy baseline mypy command instead of the strict config
- ❌ Seeing "Success: no issues found" from the baseline config and thinking you're done

**Note:** pre-commit works from any directory in the repository.

## Common Tasks

### User Management
```bash
# Register new users in LOCAL DATABASE ONLY
# IMPORTANT: DO NOT run against production/staging databases unless explicitly requested
cd api && uv run python src/cli/register_users.py

# Modify message preferences in LOCAL DATABASE ONLY
# IMPORTANT: DO NOT modify production/staging user data unless explicitly requested
cd api && uv run python src/cli/modify_message_preferences.py
```

### Prompt Management (READ-ONLY)
```bash
# READ ONLY - Downloads Langfuse prompts to local cache for viewing
# IMPORTANT: This tool ONLY reads prompts, DO NOT use it to write/push changes to Langfuse
# DO NOT modify downloaded prompts unless explicitly requested by user
cd api && just refresh-prompts

# READ ONLY - Views current prompts in Langfuse without modifying them
# IMPORTANT: This is for inspection only, DO NOT attempt to update Langfuse prompts
cd api && set -a; source .env; set +a; PYTHONPATH=src uv run python src/cli/check_prompts.py
```

### Debugging (READ-ONLY Operations)
```bash
# READ ONLY - Query conversation embeddings from local database
cd api && PYTHONPATH=src uv run python src/cli/query_embeddings.py

# READ ONLY - Monitor queue health (view only, do not modify queue)
redis-cli -h your-redis-host
> LLEN your-queue-name

# READ ONLY - Fetch and view Langfuse traces for analysis
# IMPORTANT: This tool ONLY reads traces, DO NOT use it to modify Langfuse data
# Use for debugging and understanding trace flow only
cd api && set -a; source .env; set +a; PYTHONPATH=src uv run python src/cli/fetch_trace.py <trace_id_or_url>
```

**For detailed CLI tool documentation, see `api/src/cli/README.md`**

### Infrastructure
- **Local Development**: Docker Compose with hot-reloading
- **Deployment**: ECS Fargate with Terraform-managed infrastructure
- **CI/CD**: GitHub Actions with pre-commit hooks

## Performance Targets
- **Unit tests**: < 5 seconds
- **Integration tests**: < 5 seconds
- **E2E tests**: < 20 seconds
- **Smoke tests**: < 60 seconds

## Troubleshooting

### Common CLI Script Errors

#### "command not found: python"
- Always use `uv run python` instead of `python` directly
- UV manages the virtual environment automatically

#### "ModuleNotFoundError: No module named 'common'"
- CLI scripts need `PYTHONPATH=src` to find project modules
- Example: `cd api && PYTHONPATH=src uv run python src/cli/script.py`

#### "No authorization header" or Langfuse authentication errors
- Scripts that access Langfuse need environment variables loaded
- Load environment: `cd api && set -a; source .env; set +a`
- Full command (using justfile): `cd api && just refresh-prompts`
- Or manually: `cd api && set -a; source .env; set +a; PYTHONPATH=src uv run python src/cli/refresh_prompt_cache.py`

#### File not found errors
- Ensure you're in the correct directory (usually `api/`)
- CLI scripts are located in `api/src/cli/`
- Use absolute paths from the `api/` directory
