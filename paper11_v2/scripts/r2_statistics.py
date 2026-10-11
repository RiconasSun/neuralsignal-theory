"""Pure R2 statistics/null sidecar for frozen checkpoint 6f5e33e.

No I/O, model fitting, or outcome access. Scores must already be matched causal
nats/unit-bin trial scores on the same frozen units/bins/trials. The parent
supplies canonical patient IDs, seed-resolved candidates and admissible causal
context; this module neither infers patient aliases nor validates event timing.
Budgets/seed follow protocol.json, r2_execution.json and R0-SCHEMA-1.
Population inference is subject-only and paired; trial CIs are descriptive.
"""

import hashlib

import numpy as np

SEED = 20261011
BOOTSTRAPS = 10000
SIGN_FLIPS = 100000
NULL_REPLICATES = 200
ALPHA = 0.05


def _budget(replicates, seed):
    if (isinstance(replicates, (bool, np.bool_))
            or not isinstance(replicates, (int, np.integer))
            or isinstance(seed, (bool, np.bool_))
            or not isinstance(seed, (int, np.integer))
            or replicates != BOOTSTRAPS or seed != SEED):
        raise ValueError("R2 requires replicates=10000 and seed=20261011")


def _vector(values, label):
    result = np.asarray(values, dtype=float)
    if result.ndim != 1 or not result.size or not np.isfinite(result).all():
        raise ValueError(label + " must be a nonempty finite vector")
    return result


def _records(records):
    rows = list(records)
    if not rows:
        raise ValueError("records must not be empty")
    grouped = {}
    for row in rows:
        subject, session = row["subject"], row["session"]
        if not isinstance(subject, str) or not subject:
            raise ValueError("subject must be a nonempty canonical ID")
        if not isinstance(session, str) or not session:
            raise ValueError("session must be a nonempty ID")
        sessions = grouped.setdefault(subject, {})
        if session in sessions:
            raise ValueError("duplicate subject/session record")
        scores = _vector(row["trial_scores"], "trial_scores")
        if "trial_ids" in row:
            ids = list(row["trial_ids"])
            if len(ids) != scores.size or len(set(ids)) != len(ids):
                raise ValueError("trial_ids must uniquely identify every trial")
        sessions[session] = (scores, row)
    return grouped


def aggregate(records):
    """Records: {subject, session, trial_scores, optional trial_ids}.

    Return patient_means, overall_mean, session_means and subject_count.
    mean/subject_means are equivalent compatibility aliases. Each session
    averages its trial scores, each patient averages sessions equally, and the
    population averages patients equally. Input records/arrays are untouched.
    """
    grouped = _records(records)
    sessions = {
        subject: {session: float(scores.mean())
                  for session, (scores, _) in sorted(entries.items())}
        for subject, entries in sorted(grouped.items())
    }
    subjects = {subject: float(np.mean(list(entries.values())))
                for subject, entries in sessions.items()}
    return {"mean": float(np.mean(list(subjects.values()))),
            "overall_mean": float(np.mean(list(subjects.values()))),
            "patient_means": subjects,
            "subject_means": subjects, "session_means": sessions,
            "subject_count": len(subjects)}


def _summary(samples, mean):
    return {"mean": float(mean),
            "ci": tuple(float(x) for x in np.quantile(samples, [0.025, 0.975])),
            "se": float(np.std(samples, ddof=1)),
            "replicates": BOOTSTRAPS, "seed": SEED}


def paired_sign_flip(differences):
    """Two-sided mean-difference sign test, exact for <=20 patients.

    All 2**n signs (including observed and ties) count in the exact denominator.
    Above 20, use 100000 fixed-seed signs and (1+exceedances)/(100001).
    Validity assumes symmetric/exchangeable paired null differences. A small
    roundoff tolerance counts mathematically tied floating-point sums as ties.
    """
    delta = _vector(differences, "differences")
    n = delta.size
    observed = abs(float(delta.sum()))
    tolerance = 8 * np.finfo(float).eps * n * float(np.abs(delta).sum())
    exceedances = 0
    exact = n <= 20
    total = (1 << n) if exact else SIGN_FLIPS
    rng = np.random.default_rng(SEED)
    for start in range(0, total, 8192):
        size = min(8192, total - start)
        if exact:
            indices = np.arange(start, start + size, dtype=np.uint64)
            signs = 2 * ((indices[:, None] >> np.arange(n, dtype=np.uint64))
                         & 1).astype(float) - 1
        else:
            signs = 2 * rng.integers(0, 2, size=(size, n)) - 1
        statistics = np.abs(np.sum(signs * delta, axis=1))
        exceedances += int(np.count_nonzero(statistics >= observed - tolerance))
    return {"p_value": exceedances / total if exact else
            (1 + exceedances) / (1 + total),
            "method": "exact" if exact else "monte_carlo",
            "enumerations": total, "seed": None if exact else SEED,
            "caveat": "Symmetric/exchangeable paired null required."}


