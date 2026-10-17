"""Synthetic canonical metadata and prospective UNKNOWN-support regression."""
import io,unittest
from unittest.mock import patch
import h5py
from . import source_metadata as m

class NativeReaderTests(unittest.TestCase):
    def test_annotation_metadata_whitelist(self):
        b=io.BytesIO()
        with h5py.File(b,'w') as f:
            f['intervals/invalid_times/start_time']=[1.];f['intervals/invalid_times/stop_time']=[2.]
            f['intervals/epochs/start_time']=[0.];f['intervals/epochs/stop_time']=[4.]
            f['general/localization/ElectrodesIBLBregma/brain_region']=['MOs5']
            f['units/obs_intervals']=[[0.,4.]]
        with h5py.File(b,'r') as f:
            self.assertEqual(m.value(f,'/units/obs_intervals'),[[0.,4.]])
            self.assertEqual(m.value(f,'/general/localization/ElectrodesIBLBregma/brain_region'),['MOs5'])
            self.assertEqual(m.value(f,'/intervals/invalid_times/start_time'),[1.])
    def test_unknown_raw_array_cannot_enter_through_interval_group(self):
        for p in ['/intervals/epochs/data','/general/localization/secret/data','/units/spike_times_index','/processing/behavior/Wheel/data']:
            self.assertFalse(m.permitted(p))
    def test_group_attributes_cannot_read_protected_dataset(self):
        b=io.BytesIO()
        with h5py.File(b,'w') as f:
            f['units/spike_times']=[999.];f['intervals/epochs/start_time']=[0.]
            f['intervals/epochs'].attrs['description']='Task epochs, not neural validity'
        original=m.hard
        def guarded(f,p):
            if p=='/units/spike_times':raise AssertionError('Neural node opened')
            return original(f,p)
        with h5py.File(b,'r') as f,patch.object(m,'hard',side_effect=guarded):
            rows=m.schema(f)
        self.assertTrue(any(z.get('attrs',{}).get('description')=='Task epochs, not neural validity' for z in rows))
    def test_asset_size_tamper_rejected_before_network(self):
        import copy
        r=copy.deepcopy(m.read(m.P/'SOURCE_AUDIT_ROSTER.json')['records'][0]);r['asset']['size']+=1
        with self.assertRaises(PermissionError):m.Ranges(r)

if __name__=='__main__':unittest.main()
