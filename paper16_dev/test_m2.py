import io
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock
import json
import sys
import h5py
import numpy as np
from .m2_core import running_features, physiological_summary, role_coverage, admission_possible
from .source_running import native_running, hard_object, validate_development, RangeReader
from .source_running import supervise


class Response:
    def __init__(self, status=206, etag='fixed', body=b'1234', content_range='bytes 0-3/100'):
        self.status_code = status
        self.headers = {'ETag': etag, 'Content-Range': content_range}
        self.raw = io.BytesIO(body)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class HTTP:
    def __init__(self, response):
        self.response = response
        self.calls = 0
    def get(self, *args, **kwargs):
        self.calls += 1
        return self.response
    def close(self):
        pass


class Tests(unittest.TestCase):
    def test_exact_running_causality_and_future_invariance(self):
        a = np.array([0., .03, .06]); b = np.array([.02, .05, .08]); q = np.array([.2, .4, .6])
        t = np.array([.02, .021, .05, .051])
        r, missing, parent = running_features(a, b, q, t)
        np.testing.assert_array_equal(missing, [True, False, False, False])
        np.testing.assert_array_equal(parent, [-1, 0, 0, 1])
        np.testing.assert_allclose(r[1:], np.tanh([1., 1., 2.]))
        qq = q.copy(); qq[-1] = 999
        np.testing.assert_array_equal(r, running_features(a, b, qq, t)[0])

    def test_missing_zero_duration_age_and_invalid_bridge(self):
        a = np.array([0., .15]); b = np.array([.02, .31]); q = np.zeros(2)
        r, miss, _ = running_features(a, b, q, np.array([.021, .121, .32]))
        np.testing.assert_array_equal(miss, [False, True, True]); self.assertEqual(r[0], 0.)
        self.assertTrue(running_features(a, b, q, np.array([.05]), [[.03, .04]])[1][0])
        self.assertTrue(running_features(a, b, q, np.array([.021]), [[.01, .015]])[1][0])
        for aa, bb, qq, unit in [(a, b, q, 'degrees'), (a, b, q[:-1], 'radians'),
                                  (a.astype('float32'), b, q, 'radians'), (a, b, np.array([0., np.nan]), 'radians'),
                                  (a, np.array([.0, .31]), q, 'radians')]:
            with self.assertRaises(ValueError): running_features(aa, bb, qq, np.array([.02]), unit=unit)

    def test_A_only_physiology_thresholds_exposure_occupied_and_gap_ISI(self):
        windows = [(i * 2., i * 2. + .22) for i in range(30)]
        x = np.array([s for a, b in windows for s in [a + .01, a + .03]])
        q = physiological_summary(x, windows, 'A')
        self.assertTrue(q['pass']); self.assertEqual(q['spikes'], 60); self.assertEqual(q['ISI_pairs'], 30)
        self.assertEqual(q, physiological_summary(np.r_[x, 999.], windows, 'A'))
        self.assertFalse(physiological_summary(x[:20], windows, 'A')['pass'])
        burst = np.array([s for a, b in windows for s in [a + .01, a + .0101]])
        self.assertFalse(physiological_summary(burst, windows, 'A')['pass'])
        for role in ['B', 'E', 'C', 'D']:
            with self.assertRaises(ValueError): physiological_summary(x, windows, role)
        with self.assertRaises(ValueError): physiological_summary(np.r_[x, np.nan], windows, 'A')
        with self.assertRaises(ValueError): physiological_summary(x, [(0, .22), (.1, .32)], 'A')

    def test_original_role_coverage_and_optimistic_bound_not_mask_selection(self):
        colors = np.tile([-1., 1.], 75); valid = np.ones(150, dtype=bool)
        missing = np.ones((150, 6), dtype=bool)
        c = role_coverage(missing, colors, valid)
        self.assertTrue(all(not x['possible_after_observation_support'] for role in c.values() for x in role.values()))
        missing[:, :3] = False
        c = role_coverage(missing, colors, valid)
        self.assertTrue(all(x['pass'] for role in c.values() for x in role.values()))
        # An unavailable late trial cannot be moved from E to B or A.
        valid[0] = False
        c = role_coverage(missing, colors, valid)
        self.assertEqual(c['A']['-1.0']['presentations'], 44)
        self.assertEqual(c['B']['-1.0']['presentations'], 15)
        missing[:] = True; missing[90:106, :] = False
        c = role_coverage(missing, colors, np.ones(150, dtype=bool))
        self.assertTrue(c['B']['-1.0']['possible_after_observation_support'])
        self.assertEqual(c['B']['-1.0']['optimistic_fraction_upper_bound'], 1.)
        # Actual full-source coverage differs; the upper bound is not a chosen mask.
        self.assertAlmostEqual(c['B']['-1.0']['fraction'], 8 / 15)

    def test_cohort_no_unknown_source_or_duplicate_and_all_three_floors(self):
        rows = [{'mouse_id':str(i), 'protocol':'brain_observatory_1.1' if i < 3 else 'functional_connectivity',
                 'potential_running_coverage_pass':True} for i in range(14)]
        self.assertTrue(admission_possible(rows)['possible_A_physiological_admission'])
        rows[0]['potential_running_coverage_pass'] = False
        self.assertFalse(admission_possible(rows)['possible_A_physiological_admission'])
        with self.assertRaises(ValueError): admission_possible(rows + [rows[0]])
        rows[0]['protocol'] = 'UNKNOWN'
        with self.assertRaises(ValueError): admission_possible(rows)

    def synthetic(self, name, bad_alias=False, bad_unit=False):
        f = h5py.File(name, 'w', driver='core', backing_store=False)
        f.attrs['nwb_version'] = '2.2.2'
        for path, value in [('/identifier', '123'), ('/session_start_time', 'clock'), ('/timestamps_reference_time', 'clock')]:
            f.create_dataset(path, data=value)
        start = f.create_dataset('/processing/running/running_speed/timestamps', data=np.array([0., .03]))
        f.create_dataset('/processing/running/running_speed_end_times/timestamps', data=np.array([.02, .05]))
        rot = f.create_dataset('/processing/running/running_wheel_rotation/data', data=np.array([.1, .2]))
        rot.attrs['unit'] = 'degrees' if bad_unit else 'radians'
        path = '/processing/running/running_wheel_rotation/timestamps'
        if bad_alias: f.create_dataset(path, data=start[:])
        else: f[path] = start
        f.create_dataset('/units/spike_times', data=np.array([np.nan]))
        return f

    def test_synthetic_NWB_behavior_mapping_and_neural_canary(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'work') as tmp:
            for alias, unit in [(False, False), (True, False), (False, True)]:
                with self.synthetic(str(Path(tmp)/'synthetic.h5'), alias, unit) as f:
                    audit = []
                    if alias or unit:
                        with self.assertRaises(ValueError): native_running(f, 123, {'/session_start_time':'clock','/timestamps_reference_time':'clock'}, audit)
                    else:
                        a, b, q = native_running(f, 123, {'/session_start_time':'clock','/timestamps_reference_time':'clock'}, audit)
                        self.assertEqual(len(a), 2); self.assertTrue(all('/units/' not in x for x in audit))
                    with self.assertRaises(ValueError): hard_object(f, '/units/spike_times')
                    f['/identifier_alias'] = h5py.SoftLink('/identifier')
                    with self.assertRaises(ValueError): hard_object(f, '/identifier_alias')
                    del f['/identifier']
                    f['/identifier'] = h5py.SoftLink('/session_start_time')
                    with self.assertRaises(ValueError): hard_object(f, '/identifier')

    def test_Final_and_changed_source_denied_before_open(self):
        row = {'session_id':123,'role':'Development','etag':'fixed'}
        reg = {'objects':[row], 'denied_final_session_ids':[456]}
        validate_development(row, reg)
        for changed in [{**row,'session_id':456}, {**row,'etag':'wrong'}, {**row,'role':'Final_candidate'}]:
            with self.assertRaises(ValueError): validate_development(changed, reg)

    def reader(self, response):
        r = RangeReader({'size':100,'file_id':1,'etag':'fixed'}, time.monotonic()+10)
        r.http.close(); r.http = HTTP(response)
        return r

    def test_range_identity_budget_cache_no_bulk_and_no_retry(self):
        r = self.reader(Response()); self.assertEqual(r.read(4), b'1234'); r.seek(0)
        self.assertEqual(r.read(4), b'1234'); self.assertEqual(r.calls, 1)
        for response in [Response(status=200), Response(etag='wrong'), Response(body=b'bad'), Response(content_range='bytes 1-4/100')]:
            r = self.reader(response)
            with self.assertRaises(RuntimeError): r.read(4)
            self.assertEqual(r.http.calls, 1)
        for limit in ['bytes','calls','deadline']:
            r = self.reader(Response())
            if limit == 'bytes': r.maximum = 4
            if limit == 'calls': r.calls = 4096
            if limit == 'deadline': r.deadline = time.monotonic()-1
            with self.assertRaises(RuntimeError): r.read(4)
            self.assertEqual(r.http.calls, 0)

    def test_expired_cache_and_local_stage_fail_before_access(self):
        from . import source_running as sr
        r = self.reader(Response()); self.assertEqual(r.read(4), b'1234'); r.seek(0)
        r.deadline = time.monotonic()-1
        with self.assertRaises(RuntimeError): r.read(4)
        self.assertEqual(r.http.calls, 1)
        with mock.patch.object(sr, 'review_gate', return_value={}), mock.patch.object(sr, 'read_json', side_effect=AssertionError('No access after deadline')):
            with self.assertRaises(RuntimeError): sr.main(time.monotonic()-1)

    def test_external_watchdog_cancels_blocking_child_and_requires_timely_success(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'work') as tmp:
            path = Path(tmp)/'slow.json'
            self.assertEqual(supervise([sys.executable, '-c', 'import time; time.sleep(60)'], .1, path), 124)
            receipt = json.loads(path.read_text()); self.assertTrue(receipt['child_killed']); self.assertFalse(receipt['valid_source_stage'])
            path = Path(tmp)/'fast.json'
            self.assertEqual(supervise([sys.executable, '-c', 'pass'], 5, path), 0)
            self.assertTrue(json.loads(path.read_text())['valid_source_stage'])
            path = Path(tmp)/'failed.json'
            self.assertEqual(supervise([sys.executable, '-c', 'raise SystemExit(2)'], 5, path), 2)
            self.assertFalse(json.loads(path.read_text())['valid_source_stage'])

    def test_canonical_data_unit_cannot_be_overridden_or_rescaled(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent/'work') as tmp:
            for data_unit, parent_unit, conversion, offset in [('degrees','radians',1.,0.),
                         ('radians','degrees',1.,0.), ('radians','radians',2.,0.), ('radians','radians',1.,.1)]:
                with self.synthetic(str(Path(tmp)/'synthetic.h5')) as f:
                    data = f['/processing/running/running_wheel_rotation/data']
                    data.attrs['unit'] = data_unit; data.parent.attrs['unit'] = parent_unit
                    data.attrs['conversion'] = conversion; data.attrs['offset'] = offset
                    with self.assertRaises(ValueError): native_running(f, 123, {'/session_start_time':'clock','/timestamps_reference_time':'clock'}, [])


if __name__ == '__main__':
    unittest.main()
