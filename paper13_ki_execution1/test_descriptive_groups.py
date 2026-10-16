import unittest
from . import descriptive_groups as g


class GroupTests(unittest.TestCase):
    def test_unknown_genotype_single_condition_empty_leaveout_and_unique_probes(self):
        mice=[str(j) for j in range(9)];scores={m:{name:-1. for name in g.LABELS} for m in mice}
        for j,m in enumerate(mice):scores[m]['D']+=j/100
        descriptor={m:{'documented_conditions':['Aversion'],'genotype':'NOT_DECODED_FROM_SOURCE','provider_coordinates':{'DV':[-float(j)]*8},'probe_id':'probe0'} for j,m in enumerate(mice)}
        result=g.summarize(scores,descriptor,mice)
        condition=result['groups']['condition']['groups']['Aversion'];self.assertEqual(condition['n'],9)
        self.assertIsNone(condition['leave_group_out_means']);self.assertEqual(condition['leave_group_out_status'],'UNAVAILABLE_EMPTY_REMAINDER')
        self.assertFalse(result['groups']['genotype']['groups']['NOT_DECODED_FROM_SOURCE']['documented_measured_value'])
        self.assertEqual(len(result['groups']['individual_probe']['groups']),9);self.assertTrue(result['individual_probe_leaveout_equals_mouse_leaveout'])
        self.assertFalse(result['groups']['raw_provider_DV_median']['physical_units_verified']);self.assertFalse(result['optional_group_results_can_rescue'])
