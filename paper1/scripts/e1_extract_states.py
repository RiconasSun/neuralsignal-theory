from __future__ import annotations

import argparse
import os
from collections import defaultdict
from typing import Dict, List, Tuple

from common import (
    as_float,
    ensure_dir,
    expand_glob,
    fail,
    infer_context,
    infer_cwp,
    infer_domain,
    infer_load,
    mean_vector,
    parse_subject_run,
    read_table,
    roi_columns,
    root_path,
    sub_vec,
    task_id,
    vector_from_row,
    write_json,
    write_table,
)


def native_grid_timeseries(bold_path: str, bins: tuple[int, int, int], tr: float | None) -> tuple[List[Dict[str, object]], int]:
    try:
        import nibabel as nib
        import numpy as np
    except Exception as exc:
        fail(f"nibabel/numpy are required for native grid extraction: {exc}")
    img = nib.load(bold_path)
    data = img.get_fdata(dtype="float32")
    if data.ndim != 4:
        fail(f"BOLD image is not 4D: {bold_path}")
    shape = data.shape[:3]
    n_time = data.shape[3]
    x_edges = np.linspace(0, shape[0], bins[0] + 1, dtype=int)
    y_edges = np.linspace(0, shape[1], bins[1] + 1, dtype=int)
    z_edges = np.linspace(0, shape[2], bins[2] + 1, dtype=int)
    roi_series = []
    for xi in range(bins[0]):
        for yi in range(bins[1]):
            for zi in range(bins[2]):
                xs, xe = x_edges[xi], x_edges[xi + 1]
                ys, ye = y_edges[yi], y_edges[yi + 1]
                zs, ze = z_edges[zi], z_edges[zi + 1]
                block = data[xs:xe, ys:ye, zs:ze, :]
                if block.size == 0:
                    roi_series.append([0.0] * n_time)
                else:
                    with np.errstate(invalid="ignore"):
                        vec = np.nanmean(block.reshape(-1, n_time), axis=0)
                    roi_series.append([float(x) if x == x else 0.0 for x in vec])
    rows = []
    subject, run = parse_subject_run(bold_path)
    for t in range(n_time):
        row: Dict[str, object] = {"subject": subject, "run": run, "time": float(t) * tr if tr else float(t)}
        for j, series in enumerate(roi_series):
            row[f"roi_{j + 1:03d}"] = series[t]
        rows.append(row)
    return rows, len(roi_series)


def extract_timeseries_from_nifti(bold_paths: List[str], atlas_img: str, out_dir: str, tr: float | None) -> List[str]:
    try:
        from nilearn.maskers import NiftiLabelsMasker
    except Exception as exc:
        fail(f"nilearn is required for --bold-glob/--atlas-img extraction: {exc}")
    if not os.path.isfile(atlas_img):
        fail(f"atlas image not found: {atlas_img}")
    ensure_dir(out_dir)
    masker = NiftiLabelsMasker(labels_img=atlas_img, standardize=False, detrend=False, t_r=tr)
    out_paths: List[str] = []
    for bold_path in bold_paths:
        subject, run = parse_subject_run(bold_path)
        matrix = masker.fit_transform(bold_path)
        if matrix is None or len(matrix) == 0:
            fail(f"no time points extracted from {bold_path}")
        n_roi = len(matrix[0])
        out_path = os.path.join(out_dir, subject, f"{subject}_task-paper1_{run}_timeseries.csv")
        ensure_dir(os.path.dirname(out_path))
        rows = []
        for i, values in enumerate(matrix):
            t = float(i) * tr if tr else float(i)
            row = {"subject": subject, "run": run, "time": t}
            for j in range(n_roi):
                row[f"roi_{j + 1:03d}"] = float(values[j])
            rows.append(row)
        write_table(out_path, rows)
        out_paths.append(out_path)
    return out_paths


