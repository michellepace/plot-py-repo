---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git branch:*), Bash(git remote:*)
description: Clean up after PR merge on GitHub (pull, delete branch, prune, switch to main)
---

# Post-Merge Cleanup

I have merged the PR and deleted the branch on GitHub. Please:

1. Pull latest changes from origin
2. Delete the old feature branch locally
3. Prune remote-tracking references
4. Switch to main branch
5. Confirm clean Git status with a summary table (use emojis)

## Instructions

- Use `git pull origin main` to get latest changes
- Use `git branch -d <branch-name>` to delete the local branch (find current branch first)
- Use `git remote prune origin` to clean up deleted remote branches
- Use `git checkout main` to switch to main
- Show final status in a clean table format with emojis
