import random
import copy
from Experiments.statistics import statistics
from _alns_helpers import alns_helpers
from Models.period_course import period_course
from Experiments.parameters import parameters
from Models.population import population_member
from _objective_function import objective_function
from _ga_operators_lookup import mutation_operators


class ga_steady_state_repair_operator:

    ###################### Repair operators #############################################

    # init method or constructor
    def __init__(self):
        print()

    def execute(schedule, instance_data, unscheduled_lectures):
        print("GA Steady State Mutation Repair Operator")
        statistics.ga_steady_state_count += 1

        obj_func_instance = objective_function("UD2", instance_data)
        population = []

        for i in range(parameters.pop_size):
            new_schedule = ga_steady_state_repair_operator.generate_initial_solution(schedule, instance_data, unscheduled_lectures)
            fitness= obj_func_instance.cost(new_schedule)
            member = population_member(i, new_schedule, fitness[0])
            population.append(member)

        tournament_size = int((parameters.tournament_size * parameters.pop_size) / 100)
        mutation_rate = int((parameters.mutation_rate * instance_data.total_lectures) / 100)
        alternation_frequency = parameters.alternation_frequency
        mutate_operator = 0

        for i in range(parameters.max_generations):
            selected_best = ga_steady_state_repair_operator.tournament_selection(population, tournament_size)
            selected_best_clone = copy.deepcopy(selected_best.schedule)
            f = obj_func_instance.cost(selected_best_clone)[0]

            population.sort(key=lambda x: x.fitness, reverse=True)
            worst_in_population = population[0]

            if alternation_frequency == 0:
                # if it's not the last index of the operator move on to the next operator
                # otherwise go to the first operator
                if mutate_operator < 2:
                    mutate_operator += 1
                else:
                    mutate_operator = 0

            alternation_frequency -= 1

            selected_best_clone = mutation_operators.operators[mutate_operator](instance_data,
                                                                                       selected_best_clone,
                                                                                       mutation_rate)

            selected_best_fitness = obj_func_instance.cost(selected_best_clone)[0]

            if selected_best_fitness < worst_in_population.fitness:
                population.pop(population.index(worst_in_population))
                new_member = population_member(worst_in_population.id, selected_best_clone, selected_best_fitness)
                population.append(new_member)

        population.sort(key=lambda x: x.fitness)
        best = population[0].schedule

        return best

    #             popsize = population size - numri i kromozomeve ne nje gjenerate te popullates
    #             1. Initialise: generate a population of popsize random solutions, evaluate their fitnesses.
    #             2. Run 'Select' to obtain a parent solution X.
    #             3. With probability mute_rate, mutate a copy of X to obtain a mutant M (otherwise M = X)
    #             4. Evaluate the fitness of M.
    #             5. Let W be the current worst in the population (BTR). If
    #             M is not less fit than W, then replace W with M.//(otherwise do nothing)
    #             6. If a termination condition is met (e.g. we have done 10,000 evaluations) then stop. Otherwise go to 2



    def generate_initial_solution(schedule, instance_data, unscheduled_lectures):
        print("Generate initial solution")

        new_schedule = copy.deepcopy(schedule)

        lectures = copy.deepcopy(unscheduled_lectures)
        lectures_count = len(lectures)

        # store assignments (day/period/room) for each course
        visited_positions = {}
        period_lecture_assignments = []

        unscheduled_lectures.sort(key=lambda x: (instance_data.courses_students[x]), reverse=True)
        # unscheduled_lectures.sort(key=lambda x: (instance_data.courses_students[x], len(instance_data.courses_curricula[x]), instance_data.courses_lectures[x]), reverse=True)

        for rand_lecture in unscheduled_lectures:
        # while lectures_count > 0:
        #
        #     # get a random course to schedule by excluding those already visited
        #     rand_lecture_index = randrange(lectures_count)
        #     rand_lecture = lectures[rand_lecture_index]

            # check if the course has any available periods left
            available_periods = alns_helpers.check_periods_available(new_schedule, instance_data, rand_lecture, [])
            if len(available_periods) > 0:

                # Generate random day/period based on respective ranges and on availability
                dp = random.choice([[d,p] for d in range(instance_data.days) for p in range(instance_data.periods_per_day) if [d,p] in available_periods])

                rand_day = dp[0]
                rand_period = dp[1]

                # if visited_positions.get(rand_lecture) is not None and [rand_day, rand_period] in visited_positions[rand_lecture]:
                #     continue

                # check if random lecture is not allowed to be scheduled in this random period
                if [rand_day, rand_period] in instance_data.courses_periods_constraints[rand_lecture]:
                    continue

                feasible = True
                available_rooms = []

                for r in range(instance_data.rooms_count):
                    scheduled_course = new_schedule[rand_day][rand_period][r]
                    if scheduled_course == -1:
                        available_rooms.append(r)
                    else:
                        # check if the scheduled lecture and the one to be scheduled have teacher conflicts
                        # check if the scheduled lecture and the one to be scheduled have curricula conflicts
                        if ga_steady_state_repair_operator.are_conflicting_courses(instance_data, scheduled_course, rand_lecture):
                            feasible = False
                            break

                if feasible and len(available_rooms) > 0:
                    min_cost = 999999
                    selected_room = None
                    for r in available_rooms:
                        cost = alns_helpers.calculate_room_stability_cost(new_schedule, instance_data, rand_day, rand_period, rand_lecture, r)
                        room = instance_data.rooms[r]
                        if instance_data.courses_students[rand_lecture] > int(room.size):
                            cost += instance_data.courses_students[rand_lecture] - int(room.size)
                        if cost <= min_cost:
                            selected_room = r
                            min_cost = cost

                    if selected_room is not None:
                        new_schedule[rand_day][rand_period][selected_room] = rand_lecture
                        if visited_positions.get(rand_lecture) is None:
                            visited_positions[rand_lecture] = []
                        visited_positions[rand_lecture].append([rand_day,rand_period])
                        pc = period_course(rand_day, rand_period, rand_lecture)
                        period_lecture_assignments.append(pc)
                        # lectures.pop(rand_lecture_index)
                        lectures.pop(lectures.index(rand_lecture))
                        lectures_count -= 1

            else:
                # Backtracking
                for i in period_lecture_assignments:
                    if i.course != rand_lecture:
                        scheduled_course_available_periods = alns_helpers.check_periods_available(new_schedule, instance_data,
                                                                                 i.course, [])
                        # check if this course has other available periods
                        # so if removed it will have other feasible options for scheduling
                        if len(scheduled_course_available_periods) > 0:
                            # find room in which current course is schedule
                            for r in range(instance_data.rooms_count):
                                if new_schedule[i.day][i.period][r] == i.course:
                                    break
                            # check if the random course will get any available periods
                            # if we remove current scheduled course from the schedule
                            new_schedule[i.day][i.period][r] = -1
                            rand_course_available_periods = alns_helpers.check_periods_available(new_schedule, instance_data,
                                                                                 rand_lecture, [])

                            if len(rand_course_available_periods) > 0:
                                # remove current course from assignments list and add it to unscheduled lectures
                                # period_lecture_assignments.pop(rand_lecture_index)
                                period_lecture_assignments.pop(period_lecture_assignments.index(i))
                                lectures.append(i.course)
                                lectures_count += 1
                                break
                            else:
                                new_schedule[i.day][i.period][r] = i.course

        return new_schedule

    def are_conflicting_courses(instance_data, c1, c2):
        # check if the scheduled lecture and the one to be scheduled have teacher conflicts
        if instance_data.courses_teachers[c1] == instance_data.courses_teachers[c2]:
            return True

        # check if the scheduled lecture and the one to be scheduled have curricula conflicts
        if not set(instance_data.courses_curricula[c1]).isdisjoint(
                instance_data.courses_curricula[c2]):
            return True

        return False

    def tournament_selection(population, tournament_size):
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