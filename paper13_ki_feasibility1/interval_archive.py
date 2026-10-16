"""Selective provider interval metadata from a ZIP via its public central directory.

Never opens neural metrics, traces or spike archive members. Selected HDF5
members have exactly the documented tints interval dataset and provenance attrs.
"""
import io
import json
import re
import zipfile
import h5py
from headers import normalize
from transport import META,Transport,RangeReader,sha


class ZipMetadataReader(RangeReader):
    def __init__(self,*args,published_checksum=None):
        super().__init__(*args)
        self.published_checksum=published_checksum

    def check_version(self,headers):
        if headers.get('ETag'):return super().check_version(headers)
        # Zenodo's fixed published record content endpoint supplies no ETag.
        # Pin that exact versioned URL + declared size/checksum, retain all range
        # SHA256s, and explicitly do not claim a verified full-file checksum.
        if self.url!='https://zenodo.org/api/records/14205018/files/preprocessing.zip/content' or self.published_checksum!='md5:4bbf126e997dea2cf88f7eb92bc27b07':
            raise ValueError('Missing fixed published documentation-object identity')
    def read(self,n=-1):
        # zipfile requests read-to-end after seeking into its bounded EOCD tail.
        # This exception never permits a whole-file or arbitrary remainder read.
        if n<0:
            remainder=self.size-self.pos
            if remainder>65558:raise ValueError('Unbounded archive read forbidden')
            n=remainder
        return super().read(n)


def main():
    record=json.loads((META/'preprocessing_record_14205018.json').read_text())
    item=next(r for r in record['files'] if r['key']=='preprocessing.zip')
    t=Transport();reader=ZipMetadataReader(t,item['links']['self'],item['size'],'preprocessing14205018',published_checksum=item['checksum'])
    with zipfile.ZipFile(reader) as z:
        entries=z.infolist()
        if len(entries)>30000:raise ValueError('Archive entry budget exceeded')
        index=[{'path':x.filename,'bytes':x.file_size,'compressed_bytes':x.compress_size,'crc32':x.CRC} for x in entries]
        with (META/'preprocessing_zip_index.json').open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(index,indent=2)+'\n')
        selected=[x for x in entries if re.search(r'/timeselections_quietactive/[^/]+__TSELprestim3__STATEactive(?:__all)?\.h5$',x.filename)]
        output=[]
        for x in selected:
            if x.file_size>2000000:raise ValueError('Interval member byte budget exceeded')
            data=z.read(x)
            with h5py.File(io.BytesIO(data),'r') as h:
                if not isinstance(h.get('tints',getlink=True),h5py.HardLink):raise ValueError('Interval link denied')
                node=h['tints']
                if node.ndim!=2 or node.shape[1]!=2 or node.shape[0]>10000:raise ValueError('Not an interval metadata table')
                output.append({'path':x.filename,'member_sha256':sha(data),'tints':normalize(node[()]),
                               'attributes':{k:normalize(v) for k,v in node.attrs.items()},'shape':list(node.shape)})
        with (META/'provider_active_intervals.json').open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps({'source_record':14205018,'archive_checksum_declared':item['checksum'],'full_archive_checksum_verified':False,'range_bytes':reader.used,'ranges':reader.ranges,'selected_members':output},indent=2,allow_nan=False)+'\n')
    print('Indexed',len(entries),'entries; decoded',len(output),'interval-only metadata members; bytes',reader.used)


if __name__=='__main__':main()
