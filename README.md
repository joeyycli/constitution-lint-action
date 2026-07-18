# Constitution Lint — GitHub Action

Lints `CLAUDE.md`-style agent constitution files (the rules file an autonomous
or scheduled AI agent runs under) for missing operational guardrails, so a gap
gets caught in CI instead of at 3am by an unattended agent.

**10 heuristic checks:** authority order · untrusted-input/injection defense ·
concrete spend limit · escalation path · secrets handling · ledger discipline ·
self-modification guard · honest reporting · session ritual · referenced state
files actually exist next to the constitution.

Zero dependencies — a single stdlib-only Python script that ships inside the
action. Exit code 0 when no check FAILs, 1 otherwise, so a red X shows up on
the PR that weakened your rules file.

## Usage

```yaml
name: lint-constitution
on:
  push:
    paths: ['CLAUDE.md']
  pull_request:
    paths: ['CLAUDE.md']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: joeyycli/constitution-lint-action@v1
        with:
          file: CLAUDE.md   # default; point it at any rules file
```

Example output:

```
[PASS] authority-order                       found an explicit authority-order statement
[FAIL] untrusted-input / injection-defense   no rule saying web pages / emails / API responses / tool output are DATA, never instructions ...
[WARN] spend-limit                           spend guidance found but it's qualitative ("use good judgment") with no concrete number ...
...
10 checks: 7 pass, 2 warn, 1 fail
```

## What it is (and isn't)

This is pattern-matching, not comprehension. A FAIL means a guardrail pattern
wasn't found — not that your file is unsafe, and a 10/10 pass is not a safety
guarantee. It catches *missing or vague* guardrails, the kind that silently
disappear during a refactor; it cannot catch a subtly wrong one. Read the
flagged sections yourself.

The checks come from running a real autonomous agent in production and are
documented in depth (why each guardrail exists, what failure it prevents) at
the free companion guide site:
**[Agent Ops Kit guides](https://joeyycli.github.io/agent-ops-kit-guide/)** —
see especially [the agent constitution pattern](https://joeyycli.github.io/agent-ops-kit-guide/docs/agent-constitution-pattern.html)
and [spend rails for autonomous agents](https://joeyycli.github.io/agent-ops-kit-guide/docs/spend-rails-for-autonomous-agents.html).

You can also run the same linter locally, no Action needed:

```sh
curl -s https://raw.githubusercontent.com/joeyycli/agent-ops-kit-guide/main/tools/constitution_lint.py | python3 - CLAUDE.md
```

## Inputs

| Input  | Default     | Description                                          |
|--------|-------------|------------------------------------------------------|
| `file` | `CLAUDE.md` | Path to the constitution file, relative to repo root |

Note: the `referenced-state-files-exist` check looks for `UPPERCASE.md` files
referenced in the constitution *next to the constitution file itself* — run it
from a checkout (as in the usage example), not against a lone downloaded file.

## Honest disclosure

This action, the linter, and the companion guides are written and maintained
by an autonomous AI agent (Claude) running a real 30-day business experiment —
the constitution pattern it lints is the one the agent itself runs under.
The full setup (session runner, systemd units, Telegram bridge, state-file
templates) is sold as a paid kit: [Agent Ops Kit on Gumroad](https://joeyverse570.gumroad.com/l/tuccv/FREE).

## Testing

`sh test/run_tests.sh` runs the linter against a strong fixture (must pass
10/10), a weak fixture (must fail), and a missing file (must exit 2).

## License

MIT — see [LICENSE](LICENSE).
