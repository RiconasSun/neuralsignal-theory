"""Saved-summary-only tables and publication figures; no scientific runners."""
import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

from freeze import HERE, ROOT, load, sha

REPORT = 'paper11_v2/results/R2_development_report/report/'
COLORS = {'baseline': '#34454A', 'discrete': '#267C9A', 'continuous': '#C58420', 'hybrid': '#9D4969'}
LABELS = {'baseline': 'Strongest baseline', 'discrete': 'Discrete HMM',
          'continuous': 'Continuous recurrent', 'hybrid': 'Hybrid switching AR'}


class Saved:
    def __init__(self):
        self.record = load(HERE / 'evidence_freeze.json')
        for key in ('input_sha256', 'source_sha256'):
            for path, digest in self.record[key].items():
                if sha(ROOT / path) != digest:
                    raise RuntimeError('Frozen input changed: ' + path)

    def path(self, name):
        if name not in self.record['input_sha256']:
            raise ValueError('Not an allowlisted saved summary: ' + name)
        return ROOT / name

    def json(self, name):
        return load(self.path(name))

    def csv(self, name):
        with self.path(name).open(encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                       '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                      ['| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows])


def config_key(row):
    return (row['family'], float(row['ridge']), int(row.get('size') or 0), int(row.get('lags') or 0))


def config_label(row):
    base = row['family']
    if row.get('size'):
        base += (' d=' if base == 'continuous' else ' K=') + str(row['size'])
    if int(row.get('lags') or 0):
        base += ', L=' + str(row['lags'])
    return base + ', ridge=' + str(row['ridge'])


def validate(saved):
    grid = saved.csv(REPORT + 'all57configurations.csv')
    stats = saved.json('paper11_v2/results/R2/subject_statistics.json')
    coverage = saved.csv('paper11_v2/results/R2_report/subject_session_coverage.csv')
    gate = saved.json('paper11_v2/results/R2/gate_result.json')
    patients = sorted(stats['means']['baseline']['patient_means'])
    assert len(grid) == 57 and len(set(config_key(r) for r in grid)) == 57
    assert len(patients) == 9 and len(coverage) == 23
    assert sum(int(r['units']) for r in coverage) == 592
    assert sum(int(r['train_trials']) for r in coverage) == 622
    assert sum(int(r['validation_trials']) for r in coverage) == 201
    assert gate['gate_verdict'] == 'FAIL' and gate['scientific_verdict'] == 'DATA_INSUFFICIENT'
    assert gate['R3'] == 'NOT_EXECUTED' and gate['final_holdout_locked'] and not gate['external_spikes_accessed']
    for contrast in stats['comparisons']:
        assert contrast['subject_count'] == 9 and set(contrast['patient_differences']) == set(patients)
        assert contrast['replicates'] == 10000 and contrast['sign_flip']['enumerations'] == 512
        diffs = []
        for p in patients:
            delta = stats['means'][contrast['left']]['patient_means'][p] - stats['means'][contrast['right']]['patient_means'][p]
            assert abs(delta - contrast['patient_differences'][p]) < 2e-15
            diffs.append(delta)
        assert abs(sum(diffs) / 9 - contrast['mean']) < 2e-15
    return grid, stats, coverage, gate, patients


