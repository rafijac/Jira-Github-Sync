# Copilot Automation Instructions — Jira-to-GitHub MCP Loop

> **These instructions are the driver for the end-to-end automation.**
> When you (an LLM) read this file with a Jira ticket ID in scope, execute
> the steps below **in order**, using the Jira and GitHub MCP servers
> defined in `mcp_config.json`. Do not skip any step. Do not ask for
> clarification unless a hard blocker is encountered.

---

## Pre-conditions

- You have been given a Jira ticket ID  Treat it as the
  variable `{{TICKET_ID}}` throughout these instructions.
- Both MCP servers (`jira`, `github`) are reachable and authenticated.
- You have read/write access to this repository.

---

## Step 0 — Establish a test baseline

**Tool:** terminal / shell

Before touching any code, run the full test suite and record the results.

```bash
python -m pytest tests/ -v --tb=short 2>&1 | tee baseline_results.txt
```

1. Count and record:
   - Total tests collected.
   - Number **passing** (these must still pass after your fix — do not regress them).
   - Number **failing** (these are your targets).
2. Capture the exact test IDs of every failing test, e.g.:
   ```
   FAILED tests/test_calculator.py::TestHeavyShipping::test_just_over_20kg
   FAILED tests/test_calculator.py::TestHeavyShipping::test_very_heavy_package
   FAILED tests/test_calculator.py::TestOrderTotal::test_heavy_shipping_order
   ```
3. Store this snapshot in your working context as **`BASELINE`**. Every
   subsequent step references it.
4. If **zero tests fail**, halt and surface the message:
   > "No failing tests found on HEAD. Is the correct ticket ID in scope?"
   Do not proceed until the failing tests are confirmed.

---

## Step 1 — Fetch the Jira ticket description

**Tool:** `jira` MCP server

1. Call `jira_get_issue` (or equivalent) with `issueKey = {{TICKET_ID}}`.
2. Extract the following fields from the response:
   - `summary` → use as the PR title prefix.
   - `description` → parse for:
     - **Affected function / file** (e.g. `calculate_shipping_cost` in `src/calculator.py`)
     - **Root-cause description** (the exact bug)
     - **Expected behaviour** (what the correct output should be)
     - **Failing test names** (if listed)
3. Store all extracted values in your working context. You will reference them
   in every subsequent step.

---

## Step 2 — Write a failing reproduction test (Red)

**Tools:** file-write capabilities (no MCP required for this step)

Using the Jira description from Step 1, write a **new, targeted test** that
directly reproduces the reported bug. This test must fail on the unpatched
code. It serves as a living contract: when it goes green, the bug is fixed.

### 2a — Create the reproduction test file

Add `tests/test_repro_{{TICKET_ID}}.py`. Derive test cases entirely from the
ticket's *Failing inputs / expected outputs* table extracted in Step 1.

- Import only the affected function/module identified in the ticket.
- Name the class `TestRepro{{TICKET_ID}}`.
- Write one test method per failing case described in the ticket.
- Each method's docstring must quote the input, the wrong actual output, and
  the correct expected output directly from the ticket description.
- Do **not** copy logic from existing tests — this file must be written
  from the ticket description alone.

```python
"""
Reproduction test for {{TICKET_ID}}.

Intentionally ephemeral — deleted in Step 3e once the existing suite
already covers the same cases.
"""

import pytest
from <module identified in ticket> import <function identified in ticket>


class TestRepro{{TICKET_ID}}:
    """Directly reproduces the bug described in {{TICKET_ID}}."""

    def test_<case_name>(self):
        """
        As reported: <input> → expected <correct_value>, got <wrong_value>.
        """
        assert <function>(<input>) == <expected_value>

    # Add one method per failing case listed in the ticket.
```

### 2b — Confirm the reproduction test fails (Red phase)

```bash
python -m pytest tests/test_repro_{{TICKET_ID}}.py -v
```

Expected output: **all tests in this file FAIL** with `assert 5.0 == 15.0`
(or equivalent). If any unexpectedly pass, re-read the Jira description and
adjust the test inputs until they correctly expose the defect.

---

## Step 3 — Fix the source code (Green phase)

**Tools:** file-read + file-write (no MCP required for this step)

### 3a — Apply the minimal fix

1. Read the file identified in the Jira description.
2. Locate the function named in the ticket.
3. Apply the **smallest change** that makes all failing tests pass without
   altering any currently-passing test behaviour. Derive the correct logic
   exclusively from the ticket's *Expected behaviour* section — do not guess.
4. Do **not** reformat unrelated code, rename variables, or add comments
   beyond what is strictly necessary.

### 3b — Run the reproduction test — confirm Green

