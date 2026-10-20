"""Post-STOP saved-evidence checks; no production worker or numerical execution."""
import hashlib,json,unittest,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'paper16_development_r2'
E=R/'ops/evidence/2026-10-19/p16-m3-m5-frozen-development-r2'

def load(path):return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

class SavedStopTests(unittest.TestCase):
    def test_exact_failure_and_no_scientific_retry(self):
        stop=load(P/'results/SCIENTIFIC_STOP.json')
        self.assertEqual(stop['type'],'KeyError');self.assertIn('stimulus_invalid_intervals',stop['message'])
        self.assertTrue(stop['no_retry']);self.assertTrue(stop['all_later_tasks_not_executed'])
        self.assertFalse(stop['Final_C_access']);self.assertFalse(stop['Final_D_access'])
        supervision=load(P/'results/SUPERVISION.json')
        self.assertEqual(supervision['returncode'],1);self.assertFalse(supervision['science_complete'])
        self.assertTrue(supervision['native_job_tree_enforced']);self.assertFalse(supervision['killed_at_deadline'])
        self.assertFalse(supervision['clock_failure'])

    def test_saved_metadata_member_names_match_without_array_decode(self):
        audit=load(P/'SAVED_METADATA_SCHEMA_AUDIT.json');self.assertEqual(len(audit['sources']),27)
        present=0
        for row in audit['sources']:
            path=R/row['metadata_npz'];self.assertEqual(sha(path),row['sha256'])
            with zipfile.ZipFile(path) as z:names=[Path(x).stem for x in z.namelist()]
            self.assertEqual(names,row['archive_member_names_only'])
            present+='stimulus_invalid_intervals' in names
            self.assertFalse(row['neural_values_decoded'])
        self.assertEqual(present,3);self.assertFalse(audit['sources'][0]['assumed_field_present'])

    def test_zero_optimizer_and_all_later_boundaries_preserved(self):
        for name in ['ACCESS.jsonl','HTTP.jsonl','FIT_JOURNAL.jsonl','TASK_PLAN.json','A_PREPROCESSING_STATES.json',
                     'B_SELECTION.json','M4_SELECTION_FREEZE.json','E_BATCH_CLAIM.json','E_DEVELOPMENT_RESULTS.json','WORKER_COMPLETE.json']:
            self.assertFalse((P/'results'/name).exists(),name)
        for name in ['fits','prepared','prepared_raw','roles','B_selection','E','controls']:
            self.assertFalse((P/'work'/name).exists(),name)
        facts=load(P/'EXECUTION_FACTS.json')
        self.assertEqual(facts['optimizer_attempts'],0);self.assertEqual(facts['analytic_B0_certificates'],0)
        self.assertEqual(facts['B_access_sessions'],0);self.assertEqual(facts['E_access_sessions'],0)

    def test_production_and_all_reviewed_scientific_definitions_unchanged(self):
        for row in load(P/'PREFIT_FREEZE_MANIFEST.json')['files']:
            self.assertEqual(sha(R/row['path']),row['sha256'],row['path'])
        for row in load(P/'BOOTSTRAP.json')['normative_files']:
            self.assertEqual(sha(R/row['path']),row['sha256'],row['path'])
        self.assertEqual(sha(E/'PREFIT_REVIEW.md'),'7ea6a413dadaff2fcc3928dd30ab6af2f8e64ff83aa7349220e8a33cb09b8fe0')
        self.assertEqual(sha(E/'PREFIT_REVIEW_2.md'),'fee6d38494a3a5f845ca399ea824f7115e26a627253bbbc4f816a3de59655628')
        self.assertEqual(sha(E/'PREFIT_REVIEW_3.md'),'38a42b40c9728179f660abfe68dc2ffa2acdfc5273dbcba33b98a53f1a1d1560')

if __name__=='__main__':unittest.main(verbosity=2)
