#!/bin/bash
set -e

# Project Orchestrator Helper Script
# This script provides utilities for orchestrating project implementation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_ITERATIONS=5
AGENT_TIMEOUT=1800  # 30 minutes in seconds

# Functions

print_header() {
  echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║  $1${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if PROJECT_PLAN.md exists
find_project_plan() {
  local plan_path="$1"

  if [[ -n "$plan_path" ]] && [[ -f "$plan_path" ]]; then
    echo "$plan_path"
    return 0
  fi

  # Search for PROJECT_PLAN.md in docs/specs
  local found_plan=$(find docs/specs -name "PROJECT_PLAN.md" -type f | head -1)

  if [[ -n "$found_plan" ]]; then
    echo "$found_plan"
    return 0
  fi

  return 1
}

# Verify git state is clean
check_clean_state() {
  if [[ -n $(git status -s) ]]; then
    print_error "Uncommitted changes detected"
    echo "Please commit or stash changes before orchestrating"
    return 1
  fi
  return 0
}

# Get current branch
get_current_branch() {
  git rev-parse --abbrev-ref HEAD
}

# Create orchestration directory structure
setup_orchestration_dirs() {
  local project_dir="$1"
  local orch_dir="$project_dir/orchestration"

  mkdir -p "$orch_dir/logs"
  mkdir -p "$orch_dir/reviews"
  mkdir -p "$orch_dir/tasks"

  echo "$orch_dir"
}

# Spawn background agent with timeout monitoring
spawn_agent() {
  local task_file="$1"
  local log_file="$2"
  local timeout="${3:-$AGENT_TIMEOUT}"

  print_info "Spawning agent..."
  print_info "Task: $task_file"
  print_info "Log: $log_file"

  # Spawn agent in background
  claude --dangerously-skip-permissions -p "$(cat $task_file)" \
    > "$log_file" 2>&1 &

  local pid=$!
  echo "$pid"
}

# Monitor agent with timeout
monitor_agent() {
  local pid="$1"
  local timeout="$2"
  local task_name="$3"

  local start_time=$(date +%s)
  local last_update=$start_time

  while kill -0 $pid 2>/dev/null; do
    local elapsed=$(($(date +%s) - start_time))
    local since_update=$(($(date +%s) - last_update))

    # Check timeout
    if [ $elapsed -gt $timeout ]; then
      print_error "Agent timeout after ${timeout}s"
      kill $pid 2>/dev/null
      return 1
    fi

    # Print progress every 30 seconds
    if [ $since_update -ge 30 ]; then
      local mins=$((elapsed / 60))
      local secs=$((elapsed % 60))
      print_info "$task_name in progress... ${mins}m ${secs}s elapsed"
      last_update=$(date +%s)
    fi

    sleep 5
  done

  # Get exit code
  wait $pid
  return $?
}

# Check if review passed
check_review_status() {
  local review_file="$1"

  if [[ ! -f "$review_file" ]]; then
    print_error "Review file not found: $review_file"
    return 1
  fi

  # Extract status
  local status=$(grep "^### Status:" "$review_file" | awk '{print $3}' || echo "UNKNOWN")

  # Count critical and high priority issues
  local critical_count=$(grep -c "Priority: CRITICAL" "$review_file" || echo "0")
  local high_count=$(grep -c "Priority: HIGH" "$review_file" || echo "0")

  print_info "Review Status: $status"
  print_info "Critical issues: $critical_count"
  print_info "High priority issues: $high_count"

  if [[ "$status" == "APPROVED" ]] && [[ $critical_count -eq 0 ]] && [[ $high_count -eq 0 ]]; then
    return 0
  else
    return 1
  fi
}

# Extract phases from PROJECT_PLAN.md
extract_phases() {
  local plan_file="$1"

  # This is a simple implementation - may need enhancement
  # Looks for "### Phase N: Name" patterns
  grep "^### Phase [0-9]" "$plan_file" | sed 's/^### //'
}

# Create phase branch name from phase description
slugify_phase() {
  local phase="$1"
  # Extract phase number and name, convert to slug
  # "Phase 1: Foundation Setup" -> "phase-1-foundation-setup"
  echo "$phase" | tr '[:upper:]' '[:lower:]' | tr ' :' '-' | tr -cd '[:alnum:]-'
}

# Usage information
usage() {
  cat <<EOF
Project Orchestrator Helper Script

Usage: $0 <command> [options]

Commands:
  find-plan [PATH]           Find or verify PROJECT_PLAN.md
  setup-dirs <PROJECT_DIR>   Create orchestration directory structure
  spawn-agent <TASK> <LOG>   Spawn background Claude agent
  check-review <REVIEW_FILE> Check if review passed
  extract-phases <PLAN>      Extract phases from plan

Options:
  -h, --help                 Show this help message

Examples:
  # Find project plan
  $0 find-plan docs/specs/my-project/PROJECT_PLAN.md

  # Setup orchestration directories
  $0 setup-dirs docs/specs/my-project

  # Check review status
  $0 check-review docs/specs/my-project/orchestration/reviews/phase-1.md

Environment Variables:
  AGENT_TIMEOUT              Timeout for agents in seconds (default: 1800)
  MAX_ITERATIONS             Max review/fix iterations (default: 5)

EOF
}

# Main command dispatcher
main() {
  local command="$1"
  shift

  case "$command" in
    find-plan)
      find_project_plan "$@"
      ;;
    setup-dirs)
      setup_orchestration_dirs "$@"
      ;;
    spawn-agent)
      spawn_agent "$@"
      ;;
    check-review)
      check_review_status "$@"
      ;;
    extract-phases)
      extract_phases "$@"
      ;;
    -h|--help)
      usage
      ;;
    *)
      print_error "Unknown command: $command"
      usage
      exit 1
      ;;
  esac
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
