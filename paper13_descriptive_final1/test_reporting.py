import uuid
import unittest
from unittest.mock import patch
import numpy as np
from . import build_report as r,controls
from paper13_ki_execution1.animal_stats import summarize
from paper13_ki_execution1.sensitivity_plan import MANDATORY


class ReportingTests(unittest.TestCase):
    def test_table_label_pipe_cannot_shift_scientific_columns(self):
        text=r.md_table(['group','n','effect'],[['mouse|probe',9,.01]])
        self.assertEqual(len(text.splitlines()[-1].split('|')),5)
        self.assertIn('mouse / probe',text)

    def test_full_synthetic_text_tables_figures_all_failures_retained_no_source_or_fit(self):
        out=r.P/'work'/('report_'+uuid.uuid4().hex)
        mice=['synthetic'+str(j) for j in range(9)]
        def scores(i):
            values={name:-1.+i*.001 for name in r.MODELS}
            values.update(D=-.95+i*.0001,C=-.97-i*.0001,S=-.96)
            values['Bstar']=values['B2'];return values
        per={m:{'scores':scores(j),'nominal_unit_bins':12000} for j,m in enumerate(mice)}
        stats,_=summarize({m:{k:v['scores'][k] for k in ['B4','D','C','Bstar','S']} for m,v in per.items()},mice)
        for name in r.CONTRASTS[:3]:stats['contrasts'][name]['final_claim_status']='INCONCLUSIVE'
        arrays={s:np.zeros((999,9,9)) for s in controls.SUITES}
        nulls,_=controls.summarize(arrays,{m:v['scores'] for m,v in per.items()},mice)
        panels={name:{'mandatory':True,'contributing_mice':mice[:6] if name=='recent_event' else mice,
            'computed_mice_including_subthreshold':mice,'required_coverage_pass':name!='recent_event','equal_mouse_effect_means':[.01]*6} for name in MANDATORY}
        groups={'groups':{'genotype':{'groups':{'NOT_DECODED_FROM_SOURCE':{'n':9,'leave_group_out_status':'UNAVAILABLE_EMPTY_REMAINDER','equal_mouse_effect_means':[.01]*6,'leave_group_out_means':None}}}}}
        final={'FINAL_D_EXECUTION':'VALIDLY_COMPLETED_ONCE_DESCRIPTIVE','statistics':stats,'mouse_order':mice,'per_mouse':per,'null_controls':nulls,'sensitivity_report':{'panels':panels},'descriptive_group_dependence':groups}
        calibration={'COMPLETE_C_STATE':'PASS','verified_fits':198,'initial_intermediate_endpoint_certificates':594,'max_PG':1e-5,'max_AD_relative':1e-14,'max_fixed_FD_relative':1e-8}
        development={'registered_statistics':{'contrasts':stats['contrasts']},'per_mouse':per,'mouse_order':mice}
        cell={'retained_epochs':12,'retained_units':8,'nominal_unit_bins':2400,'coverage_eligible':True,'scores':scores(0)}
        def read(path):
            name=path.name
            if name=='FINAL_D_RESULTS.json':return final
            if name=='FINAL_C_FULL_STATE_MANIFEST.json':return calibration
            if name=='M5_EXPLORATORY_RESULTS.json':return development
            if name=='RETAINED_E_CONTROLS_SUMMARY.json':return nulls
            if name.startswith('synthetic'):return {key:cell for key in MANDATORY}
            raise AssertionError('Unexpected result/source access: '+str(path))
        with patch.object(r.b,'read',side_effect=read):result=r.prepare(out)
        self.assertTrue(result['manuscript_complete'])
        self.assertEqual(len(list(out.glob('*.csv'))),6)
        text=(out/'Manuscript.md').read_text(encoding='utf8')
        self.assertNotIn('{{',text)
        for name in r.CONTRASTS:self.assertIn(name,text)
        self.assertIn('FAILED / UNAVAILABLE',text);self.assertIn('post-amendment',text)
        self.assertTrue((out/'figures/effects.svg').is_file());self.assertTrue((out/'figures/mice.png').is_file())


if __name__=='__main__':unittest.main()
