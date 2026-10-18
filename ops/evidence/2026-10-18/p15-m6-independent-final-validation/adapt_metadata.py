"""Exact source-only adapter; original masks/codec/clock equations unchanged."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4]
P=R/'paper15_final1'
original=(R/'paper15_r1/metadata_qc.py').read_text(encoding='utf-8')
text=original.replace('Frozen M1 native task/observation screens, without reading spike arrays.',
                      'Frozen M1 Final-native task/observation screens; never read spike arrays.')
text=text.replace("        if not dev:continue  # Original Final identities retained; no new Final processing.",
                  "        assert not dev, 'Only the eight Final-reserved sources'\n        annotation_audit(entry)")
text=text.replace("if f['role'] not in ('times','clusters') and (dev or f['role'] not in ('wheel_times','wheel_position'))}",
                  "if f['role'] not in ('times','clusters')}")
text=text.replace("wheel_available=dev and all(paths[k].exists() for k in ('wheel_times','wheel_position'))",
                  "wheel_available=all(paths[k].exists() for k in ('wheel_times','wheel_position'))")
text=text[:text.index("    eligible=[x for x in out if x['allocation']=='DEVELOPMENT'")]+'''    possible=[x for x in out if x['prephysiology_possible']]
    dump(P/'results/FINAL_METADATA_GATE.json',dict(final_candidates=8,
        final_metadata_examined=len(out),possible_subjects=[x['subject'] for x in possible],
        final_trial_anatomy_upper_bound=len(possible),final_lab_upper_bound=len({x['lab'] for x in possible}),
        source_metadata_complete=len(out)==8,minimum_descriptive_mice=6,minimum_primary_mice=8,
        at_least_six_metadata_possible=len(possible)>=6,Final_C_neural_access=False,
        Final_D_scientific_access=False,real_fits=0))


if __name__=='__main__':run()
'''
text=text.replace('def run():', '''def annotation_audit(entry):
    selected=next(x for x in entry['files'] if x['role']=='saturation')['key']
    probe=entry['files'][0]['probe']
    for item in entry['additional_annotation_catalog']:
        key=item['key']
        if '/raw_ephys_data/' in key and '/raw_ephys_data/'+probe+'/' not in key:continue
        if key!=selected:raise ValueError('Unresolved additional selected-probe/session invalid annotation: '+key)


def run():''')
assert text!=original and "if not dev:continue" not in text
(P/'metadata_qc.py').write_text(text,encoding='utf-8')
f=json.loads((R/'paper15_r1/SOURCE_FILE_FREEZE.json').read_text())
rows=[r for r in f['subjects'] if r['allocation']=='FINAL_RESERVED']
assert len(rows)==8
(P/'SOURCE_FILE_FREEZE.json').write_text(json.dumps(dict(f,subjects=rows,scope='Original exact eight Final entries; copied without source identity modification',all_inventory_pass=all(r['source_inventory_pass'] for r in rows)),indent=2,sort_keys=True)+'\n')
print('Final metadata adapter created; no data decoded')
