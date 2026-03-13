#!/usr/bin/env python3
"""
Incomplete Onboarding Assessor

Queries the database for incomplete onboardings and applies temperature-based
engagement assessment with time decay.

Usage:
    python assess_onboardings.py [--days N] [--output FILE]

Options:
    --days N      Time window in days (default: 30)
    --output FILE Output file path (default: stdout)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Optional


# Configurable decay thresholds
DECAY_THRESHOLD_1 = 3   # No decay within this many days
DECAY_THRESHOLD_2 = 7   # Drop 1 level by this many days
DECAY_THRESHOLD_3 = 14  # Drop 2 levels by this many days
DECAY_ALL_COLD = 15     # All become COLD after this many days

# Temperature order (for decay calculations)
TEMP_ORDER = ['COLD', 'WARM', 'HOT']

# PersonType filters
INCLUDE_PERSON_TYPES = ['user', 'user_research']


def apply_time_decay(original_temp: str, days_silent: int) -> str:
    """Apply time decay to get current temperature."""
    if original_temp not in TEMP_ORDER:
        return 'COLD'

    if days_silent is None or days_silent <= DECAY_THRESHOLD_1:
        decay_levels = 0
    elif days_silent <= DECAY_THRESHOLD_2:
        decay_levels = 1
    elif days_silent <= DECAY_THRESHOLD_3:
        decay_levels = 2
    else:  # 15+ days
        return 'COLD'  # All become COLD

    current_index = TEMP_ORDER.index(original_temp)
    new_index = max(0, current_index - decay_levels)
    return TEMP_ORDER[new_index]


def run_sql_query(query: str) -> list[dict]:
    """Run a SQL query using psql and return results as list of dicts."""
    # Find arsenal .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_paths = [
        os.path.join(script_dir, '..', '..', '..', '.env'),  # arsenal/.env
        os.path.join(script_dir, '..', '..', '..', '..', 'arsenal', '.env'),
    ]

    env_file = None
    for path in env_paths:
        if os.path.exists(path):
            env_file = os.path.abspath(path)
            break

    if not env_file:
        print("Error: Could not find arsenal/.env", file=sys.stderr)
        sys.exit(1)

    # Load environment variables
    env = os.environ.copy()
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env[key] = value

    # Run psql with JSON output
    cmd = [
        'psql',
        '-t',  # Tuples only (no headers)
        '-A',  # Unaligned output
        '-F', '\t',  # Tab separator
        '-c', query
    ]

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"SQL Error: {e.stderr}", file=sys.stderr)
        return ""


def get_incomplete_onboardings(days: int) -> str:
    """Get incomplete onboardings from the database."""
    query = f"""
    WITH incomplete_onboardings AS (
      SELECT
        co.id as onboarding_id,
        co.form_data->>'name' as initiator_name,
        co.form_data->>'invitee_name' as partner_name,
        co.form_data->>'relationship_goal' as relationship_goal,
        co.form_data->>'relationship_dynamic' as relationship_dynamic,
        co.created_at as onboarding_date,
        co.state as onboarding_state,
        EXTRACT(DAY FROM NOW() - co.created_at)::int as days_since_onboarding
      FROM conversation_onboarding co
      WHERE co.state IN ('INITIATOR_JOINED', 'PENDING')
        AND co.created_at >= NOW() - INTERVAL '{days} days'
        AND co.form_data->>'name' IS NOT NULL
        AND co.form_data->>'name' != ''
        AND co.form_data->>'name' != co.form_data->>'invitee_name'
    )
    SELECT
      io.onboarding_id,
      io.initiator_name,
      io.partner_name,
      io.relationship_goal,
      io.relationship_dynamic,
      io.onboarding_date::date,
      io.onboarding_state,
      io.days_since_onboarding,
      p.id as person_id,
      p.person_type,
      MAX(m.provider_timestamp)::date as last_user_message,
      EXTRACT(DAY FROM NOW() - MAX(m.provider_timestamp))::int as days_since_last_msg,
      COUNT(DISTINCT m.id) as message_count
    FROM incomplete_onboardings io
    LEFT JOIN persons p ON LOWER(p.name) = LOWER(io.initiator_name)
    LEFT JOIN person_contacts pc ON pc.person_id = p.id
    LEFT JOIN message m ON m.sender_person_contact_id = pc.id
      AND m.provider_timestamp >= io.onboarding_date
    WHERE p.person_type IN ('user', 'user_research')
    GROUP BY
      io.onboarding_id, io.initiator_name, io.partner_name,
      io.relationship_goal, io.relationship_dynamic, io.onboarding_date,
      io.onboarding_state, io.days_since_onboarding, p.id, p.person_type
    ORDER BY io.onboarding_date DESC;
    """
    return run_sql_query(query)


def parse_onboarding_results(raw_output: str) -> list[dict]:
    """Parse psql output into list of dicts."""
    results = []
    if not raw_output.strip():
        return results

    columns = [
        'onboarding_id', 'initiator_name', 'partner_name', 'relationship_goal',
        'relationship_dynamic', 'onboarding_date', 'onboarding_state',
        'days_since_onboarding', 'person_id', 'person_type',
        'last_user_message', 'days_since_last_msg', 'message_count'
    ]

    for line in raw_output.strip().split('\n'):
        if not line.strip():
            continue
        values = line.split('\t')
        if len(values) >= len(columns):
            row = {}
            for i, col in enumerate(columns):
                val = values[i] if i < len(values) else ''
                # Convert numeric fields
                if col in ['days_since_onboarding', 'days_since_last_msg', 'message_count']:
                    row[col] = int(val) if val and val != '' else None
                else:
                    row[col] = val if val and val != '' else None
            results.append(row)

    return results


def assess_original_temperature(row: dict) -> str:
    """
    Assess original temperature based on available data.

    Note: This is a simplified assessment. Full assessment requires
    reading chat history which should be done manually for accuracy.

    Default is WARM (sent access code = showed intent).
    """
    message_count = row.get('message_count') or 0
    relationship_dynamic = row.get('relationship_dynamic') or ''

    # Multiple goals selected often indicates high intent
    goals_count = len(relationship_dynamic.split(',')) if relationship_dynamic else 0

    # Default to WARM (they sent an access code)
    if message_count == 0:
        return 'WARM'  # Access code only, but still showed intent

    # If they sent multiple messages, likely HOT
    if message_count >= 3:
        return 'HOT'

    # Multiple goals = high intent
    if goals_count >= 3:
        return 'HOT'

    return 'WARM'


def generate_report(onboardings: list[dict], days: int) -> str:
    """Generate markdown assessment report."""
    today = datetime.now().strftime('%B %d, %Y')

    # Calculate temperatures
    for row in onboardings:
        row['original_temp'] = assess_original_temperature(row)
        days_silent = row.get('days_since_last_msg')
        if days_silent is None:
            days_silent = row.get('days_since_onboarding') or 0
        row['current_temp'] = apply_time_decay(row['original_temp'], days_silent)

    # Count by temperature
    hot_count = sum(1 for r in onboardings if r['current_temp'] == 'HOT')
    warm_count = sum(1 for r in onboardings if r['current_temp'] == 'WARM')
    cold_count = sum(1 for r in onboardings if r['current_temp'] == 'COLD')

    # Build report
    report = f"""# Incomplete Onboarding Assessment
