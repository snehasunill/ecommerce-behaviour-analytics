# Proposed experiment (NOT conducted)

**Hypothesis:** a simplified cart checkout will raise purchase completion among eligible cart users.

- Randomization unit: visitor (sticky assignment across devices where identity permits).
- Treatment: redesigned cart with clearer checkout CTA and less friction; control: unchanged cart.
- Primary metric: fraction of randomized eligible cart visitors completing a purchase within seven days of cart entry.
- Secondary: checkout-start rate, checkout error rate, elapsed time to purchase.
- Guardrails: refund/cancellation rate, checkout latency, support contacts, payment failure rate.
- Null: no difference in primary purchase rate. Alternative: two-sided difference.
- Design: 50/50 assignment, 5% two-sided alpha, 80% target power, illustrative absolute minimum detectable effect of 2 percentage points. `data/processed/experiment_power.json` calculates an initial per-arm estimate from historical visitor-funnel conversion; this proxy **does not match** a seven-day randomized eligibility baseline, so a real product team would revise it with instrumented checkout history.
- Analysis: intention-to-treat risk difference with 95% CI, two-proportion test; predefine analysis window, exclusion rules, duration and stopping protocol; one primary test, report exploratory comparisons with multiplicity control.
- Risks: identity collisions, repeat exposures, instrumentation errors, seasonal behavior, sample-ratio mismatch, cross-device assignment, and window censoring.

No treatment assignment exists in Retailrocket data; all effects are hypothetical until an actual randomized experiment is executed.
