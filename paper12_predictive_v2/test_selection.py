import unittest
from selection import boundary,rate_pairs,views,expected_shape
class SelectionTests(unittest.TestCase):
    def test_frozen_metadata_masks_not_nominal_trial_count(self):
        s={'trial_ids':{'A':list(range(347)),'B':list(range(234))},'unit_ids':{'CA1':list(range(32))}}
        self.assertEqual(expected_shape(s,'CA1','A'),(347,20,32));self.assertEqual(expected_shape(s,'CA1','B'),(234,20,32))
    def test_boundary_strict_and_undefined(self):
        m=[{'nearest_other_channel_label_vertical_um':v} for v in ('20','40','41','NA','nan')]
        self.assertEqual(boundary(range(5),m,20),[1,2]);self.assertEqual(boundary(range(5),m,40),[2])
    def test_rate_tie_no_reuse(self):self.assertEqual(rate_pairs([1,1,5],[1,1,1]),[(0,0),(1,1)])
    def test_rate_threshold(self):self.assertEqual(rate_pairs([1],[2]),[(0,0)]);self.assertEqual(rate_pairs([1],[2.01]),[])
    def test_views_matched_and_probe(self):
        m={k:[{'probe_id':'1','nearest_other_channel_label_vertical_um':'60'} for i in range(6)] for k in ('CA1','DG')}
        v=views([1]*6,[1]*6,m)
        self.assertEqual(len(v['boundary40']['CA1']),6);self.assertIn('shared_probe_1',v);self.assertNotIn('leave_probe_1',v)
if __name__=='__main__':unittest.main()
