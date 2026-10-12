"""Independent all-code versus official endpoint timing procedure, digital only."""
import contextlib
import io
import json
import numpy as np
from register import HERE,verify
from digital import old,acquire,read_edges
from clock import official,probe_segments

def main(output=None):
    verify();rows=[];inventory={r['session_id']:r['objects'] for r in old('allen_raw_inventory.json')}
    for path in sorted((HERE/'results/digital_code2').glob('*.json')):
        record=json.loads(path.read_text());sid=record['session_id'];master=record['master']
        for p in record['probes']:
            pid=p['probe_id'];prefix='visual-coding-neuropixels/raw-data/'+sid+'/'+pid+'/'
            ts=next(o for o in inventory[sid] if o['key']==prefix+'event_timestamps.npy')
            cs=next(o for o in inventory[sid] if o['key']==prefix+'channel_states.npy')
            times=read_edges(acquire(ts,sid+'_'+pid+'_timestamps',5000000,offline=True))
            states=read_edges(acquire(cs,sid+'_'+pid+'_states',5000000,offline=True))
            bt,bc,_,_=probe_segments(times,states)
            for index,segment in enumerate(p.get('segments',[])):
                row={'session_id':sid,'probe_id':pid,'segment_index':index,'matched_codes':segment['matched_codes'],
                     'comparison_executed':False,'native_start_index_assumption':0}
                start=segment['segment_start_native_seconds'];end=segment['segment_stop_native_seconds']
                mask=(bt>start)&(bt<(end if end is not None else np.inf))
                if segment['matched_codes']>=3:
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            shift,rate,_=official().get_probe_time_offset(np.asarray(master['barcode_times']),np.asarray(master['barcode_codes']),bt[mask],bc[mask],0,30000)
                        rate=float(np.asarray(rate).flat[0]);shift=float(np.asarray(shift).flat[0]);x=bt[mask]
                        endpoint=x*30000/rate-shift;allcode=x*segment['slope']+segment['offset_seconds']
                        row.update({'comparison_executed':True,'endpoint_rate_hz':rate,'allcode_rate_hz':30000/segment['slope'],
                                    'endpoint_api_rate_difference_hz':rate-p['api_sampling_rate_hz'],
                                    'max_endpoint_allcode_difference_seconds':float(np.max(np.abs(endpoint-allcode)))})
                    except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)[:200]
                else:row['reason']='Underidentified segment retained; no oracle invented'
                rows.append(row)
    target=(HERE/'results/endpoint_oracle.json') if output is None else output
    target.write_text(json.dumps(rows,indent=2,sort_keys=True))
    print(json.dumps({'segments':len(rows),'executed':sum(r['comparison_executed'] for r in rows),
                      'errors':sum('error' in r for r in rows)}));return rows

if __name__=='__main__':main()
