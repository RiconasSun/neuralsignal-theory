import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
import h5py
from headers import P,permitted,read_value,schema,assets
from transport import RangeReader
from interval_archive import ZipMetadataReader


class HeaderTests(unittest.TestCase):
    def test_manifest_receipts_not_asset_pages(self):
        result=assets()
        self.assertEqual(sum(r['dandiset']=='001260' for r in result),74)
        self.assertEqual(sum(r['dandiset']=='000473' for r in result),25)
    def local(self):
        path=P/'work'/('canary_'+uuid.uuid4().hex+'.h5');path.parent.mkdir(parents=True,exist_ok=True)
        return path

    def test_forbidden_values(self):
        for path in ['/units/spike_times','/units/spike_times_index','/units/firing_rate','/acquisition/LFP/data','/processing/EMG/data','/units/waveform_mean']:
            self.assertFalse(permitted(path),path)

    def test_permitted_metadata(self):
        for path in ['/units/id','/units/location','/units/quality','/general/subject/subject_id','/intervals/tones/start_time','/intervals/saturation/stop_time','/general/extracellular_ephys/electrodes/location','/analysis/spike saturation start/timestamps','/stimulus/presentation/10kHz/timestamps','/processing/ecephys/LFP/ElectricalSeries/starting_time']:
            self.assertTrue(permitted(path),path)

    def test_canary_never_decoded(self):
        with h5py.File(self.local(),'w') as file:
            file['units/id']=[1,2];file['units/spike_times']=[987654321.123]
            self.assertEqual(read_value(file,'/units/id'),[1,2])
            with self.assertRaisesRegex(ValueError,'denied'):read_value(file,'/units/spike_times')
            s=schema(file);self.assertTrue(any(x['path']=='/units/spike_times' and not x['allowed_value'] for x in s))

    def test_soft_and_external_links_denied(self):
        with h5py.File(self.local(),'w') as file:
            file['hidden']=[1];file.require_group('units');file['units/id']=h5py.SoftLink('/hidden')
            with self.assertRaisesRegex(ValueError,'link denied'):read_value(file,'/units/id')
            del file['units/id'];file['units/id']=h5py.ExternalLink('never_opened.h5','/secret')
            with self.assertRaisesRegex(ValueError,'link denied'):read_value(file,'/units/id')

    def test_range_cache_and_exact_bounds(self):
        class T:
            def __init__(self):self.n=0
            def request(self,url,**kwargs):
                self.n+=1
                return b'abcdefghij',{'Content-Range':'bytes 0-9/10','ETag':'abc'},{}
        t=T();r=RangeReader(t,'https://api.dandiarchive.org/file',10,'id')
        self.assertEqual(r.read(3),b'abc');r.seek(0);self.assertEqual(r.read(3),b'abc');self.assertEqual(t.n,1)
        with self.assertRaises(ValueError):r.read()
        with self.assertRaises(ValueError):r.seek(-1)

    def test_range_mismatch_fails(self):
        class T:
            def request(self,*args,**kwargs):return b'abc',{'Content-Range':'bytes 0-2/20','ETag':'a'},{}
        with self.assertRaisesRegex(RuntimeError,'Content-Range'):RangeReader(T(),'url',10,'id').read(3)

    def test_zip_read_to_end_only_in_small_tail(self):
        reader=ZipMetadataReader(None,'unused',1000000,'id')
        with self.assertRaisesRegex(ValueError,'Unbounded archive'):reader.read()
        reader.seek(1000000)
        self.assertEqual(reader.read(),b'')

    def test_no_etag_documentation_identity_is_exact(self):
        r=ZipMetadataReader(None,'https://zenodo.org/api/records/14205018/files/preprocessing.zip/content',100,'id',published_checksum='md5:4bbf126e997dea2cf88f7eb92bc27b07')
        r.check_version({})
        with self.assertRaises(ValueError):ZipMetadataReader(None,'https://unregistered.invalid',100,'id').check_version({})


if __name__=='__main__':unittest.main()
