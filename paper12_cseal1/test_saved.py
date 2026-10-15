"""Registered fresh-process saved-synthetic tests; no fits or raw input loading."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from . import host as h

def run_suite():
    h.verify_sources()
    stamp = str(time.time_ns()); work = h.HERE/'jobs'/('synthetic_'+stamp); work.mkdir(parents=True)
    rows = []; logs = work/'logs'; logs.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1'); env.pop('PYTHONPATH', None)
    old = h.ROOT/'paper12_controls1/jobs/saved_v2_9546086888504515998/exports/saved'
    manifest = h.read(old/'C_state_manifest.json')
    assert manifest['synthetic'] is True
    source = work/'retro'; source.mkdir()
    inventory = manifest['artifact_sha256']
    for name, expected in inventory.items():
        raw = (old/name).read_bytes(); assert h.digest(raw) == expected
        (source/name).write_bytes(raw)
    inv = work/'inventory.json'; h.new(inv,inventory)
    def command(src=source, dst=None, check=False, inventory_file=inv, root=h.ROOT, probe=None):
        args = [sys.executable,'-B','-m','paper12_cseal1.host','--synthetic','--source',str(src),'--receipt',str(logs/(str(time.time_ns())+'.json'))]
        if dst is not None: args += ['--destination',str(dst)]
        if check: args += ['--check']
        else: args += ['--inventory',str(inventory_file)]
        if probe: args += ['--probe',probe]
        return args
    def execute(name, args, passed=True, token=None, root=h.ROOT):
        result = subprocess.run(args,cwd=root,env=env,capture_output=True,text=True,timeout=120)
        log = {'name':name,'command':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'expected_success':passed,'expected_denial':token,'fresh_process':True}
        h.new(logs/(name+'.json'),log)
        ok = (result.returncode==0) == passed and (token is None or token in result.stderr)
        rows.append({'test':name,'passed':ok,'exit_code':result.returncode,'evidence':str((logs/(name+'.json')).relative_to(h.ROOT))})
        if not ok: raise AssertionError(name+':'+result.stderr[-1800:])
        return result
    # Genuine original retrospective label stays untouched.
    retro = work/'sealed_retro'
    execute('retrospective_saved_reconstruction',command(dst=retro))
    execute('complete_manifest_readback',command(src=retro,check=True))
    # Synthetic prospective fixture is metadata-only and explicitly test-labelled.
    prospective = work/'prospective'; shutil.copytree(source,prospective)
    roster = h.read(prospective/'provenance_roster.json'); assert roster['registration']=='RETROSPECTIVE_SAVED_SYNTHETIC'
    roster['registration']='PROSPECTIVE_BEFORE_ANY_OPTIMIZER'
    roster['test_fixture_notice']='SYNTHETIC_ONLY: prospective seal-request metadata, no prospective claim about historical fits'
    (prospective/'provenance_roster.json').write_bytes(h.canonical(roster)+b'\n')
    pinv = dict(inventory); pinv['provenance_roster.json']=h.digest((prospective/'provenance_roster.json').read_bytes())
    pinvfile=work/'prospective_inventory.json';h.new(pinvfile,pinv)
    execute('prospective_roster_saved_path',command(src=prospective,dst=work/'sealed_prospective',inventory_file=pinvfile))
    execute('repeat_destination_denied',command(dst=retro),False,'FileExistsError')
    target=work/'concurrent'; args1=command(dst=target);args2=command(dst=target)
    a=subprocess.Popen(args1,cwd=h.ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    b=subprocess.Popen(args2,cwd=h.ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    outputa=a.communicate(timeout=120);outputb=b.communicate(timeout=120)
    assert sorted([a.returncode,b.returncode])==[0,1]
    h.new(logs/'concurrent.json',{'commands':[args1,args2],'exit_codes':[a.returncode,b.returncode],'outputs':[outputa,outputb],'one_winner':True})
    rows.append({'test':'concurrent_single_winner','passed':True,'evidence':str((logs/'concurrent.json').relative_to(h.ROOT))})
    # Real interruption: terminate an actual child after namespace reservation, before manifest.
    crashdst=work/'interrupted';crashargs=command(dst=crashdst)
    child=subprocess.Popen(crashargs,cwd=h.ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    deadline=time.monotonic()+15
    while not (crashdst/'reservation.json').exists() and child.poll() is None and time.monotonic()<deadline: time.sleep(.001)
    assert (crashdst/'reservation.json').exists();child.kill();out=child.communicate(timeout=20)
    assert not (crashdst/'C_state_manifest.json').exists()
    h.new(logs/'interrupted.json',{'command':crashargs,'exit_code':child.returncode,'outputs':out,'reservation_retained':True,'manifest_absent':True})
    rows.append({'test':'actual_process_interruption','passed':True,'evidence':str((logs/'interrupted.json').relative_to(h.ROOT))})
    execute('interrupted_destination_retry_denied',command(dst=crashdst),False,'FileExistsError')
    # Check-only mutations stay inside synthetic test copies.
    damaged=work/'damaged';shutil.copytree(retro,damaged)
    original_manifest=(damaged/'C_state_manifest.json').read_bytes()
    for name, mutate, expected in [
        ('incomplete_manifest',lambda m:m.pop('cases'),'COMPLETE_C_SCHEMA'),
        ('incomplete_case_roster',lambda m:m['cases'].pop(),'COMPLETE_C_CASE_ROSTER'),
        ('missing_seed_state',lambda m:m['seed_certificates'].pop(next(iter(m['seed_certificates']))),'COMPLETE_C_N_SEEDS'),
        ('insufficient_coverage',lambda m:m['coverage'].update(primary=7),'COMPLETE_C_COVERAGE'),
        ('wrong_model_shape',lambda m:next(iter(m['cases'][0]['models'].values())).update(shape=[1,39]),'COMPLETE_C_MODEL_SHAPE'),
        ('trial_mask_tamper',lambda m:m['cases'][0]['trial_ids'].append(-7),'C_CASE_PREFIT_ROSTER_MISMATCH'),
    ]:
        value=json.loads(original_manifest);mutate(value);(damaged/'C_state_manifest.json').write_bytes(h.canonical(value))
        execute(name,command(src=damaged,check=True),False,expected)
    (damaged/'C_state_manifest.json').write_bytes(original_manifest)
    for name, artifact in [('corrupt_model_bundle','complete_states.npz'),('corrupt_roster','provenance_roster.json'),('corrupt_QC','provenance_QC.json'),('corrupt_journal','attempt_journals.zip'),('corrupt_certificate',manifest['cases'][0]['case']+'_O.json')]:
        path=damaged/artifact;raw=path.read_bytes();path.write_bytes(raw+b'corrupt')
        execute(name,command(src=damaged,check=True),False,'C_ARTIFACT_HASH');path.write_bytes(raw)
    missing=work/'missing';shutil.copytree(source,missing);(missing/'complete_states.npz').unlink()
    execute('missing_saved_state_no_reconstruction',command(src=missing,dst=work/'missing_destination'),False,'SAVED_BUNDLE_INCOMPLETE')
    wrong=dict(inventory);wrong['complete_states.npz']='0'*64;wi=work/'wrong_inventory.json';h.new(wi,wrong)
    execute('incorrect_original_output_hash',command(dst=work/'wrong_output',inventory_file=wi),False,'ORIGINAL_SAVED_HASH')
    for name, probe, expected in [
        ('raw_C_input_denied',str(work/'C_only/counts.npz'),'SAVED_ONLY_INPUT_OR_LEDGER_DENIED'),
        ('raw_D_input_denied',str(work/'D_only/counts.npz'),'SAVED_ONLY_INPUT_OR_LEDGER_DENIED'),
        ('D_key_denied',str(work/'D.key'),'SAVED_ONLY_INPUT_OR_LEDGER_DENIED'),
        ('encrypted_D_denied',str(work/'D.gcm'),'SAVED_ONLY_INPUT_OR_LEDGER_DENIED'),
        ('neural_source_denied',str(work/'neural.nwb'),'SAVED_ONLY_INPUT_OR_LEDGER_DENIED'),
        ('ledger_access_denied',str(work/'ledger.json'),'SAVED_ONLY_INPUT_OR_LEDGER_DENIED'),
        ('calibration_import_denied','import:paper12_controls1.calibration','SAVED_ONLY_IMPORT_DENIED'),
        ('optimizer_import_denied','import:scipy.optimize','SAVED_ONLY_IMPORT_DENIED'),
    ]:
        if not probe.startswith('import:'):
            Path(probe).parent.mkdir(exist_ok=True);Path(probe).write_bytes(b'SYNTHETIC_CANARY')
        execute(name,command(probe=probe),False,expected)
        if not probe.startswith('import:'): assert Path(probe).read_bytes() == b'SYNTHETIC_CANARY'
    # Independent copied repository for dependency/import mutations. No real-state paths copied.
    isolated=work/'isolated_repo';isolated.mkdir()
    files=set(h.read(h.EVIDENCE/'original_implementation_snapshot_v2.json')['sha256'])|set(h.read(h.EVIDENCE/'host_snapshot.json')['sha256'])
    files |= set(h.read(h.EVIDENCE/'registration.json')['original_hashes'])
    files |= set(h.read(h.EVIDENCE/'source_bindings_r3.json')['public_evidence_sha256'])
    for path in h.EVIDENCE.iterdir():
        if path.is_file():files.add(str(path.relative_to(h.ROOT)))
    for name in files:
        dest=isolated/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(h.ROOT/name,dest)
    isource=isolated/'paper12_cseal1/jobs/source';shutil.copytree(source,isource)
    iinv=isolated/'paper12_cseal1/jobs/inventory.json';h.new(iinv,inventory)
    def isolated_cmd():
        return [sys.executable,'-B','-m','paper12_cseal1.host','--synthetic','--source',str(isource),'--destination',str(isolated/'paper12_cseal1/jobs/dest'),'--inventory',str(iinv),'--receipt',str(isolated/'paper12_cseal1/jobs/receipt.json')]
    public_inventory=isolated/h.PREVIOUS.relative_to(h.ROOT)/'partial_seal_inventory.json'
    public_raw=public_inventory.read_bytes();public_inventory.write_bytes(public_raw+b' ')
    execute('registered_original_inventory_anchor_drift',isolated_cmd(),False,'REGISTERED_ORIGINAL_HASH',isolated)
    public_inventory.write_bytes(public_raw)
    selection=isolated/'paper12_predictive_v2/selection.py';selectionraw=selection.read_bytes()
    helper=isolated/'paper12_controls1/selection_dependency.py';helperraw=helper.read_bytes()
    hostpath=isolated/'paper12_cseal1/host.py';hostraw=hostpath.read_bytes()
    snapfile=isolated/h.EVIDENCE.relative_to(h.ROOT)/'host_snapshot.json';snapraw=snapfile.read_bytes()
    for name, path, change, expected in [
        ('missing_selection',selection,None,'FileNotFoundError'),
        ('corrupt_selection',selection,selectionraw+b'\n# changed','HOST_SOURCE_HASH'),
        ('missing_helper',helper,None,'FileNotFoundError'),
        ('corrupt_helper',helper,helperraw+b'\n# changed','HOST_SOURCE_HASH'),
        ('corrupt_host_source',hostpath,hostraw+b'\n# changed','HOST_SOURCE_HASH'),
    ]:
        raw=path.read_bytes()
        if change is None:path.unlink()
        else:path.write_bytes(change)
        execute(name,isolated_cmd(),False,expected,isolated);path.write_bytes(raw)
    # Authenticate a test-only changed helper, then demonstrate its dependency verifier fails.
    helper.write_bytes(helperraw.replace(h.SHA_SELECTION.encode() if hasattr(h,'SHA_SELECTION') else b'9a36e1c29ca9acc2e6b4e8534489c8730f68d3db313ab8b2fc2b40a1930d9d4e',b'0'*64))
    snap=json.loads(snapraw);snap['sha256']['paper12_controls1/selection_dependency.py']=h.digest(helper.read_bytes());snapfile.write_bytes(h.canonical(snap))
    execute('pinned_dependency_hash_denied',isolated_cmd(),False,'SELECTION_VERSION_HASH_MISMATCH',isolated)
    helper.write_bytes(helperraw);snapfile.write_bytes(snapraw)
    # A loader that raises after authentication must not fall back to ambient selection.
    helper.write_bytes(helperraw+b'\nraise ImportError("INJECTED_IMPORT_FAILURE")\n')
    snap=json.loads(snapraw);snap['sha256']['paper12_controls1/selection_dependency.py']=h.digest(helper.read_bytes());snapfile.write_bytes(h.canonical(snap))
    # Previous failed seal reservation cannot be reused: choose another fresh namespace.
    def failcmd():
        args=isolated_cmd();args[args.index('--destination')+1]=str(isolated/'paper12_cseal1/jobs/import_failure');return args
    execute('authenticated_import_failure_no_fallback',failcmd(),False,'INJECTED_IMPORT_FAILURE',isolated)
    helper.write_bytes(helperraw);snapfile.write_bytes(snapraw)
    # Dependency loader itself is tested fresh and without manifest shortcuts.
    selection.unlink()
    execute('loader_missing_selection', [sys.executable,'-B','-c','from paper12_controls1.selection_dependency import load_views; load_views()'],False,'FileNotFoundError',isolated)
    selection.write_bytes(selectionraw+b'\n# corrupt')
    execute('loader_corrupt_selection',[sys.executable,'-B','-c','from paper12_controls1.selection_dependency import load_views; load_views()'],False,'SELECTION_VERSION_HASH_MISMATCH',isolated)
    selection.write_bytes(selectionraw)
    execute('fresh_loader_no_module_cache',[sys.executable,'-B','-c','import sys; assert "selection" not in sys.modules; from paper12_controls1.selection_dependency import load_views; assert callable(load_views()); assert "selection" not in sys.modules; assert "paper12_predictive_v2.selection" not in sys.modules'],True,root=isolated)
    # Exact old-source byte parity proves Controller, signatures and durable ledger unchanged.
    h.verify_sources();rows.append({'test':'controller_all_non_dependency_bytes_unchanged','passed':True,'evidence':'original_release_control.py.bin + host.verify_sources'})
    assert h.read(source/'provenance_roster.json')['registration']=='RETROSPECTIVE_SAVED_SYNTHETIC'
    assert {n:h.digest((old/n).read_bytes()) for n in inventory}==inventory
    rows.append({'test':'original_synthetic_saved_artifacts_unchanged','passed':True,'evidence':'original saved manifest artifact hashes rechecked'})
    result={'mission':h.MISSION,'utc':time.time(),'host_snapshot_sha256':h.digest((h.EVIDENCE/'host_snapshot.json').read_bytes()),'passed':all(r['passed'] for r in rows),'tests':rows,'count':len(rows),'work':str(work.relative_to(h.ROOT)),'new_model_fits':0,'real_saved_state_access':False,'raw_neural_array_reads':0,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'ledger_semantics_unchanged':True,'ledger_accesses':0}
    h.new(h.EVIDENCE/('synthetic_attempt_'+stamp+'.json'),result)
    print(json.dumps({'passed':result['passed'],'tests':len(rows),'work':result['work']}))

if __name__=='__main__':run_suite()
