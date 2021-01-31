import xml_to_od
from _ectt_to_od import ectt_data
from Models.instance import instance
from _objective_function import objective_function
from _initial_solution import initial_solution
from _roulette_wheel_selection import roulette_wheel_selection
from _simulated_annealing import simulated_annealing
from _operators_lookup import operators_lookup
import random
import math
import os
import time
from Experiments.parameters import parameters
from Experiments.configs import configs
from Experiments.statistics import statistics

class alns:

    def __init__(self):

        # Get data from instance file
        if configs.instance_type == 1:
            raw_data = xml_to_od.xml_data()
        else:
            raw_data = ectt_data()

        self.instance_data = instance(raw_data)

        #  It turns out that the usage of different percentages depending on the instance size is beneficial,
        #  i.e., ds is used for small instances with less than 280 lectures and dl for larger instances.
        if self.instance_data.total_lectures <= 280:
            self.destroy_permille = parameters.ds
        else:
            self.destroy_permille = parameters.dl


    # main function to find solution of CB-CTT instance using ALNS
    def find_optimal_solution(self, solution, Uc):
        # reset statistics value
        statistics_instance = statistics()
        statistics_instance.reset()

        obj_func_instance = objective_function("UD2", self.instance_data)

        current_best = solution
    
        # Calculate cost/objective function of current solution
        current_cost, courses_penalties, curricula_penalties = obj_func_instance.cost(solution)

        avg_cost = current_cost / self.instance_data.total_lectures
        unassigned_lectures_cost = max(float(1), float(avg_cost))
        current_cost += unassigned_lectures_cost * len(Uc)

        global_best = current_best
        global_best_cost = current_cost

        if global_best_cost == 0:
            return global_best, global_best_cost

        #  The reference destroy limit nmax 0 is set to d percent of the total number of lectures.
        # calculate upper bound for events to be destoryed
        destroy_upper_bound = self.instance_data.total_lectures * self.destroy_permille
        iteration = 0
        no_best_found_count = 0
        # destroy limit based on iterations since limit -> limit increased after reheat
        iterations_since_reheat = 0
        remaining_iterations = parameters.iteration_limit
        ref_iter_limit = parameters.iteration_limit

        time_start = time.time()
    
        SA = simulated_annealing(current_cost)

        while (time.time() - time_start) < parameters.time_limit:
            deviation_ref_iter = (remaining_iterations + iterations_since_reheat) - ref_iter_limit
            destroy_decrease_power = math.log((parameters.destroy_decrease - 1) * destroy_upper_bound / parameters.destroy_decrease) \
                                     / math.log(ref_iter_limit + deviation_ref_iter)
            iteration += 1
            iterations_since_reheat += 1
            statistics.iterations += 1
            print("Iteration: ", iteration)
            remaining_iterations = parameters.iteration_limit - ((time.time()-time_start)/parameters.time_limit) * parameters.iteration_limit
            print("Remaining Iterations: ", remaining_iterations)
            # -------------------------------------------------------------------------------------------------------------------- #
            removal_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.removal_operators_weights)
            print("Removal Operators Probabilities: ", removal_operators_probabilities)
            removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)
            # removal_operator_index = 5

            repair_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.repair_operators_weights)
            print("Repair Operators Probabilities: ", repair_operators_probabilities)
            repair_operator_index = roulette_wheel_selection.spin_roulettewheel(repair_operators_probabilities)
            # repair_operator_index = 1

            lecture_period_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.lecture_period_operators_weights)
            print("Lecture-Period Operators Probabilities: ", lecture_period_operators_probabilities)
            lecture_period_operator_index = roulette_wheel_selection.spin_roulettewheel(lecture_period_operators_probabilities)
            # lecture_period_operator_index = 0
            if lecture_period_operator_index == 0:
                statistics.two_stage_best_count += 1
            elif lecture_period_operator_index == 1:
                statistics.two_stage_mean_count += 1

            lecture_room_operators_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.lecture_room_operators_weights)
            print("Lecture-Room Operators Probabilities: ", lecture_period_operators_probabilities)
            lecture_room_operator_index = roulette_wheel_selection.spin_roulettewheel(lecture_room_operators_probabilities)
            # lecture_room_operator_index = 0
            if lecture_period_operator_index == 0:
                statistics.two_stage_greatest_count += 1
            elif lecture_period_operator_index == 1:
                statistics.two_stage_match_count += 1

            priority_rules_probabilities = roulette_wheel_selection.get_probability_list(operators_lookup.priority_rules_weights)
            print("Priority Rules Probabilities: ", lecture_period_operators_probabilities)
            priority_rule_index = roulette_wheel_selection.spin_roulettewheel(priority_rules_probabilities)
            if lecture_period_operator_index == 0:
                statistics.saturation_degree_count += 1
            elif lecture_period_operator_index == 1:
                statistics.largest_degree_count += 1
            else:
                statistics.random_order_count += 1



            # -------------------------------------------------------------------------------------------------------------------- #
            # number of events to be destroyed (lectures to remove) in this iteration
            destroy_limit = min(self.instance_data.total_lectures - len(Uc), parameters.min_destroy_lectures +
                                (random.randrange(max(parameters.min_destroy_lectures, round(destroy_upper_bound) - round(math.pow(iterations_since_reheat, destroy_decrease_power))))))

            # Find neighbor solution by applying destruction/repair operator to the current solution
            new_sol, Uc = self.neighbor(solution, destroy_limit,
                                    removal_operator_index, repair_operator_index, lecture_period_operator_index, lecture_room_operator_index, priority_rule_index,
                                    courses_penalties, curricula_penalties, Uc)

            if statistics.backtrack_count > 0:
                rows = []

                for i in range(self.instance_data.days):
                    for j in range(self.instance_data.periods_per_day):
                        for k in range(self.instance_data.rooms_count):
                            if new_sol[i][j][k] != -1:
                                row = self.instance_data.courses_ids[new_sol[i][j][k]] + " " + \
                                      self.instance_data.rooms[
                                          k].id + " " + str(i) + " " + str(
                                    j) + '\n'
                                rows.append(row)

                # write formatted input to a file to be used by the next process (max-SAT)
                partial_temp_filename = 'C:/Users/vlere/qq/backtsol'

                with open(partial_temp_filename, 'w+') as f:
                    for row in rows:
                        f.write(row)

            if new_sol is not None:
                # Calculate the new solution's cost
                new_cost, courses_penalties, curricula_penalties = obj_func_instance.cost(new_sol)
                print("New solution cost: ", new_cost)

                temp_cost = new_cost + len(Uc) * unassigned_lectures_cost
                # The acceptance probability function takes in the old cost, new cost, and current temperature
                # and spits out a number between 0 and 1, which is a sort of recommendation on whether or not to jump to the new solution.
                accept = SA.accept_new_solution(temp_cost, current_cost, remaining_iterations)

                score_w1 = 0
                score_w2 = 0
                score_w3 = 0

                if accept:

                    if len(Uc) > 0:
                        unassigned_lectures_cost = min(unassigned_lectures_cost * parameters.adjust_unscheduled_cost,
                                                       float(self.instance_data.max_cost))
                    else:
                        unassigned_lectures_cost = max(float(1), unassigned_lectures_cost / parameters.adjust_unscheduled_cost)

                    statistics.accepted_count += 1
                    print("New solution accepted.")
                    if temp_cost > current_cost: # worse than current solution
                        print("New solution is worse than the current solution.")
                        statistics.worse_count += 1
                        score_w3 = parameters.w3
                    else: # better than current solution
                        print("New solution is better than the current solution.")
                        statistics.better_count += 1
                        score_w2 = parameters.w2

                    solution = new_sol
                    current_cost = temp_cost
                else:
                    print("New solution NOT accepted.")

                if new_cost < global_best_cost and len(Uc) == 0:
                    print("New solution is the global best.")
                    statistics.global_best_counts += 1
                    statistics.iteration_best = iteration
                    statistics.time_best = time.time() - time_start
                    global_best = new_sol
                    global_best_cost = new_cost
                    score_w1 = parameters.w1

                if no_best_found_count >= parameters.reheat_limit and iteration < parameters.iteration_limit:
                    SA.reheat(new_cost)
                    no_best_found_count = 0
                    statistics.reheats_count += 1
                    iterations_since_reheat = 0
                    ref_iter_limit = remaining_iterations
                else:
                    no_best_found_count += 1

                if global_best_cost == 0:
                    return global_best, global_best_cost

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
    
    def neighbor(self, solution, destroy_limit,
                 removal_operator_index, repair_operator_index, lecture_period_operator_index, lecture_room_operator_index, priority_rule_index,
                 courses_penalties, curricula_penalties, Uc):

        print("Destroy Limit: ", destroy_limit)
        lectures_to_remove = random.randint(1, destroy_limit)
        print("Lectures to remove number: ", lectures_to_remove)

        # different destroy operators expect different input parameters
        # we are handling it accordingly below
        # removal_operator_index = 5
        if removal_operator_index == 0:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, courses_penalties)
        elif removal_operator_index == 1:
            schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data, curricula_penalties)
        else:
                schedule, lectures_removed = operators_lookup.removal_operators[removal_operator_index](solution, lectures_to_remove, self.instance_data)

        # append lectured left unscheduled from prev row
        for l in Uc:
            lectures_removed.append(l)

        # repair_operator_index = 0
        # lecture_period_operator_index = 0
        # lecture_room_operator_index = 0
        # priority_rule_index = 0
        if repair_operator_index == 0:
            schedule, Uc = operators_lookup.repair_operators[repair_operator_index](schedule, self.instance_data, lectures_removed,
                                                                                operators_lookup.lecture_period_operators[lecture_period_operator_index],
                                                                                operators_lookup.lecture_room_operators[lecture_room_operator_index],
                                                                                operators_lookup.priority_rules[priority_rule_index])
        elif repair_operator_index == 1:
            schedule = operators_lookup.repair_operators[repair_operator_index](schedule, self.instance_data, lectures_removed)

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

        schedule, cost = self.find_optimal_solution(init_sol, Uc)

        return schedule, cost
