import ast
import csv
import json
import os
import unittest
from pathlib import Path
from build import Saved, validate, config_key
from freeze import HERE, ROOT, load, sha


class CloseoutEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved=Saved();cls.grid,cls.stats,cls.coverage,cls.gate,cls.patients=validate(cls.saved)
        cls.out=Path(os.environ.get('P11_CLOSEOUT_OUTPUT',str(HERE/'output'))).resolve()
        assert HERE in cls.out.parents

    def test_exact_57_grid(self):
        self.assertEqual(len(self.grid),57)
        self.assertEqual(len({config_key(r) for r in self.grid}),57)

    def test_frozen_nine_subject_denominator(self):
        self.assertEqual(len(self.patients),9)
        self.assertTrue(all(c['subject_count']==9 for c in self.stats['comparisons']))

    def test_coverage_totals(self):
        self.assertEqual(len(self.coverage),23)
        self.assertEqual(sum(int(r['units']) for r in self.coverage),592)
        self.assertEqual(sum(int(r['train_trials']) for r in self.coverage),622)
        self.assertEqual(sum(int(r['validation_trials']) for r in self.coverage),201)

    def test_four_saved_scores(self):
        summary=load(self.out/'tables/summary.json')
        self.assertEqual(len(summary['selected']),4)
        for row in summary['selected']:
            self.assertAlmostEqual(row['mean'],self.stats['means'][row['family']]['mean'],places=14)

    def test_baseline_roles_not_conflated(self):
        summary=load(self.out/'tables/summary.json')
        self.assertEqual(summary['baseline_one_SE']['family'],'stationary')
        self.assertEqual(summary['shared_offset']['ridge'],.01)
        self.assertEqual(summary['selected'][0]['config']['ridge'],.001)
        self.assertEqual(summary['selected'][0]['selection_role'],'raw strongest baseline reference')

    def test_raw_maxima_are_different_configurations(self):
        summary=load(self.out/'tables/summary.json')
        for row in summary['selected'][1:]:
            self.assertNotEqual(config_key(row['config']),config_key(summary['raw_maxima'][row['family']]))
        for family in ('discrete','hybrid'):
            self.assertGreater(float(summary['raw_maxima'][family]['patient_weighted_dev_mean']),self.stats['means']['baseline']['mean'])

    def test_all_six_patient_effects_exact(self):
        with (self.out/'tables/all_patient_paired_effects.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),9)
        for row in rows:
            for c in self.stats['comparisons']:
                self.assertEqual(float(row[c['left']+'_minus_'+c['right']]),c['patient_differences'][row['patient']])

    def test_saved_statistics_not_recomputed(self):
        self.assertTrue(all(c['replicates']==10000 and c['sign_flip']['enumerations']==512 for c in self.stats['comparisons']))
        self.assertTrue(all(c['holm_p_value']==.0234375 for c in self.stats['comparisons']))

    def test_old_scientific_failures_preserved(self):
        self.assertEqual(self.gate['gate_verdict'],'FAIL')
        self.assertEqual(self.gate['scientific_verdict'],'DATA_INSUFFICIENT')
        self.assertEqual(self.gate['R3'],'NOT_EXECUTED')
        for n in (1,2,3):
            self.assertEqual(self.saved.json(f'paper11/results/M4_amendment{n}/gate_result.json')['gate'],'FAIL')

    def test_holdout_not_unlocked(self):
        self.assertTrue(self.gate['final_holdout_locked'])
        self.assertFalse(self.gate['external_spikes_accessed'])
        self.assertFalse(self.gate['oldtest_accessed'])

    def test_no_raw_file_fallback(self):
        for name in ('paper11/raw/spikes.tsv','paper11_v2/results/R0_amendment1_code1/features/sub-01_ses-01.json','../secret'):
            with self.assertRaises(ValueError):self.saved.path(name)

    def test_no_fitting_or_network_imports(self):
        for name in ('build.py','documents.py','pdf_document.py','reference_check.py'):
            tree=ast.parse((HERE/name).read_text())
            modules=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):modules.extend(a.name for a in node.names)
                elif isinstance(node,ast.ImportFrom):modules.append(node.module or '')
            self.assertFalse(any(m.startswith(('requests','urllib','run_r2','r2_models','predictive_models','scipy.optimize')) for m in modules))

    def test_fifty_seven_table_byte_identity(self):
        self.assertEqual(sha(self.out/'tables/all57configurations.csv'),sha(self.saved.path('paper11_v2/results/R2_development_report/report/all57configurations.csv')))

    def test_full_optimizer_grid(self):
        with (self.out/'tables/optimizer_diagnostics.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),3887)

    def test_all_intervals_present(self):
        for name,n in [('patient_conditional_CIs.csv',36),('session_conditional_CIs.csv',92)]:
            with (self.out/'tables'/name).open(newline='') as f:rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),n)

    def test_seven_figure_input_hashes(self):
        manifest=load(self.out/'figure_manifest.json')
        self.assertEqual(len(manifest),7)
        for name,digests in manifest.items():
            sidecar=load(self.out/'figures'/(name+'.json'))
            self.assertEqual(sidecar['render_code_sha256'],sha(HERE/'build.py'))
            self.assertTrue(sidecar['input_sha256'])
            for path,digest in sidecar['input_sha256'].items():self.assertEqual(sha(ROOT/path),digest)
            self.assertEqual(sha(self.out/'figures'/(name+'.png')),digests['png_sha256'])

    def test_all_requested_sections(self):
        text=(self.out/'manuscript.md').read_text()
        for title in ('Abstract','Introduction','Related Work','Data and Cohort','Mathematical Model Definitions',
                      'Numerical Verification','Experimental Design','Exploratory Results','Statistical Analysis',
                      'Limitations and Falsification Boundaries','Discussion','Conclusion','References','Supplementary Methods and Results'):
            self.assertIn(title,text)
        self.assertNotIn('{{',text)

    def test_main_paper_failure_disclosures(self):
        text=(self.out/'manuscript.md').read_text()
        for claim in ('eight full count-permutation','2,896','FAIL / DATA_INSUFFICIENT','R3 is NOT EXECUTED',
                      'previously exposed','not a stochastic Poisson latent dynamical system','not independent scientific validation'):
            self.assertIn(claim,text)

    def test_all_A1_A10_present(self):
        for n in range(1,11):self.assertGreater((self.out/'attachments'/f'A{n}.md').stat().st_size,300)

    def test_claim_map_evidence(self):
        claims=load(self.out/'claim_map.json');self.assertEqual(len(claims),11)
        for claim in claims.values():
            self.assertTrue(claim['evidence'])
            for name,digest in claim['evidence'].items():self.assertEqual(sha(ROOT/name),digest)

    def test_reference_sources_cached_only(self):
        from reference_check import verify_references
        records=verify_references(self.out)
        self.assertEqual(len(records),8)
        self.assertTrue(all(not r['new_search'] for r in records))


if __name__=='__main__':unittest.main(verbosity=2)