```bash
python -m pytest tests/test_repro_{{TICKET_ID}}.py -v
```

All tests in the file must **PASS**. If any still fail, revisit the fix.

### 3c — Run the full suite — confirm no regressions

```bash
python -m pytest tests/ -v --tb=short
```

Expected result:
- Every test that was passing in **BASELINE** still passes.
- Every test that was failing in **BASELINE** now passes.
- Total failures: **0**.

If any baseline-passing test now fails, you introduced a regression — revert
the change and try a narrower fix.

### 3d — Review the diff

Mentally diff the changed file(s) against HEAD:
- Only the file named in the ticket should differ.
- The diff must involve **only** the logic change. No whitespace-only changes
  to unrelated lines, no import additions, no docstring edits.
- If the diff is wider than expected, trim it back.

### 3e — Promote the reproduction test (Keep as regression guard)

`tests/test_repro_{{TICKET_ID}}.py` now passes and acts as a permanent
regression guard — it will catch any future reintroduction of this bug.
Do **not** delete it.

Run the full suite one final time to confirm:

```bash
python -m pytest tests/ -v --tb=short
```

Expected: every test passes, including the new reproduction test.
Record this as **`POST_FIX`**. Zero failures required before proceeding.

---

## Step 4 — Create a branch, commit the fix, and open a Pull Request

**Tool:** `github` MCP server

Perform these sub-steps **in order**:

### 4a — Create a branch
```
github_create_branch(
  repo   = "<OWNER>/<REPO>",          # infer from the repo's git remote
  branch = "fix/{{TICKET_ID}}",       
  from   = "main"
)
```

### 4b — Commit the fix
```
github_create_or_update_file(
  repo    = "<OWNER>/<REPO>",
  path    = "<file path identified in ticket>",
  message = "fix({{TICKET_ID}}): <one-line summary from ticket summary field>\n\n<Root-cause description from ticket, condensed to 2-3 sentences.>",
  content = <base64-encoded patched file content>,
  branch  = "fix/{{TICKET_ID}}"
)
```

### 4c — Open a Pull Request
```
github_create_pull_request(
  repo  = "<OWNER>/<REPO>",
  title = "[{{TICKET_ID}}] <ticket summary field>",
  body  = """
## Summary
Fixes {{TICKET_ID}}: <root-cause description from ticket>.

## Changes
- <Concise description of the change made, derived from the diff in Step 3d.>

## Tests
Baseline captured in Step 0 (`baseline_results.txt`).
All previously-failing tests now pass (verified in `POST_FIX` run, Step 3e):
<paste the BASELINE failing test IDs here, one per line with a leading - >

No regressions. Zero failures.

Closes {{TICKET_ID}}
  """,
  head  = "fix/{{TICKET_ID}}",
  base  = "main"
)
```

4. Capture the returned `html_url` of the PR. You will use it in Step 5.

---

## Step 5 — Update the Jira ticket

**Tool:** `jira` MCP server

### 5a — Post a comment with the PR link
```
jira_add_comment(
  issueKey = "{{TICKET_ID}}",
  body     = "Fix implemented. Pull request opened: <PR_HTML_URL>\n\nBranch: fix/{{TICKET_ID}}"
)
```

### 5b — Transition the ticket status to 'In Review'
1. Call `jira_get_transitions` with `issueKey = {{TICKET_ID}}` to retrieve
   the list of available transitions.
2. Find the transition whose `name` matches `"In Review"` (case-insensitive).
3. Call `jira_transition_issue`:
```
jira_transition_issue(
  issueKey     = "{{TICKET_ID}}",
  transitionId = <id from step above>
)
```

---

## Completion Criteria

The loop is considered **successfully closed** when:

- [ ] `BASELINE` recorded: failing test IDs captured from the Step 0 run.
- [ ] Jira ticket fetched and fields extracted (Step 1).
- [ ] Reproduction test written, confirmed **red** on unpatched code (Step 2).
- [ ] Source fix applied; reproduction test and all `BASELINE` failures turn **green** (Step 3).
- [ ] Diff reviewed — only the target file changed, no unrelated edits (Step 3d).
- [ ] Reproduction test promoted as a regression guard; `POST_FIX` full suite run shows **zero failures** (Step 3e).
- [ ] A branch `fix/{{TICKET_ID}}` exists on `origin` (Step 4).
- [ ] A PR is open targeting `main` with the correct title and body (Step 4).
- [ ] The Jira ticket has a comment containing the PR URL (Step 5).
- [ ] The Jira ticket status is `In Review` (Step 5).

If any step fails, log the error, do not proceed to subsequent steps, and
surface the failure message clearly so a human engineer can intervene.
