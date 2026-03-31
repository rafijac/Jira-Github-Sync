# Jira-GitHub MCP Sync — Test Repository

A minimal test-bed for validating the **Jira → Code Fix → GitHub PR → Jira Update**
automation loop driven by MCP-connected LLM agents.

---

## Repository Structure

```
.
├── .github/
│   └── copilot-instructions.md   # LLM automation driver (the "loop script")
├── src/
│   └── calculator.py             # Application code — contains a deliberate bug
├── tests/
│   └── test_calculator.py        # Pytest suite — 3 tests fail on the buggy code
├── mcp_config.json               # MCP server entry-points (fill in your tokens)
├── requirements.txt
└── JIRA_TICKET_TEMPLATE.md       # Pre-written Jira description to paste into JIRA-101
```

---

## The Bug (JIRA-101)

`src/calculator.py` — `calculate_shipping_cost`:  
The `elif weight_kg >= 5` branch is a superset of `elif weight_kg > 20`, making
the heavy-shipping tier (`$15.00`) unreachable dead code. Any package over 20 kg
is silently charged the standard rate (`$5.00`).

**3 tests fail out of the box:**
- `TestHeavyShipping::test_just_over_20kg`
- `TestHeavyShipping::test_very_heavy_package`
- `TestOrderTotal::test_heavy_shipping_order`

Run to confirm:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## MCP Setup

Edit `mcp_config.json` and replace every `YOUR_*` placeholder:

| Placeholder | Where to get it |
|---|---|
| `YOUR_ORG.atlassian.net` | Your Jira cloud URL |
| `YOUR_JIRA_USER_EMAIL` | Jira account email |
| `YOUR_JIRA_API_TOKEN` | Jira → Account Settings → Security → API tokens |
| `YOUR_GITHUB_PAT` | GitHub → Settings → Developer Settings → Personal Access Tokens |

---

## Running the Automation Loop

1. Create Jira ticket **JIRA-101** using the description in `JIRA_TICKET_TEMPLATE.md`.
2. Open this repository in an MCP-capable LLM client (GitHub Copilot, Claude Code, etc.).
3. Provide the ticket ID: `JIRA-101`.
4. The agent will read `.github/copilot-instructions.md` and execute all four steps
   automatically — no further human input required.

---

## Completion Checklist

- [ ] `pytest tests/` exits with 0 failures  
- [ ] Branch `fix/JIRA-101` exists on `origin`  
- [ ] PR open on `main` with title `[JIRA-101] Fix: unreachable heavy-shipping tier`  
- [ ] Jira comment on JIRA-101 contains the PR URL  
- [ ] Jira status of JIRA-101 is `In Review`
