from random import randint
import math
import random


class simulated_annealing:

    def __init__(self, solution_cost):

        # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

        init_deterioriation = 0.04
        initial_acceptance = 0.5

        self.temperature = - init_deterioriation / math.log(initial_acceptance) * solution_cost
        self.temperature_min = 0.1

    def accept_new_solution(self, new_cost, old_cost, remaining_iterations):

        # calculate acceptance probability
        acceptance_prob = self.acceptance_probability(new_cost, old_cost)
        accepted = True if acceptance_prob > random.uniform(0, 1) else False

        # cool down the temperature
        cooling_rate = (self.temperature_min / self.temperature) ** (1 / remaining_iterations)
        self.temperature *= cooling_rate

        return accepted

    def acceptance_probability(self, new_cost, old_cost):
        if new_cost <= old_cost:
            return 1.0
        else:
            cost_diff = new_cost - old_cost
            return math.e ** (-(cost_diff) / self.temperature)









