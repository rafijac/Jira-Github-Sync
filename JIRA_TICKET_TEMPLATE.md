# Jira Ticket Template — JIRA-101

> Copy-paste the block below verbatim into the Jira ticket **Description** field.
> The automation loop depends on the exact keywords and structure shown here.

---

## Copy-paste block (Jira Description)

```
h2. Bug Report — Unreachable Shipping Tier in calculate_shipping_cost

h3. Affected File & Function
* File: +src/calculator.py+
* Function: +calculate_shipping_cost(weight_kg: float) -> float+

h3. Root Cause
The {{elif}} chain that determines the shipping tier is ordered incorrectly.
The second branch ({{elif weight_kg >= 5}}) is a mathematical superset of the
third branch ({{elif weight_kg > 20}}), so Python never evaluates the heavy-
shipping condition. It is unreachable dead code.

Buggy logic (current):
{code:python}
if weight_kg < 5:
    return 0.00
elif weight_kg >= 5:   # catches ALL weights >= 5, including > 20  <-- BUG
    return 5.00
elif weight_kg > 20:   # DEAD CODE — never reached
    return 15.00
{code}

h3. Expected Behaviour
Shipping cost must follow these tiers exactly:

|| Weight (kg)       || Cost      ||
| < 5               | $0.00 (free) |
| >= 5 and <= 20    | $5.00 (standard) |
| > 20              | $15.00 (heavy) |

The corrected logic should be:
{code:python}
if weight_kg < 5:
    return 0.00
elif weight_kg <= 20:
    return 5.00
else:
    return 15.00
{code}

h3. Failing Tests
The following Pytest tests in +tests/test_calculator.py+ currently fail:

* +TestHeavyShipping::test_just_over_20kg+
** Input: {{weight_kg = 20.1}}
** Expected: {{15.00}}
** Actual:   {{5.00}}

* +TestHeavyShipping::test_very_heavy_package+
** Input: {{weight_kg = 50.0}}
** Expected: {{15.00}}
** Actual:   {{5.00}}

* +TestOrderTotal::test_heavy_shipping_order+
** Depends on {{calculate_shipping_cost(25.0)}} returning {{15.00}}
** Expected total: {{35.00}}
** Actual total:   {{25.00}}

h3. Steps to Reproduce
{code:bash}
git clone <REPO_URL>
cd Jira-GitHub-Sync
pip install -r requirements.txt
pytest tests/test_calculator.py -v
{code}

Expected: 3 failures in TestHeavyShipping and TestOrderTotal.

h3. Acceptance Criteria
* All tests in +tests/test_calculator.py+ pass ({{pytest}} exits 0).
* The fix touches only the {{elif}} ordering inside +calculate_shipping_cost+.
* No currently-passing tests are broken.
* A PR is opened against {{main}} with the branch name {{fix/JIRA-101}}.
```
