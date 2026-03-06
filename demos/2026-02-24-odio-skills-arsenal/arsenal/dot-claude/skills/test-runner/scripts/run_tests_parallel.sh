#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find project root by looking for api/ directory
# Start from script dir and walk up until we find it
ROOT_DIR="${SCRIPT_DIR}"
while [ ! -d "${ROOT_DIR}/api" ] && [ "${ROOT_DIR}" != "/" ]; do
  ROOT_DIR="$(cd "${ROOT_DIR}/.." && pwd)"
done

if [ ! -d "${ROOT_DIR}/api" ]; then
  echo "Could not locate project root with api/ directory." >&2
  echo "Searched from: ${SCRIPT_DIR}" >&2
  exit 1
fi

API_DIR="${ROOT_DIR}/api"
LOG_DIR="${API_DIR}/tmp/test-logs"

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Define log files with timestamps
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MOCKED_LOG="${LOG_DIR}/test-mocked_${TIMESTAMP}.log"
E2E_LOG="${LOG_DIR}/test-e2e-live_${TIMESTAMP}.log"
SMOKE_LOG="${LOG_DIR}/test-smoke_${TIMESTAMP}.log"

echo "Starting parallel test runs..."
echo "Logs will be saved to: ${LOG_DIR}"
echo ""
echo "Mocked tests: ${MOCKED_LOG}"
echo "E2E Live tests: ${E2E_LOG}"
echo "Smoke tests: ${SMOKE_LOG}"
echo ""
echo "Watch logs with:"
echo "  tail -f ${MOCKED_LOG}"
echo "  tail -f ${E2E_LOG}"
echo "  tail -f ${SMOKE_LOG}"
echo ""

# Run tests in parallel, capturing output and exit codes
cd "${API_DIR}"

(just test-all-mocked > "${MOCKED_LOG}" 2>&1; echo $? > "${LOG_DIR}/.mocked_exit") &
MOCKED_PID=$!

(just test-e2e-live > "${E2E_LOG}" 2>&1; echo $? > "${LOG_DIR}/.e2e_exit") &
E2E_PID=$!

(just test-smoke > "${SMOKE_LOG}" 2>&1; echo $? > "${LOG_DIR}/.smoke_exit") &
SMOKE_PID=$!

echo "Tests running in background (PIDs: mocked=${MOCKED_PID}, e2e=${E2E_PID}, smoke=${SMOKE_PID})"
echo ""
echo "Check if tests are still running:"
echo "  ps -p ${MOCKED_PID},${E2E_PID},${SMOKE_PID}"
echo ""
echo "Or use 'jobs' to see background jobs in this shell session"
echo ""

# Exit immediately, leaving tests running in background
exit 0
