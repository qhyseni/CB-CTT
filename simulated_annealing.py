from random import randint
import math
import random
from parameters import parameters

class simulated_annealing:

    def __init__(self, solution_cost):

        # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

        self.temperature = - parameters.init_deterioriation / math.log(parameters.initial_acceptance) * solution_cost

    def accept_new_solution(self, new_cost, old_cost, remaining_iterations):

        # calculate acceptance probability
        acceptance_prob = self.acceptance_probability(new_cost, old_cost)
        accepted = True if acceptance_prob > random.uniform(0, 1) else False

        # cool down the temperature
        cooling_rate = (parameters.temperature_min / self.temperature) ** (1 / remaining_iterations)
        self.temperature *= cooling_rate

        return accepted

    def acceptance_probability(self, new_cost, old_cost):
        if new_cost <= old_cost:
            return 1.0
        else:
            cost_diff = new_cost - old_cost
            return math.e ** (-(cost_diff) / self.temperature)









