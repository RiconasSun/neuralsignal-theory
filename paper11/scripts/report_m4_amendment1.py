"""Summarize actual amended numerical diagnostics; no neural data access."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import run_m4_amendment1 as run


def main():
    gate = run.load(run.RESULTS / 'gate_result.json')
    lock = run.load(run.LOCK)
    preserved = all(run.digest(run.PAPER / name) == expected for name, expected in lock['sha256'].items())
    if not preserved:
        raise ValueError('Registered original/source identities changed')
    rows = []
    for path in sorted((run.RESULTS / 'accuracy').rglob('*.json')):
        diagnostic = run.load(path)
        if 'comparisons' not in diagnostic:
            continue
        for comparison in diagnostic['comparisons']:
            ess = [row['minimum_ess_fraction'] for row in comparison['diagnostics']]
            rows.append({'candidate': path.stem, 'particles': comparison['particles'],
                         'diagnostic_gate': diagnostic['gate'], 'discrepancy_nats_unit_bin': comparison['conservative_discrepancy'],
                         'reference_uncertainty': diagnostic['reference_uncertainty'],
                         'maximum_abs_mean_reference_shift': float(np.max(np.abs(comparison['mean_minus_reference_by_trial']))),
                         'maximum_single_run_sd': max(comparison['single_run_sd_by_trial']),
                         'minimum_ess_fraction': min(ess), 'median_minimum_ess_fraction': float(np.median(ess)),
                         'maximum_particle_weight': max(row['maximum_particle_weight'] for row in comparison['diagnostics']),
                         'overflow_rates': sum(row['overflow_rates'] for row in comparison['diagnostics']),
                         'resampling_boundary_roundoff': sum(row['roundoff_resampling_boundary_count'] for row in comparison['diagnostics']),
                         'wall_seconds': comparison['wall_seconds']})
    if rows:
        with (run.RESULTS / 'numerical_diagnostics.csv').open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout='constrained')
        for candidate in sorted({row['candidate'] for row in rows}):
            subset = [row for row in rows if row['candidate'] == candidate]
            axes[0].plot([row['particles'] for row in subset], [row['discrepancy_nats_unit_bin'] for row in subset], 'o-', label=candidate)
            axes[1].plot([row['particles'] for row in subset], [row['median_minimum_ess_fraction'] for row in subset], 'o-', label=candidate)
        axes[0].axhline(.001, color='#b94163', linestyle='--', label='Frozen0.001 threshold')
        axes[0].set(xlabel='Particles', ylabel='Discrepancy (nats/unit-bin)', yscale='log', title='Single-run numerical certification')
        axes[1].set(xlabel='Particles', ylabel='Median trial minimum ESS/N', title='Bootstrap proposal weight concentration')
        axes[0].legend(fontsize=7)
        fig.suptitle('M4-NUM-1 development diagnostics; no preferred neural regime', fontsize=11)
        fig.savefig(run.RESULTS / 'numerical_diagnostics.png', dpi=160)
        fig.savefig(run.RESULTS / 'numerical_diagnostics.pdf')
        plt.close(fig)
    result = {'scientific_gate': gate['gate'], 'original_failure_preserved': preserved,
              'numerical_rows': len(rows), 'input_diagnostics_sha256': {
                  path.relative_to(run.PAPER).as_posix(): run.digest(path) for path in sorted((run.RESULTS / 'accuracy').rglob('*.json'))},
              'source_sha256': run.digest(Path(__file__)), 'final_holdout_access': False,
              'bias': 'Signed mean-reference shifts and budget drift are sensitivity diagnostics, not known absolute bias.',
              'variance': 'Eight independent single-run replicas; SD not divided by sqrt(8) for candidate accuracy.',
              'proposal': 'ESS/max weight quantify prior-proposal concentration; no observation-aware correction-free scoring.',
              'reference': 'Two budgets, eight replicas each; finite-reference uncertainty included, absolute accuracy not proved.',
              'stability': 'Log-sum-exp weights, explicit nonfinite/degenerate checks; no rate/likelihood clipping.',
              'complete_model_competition': False if gate['gate'] == 'FAIL' else True}
    run.write(run.RESULTS / 'numerical_audit.json', result)
    print(json.dumps({key: value for key, value in result.items() if key != 'input_diagnostics_sha256'}))


if __name__ == '__main__':
    main()
