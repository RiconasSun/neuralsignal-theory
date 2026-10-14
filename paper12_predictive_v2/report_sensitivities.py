"""Descriptive reporting of all already-registered probe/rate views; no tests/selection."""
import json
import numpy as np
import study as r
from mouse_statistics import PRIMARY
def main():
    r.save(r.HERE/'descriptive_reporting_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'source_sha256':r.sha(r.HERE/'report_sensitivities.py'),'purpose':'Report every preselected probe/rate view and its coverage/residual mismatch; no new fit, test or selected hypothesis','input_sha256':r.sha(r.HERE/'results/science/native/scientific_scores.json'),'final_access':False})
    rows=r.load(r.HERE/'results/science/native/scientific_scores.json')['rows'];mice=sorted({z['mouse_id'] for z in rows});probe=[];tables='# Complete registered probe dependence assessment\n\nAll values are CA1-minus-DG nats per actual nominal unit-bin. Probe views change the selected unit pool; these are descriptive assessments, not independent-probe replication. Every available view remains in scientific_scores.json. No favorable probe replaces the primary result.\n\n| Mouse | Contribution | Primary | Selected shared-probe view | LOPO minimum | LOPO maximum | Max absolute shift from primary |\n|---|---|---|---|---|---|---|\n'
    for mouse in mice:
        local=[z for z in rows if z['mouse_id']==mouse];views={}
        for view in sorted({z['view'] for z in local}):
            pair={z['region']:z for z in local if z['view']==view}
            if set(pair)=={'CA1','DG'}:views[view]={k:pair['CA1']['gains'][k]-pair['DG']['gains'][k] for k in PRIMARY}
        shared=next((v for v in views if v.startswith('shared_probe_')),None);leave=[v for v in views if v.startswith('leave_probe_')]
        for k in PRIMARY:
            p=views['primary'][k];lo=[views[v][k] for v in leave];sh=None if shared is None else views[shared][k];changes=[views[v][k]-p for v in leave+([] if shared is None else [shared])]
            value={'mouse_id':mouse,'contrast':k,'primary':p,'shared_view':shared,'shared_difference':sh,'LOPO_views':leave,'LOPO_differences':lo,'LOPO_min':min(lo) if lo else None,'LOPO_max':max(lo) if lo else None,'max_abs_shift':max(map(abs,changes)) if changes else None};probe.append(value)
            formatvalue=lambda v:'UNAVAILABLE' if v is None else f'{v:.8f}'
            tables+='| '+' | '.join([mouse,k,*[formatvalue(value[n]) for n in ('primary','shared_difference','LOPO_min','LOPO_max','max_abs_shift')]])+' |\n'
    r.save(r.HERE/'results/probe_assessment.json',{'rows':probe,'new_tests':0,'new_fits':0,'final_access':False});(r.HERE/'PROBE_DEPENDENCE.md').write_text(tables,encoding='utf-8')
    cov=r.load(r.HERE/'results/preflight_corrected/native/coverage.json');text='# Training-rate matching coverage and residual mismatch\n\nGreedy A-only matching admits pairs within absolute log-rate distance<=log(2); it is not exact rate equalization. No B rates/scores select units. Both ROIs have equal K per mouse. Residual mismatches and changed population estimands remain limitations.\n\n| Mouse | Matched K per ROI | Median absolute log-rate ratio | Maximum absolute log-rate ratio |\n|---|---|---|---|\n'
    for v in cov['mice']:
        q=v['rate_pairs_abs_log_ratio'];text+=f"| {v['mouse_id']} | {v['views']['rate_matched']['CA1_count']} | {np.median(q):.6f} | {max(q):.6f} |\n"
    (r.HERE/'RATE_MATCHING.md').write_text(text,encoding='utf-8');print('ALL_PROBE_RATE_VIEWS_REPORTED',len(probe))
if __name__=='__main__':main()
