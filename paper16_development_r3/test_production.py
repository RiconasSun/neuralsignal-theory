"""Synthetic production mathematics, broker, causality and role-boundary tests."""
import copy,ctypes,io,json,math,os,subprocess,sys,time,unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import h5py,numpy as np
from .core import *
from . import features,models,optimizer,source,panels,controls,controller
from paper16_dev_r3.run_m2 import supervise_child

def folder(name):
    path=P/'work/synthetic'/f'{name}_{time.time_ns()}';path.mkdir(parents=True)
    assert path.resolve().is_relative_to((P/'work').resolve())
    return path

def fixture(role='A',u=3):
    starts=np.arange(150,dtype=np.float64)*2+10
    flashes={'start':starts,'stop':starts+.25,'color':np.tile([-1.,1.],75),'main_valid':np.ones(150,bool),'stimulus_valid':np.ones(150,bool)}
    first={'A':0,'B':90,'E':120}[role];rows=np.arange(first,first+6,dtype=np.int64)
    running={'start':np.ravel(starts[rows,None]+np.arange(13)*.02),
        'end':np.ravel(starts[rows,None]+np.arange(13)*.02+.01),
        'net_rotation_promoted':np.linspace(-.1,.1,len(rows)*13),'invalid':np.empty((0,2))}
    trials=[]
    for j,row in enumerate(rows):
        units=[]
        for unit in range(u):
            relative=np.arange(.005,.25,.016+unit*.001+j*.0003)
            units.append(np.sort(np.r_[starts[row]+relative,starts[row]+.1,starts[row]+.22]).astype(np.float64))
        trials.append(units)
    return flashes,running,trials,rows,np.arange(101,101+u,dtype=np.int64)

def batch(role='A',u=3,panel='MAIN'):
    f,r,t,rows,ids=fixture(role,u);return features.build(f,r,t,rows,ids,role,panel)

