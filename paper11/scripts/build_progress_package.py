"""Generate real validation/QC tables without asserting final paper completion."""
import csv
import json
from collections import Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import run_m1 as m1


def main():
    paper = m1.PAPER
    output = paper / 'results/progress'
    output.mkdir(parents=True, exist_ok=True)
    sessions = [m1.m0.load(path) for path in sorted((paper / 'results/M3/sessions').glob('*.json'))]
    rows = [{field: row[field] for field in ('family', 'alpha', 'parameters', 'validation_mean', 'validation_se')}
            | {'session': session['session_key'], 'subject': session['subject'], 'converged': row['convergence']['success'], 'iterations': row['convergence']['iterations']}
            for session in sessions for row in session['candidates']]
    with (output / 'baseline_validation_all.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    selections = Counter(session['selected']['family'] for session in sessions)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout='constrained')
    families = ['stationary', 'history', 'task', 'timing', 'drift', 'combined']
    colors = ['#596471', '#24766a', '#3b74a0', '#b94163', '#92712c', '#766795']
    axes[0].bar(families, [selections[family] for family in families], color=colors)
    axes[0].set(ylabel='Sessions selected by validation one-SE rule', title='Baseline selection (not final test)')
    axes[0].tick_params(axis='x', rotation=40)
    convergence = [row['iterations'] for row in rows]
    axes[1].hist(convergence, bins=20, color='#3b74a0', edgecolor='white')
    axes[1].set(xlabel='Optimizer iterations', ylabel='Baseline candidates', title='All 483 candidates retained')
    fig.suptitle('P11 M3: train-fitted, validation-selected baselines', fontsize=12)
    fig.savefig(output / 'baseline_validation_qc.png', dpi=160)
    fig.savefig(output / 'baseline_validation_qc.pdf')
    plt.close(fig)
    gates = {f'M{index}': m1.m0.load(paper / f'results/M{index}/gate_result.json')['gate'] if (paper / f'results/M{index}/gate_result.json').exists() else 'NOT_COMPLETED' for index in range(8)}
    m1.write_json(output / 'package_status.json', {'gates': gates, 'baseline_candidates': len(rows), 'baseline_selection_sessions': dict(selections),
                 'complete_manuscript': False, 'biorxiv_ready': False, 'final_holdout_evaluated': False,
                 'inputs_sha256': {str(path.relative_to(paper)): m1.digest(path) for path in sorted((paper / 'results/M3/sessions').glob('*.json'))},
                 'generated_at_utc': m1.now(), 'script_sha256': m1.digest(Path(__file__))})


if __name__ == '__main__':
    main()
