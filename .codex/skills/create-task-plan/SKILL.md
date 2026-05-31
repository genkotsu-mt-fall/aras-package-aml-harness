---
name: create-task-plan
description: Create the next numbered task folder under a repository tasks/ directory and draft a change-plan.md inside it. Use when the user asks to create a task, task folder, work item folder, implementation plan, change plan, or planning artifact in tasks/task-### form before making code changes.
---

# Create Task Plan

## Overview

Create a new `tasks/task-###` folder using the next available number, then write a focused `change-plan.md` for the requested work.

Keep the plan repository-specific, implementation-oriented, and concise enough that another Codex session can execute it without rediscovering the task.

## Workflow

1. Inspect the repository root and confirm `tasks/` exists.
2. List existing folders matching `tasks/task-###`.
3. Pick the next number after the highest existing numeric suffix. Preserve 3-digit zero padding, for example `task-013`.
4. Create only the new task folder. Do not modify existing task folders.
5. Draft `change-plan.md` in the new folder.
6. Verify the new folder and file exist.

## Change Plan Content

Write `change-plan.md` in Japanese when the user is working in Japanese, otherwise match the user's language.

Use this structure unless the repository has a stronger existing convention:

```markdown
# タスク: <short task title>

## 目標

<What should be true when the task is complete.>

## 背景

<Relevant context, user request, constraints, and source references.>

## 対象

- <Files, modules, commands, or behavior in scope.>

## 非対象

- <Explicit exclusions and deferred work.>

## 実装方針

- <Concrete implementation steps.>

## テスト観点

- <Focused verification scenarios.>

## 確認事項

- <Open questions, assumptions, or risks.>
```

## Repository Rules

- Follow any `AGENTS.md` instructions before writing the plan.
- Do not read or edit `.env` files.
- Do not add runtime dependencies unless the user explicitly asks.
- Do not delete tests to make checks pass.
- Avoid destructive commands.
- If the repository is `aras-package-aml-harness`, keep plans compatible with the Python standard-library-only checker constraints.

## Quality Bar

- Include concrete file paths, rule names, command names, or examples when they are already known.
- Separate desired behavior from implementation notes.
- Name constraints that should not leak into production code.
- Add test viewpoints that cover positive, negative, and boundary cases when applicable.
- Leave unknowns in `確認事項` instead of pretending they are settled.