def subject_statistics(differences, replicates=BOOTSTRAPS, seed=SEED):
    """One left-minus-right difference per independent patient.

    Return left-minus-right mean and percentile paired CI, bootstrap SE and
    two-sided sign-flip result. Resampling paired differences preserves pairing.
    Caller must enforce patient independence and disclose postselection.
    """
    _budget(replicates, seed)
    delta = _vector(differences, "differences")
    indices = np.random.default_rng(SEED).integers(
        0, len(delta), size=(BOOTSTRAPS, len(delta)))
    result = _summary(delta[indices].mean(axis=1), delta.mean())
    result.update(subject_count=len(delta), sign_flip=paired_sign_flip(delta),
                  inference_unit="patient", bootstrap="subject-only paired")
    return result


def holm(p_values):
    """Exactly six raw contrast p-values; return adjusted values in input order.

    Apply separately to development and external sets: three family pairs and
    three comparisons to the frozen strongest baseline. No automatic pooling.
    """
    p = _vector(p_values, "p_values")
    if p.size != 6 or np.any((p < 0) | (p > 1)):
        raise ValueError("Holm requires exactly six probabilities")
    order = np.argsort(p, kind="stable")
    adjusted = np.empty(6)
    adjusted[order] = np.minimum(1, np.maximum.accumulate(
        p[order] * np.arange(6, 0, -1)))
    return adjusted


def trial_ci(values, replicates=BOOTSTRAPS, seed=SEED):
    """10000 whole-population-trial resamples, descriptive session CI.

    One scalar per complete trial, never per neuron/bin. Trial scores must use
    the frozen common normalization. Not an independent-patient inference.
    """
    _budget(replicates, seed)
    scores = _vector(values, "trial_scores")
    indices = np.random.default_rng(SEED).integers(
        0, len(scores), size=(BOOTSTRAPS, len(scores)))
    result = _summary(scores[indices].mean(axis=1), scores.mean())
    result["inference_unit"] = "whole trial, descriptive conditional session"
    return result


def _trial_samples(entries, size, rng):
    values = np.zeros(size)
    for _, (scores, _) in sorted(entries.items()):
        indices = rng.integers(0, len(scores), size=(size, len(scores)))
        values += scores[indices].mean(axis=1) / len(entries)
    return values


def patient_ci(records):
    """Descriptive whole-trial CI for exactly one patient's retained sessions.

    Resample trials independently within every session; equal-session mean.
    No patient resampling and no independent-population significance claim.
    """
    rows = list(records)
    grouped = _records(rows)
    if len(grouped) != 1:
        raise ValueError("patient_ci requires exactly one patient")
    samples = _trial_samples(next(iter(grouped.values())), BOOTSTRAPS,
                             np.random.default_rng(SEED))
    result = _summary(samples, aggregate(rows)["mean"])
    result["inference_unit"] = "whole trial, descriptive conditional patient"
    return result


def hierarchical_statistics(records, replicates=BOOTSTRAPS, seed=SEED):
    """Patient-primary, within-session whole-trial bootstrap for one-SE.

    Draw patients with replacement; retain ALL sessions for each draw. Resample
    whole trials independently in each retained session, including independent
    trial draws for duplicate patient draws. Average sessions then patients.
    SE is the sample SD (ddof=1) of 10000 resampled population scores. Its CI is
    descriptive hierarchical uncertainty; population paired inference instead
    uses subject_statistics. Canonical sorted IDs make record order immaterial.
    """
    _budget(replicates, seed)
    rows = list(records)
    grouped = _records(rows)
    subjects = sorted(grouped)
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(subjects), size=(BOOTSTRAPS, len(subjects)))
    samples = np.zeros(BOOTSTRAPS)
    # Vectorize independent trial draws for each patient occurrence/slot.
    for slot in range(len(subjects)):
        for index, subject in enumerate(subjects):
            selected = np.flatnonzero(draws[:, slot] == index)
            if selected.size:
                samples[selected] += _trial_samples(
                    grouped[subject], selected.size, rng) / len(subjects)
    result = _summary(samples, aggregate(rows)["mean"])
    result["inference_unit"] = "patient primary, whole trials within sessions"
    return result


