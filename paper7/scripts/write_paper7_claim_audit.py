from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PROTOCOL = ROOT / "protocol"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    e0 = read_json(RESULTS / "p7_e0_dataset_toolchain_audit.json")
    recovery = read_json(RESULTS / "p7_environment_recovery_audit.json")
    diagnostic = read_json(RESULTS / "p7_act_sift2_engineering_diagnostic.json")
    final_smoke = read_json(RESULTS / "p7_final_route_single_subject_smoke.json")
    three_subject_smoke = read_json(RESULTS / "p7_e3_three_subject_final_route_smoke.json")
    ten_subject_qc = read_json(RESULTS / "p7_e4_ten_subject_connectome_qc.json")
    labelconvert_qc = read_json(RESULTS / "p7_e5_labelconvert_connectome_qc.json")
    sensitivity_100307 = read_json(RESULTS / "p7_e5_100307_streamline_20000_sensitivity.json")
    streaming_batch = read_json(RESULTS / "p7_e6_streaming_batch_10_2.json")
    streaming_batch_12_3 = read_json(RESULTS / "p7_e6_streaming_batch_12_3.json")
    streaming_batch_15_5 = read_json(RESULTS / "p7_e6_streaming_batch_15_5.json")
    streaming_batch_20_5 = read_json(RESULTS / "p7_e6_streaming_batch_20_5.json")
    streaming_batch_25_5 = read_json(RESULTS / "p7_e6_streaming_batch_25_5.json")
    streaming_batch_30_5 = read_json(RESULTS / "p7_e6_streaming_batch_30_5.json")
    streaming_batch_35_5 = read_json(RESULTS / "p7_e6_streaming_batch_35_5.json")
    streaming_batch_40_5 = read_json(RESULTS / "p7_e6_streaming_batch_40_5.json")
    streaming_batch_45_5 = read_json(RESULTS / "p7_e6_streaming_batch_45_5.json")
    streaming_batch_50_5 = read_json(RESULTS / "p7_e6_streaming_batch_50_5.json")
    streaming_batch_55_5 = read_json(RESULTS / "p7_e6_streaming_batch_55_5.json")
    streaming_batch_60_5 = read_json(RESULTS / "p7_e6_streaming_batch_60_5.json")
    streaming_batch_65_5 = read_json(RESULTS / "p7_e6_streaming_batch_65_5.json")
    streaming_batch_70_5 = read_json(RESULTS / "p7_e6_streaming_batch_70_5.json")
    streaming_batch_75_5 = read_json(RESULTS / "p7_e6_streaming_batch_75_5.json")
    streaming_batch_80_5 = read_json(RESULTS / "p7_e6_streaming_batch_80_5.json")
    streaming_batch_85_5 = read_json(RESULTS / "p7_e6_streaming_batch_85_5.json")
    streaming_batch_90_5 = read_json(RESULTS / "p7_e6_streaming_batch_90_5.json")
    streaming_batch_95_5 = read_json(RESULTS / "p7_e6_streaming_batch_95_5.json")
    streaming_cleanup = read_json(RESULTS / "p7_e6_streaming_cleanup_audit.json")
    available_summary = read_json(RESULTS / "p7_e6_available_fsdefault_connectome_summary.json")
    preliminary_model = read_json(RESULTS / "p7_e7_preliminary_structural_model_smoke.json")
    final_model = read_json(RESULTS / "p7_e7_final_structural_hypothesis_test.json")
    final_figures = read_json(RESULTS / "p7_final_figures.json")
    manuscript_pdf = read_json(RESULTS / "p7_manuscript_pdf.json")
    qc_freeze_v02 = PROTOCOL / "PAPER7_PRE_100_SUBJECT_QC_FREEZE_v0_2.md"
    toolchain_blocked = e0.get("status") in {
        "BLOCKED_GOLD_STANDARD_TRACTOGRAPHY_REQUIREMENTS",
        "BLOCKED_HIGH_FIDELITY_TRACTOGRAPHY_REQUIREMENTS",
    }
    recovery_status = recovery.get("status", "")
    mrtrix_partial = recovery_status == "P7_WSL_MRTRIX_PARTIAL_RECOVERY_CONNECTOME_NOT_GENERATED"
    available_n = available_summary.get("n_subjects_with_fsdefault_connectome") or 0
    if final_model.get("status"):
        final_n = final_model.get("n_subjects") or 0
        status = final_model.get("status")
        streaming_subject_count = sum(
            batch.get("n_subjects_pass_or_skipped") or 0
            for batch in [
                streaming_batch,
                streaming_batch_12_3,
                streaming_batch_15_5,
                streaming_batch_20_5,
                streaming_batch_25_5,
                streaming_batch_30_5,
                streaming_batch_35_5,
                streaming_batch_40_5,
                streaming_batch_45_5,
                streaming_batch_50_5,
                streaming_batch_55_5,
                streaming_batch_60_5,
                streaming_batch_65_5,
                streaming_batch_70_5,
                streaming_batch_75_5,
                streaming_batch_80_5,
                streaming_batch_85_5,
                streaming_batch_90_5,
                streaming_batch_95_5,
            ]
        )
        if status == "FINAL_STRUCTURAL_HYPOTHESIS_SUPPORTED":
            allowed = f"Paper 7 generated 100 fs_default84 ACT/iFOD2/SIFT2 connectomes, excluded 100307 by the frozen pre-modeling QC rule, and the final {final_n}-subject primary analysis supported subject-specific structural grounding under the tested state-prediction interface."
            blockers = []
        else:
            allowed = f"Paper 7 generated 100 fs_default84 ACT/iFOD2/SIFT2 connectomes, excluded 100307 by the frozen pre-modeling QC rule, and ran the final {final_n}-subject primary structural prediction analysis. The final gates did not support subject-specific structural grounding under the tested state-prediction interface."
            blockers = [
                "No unresolved P7 structural test blocker remains; the final result is a constrained negative result, not a missing experiment.",
                "Do not claim subject-specific structural grounding, NAP structural grounding, or CWP validation from this result.",
            ]
    elif preliminary_model.get("status") == "PASS_PRELIMINARY_STRUCTURAL_MODEL_SMOKE":
        preliminary_n = preliminary_model.get("n_subjects") or 0
        status = f"P7_{available_n}_FSDEFAULT_CONNECTOMES_{preliminary_n}_SUBJECT_PRELIMINARY_MODEL_SMOKE_COMPLETE_100_SUBJECT_HYPOTHESIS_NOT_TESTED"
        streaming_subject_count = sum(
            batch.get("n_subjects_pass_or_skipped") or 0
            for batch in [
                streaming_batch,
                streaming_batch_12_3,
                streaming_batch_15_5,
                streaming_batch_20_5,
                streaming_batch_25_5,
                streaming_batch_30_5,
                streaming_batch_35_5,
                streaming_batch_40_5,
                streaming_batch_45_5,
                streaming_batch_50_5,
                streaming_batch_55_5,
                streaming_batch_60_5,
                streaming_batch_65_5,
                streaming_batch_70_5,
                streaming_batch_75_5,
                streaming_batch_80_5,
                streaming_batch_85_5,
                streaming_batch_90_5,
                streaming_batch_95_5,
            ]
        )
        allowed = f"Paper 7 now has a 10-subject final-route ACT/iFOD2/SIFT2 QC smoke, {streaming_subject_count} streaming-batch subjects, a frozen pre-100-subject QC rule excluding 100307 from the primary analysis, {available_n} available fs_default84 connectomes, and a preliminary {preliminary_n}-subject structural-model interface smoke. The preliminary smoke ran M1 no-structure, M2 group mean, M3 true subject, swapped, rewired, and anatomical distance-only comparisons after mapping fs_default84 connectomes to the P5 aparc68 state space. Its smoke gates did not support true-subject structural superiority. This remains preliminary and does not replace the 100-subject structural prediction test."
        blockers = [
            "Scale fs_default84 connectome generation under the frozen QC/cleanup policy before a final 100-subject structural prediction test.",
            "Run the final 100-subject M1/M2/M3/swap/rewire/distance comparison before any Paper 7 structural conclusion.",
        ]
    elif streaming_batch.get("status") == "PASS_STREAMING_BATCH" and available_n >= 15 and qc_freeze_v02.exists():
        status = "P7_15_SUBJECT_STREAMING_QC_FROZEN_STRUCTURAL_HYPOTHESIS_NOT_TESTED"
        allowed = "Paper 7 now has a 10-subject final-route ACT/iFOD2/SIFT2 QC smoke plus five streaming-batch subjects using nonzero ext4-generated MSMT-CSD FOD and FreeSurfer-5TT. The available fs_default84 inventory contains 15 subjects. The 100307 outlier is now handled by a frozen pre-100-subject QC rule that excludes warning-positive or sparse connectomes from the primary analysis. The streaming runner can generate additional subject connectomes without retaining every raw DWI locally. This is still an engineering/QC scale-up milestone; the 100-subject structural prediction test remains unrun."
        blockers = [
            "Run a larger streaming batch QC or proceed only under a frozen batch-size/runtime policy before the 100-subject structural prediction test.",
            "No M1/M2/M3 structural prediction comparison has been run.",
        ]
    elif streaming_batch.get("status") == "PASS_STREAMING_BATCH" and available_n >= 15:
        status = "P7_15_SUBJECT_STREAMING_QC_READY_STRUCTURAL_HYPOTHESIS_NOT_TESTED"
        allowed = "Paper 7 now has a 10-subject final-route ACT/iFOD2/SIFT2 QC smoke plus five streaming-batch subjects using nonzero ext4-generated MSMT-CSD FOD and FreeSurfer-5TT. The available fs_default84 inventory contains 15 subjects; 100307 remains the only known warning-positive/outlier case. The streaming runner can generate additional subject connectomes without retaining every raw DWI locally. This is still an engineering/QC scale-up milestone; the 100-subject structural prediction test remains unrun."
        blockers = [
            "Resolve or preregister handling for the 100307 fs_default84 outlier before 100-subject modeling.",
            "Freeze final connectome atlas, label-conversion, streamline count, subject-exclusion QC thresholds, and streaming cleanup policy before 100-subject modeling.",
            "Run a larger streaming batch QC or proceed only under a frozen batch-size/runtime policy before the 100-subject structural prediction test.",
            "No M1/M2/M3 structural prediction comparison has been run.",
        ]
    elif streaming_batch.get("status") == "PASS_STREAMING_BATCH":
        status = "P7_12_SUBJECT_STREAMING_QC_READY_STRUCTURAL_HYPOTHESIS_NOT_TESTED"
        allowed = "Paper 7 now has a 10-subject final-route ACT/iFOD2/SIFT2 QC smoke plus a 2-subject streaming-batch extension using nonzero ext4-generated MSMT-CSD FOD and FreeSurfer-5TT. The fs_default84 label-conversion QC ran for the 10-subject smoke cohort and the streaming subjects; 100307 remains the only known warning-positive/outlier case. The streaming runner can generate additional subject connectomes without retaining every raw DWI locally. This is still an engineering/QC scale-up milestone; the 100-subject structural prediction test remains unrun."
        blockers = [
            "Resolve or preregister handling for the 100307 fs_default84 outlier before 100-subject modeling.",
            "Freeze final connectome atlas, label-conversion, streamline count, subject-exclusion QC thresholds, and streaming cleanup policy before 100-subject modeling.",
            "Run a larger streaming batch QC before attempting the frozen 100-subject structural prediction test.",
            "No M1/M2/M3 structural prediction comparison has been run.",
        ]
    elif ten_subject_qc.get("status") == "PASS_10_SUBJECT_CONNECTOME_QC_SMOKE":
        status = "P7_10_SUBJECT_CONNECTOME_QC_READY_STRUCTURAL_HYPOTHESIS_NOT_TESTED"
        allowed = "Paper 7 now has a 10-subject final-route ACT/iFOD2/SIFT2 QC smoke using nonzero ext4-generated MSMT-CSD FOD and FreeSurfer-5TT. The 10-subject fs_default84 label-conversion QC also ran; 9/10 subjects cleared load-bearing tck2connectome node-assignment warnings, while 100307 remained an outlier even at 20k streamlines. This is still an engineering/QC scale-up milestone; the 100-subject structural prediction test remains unrun."
        blockers = [
            "Resolve or preregister handling for the 100307 fs_default84 outlier before 100-subject modeling.",
            "Freeze final connectome atlas, label-conversion, streamline count, and subject-exclusion QC thresholds before 100-subject modeling.",
            "No M1/M2/M3 structural prediction comparison has been run.",
        ]
    elif three_subject_smoke.get("status") == "PASS_THREE_SUBJECT_FINAL_ROUTE_SMOKE":
        status = "P7_THREE_SUBJECT_FINAL_ROUTE_SMOKE_READY_STRUCTURAL_HYPOTHESIS_NOT_TESTED"
        allowed = "Paper 7 now has a 3-subject final-route ACT/iFOD2/SIFT2 smoke for HCP 100307, 100408, and 101107 using nonzero ext4-generated MSMT-CSD FOD. This is still an engineering scale-up milestone; the 10-subject QC and 100-subject structural prediction test remain unrun."
        blockers = [
            "Freeze atlas/label-conversion QC before treating connectomes as final cohort inputs.",
            "Run 10-subject connectome QC before 100-subject frozen test.",
            "No M1/M2/M3 structural prediction comparison has been run.",
        ]
    elif final_smoke.get("status") == "PASS_SINGLE_SUBJECT_FINAL_ROUTE_SMOKE":
        status = "P7_SINGLE_SUBJECT_FINAL_ROUTE_SMOKE_READY_COHORT_NOT_TESTED"
        allowed = "Paper 7 now has a one-subject final-route ACT/iFOD2/SIFT2 smoke connectome for HCP 100307 using nonzero ext4-generated MSMT-CSD FOD. This is an engineering smoke milestone only; cohort connectomes and the structural hypothesis test remain unrun."
        blockers = [
            "Freeze atlas/label-conversion QC before treating connectomes as final cohort inputs.",
            "Download/prepare at least 3 complete HCP subjects before scaling beyond the 100307 smoke.",
            "No M1/M2/M3 structural prediction comparison has been run.",
        ]
    elif diagnostic.get("status"):
        status = diagnostic["status"]
        allowed = "Paper 7 has progressed beyond readiness: FreeSurfer-5TT high-fidelity-route intermediates were generated for HCP 100307, but ACT/iFOD2/SIFT2 connectome generation is still not complete and the structural hypothesis has not been tested."
        blockers = [
            "MSMT-CSD zero-FOD/runtime issue must be resolved before final-route tractography.",
            "One-subject connectome_sift2_smoke.csv does not exist yet.",
            "3/10/100-subject scaling must wait until the one-subject final-route smoke passes.",
        ]
    elif mrtrix_partial:
        status = "P7_WSL_MRTRIX_PARTIAL_RECOVERY_CONNECTOME_NOT_GENERATED"
        allowed = "Paper 7 has a frozen high-fidelity ACT/iFOD2/SIFT2 structural-grounding protocol. WSL user-space MRtrix3 can read/write HCP DWI and has partial one-subject MRtrix intermediates, but cohort connectomes were not generated and the structural hypothesis was not tested."
        blockers = [
            "Full ACT/SIFT2 smoke connectome generation did not complete within the interactive run window.",
            "Only 1 local HCP subject currently satisfies the complete P7 modeling-input audit.",
        ]
    else:
        status = "P7_HIGH_FIDELITY_STRUCTURAL_GROUNDING_NOT_RUN_TOOLCHAIN_BLOCKED" if toolchain_blocked else "P7_READY_FOR_HIGH_FIDELITY_CONNECTOME_EXECUTION"
        allowed = "Paper 7 has a frozen high-fidelity ACT/iFOD2/SIFT2 structural-grounding protocol and a dataset/toolchain audit. The structural hypothesis test has not been run."
        blockers = e0.get("blockers", [])
    payload = {
        "paper": "Paper 7",
        "status": status,
        "can_claim_high_fidelity_connectomes_generated": available_n >= 100,
        "can_claim_single_subject_final_route_smoke": final_smoke.get("status") == "PASS_SINGLE_SUBJECT_FINAL_ROUTE_SMOKE",
        "can_claim_structural_incremental_value": final_model.get("status") == "FINAL_STRUCTURAL_HYPOTHESIS_SUPPORTED",
        "can_claim_subject_specific_structure_matters": final_model.get("status") == "FINAL_STRUCTURAL_HYPOTHESIS_SUPPORTED",
        "can_claim_structural_mechanism_established": False,
        "allowed_current_claim": allowed,
        "blockers": blockers,
        "e0_status": e0.get("status"),
        "environment_recovery_status": recovery_status or None,
        "engineering_diagnostic_status": diagnostic.get("status") or None,
        "final_route_single_subject_smoke_status": final_smoke.get("status") or None,
        "three_subject_final_route_smoke_status": three_subject_smoke.get("status") or None,
        "ten_subject_connectome_qc_status": ten_subject_qc.get("status") or None,
        "labelconvert_connectome_qc_status": labelconvert_qc.get("status") or None,
        "labelconvert_all_load_bearing_tck2connectome_warnings_removed": labelconvert_qc.get("all_load_bearing_tck2connectome_warnings_removed"),
        "labelconvert_load_bearing_tck2connectome_warning_subjects": labelconvert_qc.get("load_bearing_tck2connectome_warning_subjects", []),
        "streaming_batch_status": streaming_batch.get("status") or None,
        "streaming_batch_subjects": streaming_batch.get("subjects", []),
        "streaming_batch_n_subjects": streaming_batch.get("n_subjects"),
        "streaming_batch_n_pass_or_skipped": streaming_batch.get("n_subjects_pass_or_skipped"),
        "streaming_batch_12_3_status": streaming_batch_12_3.get("status") or None,
        "streaming_batch_12_3_subjects": streaming_batch_12_3.get("subjects", []),
        "streaming_batch_12_3_n_subjects": streaming_batch_12_3.get("n_subjects"),
        "streaming_batch_12_3_n_pass_or_skipped": streaming_batch_12_3.get("n_subjects_pass_or_skipped"),
        "streaming_batch_15_5_status": streaming_batch_15_5.get("status") or None,
        "streaming_batch_15_5_subjects": streaming_batch_15_5.get("subjects", []),
        "streaming_batch_15_5_n_subjects": streaming_batch_15_5.get("n_subjects"),
        "streaming_batch_15_5_n_pass_or_skipped": streaming_batch_15_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_20_5_status": streaming_batch_20_5.get("status") or None,
        "streaming_batch_20_5_subjects": streaming_batch_20_5.get("subjects", []),
        "streaming_batch_20_5_n_subjects": streaming_batch_20_5.get("n_subjects"),
        "streaming_batch_20_5_n_pass_or_skipped": streaming_batch_20_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_25_5_status": streaming_batch_25_5.get("status") or None,
        "streaming_batch_25_5_subjects": streaming_batch_25_5.get("subjects", []),
        "streaming_batch_25_5_n_subjects": streaming_batch_25_5.get("n_subjects"),
        "streaming_batch_25_5_n_pass_or_skipped": streaming_batch_25_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_30_5_status": streaming_batch_30_5.get("status") or None,
        "streaming_batch_30_5_subjects": streaming_batch_30_5.get("subjects", []),
        "streaming_batch_30_5_n_subjects": streaming_batch_30_5.get("n_subjects"),
        "streaming_batch_30_5_n_pass_or_skipped": streaming_batch_30_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_35_5_status": streaming_batch_35_5.get("status") or None,
        "streaming_batch_35_5_subjects": streaming_batch_35_5.get("subjects", []),
        "streaming_batch_35_5_n_subjects": streaming_batch_35_5.get("n_subjects"),
        "streaming_batch_35_5_n_pass_or_skipped": streaming_batch_35_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_40_5_status": streaming_batch_40_5.get("status") or None,
        "streaming_batch_40_5_subjects": streaming_batch_40_5.get("subjects", []),
        "streaming_batch_40_5_n_subjects": streaming_batch_40_5.get("n_subjects"),
        "streaming_batch_40_5_n_pass_or_skipped": streaming_batch_40_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_45_5_status": streaming_batch_45_5.get("status") or None,
        "streaming_batch_45_5_subjects": streaming_batch_45_5.get("subjects", []),
        "streaming_batch_45_5_n_subjects": streaming_batch_45_5.get("n_subjects"),
        "streaming_batch_45_5_n_pass_or_skipped": streaming_batch_45_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_50_5_status": streaming_batch_50_5.get("status") or None,
        "streaming_batch_50_5_subjects": streaming_batch_50_5.get("subjects", []),
        "streaming_batch_50_5_n_subjects": streaming_batch_50_5.get("n_subjects"),
        "streaming_batch_50_5_n_pass_or_skipped": streaming_batch_50_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_55_5_status": streaming_batch_55_5.get("status") or None,
        "streaming_batch_55_5_subjects": streaming_batch_55_5.get("subjects", []),
        "streaming_batch_55_5_n_subjects": streaming_batch_55_5.get("n_subjects"),
        "streaming_batch_55_5_n_pass_or_skipped": streaming_batch_55_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_60_5_status": streaming_batch_60_5.get("status") or None,
        "streaming_batch_60_5_subjects": streaming_batch_60_5.get("subjects", []),
        "streaming_batch_60_5_n_subjects": streaming_batch_60_5.get("n_subjects"),
        "streaming_batch_60_5_n_pass_or_skipped": streaming_batch_60_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_65_5_status": streaming_batch_65_5.get("status") or None,
        "streaming_batch_65_5_subjects": streaming_batch_65_5.get("subjects", []),
        "streaming_batch_65_5_n_subjects": streaming_batch_65_5.get("n_subjects"),
        "streaming_batch_65_5_n_pass_or_skipped": streaming_batch_65_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_70_5_status": streaming_batch_70_5.get("status") or None,
        "streaming_batch_70_5_subjects": streaming_batch_70_5.get("subjects", []),
        "streaming_batch_70_5_n_subjects": streaming_batch_70_5.get("n_subjects"),
        "streaming_batch_70_5_n_pass_or_skipped": streaming_batch_70_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_75_5_status": streaming_batch_75_5.get("status") or None,
        "streaming_batch_75_5_subjects": streaming_batch_75_5.get("subjects", []),
        "streaming_batch_75_5_n_subjects": streaming_batch_75_5.get("n_subjects"),
        "streaming_batch_75_5_n_pass_or_skipped": streaming_batch_75_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_80_5_status": streaming_batch_80_5.get("status") or None,
        "streaming_batch_80_5_subjects": streaming_batch_80_5.get("subjects", []),
        "streaming_batch_80_5_n_subjects": streaming_batch_80_5.get("n_subjects"),
        "streaming_batch_80_5_n_pass_or_skipped": streaming_batch_80_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_85_5_status": streaming_batch_85_5.get("status") or None,
        "streaming_batch_85_5_subjects": streaming_batch_85_5.get("subjects", []),
        "streaming_batch_85_5_n_subjects": streaming_batch_85_5.get("n_subjects"),
        "streaming_batch_85_5_n_pass_or_skipped": streaming_batch_85_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_90_5_status": streaming_batch_90_5.get("status") or None,
        "streaming_batch_90_5_subjects": streaming_batch_90_5.get("subjects", []),
        "streaming_batch_90_5_n_subjects": streaming_batch_90_5.get("n_subjects"),
        "streaming_batch_90_5_n_pass_or_skipped": streaming_batch_90_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_95_5_status": streaming_batch_95_5.get("status") or None,
        "streaming_batch_95_5_subjects": streaming_batch_95_5.get("subjects", []),
        "streaming_batch_95_5_n_subjects": streaming_batch_95_5.get("n_subjects"),
        "streaming_batch_95_5_n_pass_or_skipped": streaming_batch_95_5.get("n_subjects_pass_or_skipped"),
        "streaming_batch_cleanup_large_intermediates": streaming_batch.get("cleanup_large_intermediates"),
        "streaming_batch_allowed_claim": streaming_batch.get("allowed_claim"),
        "streaming_cleanup_audit_status": streaming_cleanup.get("status") or None,
        "streaming_cleanup_subjects": streaming_cleanup.get("subjects", []),
        "available_fsdefault_connectome_summary_status": available_summary.get("status") or None,
        "available_fsdefault_connectome_n_subjects": available_summary.get("n_subjects_with_fsdefault_connectome"),
        "available_fsdefault_connectome_nonzero_edges_min": available_summary.get("nonzero_edges_min"),
        "available_fsdefault_connectome_nonzero_edges_mean": available_summary.get("nonzero_edges_mean"),
        "available_fsdefault_connectome_nonzero_edges_max": available_summary.get("nonzero_edges_max"),
        "pre_100_subject_qc_freeze_v0_2_exists": qc_freeze_v02.exists(),
        "pre_100_subject_qc_freeze_v0_2_path": str(qc_freeze_v02) if qc_freeze_v02.exists() else None,
        "preliminary_structural_model_smoke_status": preliminary_model.get("status") or None,
        "preliminary_structural_model_n_subjects": preliminary_model.get("n_subjects"),
        "preliminary_structural_model_smoke_gates": preliminary_model.get("smoke_gates"),
        "preliminary_structural_model_summary": preliminary_model.get("summary"),
        "final_structural_hypothesis_status": final_model.get("status") or None,
        "final_structural_hypothesis_n_subjects": final_model.get("n_subjects"),
        "final_structural_hypothesis_n_available_connectomes_before_qc_exclusion": final_model.get("n_available_connectomes_before_qc_exclusion"),
        "final_structural_hypothesis_gates": final_model.get("final_gates"),
        "final_structural_hypothesis_summary": final_model.get("summary"),
        "final_figures_status": final_figures.get("status") or None,
        "final_figures": final_figures.get("figures", []),
        "manuscript_pdf_status": manuscript_pdf.get("status") or None,
        "manuscript_pdf": manuscript_pdf.get("pdf"),
        "streamline_sensitivity_100307_status": sensitivity_100307.get("status") or None,
        "streamline_sensitivity_100307_load_bearing_warning": sensitivity_100307.get("load_bearing_tck2connectome_warning"),
        "streamline_sensitivity_100307_nonzero_edges": sensitivity_100307.get("connectome_qc", {}).get("nonzero_edges"),
        "three_subject_final_route_subjects": three_subject_smoke.get("subjects", []),
        "ten_subject_connectome_qc_subjects": ten_subject_qc.get("subjects", []),
        "final_route_single_subject_connectome": final_smoke.get("files", {}).get("connectome", {}),
        "final_route_single_subject_qc_warning": final_smoke.get("qc_warning"),
        "forbidden_claims": [
            "Subject-specific structural connectivity constrains brain-state dynamics."
            if final_model.get("status") != "FINAL_STRUCTURAL_HYPOTHESIS_SUPPORTED"
            else "Structural mechanism is fully established.",
            "Structural mechanism is established.",
            "NAP is structurally grounded.",
            "CWP is validated.",
        ],
    }
    (RESULTS / "p7_e8_claim_audit.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
