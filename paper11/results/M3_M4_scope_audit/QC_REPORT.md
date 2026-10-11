# M3/M4 Saved Development Results

Original M0-M3 gates PASS, M4 FAIL. Audit reproduction PASS is reporting only;
requested complete scientific execution remains FAIL/INCONCLUSIVE.

Tables:
- baseline_session_candidates.csv: all483 fixed baseline candidates across23 sessions.
- baseline_subject_candidates.csv:189 fixed-candidate summaries (9 subjects x21),
  equal-session weighting within subject; no independent-neuron/window inference.
- model_training_current_run.csv:40 corrected smoke seed fits,32 HMM and8 PLDSd1.
- model_validation_certified_partial.csv:four exact HMM configurations with
  matched trial IDs and deltas versus constant; one session, not subject consistency.
- integration_accuracy.csv:all three failing particle budgets.
- model_completeness.csv:PLDS not accuracy-certified; Hybrid not executed.

Each baseline row includes parameters, convergence, iteration/wall-time cost,
validation mean and descriptive trial SE. Subject summaries are not unbiased
post-selection estimates or inferential confidence intervals. No bootstrap or
cross-family significance calculated. Training ELBO values are never compared
across families as predictive likelihood. Reference particle scores are not
inserted into the certified model comparison table after failed accuracy.

development_diagnostics.png/pdf:fixed ridge1 shown for all baseline families
without optimizing this figure; full grid retained in CSV. The right panel is
a numerical diagnostic, not evidence against continuous neural dynamics.
No valid D1/D2/D3 winner figure can be produced from the incomplete competition.

B0/B1 executed; B2 joint task+timing model missing from frozen candidate grid.
B3 maps only to own-unit five-lag log1p-history ridge-Poisson AR if approved.
Protocol amendment decisions requested before additional fitting. No frozen
source/spec/gate changes, final/external holdout reads or M5-M7 execution.
One-command audit reproduction: ../../REPRODUCE_M3_M4_AUDIT.md.