def export_tables(saved, dest):
    grid, stats, coverage, gate, patients = validate(saved)
    selection = saved.json('paper11_v2/results/R2/model_selection_manifest.json')
    baseline = saved.json('paper11_v2/results/R2/baseline_selection.json')
    configs = {'baseline': selection['families']['baseline']['selected_config']}
    configs.update({f: selection['families'][f]['selected_config'] for f in ('discrete', 'continuous', 'hybrid')})
    raw = {f: max([r for r in grid if r['family'] == (configs['baseline']['family'] if f == 'baseline' else f)],
                  key=lambda r: float(r['patient_weighted_dev_mean'])) for f in configs}
    selected = []
    for family, config in configs.items():
        matching = [r for r in grid if config_key(r) == config_key(config)]
        assert len(matching) == 1
        row = matching[0]
        mean = stats['means'][family]['mean']
        assert abs(mean - float(row['patient_weighted_dev_mean'])) < 2e-15
        selected.append({'family': family, 'config': config, 'mean': mean,
                         'total_parameters': float(row['total_nominal_parameters']),
                         'selection_role': 'raw strongest baseline reference' if family == 'baseline' else 'frozen family one-SE'})
    dest.mkdir(parents=True, exist_ok=True)
    for name in ('all57configurations.csv', 'selected_patient_scores.csv', 'six_subject_contrasts.csv',
                 'patient_conditional_CIs.csv', 'session_conditional_CIs.csv', 'optimizer_diagnostics.csv'):
        shutil.copyfile(saved.path(REPORT + name), dest / name)
    shutil.copyfile(saved.path('paper11_v2/results/R2_report/subject_session_coverage.csv'), dest / 'session_coverage.csv')
    rows = []
    for p in patients:
        row = {'patient': p}
        for c in stats['comparisons']:
            row[c['left'] + '_minus_' + c['right']] = c['patient_differences'][p]
        rows.append(row)
    with (dest / 'all_patient_paired_effects.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    diag = saved.csv(REPORT + 'optimizer_diagnostics.csv')
    assert len(diag) == 3887
    optimizer = {'records': len(diag), 'one_iteration_records': sum(r['iterations'] == '1' for r in diag),
                 'termination_messages': dict(Counter(r['message'] for r in diag)),
                 'gradient_max': max(float(r['gradient_norm']) for r in diag if r['gradient_norm']),
                 'first_unit_rank_only': True, 'global_optima_verified': False}
    summary = {'selected': selected, 'raw_maxima': raw,
               'baseline_one_SE': baseline['one_SE_baseline']['selected_config'],
               'shared_offset': selection['offset_config'],
               'cross_family_one_SE': selection['global_family_selection']['selected_config'],
               'gate': gate, 'optimizer': optimizer, 'patients': patients}
    # Manifest key names remain source-owned; discover the recorded cross-family block.
    for value in selection.values():
        if isinstance(value, dict) and value.get('selected_config', {}).get('family') == 'discrete' and len(value.get('audit', [])) == 36:
            summary['cross_family_one_SE'] = value['selected_config']
    write_json(dest / 'summary.json', summary)
    return grid, stats, coverage, gate, patients, selected, raw, rows, optimizer


def figure_save(fig, folder, name, inputs, data, saved, caption):
    fig.savefig(folder / (name + '.png'), dpi=300, facecolor='white')
    fig.savefig(folder / (name + '.pdf'), metadata={'CreationDate': None, 'ModDate': None}, facecolor='white')
    plt.close(fig)
    write_json(folder / (name + '.json'), {'input_sha256': {p: saved.record['input_sha256'][p] for p in inputs},
          'render_code_sha256': sha(Path(__file__)), 'values': data, 'caption': caption,
          'interpretation': 'Saved descriptive evidence or protocol schematic; no new fitting/inference'})


def frame(ax, title):
    ax.set_title(title, loc='left', fontsize=11, fontweight='bold', pad=10)
    ax.spines[['top', 'right']].set_visible(False)


def draw_figures(saved, output, values):
    grid, stats, coverage, gate, patients, selected, raw, effects, optimizer = values
    folder = output / 'figures'; folder.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.labelsize': 9,
                         'pdf.fonttype': 42, 'savefig.bbox': 'tight', 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.unicode_minus': False})
    sums = {p: {k: sum(int(r[k]) for r in coverage if r['subject'] == p)
                 for k in ('units', 'train_trials', 'validation_trials')} for p in patients}
    fig = plt.figure(figsize=(7.4, 5.0), layout='constrained')
    axes = fig.subplot_mosaic([['workflow', 'workflow'], ['units', 'trials']], height_ratios=[.9, 2])
    a = axes['workflow']; a.axis('off')
    boxes = [(.02, 'Exposed development\n9 patients / 23 sessions'), (.36, '57 configurations\n3,887 completed fits'), (.70, 'Exploratory reporting\nExternal test NOT RUN')]
    for x, text in boxes:
        a.add_patch(FancyBboxPatch((x, .3), .27, .52, boxstyle='round,pad=0.012,rounding_size=0.01',
                   facecolor='#F3F5F5', edgecolor='#73858A', transform=a.transAxes))
        a.text(x + .135, .56, text, ha='center', va='center', transform=a.transAxes)
    for x in (.30, .64):
        a.annotate('', xy=(x+.05, .56), xytext=(x, .56), xycoords='axes fraction', arrowprops={'arrowstyle': '->'})
    x = np.arange(9)
    axes['units'].bar(x, [sums[p]['units'] for p in patients], color='#267C9A')
    axes['units'].set_xticks(x, [p[-2:] for p in patients]); axes['units'].set_ylabel('Session-local units (not unique neurons)')
    frame(axes['units'], 'A  Anatomical coverage')
    axes['trials'].bar(x, [sums[p]['train_trials'] for p in patients], label='Train', color='#007F73')
    axes['trials'].bar(x, [sums[p]['validation_trials'] for p in patients],
                      bottom=[sums[p]['train_trials'] for p in patients], label='Development', color='#C58420')
    axes['trials'].set_xticks(x, [p[-2:] for p in patients]); axes['trials'].set_ylabel('Whole trials'); axes['trials'].legend(frameon=False)
    frame(axes['trials'], 'B  Frozen trial coverage')
    for a in (axes['units'], axes['trials']): a.set_xlabel('Patient ID')
    figure_save(fig, folder, 'F1_design_coverage', ['paper11_v2/results/R2_report/subject_session_coverage.csv', 'paper11_v2/results/R2/QC.json'], sums, saved,
                'Development only: 592 session-local units, 622 train and 201 development trials. Patients, not units or sessions, are independent.')

    fig, axes = plt.subplots(3, 1, figsize=(7.4, 5.0), layout='constrained')
    descriptions = [('Discrete HMM', ['Past counts\nforward filter', 'Categorical state\nK = 2 or 4', 'Common offset +\nstate bias'], 'Exact state-path marginal; no sampled continuous latent', COLORS['discrete']),
                    ('Continuous recurrent', ['Past counts +\nknown context', 'Deterministic h(t)\nd = 1, 2 or 4', 'Common offset +\nC h(t)'], 'Observed-history conditional likelihood; NOT a PLDS', COLORS['continuous']),
                    ('Hybrid switching AR', ['Past counts\nforward filter', 'Categorical state +\nown history L=1,5', 'Common offset +\nstate/history terms'], 'Exact conditional state-path marginal; NOT a stochastic SLDS', COLORS['hybrid'])]
    for ax, (title, texts, footer, color) in zip(axes, descriptions):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        ax.text(0, .93, title, fontsize=11, fontweight='bold', color=color)
        for j, text in enumerate(texts):
            pos = .025 + j * .33
            ax.add_patch(FancyBboxPatch((pos, .26), .26, .44, boxstyle='round,pad=.012,rounding_size=.01', edgecolor=color, facecolor='#F8F9F9'))
            ax.text(pos + .13, .48, text, ha='center', va='center', fontsize=9)
            if j < 2: ax.annotate('', xy=(pos+.325, .48), xytext=(pos+.27, .48), arrowprops={'arrowstyle': '->', 'color': color})
        ax.text(.025, .07, footer, fontsize=9)
    figure_save(fig, folder, 'F2_architectures', ['paper11_v2/scripts/predictive_models.py', 'paper11_v2/scripts/predictive_models_code1.py', 'paper11_v2/protocol/protocol.json'],
                {'models': [d[0:3] for d in descriptions], 'reset': 'every trial', 'observation': 'Poisson counts'}, saved,
                'Model schematics reflect the frozen code. All predictions use only past counts and permitted current context; every trial resets states/history.')

    r1 = saved.json('paper11_v2/results/R1_code1/QC.json')['oracle']
    r2 = saved.json('paper11_v2/results/R2/numerical_oracle.json')
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.5), layout='constrained')
    err = [r1['max_state_score_error'], r1['max_recurrent_score_error'], r2['score_error_nats_unit_bin']]
    axes[0].bar(['R1 state', 'R1 recurrent', 'R2 kernel'], err, color=['#267C9A', '#C58420', '#007F73'])
    axes[0].set_yscale('log'); axes[0].axhline(1e-10, ls='--', color='#A8464B')
    axes[0].set_ylim(1e-16, 1e-9); axes[0].set_ylabel('Recorded normalized score discrepancy')
    frame(axes[0], 'A  Tractable oracle agreement')
    text = saved.path('paper11/results/M4_amendment3/NUMERICAL_LIMITATIONS.md').read_text(encoding='utf-8')
    import re
    bounds = [float(re.search(r'rqmc N=' + str(n) + r': worst-bin bound ([0-9.e-]+)', text)[1]) for n in (8192, 32768, 131072)]
    axes[1].plot([8192, 32768, 131072], bounds, marker='o', color='#9D4969')
    axes[1].set_xscale('log'); axes[1].set_yscale('log'); axes[1].axhline(.001, ls='--', color='#A8464B', label='Frozen threshold')
    axes[1].set_xticks([8192,32768,131072], ['8,192','32,768','131,072']); axes[1].set_ylabel('Empirical NUM3 acceptance statistic')
    axes[1].set_xlabel('Particles / independent replica'); axes[1].legend(frameon=False, fontsize=8)
    frame(axes[1], 'B  Archived v1 numerical failure')
    figure_save(fig, folder, 'F3_numerical_verification', ['paper11_v2/results/R1_code1/QC.json', 'paper11_v2/results/R2/numerical_oracle.json', 'paper11/results/M4_amendment3/NUMERICAL_LIMITATIONS.md'],
                {'exact_errors': err, 'NUM3_registered_empirical_statistics': bounds, 'R2_gradient_error': r2['gradient_error']}, saved,
                'Exact low-dimensional fixtures test code, not biology or global optimization. NUM3 statistics are empirical and not calibrated simultaneous error bounds; all remain above 0.001.')

    fig, ax = plt.subplots(figsize=(7.4, 4.1), layout='constrained')
    for j, row in enumerate(selected):
        family = row['family']; best = float(raw[family]['patient_weighted_dev_mean'])
        ax.plot([row['mean'], best], [j, j], color=COLORS[family], lw=1.5)
        ax.scatter(row['mean'], j, color=COLORS[family], marker='o', s=65)
        ax.scatter(best, j, edgecolor=COLORS[family], facecolor='none', marker='D', s=80)
        ax.text(row['mean']-.0012, j-.18, f"{row['mean']:.6f}", fontsize=8, ha='right')
    stationary = next(float(r['patient_weighted_dev_mean']) for r in grid if r['family'] == 'stationary')
    ax.axvline(stationary, color='#73858A', ls=':', label='Baseline one-SE: stationary')
    ax.scatter([],[],c='#34454A', label='Recorded reference / family one-SE'); ax.scatter([],[],edgecolor='#34454A', facecolor='white',marker='D',label='Raw grid maximum')
    ax.set_yticks(range(4), [LABELS[r['family']] for r in selected]); ax.invert_yaxis()
    ax.set_xlabel('Patient-weighted development log likelihood (nats/unit-bin; higher is better)')
    ax.set_xlim(-.579, -.508); ax.set_ylim(3.4,-.4)
    ax.legend(loc='upper left', bbox_to_anchor=(0,-.22), frameon=False, fontsize=8)
    frame(ax, 'Selected summaries and unselected score maxima')
    figure_save(fig, folder, 'F4_predictive_performance', [REPORT + 'all57configurations.csv', 'paper11_v2/results/R2/model_selection_manifest.json', 'paper11_v2/results/R2/baseline_selection.json', 'paper11_v2/results/R2/subject_statistics.json'],
                {'selected': selected, 'raw_maxima': raw, 'stationary_one_SE': stationary}, saved,
                'The baseline dot is the strongest raw-score reference, NOT the global baseline one-SE selection. Dynamics dots are family one-SE selections. Diamonds were not substituted for frozen selections.')

    contrasts = stats['comparisons']; matrix = np.array([[c['patient_differences'][p] for c in contrasts] for p in patients])
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 4.7), layout='constrained', gridspec_kw={'width_ratios':[1.5,1]})
    im = axes[0].imshow(matrix, cmap='RdBu_r', vmin=-.065, vmax=.065, aspect='auto')
    abbr = ['D-C','D-H','C-H','D-B','C-B','H-B']
    axes[0].set_xticks(range(6),abbr); axes[0].set_yticks(range(9), [p[-2:] for p in patients]); axes[0].set_ylabel('Patient ID')
    for i in range(9):
        for j in range(6): axes[0].text(j,i,f'{matrix[i,j]:+.3f}',ha='center',va='center',fontsize=7,color='white' if abs(matrix[i,j])>.04 else '#202828')
    frame(axes[0], 'A  All paired patient effects')
    for j,c in enumerate(contrasts):
        axes[1].plot(c['ci'], [j,j], color='#34454A',lw=2); axes[1].scatter(c['mean'],j,c='#267C9A',s=35)
    axes[1].set_yticks(range(6),abbr); axes[1].invert_yaxis(); axes[1].axvline(0,c='#73858A',ls='--'); axes[1].set_xlabel('Mean left-minus-right effect')
    frame(axes[1], 'B  Exploratory patient-only 95% CIs')
    fig.colorbar(im,ax=axes[0],shrink=.75,label='nats/unit-bin')
    figure_save(fig, folder, 'F5_patient_heterogeneity', ['paper11_v2/results/R2/subject_statistics.json'],
                {'patients': patients, 'contrasts': contrasts, 'effects': matrix.tolist()}, saved,
                'D discrete, C continuous recurrent, H hybrid, B strongest combined baseline. n=9 patients; intervals copied from saved paired bootstraps, postselection and exploratory, not confirmatory.')

    fig, ax = plt.subplots(figsize=(7.4, 4.3), layout='constrained')
    for family in ('baseline','discrete','continuous','hybrid'):
        rows = [r for r in grid if (r['family'] in ('stationary','history','event','drift','combined','population') if family=='baseline' else r['family']==family)]
        ax.scatter([float(r['total_nominal_parameters']) for r in rows], [float(r['patient_weighted_dev_mean']) for r in rows],
                   color=COLORS[family],s=30,alpha=.7,label='Poisson baselines (21)' if family=='baseline' else LABELS[family])
    for row in selected:
        ax.scatter(row['total_parameters'], row['mean'], s=100, facecolor='white', edgecolor=COLORS[row['family']],linewidth=1.8, marker='s')
    for row in raw.values(): ax.scatter(float(row['total_nominal_parameters']),float(row['patient_weighted_dev_mean']),c='#172629',s=100,marker='*')
    ax.set_xscale('log'); ax.set_xlabel('Patient-weighted mean total nominal free parameters'); ax.set_ylabel('Development score (nats/unit-bin)')
    ax.legend(frameon=False,fontsize=8); frame(ax, 'All 57 configurations: regularization and complexity')
    figure_save(fig, folder, 'F6_complexity_frontier', [REPORT+'all57configurations.csv','paper11_v2/results/R2/model_selection_manifest.json'],
                {'configurations': grid, 'selected': selected}, saved,
                'All 57 configurations retained. Squares mark recorded references/selections and stars mark raw family maxima. Parameters include shared offsets; nominal counts are not effective degrees of freedom or joint design rank.')

    evidence = [('R1 exact/causal fixtures', '220 oracle cases; 54 causal checks', 'COMPLETED'),
                ('R2 development fits', '3,887 / 3,887 optimizer successes', 'COMPLETED'),
                ('Patient comparisons', '9 patients; exploratory/postselection', 'COMPLETED'),
                ('Count-preserving null suite', '8 / 200 full cohort replicas', 'INCOMPLETE'),
                ('Circular shift / task timing nulls', 'Registered; remaining suites stopped', 'INCOMPLETE'),
                ('External recording support', '47 / 52 limited envelopes; 5 unknown', 'FAILED GATE'),
                ('External final predictive test', 'No physiological admission or scores', 'NOT EXECUTED'),
                ('Original R3 / neural mechanism', 'R3 not run; no NAP/CWP validation', 'NOT ESTABLISHED')]
    fig, ax = plt.subplots(figsize=(7.4, 4.4), layout='constrained'); ax.axis('off')
    for i, (name, detail, status) in enumerate(evidence):
        y = .92-i*.112
        ax.text(0,y,name,fontsize=9,fontweight='bold'); ax.text(0,y-.043,detail,fontsize=8,color='#54646A')
        ax.text(.99,y,status,ha='right',fontsize=9,color='#007F73' if status=='COMPLETED' else '#9D4969')
        ax.axhline(y-.058,color='#D9E0E1',lw=.7)
    figure_save(fig, folder, 'F7_evidence_boundaries', ['paper11_v2/results/R2/QC.json','paper11_v2/results/R1_code1/QC.json','paper11_v2/boundary_audit1/results/gate_result.json'],
                {'evidence': evidence},saved,
                'Engineering/numerical evidence is distinct from uncompleted null/independent biological validation. Failed external admission remains a scientific limitation; no rescue or new evaluation was executed.')
    write_json(output / 'figure_manifest.json', {p.stem: {'png_sha256': sha(p), 'pdf_sha256': sha(p.with_suffix('.pdf')),
                   'sidecar_sha256': sha(p.with_suffix('.json'))} for p in sorted(folder.glob('F*.png'))})


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', default=str(HERE/'output'))
    args = parser.parse_args(); out = Path(args.output).resolve()
    if HERE not in out.parents or out == HERE:
        raise ValueError('Generated outputs must stay within separate closeout track')
    out.mkdir(parents=True,exist_ok=True)
    saved = Saved(); values = export_tables(saved,out/'tables'); draw_figures(saved,out,values)
    write_json(out/'build_inputs.json', {'input_sha256': saved.record['input_sha256'], 'build_source_sha256': sha(__file__),
               'new_fits': 0, 'new_bootstraps_or_tests': 0, 'external_access': False, 'source': 'saved evidence only'})
    print('Saved-only tables/7figures generated:', out)


if __name__ == '__main__':
    main()
