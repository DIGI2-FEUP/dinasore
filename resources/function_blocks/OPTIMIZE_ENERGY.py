import numpy as np
import scipy.optimize as optimize

class OPTIMIZE_ENERGY:

    def cost_energy(self, vars_):
        return (vars_[0] * 2 + vars_[1] * 20)

    def schedule(self, event_name, event_value, temperature, energy_function):
        if event_name == 'INIT':
            self.bnds = ((6, 18), (61, 78))
            return [event_value, None, 0.0, 0.0] #BEST_PARAMS, COST

        elif event_name == 'READ':

            res = optimize.dual_annealing(energy_function,
                                          bounds=self.bnds,
                                          initial_temp=temperature)
            xopt = res.x

            #in_function([6.15,63.3])

            return [None, event_value, xopt]
