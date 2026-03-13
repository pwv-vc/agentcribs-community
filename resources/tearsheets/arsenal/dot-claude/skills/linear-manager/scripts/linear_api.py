#!/usr/bin/env python3
"""
Linear API wrapper for Claude Code skill

Provides direct GraphQL API access to Linear for issue management.
"""

import os
import sys
import json
import argparse
from typing import Optional

try:
    import requests
except ImportError:
    print("❌ Error: requests library not installed")
    print("Run: pip install requests")
    sys.exit(1)

LINEAR_API_URL = "https://api.linear.app/graphql"


def get_api_key() -> str:
    """Get Linear API key from environment"""
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("❌ Error: LINEAR_API_KEY not set")
        print("\nTo fix:")
        print("1. Get API key from https://linear.app/settings/api")
        print("2. Add to arsenal/.env:")
        print('   echo "LINEAR_API_KEY=lin_api_your_key_here" >> arsenal/.env')
        sys.exit(1)
    return api_key


def graphql_request(query: str, variables: dict) -> dict:
    """Make GraphQL request to Linear API"""
    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            LINEAR_API_URL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        # Check for GraphQL errors
        if "errors" in data:
            errors = data["errors"]
            print(f"❌ GraphQL Error: {errors[0]['message']}")
            if len(errors) > 1:
                print(f"   (+ {len(errors) - 1} more errors)")
            sys.exit(1)

        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request failed: {e}")
        sys.exit(1)


def get_issue(identifier: str) -> dict:
    """Get issue details by identifier (e.g., 'ENG-123')"""
    query = """
    query Issue($id: String!) {
      issue(id: $id) {
        id
        identifier
        title
        description
        priority
        priorityLabel
        state {
          name
          type
        }
        assignee {
          id
          name
          email
        }
        team {
          id
          name
          key
        }
        labels {
          nodes {
            name
          }
        }
        comments {
          nodes {
            body
            user {
              name
            }
            createdAt
          }
        }
        url
        createdAt
        updatedAt
      }
    }
    """

    result = graphql_request(query, {"id": identifier})

    if not result.get("data", {}).get("issue"):
        print(f"❌ Issue not found: {identifier}")
        print("\nTroubleshooting:")
        print("- Check the issue ID format (e.g., 'ENG-123')")
        print("- Verify you have access to this team")
        print("- Ensure the issue hasn't been deleted")
        sys.exit(1)

    issue = result["data"]["issue"]

    # Print formatted output
    print(f"📋 {issue['identifier']}: {issue['title']}")
    print(f"🔗 {issue['url']}\n")
    print(f"Status: {issue['state']['name']}")
    print(f"Priority: {issue['priorityLabel']}")

    if issue.get('assignee'):
        print(f"Assignee: {issue['assignee']['name']}")

    if issue.get('labels', {}).get('nodes'):
        labels = [label['name'] for label in issue['labels']['nodes']]
        print(f"Labels: {', '.join(labels)}")

    if issue.get('description'):
        print(f"\nDescription:\n{issue['description']}")

    if issue.get('comments', {}).get('nodes'):
        print(f"\n💬 Comments ({len(issue['comments']['nodes'])}):")
        for comment in issue['comments']['nodes']:
            print(f"\n  {comment['user']['name']}:")
            print(f"  {comment['body'][:100]}...")

    return issue


