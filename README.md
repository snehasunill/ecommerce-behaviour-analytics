# E-Commerce Customer Behaviour & Conversion Analytics

**Python · SQL · DuckDB · pandas · SciPy · statsmodels**

An analysis of **2.76 million e-commerce interactions** to understand how shoppers progress from product views to carts and purchases, whether early repeat engagement is associated with later conversion, and what a product team should measure or test next.

The project uses the public [Retailrocket E-Commerce Dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) (May–September 2015). It combines timestamp-ordered SQL funnels, first-observed visitor cohorts, statistical comparisons and an experiment proposal. The findings are **observational**, not evidence of causal product impact.

## Key findings

| Question | Result | Interpretation |
|---|---|---|
| Where do shoppers disengage? | **69.78%** of visitors reaching an ordered cart milestone had no later qualifying purchase (**22,982 of 32,934**). | A large observed drop-off after carting warrants closer investigation; this is **not** a measured checkout-abandonment rate. |
| Is early repeat engagement associated with purchases? | **0.5767%** subsequent purchase rate among first-week multi-day visitors versus **0.0527%** for single-day visitors; **+0.524 percentage points** (95% CI **0.467–0.587 pp**). | The groups differ meaningfully in observed purchase behaviour; selection effects and purchase intent may explain part of the association. |
| How often do visitors return? | Exact-day observed return rates: **D1 2.760%**, **D7 0.561%**, **D30 0.157%**. | Return activity is uncommon on these exact days. Each measure excludes visitors without enough follow-up time. |

### The conversion journey

| Ordered milestone | Unique visitors | Share of viewers |
|---|---:|---:|
| Viewed a product | 1,404,179 | 100% |
| Added to cart after a view | 32,934 | 2.35% |
| Purchased after a qualifying cart | 9,952 | 0.71% |

This is a **visitor-level, timestamp-ordered funnel**: each stage must occur after the previous stage. Events do not necessarily belong to the same item or shopping session. See [verified findings](reports/verified_findings.md) for detailed definitions and counts.

## Dashboard and exploratory views

The repository includes a static preview of the validated aggregate metrics. The analytical pipeline also produces five datasets for further visualization: funnel, engagement groups, first-observed cohort retention, daily activity, and product metrics.

![Preview of conversion and engagement analytics](dashboard/analytics_preview.png)

The preview is generated from observed data; it is not a published Tableau dashboard. See the [dashboard guide](dashboard/README.md) for the export schema and visualization instructions.

## Recommendations for a product team

**1. Instrument the cart-to-purchase journey.** Capture checkout start, payment errors, checkout completion, session identifiers, and consistent item/cart IDs. These events would help locate the source of the observed drop-off rather than attributing it to checkout design without evidence.

**2. Test a specific conversion hypothesis.** Use the engagement association as a reason to investigate, not as proof that encouraging repeat visits causes purchases. The [experiment proposal](reports/experiment_design.md) outlines a hypothetical visitor-randomized checkout test, primary and guardrail metrics, and power analysis. **No A/B test was run on this dataset.**

**3. Track retention and product engagement with defensible denominators.** Monitor first-observed visitor cohorts with explicit follow-up eligibility, and apply minimum support thresholds when reviewing item-level conversion patterns.

For the complete business interpretation, see [the executive insights report](reports/insights.md).

## Analytical approach

- **Data preparation and quality:** Ingested **2,756,101** behavioural events from **1,407,580** distinct visitors. Checked event types, identifiers, timestamps and transaction-ID patterns. Flagged **460 exact duplicate rows** without automatically discarding repeated actions.
- **SQL funnel analysis:** Used DuckDB with CTEs, joins, conditional aggregation and time ordering to distinguish visitor progression from raw event totals.
- **Engagement analysis:** Classified visitors by the number of distinct active days during the first observed week, then measured purchases in a separate subsequent 30-day window among visitors with adequate coverage.
- **Statistical inference:** Estimated group purchase rates and uncertainty, including a 95% confidence interval for the difference in proportions. The codebase includes logistic-regression analysis; the headline findings above rely on verified group comparisons, not a claimed regression effect.
- **Retention and product analysis:** Computed exact-day D1/D7/D30 return rates with right-censoring and item-level event ratios using a minimum of 100 views for item comparisons.

The main analytical SQL queries are in [`sql/`](sql/), with ingestion, analysis, exports and validation in [`src/`](src/).

## Reproduce the analysis

Requires **Python 3.11+** and the original [Retailrocket dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset). Download and extract the CSV files into `data/raw/`:

```text
data/raw/
  events.csv
  item_properties_part1.csv
  item_properties_part2.csv
  category_tree.csv
```

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.run_all
python -m pytest -q
```

The pipeline was run locally against the original dataset, and **all 11 automated tests passed**. It writes analytical outputs to `data/processed/` (intentionally ignored by Git). Test coverage includes ordering, cohort eligibility and consistency between verified aggregates and exported metrics. A passing test suite does not by itself establish that every statistical assumption holds.

## Scope and limitations

Retailrocket records events, not complete checkout sessions, acquisitions or experimental assignments. A cart event followed by no observed transaction is not necessarily a confirmed abandoned checkout. First-observed visitors are not necessarily new customers, and exact-day returns are not signup retention. Engagement comparisons are subject to confounding; they do not establish causation. The data do not support claims about revenue lift, deployed improvements or completed experiments.

**Data source:** [Retailrocket E-Commerce Dataset (Kaggle)](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset). Raw source CSVs and local processed outputs are excluded from this repository; download the dataset from its source and review the applicable usage terms.
