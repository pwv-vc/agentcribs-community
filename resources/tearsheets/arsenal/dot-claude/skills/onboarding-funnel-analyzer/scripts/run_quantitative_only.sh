#!/bin/bash
# Quick Quantitative Funnel - Just the numbers
# Usage: ./run_quantitative_only.sh [DAYS]
# Default: 7 days

set -e

DAYS=${1:-7}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Find the project root (where arsenal/ lives) - 4 levels up from scripts/
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
CONNECT_SCRIPT="${PROJECT_ROOT}/arsenal/dot-claude/skills/sql-reader/connect.sh"

# Verify connect script exists
if [ ! -f "$CONNECT_SCRIPT" ]; then
  echo "Error: Cannot find sql-reader connect.sh at: $CONNECT_SCRIPT"
  echo "SCRIPT_DIR: $SCRIPT_DIR"
  echo "PROJECT_ROOT: $PROJECT_ROOT"
  echo "Make sure you're running from the project root."
  exit 1
fi

echo "=== Onboarding Funnel (Last ${DAYS} days) ==="
echo ""

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
  funnel_step as \"Step\",
  users as \"Users\",
  ROUND(100.0 * users / FIRST_VALUE(users) OVER (ORDER BY step_num), 1) || '%' as \"% of Start\",
  COALESCE(ROUND(100.0 * users / NULLIF(LAG(users) OVER (ORDER BY step_num), 0), 1) || '%', '-') as \"Conversion\",
  COALESCE(ROUND(100.0 * (LAG(users) OVER (ORDER BY step_num) - users) /
        NULLIF(LAG(users) OVER (ORDER BY step_num), 0), 1) || '%', '-') as \"Drop-off\"
FROM funnel_data
ORDER BY step_num;
"

echo ""
echo "State distribution:"
$CONNECT_SCRIPT "
SELECT state, COUNT(*) as count
FROM conversation_onboarding
WHERE created_at >= NOW() - INTERVAL '${DAYS} days'
GROUP BY state ORDER BY count DESC;
"
