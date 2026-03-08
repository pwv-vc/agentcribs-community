#!/bin/bash
#
# Show affect distribution for a couple
# Lists all affects and their frequency for each partner
#
# Usage:
#   ./affect_distribution.sh <person_id> [days]
#
# Examples:
#   ./affect_distribution.sh 123        # Last 56 days (8 weeks, default)
#   ./affect_distribution.sh 123 28     # Last 28 days (4 weeks)
#   ./affect_distribution.sh 123 84     # Last 84 days (12 weeks)

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

echo "=== Affect Distribution ==="
echo "Person ID: $PERSON_ID"
echo "Time period: Last $DAYS days"
echo ""

"$CONNECT_SCRIPT" "
-- Affect distribution for both people in a partnership for the last $DAYS days
WITH couple AS (
  SELECT
    c.id AS conversation_id,
    MIN(cp.person_id) AS person1_id,
    MAX(CASE WHEN cp.person_id = (SELECT MIN(person_id) FROM conversation_participant WHERE conversation_id = c.id AND role = 'MEMBER')
      THEN p.name END) AS person1_name,
    MAX(cp.person_id) AS person2_id,
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
filtered_messages AS (
  SELECT
    m.id,
    pc.person_id
  FROM message m
  JOIN couple cp ON m.conversation_id = cp.conversation_id
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '$DAYS days'
    AND m.provider_timestamp < CURRENT_DATE
),
affect_counts AS (
  SELECT
    me.affect,
    COUNT(CASE WHEN fm.person_id = cp.person1_id THEN 1 END) AS person1_count,
    COUNT(CASE WHEN fm.person_id = cp.person2_id THEN 1 END) AS person2_count
  FROM filtered_messages fm
  JOIN message_enrichment me ON me.message_id = fm.id
  CROSS JOIN couple cp
  WHERE me.affect IS NOT NULL
    AND me.affect <> 'Neutral'
  GROUP BY me.affect
)
SELECT affect, person_1, person_2, partnership FROM (
  SELECT
    'name' AS affect,
    (SELECT person1_name FROM couple) AS person_1,
    (SELECT person2_name FROM couple) AS person_2,
    'Both' AS partnership,
    0 AS sort_order
  UNION ALL
  SELECT
    'Period: Last $DAYS days' AS affect,
    '' AS person_1,
    '' AS person_2,
    '' AS partnership,
    0 AS sort_order
  UNION ALL
  SELECT
    affect,
    person1_count::text AS person_1,
    person2_count::text AS person_2,
    (person1_count + person2_count)::text AS partnership,
    1 AS sort_order
  FROM affect_counts
) AS combined
ORDER BY
  sort_order,
  CASE
    WHEN affect IN ('name', 'Period: Last $DAYS days') THEN 0
    ELSE -1 * (CAST(partnership AS int))
  END;
"

echo ""
echo "=== Interpretation Guide ==="
echo ""
echo "Positive Affects (Good):"
echo "  - Partner-Affection, Partner-Validation, Humor, Partner-Interest, Partner-Enthusiasm"
echo ""
echo "Negative Affects (Warning Signs):"
echo "  - Partner-Complaint (mild negative)"
echo "  - Partner-Criticism, Partner-Contempt, Partner-Defensiveness, Stonewalling (Four Horsemen - serious)"
echo "  - Partner-Anger, Partner-Sadness, Partner-Disgust, Partner-Whining, etc."
echo ""
echo "What to Look For:"
echo "  ✅ High positive affects (Affection, Validation, Humor) = Healthy"
echo "  ⚠️  Any Four Horsemen present = Warning signs"
echo "  🚨 Contempt appearing = Strongest predictor of relationship failure"
echo ""
