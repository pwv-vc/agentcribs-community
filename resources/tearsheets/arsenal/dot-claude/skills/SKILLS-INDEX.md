# Skills Index

Available skills for this project. The skill-router hook injects this reference on every user prompt.

## How It Works

1. User sends a message
2. skill-router hook (UserPromptSubmit) injects this index reference
3. Claude checks this index for matching skills
4. If a skill matches user intent, Claude uses it

## Available Skills

<!-- AUTO-GENERATED:SKILLS-TABLE:START -->
| Skill | When to Use |
|-------|-------------|
| `aws-logs-query` | Query AWS CloudWatch logs for staging and production environments |
| `brainstorming` | Collaborative idea-to-spec workflow for designing features |
| `citations` | Include clickable links when referencing entities (persons, conversations) |
| `couple-weekly-report` | Generate weekly relationship health report with affect ratios |
| `docker-log-debugger` | Find and debug errors using Docker Compose logs |
| `feature-spec-writer` | PM framework for writing product specs from insights |
| `funnel-analysis` | Analyze user conversion funnels and identify drop-off points |
| `getting-started` | Bootstrap skill - teaches skill discovery and mandatory usage |
| `git-writer` | Safe workflow for git write operations (git rm) |
| `incomplete-onboarding-assessor` | Assess incomplete onboardings using COLD/WARM/HOT temperature model |
| `langfuse-prompt-and-trace-debugger` | Fetch actual prompt schemas and debug production traces |
| `langfuse-prompt-iterator` | Prompt iteration workflow for debugging and improving Langfuse prompts |
| `linear-manager` | Create, update, search, and comment on Linear issues |
| `manager-review` | Quality gate before responding to user |
| `multi-model-review` | Orchestrate Claude + Codex (or any second model) for adversarial multi-model code review with structured synthesis |
| `nux-first-week-analyzer` | Analyze new user experience in their first week after onboarding |
| `playwright-tester` | Capture screenshots and run E2E tests with Playwright |
| `pm-analyst` | End-to-end PM workflow - from data analysis to Linear tickets |
| `product-analytics` | Framework for analyzing product usage data |
| `project-orchestrator` | Orchestrate multi-phase project implementation |
| `project-planner` | Plan new project or feature implementation |
| `register-twilio-test-audio` | Add new test audio files for Twilio voice calls |
| `sdlc` | SDLC workflow automation (TDD, test-runner, commit, push) |
| `semantic-search` | Find existing implementations before writing new code (DRY) |
| `skill-writer` | Create new skills or edit existing SKILL.md files |
| `sql-reader` | Query production PostgreSQL database with read-only credentials |
| `superpowers-bootstrap` | Bootstrap skill for Superpowers SDLC workflow |
| `tailscale-manager` | Manage Tailscale funnels across different ct project instances |
| `test-driven-development` | Implement features using TDD - write tests first |
| `test-fixer` | Fix failing tests, CI failures |
| `test-runner` | Run tests and lint after EVERY code change |
| `test-twilio` | Place Twilio test calls |
| `test-voice-report` | Test report generation with TEXT transcripts |
| `test-writer` | Write test code (def test_*, class Test*) |
| `relationship-analyst` | Calculate relationship affect ratios |
| `understanding-mistakes` | Post-mortem when something went wrong |
| `update-langfuse-staging-server-prompt` | Push prompt updates to Langfuse (staging or production) |
| `user-segmentation` | Cluster users into behavioral segments and personas |
| `voice-call-report` | Generate voice call reports with transcriptions and scores |
| `voice-e2e-test` | E2E test of voice call pipeline |
| `webapp-testing` | Test local web applications using Playwright |
<!-- AUTO-GENERATED:SKILLS-TABLE:END -->
