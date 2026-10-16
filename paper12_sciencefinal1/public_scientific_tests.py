"""Original ten scientific oracles with an identical public synthetic metadata file."""
from pathlib import Path
from paper12_singleowner1.test_engineering import ScientificTests as OriginalScientificTests
from paper12_singleowner1.scientific_evaluator import rate_report
from paper12_singleowner1.common import read_json, sha


class PublicScientificTests(OriginalScientificTests):
    def test_saved_roster_rate_limits_and_no_D_selection(self):
        fixture = Path(__file__).resolve().parent / 'fixtures/synthetic_provenance_roster.json'
        from .trusted_host import E
        expected = read_json(E / 'public_reproduction_dependency_amendment.json')['fixture_sha256']
        self.assertEqual(sha(fixture), expected)
        report = rate_report(read_json(fixture))
        self.assertEqual(len(report['rows']), 13)
        self.assertTrue(all(v['within_original_log2'] for v in report['rows']))
        self.assertEqual(report['rate_source'], 'C_ONLY')
