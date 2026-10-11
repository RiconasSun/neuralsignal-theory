"""Append-only deterministic recurrence repair; the failed original stays intact."""
import numpy as np
import predictive_models as original

PoissonGLM = original.PoissonGLM
StatePoisson = original.StatePoisson
poisson_logpmf = original.poisson_logpmf
make_design = original.make_design
fit_stationary = original.fit_stationary
fit_model = original.fit_model
history = original.history
forward_backward = original.forward_backward


class RecurrentPoisson(original.RecurrentPoisson):
    def _states(self, theta):
        a, b, d, c = self.unpack(theta)
        states = np.zeros(self.y.shape[:2] + (self.dimension,))
        past = np.zeros_like(self.y)
        past[:, 1:] = np.log1p(self.y[:, :-1])
        eta = np.empty_like(self.y)
        # One row uses the same arithmetic regardless of other trials/batch size.
        for trial in range(len(self.y)):
            previous = np.zeros(self.dimension)
            for t in range(self.y.shape[1]):
                previous = np.tanh(previous @ a.T + past[trial, t] @ b.T + self.x[trial, t] @ d.T)
                states[trial, t] = previous
                eta[trial, t] = self.offset[trial, t] + previous @ c.T
        return states, past, eta
