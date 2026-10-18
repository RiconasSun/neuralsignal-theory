"""Diagnostic regressions demonstrate the current bug, without fixing scientific inputs."""
import json
import unittest
import numpy as np
import pandas as pd
from .features import held

class TimeSerializationDiagnostic(unittest.TestCase):
    def test_default_pandas_rounding_changes_strict_past_membership(self):
        event=np.float64(1.000000000049)
        encoded=json.loads(pd.DataFrame({'stimOn_times':[event]}).to_json(orient='records'))[0]['stimOn_times']
        wt=np.array([0.,1.,2.]);wp=np.array([0.,.0015339807878856412,.1])
        native,ni=held(wt,wp,event);rounded,ri=held(wt,wp,encoded)
        self.assertEqual(encoded,1.);self.assertEqual(int(ni),1);self.assertEqual(int(ri),0)
        self.assertNotEqual(float(native),float(rounded))

    def test_standard_json_roundtrip_preserves_synthetic_binary64(self):
        # Prospective repair option only; production serializer is deliberately unchanged.
        values=[float(np.nextafter(1.,2.)),1.000000000049,float(np.nextafter(10000.,0.))]
        result=json.loads(json.dumps(values,allow_nan=False))
        self.assertEqual(np.asarray(values).tobytes(),np.asarray(result).tobytes())

if __name__=='__main__':unittest.main()
