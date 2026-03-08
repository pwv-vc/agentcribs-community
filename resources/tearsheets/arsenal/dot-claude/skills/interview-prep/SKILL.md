---
name: interview-prep
description: Investigate a user's onboarding and engagement history, then generate a tailored 10-question interview script as a markdown document.
---

# interview-prep Skill

## Purpose

Prepares a comprehensive interview brief and tailored question script for user research interviews. Given a user's name and phone number, this skill investigates their full journey — onboarding status, conversation history, engagement patterns, and product experience — then produces a markdown document with 10 interview questions grounded in actual user data.

**Use this skill when:**
- User says "prep for an interview" or "interview questions"
- User wants to understand a specific person's experience before talking to them
- User provides a name + phone number and asks for an investigation
- Preparing for user research, NUX analysis, or onboarding assessment calls

---

## Required Inputs

You need **both** of these from the user before starting:

| Input | Example | Notes |
|-------|---------|-------|
| **First name** | Chad | Used to search `persons` table |
| **Phone number** | 587 ***5924 | Partial is fine — search with `LIKE '%5924%'` on `person_contacts.handle` |

If the user doesn't provide both, ask before proceeding.

---

## Step 1: Find the User

Use the **sql-reader skill** to locate the person.

```sql
SELECT p.id, pc.provider, pc.created_at
FROM persons p
JOIN person_contacts pc ON pc.person_id = p.id
WHERE LOWER(p.name) LIKE '%{name}%'
  AND pc.handle LIKE '%{last_digits}%';
```

**Capture:** `person_id`, `p.id`, `provider` (linq/evolution), `created_at` (signup date).

If no results, try broader searches (name only, phone only). If multiple matches, present options to the user.

---

## Step 2: Map Their Conversations

```sql
SELECT cp.conversation_id, cp.role, c.type, c.state, c.created_at as conv_created
FROM conversation_participant cp
JOIN conversation c ON c.id = cp.conversation_id
WHERE cp.person_id = {person_id}
ORDER BY c.created_at;
```

**Key things to note:**
- `c.state` — Is it `ONBOARDING` or `ACTIVE`? This is the most important onboarding signal.
- `c.type` — `ONE_ON_ONE` (just user + Codel) vs `GROUP` (couple conversation)
- How many conversations exist? A single ONE_ON_ONE with state=ONBOARDING means the partner never joined.

---

## Step 3: Get Onboarding Status

```sql
-- Conversation-level onboarding
SELECT co.state, co.form_data, co.access_code, co.group_invite_data,
       co.reminder_count, co.last_reminder_sent_at, co.created_at, co.updated_at
FROM conversation_onboarding co
WHERE co.conversation_id = {conversation_id};

-- Participant-level onboarding
SELECT cpo.is_initiator, cpo.state, cpo.form_data,
       cpo.person_contact_id, cpo.created_at, cpo.updated_at
FROM conversation_participant_onboarding cpo
WHERE cpo.conversation_id = {conversation_id};
```

**What to extract from `form_data`:**
- Name, phone, birthday, timezone
- Consent timestamp
- User agent (tells you device + how they found Wren, e.g. Reddit app browser)
- IP address (can indicate geography)

**Onboarding states to look for:**
- `FORM_SUBMITTED` — Completed webapp form but not fully active
- Check if partner has a participant_onboarding row (if not, partner never started)

---

## Step 4: Get All Participants

```sql
SELECT cp.person_id, cp.role, p.id
FROM conversation_participant cp
JOIN persons p ON cp.person_id = p.id
WHERE cp.conversation_id = {conversation_id};
```

**Check:** Is it just the user + Codel (THERAPIST role)? Or did a partner join? This determines whether the core product was ever activated.

---

## Step 5: Pull Full Message History

```sql
SELECT m.id, m.content, m.provider_timestamp, m.created_at,
       p.id as sender_person_id
FROM message m
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
WHERE m.conversation_id = {conversation_id}
ORDER BY m.provider_timestamp ASC;
```

**Read the entire conversation.** Look for:

- **Onboarding form answers** — Often appear as early messages (relationship type, goals, situation descriptors)
- **First substantive exchange** — How did the user describe their situation?
- **Emotional tone** — Are they open, guarded, frustrated, hopeful?
- **Key turning points** — Where did engagement peak or drop off?
- **Friction moments** — Repeated questions, confusion, failed image uploads, product misunderstandings
- **Stated needs** — What does the user say they want help with?
- **Product feedback** — Any explicit comments about Wren, comparisons to other tools
- **Interview willingness** — Did they agree to a research call? Any conditions?

