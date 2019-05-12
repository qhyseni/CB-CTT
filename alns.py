import xml_to_od
import ectt_to_od
from objective_function import objective_function
from initial_solution import initial_solution
from roulette_wheel_selection import roulette_wheel_selection
from alns_operators import operators
from Entities.xml_instance import xml_instance
import random
import math
import subprocess
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

removal_operators_weights = {
    "0": 1,
    "1": 1,
    "2": 1,
    "3": 1,
    "4": 1,
    "5": 1}

removal_operators = {
    0: operators.worst_courses_removal,
    1: operators.worst_curricula_removal,
    2: operators.random_lecture_removal,
    3: operators.random_dayperiod_removal,
    4: operators.random_roomday_removal,
    5: operators.random_teacher_removal
}
#

def anneal(solution):
    obj_func_instance = objective_function("UD2", instance_data)

    current_best = solution
    # Calculate cost/objective function of vurrent solution
    current_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(solution)

    global_best = current_best
    global_best_cost = current_cost

    w1 = 30  # score for new global best
    w2 = 15  # score for accepted
    w3 = 10  # score for better then current solution

    T = 10000.0
    T_min = 0.00001
    alpha = 0.9

    # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

    init_deterioriation = 0.04
    initial_acceptance = 0.5


    # T = - init_deterioriation / math.log(initial_acceptance) * solution
    time_start = time.time()
    time_all_cost =0

    iteration = 0


    while T > T_min:

        iteration += 1
        print('iteration:',iteration)

        time_iteration_start = time.time()

        removal_operators_probabilities = roulette_wheel_selection.get_probability_list(removal_operators_weights)
        removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)

        # Find neighbor solution by applying destruction/repair operator to the current solution
        new_sol = neighbor(solution, removal_operator_index, instance_data, course_penalties, curriculum_penalties)

        # Calculate the new solution's cost
        new_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(new_sol)

        # The acceptance probability function takes in the old cost, new cost, and current temperature
        # and spits out a number between 0 and 1, which is a sort of recommendation on whether or not to jump to the new solution.
        acceptance_prob = acceptance_probability(current_cost, new_cost, T)

        score_w1 = 0
        score_w2 = 0
        score_w3 = 0


        if acceptance_prob > random.uniform(0, 1):
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

        time_iteration_cost = time.time() - time_iteration_start
        time_all_cost += time_iteration_cost
        print(time_iteration_cost)

        # iteration limit is calculated
        # iteration_limit = 170
        # expected number of remaining iterations
        # remaining_iterations = iteration_limit * (1 - ((time.time() - time_start) / 480))
        # Usually, the temperature is started at 1.0 and is decreased
        # at the end of each iteration by multiplying it by a constant called α
        # alpha = (T_min / T) ** (1 / remaining_iterations)
        T = T * alpha

    print('===============================')
    print(global_best_cost)
    return global_best



def acceptance_probability(old_cost, new_cost, T):
    if new_cost <= old_cost:
        return 1.0
    else:
        cost_diff = new_cost - old_cost
        return math.e ** (-(cost_diff) / T)



def neighbor(solution, removal_operator_index, instance_data, courses_penalties, curricula_penalties):

    lectures_counter = 0
    for course in instance_data.courses:
        lectures_counter += int(course.lectures)

    #  The reference destroy limit nmax 0 is set to d percent of the total number of lectures.
    #  It turns out that the usage of different percentages depending on the instance size is beneficial,
    #  i.e., ds is used for small instances with less than 280 lectures and dl for larger instances.
    if lectures_counter <= 280:
        destroy_limit = random.randint(1, math.floor(0.30 * lectures_counter))
    else:
        destroy_limit = random.randint(1, math.floor(0.25 * lectures_counter))

    # destroy_limit = lectures_counter

    selection_probability = 5

    if removal_operator_index == 0:
        schedule, lectures_removed = removal_operators[removal_operator_index](solution, destroy_limit, instance_data, courses_penalties, selection_probability)
    elif removal_operator_index == 1:
        schedule, lectures_removed = removal_operators[removal_operator_index](solution, destroy_limit, instance_data, curricula_penalties, selection_probability)
    else:
        schedule, lectures_removed = removal_operators[removal_operator_index](solution, destroy_limit, instance_data)

    print('removed: ',len(lectures_removed))
    try:
        os.remove('/tmp/partial')
    except OSError:
        pass
    with open('/tmp/partial', 'a+') as f:
        print('')
        # print solution  to console
        for i in range(instance_data.days):
            for j in range(instance_data.periods):
                for k in range(len(instance_data.rooms)):
                    if schedule[i][j][k] != "":
                        line = schedule[i][j][k]+" "+instance_data.rooms[k].id+" " + str(i) + " "+ str(j)+'\n'
                        f.write(line)

        for lecture in lectures_removed:
            line = lecture + " " + "-1" + " " + "-1" + " " + "-1" +'\n'
            f.write(line)

    subprocess.check_output(
                        ['java', '-jar',
                         '/home/administrator/Documents/thesis/cb-ctt/cb-ctt.jar',
                         '/home/administrator/Documents/thesis/datasets/comp01.ectt',
                         '/tmp/partial',
                         '/home/administrator/Documents/thesis/cb-ctt/output.txt',
                         '/home/administrator/Documents/thesis/cb-ctt/Open-LinSBPS_static'])

    schedule =  [[["" for k in range(len(instance_data.rooms))] for j in range(instance_data.periods)] for i in range(instance_data.days)]
    with open('/home/administrator/Documents/thesis/cb-ctt/output.txt', "r") as content:
        for line in content:
            values = line.rstrip('\n').split(' ')
            if values != ['']:
                day = int(values[2])
                period = int(values[3])
                room = instance_data.rooms.index(next((i for i in instance_data.rooms if i.id == values[1]), None))
                schedule[day][period][room] = values[0]



    return schedule
    # schedule = operators.repair_operator(schedule, lectures_removed)


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
schedule = anneal(initial_solution)

print('success')

# x1,  x2 = worst_courses_removal(initial_solution, course_penalties, destroy_limit, xmldata, 5)
# x1,  x2 = worst_curricula_removal(initial_solution, curriculum_penalties, destroy_limit, xmldata, 5)
# x1,  x2 = random_lecture_removal(initial_solution, destroy_limit, xmldata)
# x1,  x2 = random_dayperiod_removal(initial_solution, destroy_limit, xmldata)
# x1,  x2 = random_roomday_removal(initial_solution, destroy_limit, xmldata)
# x1,  x2 = random_teacher_removal(initial_solution, destroy_limit, xmldata)
