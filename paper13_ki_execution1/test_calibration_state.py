import copy
import unittest
from . import calibration_state as v
from . import test_predictive as fixtures
from .sensitivity_plan import unit_panels


class StateTests(unittest.TestCase):
    def fixture(self):
        _,_,bundle=fixtures.PredictiveTests().fixture();bundle['training_partition']='C'
        bundle['units']=[{'unit_id':j,'label':'PL5'} for j in range(8)]
        bundle['unit_QC']={str(j):{'partition':'C','pass':True,'rate_hz':1.,'refractory_fraction':0.} for j in range(8)}
        bundle['source_fit_requests']={name:name+'-request' for name in ['B0','B1','B2','B3','B4','D','C','S']}
        bundle['all_C_fit_requests']={str(j):str(j) for j in range(22)}
        bundle['sensitivity_unit_masks']=unit_panels(bundle)
        return bundle

    def test_complete_original_mathematical_dimensions_and_zero_scalers(self):
        result=v.validate(self.fixture());self.assertTrue(result['complete']);self.assertEqual(result['baseline_parameter_counts']['B4'],288)

    def test_incomplete_coefficients_scalers_source_order_and_Q_denied(self):
        original=self.fixture()
        for label,change in [('theta',lambda b:b['baseline_thetas'].update(B4=[0.])),
            ('bounds',lambda b:b['D'].update(theta=[9.]*16)),
            ('sd',lambda b:b['C']['state'].update(count_sd=[-1.]*8)),
            ('Q',lambda b:b['C']['state'].update(Q=[[0.,0.]]*8)),
            ('sources',lambda b:b['baseline_scalers']['B2'].update(source_units=[[-1]*4]*8)),
            ('scaler_shape',lambda b:b['baseline_scalers']['B4'].update(mean=[[0.]*35]*8))]:
            bundle=copy.deepcopy(original);change(bundle)
            with self.subTest(label=label),self.assertRaises(ValueError):v.validate(bundle)

    def test_wrong_training_role_QC_masks_or_missing_request_denied(self):
        original=self.fixture()
        bundle=copy.deepcopy(original);bundle['training_partition']='A'
        with self.assertRaises(PermissionError):v.validate(bundle)
        for change in [lambda b:b['unit_QC']['0'].update(partition='D'),
            lambda b:b['sensitivity_unit_masks'].update(first4=[True]*8),
            lambda b:b['source_fit_requests'].pop('S')]:
            bundle=copy.deepcopy(original);change(bundle)
            with self.assertRaises(ValueError):v.validate(bundle)
