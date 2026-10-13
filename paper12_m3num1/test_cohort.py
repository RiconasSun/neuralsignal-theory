import threading
import unittest
from cohort import launch_one,valid_roster,within_budget,cleanup,_timers


class CohortAdapter(unittest.TestCase):
    def test_exact_adapter_scope_and_compilation(self):
        text,changes=launch_one({'session_id':'SYNTHETIC_FIXTURE'},threading.Event(),compile_only=True)
        self.assertEqual(sorted(changes),sorted(['full','phase','sessions','private_runtime','private_runtime']))
        self.assertIn('full = False',text)
        self.assertIn('sessions = [selected_session]',text)
        self.assertIn('phase = selected_phase',text)
        self.assertIn('peer_stop=peer_stop',text)
        self.assertIn('runtime_relative',text)

    def test_no_optimizer_override_in_adapter(self):
        text,_=launch_one({'session_id':'SYNTHETIC_FIXTURE'},threading.Event(),compile_only=True)
        self.assertNotIn('ftol=',text)
        self.assertNotIn('gtol=',text)
        self.assertIn("code_sha256",text)
        self.assertIn('completed(r,',text)

    def records(self):
        return [dict(session_id='SYNTHETIC',region=region,kind=kind,ridge=ridge,seed=seed,
            converged=True,optimizer_success=True,projected_gradient=0.,training_LL_nats_per_unit_bin=-1.,validation_LL_nats_per_unit_bin=-1.)
            for region in ('CA1','DG') for kind in ('stationary','history','population','event','drift','combined')
            for ridge in ([None] if kind=='stationary' else [.001,.01,.1,1.]) for seed in (11,23,37)]

    def test_progressive_complete_roster(self):
        rows=self.records();self.assertTrue(valid_roster(rows,[{'session_id':'SYNTHETIC'}]))
        self.assertFalse(valid_roster(rows[:-1],[{'session_id':'SYNTHETIC'}]))
        self.assertFalse(valid_roster(rows+[rows[0]],[{'session_id':'SYNTHETIC'}]))

    def test_progressive_failed_and_nonfinite(self):
        for key,value in (('converged',False),('projected_gradient',.002),('validation_LL_nats_per_unit_bin',float('nan'))):
            rows=self.records();rows[0][key]=value
            self.assertFalse(valid_roster(rows,[{'session_id':'SYNTHETIC'}]))

    def test_deadline_rejection(self):
        self.assertTrue(within_budget(False,43199.))
        self.assertFalse(within_budget(False,43200.))
        self.assertFalse(within_budget(True,1.))

    def test_timer_cleanup_on_exception(self):
        class Timer:
            cancelled=False
            def cancel(self):self.cancelled=True
        timer=Timer();_timers.append(timer)
        try:
            @cleanup
            def fail():raise RuntimeError('SYNTHETIC')
            with self.assertRaises(RuntimeError):fail()
            self.assertTrue(timer.cancelled)
        finally:_timers.remove(timer)


if __name__=='__main__':unittest.main()
