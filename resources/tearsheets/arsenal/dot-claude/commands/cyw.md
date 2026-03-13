# cyw (commit your work)

Generate three concise commit summaries for current git changes.

## Instructions

1. Run `git diff --cached > ./commit-staged.diff` to save staged changes
2. Run `git diff > ./commit-unstaged.diff` to save unstaged changes
3. Run `git diff HEAD > ./commit-all.diff` to save all changes
4. Run `git status` to understand the overall state
5. Run `ls` to confirm diff files were created

Then provide three commit summaries:

### Staged Changes Summary
Write a brief 16-word commit summary for staged changes. Do not oversell. Be specific and honest.

### Unstaged Changes Summary
Write a brief 16-word commit summary for unstaged changes. Do not oversell. Be specific and honest.

### All Changes Summary
Write a brief 16-word commit summary for all changes (staged + unstaged). Do not oversell. Be specific and honest.

Format each summary clearly with headers so the user can easily copy the one they need.

If no changes exist in a category, state "No changes" instead of generating a summary.