def extract_timeseries_from_native_grid(bold_paths: List[str], out_dir: str, tr: float | None, bins: tuple[int, int, int]) -> List[str]:
    ensure_dir(out_dir)
    out_paths: List[str] = []
    expected_roi = bins[0] * bins[1] * bins[2]
    for bold_path in bold_paths:
        subject, run = parse_subject_run(bold_path)
        rows, n_roi = native_grid_timeseries(bold_path, bins, tr)
        if n_roi != expected_roi:
            fail(f"native grid ROI count mismatch in {bold_path}")
        out_path = os.path.join(out_dir, subject, f"{subject}_task-paper1_{run}_timeseries.csv")
        ensure_dir(os.path.dirname(out_path))
        write_table(out_path, rows)
        out_paths.append(out_path)
    write_json(
        root_path("state_extraction", "native_grid_extraction.json"),
        {
            "status": "completed",
            "method": "native_image_space_grid",
            "bins": list(bins),
            "roi_count": expected_roi,
            "bold_files": len(bold_paths),
            "limitation": "Grid cells are fixed by image index space and are not a neuroanatomical atlas.",
        },
    )
    return out_paths


def inferred_trial_ids(events: List[Dict[str, str]]) -> List[str]:
    explicit = [e.get("trial_id") or e.get("trial") or e.get("trial_index") for e in events]
    if any(explicit):
        return [str(x) if x else str(i + 1) for i, x in enumerate(explicit)]
    trial = 0
    ids: List[str] = []
    active = False
    for event in events:
        cwp = infer_cwp(event)
        if cwp in {"CUE", "ENCODE"} or not active:
            trial += 1
            active = True
        ids.append(str(trial))
        if cwp in {"PROBE", "REST"}:
            active = False
    return ids


def load_timeseries(paths: List[str]) -> Tuple[Dict[Tuple[str, str], List[Dict[str, str]]], List[str]]:
    out: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    all_roi_cols: List[str] | None = None
    for path in paths:
        rows = read_table(path)
        if not rows:
            continue
        cols = roi_columns(rows)
        if not cols:
            fail(f"no ROI columns found in time-series file: {path}")
        if all_roi_cols is None:
            all_roi_cols = cols
        elif cols != all_roi_cols:
            fail(f"ROI columns differ in {path}; all runs must use the same fixed atlas")
        subject, run = parse_subject_run(path, rows[0])
        for row in rows:
            row.setdefault("subject", subject)
            row.setdefault("run", run)
        out[(subject, run)] = rows
    if not out:
        fail("no time-series CSV files found; expected columns time, roi_001, roi_002, ...")
    return out, all_roi_cols or []


def rows_in_window(rows: List[Dict[str, str]], start: float, end: float) -> List[Dict[str, str]]:
    selected = []
    for row in rows:
        t = as_float(row.get("time") or row.get("tr") or row.get("frame"), default=None)
        if start <= t < end:
            selected.append(row)
    return selected


