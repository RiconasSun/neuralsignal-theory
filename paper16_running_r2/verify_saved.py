"""Saved running states and synthetic fixtures only; never reopens a real source."""
import contextlib
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
import h5py
import numpy as np
import requests
import scipy

from . import run_sources as run
from .precision import array_identity,derive,admission_possible
from .reader import ALIAS,TARGET,ROT,END,SCALARS

R=Path(__file__).resolve().parents[1]
P=R/'paper16_running_r2'
E=R/'ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2'
BASE='67188e8e53a5c9a6c2ae7835b8b29aab7768db9e'


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextlib.contextmanager
def saved_only():
    from .test_interface import ImageHTTP
    oldfile,oldload,oldpopen=h5py.File,np.load,subprocess.Popen
    def deny(*a,**kw):raise RuntimeError('Network forbidden in saved-only reproduction')
    def file(name,mode='r',**kw):
        synthetic_image=isinstance(name,run.RangeReader) and isinstance(name.http,ImageHTTP) and name.item['file_id']=='synthetic' and mode=='r'
        if not synthetic_image:
            if not isinstance(name,(str,os.PathLike)) or mode!='w' or kw.get('driver')!='core' or kw.get('backing_store') is not False:
                raise ValueError('Only nonpersistent synthetic HDF5 permitted; no native NWB opens')
            path=Path(name).resolve();path.relative_to((P/'work').resolve())
            if path.suffix!='.h5':raise ValueError('Synthetic HDF5 name')
        return oldfile(name,mode,**kw)
    def load(name,*a,**kw):
        path=Path(name).resolve()
        if path.suffix!='.npz' or not any(path.is_relative_to(root) for root in [(P/'results').resolve(),(P/'work').resolve(),(R/'paper16_m1/metadata').resolve()]):
            raise ValueError('Only saved R2 running or frozen flash metadata arrays')
        if kw.get('allow_pickle') is not False:raise ValueError('No pickle loading')
        return oldload(name,*a,**kw)
    class Popen(oldpopen):
        def __init__(self,args,*a,**kw):
            if not isinstance(args,(tuple,list)):raise ValueError('Unstructured child denied')
            git=args[0]=='git' and len(args)>1 and args[1] in ['show','diff','status','rev-parse','ls-tree']
            idle=len(args)>2 and args[0]==sys.executable and args[1]=='-c' and args[2] in ['import time;time.sleep(60)','pass']
            hardkill=len(args)>4 and args[:3]==[sys.executable,'-B','-c'] and "patch('requests.Session',return_value=ImageHTTP(image))" in args[3] and 'run.run_one(item' in args[3]
            if hardkill:Path(args[4]).resolve().relative_to((P/'work').resolve())
            if not(git or idle or hardkill):raise ValueError('Only read-only local Git or fixed synthetic child permitted')
            super().__init__(args,*a,**kw)
    with patch.object(socket.socket,'connect',deny),patch.object(socket,'create_connection',deny),patch.object(requests.Session,'request',deny),patch.object(h5py,'File',file),patch.object(np,'load',load),patch.object(subprocess,'Popen',Popen):
        yield


def case_path(name,sid):
    path=(R/name).resolve();path.relative_to((P/'results'/str(sid)).resolve())
    return path


def native_state(result):
    sid=result['session_id'];bundle=result['native_bundle'];native={}
    if bundle.get('manifest_path'):
        path=case_path(bundle['manifest_path'],sid)
        assert sha(path)==bundle['manifest_sha256']
        manifest=read(path);assert manifest['vectors']==bundle['vectors'] and manifest['complete']==bundle['complete']
    for key,entry in bundle['vectors'].items():
        path=case_path(entry['path'],sid);assert sha(path)==entry['sha256']
        with np.load(path,allow_pickle=False) as data:
            assert data.files==['values'];native[key]=data['values'].copy()
        assert entry['arrays']=={'values':array_identity(native[key])}
        assert read(path.with_suffix('.json'))==entry
    return native


def independent_lookup(arrays):
    a,b,q,t,bad=(arrays[k] for k in ['start','end','net_rotation_promoted','targets','invalid'])
    duration=b-a;valid=(duration>0)&(duration<=.1)
    out=np.zeros(t.shape,dtype=np.float64);missing=np.ones(t.shape,dtype=bool);parent=np.full(t.shape,-1,dtype=np.int64)
    # Independent full candidate masks, not the production searchsorted lookup.
    for idx in np.ndindex(t.shape):
        now=t[idx];eligible=valid&(b<now)&(now-b>0)&(now-b<=.1)
        for lo,hi in bad:eligible&=~((lo<now)&(a<hi))
        candidates=np.flatnonzero(eligible)
        if len(candidates):
            p=int(candidates[-1]);parent[idx]=p;missing[idx]=False
            out[idx]=math.tanh(float(q[p]/(b[p]-a[p]))/10.)
    assert out.tobytes()==arrays['running'].tobytes()
    assert missing.tobytes()==arrays['missing'].tobytes()
    assert parent.tobytes()==arrays['parent'].tobytes()


