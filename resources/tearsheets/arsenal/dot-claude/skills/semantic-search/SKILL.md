---
name: semantic-search
description: "INVOKE BEFORE writing new code to find existing implementations (DRY). Also for codebase exploration and production data search. Run: docker exec arsenal-semantic-search-cli code-search find 'query'"
---

# Semantic Search

Semantic search tool that uses vector embeddings to find code, messages, and facts by **meaning** rather than exact text matching.

**Two search domains:**
1. **Code search** (`find`) - Search indexed Python functions/classes
2. **Production data search** (`find-messages`, `find-facts`) - Search user messages and facts in production database

## When to Use

**Code search** - Use proactively when:
- User asks "how do I..." or "where is the code that..."
- Looking for functions by purpose (e.g., "authentication", "database queries", "webhook handling")
- Traditional grep fails to find relevant code
- Exploring unfamiliar codebases

**Production data search** - Use proactively when:
- Analyzing user feedback or product issues
- Finding patterns in user messages (e.g., "users confused about...")
- Searching facts about users or relationships
- Debugging why certain prompts failed
- Looking for similar user situations across couples

## Prerequisites

The skill requires:
1. Docker and Docker Compose installed
2. OpenAI API key (for generating embeddings)
3. Codebase indexed (done during install.sh or manually)

**Check if installed:**
```bash
docker ps | grep semantic-search
```

**If not running:**
```bash
cd .claude/skills/semantic-search && docker-compose up -d
```

## Primary Commands

### Search Semantically
```bash
# Find authentication code
docker exec arsenal-semantic-search-cli code-search find "user authentication login verification"

# Find webhook handlers
docker exec arsenal-semantic-search-cli code-search find "handle incoming webhook messages"

# Find database operations
docker exec arsenal-semantic-search-cli code-search find "save data to PostgreSQL database"

# Find API endpoints
docker exec arsenal-semantic-search-cli code-search find "HTTP request routing webhooks"

# More results (default is 5)
docker exec arsenal-semantic-search-cli code-search find "async processing" --limit 10
```

### View Statistics
```bash
docker exec arsenal-semantic-search-cli code-search stats
```

### Re-index After Code Changes
```bash
# Re-index entire codebase (clears old index)
docker exec arsenal-semantic-search-cli code-search index /project --clear

# Index without clearing
docker exec arsenal-semantic-search-cli code-search index /project
```

## Production Data Search (Messages & Facts)

Search user messages and facts in the production database semantically. Requires production database credentials in `arsenal/.env`.

### Search Messages
```bash
# Find messages about confusion with the app
docker exec arsenal-semantic-search-cli code-search find-messages "users confused about how to use the app"

# Find product feedback
docker exec arsenal-semantic-search-cli code-search find-messages "feature request or suggestion"

# Search with custom time range (default: 7 days)
docker exec arsenal-semantic-search-cli code-search find-messages "feeling unheard" --hours 720  # 30 days

# Limit results
docker exec arsenal-semantic-search-cli code-search find-messages "money stress" --limit 20
```

### Search Facts
```bash
# Find facts about relationship patterns
docker exec arsenal-semantic-search-cli code-search find-facts "feeling unheard in relationship"

# Find facts about communication styles
docker exec arsenal-semantic-search-cli code-search find-facts "avoidant attachment style"

# Adjust confidence threshold (default: 0.6)
docker exec arsenal-semantic-search-cli code-search find-facts "trigger words" --confidence 0.8
```

### Example Output (Messages)
```
Searching messages for: users confused about how to use the app
Time range: last 168 hours
--------------------------------------------------------------------------------

Found 5 results:

1. [0.847] Person 42 (ONE_ON_ONE)
   Time: 2025-12-09 04:42
   I'm confused though - am I supposed to use the app or the group thread?

2. [0.812] Person 87 (ONE_ON_ONE)
   Time: 2025-12-06 04:49
   I wasnt asking for coaching but to still provide my answers in the group thread...
```

