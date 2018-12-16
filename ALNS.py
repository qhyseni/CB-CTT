import XMLtoOD
import ObjectiveFunction
import InitialSolution
from random import randint
import random
import math


def worst_courses_removal(schedule, course_penalties, destroy_limit, xmldata, selection_probability):

    lectures_removed = []

    sorted_course_penalties = sorted(course_penalties.items(), key=lambda kv: kv[1], reverse=True)
    courses_count = len(sorted_course_penalties)
    while destroy_limit > 0:
        upsilon = random.random()
        index_for_removal = math.floor(courses_count * (upsilon ** selection_probability))
        a = sorted_course_penalties[index_for_removal]
        del sorted_course_penalties[index_for_removal]

        for i in range(xmldata.Days):
            for j in range(xmldata.PeriodsPerDay):
                for k in range(len(xmldata.Rooms)):
                    lecture = schedule[i][j][k]
                    if lecture != 0 and lecture[1] == a[0]:
                        lectures_removed.append(lecture)
                        schedule[i][j][k] = 0
        destroy_limit -= 1

    return schedule, lectures_removed


def worst_curricula_removal(schedule, curriculum_penalties, destroy_limit, xmldata, selection_probability):

    lectures_removed = []

    sorted_curriculum_penalties = sorted(curriculum_penalties.items(), key=lambda kv: kv[1], reverse=True)
    curricula_count = len(sorted_curriculum_penalties)
    while destroy_limit > 0:
        upsilon = random.random()
        index_for_removal = math.floor(curricula_count * (upsilon ** selection_probability))
        a = sorted_curriculum_penalties[index_for_removal]
        del sorted_curriculum_penalties[index_for_removal]

        for i in range(xmldata.Days):
            for j in range(xmldata.PeriodsPerDay):
                for k in range(len(xmldata.Rooms)):
                    lecture = schedule[i][j][k]
                    if lecture != 0 and lecture[1] == a[0]:
                        lectures_removed.append(lecture)
                        schedule[i][j][k] = 0
        destroy_limit -= 1

    return schedule, lectures_removed


# The random destroy operator removes lectures from the schedule at random.
def random_lecture_removal(schedule, destroy_limit, xmldata):

    lectures_removed = []

    while destroy_limit > 0:
        day = randint(0, xmldata.Days - 1)
        period = randint(0, xmldata.PeriodsPerDay - 1)
        room = randint(0, len(xmldata.Rooms) - 1)

        lectures_removed.append(schedule[day][period][room])
        schedule[day][period][room] = 0

    return schedule, lectures_removed

# The random destroy operator removes lectures from the schedule at random.
def random_dayperiod_removal(schedule, destroy_limit, xmldata):

    lectures_removed = []

    while destroy_limit > 0:
        day = randint(0, xmldata.Days - 1)
        period = randint(0, xmldata.PeriodsPerDay - 1)

        for k in range(len(xmldata.Rooms)):
            lectures_removed.append(schedule[day][period][k])
            schedule[day][period][k] = 0

            destroy_limit -= 1

    return schedule, lectures_removed


# The random destroy operator removes lectures from the schedule at random.
def random_roomday_removal(schedule, destroy_limit, xmldata):

    lectures_removed = []

    while destroy_limit > 0:
        day = randint(0, xmldata.Days - 1)
        room = randint(0, len(xmldata.Rooms) - 1)

        for j in range(xmldata.PeriodsPerDay):
            lectures_removed.append(schedule[day][j][room])
            schedule[day][j][room] = 0

            destroy_limit -= 1

    return schedule, lectures_removed


# The random destroy operator removes lectures from the schedule at random.
def random_teacher_removal(schedule, destroy_limit, xmldata):

    lectures_removed = []

    teachers = list(set([o.TeacherId for o in xmldata.Courses]))

    while destroy_limit > 0:

        rand_teacher = random.choice(teachers)

        for i in range(xmldata.Days):
            for j in range(xmldata.PeriodsPerDay):
                for k in range(len(xmldata.Rooms)):
                    lecture = schedule[i][j][k]
                    if lecture != 0 and lecture[2] == rand_teacher:
                        lectures_removed.append(lecture)
                        schedule[i][j][k] = 0

            destroy_limit -= 1

    return schedule, lectures_removed


# Get data from XML File
xmldata = XMLtoOD.XMLData()

# Generate initial solution
initial_solution_instance = InitialSolution.InitialSolution(xmldata)
initial_solution = initial_solution_instance.generate_solution()

course_penalties = dict()
curriculum_penalties = dict()

courses = xmldata.Courses
curricula = xmldata.Curricula


for course in courses:
    course_penalties[course.Id] = 0

for curriculum in curricula:
    curriculum_penalties[curriculum.Id] = 0


obj_func_instance = ObjectiveFunction.ObjectiveFunction("UD2", xmldata)

old_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(initial_solution, course_penalties)
destroy_limit = math.floor(0.2 * len(xmldata.Courses))

# blah = worst_removal(initial_solution, course_penalties, destroy_limit, xmldata, 5)


#
# def anneal(sol):
#
#     obj_func_instance = ObjectiveFunction("UD2", xmldata)
#
#     old_cost = obj_func_instance.cost(initial_solution)
#
#     T = 1.0
#     T_min = 0.00001
#     alpha = 0.9
#
#     while T > T_min:
#
#         new_sol = neighbor(sol)
#         new_cost = cost(new_sol)
#         ap = acceptance_probability(old_cost, new_cost, T)
#         if ap > random():
#             sol = new_sol
#             old_cost = new_cost
#
#         T = T*alpha
#     return sol, cost