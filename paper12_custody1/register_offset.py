"""Prospective shared-offset amendment; no neural access or model execution."""
from datetime import datetime, timezone
import register as r


def main():
    r.verify()
    method = r.load(r.HERE / 'method_registration1.json')
    if method['method_sha256'] != r.sha(r.HERE / 'M3_METHOD_DECISION1.json'):
        raise RuntimeError('AUTHORIZED_METHOD_CHANGED')
    result = dict(utc=datetime.now(timezone.utc).isoformat(),
                  amendment_sha256=r.sha(r.HERE / 'M4_OFFSET_AMENDMENT1.json'),
                  method_registration_sha256=r.sha(r.HERE / 'method_registration1.json'),
                  register_offset_sha256=r.sha(r.HERE / 'register_offset.py'),
                  archived_math_sha256={p: r.sha(r.ROOT / 'paper11_v2/scripts' / p) for p in
                                        ('predictive_models.py', 'predictive_models_code1.py')},
                  real_M4_fits_executed=False, final_holdout_evaluated=False,
                  original_evidence_reclassified=False)
    r.save(r.HERE / 'offset_registration1.json', result, True)
    print('ALL_THREE_FAMILIES_SHARED_OFFSET_REGISTERED_BEFORE_REAL_FITS')


if __name__ == '__main__':
    main()
