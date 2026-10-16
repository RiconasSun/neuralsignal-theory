"""Decode only registered scalar/context/event/support metadata columns."""
import json
import numpy as np
import pandas as pd
from .audit import P,ROOT,read,write,table,sha
from .range_metadata import PREFIX,IBL,MetadataRanges


def columns():
    import pyarrow.parquet as pq
    policy=read(P/'COLUMN_REGISTRATION.json');report={}
    for name,url,key in [('session',PREFIX+'session.parquet','DR_session'),('trials',PREFIX+'trials.parquet','DR_trials'),('units',PREFIX+'units.parquet','DR_units'),('IBL_trials',IBL,'IBL_trials')]:
        output=P/'metadata'/(name+'_metadata.csv.gz');receipt=output.with_suffix('.receipt.json')
        if output.exists():
            if sha(output)!=read(receipt)['output_sha256']:raise ValueError('Decoded metadata changed')
            continue
        names=policy[key]
        if set(names)&set(policy['explicitly_forbidden_columns']):raise PermissionError('Forbidden neural-valued column')
        source=MetadataRanges(url)
        if name=='IBL_trials':
            old=read(ROOT/'paper13/metadata/trials_schema.json')['head']['response_headers']
            if source.etag!=old['ETag'] or source.size!=int(old['Content-Length']):raise ValueError('Original IBL trial object changed')
        else:
            schema=read(P/'metadata'/('DR_'+name+'_schema.json'))
            if source.etag!=schema['ETag'] or source.size!=schema['object_size']:raise ValueError('Registered DR metadata object changed')
        pf=pq.ParquetFile(source,pre_buffer=False)
        if not set(names)<=set(pf.schema_arrow.names):raise ValueError('Registered metadata field missing')
        df=pf.read(columns=names,use_threads=False).to_pandas(ignore_metadata=True)
        if name=='units':
            def normal(v):
                if isinstance(v,np.ndarray):return [normal(x) for x in v.tolist()]
                if isinstance(v,list):return [normal(x) for x in v]
                return v.item() if isinstance(v,np.generic) else v
            df['obs_intervals']=df.obs_intervals.map(lambda v:json.dumps(normal(v)))
        if name=='IBL_trials':
            old=pd.read_csv(ROOT/'paper13/metadata/trials_metadata.csv.gz',float_precision='round_trip')
            if len(old)!=len(df) or old.eid.tolist()!=df.eid.tolist() or not np.array_equal(old.stimOn_times.to_numpy(),df.stimOn_times.to_numpy(),equal_nan=True):
                raise ValueError('IBL old/new metadata row identities do not match exactly')
        table(output,df)
        r={'url':url,'ETag':source.etag,'object_size':source.size,'columns':names,'rows':len(df),'output_sha256':sha(output),'pyarrow':__import__('pyarrow').__version__,
            'neural_columns_decoded':[],'pre_buffer':False,'no_NWB_or_SDK_fallback':True}
        write(receipt,r);report[name]=r
    print(json.dumps({name:{'rows':r['rows'],'columns':len(r['columns'])} for name,r in report.items()}))


if __name__=='__main__':columns()
