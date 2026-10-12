"""Append-only human-authorized method clarification, never rewrites old protocol."""
from datetime import datetime, timezone
import register as r


def main():
    r.verify()
    implementation = r.load(r.HERE / 'development_registration.json')
    for name, digest in implementation['implementation_sha256'].items():
        if r.sha(r.HERE / name) != digest:
            raise RuntimeError('DEVELOPMENT_IMPLEMENTATION_CHANGED')
    decision = r.load(r.HERE / 'M3_METHOD_DECISION1.json')
    if decision['ridge_normalization'] != 'per_unit_exposure' or decision['offset_policy']['ridge'] != .1 or decision['offset_policy']['seeds'] != [11, 23, 37] or decision['offset_policy']['validation_selection'] is not False:
        raise RuntimeError('HUMAN_METHOD_DECISION_MISMATCH')
    result = dict(utc=datetime.now(timezone.utc).isoformat(),
                  method_sha256=r.sha(r.HERE / 'M3_METHOD_DECISION1.json'),
                  implementation_registration_sha256=r.sha(r.HERE / 'development_registration.json'),
                  register_method_sha256=r.sha(r.HERE / 'register_method.py'),
                  real_development_values_exposed_to_analysis=False,
                  final_values_exposed_to_analysis=False, final_holdout_evaluated=False,
                  original_protocol_reclassified=False)
    r.save(r.HERE / 'method_registration1.json', result, True)
    print('HUMAN_AUTHORIZED_METHOD_CLARIFICATIONS_FROZEN_BEFORE_REAL_ANALYSIS')


if __name__ == '__main__':
    main()
