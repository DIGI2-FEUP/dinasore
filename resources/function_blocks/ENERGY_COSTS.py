import numpy as np

class ENERGY_COSTS:

    def schedule(self, event_name, event_value, params):
        if event_name == 'INIT':
            return [event_value, None, None, 0.0, 0.0]

        elif event_name == 'READ':
            return [None, event_value, None, self.cost_energy, 0.0]

        elif event_name == 'READ_DATA':
            return [None,  None, event_value, 0.0, self.cost_energy(params)]

    def cost_energy(self, vars_):
        return (vars_[0] * 2 + vars_[1] * 20)