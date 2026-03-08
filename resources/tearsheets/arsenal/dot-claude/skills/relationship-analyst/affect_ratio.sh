#!/bin/bash
#
# Calculate Affect Ratio for a specific person
#
# Usage:
#   ./affect_ratio.sh <person_id> [days]
#
# Examples:
#   ./affect_ratio.sh 123        # Last 56 days (8 weeks, default)
#   ./affect_ratio.sh 123 28     # Last 28 days (4 weeks)
#   ./affect_ratio.sh 123 84     # Last 84 days (12 weeks)

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

echo "=== Affect Ratio Analysis ==="
echo "Person ID: $PERSON_ID"
echo "Time period: Last $DAYS days"
echo ""

"$CONNECT_SCRIPT" "
-- Calculate affect ratio for a specific person over last $DAYS days
WITH target_person AS (
  SELECT
    p.id AS person_id,
    p.name AS person_name,
    cp.person_contact_id,
    cp.conversation_id
  FROM persons p
  JOIN conversation_participant cp ON cp.person_id = p.id
  WHERE p.id = $PERSON_ID
    AND cp.role = 'MEMBER'
  LIMIT 1
),
affect_counts AS (
  SELECT
    tp.person_id,
    tp.person_name,
    tp.conversation_id,
    -- Count positive affects
    COUNT(*) FILTER (
      WHERE me.affect IN (
        'Partner-Affection',
        'Partner-Validation',
        'Partner-Enthusiasm',
        'Humor',
        'Partner-Interest'
      )
    ) AS positive_count,
    -- Count negative affects
    COUNT(*) FILTER (
      WHERE me.affect IN (
        'Partner-Criticism',
        'Partner-Contempt',
        'Partner-Defensiveness',
        'Partner-Complaint',
        'Partner-Sadness',
        'Partner-Anger',
        'Partner-Belligerence',
        'Partner-Domineering',
        'Partner-Fear / Tension',
        'Partner-Threats',
        'Partner-Disgust',
        'Partner-Whining',
        'Stonewalling'
      )
    ) AS negative_count,
    -- Total messages with affect classification
    COUNT(*) AS total_classified,
    -- Date range
    MIN(m.provider_timestamp)::date AS first_message_date,
    MAX(m.provider_timestamp)::date AS last_message_date
  FROM target_person tp
  JOIN message m ON m.conversation_id = tp.conversation_id
    AND m.sender_person_contact_id = tp.person_contact_id
  JOIN message_enrichment me ON me.message_id = m.id
  WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '$DAYS days'
    AND m.provider_timestamp < CURRENT_DATE
  GROUP BY tp.person_id, tp.person_name, tp.conversation_id
)
SELECT
  person_id,
  person_name,
  conversation_id,
  positive_count,
  negative_count,
  total_classified,
  first_message_date,
  last_message_date,
  -- Calculate affect ratio
  CASE
    WHEN negative_count = 0 AND positive_count > 0 THEN 100.0
    WHEN negative_count = 0 THEN 0.0
    ELSE ROUND(positive_count::numeric / negative_count::numeric, 2)
  END AS affect_ratio,
  -- Health assessment
  CASE
    WHEN negative_count = 0 AND positive_count > 0 THEN '🌟 Exceptional (no negatives)'
    WHEN negative_count = 0 THEN '⚠️ No data'
    WHEN positive_count::numeric / negative_count::numeric >= 20.0 THEN '🌟 Exceptional (≥20:1)'
    WHEN positive_count::numeric / negative_count::numeric >= 5.0 THEN '✅ Healthy (≥5:1)'
    WHEN positive_count::numeric / negative_count::numeric >= 1.0 THEN '⚠️ At-Risk (1:1-5:1)'
    ELSE '🚨 Distress (<1:1)'
  END AS relationship_health,
  -- Targets
  5 AS lower_target,
  20 AS upper_target
FROM affect_counts;
"

echo ""
echo "=== Interpretation Guide ==="
echo "🌟 Exceptional (≥20:1)  - Upper target, exceptional relationship health"
echo "✅ Healthy (≥5:1)       - Lower target, research 'magic ratio'"
echo "⚠️ At-Risk (1:1-5:1)    - Below target, encourage more positive interactions"
echo "🚨 Distress (<1:1)      - Critical, high-priority intervention needed"
echo ""
