"""Report failed synthetic proposal diagnostics, never experimental findings."""
import csv
import sys
from pathlib import Path
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import run_m4_amendment1 as previous

PAPER = previous.PAPER
OUTPUT = PAPER/'results/M4_amendment2'


def main():
    audit = previous.load(OUTPUT/'numerical_oracle_audit.json')
    rows = [{'fixture': row['fixture'], 'seed': row['seed'], 'particles': row['particles'],
             'max_per_bin_error_nats_unit_bin': row['maximum_error_nats_unit_bin'],
             'oracle_budget_shift_nats_unit_bin': row['oracle_budget_shift_nats_unit_bin'],
             'signed_sequence_mean_error_nats_unit_bin': float(np.mean(np.asarray(row['particle_scores'])-row['oracle_scores'])/4),
             'minimum_ess_fraction': row['diagnostics']['minimum_ess_fraction'],
             'maximum_particle_weight': row['diagnostics']['maximum_particle_weight']}
            for row in audit['rows']]
    with (OUTPUT/'controlled_oracle_diagnostics.csv').open('w',encoding='utf-8',newline='') as handle:
        writer = csv.DictWriter(handle,fieldnames=list(rows[0]) if rows else ['fixture','seed','particles','max_per_bin_error_nats_unit_bin'],lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    summaries = []
    fig, axes = plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    for fixture,color in [('controlled_K1_D2','#24766a'),('controlled_K2_D2','#b94163')]:
        subset = [row for row in rows if row['fixture']==fixture]
        if not subset:
            continue
        values = np.asarray([row['signed_sequence_mean_error_nats_unit_bin'] for row in subset])
        sd = float(values.std(ddof=1)) if len(values)>1 else None
        summaries.append({'fixture':fixture,'replicas':len(subset),'mean_signed_sequence_error':float(values.mean()),
                          'sequence_error_sd':sd,
                          'max_absolute_sequence_error':float(np.max(np.abs(values))),
                          'sequence_conservative_discrepancy':float(np.max(np.abs(values))+1.96*sd) if sd is not None else None})
        axes[0].scatter([fixture]*len(subset),[row['max_per_bin_error_nats_unit_bin'] for row in subset],color=color)
        axes[1].scatter([fixture]*len(subset),[row['minimum_ess_fraction'] for row in subset],color=color)
    axes[0].axhline(.001,color='#596471',linestyle='--')
    axes[0].set(title='Controlled oracle gate '+audit['gate'],ylabel='Max per-bin error (nats/unit-bin)')
    axes[1].set(title='High ESS does not certify score precision',ylabel='Minimum ESS/N')
    for axis in axes:
        axis.tick_params(axis='x',rotation=15,labelsize=9)
    fig.suptitle('M4-NUM-2 synthetic fixtures only; no real hippocampal evaluation',fontsize=11)
    fig.savefig(OUTPUT/'controlled_oracle_diagnostics.png',dpi=160)
    fig.savefig(OUTPUT/'controlled_oracle_diagnostics.pdf')
    plt.close(fig)
    sources = ['scripts/guided_poisson_filter.py','scripts/oracle_m4_num2.py','scripts/report_m4_num2.py',
               'tests/test_m4_num2.py','scripts/reproduce-m4-num2.ps1','data_manifest/M4/numerical_amendment2.json']
    previous.write(OUTPUT/'qc_report.json',{'fixtures_not_experimental_findings':True,'summaries':summaries,
        'failed_replicas':sum(row['max_per_bin_error_nats_unit_bin']+row['oracle_budget_shift_nats_unit_bin']>.001 for row in rows),
        'total_replicas':len(rows),'real_neural_evaluation':False,'final_holdout_access':False,
        'source_sha256':{name:previous.digest(PAPER/name) for name in sources},
        'oracle_audit_sha256':previous.digest(OUTPUT/'numerical_oracle_audit.json'),
        'runtime':{'executable':sys.executable,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__}})
    previous.write(OUTPUT/'gate_result.json',{'milestone':'M4','amendment':'M4-NUM-2','gate':audit['gate'],
        'scientific_verdict':'INCONCLUSIVE' if audit['gate']=='FAIL' else 'NOT_EVALUATED','stage':'proposal_controlled_oracle',
        'errors':audit['errors'],'proposal_unit_tests_exit_code':audit['tests_exit_code'],
        'registration_status':'NOT_ACTIVATED_FOR_REAL_EVALUATION','threshold_nats_unit_bin':.001,
        'final_holdout_access':False,'real_neural_evaluation':False,'finished_at_utc':previous.now()})
    previous.write(OUTPUT/'claim_audit.json',{'supported':['Formula/implementation unit tests exit code '+str(audit['tests_exit_code']),
        'Controlled synthetic numerical-oracle precision '+audit['gate']+'; no real-data inference'],
        'unsupported':['Real d2 degeneracy resolved','Real M4 numerical gate passed','Fair full model competition completed',
        'Preferred hippocampal regime','NAP/CWP/neural primitives validated','Absolute integration accuracy proved']})
    print('NUM2 controlled oracle '+audit['gate']+'; real evaluation not activated.')


if __name__=='__main__':
    main()