### Example Output (Facts)
```
Searching facts for: feeling unheard in relationship
Min confidence: 0.6
--------------------------------------------------------------------------------

Found 5 results:

1. [0.891] Person 15 - trigger
   Confidence: 0.85
   Feels dismissed when his perspective is labeled rather than validated

2. [0.834] Person 23 - communication_style
   Confidence: 0.78
   Tends to shut down when feeling criticized
```

## How It Works

1. **AST Parsing**: Extracts all Python functions and classes with signatures and docstrings
2. **OpenAI Embeddings**: Generates 1536-dimensional vectors using text-embedding-3-small model
3. **pgvector**: Stores vectors in PostgreSQL with vector similarity extension
4. **Cosine Similarity**: Finds semantically similar code using IVFFlat index (<1s response time)

## Architecture

- **Database**: PostgreSQL 16 with pgvector extension on port 5430
- **CLI**: Python 3.11 with AST parsing for accurate code extraction
- **Container**: arsenal-semantic-search-cli with mounted project root at /project
- **Storage**: Persistent postgres-data volume for embeddings

## Example Workflows

### Finding Authentication Code
```bash
docker exec arsenal-semantic-search-cli code-search find "user authentication login verification" --limit 10
```

Expected output:
```
Found 3 results:
1. authenticate_user (score: 0.91)
   File: api/auth/handlers.py
   Type: function
   Signature: def authenticate_user(username: str, password: str) -> bool
   Docstring: Verify user credentials against database

2. verify_token (score: 0.85)
   File: api/auth/jwt.py
   Type: function
   Signature: def verify_token(token: str) -> dict
```

### Finding Similar Functions
```bash
# User wants to implement something similar to an existing function
docker exec arsenal-semantic-search-cli code-search find "process webhook payload validate signature"
```

### After Major Code Changes
```bash
# Re-index to include new code
docker exec arsenal-semantic-search-cli code-search index /project --clear

# Verify index updated
docker exec arsenal-semantic-search-cli code-search stats
```

## Integration with Claude Code

When a user asks questions like:
- "Where do we handle webhooks?"
- "How do we authenticate users?"
- "Is there code for sending emails?"

**Workflow:**
1. Use semantic-search to search semantically
2. Read the relevant files found
3. Provide the user with file paths and line numbers

```bash
# User: "Where do we handle Twilio webhooks?"
docker exec arsenal-semantic-search-cli code-search find "Twilio webhook incoming calls"

# Claude reads the top result
Read api/routes/webhooks.py

# Claude responds with context
"Twilio webhooks are handled in api/routes/webhooks.py:45 by the handle_incoming_call function..."
```

## Performance

- **Search Speed**: <1 second for most queries
- **Index Speed**: ~5 files per second
- **Memory Usage**: ~100MB for 1000 functions indexed
- **Storage**: ~1KB per indexed function

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Container not running | `cd arsenal && docker-compose up -d` |
| No results found | Re-index: `docker exec arsenal-semantic-search-cli code-search index /project --clear` |
| OpenAI API error | Verify OPENAI_API_KEY in `arsenal/.env` |
| Database connection error | Check postgres health: `cd arsenal && docker-compose ps` |
| Port conflict (5430) | Edit docker-compose.yml to use different port |
| Stale results | Re-index after code changes |
| Container missing | Check if skill was installed: `ls .claude/skills/semantic-search` |
| Production DB error | Set PGHOST, PGDATABASE, PGUSER, PGPASSWORD in `arsenal/.env` |
| find-messages/find-facts fails | Production credentials not configured (optional feature) |

## Common Issues

### Container Not Found
```bash
# Check if containers exist
docker ps -a | grep semantic-search

# Start containers
cd .claude/skills/semantic-search && docker-compose up -d
```

### Empty Index
```bash
# Verify index exists
docker exec arsenal-semantic-search-cli code-search stats

# If total_elements is 0, re-index
docker exec arsenal-semantic-search-cli code-search index /project --clear
```

