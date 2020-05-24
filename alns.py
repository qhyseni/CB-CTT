import xml_to_od
import ectt_to_od
from Entities.instance import instance
from Entities.xml_instance import xml_instance
from objective_function import objective_function
from initial_solution import initial_solution
from roulette_wheel_selection import roulette_wheel_selection
from simulated_annealing import simulated_annealing
from alns_destroy_operators import destroy_operators
from alns_repair_operators import repair_operators
from operators_lookup import operators_lookup
from maxSAT_repair_operator import maxSAT
import random
import math
import os
import time
from Experiments.parameters import parameters
from Experiments.configs import configs
from itertools import product
from Experiments.statistics import statistics

class alns:

    def __init__(self):

        # Get data from instance file
        if configs.instance_type == 1:
            raw_data = xml_to_od.xml_data()
        else:
            raw_data = ectt_to_od.ectt_data()

        self.instance_data = instance(raw_data)

    # main function to find solution of CB-CTT instance using ALNS
    def find_optimal_solution(self, solution, Uc):
        # reset statistics value
        statistics_instance = statistics()
        statistics_instance.reset()

        obj_func_instance = objective_function("UD2", self.instance_data)
    
        current_best = solution
    
        # Calculate cost/objective function of current solution
        current_cost, courses_penalties, curricula_penalties = obj_func_instance.cost(solution)
    
        global_best = current_best
        global_best_cost = current_cost

        time_start = time.time()
    
        SA = simulated_annealing(current_cost)
    
        iteration = 0

        while (time.time() - time_start) < parameters.time_limit:
            iteration += 1
            statistics.iterations += 1
            print("Iteration: ", iteration)
            remaining_iterations = parameters.iteration_limit - ((time.time()-time_start)/parameters.time_limit) * parameters.iteration_limit
            print("Remaining Iterations: ", remaining_iterations)
            # -------------------------------------------------------------------------------------------------------------------- #
            removal_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.removal_operators_weights)
            print("Removal Operators Probabilities: ", removal_operators_probabilities)
            removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)

            repair_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.repair_operators_weights)
            print("Repair Operators Probabilities: ", repair_operators_probabilities)
            repair_operator_index = roulette_wheel_selection.spin_roulettewheel(repair_operators_probabilities)
            # repair_operator_index = 0

            lecture_period_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.lecture_period_operators_weights)
            print("Lecture-Period Operators Probabilities: ", lecture_period_operators_probabilities)
            lecture_period_operator_index = roulette_wheel_selection.spin_roulettewheel(lecture_period_operators_probabilities)
            # lecture_period_operator_index = 0

            lecture_room_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.lecture_room_operators_weights)
            print("Lecture-Room Operators Probabilities: ", lecture_period_operators_probabilities)
            lecture_room_operator_index = roulette_wheel_selection.spin_roulettewheel(lecture_room_operators_probabilities)
            # lecture_room_operator_index = 0

            priority_rules_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.priority_rules_weights)
            print("Priority Rules Probabilities: ", lecture_period_operators_probabilities)
            priority_rule_index = roulette_wheel_selection.spin_roulettewheel(priority_rules_probabilities)

            # -------------------------------------------------------------------------------------------------------------------- #

            # Find neighbor solution by applying destruction/repair operator to the current solution
            new_sol, Uc = self.neighbor(solution, iteration, remaining_iterations,
                                    removal_operator_index, repair_operator_index, lecture_period_operator_index, lecture_room_operator_index, priority_rule_index,
                                    courses_penalties, curricula_penalties, Uc)

            if new_sol is not None:
                # Calculate the new solution's cost
                new_cost, courses_penalties, curricula_penalties = obj_func_instance.cost(new_sol)
                print("New solution cost: ", new_cost)
                # The acceptance probability function takes in the old cost, new cost, and current temperature
                # and spits out a number between 0 and 1, which is a sort of recommendation on whether or not to jump to the new solution.
                accept = SA.accept_new_solution(new_cost, current_cost, remaining_iterations)

                score_w1 = 0
                score_w2 = 0
                score_w3 = 0

                if accept:
                    statistics.accepted_count += 1
                    print("New solution accepted.")
                    solution = new_sol
                    current_cost = new_cost
                    if new_cost > current_cost: # worse than current solution
                        print("New solution is worse than the current solution.")
                        statistics.worse_count += 1
                        score_w3 = parameters.w3
                    else: # better than current solution
                        print("New solution is better than the current solution.")
                        statistics.better_count += 1
                        score_w2 = parameters.w2
                else:
                    print("New solution NOT accepted.")

                if new_cost < global_best_cost:
                    print("New solution is the global best.")
                    statistics.global_best_counts += 1
                    statistics.iteration_best = iteration
                    statistics.time_best = time.time() - time_start
                    global_best = new_sol
                    global_best_cost = new_cost
                    score_w1 = parameters.w1

                print("Score W1: ", score_w1)
                print("Score W2: ", score_w3)
                print("Score W3: ", score_w3)

                psi = max(score_w1, score_w2, score_w3)
                print("PSI: ", psi)
                lambda_param = 0.8

                # recalculate weights of  operators based on the accepted solution
                operators_lookup.removal_operators_weights[str(removal_operator_index)] = lambda_param * operators_lookup.removal_operators_weights[str(removal_operator_index)] + (1-lambda_param) * psi
                operators_lookup.repair_operators_weights[str(repair_operator_index)] = lambda_param * operators_lookup.repair_operators_weights[str(repair_operator_index)] + (1-lambda_param) * psi
                # we need to recalculate weights only if two-stage operation was performed
                # if max-SAT was performed it means that the below operators weren't used, hence didn't have impact in the result
                # consequently we won't update the weights in this iteration
                if repair_operator_index == 0:
                    operators_lookup.lecture_period_operators_weights[str(lecture_period_operator_index)] = lambda_param * operators_lookup.lecture_period_operators_weights[str(lecture_period_operator_index)] + (1-lambda_param) * psi
                    operators_lookup.lecture_room_operators_weights[str(lecture_room_operator_index)] = lambda_param * operators_lookup.lecture_room_operators_weights[str(lecture_room_operator_index)] + (1-lambda_param) * psi
                    operators_lookup.priority_rules_weights[str(priority_rule_index)] = lambda_param * operators_lookup.priority_rules_weights[str(priority_rule_index)] + (1-lambda_param) * psi

            else:
                print("None")

        print('===============================\n')
        print("Best solution cost: ", global_best_cost)
        print('===============================\n')

        # ---------------------------------------------------------------
        # try:
        #     os.remove('/tmp/solution' + time.time())
        # except OSError:
        #     pass
        # with open('/tmp/solution' + time.time(), 'a+') as f:
        #     # print solution  to console
        #     for i in range(self.instance_data.days):
        #         for j in range(self.instance_data.periods_per_day):
        #             for k in range(len(self.instance_data.rooms)):
        #                 if solution[i][j][k] != "":
        #                     line = solution[i][j][k] + " " + self.instance_data.rooms[k].id + " " + str(i) + " " + str(j) + '\n'
        #                     f.write(line)

        statistics.time = time.time() - time_start

        statistics_instance.print_statistics()
        return global_best, global_best_cost
    
    def neighbor(self, solution, iteration, remaining_iterations,
                 removal_operator_index, repair_operator_index, lecture_period_operator_index, lecture_room_operator_index, priority_rule_index,
                 courses_penalties, curricula_penalties, Uc):

        lectures_counter = 0
        for course in self.instance_data.courses:
            lectures_counter += int(course.lectures)
    
        #  The reference destroy limit nmax 0 is set to d percent of the total number of lectures.
        #  It turns out that the usage of different percentages depending on the instance size is beneficial,
        #  i.e., ds is used for small instances with less than 280 lectures and dl for larger instances.
    
        if lectures_counter <= 280:
            reference_destroy_limit = math.floor(parameters.ds * lectures_counter)
        else:
            reference_destroy_limit = math.floor(parameters.dl * lectures_counter)

        print("Reference Destroy Limit: ", reference_destroy_limit)
        expected_iteration_limit = remaining_iterations + iteration
        print("Expected Iteration Limit: ", expected_iteration_limit)
        destroy_limit = math.floor(reference_destroy_limit
                                   - math.pow(iteration, math.log((((parameters.destroy_decrease_parameter - 1)
                                                                    / parameters.destroy_decrease_parameter)
                                                                   * reference_destroy_limit), expected_iteration_limit)))
        print("Destroy Limit: ", destroy_limit)
        lectures_to_remove = random.randint(1, destroy_limit)
        print("Lectures to remove number: ", lectures_to_remove)

        # different destroy operators expect different input parameters
        # we are handling it accordingly below
        if removal_operator_index == 0:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, courses_penalties)
        elif removal_operator_index == 1:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, curricula_penalties)
        else:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data)

        # append lectured left unscheduled from prev row
        for l in Uc:
            lectures_removed.append(l)

        if repair_operator_index == 0:
            schedule, Uc = operators_lookup.repair_operators[repair_operator_index](schedule, self.instance_data, lectures_removed,
                                                                                operators_lookup.lecture_period_operators[lecture_period_operator_index],
                                                                                operators_lookup.lecture_room_operators[lecture_room_operator_index],
                                                                                operators_lookup.priority_rules[priority_rule_index])
        elif repair_operator_index == 1:
            schedule, Uc = operators_lookup.repair_operators[repair_operator_index](schedule, self.instance_data, lectures_removed)

        return schedule, Uc
    
    def execute(self):
        # there might be lectures that end up unscheduled during the 2-stage operation
        # we are assuming that MaxSAT might leave unscheduled lectures for the sake of consistency, althouch this is not true
        # maxSAt always returns scheduled lectures
        Uc = []

        # Generate initial solution
        initial_solution_instance = initial_solution(self.instance_data)
        init_sol, Uc = initial_solution_instance.generate_solution()
        # --------------------------------------------------

        # ---------------------------------------------------------------
        try:
            os.remove('/tmp/initial_solution')
        except OSError:
            pass
        with open('/tmp/initial_solution', 'a+') as f:
            # print solution  to console
            for i in range(self.instance_data.days):
                for j in range(self.instance_data.periods_per_day):
                    for k in range(len(self.instance_data.rooms)):
                        if init_sol[i][j][k] != "":
                            line = init_sol[i][j][k] + " " + self.instance_data.rooms[k].id + " " + str(i) + " " + str(j) + '\n'
                            f.write(line)

        schedule, cost = self.find_optimal_solution(init_sol, Uc)

        return schedule, cost, Uc
