# Semantic Code Search Skill

A Claude Code skill that provides semantic code search using vector embeddings. Find functions, classes, and code by **meaning** rather than exact text matching.

## Overview

This skill uses:
- **PostgreSQL with pgvector** for vector similarity search
- **OpenAI embeddings** (text-embedding-3-small) for semantic understanding
- **Python AST parsing** for accurate code extraction
- **Docker containers** for isolated, portable deployment

## Installation

### Automatic (via superpowers install.sh)

When you run `./superpowers/install.sh` in your project, you'll be prompted to set up semantic-search:

```bash
./superpowers/install.sh
# Follow prompts, enter OpenAI API key when asked
# The key will be saved to superpowers/.env
```

### Manual Setup

```bash
# 1. Configure OpenAI API key
cd superpowers
cp .env.example .env
# Edit .env and add your OpenAI API key

# 2. Start containers (from superpowers directory)
docker-compose up -d --build

# 3. Wait for database to be ready (about 10 seconds)
sleep 10

# 4. Index your codebase
docker exec superpowers-semantic-search-cli code-search index /project --clear

# 5. Verify setup
docker exec superpowers-semantic-search-cli code-search stats
```

## Usage

### Search for Code
```bash
# Find authentication code
docker exec superpowers-semantic-search-cli code-search find "user authentication login verification"

# Find webhook handlers
docker exec superpowers-semantic-search-cli code-search find "handle incoming webhook messages"

# Find database operations
docker exec superpowers-semantic-search-cli code-search find "save data to PostgreSQL database"

# More results (default is 5)
docker exec superpowers-semantic-search-cli code-search find "async processing" --limit 10
```

### View Statistics
```bash
docker exec superpowers-semantic-search-cli code-search stats
```

### Re-index After Code Changes
```bash
docker exec superpowers-semantic-search-cli code-search index /project --clear
```

## How Claude Code Uses This

When installed, Claude Code can automatically use this skill when:
- You ask "Where is the code that handles X?"
- You ask "How do we implement Y?"
- Traditional grep searches aren't finding what you need

Example interaction:
```
You: "Where do we handle Twilio webhooks?"

Claude: *Uses semantic-search skill*
        docker exec code-search-cli code-search find "Twilio webhook incoming calls"

        Found in api/routes/webhooks.py:45 - handle_incoming_call function
```

## Architecture

```
superpowers/
└── dot-claude/
    └── skills/
        └── semantic-search/
            ├── SKILL.md              # Instructions for Claude Code
            ├── README.md             # This file (for humans)
            ├── docker-compose.yml    # Container orchestration
            ├── Dockerfile            # Python app container
            ├── requirements.txt      # Python dependencies
            ├── init.sql             # Database schema
            ├── .env.example         # Environment template
            └── src/
                ├── cli.py           # Command-line interface
                ├── indexer.py       # AST-based code parsing
                ├── embeddings.py    # OpenAI integration
                └── database.py      # PostgreSQL/pgvector ops
```

## Configuration

### Environment Variables

Configuration is centralized in `superpowers/.env`:
```bash
# superpowers/.env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://codesearch:codesearch@postgres:5432/codesearch  # (optional, default is fine)
```

All superpowers skills share this configuration file for easier management.

### Docker Compose

- **Orchestration**: Centralized at `superpowers/docker-compose.yml`
- **Postgres Port**: 5433 (host) → 5432 (container)
- **Project Mount**: `..:/project:ro` (parent of superpowers, read-only)
- **Container Names**: `superpowers-semantic-search-cli`, `superpowers-semantic-search-db`
- **Volume**: `semantic-search-data` (persists embeddings)

## Performance

- **Search Speed**: <1 second
- **Index Speed**: ~5 files/second
- **Memory**: ~100MB for 1000 functions
- **Storage**: ~1KB per function

## Maintenance

### View Logs
```bash
cd superpowers
docker-compose logs -f semantic-search-cli
docker-compose logs -f semantic-search-db
```

### Restart Services
```bash
cd superpowers
docker-compose restart semantic-search-cli semantic-search-db
```

### Stop Services
```bash
cd superpowers
docker-compose stop semantic-search-cli semantic-search-db
```

### Full Reset (deletes all indexed data)
```bash
cd superpowers
docker-compose down -v
docker-compose up -d --build
docker exec superpowers-semantic-search-cli code-search index /project --clear
```

## Troubleshooting

### Container Not Running
```bash
# Check status
docker ps -a | grep superpowers-semantic-search

# Start containers
cd superpowers
docker-compose up -d
```

### No Search Results
```bash
# Verify index exists
docker exec superpowers-semantic-search-cli code-search stats

# Re-index if needed
docker exec superpowers-semantic-search-cli code-search index /project --clear
```

### OpenAI API Errors
```bash
# Check if key is set
docker exec superpowers-semantic-search-cli env | grep OPENAI_API_KEY

# Set key in .env file
echo "OPENAI_API_KEY=sk-..." >> superpowers/.env

# Restart containers
cd superpowers
docker-compose restart
```

### Port Conflicts (5433)
If port 5433 is already in use, edit `superpowers/docker-compose.yml`:
```yaml
services:
  semantic-search-db:
    ports:
      - "5434:5432"  # Use different port
```

## Limitations

- Currently only indexes Python files
- Requires OpenAI API key (costs ~$0.01 per 1000 functions indexed)
- Read-only mount prevents indexing changes to source from container

## Future Enhancements

- [ ] Multi-language support (JavaScript, TypeScript, Go, Rust)
- [ ] Local embedding models (no OpenAI dependency)
- [ ] Incremental indexing (only new/changed files)
- [ ] Code similarity recommendations
- [ ] Integration with IDE extensions

## License

MIT

## Credits

Part of the Superpowers collection for Claude Code.
