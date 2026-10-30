# Verified observed findings — Retailrocket

- Dataset: **2,756,101 recorded events** across **1,407,580 observed visitors**.
- Ordered visitor funnel: **1,404,179 views → 32,934 carts → 9,952 purchases** (distinct visitors, strictly ordered milestones).
- Of visitors reaching the qualifying cart stage, **69.78%** did not have a later observed qualifying purchase; this is not verified checkout abandonment.
- View-to-purchase progression: **0.71%** of visitors with a view.
- Within the follow-up-eligible landmark sample, future 30-day purchase rates differed by **+0.524 percentage points** between repeat-day and single-day first-week engagement groups (association, not causation).
- Repeat group: 354/61,381; single-day group: 530/1,005,509.
- D1 exact-day observed return: **2.76%** (38,827/1,406,800 eligible cohort members).
- D7 exact-day observed return: **0.56%** (7,610/1,357,178 eligible cohort members).
- D30 exact-day observed return: **0.16%** (1,797/1,141,997 eligible cohort members).
- Items with at least 100 observed view events: **3,984**.

## Resume bullet candidates — verify these descriptions before using
- Analyzed **2,756,101 e-commerce behavioral events** with DuckDB SQL, constructing an ordered visitor funnel that quantified **69.78%** observed cart-stage non-progression.
- Compared future purchase rates across first-week engagement groups with 95% confidence intervals and logistic regression, measuring an observed **+0.524-percentage-point** difference while separating predictors from subsequent outcomes.
- Produced **5 Tableau-ready analytical datasets** spanning funnel, engagement, cohort return, temporal trends, and item performance; evaluated **3,984** adequately supported items and documented a checkout A/B test proposal (not conducted).

Dashboard status: CSV exports generated; Tableau visualization still requires manual authoring/publication.
No experiment was run, and no actual improvement in conversion is claimed.
