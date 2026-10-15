"""Append-only saved-state assembly using the unchanged scientific validator."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'paper12_cseal1'
EVIDENCE = ROOT / 'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1'
PREVIOUS = ROOT / 'ops/evidence/2026-10-14/p12-final-prerelease-controls-1-c-only'
REAL_SOURCE = ROOT / 'paper12_controls1/.private/sealed_C_state'
REAL_DEST = HERE / '.private/sealed_C_recovery_1'
MISSION = 'P12-C-SEAL-HOST-IMPORT-REPAIR-1'

def digest(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def new(path, value):
    with Path(path).open('xb') as f:
        f.write(canonical(value) + b'\n'); f.flush(); os.fsync(f.fileno())

def verify_sources():
    snapshot = read(EVIDENCE / 'host_snapshot.json')
    for name, expected in snapshot['sha256'].items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise PermissionError('HOST_SOURCE_HASH:' + name)
    registration = read(EVIDENCE/'registration.json')
    for name, expected in registration['original_hashes'].items():
        if name == 'paper12_controls1/release_control.py': path = EVIDENCE/'original_release_control.py.bin'
        elif name == 'ops/daily-operations.md': path = EVIDENCE/'daily_at_registration.bin'
        else: path = ROOT/name
        if digest(path.read_bytes()) != expected: raise PermissionError('REGISTERED_ORIGINAL_HASH:' + name)
    anchors = read(EVIDENCE/'source_bindings_r3.json')
    for name, expected in anchors['public_evidence_sha256'].items():
        if digest((ROOT/name).read_bytes()) != expected: raise PermissionError('PUBLIC_EVIDENCE_ANCHOR:' + name)
    inventory = read(PREVIOUS/'partial_seal_inventory.json')['sha256']
    if len(inventory) != 1858 or inventory['complete_states.npz'] != anchors['original_complete_states_sha256']:
        raise PermissionError('ORIGINAL_MODEL_BUNDLE_ANCHOR')
    original = read(EVIDENCE / 'original_implementation_snapshot_v2.json')['sha256']
    for name, expected in original.items():
        path = EVIDENCE / 'original_release_control.py.bin' if name == 'paper12_controls1/release_control.py' else ROOT / name
        if digest(path.read_bytes()) != expected:
            raise PermissionError('ORIGINAL_SOURCE_HASH:' + name)
    old = (EVIDENCE / 'original_release_control.py.bin').read_text(encoding='utf-8')
    current = (ROOT / 'paper12_controls1/release_control.py').read_text(encoding='utf-8')
    replacement = '    if __package__:\n        from .selection_dependency import load_views\n        views=load_views()\n    else:\n        from selection import views'
    if current.replace(replacement, '    from selection import views') != old:
        raise PermissionError('NON_DEPENDENCY_CONTROLLER_CHANGE')
    if 'selection' in sys.modules or any(k.endswith('.calibration') for k in sys.modules):
        raise PermissionError('FRESH_HOST_REQUIRED')
    return snapshot

def protect(path):
    import win32api
    import win32security as ws
    import ntsecuritycon as rights
    path = Path(path)
    if not path.absolute().is_relative_to(HERE) or path.is_symlink() or getattr(path.lstat(), 'st_file_attributes', 0) & 0x400:
        raise PermissionError('PROTECTED_DESTINATION_PATH')
    token = ws.OpenProcessToken(win32api.GetCurrentProcess(), rights.TOKEN_QUERY)
    user = ws.GetTokenInformation(token, ws.TokenUser)[0]
    acl = ws.ACL(); flags = ws.OBJECT_INHERIT_ACE | ws.CONTAINER_INHERIT_ACE if path.is_dir() else 0
    for sid in ('S-1-15-2-1', 'S-1-15-2-2'):
        acl.AddAccessDeniedAceEx(ws.ACL_REVISION, flags, rights.FILE_ALL_ACCESS, ws.ConvertStringSidToSid(sid))
    acl.AddAccessAllowedAceEx(ws.ACL_REVISION, flags, rights.READ_CONTROL, ws.ConvertStringSidToSid('S-1-3-4'))
    for sid in (user, ws.ConvertStringSidToSid('S-1-5-18')):
        acl.AddAccessAllowedAceEx(ws.ACL_REVISION, flags, rights.FILE_ALL_ACCESS, sid)
    ws.SetNamedSecurityInfo(str(path), ws.SE_FILE_OBJECT, ws.DACL_SECURITY_INFORMATION | ws.PROTECTED_DACL_SECURITY_INFORMATION, None, None, acl, None)
    info = ws.GetNamedSecurityInfo(str(path), ws.SE_FILE_OBJECT, ws.DACL_SECURITY_INFORMATION)
    actual = info.GetSecurityDescriptorDacl()
    if not info.GetSecurityDescriptorControl()[0] & ws.SE_DACL_PROTECTED or [actual.GetAce(i) for i in range(actual.GetAceCount())] != [acl.GetAce(i) for i in range(acl.GetAceCount())]:
        raise PermissionError('DESTINATION_ACL_MISMATCH')
    return {'protected': True, 'appcontainer_denied': True, 'custodian_system_only': True}

class SavedOnlyGuard:
    def __init__(self, source, destination, receipt):
        self.source = Path(source).resolve(); self.destination = Path(destination).absolute()
        self.receipt = Path(receipt).absolute()
        self.opens = set(); self.denied = []
    def __call__(self, event, args):
        if event == 'import':
            name = str(args[0])
            if any(x in name for x in ('calibration', 'real_C', 'state_manifest', 'scipy.optimize', 'torch', 'jax')):
                self.denied.append(event + ':' + name); raise PermissionError('SAVED_ONLY_IMPORT_DENIED')
        if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.bind'):
            self.denied.append(event); raise PermissionError('SAVED_ONLY_EXECUTION_DENIED')
        if event != 'open' or isinstance(args[0], int): return
        path = Path(os.fsdecode(args[0])).absolute()
        if path == self.receipt:
            self.opens.add(str(path)); return
        relative = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        lower = '/' + str(relative).lower().replace('\\', '/')
        bundled = path.is_relative_to(self.source) or path.is_relative_to(self.destination)
        prohibited = any(s in lower for s in ('/c_only/', '/ledger', '/d_only/')) or path.suffix.lower() in ('.gcm', '.key', '.nwb', '.npy')
        if path.suffix.lower() == '.npz' and not (bundled and path.name == 'complete_states.npz'): prohibited = True
        if '/.private/' in lower and not bundled: prohibited = True
        if '/jobs/' in lower and not bundled: prohibited = True
        if prohibited:
            self.denied.append(str(path)); raise PermissionError('SAVED_ONLY_INPUT_OR_LEDGER_DENIED')
        self.opens.add(str(path))

def build_manifest(source, destination, inventory, attestation):
    import numpy as np
    from paper12_controls1.release_control import safe, validate_state_manifest
    source = Path(source); destination = Path(destination)
    # Atomic namespace consumption; failure/crash leaves the reservation intact.
    destination.mkdir(exist_ok=False)
    acl = protect(destination)
    new(destination / 'reservation.json', {'mission': MISSION, 'source_inventory_sha256': digest(canonical(inventory)), 'utc': datetime.now(timezone.utc).isoformat()})
    files = {p.name for p in source.iterdir() if p.is_file()}
    if not set(inventory) <= files: raise PermissionError('SAVED_BUNDLE_INCOMPLETE')
    artifacts = {}
    for name, expected in inventory.items():
        if Path(name).name != name: raise PermissionError('SAVED_PATH_INVALID')
        raw = safe(source, source / name).read_bytes()
        if digest(raw) != expected: raise PermissionError('ORIGINAL_SAVED_HASH:' + name)
        with (destination / name).open('xb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        protect(destination / name)
        artifacts[name] = digest((destination / name).read_bytes())
        if artifacts[name] != expected: raise PermissionError('COPY_HASH')
    inputs = read(destination / 'provenance_input_manifest.json')
    report = read(destination / 'provenance_calibration_states.json')
    roster = read(destination / 'provenance_roster.json')
    cases = []; seeds = {}
    with np.load(destination / 'complete_states.npz', allow_pickle=False) as arrays:
        for row in report['cases']:
            case = row['case']; models = {}
            for label in row['models']:
                name = case + '_' + label + '.json'
                value = dict(row['arrays'][label]); value['certificate_sha256'] = artifacts[name]; models[label] = value
            mean = arrays[case + '_mean']; scale = arrays[case + '_scale']
            cases.append({'case':case, 'mouse_id':row['mouse_id'], 'session_id':row['session_id'], 'region':row['region'], 'view':row['view'], 'unit_ids':row['unit_ids'], 'selection':row['selection'], 'trial_ids':row['C_trial_ids'], 'trial_mask_sha256':digest(canonical(row['C_trial_ids'])), 'mean_key':case+'_mean', 'scale_key':case+'_scale', 'scaler_sha256':digest(np.ascontiguousarray(mean).tobytes()+np.ascontiguousarray(scale).tobytes()), 'models':models})
            if row['view'] == 'primary':
                prefix = row['session_id'] + '_' + row['region']
                for seed in ('11','23','37','mean'):
                    name = prefix + ('_N_mean' if seed == 'mean' else '_N_seed'+seed) + '.json'; cert = read(destination/name)
                    key = case+'_N' if seed == 'mean' else prefix+'_N_seed'+seed
                    seeds[row['mouse_id']+'_'+row['region']+'_'+seed] = {'file':name, 'sha256':artifacts[name], 'original_PG':cert['original_PG'], 'AD_error':cert['AD_scaled_error'], 'array_key':key, 'array_sha256':digest(np.ascontiguousarray(arrays[key]).tobytes())}
    new(destination / 'recovery_attestation.json', attestation)
    artifacts['recovery_attestation.json'] = digest((destination/'recovery_attestation.json').read_bytes())
    manifest = {'version':2, 'cohort':[s['mouse_id'] for s in inputs['sessions']], 'cases':cases, 'expected_cases':[[s['mouse_id'],r,v] for s in roster['sessions'] for v in s['views'] for r in ('CA1','DG')], 'seed_certificates':seeds, 'coverage':roster['paired_counts'], 'synthetic':inputs['synthetic'], 'artifact_sha256':artifacts}
    validate_state_manifest(manifest, destination)
    if not manifest['synthetic']: verify_real_counts(manifest, destination)
    new(destination / 'C_state_manifest.json', manifest)
    receipt = {'mission':MISSION, 'COMPLETE_C_SEAL_PASS':True, 'C_manifest_sha256':digest(canonical(manifest)), 'C_manifest_file_sha256':digest((destination/'C_state_manifest.json').read_bytes()), 'original_artifacts':len(inventory), 'original_files_preserved':True, 'cases':len(cases), 'cohort':manifest['cohort'], 'seed_certificates':len(seeds), 'coverage':manifest['coverage'], 'ACL':acl, 'new_fits':0, 'raw_neural_arrays_opened':0, 'D_RELEASE_CONSUMED':False, 'D_EVALUATION_EXECUTED':False}
    new(destination / 'C_sealing_receipt.json', receipt)
    for name in ('reservation.json','recovery_attestation.json','C_state_manifest.json','C_sealing_receipt.json'): protect(destination/name)
    return receipt

def verify_real_counts(manifest, bundle):
    counts = {'mice':len(manifest['cohort']), 'subfields':len({(c['mouse_id'],c['region']) for c in manifest['cases']}), 'cases':len(manifest['cases']), 'GLM_fits':0, 'N_seed_fits':sum(not k.endswith('_mean') for k in manifest['seed_certificates']), 'N_mean_certificates':sum(k.endswith('_mean') for k in manifest['seed_certificates']), 'unit_endpoint_certificates':0}
    for case in manifest['cases']:
        for label in case['models']:
            cert = read(bundle/(case['case']+'_'+label+'.json'))
            rows = cert.get('certificates' if cert.get('reused') else 'records', [])
            counts['unit_endpoint_certificates'] += len(rows)
            if not cert.get('reused'): counts['GLM_fits'] += len(rows)
    if counts != read(EVIDENCE/'registration.json')['expected_real']: raise PermissionError('REAL_COMPLETE_COUNTS_MISMATCH')
    identity = read(bundle/'provenance_identity.json')
    expected = read(PREVIOUS/'execution_source_binding.json')
    if identity['source_code_sha256'] != expected['source_files']: raise PermissionError('ORIGINAL_WORKER_SOURCE_IDENTITY')
    frozen = read(ROOT/'paper12_controls1/prospective_registration.json')['source_sha256']
    if identity['frozen_source_sha256'] != frozen: raise PermissionError('ORIGINAL_SCIENTIFIC_SOURCE_IDENTITY')
    runtime = read(ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256']
    if identity['runtime_sha256'] != runtime: raise PermissionError('ORIGINAL_RUNTIME_IDENTITY')
    if identity['sealer_sha256'] != digest((EVIDENCE/'original_state_manifest.py.bin').read_bytes()): raise PermissionError('ORIGINAL_SEALER_IDENTITY')
    return counts

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--synthetic', action='store_true'); parser.add_argument('--source'); parser.add_argument('--destination'); parser.add_argument('--inventory'); parser.add_argument('--check', action='store_true'); parser.add_argument('--probe'); parser.add_argument('--receipt', required=True)
    args = parser.parse_args(); snapshot = verify_sources()
    import numpy as np
    from paper12_controls1.release_control import validate_state_manifest
    # Preload only cryptography/numpy/Windows ACL support before installing the I/O audit.
    import win32api, win32security, ntsecuritycon
    if args.synthetic:
        source = Path(args.source).resolve(); destination = Path(args.destination).absolute() if args.destination else source
        if not source.is_relative_to(HERE/'jobs'): raise PermissionError('SYNTHETIC_TEST_ROOT')
        inventory = read(args.inventory) if args.inventory else None
        if read(source/'provenance_input_manifest.json')['synthetic'] is not True: raise PermissionError('SYNTHETIC_REAL_CONFUSION')
        approval = None
    else:
        if args.source or args.destination or args.inventory or args.probe: raise PermissionError('FIXED_REAL_PATHS_REQUIRED')
        source = REAL_DEST if args.check else REAL_SOURCE; destination = REAL_DEST
        approval = read(EVIDENCE/'engineering_gate.json')
        if approval['decision'] != 'APPROVED_SAVED_ONLY_RECOVERY' or approval['host_snapshot_sha256'] != digest((EVIDENCE/'host_snapshot.json').read_bytes()): raise PermissionError('INDEPENDENT_GATE_REQUIRED')
        for role in ('engineering','scientific'):
            if digest((EVIDENCE/approval[role]['file']).read_bytes()) != approval[role]['sha256']: raise PermissionError('INDEPENDENT_REVIEW_HASH')
        test_path = EVIDENCE/approval['synthetic_tests']['file']
        if digest(test_path.read_bytes()) != approval['synthetic_tests']['sha256']: raise PermissionError('SYNTHETIC_REVIEW_BINDING')
        tests = read(test_path)
        if tests['passed'] is not True or tests['host_snapshot_sha256'] != approval['host_snapshot_sha256']: raise PermissionError('SYNTHETIC_GATES_REQUIRED')
        inventory = read(PREVIOUS/'partial_seal_inventory.json')['sha256']
        if not args.check:
            new(EVIDENCE/'real_recovery_attempt.json', {'mission':MISSION,'utc':datetime.now(timezone.utc).isoformat(),'engineering_gate_sha256':digest((EVIDENCE/'engineering_gate.json').read_bytes()),'source':str(source.relative_to(ROOT)),'destination':str(destination.relative_to(ROOT)),'one_attempt_no_retry':True})
            destination.parent.mkdir(exist_ok=True)
            protect(destination.parent)
    receipt = Path(args.receipt).absolute()
    if not receipt.is_relative_to(HERE/'jobs' if args.synthetic else EVIDENCE): raise PermissionError('RECEIPT_PATH')
    guard = SavedOnlyGuard(source,destination,receipt); sys.addaudithook(guard)
    if args.probe:
        if args.probe.startswith('import:'): __import__(args.probe[7:])
        else: Path(args.probe).read_bytes()
        raise AssertionError('PROBE_WAS_NOT_DENIED')
    if args.check:
        manifest = read(source/'C_state_manifest.json'); validate_state_manifest(manifest,source)
        result = read(source/'C_sealing_receipt.json')
        if digest(canonical(manifest)) != result['C_manifest_sha256']: raise PermissionError('RECEIPT_MANIFEST_MISMATCH')
        if not args.synthetic: result['verified_counts'] = verify_real_counts(manifest,source)
    else:
        result = build_manifest(source,destination,inventory,{'mission':MISSION,'host_snapshot_sha256':digest((EVIDENCE/'host_snapshot.json').read_bytes()),'original_snapshot_sha256':'dc48694e8c42843bc8923660d38dc5cc816eff9b2ebefe9bd2f6b36c33ef13d7','original_provenance_preserved':True,'saved_only':True,'synthetic':args.synthetic,'engineering_gate':approval})
    result.update({'fresh_selection_cache_empty_at_start':True,'audit_open_paths':sorted(guard.opens),'audit_denied':guard.denied,'optimizer_imports':0,'raw_C_D_input_reads':0,'ledger_opens':0,'host_snapshot_sha256':digest((EVIDENCE/'host_snapshot.json').read_bytes())})
    new(args.receipt,result); print(json.dumps({'passed':True,'cases':result['cases'],'saved_only':True}))

if __name__ == '__main__':
    try: main()
    except BaseException:
        traceback.print_exc(); sys.exit(1)
