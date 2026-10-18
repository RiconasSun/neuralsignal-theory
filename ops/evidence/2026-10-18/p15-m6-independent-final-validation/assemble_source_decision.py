"""Assemble saved metadata admission without replaying any source attempt."""
import datetime
from paper15_final1.source import P,E,R,source_rows,read,dump,sha

target=P/'results/FINAL_METADATA_GATE.json';assert not target.exists()
failure=read(E/'NYU21_NATIVE_WHEEL_FAILURE.json')
assert failure['subject']=='NYU-21' and failure['strict_timestamp_order'] is False
assert failure['nonpositive_timestamp_differences']==16485
preserved=read(E/'METADATA_INTERRUPTION_PRESERVATION.json')
for filename,h in preserved['completed_state_sha256'].items():assert sha(P/'metadata'/filename)==h
records=[]
for row in source_rows():
    subject=row['subject'];path=P/'metadata'/(subject+'_task.json')
    if subject=='NYU-21':
        assert not path.exists()
        records.append(dict(subject=subject,source_metadata_pass=False,prephysiology_possible=False,
            reason='NATIVE_WHEEL_NOT_STRICTLY_INCREASING',source_failure_sha256=sha(E/'NYU21_NATIVE_WHEEL_FAILURE.json'),
            wheel_duplicate_adjacent_pairs=16485,source_repaired=False,attempt_retried=False))
        continue
    doc=read(path);result=doc['result'];assert result['allocation']=='FINAL_RESERVED'
    records.append(dict(subject=subject,source_metadata_pass=True,prephysiology_possible=result['prephysiology_possible'],
        structural_eligible_epochs=result['structural_eligible_epochs'],native_provider_good=result['source_mapping']['native_MOp_provider_good'],
        metadata_sha256=sha(path),original_native_trials=result['original_native_trials'],lab=result['lab']))
possible=[r['subject'] for r in records if r['prephysiology_possible']]
assert len(records)==8 and len(possible)==7
dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),subjects=records,final_candidates=8,
    possible_subjects=possible,final_trial_anatomy_upper_bound=7,source_metadata_complete=True,
    all_eight_source_pass=False,source_exclusions=['NYU-21'],source_selection_changed=False,
    at_least_six_metadata_possible=True,primary_eight_mouse_gate_possible=False,
    prospective_interpretation='At most7 mice; DESCRIPTIVE ONLY mandatory regardless of effects/p-values; no replacement of excluded animal',
    minimum_descriptive_mice=6,minimum_primary_mice=8,Final_C_neural_access=False,Final_D_scientific_access=False,real_fits=0))
dump(E/'SOURCE_ADMISSION_RECEIPT.json',dict(source_gate_sha256=sha(target),completed_original_states_unchanged=6,
    last_unattempted_completed='ZFM-01936',excluded_without_repair='NYU-21',not_a_restarted_metadata_batch=True,
    original_failure_preserved=True,prospective_descriptive_only=True,Final_neural_read=False))
print('All8source dispositions complete:7metadata-admissible,NYU21excluded; maximum DESCRIPTIVE ONLY')
