import xml_to_od
import ectt_to_od
from objective_function import objective_function
from initial_solution import initial_solution
from roulette_wheel_selection import roulette_wheel_selection
from simulated_annealing import simulated_annealing
from alns_destroy_operators import destroy_operators
from alns_repair_operators import repair_operators
from Entities.xml_instance import xml_instance
from maxSAT_repair_operator import maxSAT
import random
import math
import os
import time
import xlsxwriter
from parameters import parameters
from configs import configs
from operators_lookup import operators_lookup
from Entities.instance import instance
from itertools import product

class alns:

    def __init__(self):

        # Get data from instance file
        if configs.instance_type == 1:
            raw_data = xml_to_od.xml_data()
        else:
            raw_data = ectt_to_od.ectt_data()

        self.instance_data = instance(raw_data)


    # main function to find solution of CB-CTT instance using ALNS
    def find_optimal_solution(self, solution):
    
        obj_func_instance = objective_function("UD2", self.instance_data)
    
        current_best = solution
    
        # Calculate cost/objective function of current solution
        current_cost, courses_penalties, curricula_penalties = obj_func_instance.cost(solution)
    
        global_best = current_best
        global_best_cost = current_cost

        time_start = time.time()
    
        SA = simulated_annealing(current_cost)
    
        iteration = 0

        # print('ALNS main exec START')
        while (time.time() - time_start) < parameters.time_limit:

            print("alns iteration: ", iteration)

            iteration += 1
            remaining_iterations = parameters.iteration_limit - ((time.time()-time_start)/parameters.time_limit) * parameters.iteration_limit

            # -------------------------------------------------------------------------------------------------------------------- #
            removal_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.removal_operators_weights)
            removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)

            repair_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.repair_operators_weights)
            # repair_operator_index = roulette_wheel_selection.spin_roulettewheel(repair_operators_probabilities)
            repair_operator_index = 0

            lecture_period_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.lecture_period_operators_weights)
            lecture_period_operator_index = roulette_wheel_selection.spin_roulettewheel(lecture_period_operators_probabilities)

            lecture_room_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.lecture_room_operators_weights)
            lecture_room_operator_index = roulette_wheel_selection.spin_roulettewheel(lecture_room_operators_probabilities)

            priority_rules_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.priority_rules_weights)
            priority_rule_index = roulette_wheel_selection.spin_roulettewheel(priority_rules_probabilities)

            # -------------------------------------------------------------------------------------------------------------------- #

            # Find neighbor solution by applying destruction/repair operator to the current solution
            new_sol = self.neighbor(solution, iteration, remaining_iterations,
                                    removal_operator_index, repair_operator_index, lecture_period_operator_index, lecture_room_operator_index, priority_rule_index,
                                    courses_penalties, curricula_penalties)

            if new_sol is not None:
                # Calculate the new solution's cost
                new_cost, courses_penalties, curricula_penalties = obj_func_instance.cost(new_sol)

                # The acceptance probability function takes in the old cost, new cost, and current temperature
                # and spits out a number between 0 and 1, which is a sort of recommendation on whether or not to jump to the new solution.
                accept = SA.accept_new_solution(new_cost, current_cost, remaining_iterations)

                score_w1 = 0
                score_w2 = 0
                score_w3 = 0

                if accept:
                    solution = new_sol
                    current_cost = new_cost
                    if new_cost > current_cost: # worse than current solution
                        score_w3 = parameters.w3
                    else: # better than current solution
                        score_w2 = parameters.w2

                if new_cost < global_best_cost:
                    global_best = new_sol
                    global_best_cost = new_cost
                    score_w1 = parameters.w1

                psi = max(score_w1, score_w2, score_w3)
                lambda_param = 0.8

                # recalcuate weights of  operators based on the accepted solution
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
        # print('ALNS main exec END')
        print('===============================\n')
        print(global_best_cost)
        print('===============================\n')
        return global_best, global_best_cost
    
    def neighbor(self, solution, iteration, remaining_iterations,
                 removal_operator_index, repair_operator_index, lecture_period_operator_index, lecture_room_operator_index, priority_rule_index,
                 courses_penalties, curricula_penalties):

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
    
        expected_iteration_limit = remaining_iterations + iteration
    
        destroy_limit = math.floor(reference_destroy_limit
                                   - math.pow(iteration, math.log((((parameters.destroy_decrease_parameter - 1)
                                                                    / parameters.destroy_decrease_parameter)
                                                                   * reference_destroy_limit), expected_iteration_limit)))
        print('destroy limit', destroy_limit)
    
        lectures_to_remove = random.randint(1, destroy_limit)
        # print('lectures_to_remove', lectures_to_remove)
    
        # different destroy operators expect different input parameters
        # we are handling it accordingly below
        if removal_operator_index == 0:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, courses_penalties)
        elif removal_operator_index == 1:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, curricula_penalties)
        else:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data)

        if repair_operator_index == 0:
            schedule = operators_lookup.repair_operators[repair_operator_index](schedule, self.instance_data, lectures_removed,
                                                                                operators_lookup.lecture_period_operators[lecture_period_operator_index],
                                                                                operators_lookup.lecture_room_operators[lecture_room_operator_index],
                                                                                operators_lookup.priority_rules[priority_rule_index])
        elif repair_operator_index == 1:
            schedule = operators_lookup.repair_operators[repair_operator_index](schedule, self.instance_data, lectures_removed)

        return schedule
    
    def execute(self):
        
        # Generate initial solution

        initial_solution_instance = initial_solution(self.instance_data)

        init_sol = initial_solution_instance.generate_solution()

        # try:
        #     os.remove('/tmp/initial_solution')
        # except OSError:
        #     pass
        # with open('/tmp/initial_solution', 'a+') as f:
        #     # print solution  to console
        #     for i in range(self.instance_data.days):
        #         for j in range(self.instance_data.periods_per_day):
        #             for k in range(len(self.instance_data.rooms)):
        #                 if init_sol[i][j][k] != "":
        #                     line = init_sol[i][j][k] + " " + self.instance_data.rooms[k].id + " " + str(i) + " " + str(j) + '\n'
        #                     f.write(line)
        #

        schedule, cost = self.find_optimal_solution(init_sol)

        print('success')
        return schedule, cost
