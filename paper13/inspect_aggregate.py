"""Inspect only parquet schemas, then explicitly permitted metadata columns."""
import argparse
import csv
import gzip
import io
import json
from pathlib import Path
from acquire_metadata import HERE, META, Transport, ParquetRanges, sha

TAG = '2024_Q2_IBL_et_al_BWM'
BASE = f'https://ibl-brain-wide-map-public.s3.amazonaws.com/aggregates/{TAG}/'
ALLOWED = {
    'clusters': {'eid','pid','cluster_id','atlas_id','uuids','label'},
    'trials': {'eid','trial_id','trial','index','bwm_include','stimOn_times',
               'goCue_times','feedback_times','firstMovement_times','response_times',
               'intervals_0','intervals_1','probabilityLeft','saturation_stim_plus04',
               'saturation_feedback_plus04','saturation_move_minus02',
               'saturation_stim_minus04_minus01','saturation_stim_plus06',
               'saturation_stim_minus06_plus06','saturation_stim_plus01'},
}


def run(kind, decode=False):
    import pyarrow
    import pyarrow.parquet as pq
    t=Transport()
    reader=ParquetRanges(t,BASE+kind+'.pqt')
    file=pq.ParquetFile(reader)
    columns=[x for x in file.schema_arrow.names if x in ALLOWED[kind]]
    info={'tag':TAG,'kind':kind,'head':reader.head,'schema':str(file.schema_arrow),
          'rows':file.metadata.num_rows,'groups':file.num_row_groups,
          'allowed_columns':columns,'decoded':decode,'pyarrow_version':pyarrow.__version__}
    if decode:
        required={'eid','pid','cluster_id','atlas_id','label'} if kind=='clusters' else {'eid','bwm_include'}
        if not required.issubset(columns):
            raise RuntimeError('Essential metadata columns absent')
        table=file.read(columns=columns,use_threads=False)
        buf=io.StringIO(newline='')
        writer=csv.DictWriter(buf,fieldnames=columns)
        writer.writeheader()
        writer.writerows(table.to_pylist())
        payload=gzip.compress(buf.getvalue().encode(),mtime=0)
        with (META/(kind+'_metadata.csv.gz')).open('xb') as f: f.write(payload)
        info.update(output_sha256=sha(payload),output_rows=table.num_rows)
    info.update(requests=t.calls,transport_bytes=t.used)
    name=kind+('_decoded' if decode else '_schema')+'.json'
    with (META/name).open('x',encoding='utf8') as f: f.write(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('kind',choices=sorted(ALLOWED))
    parser.add_argument('--decode',action='store_true')
    args=parser.parse_args()
    run(args.kind,args.decode)
