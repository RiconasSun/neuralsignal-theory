import unittest
import numpy as np
from model_math import make
from oracle import check_gradient,scalar_ll

class HybridHistory(unittest.TestCase):
    def test_all_five_lags_independent_all_coordinates_and_exhaustive(self):
        y=np.array([[[1,2],[0,1],[2,0],[1,1],[0,2],[2,1]],[[2,1],[1,0],[0,2],[2,2],[1,0],[0,1]]],dtype=float)
        x=np.zeros((2,6,3));offset=np.full(y.shape,-.3)
        for size in (2,3,4):
            for ridge in (.001,.01,.1,1.):
                for seed in (11,23,37):
                    model=make('Hybrid',y,x,offset,size);theta=model.initial(seed)
                    self.assertTrue(np.all(np.max(model.history,axis=(0,1,2))>0))
                    result=check_gradient(theta,model,ridge,'Hybrid',size,range(len(theta)))
                    self.assertTrue(result['passed'],result)
                    error=abs(model.score(theta)-scalar_ll(theta,'Hybrid',y,x,offset,size,True))
                    self.assertLessEqual(error,1e-10)

if __name__=='__main__':unittest.main(verbosity=2)
