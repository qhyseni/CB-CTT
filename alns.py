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
from Entities.instance import instance
from MIP_V2_repair_operator import mip_operator
from itertools import product

class alns:

    def __init__(self):
        # Get data from instance file
        if configs.instance_type == 1:
            raw_data = xml_to_od.xml_data()
        else:
            raw_data = ectt_to_od.ectt_data()

        self.instance_data = instance(raw_data)

        # Initial weights of removal operators set to 1
        self.removal_operators_weights = {
            "0": 1,
            "1": 1,
            "2": 1,
            "3": 1,
            "4": 1,
            "5": 1,
            "6": 1}

        # array of removal operators methods with touple of position (key) and value (method name)
        self.removal_operators = {
            0: destroy_operators.worst_courses_removal,
            1: destroy_operators.worst_curricula_removal,
            2: destroy_operators.random_lecture_removal,
            3: destroy_operators.random_dayperiod_removal,
            4: destroy_operators.random_roomday_removal,
            5: destroy_operators.random_teacher_removal,
            6: destroy_operators.restricted_roomcourse_removal
        }

        # Initial weights of repair operators set to 1
        self.repair_operators_weights = {
            "0": 1,
            "1": 1,
            "2": 1}


        # array of repair operators methods with touple of position (key) and value (method name)
        self.repair_operators = {
            0: repair_operators.two_stage_repair_operator,
            1: repair_operators.one_stage_repair_operator,
            2: maxSAT.solve
        }
    
    # main function to find solution of CB-CTT instance using ALNS
    def find_optimal_solution(self, solution):
    
        obj_func_instance = objective_function("UD2", self.instance_data)
    
        current_best = solution
    
        # Calculate cost/objective function of current solution
        current_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(solution)
    
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

            removal_operators_probabilities = roulette_wheel_selection.get_probability_list(self.removal_operators_weights)
            removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)

            repair_operators_probabilities = roulette_wheel_selection.get_probability_list(self.repair_operators_weights)
            repair_operator_index = roulette_wheel_selection.spin_roulettewheel(repair_operators_probabilities)
    
            # Find neighbor solution by applying destruction/repair operator to the current solution
            new_sol = self.neighbor(solution, iteration, remaining_iterations, removal_operator_index, repair_operator_index, course_penalties, curriculum_penalties)

            if new_sol is not None:
                # Calculate the new solution's cost
                new_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(new_sol)

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

                # recalcuate weights of removal operators based on the accepted solution
                self.removal_operators_weights[str(removal_operator_index)] = lambda_param * self.removal_operators_weights[str(removal_operator_index)] + (1-lambda_param) * psi
                self.repair_operators_weights[str(repair_operator_index)] = lambda_param * self.repair_operators_weights[str(removal_operator_index)] + (1-lambda_param) * psi

            else:
                print("None")
        # print('ALNS main exec END')
        print('===============================\n')
        print(global_best_cost)
        print('===============================\n')
        return global_best, global_best_cost
    
    def neighbor(self, solution, iteration, remaining_iterations, removal_operator_index, repair_operator_index, courses_penalties, curricula_penalties):
    
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
    
    
        if removal_operator_index == 0:
            schedule, lectures_removed = self.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, courses_penalties)
        elif removal_operator_index == 1:
            schedule, lectures_removed = self.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, curricula_penalties)
        else:
            schedule, lectures_removed = self.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data)


        schedule = repair_operators.two_stage_repair_operator(schedule, lectures_removed, self.instance_data)
        # print('\nremoved: ',len(lectures_removed))
    
        # lines = []
        #
        # for i in range(self.instance_data.days):
        #     for j in range(self.instance_data.periods_per_day):
        #         for k in range(self.instance_data.rooms_count):
        #             if schedule[i][j][k] != "":
        #                 line = schedule[i][j][k] + " " + self.instance_data.rooms[k].id + " " + str(i) + " " + str(
        #                     j) + '\n'
        #                 lines.append(line)
        #
        # for lecture in lectures_removed:
        #     line = lecture + " " + "-1" + " " + "-1" + " " + "-1" + '\n'
        #     lines.append(line)
        #
        # schedule = maxSAT.solve(self.instance_data, lines)

        return schedule
    
    def execute(self):
        
        # Generate initial solution

        initial_solution_instance = initial_solution(self.instance_data)

        init_sol = initial_solution_instance.generate_solution()

        # # MIP TESTS
        #
        # initial_solution = [[["" for k in range(len(self.instance_data.rooms))] for j in range(self.instance_data.periods_per_day)] for i in range(self.instance_data.days)]
        #
        # mip_instance = mip_operator(self.instance_data)
        #
        # result = mip_instance.repair()
        #
        # for c in range(len(self.instance_data.courses)):
        #     for d in range(int(self.instance_data.days)):
        #         for p in range(int(self.instance_data.periods_per_day)):
        #             for r in range(int(self.instance_data.rooms_count)):
        #                 if result[c][d][p][r].x > 0.99:
        #                     initial_solution[d][p][r] = self.instance_data.courses[c].id
        #
        # print('qendresa',' init sol', initial_solution)
        #
        # obj_func_instance = objective_function("UD2", self.instance_data)
        #
        # # # Calculate cost/objective function of current solution
        # current_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(init_sol)
        # qendresa = current_cost
        # print('INITIAL SOLUTION COST: ', current_cost)
        #
        # # END MIP TESTS

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