def create_issue(
    title: str,
    team_id: str,
    description: str = "",
    priority: str = "",
    status: str = "",
    assignee_id: str = "",
) -> dict:
    """Create a new Linear issue"""
    query = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
    """

    # Map priority string to int (0=none, 1=urgent, 2=high, 3=medium, 4=low)
    priority_map = {"urgent": 1, "high": 2, "medium": 3, "low": 4, "none": 0}
    priority_int = priority_map.get(priority.lower(), 0) if priority else 0

    # Build input object
    input_data = {
        "title": title,
        "teamId": team_id,
    }

    if description:
        input_data["description"] = description
    if priority_int > 0:
        input_data["priority"] = priority_int
    if assignee_id:
        input_data["assigneeId"] = assignee_id
    # Note: status requires state ID, not name - would need to fetch states first
    # Skipping status for now to keep it simple

    result = graphql_request(query, {"input": input_data})

    if result["data"]["issueCreate"]["success"]:
        issue = result["data"]["issueCreate"]["issue"]
        print(f"✅ Created issue {issue['identifier']}: {issue['title']}")
        print(f"🔗 {issue['url']}")
        return issue
    else:
        print("❌ Failed to create issue")
        sys.exit(1)


def update_issue(
    issue_id: str,
    title: str = "",
    description: str = "",
    priority: str = "",
    status: str = "",
) -> dict:
    """Update an existing Linear issue"""
    query = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
    """

    # Build input object
    input_data = {}

    if title:
        input_data["title"] = title
    if description:
        input_data["description"] = description
    if priority:
        priority_map = {"urgent": 1, "high": 2, "medium": 3, "low": 4, "none": 0}
        input_data["priority"] = priority_map.get(priority.lower(), 0)

    # Note: status would need state ID mapping - leaving for future enhancement

    if not input_data:
        print("⚠️  No fields to update")
        return {}

    result = graphql_request(query, {"id": issue_id, "input": input_data})

    if result["data"]["issueUpdate"]["success"]:
        issue = result["data"]["issueUpdate"]["issue"]
        print(f"✅ Updated issue {issue['identifier']}")
        print(f"🔗 {issue['url']}")
        return issue
    else:
        print("❌ Failed to update issue")
        sys.exit(1)


def search_issues(
    query_text: str = "",
    team_id: str = "",
    assignee_id: str = "",
    limit: int = 10,
) -> list:
    """Search for Linear issues"""
    query = """
    query Issues($filter: IssueFilter, $first: Int) {
      issues(filter: $filter, first: $first) {
        nodes {
          id
          identifier
          title
          priority
          priorityLabel
          state {
            name
          }
          assignee {
            name
          }
          url
        }
      }
    }
    """

    # Build filter
    filter_obj = {}
    if team_id:
        filter_obj["team"] = {"id": {"eq": team_id}}
    if assignee_id:
        filter_obj["assignee"] = {"id": {"eq": assignee_id}}

    result = graphql_request(query, {"filter": filter_obj, "first": limit})

    issues = result["data"]["issues"]["nodes"]

    # Filter by text locally (Linear's text search is more complex)
    if query_text:
        query_lower = query_text.lower()
        issues = [
            issue for issue in issues
            if query_lower in issue['title'].lower()
        ]

    print(f"📋 Found {len(issues)} issue(s)\n")

    for issue in issues:
        assignee = issue['assignee']['name'] if issue.get('assignee') else "Unassigned"
        print(f"{issue['identifier']}: {issue['title']}")
        print(f"  Status: {issue['state']['name']} | Priority: {issue['priorityLabel']} | Assignee: {assignee}")
        print(f"  🔗 {issue['url']}\n")

    return issues


def add_comment(issue_id: str, body: str) -> dict:
    """Add a comment to an issue"""
    query = """
    mutation CommentCreate($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment {
          id
          body
        }
      }
    }
    """

    result = graphql_request(query, {
        "input": {
            "issueId": issue_id,
            "body": body,
        }
    })

    if result["data"]["commentCreate"]["success"]:
        print(f"✅ Added comment to issue")
        return result["data"]["commentCreate"]["comment"]
    else:
        print("❌ Failed to add comment")
        sys.exit(1)