class ProductionTests(unittest.TestCase):
    def test_cache_integrity_transfer_reservation_and_no_retry(self):
        item={'session_id':123,'size':2*1024**3,'etag':'synthetic'};raw=b'fixture'
        meta={'session_id':123,'source_size':item['size'],'etag':'synthetic','offset':0,'bytes':7,'sha256':hashlib.sha256(raw).hexdigest()}
        source.cache_identity(item,0,7,meta,raw)
        for key,value in [('etag','wrong'),('session_id',124),('sha256','0'*64),('bytes',8)]:
            with self.subTest(key=key),self.assertRaises(AccessStop):source.cache_identity(item,0,7,{**meta,key:value},raw)
        with self.assertRaises(AccessStop):source.cache_identity(item,0,7,meta,b'corrupt')
        self.assertEqual(source.reserve_transport([],item,0,1048576),1048577)
        with self.assertRaises(BudgetStop):source.reserve_transport([],item,0,1048577)
        with self.assertRaises(BudgetStop):source.reserve_transport([{'session_id':123,'offset':1,'reserved_bytes':512*1024**2}],item,0,7)
        with self.assertRaises(BudgetStop):source.reserve_transport([{'session_id':124,'offset':1,'reserved_bytes':8*1024**3}],item,0,7)
        with self.assertRaises(AccessStop):source.reserve_transport([{'session_id':123,'offset':0,'reserved_bytes':8}],item,0,7)

    def test_production_native_B_E_reader_synthetic_canaries_and_source_mismatch(self):
        root=folder('native_roles');path=root/'fixture.h5';sid=9990001
        item={'session_id':sid,'probe_id':7,'source_probe_name':'probeTEST','role':'Development','mouse_id':'9990000'}
        starts=np.arange(150,dtype=np.float64)*2
        flashes={'start':starts,'stop':starts+.25,'color':np.tile([-1.,1.],75),'main_valid':np.ones(150,bool)}
        header={'root_attributes':{'nwb_version':'2.2.2','object_id':'synthetic'},'/session_start_time':'clock','/timestamps_reference_time':'clock','probe_metadata':{}}
        native_rows=[np.array([np.nan]),np.sort(np.ravel(starts[:,None]+[.02,.1,.15,.24])),np.sort(np.ravel(starts[:,None]+[.03,.12,.18,.23]))]
        with h5py.File(path,'w') as f:
            f.attrs['nwb_version']='2.2.2';f.attrs['object_id']='synthetic'
            for key,value in [('identifier',str(sid)),('session_start_time','clock'),('timestamps_reference_time','clock')]:f.create_dataset(key,data=value)
            for prefix in ['/general/devices/','/general/extracellular_ephys/']:
                group=f.require_group(prefix+'probeTEST');group.attrs['probe_id']=7
                header['probe_metadata'][prefix+'probeTEST']={'attributes':{'probe_id':'7'}}
            f.create_dataset('/units/id',data=np.array([100,101,102],dtype=np.int64));f.create_dataset('/units/peak_channel_id',data=np.full(3,42,dtype=np.int64))
            target=f.create_dataset('/units/spike_times',data=np.concatenate(native_rows));index=f.create_dataset('/units/spike_times_index',data=np.cumsum([len(x) for x in native_rows],dtype=np.uint64));index.attrs['target']=target.ref
        qpath=root/'QC.jsonl';qpath.write_text(''.join(json.dumps({'unit_id':uid,'peak_channel_id':42,'full_row_integrity_only':array_id(native_rows[i])})+'\n' for i,uid in [(1,101),(2,102)]),encoding='utf8')
        from paper16_source_r4.neural_reader import REQUIRED,metadata
        with h5py.File(path,'r') as f:native={name:metadata(f[name]) for name in REQUIRED}
        once(root/'NATIVE.json',{'native_objects':native})
        record={'source':item,'selection':{'selected_unit_ids':[101,102],'common_mask':[True]*150},
            'QC':{'path':qpath.relative_to(R).as_posix(),'sha256':sha(qpath)},
            'result':{'path':(root/'NATIVE.json').relative_to(R).as_posix(),'sha256':sha(root/'NATIVE.json')}}
        original_journal=source.CacheReader._journal
        class SyntheticReader(io.BytesIO):
            _journal=staticmethod(original_journal)
            def __init__(self,*args):super().__init__(path.read_bytes())
        stage=load(os.environ['P16_R3_TEST_STAGE'])
        for role,lo,hi in [('B',90,120),('E',120,150)]:
            if role=='E':once(root/role/'results/NONREFIT_COVERAGE_PLAN.json',{item['mouse_id']:{'N3_full_flash_support':True}})
            with patch.object(source,'P',root/role),patch.object(source,'metadata',return_value=(header,flashes,{},{})),patch.object(source,'validate',return_value={}),patch.object(source,'CacheReader',SyntheticReader),patch.object(controller,'require_phase'):
                _,_,trials,rows,units=source.native_role(record,role,stage)
            np.testing.assert_array_equal(rows,np.arange(lo,hi));self.assertEqual(units.tolist(),[101,102])
            for j,row in enumerate(rows):
                self.assertEqual(len(trials[j][0]),3 if role=='B' else 4)
                self.assertTrue(np.all(trials[j][0]>=starts[row]));self.assertTrue(np.all(trials[j][0]<starts[row]+(.22 if role=='B' else .25)))
        with h5py.File(path,'r+') as f:f['/units/spike_times'][len(native_rows[0])+len(native_rows[1])-1]=np.nan
        with patch.object(source,'P',root/'corrupt'),patch.object(source,'metadata',return_value=(header,flashes,{},{})),patch.object(source,'validate',return_value={}),patch.object(source,'CacheReader',SyntheticReader),patch.object(controller,'require_phase'):
            with self.assertRaises(ValueError):source.native_role(record,'B',stage)

    def test_primary_features_match_frozen_spec_and_exact_boundaries(self):
        f,r,t,rows,ids=fixture();b=features.build(f,r,t,rows,ids,'A')
        for j,row in enumerate(rows):
            for k in range(6):
                edge=spec.grid(f['start'][row])[5+k];running,missing=spec.past_rotation(r['start'],r['end'],r['net_rotation_promoted'],edge,r['invalid'])
                previous=None if row==0 else f['color'][row-1];gap=0 if row==0 else f['start'][row]-f['stop'][row-1]
                expected=spec.nuisance(int(f['color'][row]),5+k,previous,gap,int(np.count_nonzero(f['color'][:row]==f['color'][row])),int(row),edge,f['start'][0],running,missing)
                np.testing.assert_array_equal(b.raw[j,k,0,:24],expected)
                np.testing.assert_array_equal(b.raw[j,k,:,24:30],spec.histories(t[j],f['start'][row],5+k))
                np.testing.assert_array_equal(b.raw[j,k,:,30:],dynamics.continuous_features(t[j],f['start'][row],5+k))

    def test_strict_future_current_and_role_reset_no_bin_leakage(self):
        f,r,trials,rows,ids=fixture();original=features.build(f,r,trials,rows,ids,'A')
        changed=copy.deepcopy(trials)
        cutoff=spec.grid(f['start'][rows[0]])[5]
        changed[0]=[np.sort(np.r_[x,cutoff,cutoff+.005,f['start'][rows[0]]-.01]) for x in changed[0]]
        after=features.build(f,r,changed,rows,ids,'A')
        np.testing.assert_array_equal(original.raw[0,0],after.raw[0,0]);np.testing.assert_array_equal(original.raw[1:],after.raw[1:])
        f['main_valid'][0]=False
        out=features.build(f,r,trials,rows,ids,'A');self.assertEqual(out.raw[1,0,0,13],0)
        self.assertEqual(out.raw[1,0,0,12],-1)
        f['stimulus_valid'][0]=False
        out=features.build(f,r,trials,rows,ids,'A');self.assertEqual(out.raw[1,0,0,13],1)
        with self.assertRaises(AccessStop):features.build(f,r,trials,rows,ids,'B')
        for role in ['C','D','Final']:
            with self.assertRaises(AccessStop):features.build(f,r,trials,rows,ids,role)

    def test_previous_stimulus_not_neural_QC_original_index_unknown_and_repetition(self):
        f,r,t,rows,ids=fixture();keep=np.array([0,2,3,4,5]);base=features.build(f,r,[t[i] for i in keep],rows[keep],ids,'A')
        f['main_valid'][1]=False
        support_only=features.build(f,r,[t[i] for i in keep],rows[keep],ids,'A')
        np.testing.assert_array_equal(base.raw,support_only.raw)
        np.testing.assert_array_equal(base.y,support_only.y);np.testing.assert_array_equal(base.score_mask,support_only.score_mask)
        self.assertEqual(support_only.raw[1,0,0,12],f['color'][1])
        f['stimulus_valid'][1]=False
        invalid=features.build(f,r,[t[i] for i in keep],rows[keep],ids,'A')
        np.testing.assert_array_equal(invalid.raw[1,:,:,12:15],np.tile([0.,1.,0.],(6,3,1)))
        np.testing.assert_array_equal(invalid.raw[...,15],base.raw[...,15])
        f['color'][1]=np.nan;f['stimulus_valid']=source.stimulus_validity(f['start'],f['stop'],f['color'],[])
        unknown=features.build(f,r,[t[i] for i in keep],rows[keep],ids,'A');self.assertEqual(unknown.raw[1,0,0,13],1)
        valid=source.stimulus_validity(np.array([0.,2.]),np.array([.25,2.25]),np.array([-1.,1.]),np.array([[.1,.2]]))
        np.testing.assert_array_equal(valid,[False,True])

    def test_all_live_normative_hashes_before_prefit_and_fresh_policy_import(self):
        from . import core
        real_sha=core.sha
        for row in load(P/'BOOTSTRAP.json')['normative_files']:
            for missing in [False,True]:
                def changed(path):
                    if Path(path)==R/row['path']:
                        if missing:raise FileNotFoundError('synthetic missing normative')
                        return '0'*64
                    return real_sha(path)
                with self.subTest(path=row['path'],missing=missing),patch.object(core,'sha',side_effect=changed):
                    with self.assertRaises((ImplementationStop,FileNotFoundError)):core.verify_pins()
                    with self.assertRaises((ImplementationStop,FileNotFoundError)):controller.verify_prefit()
        code="""import hashlib,json
original_hash=hashlib.file_digest
original_json=json.loads
def altered(file,*a,**k):
 if str(file.name).endswith('NUMERICAL_POLICY.json'):raise RuntimeError('DENIED_BEFORE_POLICY_PARSE')
 return original_hash(file,*a,**k)
def parsed(value,*a,**k):
 if b'AD_scaled_coordinate_error_max' in (value if isinstance(value,bytes) else value.encode()):raise AssertionError('POLICY_PARSED_TOO_EARLY')
 return original_json(value,*a,**k)
hashlib.file_digest=altered
json.loads=parsed
import paper16_development_r3.core
"""
        child=subprocess.run([sys.executable,'-B','-c',code],cwd=R,capture_output=True,text=True)
        self.assertNotEqual(child.returncode,0);self.assertIn('DENIED_BEFORE_POLICY_PARSE',child.stderr);self.assertNotIn('POLICY_PARSED_TOO_EARLY',child.stderr)

    def test_S04_both_complementary_panels_empty_mixed_and_denominators(self):
        support=np.array([[True,True,False],[True,True,True]])
        scores={name:np.arange(6,dtype=float).reshape(2,3)+i for i,name in enumerate(MODELS)}
        for missing in [np.zeros((2,3),bool),np.ones((2,3),bool),np.array([[True,False,True],[False,True,False]])]:
            result=controls.running_panels(scores,support,missing,8,.02)
            self.assertEqual(sum(r['actual_valid_unit_bins'] for r in result.values()),40)
            self.assertAlmostEqual(sum(r['score_exposure_seconds_per_unit'] for r in result.values()),.1)
            for name,mask in [('available',support&~missing),('missing',support&missing)]:
                if not mask.any():self.assertIsNone(result[name]['result']);self.assertEqual(result[name]['status'],'EMPTY_NO_SCORABLE_BINS')
                else:self.assertEqual(result[name]['result'],controls.all_effects(scores,mask,8))

    def test_metadata_QC_result_running_identity_fail_before_decode_or_adapter(self):
        root=folder('metadata_identity');sid=123;metadata_path=root/'flash.json';once(metadata_path,{'synthetic':True})
        starts=np.arange(150,dtype=float)*2
        flashes={'start':starts,'stop':starts+.25,'color':np.tile([-1.,1.],75),'main_valid':np.ones(150,bool)}
        flashes['main_valid'][0]=False
        np.savez_compressed(metadata_path.with_suffix('.npz'),**flashes,stimulus_invalid_intervals=np.array([[2.1,2.2]]))
        pins={'metadata_path':'flash.json','metadata_sha256':sha(metadata_path),'flash_array_sha256':sha(metadata_path.with_suffix('.npz'))}
        running={'start':np.array([0.]),'end':np.array([.01]),'net_rotation_promoted':np.array([0.])}
        running_path=root/f'paper16_running_r2/results/{sid}/DERIVED_RUNNING.npz';running_path.parent.mkdir(parents=True)
        np.savez_compressed(running_path,**running)
        identities={k:{'shape':list(v.shape),'dtype':v.dtype.str,'raw_bytes_sha256':hashlib.sha256(v.tobytes()).hexdigest()} for k,v in running.items()}
        once(running_path.with_name('RESULT.json'),{'derived_bundle':{'path':running_path.relative_to(root).as_posix(),'sha256':sha(running_path),'arrays':identities},'frozen_flash_metadata':pins})
        once(root/'source.json',{'source_metadata_pins':pins});(root/'QC.jsonl').write_text('{}\n',encoding='utf8')
        record={'source':{'session_id':sid},'QC':{'path':'QC.jsonl','sha256':sha(root/'QC.jsonl')},'result':{'path':'source.json','sha256':sha(root/'source.json')}}
        compatible={'frozen_metadata_npz':{'sha256':pins['flash_array_sha256']},'original_main_valid':flashes['main_valid'].tolist(),'stimulus_invalid_intervals':[[2.1,2.2]],'stimulus_valid':source.stimulus_validity(starts,starts+.25,flashes['color'],[[2.1,2.2]]).tolist()}
        with patch.object(source,'R',root),patch.object(source,'verify_pins'),patch.object(source,'validate'),patch.object(source,'compatibility',return_value=compatible),patch.object(source,'source_inputs',return_value=({},copy.deepcopy(flashes),running,pins)) as adapter:
            _,actual,_,_=source.metadata(record)
            self.assertTrue(actual['stimulus_valid'][0]);self.assertFalse(actual['main_valid'][0]);self.assertFalse(actual['stimulus_valid'][1])
            for target in [root/'QC.jsonl',root/'source.json',metadata_path,metadata_path.with_suffix('.npz'),running_path]:
                original=target.read_bytes()
                for mode in ['corrupt','missing']:
                    if mode=='corrupt':target.write_bytes(b'corrupted synthetic')
                    else:target.unlink()
                    adapter.reset_mock()
                    with self.subTest(path=str(target),mode=mode),self.assertRaises(AccessStop):source.metadata(record)
                    adapter.assert_not_called();target.write_bytes(original)
            adapter.return_value=({},copy.deepcopy(flashes),running,{**pins,'metadata_sha256':'0'*64})
            with self.assertRaises(AccessStop):source.metadata(record)
        from . import core
        real_sha=core.sha
        for name in ['paper16_m1/code/roster_metadata.py','paper16_m0/metadata/probes.body','paper16_running_r2/results/750749662/RESULT.json']:
            for missing in [False,True]:
                def bad(path):
                    if Path(path)==R/name:
                        if missing:raise FileNotFoundError('synthetic dependency missing')
                        return '0'*64
                    return real_sha(path)
                with patch.object(core,'sha',side_effect=bad),patch.object(source,'source_inputs',side_effect=AssertionError('No decode before pins')):
                    with self.assertRaises((ImplementationStop,FileNotFoundError)):source.metadata(source.admitted()[0])

    def test_actual27_production_metadata_adapter_without_neural_features(self):
        from .phase_gate import compatibility
        rows=source.admitted();self.assertEqual(len(rows),27);present=0
        with patch.object(source,'saved_A',side_effect=AssertionError('No A neural read')),patch.object(source,'native_role',side_effect=AssertionError('No B/E neural read')),patch.object(features,'build',side_effect=AssertionError('No real neural features')):
            for row in rows:
                state=compatibility(row);header,flashes,running,pins=source.metadata(row)
                np.testing.assert_array_equal(flashes['stimulus_valid'],state['stimulus_valid'])
                np.testing.assert_array_equal(flashes['main_valid'],state['original_main_valid'])
                self.assertEqual(pins['flash_array_sha256'],state['frozen_metadata_npz']['sha256'])
                present+=state['stimulus_field_already_present']
        self.assertEqual(present,3)

    def test_compatibility_hash_missing_state_and_wrong_source_fail_before_adapter(self):
        from . import identity,phase_gate
        row=source.admitted()[0];target=R/load(P/'PHASE_A_RESULTS.json')['files'][0]['path'];real_sha=identity.sha
        for missing in [False,True]:
            def changed(path):
                if Path(path)==target:
                    if missing:raise FileNotFoundError('synthetic missing compatibility')
                    return '0'*64
                return real_sha(path)
            with patch.object(identity,'sha',side_effect=changed),patch.object(source,'source_inputs',side_effect=AssertionError('No metadata decode')):
                with self.assertRaises((identity.ProvenanceStop,FileNotFoundError)):source.metadata(row)
        bad=copy.deepcopy(row);bad['source']['session_id']+=1
        with self.assertRaises(identity.ProvenanceStop):phase_gate.compatibility(bad)

    def test_saved_statistics_bootstrap_BO_FC_tamper_missing_and_unexecuted(self):
        from . import reproduce
        names=[a+'-'+b for a,b in CONTRASTS];records=[]
        for i in range(27):
            absolute={m:-.1-(k+1)*(i+1)*.00013 for k,m in enumerate(MODELS)}
            records.append({'mouse_id':str(100+i),'protocol':'BO' if i<5 else 'FC','absolute':absolute,
                'effects':{a+'-'+b:absolute[a]-absolute[b] for a,b in CONTRASTS},'actual_valid_unit_bins':1440-i*8})
        cohort={r['mouse_id']:r['protocol'] for r in records}
        v=np.array([[r['effects'][k] for k in names] for r in records])
        draw=np.random.Generator(np.random.PCG64(16042)).integers(0,27,size=(10000,27))
        summary={'mice':records,'effect_names':names,'equal_mouse_mean':[math.fsum(v[:,k])/27 for k in range(6)],
            'exploratory_whole_mouse_CI95':np.quantile(v[draw].mean(axis=1),[.025,.975],axis=0,method='linear').tolist(),
            'bootstrap_seed':16042,'bootstrap_replicates':10000,'BO_FC':controls.descriptive_groups(records),
            'scope':'EXPLORATORY_DEVELOPMENT_ONLY','Final_gate':'NOT_EXECUTED_FINAL_BOUNDARY'}
        reproduce.verify_statistics(summary,cohort)
        paths=[['exploratory_whole_mouse_CI95',0,0],['bootstrap_seed'],['bootstrap_replicates'],
            ['BO_FC','BO','CI95',0,0],['BO_FC','FC','seed'],['BO_FC','BO','bootstrap_replicates'],
            ['BO_FC','FC','n'],['BO_FC','BO','absolute_model_means','D'],
            ['BO_FC','FC','actual_unit_bins_sum_descriptive_not_inference_n']]
        for path in paths:
            changed=copy.deepcopy(summary);target=changed
            for key in path[:-1]:target=target[key]
            target[path[-1]]+=.123
            with self.subTest(path=path),self.assertRaises(RuntimeError):reproduce.verify_statistics(changed,cohort)
        for path in [['exploratory_whole_mouse_CI95'],['BO_FC'],['BO_FC','FC','CI95'],['BO_FC','BO','mouse_ids']]:
            changed=copy.deepcopy(summary);target=changed
            for key in path[:-1]:target=target[key]
            del target[path[-1]]
            with self.subTest(missing=path),self.assertRaises((RuntimeError,KeyError)):reproduce.verify_statistics(changed,cohort)
        changed=copy.deepcopy(summary);changed['mice'][0]['protocol']='FC'
        with self.assertRaises(RuntimeError):reproduce.verify_statistics(changed,cohort)
        with patch.object(reproduce,'P',folder('unexecuted_saved_results')),patch.object(reproduce,'recompute_statistics',side_effect=AssertionError('No E statistics without E execution')):
            value=reproduce.facts();self.assertNotIn('E_results_recomputed_from_saved_scores_only',value)

    def test_training_only_scaling_active_names_and_nested_objective(self):
        b=batch();scaler=features.Scaling.fit(b);before=copy.deepcopy(scaler)
        e=batch('E');e.raw[...,12:]+=100;_ =scaler.transform(e)
        np.testing.assert_array_equal(before.mean,scaler.mean)
        with self.assertRaises(AccessStop):features.Scaling.fit(e)
        self.assertTrue(np.all(scaler.active[:,:12]));self.assertTrue(np.all(scaler.scale>=.25))
        rng=np.random.Generator(np.random.PCG64(16070))
        for u in range(3):
            obj=models.Objective(b,scaler,'B1',.1,u);x=obj.x0.copy();x[12:]=rng.uniform(-.01,.01,len(x)-12)
            expected=obj.analytic(x)[0]
            for family in ['B2','B3','B4','C']:
                bigger=models.Objective(b,scaler,family,.1,u);theta=bigger.x0.copy()
                for j,local in enumerate(obj.free):theta[np.where(bigger.free==local)[0][0]]=x[j]
                self.assertAlmostEqual(bigger.analytic(theta)[0],expected,places=12)

    def test_all_glm_families_independent_AD_and_fixed_FD(self):
        b=batch();s=features.Scaling.fit(b)
        for model in ['B1','B2','B3','B4','C']:
            obj=models.Objective(b,s,model,.1,0);x=obj.x0.copy();x[12:]=.03
            value,g=obj.analytic(x);dv,ad=obj.AD(x)
            self.assertAlmostEqual(value,dv,places=11);self.assertLessEqual(np.max(np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))),1e-8)
            fd=[]
            for k in range(len(x)):
                plus=x.copy();minus=x.copy();plus[k]+=1e-5;minus[k]-=1e-5
                fd.append((obj.analytic(plus)[0]-obj.analytic(minus)[0])/2e-5)
            np.testing.assert_allclose(g,fd,rtol=0,atol=2e-5)

    def test_full_capacity_DS_packing_independent_AD_and_forward_score(self):
        rng=np.random.Generator(np.random.PCG64(16071));b=batch(u=8)
        b.raw[...,12:]=rng.uniform(-.2,.2,b.raw[...,12:].shape)
        s=features.Scaling.fit(b)
        for mode in ['D','S']:
            obj=models.Objective(b,s,mode,.1,seed=11);self.assertEqual(len(obj.x0),251)
            value,g=obj.analytic(obj.x0);dv,ad=obj.AD(obj.x0)
            self.assertAlmostEqual(value,dv,places=11);np.testing.assert_allclose(g,ad,rtol=0,atol=1e-8)
            scores,prior,means=models.causal_score(obj.expand(obj.x0),obj.X,b.y,b.dt,mode,b.gates)
            frozen=dynamics.objective(obj.expand(obj.x0),obj.X,b.y,b.dt,.1,mode,b.gates,12,True)[2]
            np.testing.assert_allclose(scores,frozen,rtol=0,atol=1e-12)
            changed=b.y.copy();changed[:,2:]+=10
            _,prior2,mean2=models.causal_score(obj.expand(obj.x0),obj.X,changed,b.dt,mode,b.gates)
            np.testing.assert_array_equal(prior[:,:3],prior2[:,:3]);np.testing.assert_array_equal(means[:,:3],mean2[:,:3])

    def test_DS_training_nested_B4_and_scorer_never_calls_smoother(self):
        b=batch(u=2);s=features.Scaling.fit(b)
        for mode in ['D','S']:
            obj=models.Objective(b,s,mode,.1,seed=23);x=obj.x0.copy()
            full=obj.expand(x);u,f=obj.X.shape[-2:];full[u*f:]=0;x=full[obj.free]
            baseline=sum(models.Objective(b,s,'B4',.1,i).analytic(models.Objective(b,s,'B4',.1,i).x0)[0] for i in range(u))/u
            self.assertAlmostEqual(obj.analytic(x)[0],baseline,places=12)
            with patch.object(dynamics,'objective',side_effect=AssertionError('Evaluation smoothing forbidden')):
                self.assertTrue(np.isfinite(obj.score(x,b)).all())

    def test_S07_score_domain_exact_sort_and_main_population_immutable(self):
        b=batch(u=8);original=b.unit_ids.copy();b.y[:]=0
        for u,count in enumerate([36,12,42,18,40,24,38,30]):b.y[0,0,u]=count
        middle,rates=features.middle_rate_units(b)
        np.testing.assert_array_equal(middle,original[[5,7,0,6]]);np.testing.assert_array_equal(b.unit_ids,original)
        b.y[:]=1;middle,_=features.middle_rate_units(b);np.testing.assert_array_equal(middle,original[2:6])
        b.role='E'
        with self.assertRaises(AccessStop):features.middle_rate_units(b)

    def test_N4_all11_raw_maps_frozen_nonzero_scaler_and_targets(self):
        b=batch();s=features.Scaling.fit(b);frozen=copy.deepcopy(s);y=b.y.copy();seen=set()
        for mapping in load(R/'paper16_precision_contract_r1/PRECISION_CONTRACT.json')['N4']['operators']:
            flip,shift=mapping['color_flip'],mapping['time_rotation'];out=features.wrong_map(b,flip,shift)
            seen.add(out[...,:12].tobytes());np.testing.assert_array_equal(out[...,12:22],b.raw[...,12:22]);np.testing.assert_array_equal(out[...,23:],b.raw[...,23:])
            np.testing.assert_array_equal(out[...,22],(-1 if flip else 1)*b.raw[...,22])
            for j,color in enumerate(b.colors):
                for k in range(6):self.assertEqual(np.argmax(out[j,k,0,:12]),int((-color if flip else color)==1)*6+(k+shift)%6)
            changed=replace(b,raw=out);scaled=s.transform(changed)
            np.testing.assert_allclose(scaled[...,22],(out[...,22]-s.mean[:,22])/s.scale[:,22])
        self.assertEqual(len(seen),11);np.testing.assert_array_equal(y,b.y);np.testing.assert_array_equal(frozen.mean,s.mean)
        with self.assertRaises(ImplementationStop):features.wrong_map(b,0,0)

    def test_all_refit_panel_feature_shapes_and_pupil_strict_past(self):
        f,r,t,rows,ids=fixture(u=8)
        for name,b1,columns in [('S01',36,46),('S02',28,38),('S09',26,36)]:
            b=features.build(f,r,t,rows,ids,'A',name);self.assertEqual(b.b1,b1);self.assertEqual(b.raw.shape[-1],columns)
            self.assertEqual(b.y.shape[1],12 if name=='S01' else 6)
        pupil=np.zeros((6,6,2));pupil[...,0]=np.arange(36).reshape(6,6)+1
        for j,row in enumerate(rows):pupil[j,:,1]=spec.grid(f['start'][row])[5:11]-.01
        b=features.build(f,r,t,rows,ids,'A','S05',pupil=pupil,pupil_median=18.)
        self.assertEqual(b.b1,26);self.assertTrue(b.score_mask.all())
        pupil[0,0,1]=spec.grid(f['start'][rows[0]])[5]
        b=features.build(f,r,t,rows,ids,'A','S05',pupil=pupil,pupil_median=18.);self.assertFalse(b.score_mask[0,0])

    def test_N1_joint_donors_preserve_targets_nuisance_and_strata(self):
        b=batch('E');b.ordinals=np.arange(120,132);b.colors=np.tile([-1,1],6)
        b.raw=np.concatenate([b.raw,b.raw+0.01],axis=0);b.y=np.concatenate([b.y,b.y],axis=0)
        rng=controls.rng_for('123','N1');donors=controls.donor_map(b,rng)
        self.assertTrue(np.all(donors!=np.arange(12)));np.testing.assert_array_equal(b.colors[donors],b.colors)
        changed=controls.history_derangement(b,donors)
        np.testing.assert_array_equal(changed.y,b.y);np.testing.assert_array_equal(changed.raw[...,:b.b1],b.raw[...,:b.b1])
        np.testing.assert_array_equal(changed.raw[...,b.b1:],b.raw[donors,...,b.b1:])

    def test_N2_primary_invariance_and_N3_full_flash_counts(self):
        f,r,t,rows,ids=fixture('E');b=features.build(f,r,t,rows,ids,'E')
        jitter=controls.jitter_trials(f,t,rows,controls.rng_for('123','N2'));other=features.build(f,r,jitter,rows,ids,'E')
        np.testing.assert_array_equal(b.y,other.y);np.testing.assert_array_equal(b.raw[...,:30],other.raw[...,:30])
        shifted=controls.shift_trials(f,t,rows,controls.rng_for('123','N3'))
        for j,row in enumerate(rows):
            for u in range(len(ids)):
                self.assertEqual(len(t[j][u]),len(shifted[j][u]));self.assertTrue(np.all((shifted[j][u]>=f['start'][row])&(shifted[j][u]<f['stop'][row])))

    def test_external_counter_denies_before_pair6001_and_iteration1501(self):
        counter=optimizer.Counter();evaluated=0
        for _ in range(6000):counter.value_gradient();evaluated+=1
        with self.assertRaises(BudgetStop):counter.value_gradient();evaluated+=1
        self.assertEqual(evaluated,6000)
        counter=optimizer.Counter()
        for _ in range(1500):counter.accepted()
        with self.assertRaises(BudgetStop):counter.accepted()
        with self.assertRaises(BudgetStop):counter.value_gradient()

    def test_external_actual_client_overcall_denied_before_evaluation6001(self):
        class ConstantObjective:
            x0=np.array([0.]);lo=np.array([-1.]);hi=np.array([1.]);calls=0
            def analytic(self,x):self.calls+=1;return 0.,np.array([0.])
        objective=ConstantObjective();root=folder('external_overcall')/'fit';stage=load(os.environ['P16_R3_TEST_STAGE'])
        original_popen=subprocess.Popen
        code="import json,sys;from pathlib import Path;c=json.loads(Path(sys.argv[1]).read_text());x=c['x0'];\nfor i in range(6001):\n print(json.dumps({'op':'FG','x':x}),flush=True);json.loads(sys.stdin.readline())\n"
        def injected(command,**kwargs):return original_popen([sys.executable,'-c',code,command[-1]],**kwargs)
        with patch.object(optimizer.subprocess,'Popen',side_effect=injected):
            with self.assertRaises(BudgetStop):optimizer.fit(objective,root,stage,{'scope':'SYNTHETIC_EXTERNAL_OVERCLIENT'})
        self.assertEqual(objective.calls,6000);self.assertEqual(load(root/'FAILURE.json')['value_gradient_pairs'],6000)

    def test_external_broker_actual_glm_and_all6_latent_seed_certificates(self):
        from . import reproduce
        b=batch(u=2);s=features.Scaling.fit(b);stage=load(os.environ['P16_R3_TEST_STAGE'])
        specifications=[('B1',None,0)]+[(m,seed,None) for m in ['D','S'] for seed in [11,23,37]]
        for model,seed,unit in specifications:
            obj=models.Objective(b,s,model,.1,unit,seed);path=folder('broker_'+model+'_'+str(seed))/'fit'
            x,report=optimizer.fit(obj,path,stage,{'scope':'SYNTHETIC_ONLY','model':model,'seed':seed})
            self.assertTrue(report['numerical_pass']);self.assertLessEqual(report['projected_gradient_inf'],1e-5)
            diag=load(path/'DIAGNOSTICS.json');self.assertEqual(diag['FD_objective_calls'],24*len(x));self.assertEqual(diag['AD_calls'],3)
            self.assertEqual(diag['analytic_checkpoint_calls'],3)
            self.assertEqual(reproduce.fit(path)['numerical_pass'],True)
            with self.assertRaises(FileExistsError):optimizer.fit(obj,path,stage,{'scope':'SYNTHETIC_ONLY'})

    def test_external_actual_iteration1501_denied_before_acceptance(self):
        class Objective:
            x0=np.array([0.]);lo=np.array([-1.]);hi=np.array([1.])
        root=folder('external_iteration')/'fit';stage=load(os.environ['P16_R3_TEST_STAGE']);original_popen=subprocess.Popen
        code="import json,sys;from pathlib import Path;c=json.loads(Path(sys.argv[1]).read_text());x=c['x0'];\nfor i in range(1501):\n print(json.dumps({'op':'ITER','x':x}),flush=True);json.loads(sys.stdin.readline())\n"
        def injected(command,**kwargs):return original_popen([sys.executable,'-c',code,command[-1]],**kwargs)
        with patch.object(optimizer.subprocess,'Popen',side_effect=injected):
            with self.assertRaises(BudgetStop):optimizer.fit(Objective(),root,stage,{'scope':'SYNTHETIC_ITERATION_OVERCLIENT'})
        self.assertEqual(load(root/'FAILURE.json')['accepted_iterations'],1500)
        self.assertEqual(len(source.CacheReader._journal(root/'ACCEPTED.jsonl')),1500)

    def test_Final_altered_sources_and_pre_gate_roles_denied_before_data(self):
        reg=load(P/'ACCESS_REGISTRATION.json');bad=copy.deepcopy(reg['objects'][0]);bad['session_id']=reg['denied_final_session_ids'][0]
        with patch('requests.Session',side_effect=AssertionError('Must deny before transport')):
            with self.assertRaises(AccessStop):source.CacheReader(bad,load(os.environ['P16_R3_TEST_STAGE']))
        bad=copy.deepcopy(reg['objects'][0]);bad['etag']='wrong'
        with self.assertRaises(AccessStop):source.validate(bad)
        for role in ['C','D','Final']:
            with self.assertRaises(AccessStop):controller.require_phase(role)
        for role in ['A','B','E']:
            with self.assertRaises((AccessStop,FileNotFoundError)):controller.require_phase(role)

    def test_mandatory_task_budget_all_models_seeds_no_optional_failure_relabel(self):
        records=[];panel_map={}
        for i in range(27):
            record={'source':{'mouse_id':str(100+i)},'selection':{'selected_unit_ids':list(range(8))}}
            records.append(record);panel_map[str(100+i)]=[{'panel':p,'status':'AVAILABLE','unit_ids':list(range(4 if p in ['S06','S07'] else 8))} for p in REFIT_PANELS]
        plan=panels.task_plan(records,panel_map);self.assertEqual(plan['optimizer_attempt_count'],7506)
        self.assertEqual(sum(x['model']=='B1' and x['panel']=='MAIN' for x in plan['tasks']),648)
        for i in panel_map:panel_map[i]=[x for x in panel_map[i] if x['panel']!='S05']
        self.assertEqual(panels.task_plan(records,panel_map)['optimizer_attempt_count'],7506-27*30)
        self.assertEqual(plan['Final_reserved'],7722)
        with self.assertRaises(FileNotFoundError):controller.verify_completed(plan['tasks'][:1])

    def test_native_external_wall_job_kills_descendants(self):
        root=folder('wall');pidfile=root/'pids.json';code="import subprocess,sys,time,json;from pathlib import Path;p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);Path(sys.argv[1]).write_text(json.dumps([__import__('os').getpid(),p.pid]));time.sleep(60)"
        result=supervise_child([sys.executable,'-c',code,str(pidfile)],time.monotonic()+1.5,root/'hang.log')
        self.assertTrue(result['killed_at_deadline']);self.assertTrue(result['native_job_tree_enforced']);self.assertTrue(pidfile.exists())
        k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
        k.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];k.WaitForSingleObject.restype=ctypes.c_ulong;k.CloseHandle.argtypes=[ctypes.c_void_p]
        for pid in load(pidfile):
            handle=k.OpenProcess(0x100000,False,pid)
            if handle:
                try:self.assertEqual(k.WaitForSingleObject(handle,0),0)
                finally:k.CloseHandle(handle)

    def test_actual_role_split_fullrow_integrity_and_original_cut_canaries(self):
        f,r,t,rows,ids=fixture('B');spikes=np.sort(np.concatenate([x[0] for x in t]+[np.array([0.,400.])])).astype(float)
        mask=np.ones(150,bool);brows,values=source.split_role(spikes,f,mask,'B');self.assertTrue(np.all((brows>=90)&(brows<120)))
        self.assertTrue(all(np.all((x>=f['start'][row])&(x<f['start'][row]+.22)) for row,x in zip(brows,values)))
        broken=spikes.copy();broken[-1]=np.nan
        with self.assertRaises(ValueError):source.split_role(broken,f,mask,'B')
        with self.assertRaises(AccessStop):source.split_role(spikes,f,mask,'D')

    def test_frozen_value_scope_denies_unregistered_native_dataset(self):
        root=folder('hdf5');path=root/'fixture.h5'
        with h5py.File(path,'w') as f:f.create_dataset('allowed',data=[1.]);f.create_dataset('forbidden',data=[np.nan])
        from paper16_source_r4.neural_reader import value_scope
        with h5py.File(path,'r') as f:
            address=int(h5py.h5o.get_info(f['allowed'].id).addr);reads=[]
            with value_scope(f,{address:('/allowed',[slice(None)])},reads):
                np.testing.assert_array_equal(f['allowed'][:],[1.])
                with self.assertRaises(ValueError):_=f['forbidden'][:]

    def test_missing_or_incomplete_frozen_state_manifest_fail_closed(self):
        with self.assertRaises(FileNotFoundError):controller.validate_m4_freeze({'states':[],'selected_seeds':[]},{'tasks':[]})
        a=np.array([[-1.,1.]]);g=np.array([[-2.,3.]])
        np.testing.assert_array_equal(spec.projected_gradient(a,g,-1,1),g)

if __name__=='__main__':unittest.main(verbosity=2)