def event_stage_state(
    event: Dict[str, str],
    ts_rows: List[Dict[str, str]],
    roi_cols: List[str],
    hrf_lag: float,
    baseline_seconds: float,
) -> Dict[str, object] | None:
    cwp = infer_cwp(event)
    if cwp not in {"ENCODE", "MAINTAIN", "PROBE"}:
        return None
    onset = as_float(event.get("onset"), default=None)
    duration = as_float(event.get("duration"), default=None)
    start = onset + hrf_lag
    end = start + duration
    stage_rows = rows_in_window(ts_rows, start, end)
    if not stage_rows:
        return None
    state = mean_vector([vector_from_row(r, roi_cols) for r in stage_rows])
    baseline_start = max(0.0, onset - baseline_seconds + hrf_lag)
    baseline_end = onset + hrf_lag
    baseline_rows = rows_in_window(ts_rows, baseline_start, baseline_end)
    baseline = mean_vector([vector_from_row(r, roi_cols) for r in baseline_rows]) if baseline_rows else [0.0] * len(state)
    delta = sub_vec(state, baseline)
    domain = infer_domain(event)
    load = infer_load(event)
    context = infer_context(event)
    return {
        "cwp": cwp,
        "domain": domain,
        "load": load,
        "context": context,
        "task_id": task_id(domain, load, cwp, context),
        "onset": onset,
        "duration": duration,
        "hrf_lag": hrf_lag,
        "baseline_start": baseline_start,
        "baseline_end": baseline_end,
        "n_timepoints": len(stage_rows),
        **{col: state[i] for i, col in enumerate(roi_cols)},
        **{f"delta_{col}": delta[i] for i, col in enumerate(roi_cols)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="E1: extract stage-level brain states from events + ROI time-series CSV.")
    parser.add_argument("--events-glob", default=root_path("data_manifest", "**", "*events.tsv"))
    parser.add_argument("--timeseries-glob", default=root_path("state_extraction", "input_timeseries", "**", "*.csv"))
    parser.add_argument("--bold-glob", default="")
    parser.add_argument("--atlas-img", default="")
    parser.add_argument("--native-grid", action="store_true")
    parser.add_argument("--grid-bins", default="6,6,6")
    parser.add_argument("--tr", type=float, default=None)
    parser.add_argument("--out", default=root_path("state_extraction", "stage_states.csv"))
    parser.add_argument("--timeseries-out-dir", default=root_path("state_extraction", "input_timeseries"))
    parser.add_argument("--hrf-lag", type=float, default=4.0)
    parser.add_argument("--baseline-seconds", type=float, default=4.0)
    args = parser.parse_args()

    event_paths = expand_glob(args.events_glob)
    ts_paths = expand_glob(args.timeseries_glob)
    if args.bold_glob and args.native_grid:
        bold_paths = expand_glob(args.bold_glob)
        if not bold_paths:
            fail(f"no BOLD files matched {args.bold_glob}")
        bins_raw = [int(x.strip()) for x in args.grid_bins.split(",")]
        if len(bins_raw) != 3 or any(x <= 0 for x in bins_raw):
            fail("--grid-bins must be three positive integers, for example 6,6,6")
        ts_paths = extract_timeseries_from_native_grid(
            bold_paths,
            args.timeseries_out_dir,
            args.tr,
            (bins_raw[0], bins_raw[1], bins_raw[2]),
        )
    elif args.bold_glob and args.atlas_img:
        bold_paths = expand_glob(args.bold_glob)
        if not bold_paths:
            fail(f"no BOLD files matched {args.bold_glob}")
        ts_paths = extract_timeseries_from_nifti(
            bold_paths,
            args.atlas_img,
            args.timeseries_out_dir,
            args.tr,
        )
    if not event_paths:
        fail(f"no events files matched {args.events_glob}")
    if not ts_paths:
        fail(f"no ROI time-series CSV files matched {args.timeseries_glob}")
    ts_by_run, roi_cols = load_timeseries(ts_paths)

    rows_out: List[Dict[str, object]] = []
    skipped_events = 0
    for event_path in event_paths:
        events = read_table(event_path)
        if not events:
            continue
        subject, run = parse_subject_run(event_path, events[0])
        ts_rows = ts_by_run.get((subject, run))
        if ts_rows is None:
            skipped_events += len(events)
            continue
        trial_ids = inferred_trial_ids(events)
        for event, trial_id in zip(events, trial_ids):
            state = event_stage_state(event, ts_rows, roi_cols, args.hrf_lag, args.baseline_seconds)
            if state is None:
                skipped_events += 1
                continue
            state.update({"subject": subject, "run": run, "trial_id": trial_id, "source_events": event_path})
            rows_out.append(state)

    if not rows_out:
        fail("no ENCODE/MAINTAIN/PROBE states extracted; check processing_stage labels, HRF lag, and time-series coverage")

    meta_cols = [
        "subject",
        "run",
        "trial_id",
        "cwp",
        "domain",
        "load",
        "context",
        "task_id",
        "onset",
        "duration",
        "hrf_lag",
        "baseline_start",
        "baseline_end",
        "n_timepoints",
        "source_events",
    ]
    fieldnames = meta_cols + roi_cols + [f"delta_{c}" for c in roi_cols]
    write_table(args.out, rows_out, fieldnames)
    write_json(
        os.path.join(os.path.dirname(args.out), "e1_summary.json"),
        {
            "experiment": "E1",
            "status": "completed",
            "events_files": len(event_paths),
            "timeseries_files": len(ts_paths),
            "states_extracted": len(rows_out),
            "skipped_events": skipped_events,
            "roi_count": len(roi_cols),
            "output": os.path.abspath(args.out),
            "hrf_lag": args.hrf_lag,
            "baseline_seconds": args.baseline_seconds,
        },
    )
    print(f"E1 wrote {len(rows_out)} states to {args.out}")


if __name__ == "__main__":
    main()
