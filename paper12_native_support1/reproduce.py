"""One-command audit replay. No neural data, fitting or new scientific scope."""
import json
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path
from register import HERE,sha,verify
import analysis
import consolidate
from clock import decode,affine,probe_segments
from digital import read_edges,acquire,old
from storage import load

def main(full=False):
    prior=verify();manifest=load(HERE/'manifest.json')
    starting_manifest_sha256=sha(HERE/'manifest.json')
    for group in ('metadata_sha256','source_sha256','results_sha256'):
        for name,digest in manifest[group].items():
            if sha(HERE/name)!=digest:raise RuntimeError('Final candidate drift: '+name)
    output=HERE/'replay/results';output.mkdir(exist_ok=True,parents=True)
    analysis.main(output);consolidate.main(output)
    comparisons={}
    for path in (HERE/'results').glob('*'):
        if path.is_file() and path.name!='endpoint_oracle.json':
            comparisons[path.name]=sha(path)==sha(output/path.name)
    # Recompute every barcode fit from saved permitted digital evidence.
    inventory={r['session_id']:r['objects'] for r in old('allen_raw_inventory.json')}
    fit_checks=0
    for path in (HERE/'results/digital_code2').glob('*.json'):
        result=load(path);sid=result['session_id'];master=result['master']
        times,codes,mismatch=decode(master['barcode_on_seconds'],master['barcode_off_seconds'])
        if times.tolist()!=master['barcode_times'] or codes.astype(int).tolist()!=master['barcode_codes']:raise RuntimeError('Master decoder parity')
        for probe in result['probes']:
            pid=probe['probe_id'];prefix='visual-coding-neuropixels/raw-data/'+sid+'/'+pid+'/'
            ts=next(o for o in inventory[sid] if o['key']==prefix+'event_timestamps.npy')
            cs=next(o for o in inventory[sid] if o['key']==prefix+'channel_states.npy')
            pt=read_edges(acquire(ts,sid+'_'+pid+'_timestamps',5000000,offline=True))
            ps=read_edges(acquire(cs,sid+'_'+pid+'_states',5000000,offline=True))
            bt,bc,_,_=probe_segments(pt,ps)
            for segment in probe['segments']:
                start=segment['segment_start_native_seconds'];end=segment['segment_stop_native_seconds']
                mask=(bt>start)&(bt<(end if end is not None else float('inf')))
                check=affine(master['barcode_times'],master['barcode_codes'],bt[mask],bc[mask])
                if any(segment[k]!=v for k,v in check.items()):raise RuntimeError('All-code clock diagnostic parity')
                fit_checks+=1
    timing_comparisons={}
    if full:
        import digital,visual_clock
        import endpoint_oracle
        digital_dir=HERE/'replay/digital';visual_dir=HERE/'replay/visual'
        digital.main(output=digital_dir,offline=True);visual_clock.main(output=visual_dir)
        for path in (HERE/'results/digital_code2').glob('*.json'):
            timing_comparisons['digital/'+path.name]=sha(path)==sha(digital_dir/path.name)
        for path in (HERE/'metadata/visual_clock_code1').glob('*.json'):
            timing_comparisons['visual/'+path.name]=sha(path)==sha(visual_dir/path.name)
        endpoint_oracle.main(output/HERE.joinpath('results/endpoint_oracle.json').name)
        timing_comparisons['endpoint_oracle']=sha(HERE/'results/endpoint_oracle.json')==sha(output/'endpoint_oracle.json')
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py','-v'],capture_output=True,text=True)
    (HERE/'replay/tests.log').write_text(test.stdout+test.stderr)
    if test.returncode or not all(comparisons.values()) or not all(timing_comparisons.values()):raise RuntimeError('Reproduction/test mismatch')
    if sha(HERE/'manifest.json')!=starting_manifest_sha256:raise RuntimeError('Manifest changed during replay; stale proof refused')
    for group in ('metadata_sha256','source_sha256','results_sha256'):
        if any(sha(HERE/name)!=digest for name,digest in manifest[group].items()):raise RuntimeError('Candidate changed during replay')
    receipt={'utc':datetime.now(timezone.utc).isoformat(),'mode':'FULL_FROZEN_DIGITAL_TIMING' if full else 'SAVED_METADATA',
             'network_requests':0,'neural_values_decoded':False,'new_neural_model_fits':0,'M1_executed':False,
             'exit_code':test.returncode,'comparisons':comparisons,'timing_comparisons':timing_comparisons,
             'recomputed_clock_segments':fit_checks,'prior_files_unchanged':len(prior['prior_hashes']),
             'original_M0_pass':False,'manifest_sha256':starting_manifest_sha256}
    (HERE/'replay/reproduction_result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('timing_comparisons','comparisons')},indent=2))

if __name__=='__main__':main('--full-digital-timing' in sys.argv)
