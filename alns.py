import xml_to_od
import ectt_to_od
from objective_function import objective_function
from initial_solution import initial_solution
from roulette_wheel_selection import roulette_wheel_selection
from simulated_annealing import simulated_annealing
from alns_destroy_operators import destroy_operators
from Entities.xml_instance import xml_instance
from maxSAT_repair_operator import maxSAT
import random
import math
import os
import time

# Get data from XML File
xmldata = ectt_to_od.ectt_data()
# xmldata = xml_to_od.xml_data()


instance_data = xml_instance(xmldata.days(),
                             xmldata.periods(),
                             xmldata.min_daily_lectures(),
                             xmldata.max_daily_lectures(),
                             xmldata.courses(),
                             xmldata.rooms(),
                             xmldata.curricula(),
                             xmldata.period_constraints(),
                             xmldata.room_contraints())

# Initial weights of removal operators set to 1
removal_operators_weights = {
    "0": 1,
    "1": 1,
    "2": 1,
    "3": 1,
    "4": 1,
    "5": 1,
    "6": 1}


# array of removal operators methods with touple of position (key) and value (method name)
removal_operators = {
    0: destroy_operators.worst_courses_removal,
    1: destroy_operators.worst_curricula_removal,
    2: destroy_operators.random_lecture_removal,
    3: destroy_operators.random_dayperiod_removal,
    4: destroy_operators.random_roomday_removal,
    5: destroy_operators.random_teacher_removal,
    6: destroy_operators.restricted_roomcourse_removal
}


# main function to find solution of CB-CTT instance using ALNS
def find_optimal_solution(solution):

    obj_func_instance = objective_function("UD2", instance_data)

    current_best = solution

    # Calculate cost/objective function of current solution
    current_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(solution)

    global_best = current_best
    global_best_cost = current_cost

    w1 = 30  # score for new global best
    w2 = 15  # score for accepted
    w3 = 10  # score for better then current solution

    time_limit = 480
    iteration_limit = 200000

    time_start = time.time()

    SA = simulated_annealing(current_cost)

    iteration = 0

    while (time.time() - time_start) < time_limit:

        iteration += 1
        remaining_iterations = iteration_limit - ((time.time()-time_start)/time_limit)*iteration_limit


        removal_operators_probabilities = roulette_wheel_selection.get_probability_list(removal_operators_weights)
        removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)

        # Find neighbor solution by applying destruction/repair operator to the current solution
        new_sol = neighbor(instance_data, solution, iteration, remaining_iterations, removal_operator_index, course_penalties, curriculum_penalties)

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
            score_w2 = w2
            if new_cost < current_cost:
                score_w3 = w3

        if new_cost < global_best_cost:
            global_best = new_sol
            global_best_cost = new_cost
            score_w1 = w1

        psi = max(score_w1, score_w2, score_w3)
        lambda_param = 0.8

        # recalcuate weights of removal operators based on the accepted solution
        removal_operators_weights[str(removal_operator_index)] = lambda_param * removal_operators_weights[str(removal_operator_index)] + (1-lambda_param) * psi

    print('===============================')
    print(global_best_cost)
    return global_best


def neighbor(instance_data, solution, iteration, remaining_iterations,removal_operator_index, courses_penalties, curricula_penalties):

    lectures_counter = 0
    for course in instance_data.courses:
        lectures_counter += int(course.lectures)

    #  The reference destroy limit nmax 0 is set to d percent of the total number of lectures.
    #  It turns out that the usage of different percentages depending on the instance size is beneficial,
    #  i.e., ds is used for small instances with less than 280 lectures and dl for larger instances.

    if lectures_counter <= 280:
        reference_destroy_limit = math.floor(0.30 * lectures_counter)
    else:
        reference_destroy_limit = math.floor(0.25 * lectures_counter)

    expected_iteration_limit = remaining_iterations + iteration
    destroy_decrease_parameter = 3
    destroy_limit = math.floor(reference_destroy_limit - math.pow(iteration, math.log((((destroy_decrease_parameter - 1)/destroy_decrease_parameter)*reference_destroy_limit), expected_iteration_limit)))
    print('destroy limit', destroy_limit)

    lectures_to_remove = random.randint(1, destroy_limit)
    print('lectures_to_remove', lectures_to_remove)

    selection_probability = 5

    if removal_operator_index == 0:
        schedule, lectures_removed = removal_operators[removal_operator_index](solution, lectures_to_remove, instance_data, courses_penalties, selection_probability)
    elif removal_operator_index == 1:
        schedule, lectures_removed = removal_operators[removal_operator_index](solution, lectures_to_remove, instance_data, curricula_penalties, selection_probability)
    else:
        schedule, lectures_removed = removal_operators[removal_operator_index](solution, lectures_to_remove, instance_data)

    print('removed: ',len(lectures_removed))

    lines = []

    for i in range(instance_data.days):
        for j in range(instance_data.periods):
            for k in range(len(instance_data.rooms)):
                if schedule[i][j][k] != "":
                    line = schedule[i][j][k] + " " + instance_data.rooms[k].id + " " + str(i) + " " + str(
                        j) + '\n'
                    lines.append(line)

    for lecture in lectures_removed:
        line = lecture + " " + "-1" + " " + "-1" + " " + "-1" + '\n'
        lines.append(line)

    schedule = maxSAT.solve(instance_data, lines)

    return schedule


# Generate initial solution
initial_solution_instance = initial_solution(instance_data)

initial_solution = initial_solution_instance.generate_solution()

try:
    os.remove('/home/administrator/Downloads/file_to_write')
except OSError:
    pass
with open('/home/administrator/Downloads/file_to_write', 'a+') as f:
    # print solution  to console
    for i in range(instance_data.days):
        for j in range(instance_data.periods):
            for k in range(len(instance_data.rooms)):
                if initial_solution[i][j][k] != "":
                    line = initial_solution[i][j][k] + " " + instance_data.rooms[k].id + " " + str(i) + " " + str(j) + '\n'
                    f.write(line)


#
schedule = find_optimal_solution(initial_solution)

print('success')

