# Tableau Public build guide

**Status: Tableau dashboard not built or published.** Five genuine Tableau-ready aggregate CSVs are included in `data/processed/tableau/` from the independently verified pandas export. The `dashboard/analytics_preview.png` file is an independently rendered static preview, **not** a Tableau screenshot.

Build a Tableau dashboard (1200 × 850 px), title **Customer Journey | Engagement & Conversion Analytics**.

1. Connect separately to each of the five aggregated CSVs. Do not physically join unrelated grain tables. Create worksheets from each data source.
2. KPI strip: from `funnel_summary` show `viewed`, `view_to_purchase_pct`, `view_to_cart_pct`, `cart_to_purchase_pct`. Label as *ordered observed visitor funnel*; do not call these events.
3. Funnel: three horizontal bars using `viewed`, `carted`, `purchased`; place stage drop-offs in labels. Use these mutually nested totals rather than raw event counts.
4. Engagement: two bars `engagement_group` vs `purchase_pct`; labels show `visitors`. This is 7-day predictor / 30-day future outcome, not a causal effect.
5. Retention: heatmap `cohort_week` × `day_n`, color `return_pct`; tooltip `eligible_visitors` and `returned_visitors`. Note exact-day D1/D7/D30 and horizon censoring.
6. Weekly trends: `daily_activity`, truncate `event_date` to week, sum `event_count`, color by event. Note aggregation of daily unique visitors cannot yield weekly unique visitors.
7. Item scatter: `views` x-axis vs `purchase_events_per_100_views` y-axis, `itemid` on detail, `carts` in tooltip. The export already filters items with fewer than 100 views. These are event ratios, **not product purchase probabilities**.
8. Add a methodology footer with date coverage, funnel ordering rule, engagement eligibility rule, observational limitations, and small supporting sample sizes.

Use an accessible palette (charcoal, muted teal, amber), restrained fonts, a fixed 2-decimal percentage format, and obvious denominator labels. Dashboard URL/screenshots should be added only after it is actually published.

Do not add category filters without reliable point-in-time mappings. Avoid interpreting cross-dataset filters as synchronized until explicitly implemented.
