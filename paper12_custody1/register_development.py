"""Freeze synthetic implementation preparation; does not choose scientific methods."""
from datetime import datetime, timezone
import register as r


def main():
    r.verify()
    files = ('register_development.py', 'aggregate4.py', 'test_aggregate4.py',
             'baseline_features.py', 'test_baseline_features.py', 'baseline_fit.py',
             'test_baseline_fit.py', 'native_analysis_check.py', 'analysis_worker.py',
             'development_export.py', 'launch_analysis.py', 'manifest_validation.py',
             'test_manifest_validation.py')
    result = dict(utc=datetime.now(timezone.utc).isoformat(),
                  implementation_sha256={name: r.sha(r.HERE / name) for name in files},
                  scope='Synthetic numerical/native-role preparation; real M3 requires full M2 PASS and separately frozen human ridge-normalization decision',
                  scientific_method_choice='UNRESOLVED',
                  real_development_values_exposed_to_analysis=False,
                  final_values_exposed_to_analysis=False, final_holdout_evaluated=False,
                  original_scientific_protocol_reclassified=False)
    r.save(r.HERE / 'development_registration.json', result, True)
    print('SYNTHETIC_IMPLEMENTATION_BOUND;REAL_METHOD_CHOICE_UNRESOLVED')


if __name__ == '__main__':
    main()
