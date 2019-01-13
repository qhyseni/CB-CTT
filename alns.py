import xml_to_od
from objective_function import objective_function
from initial_solution import  initial_solution
from roulette_wheel_selection import roulette_wheel_selection
from alns_operators import operators
from Entities.xml_instance import xml_instance
import random
import math




# Get data from XML File
xmldata = xml_to_od.xml_data()

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

def anneal(solution):


    obj_func_instance = objective_function("UD2", instance_data)

    current_best = solution
    # Calculate cost/objective function of vurrent solution
    current_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(current_best)

    global_best = current_best
    global_best_cost = current_cost

    w1, w2, w3 = 1

    T = 1.0
    T_min = 0.00001
    alpha = 0.9

    while T > T_min:

        # Find neighbor solution by applying destruction/repair operator to the current solution
        new_sol = neighbor(current_best, removal_operators_weights)

        # Calculate the new solution's cost
        new_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(new_sol)

        # The acceptance probability function takes in the old cost, new cost, and current temperature
        # and spits out a number between 0 and 1, which is a sort of recommendation on whether or not to jump to the new solution.
        acceptance_prob = acceptance_probability(current_cost, new_cost, T)

        if acceptance_prob > random():
            solution = new_sol
            current_cost = new_cost
            new_accepted = w1

        if new_cost < global_best_cost:
            global_best = new_sol
            new_best = w2

        if new_cost < current_cost:
            new_current = w3

        psi = max(new_accepted, new_best, new_current)

        # Usually, the temperature is started at 1.0 and is decreased
        # at the end of each iteration by multiplying it by a constant called α
        T = T*alpha

    return solution


def acceptance_probability(old_cost, new_cost, T):

    return math.e**((new_cost-old_cost)/T)


def neighbor(solution, removal_operators_weights):

    removal_operators_probabilities = roulette_wheel_selection.get_probability_list(removal_operators_weights)
    removal_operator_index = roulette_wheel_selection.spin_roulettewheel(removal_operators_probabilities)

    # removal_operators[removal_operator_index](solution, )


# Generate initial solution
initial_solution_instance = initial_solution(instance_data)
initial_solution = initial_solution_instance.generate_solution()

schedule = anneal(initial_solution)

destroy_limit = math.floor(0.2 * len(instance_data.courses))





# x1,  x2 = worst_courses_removal(initial_solution, course_penalties, destroy_limit, xmldata, 5)
# x1,  x2 = worst_curricula_removal(initial_solution, curriculum_penalties, destroy_limit, xmldata, 5)
# x1,  x2 = random_lecture_removal(initial_solution, destroy_limit, xmldata)
# x1,  x2 = random_dayperiod_removal(initial_solution, destroy_limit, xmldata)
# x1,  x2 = random_roomday_removal(initial_solution, destroy_limit, xmldata)
# x1,  x2 = random_teacher_removal(initial_solution, destroy_limit, xmldata)