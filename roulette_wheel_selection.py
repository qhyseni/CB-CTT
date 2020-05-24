from random import randint
import random
from Experiments.statistics import statistics


class roulette_wheel_selection:

    # we can create a probability list (imaginary proportion of the wheel)
    def get_probability_list(weights):
        fitness = weights.values()
        total_fit = float(sum(fitness))
        relative_fitness = [f / total_fit for f in fitness]
        probabilities = [sum(relative_fitness[:i + 1])
                         for i in range(len(relative_fitness))]
        return probabilities

    # Simulation of wheel rotation where the element with highest fitness/probability get the higher chance to get selected
    def spin_roulettewheel(probabilities):

        r = random.random()
        for i in range(len(probabilities)):
            if r <= probabilities[i]:
                return i
