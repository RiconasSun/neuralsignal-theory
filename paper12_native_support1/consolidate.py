"""Add physical stimulus-clock evidence and explicit warning classifications."""
import csv
import json
from pathlib import Path
from register import HERE,ROOT,sha,verify
from analysis import write_csv
from storage import load

def main(output=None):
    verify();out=Path(output) if output else HERE/'results'
    rows=list(csv.DictReader((out/'session_evidence_matrix.csv').open()))
    clock_rows=[];fc_primary=[];secondary=[]
    for row in rows:
        sid=row['session_id'];visual=load(HERE/'metadata/visual_clock_code1'/(sid+'.json'))
        row['visual_all_registered_tables_pass']=visual['pass']
        for kind,prefix in [('grating','drifting_gratings'),('movie','natural_movie_one')]:
            name=next((n for n in visual.get('per_table',{}) if n.startswith(prefix)),None)
            values=visual.get('per_table',{}).get(name,{})
            good=bool(values.get('p95_seconds') is not None and values['p95_seconds']<=.001 and values['max_seconds']<=.005)
            row[kind+'_physical_frame_clock_pass']=good
            row[kind+'_physical_frame_max_error_seconds']=values.get('max_seconds')
            row[kind+'_physical_frame_p95_error_seconds']=values.get('p95_seconds')
            clock_rows.append({'session_id':sid,'kind':kind,'targets':values.get('targets',0),
                               'physical_frame_clock_pass':good,'max_error_seconds':values.get('max_seconds'),
                               'p95_error_seconds':values.get('p95_seconds'),'above5ms':values.get('above5ms')})
        if row['protocol']=='functional_connectivity':
            if row['grating_physical_frame_clock_pass'] and int(row['grating_clock_bracketed_paired_trials'])>0:fc_primary.append(sid)
            if row['movie_physical_frame_clock_pass'] and int(row['movie_clock_bracketed_paired_trials'])>0:secondary.append(sid)
    write_csv(out/'session_evidence_matrix.csv',rows);write_csv(out/'physical_frame_timing.csv',clock_rows)
    summary=load(out/'summary.json')
    summary.update({'functional_connectivity_physical_clock_grating_potential_mice':len(fc_primary),
                    'functional_connectivity_physical_clock_movie_potential_mice':len(secondary),
                    'visual_all_table_pass_sessions':sum(load(p)['pass'] for p in (HERE/'metadata/visual_clock_code1').glob('*.json')),
                    'primary_supported_grating_trial_min':min(int(r['grating_clock_bracketed_paired_trials']) for r in rows if r['session_id'] in fc_primary),
                    'primary_supported_grating_trial_max':max(int(r['grating_clock_bracketed_paired_trials']) for r in rows if r['session_id'] in fc_primary)})
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True))
    verdict='CURATED_RELEASE_SUPPORT_ONLY_PROPOSE_SEPARATE_EXPLORATORY_PROTOCOL' if len(fc_primary)>=16 else 'INCONCLUSIVE'
    gate={'mission':'P12-M0-NATIVE-SUPPORT-AUDIT-1','scientific_verdict':verdict,
          'original_M0_reclassified':False,'original_criteria_demonstrated':False,
          'original_M0_pass':False,'native_recording_continuity_certified':False,
          'scientific_validation_pass':False,'M1_authorized_or_executed':False,
          'functional_connectivity_potential_mice':len(fc_primary),'minimum_required_mice':16,
          'resolved':['Full58session/332probe denominator','Digital barcode-to-master relative timing and diagnosed segments',
                      'Physical visual sync-to-curated stimulus clock diagnostics','Real repeated grating trials and complete movie-cycle distinction',
                      'Known-invalid tags attributed to probes/global sessions','Unit/channel/probe/atlas coordinate joins and geometry sensitivity'],
          'unresolved':['Lossless native packet continuity and per-bin observed exposure cannot be certified from serialized counter/byte length',
                        'Independent blind histological ground truth and quantitative registration error are unavailable',
                        '54calendar epoch disagreements remain; only elapsed-clock consistency assessed',
                        'Two visual-table maximum-error failures and two sessions with nonpositive movie intervals retained',
                        'Physiological unit eligibility/firing adequacy not assessed'],
          'warning_classes':{'critical_for_original_admission':['Native lossless observation/continuity certificate absent'],
                             'explicit_exploratory_sensitivity':['Physiology-assisted atlas labels','20/40um channel-label boundary proxies',
                                                               'Known gaps/underidentified segments','Calendar metadata inconsistency','Failed movie/frame diagnostics'],
                             'optional_omit_prospectively':['Running/pupil/other behavior covariates; no mandatory missingness gate for a stimulus-controlled design']},
          'warning_count':5,'bug_count':0,'next':'Recommend separate curated-release exploratory M1 protocol decision only; no M1 launch here',
          'IBL_accessed':False,'IBL_reason':'Allen yields sufficient common-protocol timing-supported potentials; missing lossless packet/independent anatomy certificate is not demonstrably resolved by the old IBL inventory. No justified extra cohort assessment.',
          'preserved_original_gate_sha256':{n:sha(ROOT/'paper12/results'/n) for n in ('allen_gate_result.json','ibl_gate_result.json','gate_result.json')}}
    (out/'gate_result.json').write_text(json.dumps(gate,indent=2,sort_keys=True))
    print(json.dumps(summary,indent=2));return gate

if __name__=='__main__':main()
