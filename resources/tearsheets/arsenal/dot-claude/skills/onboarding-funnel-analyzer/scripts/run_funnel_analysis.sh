#!/bin/bash
# Onboarding Funnel Analysis Script
# Usage: ./run_funnel_analysis.sh [DAYS]
# Default: 7 days

set -e

DAYS=${1:-7}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Find the project root (where arsenal/ lives) - 4 levels up from scripts/
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
CONNECT_SCRIPT="${PROJECT_ROOT}/arsenal/dot-claude/skills/sql-reader/connect.sh"
OUTPUT_DIR="${SCRIPT_DIR}/../output"

# Verify connect script exists
if [ ! -f "$CONNECT_SCRIPT" ]; then
  echo "Error: Cannot find sql-reader connect.sh at: $CONNECT_SCRIPT"
  echo "SCRIPT_DIR: $SCRIPT_DIR"
  echo "PROJECT_ROOT: $PROJECT_ROOT"
  echo "Make sure you're running from the project root."
  exit 1
fi
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
OUTPUT_FILE="${OUTPUT_DIR}/funnel_analysis_${TIMESTAMP}.md"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Onboarding Funnel Analysis ===${NC}"
echo -e "Time window: ${YELLOW}${DAYS} days${NC}"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Initialize output file
cat > "$OUTPUT_FILE" << EOF
# Onboarding Funnel Analysis

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Time Window:** Last ${DAYS} days

---

EOF

echo -e "${YELLOW}Step 1: Quantitative Funnel Summary${NC}"
echo "" >> "$OUTPUT_FILE"
echo "## Step 1: Quantitative Funnel Summary" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

$CONNECT_SCRIPT "
WITH funnel_data AS (
  SELECT 1 as step_num, 'Form Submitted' as funnel_step,
    COUNT(DISTINCT id) as users
  FROM conversation_onboarding
  WHERE created_at >= NOW() - INTERVAL '${DAYS} days'
    AND form_data->>'name' IS NOT NULL
    AND LENGTH(form_data->>'name') > 1

  UNION ALL

  SELECT 2, 'Messaged Wren',
    COUNT(DISTINCT co.id)
  FROM conversation_onboarding co
  JOIN conversation_participant_onboarding cpo
    ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
  JOIN person_contacts pc ON cpo.person_contact_id = pc.id
  JOIN persons p ON pc.person_id = p.id
  WHERE co.created_at >= NOW() - INTERVAL '${DAYS} days'
    AND co.state IN ('INITIATOR_JOINED', 'COMPLETED')
    AND p.type != 'TEST'

  UNION ALL

  SELECT 3, 'Real Exchange',
    COUNT(DISTINCT uc.person_id)
  FROM (
    SELECT DISTINCT co.id as onboarding_id, pc.person_id, c.id as conv_id
    FROM conversation_onboarding co
    JOIN conversation_participant_onboarding cpo
      ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
    JOIN person_contacts pc ON cpo.person_contact_id = pc.id
    JOIN persons p ON pc.person_id = p.id
    JOIN conversation_participant cp ON cp.person_id = pc.person_id
    JOIN conversation c ON c.id = cp.conversation_id AND c.type = 'ONE_ON_ONE'
    WHERE co.created_at >= NOW() - INTERVAL '${DAYS} days'
      AND co.state IN ('INITIATOR_JOINED', 'COMPLETED')
      AND p.type != 'TEST'
  ) uc
  JOIN message m ON m.conversation_id = uc.conv_id
  JOIN person_contacts mpc ON m.sender_person_contact_id = mpc.id AND mpc.person_id = uc.person_id
  WHERE m.provider_data->>'source' IS DISTINCT FROM 'onboarding_form'
    AND m.content NOT LIKE '%WREN-%'
    AND m.content NOT LIKE 'My birthday%'
    AND m.content NOT LIKE 'Our relationship%'
    AND m.content NOT LIKE 'We''re in a%'

  UNION ALL

  SELECT 4, 'Partner Joined',
    COUNT(DISTINCT co.id)
  FROM conversation_onboarding co
  JOIN conversation_participant_onboarding cpo
    ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
  JOIN person_contacts pc ON cpo.person_contact_id = pc.id
  JOIN persons p ON pc.person_id = p.id
  WHERE co.created_at >= NOW() - INTERVAL '${DAYS} days'
    AND co.state = 'COMPLETED'
    AND p.type != 'TEST'
)
SELECT
  funnel_step,
  users,
  ROUND(100.0 * users / FIRST_VALUE(users) OVER (ORDER BY step_num), 1) as pct_of_start,
  ROUND(100.0 * users / NULLIF(LAG(users) OVER (ORDER BY step_num), 0), 1) as conversion,
  ROUND(100.0 * (LAG(users) OVER (ORDER BY step_num) - users) /
        NULLIF(LAG(users) OVER (ORDER BY step_num), 0), 1) as drop_off