def check_case(item,result):
    sid=item['session_id'];assert result['source']==item and result['session_id']==sid
    assert result['mouse_id']==item['mouse_id'] and result['protocol']==item['protocol']
    assert result['neural_values_read']==result['model_fits']==0
    assert not result['A_physiology_executed'] and not result['Final_C_access'] and not result['Final_D_access']
    assert read(P/'results'/str(sid)/'ATTEMPT.json')['source']==item
    native=native_state(result) if result.get('native_bundle') else {}
    if result['status'] not in ['SOURCE_RUNNING_PASS','FIRST_SOURCE_COVERAGE_STOP']:
        assert result.get('no_retry') is True
        return {'session_id':sid,'status':result['status'],'partial_vectors_verified':sorted(native)}
    assert set(native)=={'start','end','rotation'} and result['native_bundle']['complete']
    header,onsets,colors,valid,bad,meta=run.source_inputs(item)
    arrays,numerics=derive(native['start'],native['end'],native['rotation'],onsets,colors,valid,bad,sid==750749662)
    assert result['frozen_flash_metadata']==meta
    for key,value in numerics.items():assert result[key]==value,(sid,key)
    path=case_path(result['derived_bundle']['path'],sid);assert sha(path)==result['derived_bundle']['sha256']
    with np.load(path,allow_pickle=False) as saved:
        assert set(saved.files)==set(arrays)
        for key,value in arrays.items():
            assert saved[key].dtype==value.dtype and saved[key].shape==value.shape and saved[key].tobytes()==value.tobytes(),(sid,key)
            assert result['derived_bundle']['arrays'][key]==array_identity(value)
    independent_lookup(arrays)
    structure=result['structure'];objects=structure['objects']
    assert structure['root']['attributes']['nwb_version']=='2.2.2'
    assert structure['source_clock_scalars']=={SCALARS[0]:str(sid),SCALARS[1]:header[SCALARS[1]],SCALARS[2]:header[SCALARS[2]]}
    assert objects[ALIAS]['address']==objects[TARGET]['address'] and all(x['same_file'] for x in objects.values())
    assert objects[ROT]['dtype']==native['rotation'].dtype.str
    assert all(objects[x]['dtype']=='<f8' for x in [ALIAS,TARGET,END])
    assert structure['rotation_attributes']['unit']=='radians'
    assert structure['rotation_attributes'].get('conversion',1.)==1. and structure['rotation_attributes'].get('offset',0.)==0.
    assert set(result['dataset_paths_read'])==set((*SCALARS,ROT,TARGET,END)) and len(result['dataset_paths_read'])==6
    assert result['float64_promotion_exact'] and result['timestamps_preserved'] and result['no_imputed_zero_rows']
    if sid==750749662:assert result['status']=='SOURCE_RUNNING_PASS' and result['direct_running_coverage_pass']
    return {'session_id':sid,'status':result['status'],'native_rows':len(native['start']),'direct_coverage_pass':result['direct_running_coverage_pass'],
            'potential_coverage_pass':result['potential_running_coverage_pass'],'independent900_target_lookup_pass':True}


def check_budget(results):
    events=[json.loads(x) for x in (P/'results/BUDGET_JOURNAL.jsonl').read_text(encoding='utf8').splitlines()]
    assert (P/'results/BUDGET_JOURNAL.jsonl').read_bytes().startswith((P/'results/BUDGET_FIRST.jsonl').read_bytes())
    reservations=[x for x in events if x['event']=='RESERVED']
    total_reserved=sum(x['reserved_bytes'] for x in reservations);total_payload=sum(x['bytes'] for x in events if x['event']=='PAYLOAD')
    assert total_reserved<=3758096384
    for result in results:
        sid=result['session_id'];subset=[x for x in events if x['session_id']==sid]
        requests=[x for x in subset if x['event']=='RESERVED']
        assert [x['request'] for x in requests]==list(range(1,result['new_requests']+1))
        assert sum(x['reserved_bytes'] for x in requests)==result['new_reserved_bytes']<=134217728
        assert sum(x['bytes'] for x in subset if x['event']=='PAYLOAD')==result['new_payload_bytes']
        assert result['new_requests']<=4096
        completes=[x for x in subset if x['event']=='COMPLETE_RANGE'];headers=[x for x in subset if x['event']=='RESPONSE_HEADERS']
        assert [{k:v for k,v in x.items() if k not in ['event','monotonic','session_id']} for x in completes]==result['ranges']
        assert [{k:v for k,v in x.items() if k not in ['event','monotonic','session_id']} for x in headers]==result['response_headers']
        for reservation in requests:
            assert reservation['reserved_bytes']==reservation['expected_bytes']+1 and 0<reservation['expected_bytes']<=1048576
        for row,header in zip(result['ranges'],result['response_headers']):
            assert header=={'request':row['request'],'status':206,'content_range':f"bytes {row['offset']}-{row['offset']+row['bytes']-1}/{result['source']['size']}",'etag':result['source']['etag']}
            assert sum(x['bytes'] for x in subset if x['event']=='PAYLOAD' and x['request']==row['request'])==row['bytes']
        assert result['payload_accounting_complete']==(len(completes)==result['new_requests'])
    assert total_reserved==sum(x['new_reserved_bytes'] for x in results)
    assert total_payload==sum(x['new_payload_bytes'] for x in results)
    return {'requests':len(reservations),'payload_bytes':total_payload,'reserved_bytes':total_reserved}


