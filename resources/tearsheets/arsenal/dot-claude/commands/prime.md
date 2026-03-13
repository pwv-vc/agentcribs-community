# Prime
> Build initial understanding of codebase structure and current work.
>
> **When to use**: First conversation in new worktree, after long break, major refactoring
> **When to skip**: Bug fixes, small features, test debugging, PR reviews
>
> **Token Impact**: ~5-10k tokens (~5% of context)

## Run
git ls-files | awk -F'/' 'NF<=3'  # Show files up to 2 directories deep
git status
grep '^##\? ' README.md | head -50  # Get README structure without reading the entire file

## Read
QUICKSTART.md

## Refresh Prompt Cache (Optional)
cd api && just refresh-prompts

## Note
- **Superpowers bootstrap already loaded** via session-start-hook (getting-started skill, mandatory workflows)
- AGENTS.md is already loaded as a memory file - no need to read again
- README.md structure shown via grep - read specific sections as needed
- For deep-dives, read focused docs separately:
  - Testing patterns: `api/tests/AGENTS.md`
  - Prompt system: `docs/PROMPT_REFERENCE.md`
  - Full setup details: `README.md` sections 2-3

**Remember:** After ANY code change, use test-runner skill (ruff → lint → test-all-mocked → full suite)
