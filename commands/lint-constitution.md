---
description: Lint an agent constitution file (CLAUDE.md by default) for missing operational guardrails
argument-hint: [path-to-constitution-file]
allowed-tools: Bash(python3:*)
---

Linter output for the requested file:

!`f="$ARGUMENTS"; python3 "${CLAUDE_PLUGIN_ROOT}/constitution_lint.py" "${f:-CLAUDE.md}"`

Summarize the result for the user. For each FAIL, explain in one line what
guardrail is missing and what a satisfying rule would look like (the check
names describe the missing guardrail — e.g. a concrete spend limit, an
explicit escalation path, a rule treating web/email/API content as data
rather than instructions). If every check passes, say so briefly. These are
heuristic pattern checks on the document text, not a guarantee the rules are
sound — say that too. Do not edit any file unless the user explicitly asks.