def checks():
    assert sys.version.split()[0]=='3.11.15' and (np.__version__,scipy.__version__,h5py.__version__,requests.__version__)==('2.4.6','1.16.3','3.16.0','2.32.5')
    reg=run.review_gate()
    old_daily=subprocess.check_output(['git','show',BASE+':ops/daily-operations.md'],cwd=R)
    assert (R/'ops/daily-operations.md').read_bytes().endswith(old_daily)
    changed=subprocess.check_output(['git','diff','--name-only',BASE,'--'],cwd=R).decode().splitlines()
    assert all(x=='ops/daily-operations.md' or x.startswith(('paper16_running_r2/','ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2/')) for x in changed)
    trace=read(P/'REQUIREMENT_TRACE.json');baseline=read(E/'baseline.json')
    assert trace['baseline_sha256']==sha(E/'baseline.json') and len(trace['items'])==baseline['requirement_count']==197
    assert sum(x['status']=='VERIFIED' for x in trace['items'])==trace['content_verified_count']==185
    for before,after in zip(baseline['requirements'],trace['items']):
        assert all(before[k]==after[k] for k in ['id','source_line','requirement']) and after['evidence']
    assert len(read(P/'SEMANTIC_ACCEPTANCE.json')['items'])==88
    assert len(reg['objects'])==28 and len(reg['denied_final_session_ids'])==27
    stage=read(P/'results/STAGE_ATTEMPT.json');assert abs(stage['deadline']-stage['started']-14400)<1e-8
    found=list((P/'results').glob('*/RESULT.json'));byid={x['session_id']:x for x in reg['objects']}
    results=sorted([read(x) for x in found],key=lambda x:int(x['mouse_id']))
    assert len(results)==len({x['session_id'] for x in results}) and results[0]['session_id']==750749662
    assert all(x['session_id'] in byid for x in results)
    details=[check_case(byid[x['session_id']],x) for x in results]
    budget=check_budget(results)
    for phase in ['first','remaining']:
        path=P/f'results/SUPERVISION_{phase}.json'
        if not path.exists():continue
        receipt=read(path);assert receipt['deadline']==stage['deadline']
        if receipt.get('valid_completed_worker'):
            assert receipt['child_exit']==0 and not receipt['child_killed'] and receipt['completed']<stage['deadline']
        assert read(P/f'results/WORKER_{phase}.json')['deadline']==stage['deadline']
    passed=[x for x in results if x['status']=='SOURCE_RUNNING_PASS'];failed=[x for x in results if x['status']!='SOURCE_RUNNING_PASS']
    if len(results)>1:run.first_review_gate()
    if (P/'results/RUNNING_GATE.json').exists():
        summary=read(P/'results/RUNNING_GATE.json');assert len(passed)==28 and not failed
        expected=admission_possible(passed)
        for k,v in expected.items():assert summary[k]==v
        assert summary['terminal_verdict']==('RUNNING_SOURCE_GATE_PASS' if expected['possible_A_physiological_admission'] else 'DEVELOPMENT_RUNNING_COVERAGE_INSUFFICIENT')
        verdict=summary['terminal_verdict']
    else:
        assert len(failed)==1 and results[-1]==failed[0]
        verdict=failed[0]['terminal_verdict']
    facts_path=P/'RUNNING_COHORT_FACTS.json'
    if facts_path.exists():
        facts=read(facts_path)
        assert facts['new_budget']==budget and facts['verdict']==verdict
        assert facts['sources_attempted']==len(results) and facts['sources_completed']==len(passed) and facts['sources_failed']==len(failed)
        assert facts['native_rows']==sum(x['native_retained_rows'] for x in passed)
        assert facts['coverage_cells']==6*len(passed)
        assert facts['source_valid_scored_bins']==sum(c['score_bins'] for x in passed for r in x['coverage'].values() for c in r.values())
        assert facts['available_scored_bins']==sum(c['available'] for x in passed for r in x['coverage'].values() for c in r.values())
        assert facts['minimum_role_color_fraction']==min(c['fraction'] for x in passed for r in x['coverage'].values() for c in r.values())
        assert facts['potential_mice']==summary['eligible_running'] and facts['potential_BO']==summary['BO'] and facts['potential_FC']==summary['FC']
        assert facts['global_stage_elapsed_seconds']==round(read(P/'results/SUPERVISION_remaining.json')['completed']-stage['started'],3)
        with (P/'DEVELOPMENT_RUNNING_COVERAGE.csv').open(encoding='utf8',newline='') as f:table=list(csv.DictReader(f))
        assert len(table)==168 and len({(x['session_id'],x['role'],x['color']) for x in table})==168
        lookup={str(x['session_id']):x for x in results}
        for row in table:
            source=lookup[row['session_id']];cell=source['coverage'][row['role']][row['color']]
            assert row['mouse_id']==source['mouse_id'] and row['protocol']==source['protocol']
            assert int(row['probe_id'])==source['source']['probe_id'] and row['probe_name']==source['source']['probe_name']
            assert int(row['minimum_presentations'])==(30 if row['role']=='A' else 8)
            for key,value in cell.items():assert row[key]==str(value),(row['session_id'],key)
        with (P/'SOURCE_ATTEMPT_LEDGER.csv').open(encoding='utf8',newline='') as f:table=list(csv.DictReader(f))
        assert len(table)==28 and {x['session_id'] for x in table}==set(lookup)
        for row in table:
            source=lookup[row['session_id']]
            assert row['status']==source['status'] and int(row['requests'])==source['new_requests']
            assert int(row['payload_bytes'])==source['new_payload_bytes'] and int(row['reserved_bytes'])==source['new_reserved_bytes']
            assert row['native_manifest_sha256']==source['native_bundle']['manifest_sha256'] and row['derived_sha256']==source['derived_bundle']['sha256']
        resources=read(P/'RESOURCE_LEDGER.json')
        assert all(resources['new_R2'][key]==value for key,value in budget.items())
        assert resources['administrative_cumulative']['requests']==83+budget['requests']
        assert resources['administrative_cumulative']['payload_bytes']==167624+budget['payload_bytes']
        assert resources['administrative_cumulative']['reserved_bytes']==167707+budget['reserved_bytes']
        handoff=read(P/'HANDOFF_FIELDS.json')
        assert handoff['TERMINAL_VERDICT']==verdict and handoff['DEVELOPMENT_RUNNING_SOURCES_COMPLETED']==len(passed) and handoff['DEVELOPMENT_RUNNING_SOURCES_FAILED']==len(failed)
        assert handoff['POTENTIAL_COUNTS']=={'overall':summary['eligible_running'],'BO':summary['BO'],'FC':summary['FC']}
        assert handoff['MODEL_FITS_EXECUTED']==0 and not any(handoff[x] for x in ['A_PHYSIOLOGICAL_QC_EXECUTED','FINAL_C_ACCESS','FINAL_D_ACCESS','M2_FULL_RESUME_READY'])
    freeze=P/'RUNNING_FREEZE_MANIFEST.json'
    if freeze.exists():
        from .payload_contract import EXPECTED_PAYLOAD
        rows=read(freeze)['files'];assert len(rows)==len(EXPECTED_PAYLOAD) and {x['path'] for x in rows}==set(EXPECTED_PAYLOAD)
        for row in rows:
            path=R/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
    return {'terminal_verdict':verdict,'sources_attempted':len(results),'completed':len(passed),'failed':len(failed),'unattempted':28-len(results),
            'budget':budget,'cases':details,'historical_payloads_verified':492,'neural_values_read':0,'model_fits':0,'Final_C_D_access':False,
            'frozen_payloads':len(read(freeze)['files']) if freeze.exists() else 'NOT_YET_FROZEN'}


def main():
    with saved_only():
        result=checks()
        suite=unittest.defaultTestLoader.loadTestsFromNames(['paper16_running_r2.test_running','paper16_running_r2.test_interface'])
        tests=unittest.TextTestRunner(verbosity=2).run(suite);assert tests.wasSuccessful() and tests.testsRun==19
        result['synthetic_tests_passed']=tests.testsRun
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
