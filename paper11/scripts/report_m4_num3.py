"""Report saved controlled evidence; never evaluates experimental data."""
import csv
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import run_m4_num3 as run


def main():
    run.assert_frozen()
    output = run.OUTPUT
    qc = run.load(output/'qc_report.json')
    gate = run.load(output/'gate_result.json')
    records = []
    for fixture in qc['fixtures']:
        for estimate in fixture['evaluations']:
            for bin_index in range(len(estimate['bin_sd'])):
                records.append({'fixture': fixture['fixture'], 'method': estimate['method'],
                    'particles': estimate['particles'], 'bin': bin_index,
                    'bin_discrepancy': estimate['bin_discrepancy'][bin_index],
                    'trial_discrepancy': estimate['trial_discrepancy'],
                    'replicate_sd': estimate['bin_sd'][bin_index],
                    'mean_minus_oracle': estimate['bin_mean_minus_oracle'][bin_index],
                    'mean_95_halfwidth': estimate['mean_error_95_halfwidth'][bin_index],
                    'prefix_jensen_gap': estimate['prefix_jensen_gap_nats_unit'][bin_index],
                    'oracle_sensitivity': fixture['oracle']['sensitivity_nats_unit_bin'][bin_index],
                    'minimum_ess_fraction': min(d['minimum_ess_fraction'] for d in estimate['diagnostics']),
                    'wall_seconds': estimate['wall_seconds']})
    fields = list(records[0]) if records else ['fixture', 'method', 'particles']
    with (output/'diagnostics.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout='constrained')
    for fixture in qc['fixtures']:
        estimates = [v for v in fixture['evaluations'] if v['method'] == 'rqmc']
        if not estimates:
            continue
        axes[0].plot([v['particles'] for v in estimates], [v['maximum_bin_discrepancy'] for v in estimates], 'o-', label=fixture['fixture'])
        axes[1].plot([v['particles'] for v in estimates], [max(v['bin_sd']) for v in estimates], 'o-', label=fixture['fixture'])
    axes[0].axhline(.001, color='#555555', linestyle='--', label='Frozen threshold')
    for axis in axes:
        axis.set_xscale('log', base=2)
        axis.set_yscale('log')
        axis.set_xlabel('Particles / independent scramble')
        axis.legend(fontsize=8)
        axis.grid(alpha=.2)
    axes[0].set_ylabel('Worst-bin discrepancy (nats/unit-bin)')
    axes[1].set_ylabel('Largest replicate SD (nats/unit-bin)')
    fig.suptitle('NUM3 controlled fixtures only; gate '+gate['gate'])
    fig.savefig(output/'numerical_feasibility.png', dpi=150)
    fig.savefig(output/'numerical_feasibility.pdf')
    plt.close(fig)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(run.PAPER/'tests'), '-v'], capture_output=True, text=True)
    run.assert_frozen()
    (output/'regression-tests.txt').write_text(tests.stdout+tests.stderr, encoding='utf-8')
    run.write(output/'output_validation.json', {'full_regression_exit_code': tests.returncode,
        'registered_hashes_match': run.load(run.LOCK)['sha256'] == run.identity(),
        'report_source_sha256': run.digest(Path(__file__)),
        'fixture_qc_sha256': run.digest(output/'qc_report.json'),
        'gate_sha256': run.digest(output/'gate_result.json'),
        'finished_at_utc': run.now(), 'real_neural_data_access': False})
    lines = ['# Complete NUM3 Numerical Limitations', '',
             'All entries concern controlled sequences, not biological evidence.',
             'Registered UTC: '+run.load(run.LOCK)['registered_at_utc']+'.',
             'Gate '+gate['gate']+'; '+('; '.join(gate['errors']) or 'controlled feasibility only')+'.', '',
             '## Error Sources',
             '- Monte Carlo variability: independent16-replicate SD, worst errors and numerical95% mean halfwidth reported per bin/budget.',
             '- Reference uncertainty: independent GH and GL order shifts, cross-method difference and finite-domain tail sensitivity reported separately. No finite-particle reference used as truth.',
             '- Log-score bias: mean-minus-oracle and prefix Jensen gap are recorded separately from SD. A confidence interval containing zero does not prove no bias. The Jensen gap is a diagnostic, not exact expected bias; bin evidence ratios are not unbiased likelihood estimators.',
             '- Integration error: independent-method/order consistency supports only empirical discretization stability; no rigorous quadrature remainder bound. Conservative tail bound controls omitted prior-path probability with Poisson likelihood<=1, not discretization. Log sensitivity uses estimated prefix evidence, not a certified evidence lower bound.',
             '- High ESS: instrumented for concentration, never accepted as likelihood accuracy proof.', '',
             '## Registered Results']
    for fixture in qc['fixtures']:
        lines += ['### '+fixture['fixture'], 'Independent oracle: '+fixture['oracle']['gate']+'.']
        if 'sensitivity_nats_unit_bin' in fixture['oracle']:
            lines.append('Maximum reference sensitivity: '+str(max(fixture['oracle']['sensitivity_nats_unit_bin']))+'.')
        for value in fixture['evaluations']:
            lines.append(f"- {value['method']} N={value['particles']}: worst-bin bound {value['maximum_bin_discrepancy']:.12g}; trial bound {value['trial_discrepancy']:.12g}; max SD {max(value['bin_sd']):.12g}; min ESS/N {min(d['minimum_ess_fraction'] for d in value['diagnostics']):.8g}.")
    lines += ['', '## Boundaries',
              'Primary scientific metric remains trial-normalized joint predictive likelihood. The controlled procedure additionally requires per-bin precision; it does not redefine the frozen scientific metric.',
              'Threshold0.001 unchanged. No seed/replica exclusion, target-density approximation, best-replica selection, post-failure budget increase or final holdout access.',
              'Lexicographic RQMC particle ordering is not the Hilbert SQMC algorithm; published SQMC convergence rates are not asserted for this implementation.',
              'Worst replica plus1.96 SD is an empirical frozen acceptance statistic, not a calibrated simultaneous95% confidence or prediction bound.',
              'Three-bin low-dimensional oracles cannot establish accuracy on longer real trials, other fitted configurations or the full cohort.',
              'A failed conservative verification procedure means accuracy not established under the registered procedure, not proof that0.001 is impossible for every numerical method.',
              'On mandatory FAIL, numerical remediation stops; M4 remains INCONCLUSIVE. Prior failures remain immutable.', '',
              '## Five Outstanding Scientific Warnings',
              '- R05: full Discrete/Continuous/Hybrid competition incomplete.',
              '- R06: complete selected-model freeze/locked holdout evidence incomplete; isolation retained.',
              '- R07: subject-level statistics and required nulls not executed.',
              '- R08: subject transfer and independent external compatibility/test not executed.',
              '- R13: full-paper one-command reproduction not established. Controlled STOP reproduction is narrower.',
              'None cleared administratively using improved variance, unit tests or upload.', '',
              'Full regression exit code: '+str(tests.returncode)+'. No NAP/CWP or preferred-regime validation.']
    (output/'NUMERICAL_LIMITATIONS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({'full_regression_exit_code': tests.returncode, 'diagnostic_rows': len(records), 'gate': gate['gate']}))
    return tests.returncode


if __name__ == '__main__':
    sys.exit(main())