def hierarchical_se(sessionrecords, replicates=BOOTSTRAPS, seed=SEED):
    """Return scalar patient-primary whole-trial sample-SD standard error."""
    return hierarchical_statistics(sessionrecords, replicates, seed)["se"]


def _alignment(grouped):
    return tuple((subject, session, len(scores),
                  tuple(row["trial_ids"]) if "trial_ids" in row else None)
                 for subject, entries in sorted(grouped.items())
                 for session, (scores, row) in sorted(entries.items()))


def choose_one_se(candidates, replicates=BOOTSTRAPS, seed=SEED):
    """Select ONE global configuration from a complete, seed-resolved grid.

    Candidates in frozen order: {config: dict including ridge, records,
    mean_parameters: float}. Parent computes mean_parameters from total nominal
    shared + extra counts with equal-session/equal-patient weights.
    Matched trial_ids are recommended; absent IDs imply caller-certified matched
    trial order. All candidates must match IDs/session/trial structure.
    Eligibility: mean >= best mean - hierarchical SE of best-mean candidate.
    Prefer lowest equal-session/equal-patient mean complexity, then highest
    ridge, then original candidate order. Return selected_index/config, best
    index/SE, threshold and complete frontier. Seed choice is parent-owned,
    strictly training-objective based; no external/final tuning is performed.
    """
    _budget(replicates, seed)
    choices = list(candidates)
    if not choices:
        raise ValueError("candidate grid is empty")
    frontier, alignment = [], None
    for index, candidate in enumerate(choices):
        rows = list(candidate["records"])
        grouped = _records(rows)
        current = _alignment(grouped)
        if alignment is not None and alignment != current:
            raise ValueError("candidates must use the same patients/sessions/trials")
        alignment = current
        config = candidate["config"]
        if not isinstance(config, dict):
            raise ValueError("config must be a dictionary containing ridge")
        ridge = float(config["ridge"])
        if not np.isfinite(ridge) or ridge < 0:
            raise ValueError("ridge must be finite and nonnegative")
        complexity = float(candidate["mean_parameters"])
        if not np.isfinite(complexity) or complexity < 0:
            raise ValueError("mean_parameters must be finite and nonnegative")
        frontier.append({"index": index, "config": candidate["config"],
                         "mean": aggregate(rows)["mean"],
                         "mean_complexity": complexity,
                         "ridge": ridge})
        # Materialize iterator records so best-candidate uncertainty is reusable.
        choices[index] = dict(candidate, records=rows)
    best = max(range(len(choices)), key=lambda i: frontier[i]["mean"])
    se = hierarchical_statistics(choices[best]["records"])["se"]
    threshold = frontier[best]["mean"] - se
    eligible = []
    for item in frontier:
        item["eligible"] = item["mean"] >= threshold
        if item["eligible"]:
            eligible.append(item["index"])
    selected = min(eligible, key=lambda i: (frontier[i]["mean_complexity"],
                                           -frontier[i]["ridge"], i))
    return {"selection": choices[selected]["config"], "audit": frontier,
            "selected_index": selected, "selected_config": choices[selected]["config"],
            "best_index": best, "best_se": se, "threshold": threshold,
            "frontier": frontier}


def partition_rng(replicate, partition=None):
    """Fresh local generator, seed 20261011+replicate (0..199).

    A named partition uses a stable SHA-256 SeedSequence spawn key, rooted in
    the frozen seed+replicate. Different names separate partition substreams;
    no Python salted hash or global/shared RNG. None is a single-partition
    compatibility stream. transform_null requires an explicit nonempty name.
    """
    if (isinstance(replicate, (bool, np.bool_))
            or not isinstance(replicate, (int, np.integer))
            or not 0 <= replicate < NULL_REPLICATES):
        raise ValueError("replicate must be an integer in 0..199")
    if partition is None:
        return np.random.default_rng(SEED + int(replicate))
    if not isinstance(partition, str) or not partition:
        raise ValueError("partition must be a nonempty stable identifier")
    digest = hashlib.sha256(partition.encode("utf-8")).digest()
    key = tuple(int.from_bytes(digest[i:i + 4], "little")
                for i in range(0, len(digest), 4))
    return np.random.default_rng(np.random.SeedSequence(
        SEED + int(replicate), spawn_key=key))


def _counts(counts):
    values = np.asarray(counts)
    if (values.ndim != 3 or any(size == 0 for size in values.shape)
            or not np.issubdtype(values.dtype, np.number)
            or np.iscomplexobj(values) or not np.isfinite(values).all()
            or np.any(values < 0) or np.any(values != np.floor(values))):
        raise ValueError("counts must be finite nonnegative integers [N,T,U]")
    return values


