import io
import unittest

import h5py
import numpy as np
import audit


class BoundaryTests(unittest.TestCase):
    def file(self,first='55.0',unit='seconds'):
        f=h5py.File(io.BytesIO(),'w')
        f.attrs['nwb_version']='2.1.0'
        f.create_dataset('session_start_time',data='2000-01-01T00:00:00Z')
        f.create_dataset('timestamps_reference_time',data='2000-01-01T00:00:00Z')
        g=f.create_group('acquisition/events');g.attrs['neurodata_type']='AnnotationSeries'
        g.attrs['description']='55start,66end,1stimulus. Unknown99.'
        g.create_dataset('data',data=np.asarray([first,'31.0','66.0'],dtype=h5py.string_dtype()))
        t=g.create_dataset('timestamps',data=[10.,50.,100.]);t.attrs['unit']=unit
        f.create_dataset('units/spike_times',data=[1234.])
        f.create_dataset('intervals/trials/response_value',data=[999.])
        return f

    def test_only_metadata_and_first_label(self):
        with self.file() as f:
            meta=audit.inspect(f)
        self.assertEqual(meta['first_TTL'],'55.0')
        labels=[r for r in meta['decode_ledger'] if r['path'].endswith('/data')]
        self.assertEqual([r['index'] for r in labels],[0])
        self.assertFalse(any('units' in r['path'] or 'trials' in r['path'] for r in meta['decode_ledger']))

    def test_forbidden_before_hdf_dereference(self):
        for p,i in [('units/spike_times',0),('units/spike_times_index',-1),('intervals/trials/response_value',0),
                    ('acquisition/events/data',-1),('acquisition/events/data',1),('acquisition/events/data',True),
                    ('acquisition/experiment_ids/data',0),('acquisition/events/timestamps',1)]:
            with self.subTest(p=p,i=i),self.assertRaises(ValueError):audit.decode(None,p,i,[])

    def test_raw_allowlist_cannot_inject_unit_values(self):
        with self.assertRaises(ValueError):audit.decode(None,'units/spike_times',0,[],raw_paths=('units/spike_times',))

    def test_soft_and_external_links_denied(self):
        with self.file() as f:
            f['soft']=h5py.SoftLink('/units/spike_times')
            f['ext']=h5py.ExternalLink('not-opened.nwb','/units/spike_times')
            for p in ['soft','ext']:
                with self.assertRaises(ValueError):audit.native(f,p)

    def test_unknown_labels_are_not_boundaries(self):
        for first in ['1.0','99.0']:
            with self.file(first) as f:meta=audit.inspect(f)
            result=audit.assess(meta,{'status':'UNKNOWN_SUPPORT'},[{'start':20.}])
            self.assertEqual(result['verdict'],'INCONCLUSIVE')

    def test_original_documented_nonzero_origin(self):
        with self.file() as f:meta=audit.inspect(f)
        old={'status':'DOCUMENTED_CONTINUOUS_SUPPORT','experiment_start':10.,'experiment_end':100.}
        self.assertEqual(audit.assess(meta,old,[{'start':99.}])['verdict'],'PASS')

    def test_explicit_outside_support_fails(self):
        with self.file() as f:meta=audit.inspect(f)
        old={'status':'DOCUMENTED_CONTINUOUS_SUPPORT','experiment_start':10.,'experiment_end':100.}
        self.assertEqual(audit.assess(meta,old,[{'start':99.01}])['verdict'],'FAIL')

    def test_deidentified_date_does_not_imply_recording_zero(self):
        with self.file('1.0') as f:meta=audit.inspect(f)
        self.assertEqual(audit.assess(meta,{},[{'start':20.}])['verdict'],'INCONCLUSIVE')

    def test_unknown_clock_does_not_pass(self):
        with self.file(unit='us') as f:meta=audit.inspect(f)
        self.assertEqual(audit.assess(meta,{},[{'start':20.}])['verdict'],'INCONCLUSIVE')

    def test_changed_prior_envelope_cannot_pass(self):
        with self.file() as f:meta=audit.inspect(f)
        old={'status':'DOCUMENTED_CONTINUOUS_SUPPORT','experiment_start':0.,'experiment_end':100.}
        self.assertEqual(audit.assess(meta,old,[{'start':20.}])['verdict'],'INCONCLUSIVE')

    def test_annotation_and_spike_series_not_raw_support(self):
        with self.file() as f:
            g=f.create_group('acquisition/neural');g.attrs['neurodata_type']='SpikeEventSeries'
            g.create_dataset('timestamps',data=[88.,99.])
            meta=audit.inspect(f)
        self.assertEqual(meta['raw_streams'],[])
        self.assertFalse(any(r['path'].startswith('acquisition/neural') for r in meta['decode_ledger']))

    def test_electrical_series_shape_not_signal_values(self):
        with self.file() as f:
            g=f.create_group('acquisition/raw');g.attrs['neurodata_type']='ElectricalSeries'
            g.create_dataset('data',data=np.full((20,2),987654.))
            t=g.create_dataset('starting_time',data=1.);t.attrs['rate']=1000.;t.attrs['unit']='seconds'
            meta=audit.inspect(f)
        self.assertEqual(meta['raw_streams'][0]['signal_shape'],[20,2])
        self.assertFalse(any(r['path']=='acquisition/raw/data' for r in meta['decode_ledger']))
        self.assertEqual(audit.assess(meta,{},[{'start':20.}])['verdict'],'INCONCLUSIVE')

    def test_exact_half_open_containment(self):
        self.assertTrue(audit.contain(10.,100.,[{'start':10.},{'start':99.}]))
        self.assertFalse(audit.contain(10.,100.,[{'start':9.999}]))

    def test_invalid_boundaries_or_epochs_fail(self):
        for start,stop,ts in [(0.,0.,[{'start':1.}]),(0.,float('inf'),[{'start':1.}]),(0.,2.,[]),(0.,2.,[{'start':float('nan')}])]:
            with self.assertRaises(ValueError):audit.contain(start,stop,ts)

    def test_scaling_and_offset_not_silently_corrected(self):
        for attrs in [{'unit':'us'},{'unit':'seconds','offset':100.},{'unit':'seconds','conversion':1e-6}]:
            self.assertFalse(audit.seconds(attrs))

    def test_unknown_text_not_numeric_label(self):
        for x in ['55garbage',True,'nan','55.01']:self.assertIsNone(audit.label(x))

    def test_nonfinite_scalar_denied(self):
        with self.assertRaises(ValueError):audit.scalar(float('inf'))

    def test_no_new_trial_response_or_full_ttl_accessor(self):
        with self.file() as f:
            for p in ['intervals/trials/start_time','acquisition/events/data']:
                with self.assertRaises(ValueError):audit.decode(f,p,slice(None),[])


if __name__=='__main__':unittest.main()
