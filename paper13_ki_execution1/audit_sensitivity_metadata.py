"""Saved headers and A/C QC only; no B/E/D neural arrays or source IO."""
import datetime
from .source import ROOT,P,ALLOCATION,sha
from .baseline_A import read,save_matching
from . import sensitivity_plan as s


def run():
    rows=[]
    for record in ALLOCATION:
        mouse=record['mouse_id'];qc=read(P/'results/qc'/(mouse+'.json'))
        if sha((ROOT/record['header_file']).read_bytes())!=record['header_sha256']:raise ValueError('Frozen header mismatch')
        plan=s.metadata(record);partition='E' if record['role']=='development' else 'D'
        epochs=[e for e in record['epochs'] if e['partition']==partition]
        masks=s.unit_panels({'units':qc['selected_units'],'unit_QC':{str(a['unit_id']):a for a in qc['attempts'] if a['pass']}})
        counts={name:len(epochs) for name in masks}
        counts['recent_event']=sum(plan['recent_event'][str(e['ordinal'])] for e in epochs)
        for name in ['alignment_minus01','alignment_plus01']:counts[name]=sum(e['retained'] for e in plan[name] if e['partition']==partition)
        units={name:sum(mask) for name,mask in masks.items()}
        units.update({name:8 for name in ['recent_event','alignment_minus01','alignment_plus01']})
        rows.append({'mouse_id':mouse,'role':record['role'],'report_partition':partition,'epochs':counts,'units':units,
            'metadata_coverage_eligible':{name:bool(counts[name]>=10 and units[name]>=4) for name in s.MANDATORY},
            'recent_retained_parent_ordinals':[e['ordinal'] for e in epochs if plan['recent_event'][str(e['ordinal'])]],
            'header_sha256':record['header_sha256'],'QC_file_sha256':sha((P/'results/qc'/(mouse+'.json')).read_bytes())})
    final=[r for r in rows if r['role']=='final']
    result={'audit_scope':'Saved header metadata and frozen A/C unit QC only; no final D neural outcomes',
        'rows':rows,'final_contributors':{name:sum(r['metadata_coverage_eligible'][name] for r in final) for name in s.MANDATORY},
        'required_final_contributors':8,'minimum_epochs_per_contributor':10,'minimum_units_per_contributor':4,
        'final_C_model_fits_executed':False,'final_D_outcomes_accessed':False,
        'interpretation':'Coverage evidence only; original protocol governs claim withholding/stopping, independent review pending'}
    path=P/'results/M6_SENSITIVITY_METADATA_AUDIT.json';save_matching(path,result)
    print(result['final_contributors'])


if __name__=='__main__':run()
