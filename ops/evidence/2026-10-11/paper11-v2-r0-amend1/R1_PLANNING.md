# R1 Verification Plan (Not Executed)

Activate only after complete R0 admission review. Comparative causal predictive
representations; no PLDS latent substitution, no ontology claim, no real-cohort
fit in R1. All scientific scores/nulls/generalization remain R2.

Poisson eta is log expected count per100ms bin, not unscaled rate. Exact scoring
includes log(y!) and sums the joint population log probability before dividing
by actual observed unit-bins. Trial boundaries reset history and filtering.

Discrete/switching models use normalized log-space forward recursion, then exact
backward state/transition expectations for an analytical training gradient.
Switching emissions depend only on previous observed own-unit counts, so hidden
state marginal remains exactly tractable. Full small-sequence path enumeration
must independently match predictive increments and total score<=1e-10nats/bin.

Continuous recurrence is deterministic tanh of previous hidden state, previous
log1p population counts and current known causal context. No latent integration,
proposal or particle score. Validate scalar independent recursion and BPTT
analytical derivatives. Initial hidden/history zero; never use current target
counts, future responses/context or smoothing in predictive scoring.

Six strong baselines use exact Poisson GLMs/stationary rate. Training-only feature
scales and nuisance offsets; all families share frozen combined offset.
Conservative coefficient bounds, objective normalization, free-logit gauge,
optimization budget, seeds11/23/37, convergence and complexity diagnostics must
be explicitly registered before controlled fixture training, not chosen after
looking at winners. Every initialization kept; no favorable-seed exclusion.
Gate failure is preserved and stops, not a reason to drop the failing family.