def _offsets(bins):
    if bins == 60:
        return 5, 21
    if bins == 10:
        return 5, 10
    raise ValueError("circular nulls require registered T=60 or T=10")


def bin_permutation(counts, replicate, partition=None):
    """Independent trial/unit bin permutations preserving every trial/unit total."""
    values = _counts(counts)
    rng = partition_rng(replicate, partition)
    result = values.copy()
    for trial in range(values.shape[0]):
        for unit in range(values.shape[2]):
            result[trial, :, unit] = rng.permutation(values[trial, :, unit])
    return result


def circular_shift(counts, replicate, partition=None):
    """Return (counts_copy, offsets[N,U]); independent nonidentity rotations."""
    values = _counts(counts)
    low, high = _offsets(values.shape[1])
    shifts = partition_rng(replicate, partition).integers(
        low, high, size=(values.shape[0], values.shape[2]))
    result = values.copy()
    for trial in range(values.shape[0]):
        for unit in range(values.shape[2]):
            result[trial, :, unit] = np.roll(values[trial, :, unit], shifts[trial, unit])
    return result, shifts


def context_rotate(counts, context, replicate, partition=None):
    """Return (unchanged_counts_copy, rotated_context, offsets[N]).

    Context [N,T,X] contains ONLY caller-certified known-at-scored-time timing
    covariates, with training-fitted transforms/mask already fixed. Rotate all
    context columns together by one admissible offset per trial. Never rotate
    trials, counts, partition membership or future/response/outcome attributes.
    """
    values = _counts(counts)
    x = np.asarray(context)
    if (x.ndim != 3 or x.shape[:2] != values.shape[:2]
            or not np.issubdtype(x.dtype, np.number) or np.iscomplexobj(x)
            or not np.isfinite(x).all()):
        raise ValueError("context must be finite matching [N,T,X]")
    low, high = _offsets(values.shape[1])
    shifts = partition_rng(replicate, partition).integers(low, high, size=values.shape[0])
    result = x.copy()
    for trial in range(values.shape[0]):
        result[trial] = np.roll(x[trial], shifts[trial], axis=0)
    return values.copy(), result, shifts


def transform_null(y, x, kind, replicate, external=False, *, partition):
    """Parent API: return (transformed_y, transformed_x, countaudit).

    kind is bin_permutation, circular_shift or context_rotate. external=False
    requires T=60; True requires T=10. A stable explicit partition identifier
    (including session/split) separates RNG streams. Same identifier/replicate
    gives reproducible controls. x contains only known-at-time timing context;
    causal history must be recomputed by the parent from transformed counts.
    Audit includes before/after [N,U] totals, shifts where applicable, root seed,
    partition and stream derivation. No caller array is modified or shared.
    """
    values = _counts(y)
    if not isinstance(external, (bool, np.bool_)):
        raise ValueError("external must be boolean")
    if values.shape[1] != (10 if external else 60):
        raise ValueError("epoch bins do not match external/primary policy")
    if not isinstance(partition, str) or not partition:
        raise ValueError("partition must explicitly identify session/split")
    context = np.asarray(x)
    if (context.ndim != 3 or context.shape[:2] != values.shape[:2]
            or not np.issubdtype(context.dtype, np.number)
            or np.iscomplexobj(context) or not np.isfinite(context).all()):
        raise ValueError("context must be finite matching [N,T,X]")
    if kind == "bin_permutation":
        transformed = bin_permutation(values, replicate, partition)
        transformed_x, shifts = context.copy(), None
    elif kind == "circular_shift":
        transformed, shifts = circular_shift(values, replicate, partition)
        transformed_x = context.copy()
    elif kind == "context_rotate":
        transformed, transformed_x, shifts = context_rotate(
            values, context, replicate, partition)
    else:
        raise ValueError("unknown null kind")
    # Python-integer accumulation avoids overflow for integer count arrays.
    before = values.astype(object).sum(axis=1)
    after = transformed.astype(object).sum(axis=1)
    preserved = bool(np.array_equal(before, after))
    if not preserved:
        raise ArithmeticError("null transform failed count preservation")
    audit = {"kind": kind, "replicate": int(replicate),
             "root_seed": SEED + int(replicate), "partition": partition,
             "rng_context": "SHA256(partition) SeedSequence spawn_key",
             "before": before.tolist(), "after": after.tolist(),
             "count_preserved": preserved, "counts_unchanged": bool(
                 np.array_equal(values, transformed)),
             "shifts": None if shifts is None else shifts.tolist()}
    return transformed, transformed_x, audit


# Descriptive aliases for callers using the more specific names.
session_ci = trial_ci
holm_six = holm
one_se_select = choose_one_se