**Date:** {today}
**Time Window:** Last {days} days

## Framework

Using temperature-based engagement model with time decay:

### Temperature Levels
- **WARM**: Showed intent (sent access code, basic engagement)
- **HOT**: High engagement (asked questions, shared personal info, did demo)
- **COLD**: After time decay or explicit decline

### Time Decay Rules
- 0-{DECAY_THRESHOLD_1} days: No decay
- {DECAY_THRESHOLD_1+1}-{DECAY_THRESHOLD_2} days: Drop one level
- {DECAY_THRESHOLD_2+1}-{DECAY_THRESHOLD_3} days: Drop two levels
- {DECAY_ALL_COLD}+ days: All become COLD

---

## Summary

| Metric | Count |
|--------|-------|
| Total incomplete | {len(onboardings)} |
| Currently HOT | {hot_count} |
| Currently WARM | {warm_count} |
| Currently COLD | {cold_count} |

---

## Assessment Table

| User | Partner | Onboarding | Days Since | Last Msg | Days Silent | Original | Current |
|------|---------|------------|------------|----------|-------------|----------|---------|
"""

    for row in onboardings:
        user = row['initiator_name'] or 'Unknown'
        partner = row['partner_name'] or 'Unknown'
        onboard_date = row['onboarding_date'] or 'Unknown'
        days_since = row['days_since_onboarding'] or '?'
        last_msg = row['last_user_message'] or 'Never'
        days_silent = row['days_since_last_msg'] or row['days_since_onboarding'] or '?'
        orig = row['original_temp']
        curr = row['current_temp']

        report += f"| {user} | {partner} | {onboard_date} | {days_since} | {last_msg} | {days_silent} | {orig} | **{curr}** |\n"

    # Priority sections
    report += "\n---\n\n## Priority List\n\n"

    # HOT (Immediate)
    hot_users = [r for r in onboardings if r['current_temp'] == 'HOT']
    report += "### Immediate Action (HOT)\n\n"
    if hot_users:
        for row in hot_users:
            report += f"- **{row['initiator_name']}** with {row['partner_name']} — {row['days_since_last_msg'] or 0} days silent\n"
    else:
        report += "No currently HOT leads.\n"

    # WARM (High Priority)
    warm_users = [r for r in onboardings if r['current_temp'] == 'WARM']
    report += "\n### High Priority (WARM)\n\n"
    if warm_users:
        for row in warm_users:
            report += f"- **{row['initiator_name']}** with {row['partner_name']} — {row['days_since_last_msg'] or row['days_since_onboarding'] or 0} days silent (originally {row['original_temp']})\n"
    else:
        report += "No currently WARM leads.\n"

    # COLD (Low Priority)
    cold_users = [r for r in onboardings if r['current_temp'] == 'COLD']
    report += "\n### Low Priority (COLD)\n\n"
    if cold_users:
        for row in cold_users:
            report += f"- **{row['initiator_name']}** with {row['partner_name']} — {row['days_since_last_msg'] or row['days_since_onboarding'] or 0} days silent (originally {row['original_temp']})\n"
    else:
        report += "No COLD leads.\n"

    report += """
---

## Recommended Actions

| Current Temp | Action | Approach |
|--------------|--------|----------|
| **HOT** | Convert | Help craft partner invite, emphasize value |
| **WARM** | Stoke the flame | Build on what they shared, deepen conversation |
| **COLD** | Light the spark | Low-barrier CTA, ask what's holding them back |

---

## Notes

- Original temperature is estimated from message counts. For accurate assessment, review actual chat history.
- Users with 0 messages after access code are still WARM (showed intent by joining).
- Time decay reflects that engagement "cools" without interaction.
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Assess incomplete onboardings with temperature model'
    )
    parser.add_argument(
        '--days', type=int, default=30,
        help='Time window in days (default: 30)'
    )
    parser.add_argument(
        '--output', type=str,
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    # Get data
    print(f"Querying incomplete onboardings from last {args.days} days...", file=sys.stderr)
    raw_output = get_incomplete_onboardings(args.days)

    # Parse results
    onboardings = parse_onboarding_results(raw_output)
    print(f"Found {len(onboardings)} incomplete onboardings", file=sys.stderr)

    if not onboardings:
        print("No incomplete onboardings found in the specified time window.")
        return

    # Generate report
    report = generate_report(onboardings, args.days)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == '__main__':
    main()
