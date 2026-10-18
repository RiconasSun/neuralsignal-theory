"""Synthetic finite-reference, coverage and fixed RNG regression oracles."""
import unittest
import numpy as np
from paper15_m1.synthetic import control_seed
from .controls import seed,thinning_seed,thin_role,stratum_keys,cyclic_donors,block_donors,reference,coverage,history_from_microbins


class ControlTests(unittest.TestCase):
    def test_frozen_seed_matches_M1_oracle_and_role_isolation(self):
        for suite in ['N1','N2','N3','N4']:
            self.assertEqual(seed(suite,'mouse','D',37),control_seed(suite,'mouse','D',37))
        for role in ['C','A','B','E']:
            with self.assertRaises(PermissionError):seed('N1','mouse',role,0)
    def test_N1_multivariate_count_preservation_and_no_input_mutation(self):
        y=np.arange(4*20*3).reshape(4,20,3);original=y.copy()
        out,ix,meta=reference(y,'N1',np.array([4,3,2,1]),np.random.default_rng(1))
        np.testing.assert_array_equal(out.sum(1),y.sum(1));np.testing.assert_array_equal(y,original)
        self.assertTrue(all(1<=x['offset']<=19 for x in meta['offsets']))
        self.assertEqual([x['trial'] for x in meta['offsets']],[1,2,3,4])
    def test_N2_exact_strata_nonself_cycle_and_draw_schedule(self):
        ids=np.array([3,1,2,5,4,6]);keys=[(0,0),(0,0),(0,0),(1,0),(1,0),(2,0)]
        rng=np.random.Generator(np.random.PCG64(10));other=np.random.Generator(np.random.PCG64(10))
        donors=cyclic_donors(ids,keys,rng)
        other.integers(1,3);other.integers(1,2)
        self.assertEqual(rng.bit_generator.state,other.bit_generator.state)
        self.assertEqual(donors[-1],-1)
        for i,d in enumerate(donors):
            if d>=0:self.assertNotEqual(i,d);self.assertEqual(keys[i],keys[d])
        self.assertEqual(len(set(donors[donors>=0])),5)
    def test_wheel_stratum_ties_lower_and_original_role_half(self):
        tr=[dict(contrastLeft=.25,contrastRight=None)]*10
        keys=stratum_keys(tr,[1,4,5,8],(0,10),[2,2,3,1],2)
        self.assertEqual(keys,[(0,0,0,0),(0,0,0,0),(0,0,1,1),(0,0,1,0)])
    def test_N4_complete_original_blocks_and_withinblock_order(self):
        ids=np.arange(40);donors=block_donors(ids,(0,40),np.random.default_rng(4))
        self.assertTrue((donors>=0).all());self.assertFalse((ids==donors).any())
        np.testing.assert_array_equal(donors%5,ids%5)
        ids=np.delete(ids,2);donors=block_donors(ids,(0,40),np.random.default_rng(4))
        self.assertTrue((donors[ids<5]==-1).all())
    def test_original_and_reference_common_exposure_coverage(self):
        self.assertTrue(coverage(np.arange(30),50));self.assertFalse(coverage(np.arange(29),40))
        self.assertFalse(coverage(np.arange(30),51))
    def test_role_thinning_draws_all_spikes_and_stays_original_order(self):
        t=np.repeat(np.arange(100),2).astype(float);labels=np.zeros(200,int)
        kept,_,receipt=thin_role(t,labels,[0],['uuid'],[8.],'mouse','C')
        rng=np.random.Generator(np.random.PCG64(thinning_seed('mouse','uuid','C')))
        mask=rng.random(200)<.25
        np.testing.assert_array_equal(kept,t[mask]);self.assertEqual(receipt[0]['draw_count'],200)
        self.assertTrue((np.diff(kept)>=0).all())
        for role in ['A','B','E']:
            with self.assertRaises(PermissionError):thin_role(t,labels,[0],['uuid'],[8.],'mouse',role)
    def test_thinning_chunk_invariance_without_reseeding(self):
        s=thinning_seed('mouse','uuid','D');a=np.random.Generator(np.random.PCG64(s));b=np.random.Generator(np.random.PCG64(s))
        np.testing.assert_array_equal(a.random(103),np.r_[b.random(17),b.random(86)])
    def test_history_uses_past_microbins_only_and_resets(self):
        y=np.ones((2,20,2),int);h=history_from_microbins(y)
        np.testing.assert_array_equal(h[:,0],0);np.testing.assert_allclose(h[:,10:],20,atol=1e-14)
        changed=y.copy();changed[0,13:]=1000;h2=history_from_microbins(changed)
        np.testing.assert_array_equal(h[:,:13],h2[:,:13]);np.testing.assert_array_equal(h[1],h2[1])


if __name__=='__main__':unittest.main(verbosity=2)
