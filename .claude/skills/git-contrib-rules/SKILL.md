---
name: git-contrib-rules
description: Enforces contribution rules for this repository — feature branches only (no commits to main), and conventional commit message format. Use before committing or when asked to commit changes.
---

# Git Contribution Rules

Enforces the two contribution rules for this repository:

1. **No direct commits to `main`** — all changes must go through a feature branch.
2. **Conventional commit messages** — messages must follow the [conventional-changelog-metahub](https://github.com/pvdlg/conventional-changelog-metahub#commit-types) format.

## When to Use This Skill

Invoke this skill (or apply these rules automatically) whenever you are about to:

- Create a git commit
- Stage and commit changes on behalf of the user
- Advise the user on how to commit

## Rule 1 — No Direct Commits to `main`

Before committing, check the current branch:

```bash
git branch --show-current
```

If the output is `main` (or `master`):

1. **Stop. Do not commit.**
2. Tell the user they must work on a feature branch, not `main`.
3. Suggest a branch name derived from the work being done, e.g.:
   - `feat/skill-git-contrib-rules`
   - `fix/typo-in-readme`
   - `chore/update-dependencies`
4. Offer to create and switch to the branch:

```bash
git checkout -b <suggested-branch-name>
```

Only proceed with the commit after the branch has been switched.

## Rule 2 — Conventional Commit Messages

Every commit message must start with one of the following prefixes followed by a colon and a space:

| Type       | Use for                                          |
|------------|--------------------------------------------------|
| `feat`     | A new feature                                    |
| `fix`      | A bug fix                                        |
| `docs`     | Documentation changes only                       |
| `style`    | Formatting, whitespace — no logic change         |
| `refactor` | Code change that is neither a fix nor a feature  |
| `perf`     | Performance improvement                          |
| `test`     | Adding or updating tests                         |
| `build`    | Build system or dependency changes               |
| `ci`       | CI/CD configuration changes                      |
| `chore`    | Maintenance tasks that don't fit the above       |
| `revert`   | Reverts a previous commit                        |

**Valid examples:**
- `feat: add post-interview summary export`
- `fix: correct regex for PDF filename parsing`
- `docs: update contributing guidelines`
- `chore: add git-contrib-rules skill`

**Invalid examples (reject these):**
- `Update readme` — missing type prefix
- `WIP` — not a conventional message
- `fixed stuff` — missing type prefix

If the proposed commit message is invalid:

1. **Do not commit.**
2. Point out what is wrong with the message.
3. Suggest a corrected version following the format above.

## Workflow Summary

```
1. Check branch → if main, create feature branch first
2. Check commit message format → if invalid, suggest a fix
3. Only then proceed with the commit
```