---

## Step 6: Check for Image Attachments

```sql
SELECT m.id, m.provider_timestamp,
       m.provider_data->'attachments' as attachments
FROM message m
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
WHERE pc.person_id = {person_id}
  AND m.conversation_id = {conversation_id}
  AND (m.content IS NULL OR m.content = '')
  AND m.provider_data->'attachments' IS NOT NULL
ORDER BY m.provider_timestamp;
```

Image uploads show up as blank-content messages with attachment metadata. Note:
- How many images were sent
- Whether the same images were sent multiple times (check filenames)
- How Wren responded (it can't process images — did it handle this gracefully?)

---

## Step 7: Get Engagement Metrics

```sql
-- Message counts by sender and day
SELECT
  DATE(m.provider_timestamp) as day,
  p.id as sender_id,
  COUNT(*) FILTER (WHERE m.content IS NOT NULL AND m.content != '') as text_msgs,
  COUNT(*) FILTER (WHERE m.content IS NULL OR m.content = '') as media_msgs
FROM message m
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
WHERE m.conversation_id = {conversation_id}
GROUP BY DATE(m.provider_timestamp), p.id
ORDER BY day, sender_id;
```

Also check:
```sql
-- Last activity
SELECT
  MAX(m.provider_timestamp) FILTER (WHERE pc.person_id = {person_id}) as last_user_msg,
  MAX(m.provider_timestamp) as last_any_msg
FROM message m
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
WHERE m.conversation_id = {conversation_id};

-- Reactions
SELECT m.id, m.content, m.provider_timestamp
FROM message m
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
WHERE pc.person_id = {person_id}
  AND m.conversation_id = {conversation_id}
  AND m.provider_data->>'reaction_id' IS NOT NULL;

-- Person facts
SELECT fact, type, confidence, created_at
FROM person_fact
WHERE person_id = {person_id}
ORDER BY created_at;
```

---

## Step 8: Check Conversation Data

```sql
SELECT c.data, c.state, c.provider_data
FROM conversation c
WHERE c.id = {conversation_id};
```

The `data` field may contain `latest_timezone` and other metadata. The `provider_data` field has chat handles and provider-specific info.

---

## Step 9: Synthesize Findings

Before writing questions, prepare a structured brief. Present this to the user first:

### User Profile Brief Template

```markdown
## {Name} — User Profile & Onboarding Assessment

**Person:** {Name} ([view](https://admin.prod.cncorp.io/persons/{id})) | Phone: {masked} | Provider: {provider}
**Conversation:** {conv_id} ([view](https://admin.prod.cncorp.io/conversations/{conv_id})) | Created: {date}
**Timezone:** {tz} | **DOB:** {dob}

### Onboarding Status: {STATUS SUMMARY}
- Conversation state: {ONBOARDING/ACTIVE}
- Participant onboarding state: {state}
- Partner: {Joined / Never joined / details}

### Timeline & Engagement
{Day-by-day breakdown with timestamps and key moments}

### Engagement Summary
| Metric | Value |
|---|---|
| Total text messages from user | X |
| Total media messages | X |
| Total messages from Wren | X |
| Days active | X |
| Last message | {date} |
| Days since last activity | X |

### Key Themes
{What matters to this user, what they're dealing with, what they want}

### Product Friction Points
{Where things didn't work, confusion, unmet expectations}
```

**Present this brief to the user and confirm before generating questions.**

---

## Step 10: Generate 10 Interview Questions

Write a markdown document with 10 questions. Follow these principles:

### Data Protection in Questions

**The interview document may be shared with team members, stakeholders, or stored in shared drives. Protect user privacy:**

**ALLOWED in questions and interviewer notes:**
- User's first name and partner's first name (we are interviewing them)
- Relationship type and general dynamics (e.g., "co-parenting situation," "conflict around trust and communication")
- Product interaction patterns (e.g., "sent images that Wren couldn't process," "asked about how the shared space works")
- General emotional themes (e.g., "expressed feeling unheard," "described a pattern of conflict escalation")
- Onboarding status and engagement metrics

**BANNED from questions and interviewer notes:**
- Direct quotes from the user's private conversations with Wren
- Specific medical or mental health diagnoses the user disclosed
- Details about addiction, abuse, or criminal/legal matters
- Specific details about homelessness, financial distress, or other vulnerabilities
- Content from images or screenshots the user shared
- Any detail that would be embarrassing or harmful if the document were shared beyond the interview team

**The principle:** Abstract one level up from the raw messages. You read the full conversation to *understand* the user, but the interview doc should reference **product interactions and relationship dynamics**, not the private emotional content itself. Let the user choose what to share in the interview — don't front-load their disclosures into the question script.

**Example — BAD (leaks private content):**
> *She disclosed BPD, ADHD, depression, and anxiety. She said Lewis calls her "lazy" and "worthless." She's been in survival mode since age 9.*

**Example — GOOD (abstracted to dynamics):**
> *She described significant personal challenges beyond the relationship and a pattern where expressing her feelings is met with dismissiveness. Probe gently for what kind of support would feel most useful.*

### Question Design Principles

1. **Ground every question in product interactions, not private disclosures.** Each question should reference something observable about how the user engaged with Wren — a behavior, a product moment, a pattern of usage. Not what they confided.

2. **Include interviewer notes.** Below each question, add italicized context about the *product interaction pattern* you observed and what to listen for. Do not include direct quotes or sensitive personal details.

3. **Flow from concrete to abstract.** Start with their entry point and first impressions, move through specific product friction moments, end with product vision and future needs.

4. **Reference their experience, not their words.** Instead of quoting what they said, describe what they were trying to do. "You tried to share some context with Wren by sending images" rather than quoting the messages themselves.

5. **Don't lead.** Frame questions to elicit honest feedback, not to confirm assumptions. "What surprised you?" is better than "Were you surprised that X didn't work?"

6. **Cover these areas** (adjust based on what's relevant to this user):

| Area | Questions | Focus |
|------|-----------|-------|
| Discovery & signup | 1-2 | How they found Wren, what they expected |
| Onboarding experience | 2-3 | Form, first messages, initial impressions |
| Engagement & value | 2-3 | What felt helpful, what felt off, specific moments |
| Friction & gaps | 1-2 | Where things broke down, unmet needs |
| Product fit & future | 1-2 | What would make them stay, what they'd change |

7. **Include logistics note** at the bottom with any scheduling context from the conversation (timezone, preferences about video/timing, etc).

### Output Format

Save the document to `docs/{name_lowercase}_interview_questions.md`:

```markdown
# Interview Questions — {Name} (Person {id})

**Context:** {2-3 sentence summary of who they are and their situation}

---

## {Section Name}

**1. {Question text}**
*{Interviewer notes: what you know from data, what to probe for}*

**2. {Question text}**
*{Interviewer notes}*

...

---

**Interview logistics:** {timezone, scheduling preferences, any conditions they mentioned}
```

---

## Citations

**All entity IDs must include clickable admin links:**

- Person: `[view](https://admin.prod.cncorp.io/persons/{id})`
- Conversation: `[view](https://admin.prod.cncorp.io/conversations/{id})`
- Messages: `[view](https://admin.prod.cncorp.io/conversations/{id}/messages)`

---

## Common Violations

- **BANNED:** Writing generic interview questions not grounded in user data
- **BANNED:** Skipping the user brief — always present findings before generating questions
- **BANNED:** Using "approximately" or guessing at data — all claims must come from actual query results
- **BANNED:** Omitting citations for person/conversation IDs
- **BANNED:** Not reading the full message history — you must understand the entire conversation before writing questions
- **BANNED:** Including direct quotes from the user's private conversations in the interview document
- **BANNED:** Including specific medical/mental health diagnoses, addiction details, or other sensitive disclosures in the interview document
- **BANNED:** Including details about homelessness, financial distress, abuse, or legal matters in the interview document
- **BANNED:** Writing interviewer notes that front-load the user's private disclosures — let the user decide what to share in the interview

---

## Success Criteria

You've completed this skill when:
- [ ] User found via sql-reader with actual query results
- [ ] All conversations and onboarding records retrieved
- [ ] Full message history read and analyzed
- [ ] User profile brief presented with citations
- [ ] 10 interview questions written, each grounded in observed product interaction data
- [ ] Questions reference product interactions and relationship dynamics, NOT private disclosures
- [ ] No direct quotes from private conversations appear in the interview document
- [ ] No sensitive personal details (diagnoses, addiction, legal, financial) appear in the interview document
- [ ] Questions saved as markdown doc in `docs/`
- [ ] Admin link provided to the user
