"""Freeze exact essential native file identity before any real pilot payload."""
import datetime, hashlib, json, re
from pathlib import PurePosixPath
from .coverage import P,dump

def main():
    files=[]
    identity=json.loads((P/'PILOT_IDENTITY_FREEZE.json').read_text(encoding='utf8'))
    for p in identity['pilots']:
        inv=json.loads((P/'source'/(p['eid']+'_s3.json')).read_text(encoding='utf8'))
        root=inv['prefix'];probe=p['probe_name']
        rules={
          'times':(f'alf/{probe}/pykilosort/#2024-05-06#/','spikes.times.'),
          'clusters':(f'alf/{probe}/pykilosort/#2024-05-06#/','spikes.clusters.'),
          'cluster_channels':(f'alf/{probe}/pykilosort/#2024-05-06#/','clusters.channels.'),
          'metrics':(f'alf/{probe}/pykilosort/#2024-05-06#/','clusters.metrics.'),
          'uuids':(f'alf/{probe}/pykilosort/#2024-05-06#/','clusters.uuids.'),
          'atlas':(f'alf/{probe}/pykilosort/#2024-05-06#/','channels.brainLocationIds_ccf_2017.'),
          'trials':('alf/#2025-03-03#/','_ibl_trials.table.'),
          'wheel_times':('alf/','_ibl_wheel.timestamps.'),
          'wheel_position':('alf/','_ibl_wheel.position.'),
          'saturation':(f'raw_ephys_data/{probe}/','_iblqc_ephysSaturationAP.samples.'),
          'recording_meta':(f'raw_ephys_data/{probe}/',f'_spikeglx_ephysData_g0_t0.imec{int(probe[-2:])}.ap.'),
          'sync':(f'raw_ephys_data/{probe}/',f'_spikeglx_ephysData_g0_t0.imec{int(probe[-2:])}.sync.')}
        for role,(collection,start) in rules.items():
            matches=[x for x in inv['objects'] if str(PurePosixPath(x['key']).parent)+'/'==root+collection and PurePosixPath(x['key']).name.startswith(start)
                     and (role!='recording_meta' or x['key'].endswith('.meta'))]
            assert len(matches)==1,(p['subject'],role,len(matches))
            x=matches[0];assert x['bytes']<=450000000
            files.append(dict(**x,subject=p['subject'],eid=p['eid'],pid=p['pid'],probe=probe,role=role,
                dataset_uuid=re.search(r'\.([0-9a-f-]{36})\.',x['key']).group(1),bucket=inv['bucket']))
    assert sum(x['bytes'] for x in files)<=1200000000
    target=P/'PILOT_FILE_FREEZE.json';assert not target.exists()
    dump(target,dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,total_bytes=sum(x['bytes'] for x in files),
        source_identity='Public S3 dataset UUID, explicit revision, listing size/ETag; MD5 checked when single-part ETag, SHA256 recorded after access',
        reader='ONE-api 3.6.1 one.remote.aws.s3_download_file + one.alf.io.load_file_content',
        native_trial_policy='2025-03-03 native table, structural finite/order screen and source known saturation masked. No old bwm/saturation flags transferred. Native-vs-aggregate values compared transparently.',
        observation_policy='AP meta recorded file duration mapped via provider probe-to-session sync; intersect trial windows, mask known saturation. Conventional curated support, no packet-loss certificate.',
        count_demo='First 10 eligible native trials; fixed 50 ms bins over [stim,stim+.5), all good MOp units, zeros retained, invalid bins masked; half-open counts exclude right edge.',
        stop='Essential identity/clock/mapping/nonfinite unrecoverable contradiction => stop, no replacement pilots or fitting'))
    print(json.dumps(dict(files=len(files),bytes=sum(x['bytes'] for x in files))))
if __name__=='__main__':main()