def get_user_issues(status: str = "", include_archived: bool = False) -> list:
    """Get issues assigned to the current user"""
    query = """
    query Viewer {
      viewer {
        id
        name
        assignedIssues(
          filter: { state: { type: { nin: [completed, canceled] } } }
          first: 50
        ) {
          nodes {
            id
            identifier
            title
            priority
            priorityLabel
            state {
              name
              type
            }
            url
          }
        }
      }
    }
    """

    result = graphql_request(query, {})

    viewer = result["data"]["viewer"]
    issues = viewer["assignedIssues"]["nodes"]

    # Filter by status if provided
    if status:
        status_lower = status.lower()
        issues = [
            issue for issue in issues
            if status_lower in issue['state']['name'].lower()
        ]

    print(f"📋 {viewer['name']}'s issues ({len(issues)} total)\n")

    for issue in issues:
        print(f"{issue['identifier']}: {issue['title']}")
        print(f"  Status: {issue['state']['name']} | Priority: {issue['priorityLabel']}")
        print(f"  🔗 {issue['url']}\n")

    return issues


def get_teams() -> list:
    """Get all teams in the workspace"""
    query = """
    query Teams {
      teams {
        nodes {
          id
          name
          key
        }
      }
    }
    """

    result = graphql_request(query, {})
    teams = result["data"]["teams"]["nodes"]

    print(f"📋 Teams in workspace ({len(teams)} total)\n")

    for team in teams:
        print(f"{team['name']} ({team['key']})")
        print(f"  ID: {team['id']}\n")

    return teams


def main():
    parser = argparse.ArgumentParser(description="Linear API wrapper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-issue command
    get_parser = subparsers.add_parser("get-issue", help="Get issue details")
    get_parser.add_argument("identifier", help="Issue identifier (e.g., ENG-123)")

    # create-issue command
    create_parser = subparsers.add_parser("create-issue", help="Create new issue")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--team-id", required=True)
    create_parser.add_argument("--description", default="")
    create_parser.add_argument("--priority", default="", choices=["", "urgent", "high", "medium", "low", "none"])
    create_parser.add_argument("--status", default="")
    create_parser.add_argument("--assignee-id", default="")

    # update-issue command
    update_parser = subparsers.add_parser("update-issue", help="Update issue")
    update_parser.add_argument("--issue-id", required=True)
    update_parser.add_argument("--title", default="")
    update_parser.add_argument("--description", default="")
    update_parser.add_argument("--priority", default="", choices=["", "urgent", "high", "medium", "low", "none"])
    update_parser.add_argument("--status", default="")

    # search-issues command
    search_parser = subparsers.add_parser("search-issues", help="Search issues")
    search_parser.add_argument("--query", default="")
    search_parser.add_argument("--team-id", default="")
    search_parser.add_argument("--assignee-id", default="")
    search_parser.add_argument("--limit", type=int, default=10)

    # add-comment command
    comment_parser = subparsers.add_parser("add-comment", help="Add comment to issue")
    comment_parser.add_argument("--issue-id", required=True)
    comment_parser.add_argument("--body", required=True)

    # get-user-issues command
    user_parser = subparsers.add_parser("get-user-issues", help="Get user's assigned issues")
    user_parser.add_argument("--status", default="")
    user_parser.add_argument("--include-archived", action="store_true")

    # get-teams command
    teams_parser = subparsers.add_parser("get-teams", help="List all teams")

    args = parser.parse_args()

    # Execute command
    if args.command == "get-issue":
        get_issue(args.identifier)
    elif args.command == "create-issue":
        create_issue(
            args.title,
            args.team_id,
            args.description,
            args.priority,
            args.status,
            args.assignee_id,
        )
    elif args.command == "update-issue":
        update_issue(
            args.issue_id,
            args.title,
            args.description,
            args.priority,
            args.status,
        )
    elif args.command == "search-issues":
        search_issues(
            args.query,
            args.team_id,
            args.assignee_id,
            args.limit,
        )
    elif args.command == "add-comment":
        add_comment(args.issue_id, args.body)
    elif args.command == "get-user-issues":
        get_user_issues(args.status, args.include_archived)
    elif args.command == "get-teams":
        get_teams()


if __name__ == "__main__":
    main()
