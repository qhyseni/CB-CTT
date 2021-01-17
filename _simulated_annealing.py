from random import randint
import math
import random
from Experiments.parameters import parameters
from Experiments.statistics import statistics


class simulated_annealing:

    def __init__(self, solution_cost):

        # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

        self.temperature = - parameters.init_deterioriation / math.log(parameters.initial_acceptance) * solution_cost
        print("Simulated Annealing Init Temperature: ", self.temperature)

    def accept_new_solution(self, new_cost, old_cost, remaining_iterations):

        # calculate acceptance probability
        acceptance_prob = self.acceptance_probability(new_cost, old_cost)
        print("Simulated Annealing Acceptance Probability: ", acceptance_prob)
        accepted = True if acceptance_prob > random.uniform(0, 1) else False

        # cool down the temperature
        cooling_rate = (parameters.temperature_min / self.temperature) ** (1 / remaining_iterations)
        print("Simulated Annealing Cooling Rate: ", cooling_rate)
        self.temperature *= cooling_rate
        print("Simulated Annealing Temperature after cooling: ", self.temperature)
        return accepted

    def acceptance_probability(self, new_cost, old_cost):
        if new_cost <= old_cost:
            return 1.0
        else:
            cost_diff = new_cost - old_cost
            return math.e ** (-(cost_diff) / self.temperature)

    def reheat(self, solution_cost):

        # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

        if solution_cost == 0:
            # temperature must not be zero
            solution_cost += 1
        self.temperature = - parameters.init_deterioriation / math.log(parameters.initial_acceptance) * solution_cost
        print("Simulated Annealing Reheat Temperature: ", self.temperature)