FROM funnel_data
ORDER BY step_num;
" >> "$OUTPUT_FILE" 2>&1

echo -e "${GREEN}✓ Step 1 complete${NC}"

echo -e "${YELLOW}Step 2: State Distribution${NC}"
echo "" >> "$OUTPUT_FILE"
echo "## Step 2: State Distribution" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

$CONNECT_SCRIPT "
SELECT
  state,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM conversation_onboarding
WHERE created_at >= NOW() - INTERVAL '${DAYS} days'
GROUP BY state
ORDER BY count DESC;
" >> "$OUTPUT_FILE" 2>&1

echo -e "${GREEN}✓ Step 2 complete${NC}"

echo -e "${YELLOW}Step 3: Segment by Relationship Type${NC}"
echo "" >> "$OUTPUT_FILE"
echo "## Step 3: Segment by Form Data" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### By Relationship Type" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

$CONNECT_SCRIPT "
SELECT
  co.form_data->>'relationship_type' as relationship_type,
  COUNT(*) as form_submissions,
  COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) as messaged_wren,
  COUNT(*) FILTER (WHERE co.state = 'COMPLETED') as completed,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) / NULLIF(COUNT(*), 0), 1) as msg_rate
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '${DAYS} days'
  AND co.form_data->>'name' IS NOT NULL
GROUP BY co.form_data->>'relationship_type'
ORDER BY form_submissions DESC;
" >> "$OUTPUT_FILE" 2>&1

echo "" >> "$OUTPUT_FILE"
echo "### By Platform (Provider)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

$CONNECT_SCRIPT "
SELECT
  co.form_data->>'provider' as platform,
  COUNT(*) as form_submissions,
  COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) as messaged_wren,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) / NULLIF(COUNT(*), 0), 1) as msg_rate
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '${DAYS} days'
  AND co.form_data->>'name' IS NOT NULL
GROUP BY co.form_data->>'provider'
ORDER BY form_submissions DESC;
" >> "$OUTPUT_FILE" 2>&1

echo -e "${GREEN}✓ Step 3 complete${NC}"

echo -e "${YELLOW}Step 4: User Details (INITIATOR_JOINED)${NC}"
echo "" >> "$OUTPUT_FILE"
echo "## Step 4: All Users Who Messaged Wren" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

$CONNECT_SCRIPT "
SELECT
  co.id as onboarding_id,
  co.form_data->>'name' as name,
  co.form_data->>'phone' as phone,
  co.form_data->>'relationship_type' as rel_type,
  co.form_data->>'provider' as platform,
  co.state,
  p.id as person_id,
  p.type as person_type,
  ROUND(EXTRACT(EPOCH FROM (NOW() - pc.created_at)) / 3600, 1) as hours_since_access_code,
  CASE
    WHEN co.form_data->>'phone' LIKE '+1%' THEN 'US/Canada'
    WHEN co.form_data->>'phone' LIKE '+27%' THEN 'South Africa'
    WHEN co.form_data->>'phone' LIKE '+44%' THEN 'UK'
    WHEN co.form_data->>'phone' LIKE '+353%' THEN 'Ireland'
    WHEN co.form_data->>'phone' LIKE '+61%' THEN 'Australia'
    WHEN co.form_data->>'phone' LIKE '+971%' THEN 'UAE'
    ELSE 'Other'
  END as country
FROM conversation_onboarding co
JOIN conversation_participant_onboarding cpo
  ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
JOIN person_contacts pc ON cpo.person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
WHERE co.created_at >= NOW() - INTERVAL '${DAYS} days'
  AND co.state IN ('INITIATOR_JOINED', 'COMPLETED')
  AND p.type != 'TEST'
ORDER BY co.created_at ASC;
" >> "$OUTPUT_FILE" 2>&1

echo -e "${GREEN}✓ Step 4 complete${NC}"

echo ""
echo -e "${GREEN}=== Analysis Complete ===${NC}"
echo -e "Output written to: ${YELLOW}${OUTPUT_FILE}${NC}"
echo ""
echo "To copy to docs folder:"
echo "  cp \"${OUTPUT_FILE}\" docs/onboarding_funnel_analysis_$(date +%Y-%m-%d).md"
