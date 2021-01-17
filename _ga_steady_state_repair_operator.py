import random
import copy
from _alns_helpers import alns_helpers
from Experiments.statistics import statistics
from Models.period_course import period_course
from Models.period_conflict_courses import period_conflict_courses

class ga_steady_state_repair_operator:

    ###################### Repair operators #############################################

    def ga_steady_state_repair_operator(schedule, instance_data):
        print("GA Steady State Mutation Repair Operator")
        statistics.ga_steady_state_count += 1

    #             popsize = population size - numri i kromozomeve ne nje gjenerate te popullates
    #             1. Initialise: generate a population of popsize random solutions, evaluate their fitnesses.
    #             2. Run 'Select' to obtain a parent solution X.
    #             3. With probability mute_rate, mutate a copy of X to obtain a mutant M (otherwise M = X)
    #             4. Evaluate the fitness of M.
    #             5. Let W be the current worst in the population (BTR). If
    #             M is not less fit than W, then replace W with M.//(otherwise do nothing)
    #             6. If a termination condition is met (e.g. we have done 10,000 evaluations) then stop. Otherwise go to 2


    def tournament_selection(population, tournament_size):
        print("Tournament Selection")
        statistics.ga_steady_state_count += 1

    #         Select:
    #         Randomly choose tournament_ size individuals from the population.
    #         Let X be the one with best fitness (BTR);
    #         return X.

        selected_parents = []
        added_indicies = []
        population_count = len(population)

        for i in range(tournament_size):
            while True:
                parent_index = random.randrange(population_count)
                if not added_indicies.__contains__(parent_index):
                    break

            selected_parents.append(population[parent_index])
            added_indicies.append(parent_index)

        selected_parents.sort(key=lambda x: x.fitness)

        return selected_parents[0]

    ###################### End of Repair operators ############################################