### OpenAI API Key Missing
```bash
# Check if key is set in container
docker exec arsenal-semantic-search-cli env | grep OPENAI_API_KEY

# If missing, set in arsenal/.env and restart
cd arsenal
echo "OPENAI_API_KEY=your-key-here" >> .env
docker-compose down && docker-compose up -d
```

## Maintenance

### View Logs
```bash
cd .claude/skills/semantic-search
docker-compose logs -f
```

### Restart Services
```bash
cd .claude/skills/semantic-search
docker-compose restart
```

### Full Reset
```bash
cd arsenal
docker-compose down -v  # Warning: deletes all indexed data
docker-compose up -d
docker exec arsenal-semantic-search-cli code-search index /project --clear
```

## Tips for Effective Searching

1. **Use descriptive queries**: "handle user authentication with JWT tokens" is better than "auth"
2. **Include context**: "save conversation to database with embeddings" vs "save database"
3. **Try variations**: If no results, rephrase the query
4. **Check stats first**: Verify index is populated before searching
5. **Re-index often**: After pulling new code or major changes

## Quick Reference

```bash
# 🔥 Search for code
docker exec arsenal-semantic-search-cli code-search find "your semantic query here"

# 🔥 Search production messages (requires DB credentials)
docker exec arsenal-semantic-search-cli code-search find-messages "your query" --hours 168

# 🔥 Search production facts (requires DB credentials)
docker exec arsenal-semantic-search-cli code-search find-facts "your query"

# 🔥 View index statistics
docker exec arsenal-semantic-search-cli code-search stats

# 🔥 Re-index codebase
docker exec arsenal-semantic-search-cli code-search index /project --clear

# 🔥 Check if running
docker ps | grep arsenal-semantic-search

# 🔥 Start containers
cd arsenal && docker-compose up -d

# 🔥 View logs
cd arsenal && docker-compose logs -f semantic-search-cli
```

## Configurable Table Search

Production data search is **configurable** via `tables.yaml`. You can add new tables to search by defining them in the config file.

### List Available Tables
```bash
docker exec arsenal-semantic-search-cli code-search list-tables
```

### Config File Format
Edit `arsenal/dot-claude/skills/semantic-search/tables.yaml`:

```yaml
tables:
  # Each key becomes a "find-{key}" command
  messages:
    table: message              # Database table name
    alias: m                    # SQL alias (must be unique)
    description: "Search user messages semantically"
    content_column: content     # Column with searchable text
    embedding_column: embedding # Column with vector embedding
    display_columns:            # Columns to show in results
      - "m.id"
      - "m.content"
      - "m.provider_timestamp"
      - "p.id as sender_id"
    joins:                      # Optional JOINs for enriching results
      - "JOIN persons p ON m.person_id = p.id"
    filters:
      time_column: provider_timestamp  # Enables --hours filter
      default_hours: 168
      # OR
      confidence_column: confidence    # Enables --confidence filter
      default_min_confidence: 0.6
```

### Adding a New Searchable Table

1. Add the table definition to `tables.yaml`
2. Restart the container: `docker-compose restart semantic-search-cli`
3. The new `find-{name}` command is automatically available

Example - adding conversation search:
```yaml
tables:
  conversations:
    table: conversation
    alias: conv
    description: "Search conversations by summary"
    content_column: summary
    embedding_column: summary_embedding
    display_columns:
      - "conv.id"
      - "conv.summary"
      - "conv.type"
    joins: []
    filters:
      time_column: created_at
      default_hours: 720
```

After restart: `code-search find-conversations "relationship conflict"`

## Notes

- Default project mount: `/project` (parent of arsenal directory)
- Database port: 5430 (avoids conflicts with other PostgreSQL instances)
- Container names: `arsenal-semantic-search-cli`, `arsenal-semantic-search-db`
- Embeddings model: OpenAI text-embedding-3-small (1536 dimensions)
- Only Python files are currently indexed (future: multi-language support)
- Index persists across container restarts via Docker volume
- **Production data search is configurable** - define tables in `tables.yaml`
- Requires PGHOST, PGDATABASE, PGUSER, PGPASSWORD in `arsenal/.env` for production search
- Code search works standalone without production database credentials
