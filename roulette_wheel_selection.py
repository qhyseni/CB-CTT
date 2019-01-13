from random import randint
import random


class roulette_wheel_selection:

    # we can create a probability list (imaginary proportion of the wheel)
    def get_probability_list(removal_operators_weights):
        fitness = removal_operators_weights.values()
        total_fit = float(sum(fitness))
        relative_fitness = [f / total_fit for f in fitness]
        probabilities = [sum(relative_fitness[:i + 1])
                         for i in range(len(relative_fitness))]
        return probabilities

    # Simulation of wheel rotation where the element with highest fitness/probability get the higher chance to get selected
    def spin_roulettewheel(probabilities):
        slot_count = len(probabilities)
        randno = random.randint(0, 10000)
        rot_degree = randno % 360
        rot_unit = 360 / slot_count
        rol_no = (rot_degree - (rot_degree % (rot_unit))) / rot_unit
        rol_value = probabilities[int(rol_no)]
        return int(rol_no)
