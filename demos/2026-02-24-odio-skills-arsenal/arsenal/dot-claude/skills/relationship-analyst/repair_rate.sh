#!/bin/bash
#
# Calculate Repair Rate for a couple
#
# Usage:
#   ./repair_rate.sh <person_id> [days]
#
# Examples:
#   ./repair_rate.sh 123        # Last 56 days (8 weeks, default)
#   ./repair_rate.sh 123 28     # Last 28 days (4 weeks)
#   ./repair_rate.sh 123 84     # Last 84 days (12 weeks)

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <person_id> [days]"
  echo ""
  echo "Examples:"
  echo "  $0 123        # Last 56 days (8 weeks, default)"
  echo "  $0 123 28     # Last 28 days (4 weeks)"
  echo "  $0 123 84     # Last 84 days (12 weeks)"
  exit 1
fi

PERSON_ID="$1"
DAYS="${2:-56}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONNECT_SCRIPT="$SCRIPT_DIR/../sql-reader/connect.sh"

if [ ! -f "$CONNECT_SCRIPT" ]; then
    echo "Error: sql-reader connect.sh not found at $CONNECT_SCRIPT"
    exit 1
fi

echo "=== Repair Rate Analysis ==="
echo "Person ID: $PERSON_ID"
echo "Time period: Last $DAYS days"
echo ""

"$CONNECT_SCRIPT" "
-- Calculate repair rate for a couple over last $DAYS days
WITH couple_info AS (
  SELECT
    c.id AS conversation_id,
    MIN(cp.person_id) AS person1_id,
    MAX(cp.person_id) AS person2_id,
    MAX(CASE WHEN cp.person_id = (SELECT MIN(person_id) FROM conversation_participant WHERE conversation_id = c.id AND role = 'MEMBER')
      THEN p.name END) AS person1_name,
    MAX(CASE WHEN cp.person_id = (SELECT MAX(person_id) FROM conversation_participant WHERE conversation_id = c.id AND role = 'MEMBER')
      THEN p.name END) AS person2_name
  FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  JOIN persons p ON cp.person_id = p.id
  WHERE c.type = 'GROUP'
    AND cp.role = 'MEMBER'
    AND $PERSON_ID IN (
      SELECT person_id
      FROM conversation_participant
      WHERE conversation_id = c.id
    )
  GROUP BY c.id
  HAVING COUNT(DISTINCT cp.person_id) = 2
  LIMIT 1
),
-- Find all conflicts started by each person
conflicts AS (
  SELECT
    m.id as conflict_message_id,
    pc.person_id as conflict_starter_id,
    m.provider_timestamp as conflict_time,
    m.conversation_id
  FROM couple_info ci
  JOIN message m ON m.conversation_id = ci.conversation_id
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN message_enrichment me ON me.message_id = m.id
  WHERE me.conflict_state IN ('New Conflict', 'New conflict', 'Escalation')
    AND m.provider_timestamp >= CURRENT_DATE - INTERVAL '$DAYS days'
    AND m.provider_timestamp < CURRENT_DATE
),
-- Check next 5 responses from partner for escalation
conflict_responses AS (
  SELECT
    c.conflict_message_id,
    c.conflict_starter_id,
    c.conflict_time,
    ci.person1_id,
    ci.person2_id,
    -- Did partner respond?
    MAX(CASE WHEN m2.id IS NOT NULL AND pc2.person_id != c.conflict_starter_id THEN 1 ELSE 0 END) as has_response,
    -- Did partner escalate in next 5 messages?
    MAX(CASE
      WHEN pc2.person_id != c.conflict_starter_id
        AND me2.conflict_state IN ('Escalation', 'New Conflict', 'New conflict', 'De-escalation Failed')
      THEN 1
      ELSE 0
    END) as has_escalation
  FROM conflicts c
  JOIN couple_info ci ON ci.conversation_id = c.conversation_id
  LEFT JOIN LATERAL (
    SELECT m.id, m.sender_person_contact_id, m.provider_timestamp
    FROM message m
    WHERE m.conversation_id = c.conversation_id
      AND m.provider_timestamp > c.conflict_time
    ORDER BY m.provider_timestamp
    LIMIT 5
  ) m2 ON true
  LEFT JOIN person_contacts pc2 ON m2.sender_person_contact_id = pc2.id
  LEFT JOIN message_enrichment me2 ON me2.message_id = m2.id
  GROUP BY c.conflict_message_id, c.conflict_starter_id, c.conflict_time, ci.person1_id, ci.person2_id
)
SELECT
  ci.person1_name,
  ci.person2_name,

  -- Person 1 starts conflict, Person 2's repair rate
  COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id) as person1_conflicts_introduced,
  CASE
    WHEN COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id AND cr.has_response = 1) = 0 THEN NULL
    ELSE ROUND(
      100.0 * COUNT(*) FILTER (
        WHERE cr.conflict_starter_id = ci.person1_id
          AND cr.has_response = 1
          AND cr.has_escalation = 0
      )::numeric /
      NULLIF(COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id AND cr.has_response = 1), 0)::numeric,
      1
    )
  END AS person2_repair_rate,

  -- Person 2 starts conflict, Person 1's repair rate
  COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id) as person2_conflicts_introduced,
  CASE
    WHEN COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id AND cr.has_response = 1) = 0 THEN NULL
    ELSE ROUND(
      100.0 * COUNT(*) FILTER (
        WHERE cr.conflict_starter_id = ci.person2_id
          AND cr.has_response = 1
          AND cr.has_escalation = 0
      )::numeric /
      NULLIF(COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id AND cr.has_response = 1), 0)::numeric,
      1
    )
  END AS person1_repair_rate,

  75 AS healthy_repair_threshold

FROM couple_info ci
LEFT JOIN conflict_responses cr ON cr.person1_id = ci.person1_id AND cr.person2_id = ci.person2_id
GROUP BY ci.person1_name, ci.person2_name;
"

echo ""
echo "=== Interpretation Guide ==="
echo "Repair Rate = % of conflicts where partner responds WITHOUT escalating"
echo ""
echo "✅ Healthy (≥75%)      - Good emotional regulation, can handle conflict"
echo "🚨 Defensive (<75%)    - Tends to escalate conflicts, poor repair ability"
echo "⚠️  NULL               - No conflicts with responses in time window"
echo ""
echo "Key Metrics:"
echo "  - personX_conflicts_introduced: How many conflicts that person started"
echo "  - personY_repair_rate: When X starts conflict, % of time Y doesn't escalate"
echo ""
