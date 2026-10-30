# Understanding Customer Engagement and Conversion in Online Retail

## Executive summary
An independent analysis of **2,756,101 Retailrocket events** recorded between May and September 2015 shows that only **9,952 of 32,934** visitors who reached a timestamp-ordered cart milestone later reached a purchase milestone (**30.22% progression**, **69.78% drop-off**). This is a visitor-level *observed funnel*, not a session-level checkout abandonment metric. Among visitors with adequate follow-up, first-week repeat-day engagement was associated with a higher subsequent purchase rate, but the observational comparison cannot establish causality.

## Business questions and methodology
1. Where do visitors fail to progress through observed view → cart → purchase milestones? Count distinct visitors in chronological order, requiring strictly later timestamps.
2. Does first-week repeat engagement correlate with later purchases? Define engagement using days 0–7 after first-observed activity, then purchases during days 7–37; require complete follow-up.
3. How frequently do visitors return on an exact later day? Use first-observed cohorts with horizon-specific eligible populations for D1, D7 and D30.
4. Which products show significant interactions? Compare item view, cart and purchase **event ratios**, filtering to items with at least 100 views.

## Finding 1 — The largest observed funnel drop-off is after carting
**Evidence:** 1,404,179 visitors viewed a product, 32,934 later added something to a cart, and 9,952 subsequently purchased. View → cart progression was **2.35%**; cart → purchase progression was **30.22%**. **22,982 of the 32,934 cart-stage visitors (69.78%)** had no later qualifying transaction.

**Implication:** Investigate cart-to-purchase journeys, but do not claim checkout UX caused the drop-off. There are no session IDs, checkout-step events or guaranteed same-item matches. **Next step:** instrument checkout initiation, payment failures, item-level cart linkage and completion within a fixed observation window.

## Finding 2 — Repeat observed engagement is associated with later conversion
**Evidence:** Among 1,066,890 visitors with a full 37-day observation opportunity, **354 of 61,381** visitors active on 2+ distinct days in their first week later purchased (0.5767%), versus **530 of 1,005,509** active on one day (0.0527%). Difference: **0.524 percentage points**; 95% confidence interval **0.467–0.587 percentage points**.

**Implication:** Early repeated engagement helps identify a segment worth investigating. It does **not** prove that making people return will increase purchases. Selection and underlying intent may explain the contrast. **Next step:** pre-register a targeted experiment and collect acquisition and session context.

## Finding 3 — Exact-day observed return rates are low
**Evidence:** D1: **38,827 / 1,406,800 (2.760%)**; D7: **7,610 / 1,357,178 (0.561%)**; D30: **1,797 / 1,141,997 (0.157%)**. Denominators vary because visitors lacking enough follow-up are excluded.

**Implication:** Establish retention monitoring using first-observed cohorts and defensible eligibility rules. These are not signup retention rates, and horizon-specific populations differ.

## Recommended actions, prioritized
**P1 — Improve funnel event instrumentation.** Highest diagnostic value; fixes inability to localize drop-off or attribute checkout failures.

**P2 — Evaluate repeat-engagement hypotheses.** Design a randomized intervention around cart continuation or return experience, rather than inferring causality from the cohort contrast.

**P3 — Monitor first-observed return cohorts and product engagement.** Keep right-censoring rules, item minimum-volume thresholds and rates visible to analysts.

## Hypothetical A/B experiment
Randomize eligible visitors at cart initiation between current and simplified checkout experiences, keeping assignment stable by visitor. Primary metric: seven-day cart-to-purchase conversion. Check checkout errors, page performance and refunds as guardrails. Power calculations require a baseline aligned with this experiment's eligibility and outcome window. **No randomized experiment occurred in the source dataset.**

## Methodological boundaries
This dataset cannot establish unique shopping sessions, actual new-user acquisition, causal treatment effects, revenue lift or a particular checkout failure. Duplicate event rows were flagged but retained. Findings above came from an independent pandas audit; **DuckDB execution, multivariable logistic regression and Tableau publication remain unverified** until run separately.
