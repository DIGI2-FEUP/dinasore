import numpy as np

class ENERGY_MODEL:

    def schedule(self, event_name, event_value, target, cost_energy):
        if event_name == 'INIT':
            self.bnds = ((6, 18), (61, 78))
            return [event_value, None, 0.0]

        elif event_name == 'READ':
            self.target = target
            self.cost_energy = cost_energy
            return [None, event_value, self.energy]

    # Parameter Quality - Model
    def f(self, x, y):
        return np.sin(np.sqrt(x ** 2 + y ** 2))

    def cost_quality(self, x_, y_):
        return (self.f(x_, y_) - self.target) ** 2

    def energy(self, vars_):
        x_, y_ = vars_
        weightQ_new = 0.999999

        if np.any(x_ < self.bnds[0][0]) or np.any(x_ > self.bnds[0][1]) or np.any(y_ < self.bnds[1][0]) or np.any(y_ > self.bnds[1][1]):
            return 999999
        else:
            return (1 - weightQ_new) * (self.cost_energy(vars_) / 100) ** 2 + (weightQ_new) * (self.cost_quality(x_, y_)) ** 2