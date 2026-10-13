import copy
import unittest
import numpy as np
from roster_guard import validate_roster,OPTIONS


class RosterTests(unittest.TestCase):
    def fixture(self):
        rows=[];meta={};states={};sessions=[dict(session_id='1',mouse_id='mouse')]
        check=dict(passed=True,max_relative_errors=[0,0])
        for roi in ('CA1','DG'):
            case='1_'+roi;meta[case]=dict(mouse_id='mouse',unit_count=2,training_array_sha256='hash')
            for seed in (11,23,37):
                rows.append(dict(session_id='1',mouse_id='mouse',region=roi,seed=seed,ridge=.1,training_only=True,
                    optimizer_policy=OPTIONS,training_array_sha256='hash',converged=True,optimizer_success=True,
                    projected_gradient=0,initial_gradient_check=check,terminal_gradient_check=check))
                states[case+'_'+str(seed)]=np.zeros((2,29))
        return rows,meta,states,sessions

    def test_exact_roster_and_state_keys(self):
        rows,meta,states,sessions=self.fixture();self.assertTrue(validate_roster(rows,meta,states,sessions))
        with self.assertRaises(RuntimeError):validate_roster(rows[:-1],meta,states,sessions)
        with self.assertRaises(RuntimeError):validate_roster(rows+[rows[0]],meta,states,sessions)
        states.pop('1_CA1_11')
        with self.assertRaises(RuntimeError):validate_roster(rows,meta,states,sessions)

    def test_oracles_and_PG_cannot_be_administratively_passed(self):
        rows,meta,states,sessions=self.fixture();rows[0]['projected_gradient']=.0011
        with self.assertRaises(RuntimeError):validate_roster(rows,meta,states,sessions)
        rows[0]['projected_gradient']=0;rows[0]['terminal_gradient_check']=dict(passed=True,max_relative_errors=[.01,.01])
        with self.assertRaises(RuntimeError):validate_roster(rows,meta,states,sessions)

    def test_bounds_and_feature_dimensions(self):
        rows,meta,states,sessions=self.fixture();states['1_CA1_11']=np.ones((2,29))*9
        with self.assertRaises(RuntimeError):validate_roster(rows,meta,states,sessions)
        states['1_CA1_11']=np.zeros((2,28))
        with self.assertRaises(RuntimeError):validate_roster(rows,meta,states,sessions)
