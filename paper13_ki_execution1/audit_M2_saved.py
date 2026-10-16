"""Independent saved A/C QC/count reconstruction; no source/network imports."""
import hashlib
import json
from pathlib import Path
import numpy as np

P=Path(__file__).resolve().parent
ROOT=P.parent


def read(path):return json.loads(path.read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    gate=read(P/'results/M2_GATE.json');allocation=read(P/'EPOCH_UNIT_ALLOCATION.json')['records']
    assert gate['M2']=='PASS' and len(gate['all19_candidates'])==19
    assigned={r['mouse_id']:r for r in allocation};attempts=0;passes=0;selected=0;unit_bins=0
    for saved in gate['all19_candidates']:
        record=assigned[saved['mouse_id']]
        assert saved['role']==record['role'] and saved['partition']==record['QC_partition'] and not saved['B_E_D_exported']
        path=P/'results/qc'/(saved['mouse_id']+'.json')
        assert read(path)==saved
        journal=read_lines(path.with_name(path.stem+'.attempts.jsonl'))
        assert journal[0]['event']=='MOUSE_START' and journal[-1]['event']=='MOUSE_COMPLETE'
        assert journal[-1]['result_sha256']==sha(path)
        complete=[r for r in journal if r['event']=='UNIT_COMPLETE'];starts=[r for r in journal if r['event']=='UNIT_START']
        assert len(complete)==len(starts)==len(saved['attempts'])
        good=[]
        for index,result in enumerate(saved['attempts']):
            expected=record['PL_units_numeric_order'][index]
            assert all(result[k]==expected[k] for k in ['unit_id','row','label','electrode_row'])
            assert starts[index]['unit_id']==complete[index]['unit_id']==result['unit_id']
            assert complete[index]['QC']=={k:v for k,v in result.items() if k not in ['unit_id','row','electrode_row','label','partition']}
            n=result['training_spikes'];ni=result['within_epoch_ISIs'];bad=result['refractory_ISIs'];occupied=result['occupied_epochs']
            frac=bad/ni if ni else None
            expected_pass=n>=50 and ni>=30 and occupied>=12 and .1<=n/180<=100 and frac is not None and frac<=.01
            assert result['pass']==expected_pass and result['rate_hz']==n/180 and result['refractory_fraction']==frac
            attempts+=1;passes+=result['pass']
            if result['pass']:good.append(expected)
        assert saved['selected_units']==good[:8] and saved['eligible']==(len(good)>=8)
        state_path=ROOT/saved['training_state_file']
        assert sha(state_path)==saved['training_state_sha256']==journal[-1]['training_state_sha256']
        with np.load(state_path,allow_pickle=False) as state:
            assert set(state.files)=={'counts','unit_ids'}|{f'unit{j}_{part}' for j in range(8) for part in ['times','ends']}
            assert state['unit_ids'].tolist()==[u['unit_id'] for u in good[:8]]
            assert state['counts'].shape==(60,30,8)
            for j,unit in enumerate(good[:8]):
                times=state[f'unit{j}_times'];ends=state[f'unit{j}_ends']
                assert len(ends)==60 and ends[-1]==len(times) and np.all(np.diff(ends)>=0)
                source_result=next(a for a in saved['attempts'] if a['unit_id']==unit['unit_id'])
                n=ni=bad=occupied=0;begin=0
                for e,end in enumerate(ends):
                    t=times[begin:int(end)];begin=int(end)
                    assert np.isfinite(t).all() and np.all((t>=0)&(t<3)) and np.all(np.diff(t)>0)
                    n+=len(t);ni+=max(len(t)-1,0);occupied+=bool(len(t));bad+=int(np.count_nonzero(np.diff(t)<.0015))
                    index=np.searchsorted(np.arange(31)/10,t,side='right')-1
                    reconstructed=np.bincount(index,minlength=30)
                    np.testing.assert_array_equal(reconstructed,state['counts'][e,:,j])
                assert (n,ni,bad,occupied)==tuple(source_result[k] for k in ['training_spikes','within_epoch_ISIs','refractory_ISIs','occupied_epochs'])
                selected+=1
            unit_bins+=int(state['counts'][:,5:].size)
    assert attempts==211 and passes==selected==152 and unit_bins==19*60*25*8
    report={'M2_saved_audit':'PASS','mice':19,'eligible_development':len(gate['eligible_development']),
        'eligible_final':len(gate['eligible_final']),'unit_attempts':attempts,'QC_pass':passes,'QC_fail':attempts-passes,
        'saved_selected_units_reconstructed':selected,'nominal_scored_A_C_unit_bins':unit_bins,
        'new_source_reads':0,'new_model_fits':0,'B_E_D_values_loaded':False}
    print(json.dumps(report));return report


def read_lines(path):return [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()]


if __name__=='__main__':run()
