"""Trusted A/B export only; never unseals C/D or exports source vectors."""
import hashlib
from pathlib import Path
import numpy as np
import register as r
import custodian
from cipher_core import unseal


def main():
    custodian.check_gate()
    gate = r.load(r.HERE / 'results/M2/aggregate4/gate_result.json')
    if gate['gate'] != 'PASS':
        raise PermissionError('M2_FULL_COHORT_GATE_REQUIRED')
    policy = r.load(r.HERE / 'development_registration.json')
    for name, digest in policy['implementation_sha256'].items():
        if r.sha(r.HERE / name) != digest:
            raise PermissionError('DEVELOPMENT_IMPLEMENTATION_CHANGED')
    method = r.load(r.HERE / 'M3_METHOD_DECISION1.json')
    method_registration = r.load(r.HERE / 'method_registration1.json')
    if method_registration['method_sha256'] != r.sha(r.HERE / 'M3_METHOD_DECISION1.json') or method_registration['implementation_registration_sha256'] != r.sha(r.HERE / 'development_registration.json'):
        raise PermissionError('PROSPECTIVE_METHOD_DECISION_CHANGED')
    if method['ridge_normalization'] not in ('total_unit_bins', 'per_unit_exposure'):
        raise PermissionError('HUMAN_RIDGE_DECISION_REQUIRED')
    old = r.ROOT / 'paper12_curated_v1'
    animals = r.load(old / 'locks/animals.json')
    units = r.load(old / 'locks/units.json'); trials = r.load(old / 'locks/trials.json')
    root = r.HERE / 'exports/development1'
    root.mkdir(exist_ok=False, parents=True)
    custodian.protect(root)
    manifest = dict(group='development', compartments=['A', 'B'], sessions=[],
                    M2_gate_sha256=r.sha(r.HERE / 'results/M2/aggregate4/gate_result.json'),
                    development_registration_sha256=r.sha(r.HERE / 'development_registration.json'),
                    method_decision_sha256=r.sha(r.HERE / 'M3_METHOD_DECISION1.json'),
                    ridge_normalization=method['ridge_normalization'])
    conditions = sorted({t['condition'] for t in trials})
    if len(conditions) != 8:
        raise ValueError('FROZEN_CONDITION_SET_CHANGED')
    for animal in animals:
        if animal['group'] != 'development':
            continue
        sid = animal['session_id']; receipt_path = r.HERE / 'results/M2/index2/sessions' / (sid + '.json')
        receipt = r.load(receipt_path)
        if r.sha(receipt_path) != gate['receipt_sha256'][str(receipt_path.relative_to(r.HERE))]:
            raise ValueError('COHORT_GATE_RECEIPT_CHANGED')
        if not receipt['eligible_mouse']:
            continue
        namespace = receipt.get('custody_artifact_namespace', 'real_index2')
        if namespace not in ('real_index2', 'real_transport1'):
            raise ValueError('CUSTODY_NAMESPACE_INVALID')
        private = r.HERE / '.private' / namespace / sid
        session_units = [u for u in units if u['session_id'] == sid]
        session_trials = [t for t in trials if t['session_id'] == sid]
        qc = {u['unit_id']: u for u in r.load(private / 'private_provenance.json')['unit_QC']}
        fields = {}
        selected = {}
        for region in ('CA1', 'DG'):
            ids = [i for i, u in enumerate(session_units) if u['subfield'] == region and qc[u['unit_id']]['eligible']]
            ids.sort(key=lambda i: hashlib.sha256(('P12-CURATED-EXPLORATORY-V1|unit|' + session_units[i]['unit_id']).encode()).hexdigest())
            selected[region] = ids[:32]
            if len(selected[region]) < 5:
                raise ValueError('PHYSIOLOGICAL_ADMISSION_RECEIPT_MISMATCH')
            fields[region + '_unit_ids'] = np.array([session_units[i]['unit_id'] for i in selected[region]])
        base_context = dict(study=r.ID, mouse=animal['mouse_id'], source_etag=receipt['source_etag'],
                            trial_lock_sha256=r.sha(old / 'locks/trials.json'), unit_lock_sha256=r.sha(old / 'locks/units.json'))
        for compartment, partition in (('A', 'train'), ('B', 'validation')):
            subset = [t for t in session_trials if t['partition'] == partition and t['metadata_admitted']]
            shape = (len(subset), 20, len(session_units))
            envelope = private / (compartment + '.gcm')
            if r.sha(envelope) != receipt['ciphertext_receipts'][compartment]['ciphertext_sha256']:
                raise ValueError('ENCRYPTED_COMPARTMENT_CHANGED')
            context = dict(**base_context, compartment=compartment, shape=list(shape), dtype='<u4')
            data = unseal((private / (compartment + '.key')).read_bytes(), envelope.read_bytes(), context)
            tensor = np.frombuffer(data, dtype='<u4').reshape(shape)
            for region in ('CA1', 'DG'):
                fields[region + '_' + compartment] = tensor[:, :, selected[region]]
            fields['conditions_' + compartment] = np.array([conditions.index(t['condition']) for t in subset])
            fields['orders_' + compartment] = np.array([t['provider_row_index'] for t in subset])
            fields['trial_ids_' + compartment] = np.array([t['trial_id'] for t in subset])
            del tensor, data
        path = root / (sid + '.npz')
        np.savez(path, **fields)
        custodian.protect(path)
        manifest['sessions'].append(dict(mouse_id=animal['mouse_id'], session_id=sid,
                                         file=path.name, sha256=r.sha(path),
                                         unit_ids={region: fields[region + '_unit_ids'].tolist() for region in ('CA1', 'DG')},
                                         trial_ids={compartment: fields['trial_ids_' + compartment].tolist() for compartment in ('A', 'B')}))
    from manifest_validation import validate_manifest
    qc_receipts = {a['session_id']: r.load(r.HERE / 'results/M2/index2/sessions' / (a['session_id'] + '.json'))
                   for a in animals if a['group'] == 'development'}
    validate_manifest(manifest, animals, qc_receipts, r.sha(r.HERE / 'results/M2/aggregate4/gate_result.json'),
                      r.sha(r.HERE / 'development_registration.json'))
    r.save(root / 'manifest.json', manifest, True); custodian.protect(root / 'manifest.json')
    issuer = r.HERE / '.private/development_export_issuer.json'
    r.save(issuer, dict(manifest_sha256=r.sha(root / 'manifest.json'),
                       M2_gate_sha256=manifest['M2_gate_sha256'],
                       development_registration_sha256=manifest['development_registration_sha256'],
                       method_decision_sha256=manifest['method_decision_sha256']), True)
    custodian.protect(issuer)
    print('DEVELOPMENT_AB_EXPORTED_TO_PROTECTED_ROLE_INPUT_ONLY')


if __name__ == '__main__':
    main()
