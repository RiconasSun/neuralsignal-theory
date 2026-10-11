"""Descriptive real training-only QC; no model or heldout figures."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import run_m1 as m1


def main():
    results = m1.PAPER / 'results' / 'M2'
    qc = json.loads((results / 'qc_report.json').read_text())
    manifest = json.loads((m1.PAPER / 'data_manifest' / 'M2' / 'features.json').read_text())
    subjects = sorted({row['session_key'].split('/')[0] for row in manifest['files']})
    units = [sum(row['units'] for row in manifest['files'] if row['session_key'].startswith(subject + '/')) for subject in subjects]
    sessions = [sum(row['session_key'].startswith(subject + '/') for row in manifest['files']) for subject in subjects]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout='constrained')
    axes[0].bar(subjects, units, color='#24766a')
    axes[0].set(ylabel='Session-local units (not persistent neurons)', title='M1-selected training cohort')
    axes[0].tick_params(axis='x', rotation=45)
    for index, (unit, session) in enumerate(zip(units, sessions)):
        axes[0].text(index, unit + 2, f'{session} session' + ('' if session == 1 else 's'), ha='center', fontsize=8)
    axes[1].bar(['Zero counts', 'Nonzero counts'], [qc['zero_bin_fraction'], 1 - qc['zero_bin_fraction']], color=['#596471', '#b94163'])
    axes[1].set(ylim=(0, 1), ylabel='Fraction of conditional training unit-bins', title='100 ms training counts')
    fig.suptitle('P11 descriptive QC: exact observation coverage unresolved', fontsize=12)
    output = results / 'figures'
    output.mkdir(exist_ok=True)
    fig.savefig(output / 'training_qc.png', dpi=160)
    fig.savefig(output / 'training_qc.pdf')
    plt.close(fig)
    m1.write_json(output / 'provenance.json', {
        'script_sha256': m1.digest(Path(__file__)), 'matplotlib': matplotlib.__version__,
        'inputs_sha256': {str(path.relative_to(m1.PAPER)): m1.digest(path) for path in (results / 'qc_report.json', m1.PAPER / 'data_manifest' / 'M2' / 'features.json')},
        'claim_scope': 'conditional training cohort/counts only; no scientific model preference', 'holdout_access': False})


if __name__ == '__main__':
    main()
