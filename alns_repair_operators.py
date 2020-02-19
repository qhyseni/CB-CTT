import random
from random import randint, shuffle
import math
from parameters import parameters
from itertools import groupby
import collections
from collections import OrderedDict
from Entities.penalty import penalty
from Entities.period_course import period_course
from configs import configs
import os
import uuid
from objective_function import objective_function

class repair_operators:

    ###################### Repair operators #############################################
    def check_periods_available(schedule, instance_data, course, period_lecture_assignments):
        # print('check period is available')
        available_periods = []
        course_curricula = [i for i in instance_data.curricula if course.id in i.courses]

        for d in range(instance_data.days):
            for p in range(instance_data.periods_per_day):
                is_available = repair_operators.is_period_available(schedule, instance_data, course, course_curricula, period_lecture_assignments, d, p)
                if is_available:
                    available_periods.append([d, p])
                # else:
                # In case a course is in line that cannot be scheduled conflict-free, a backtracking mechanism is applied.
                # Only lectures that do not belong to the fixed part of the current schedule can be removed.
                # period_lecture_assignments contains all assignments of unscheduled lectures to periods, up to this point
                # hence we will create a new set of periods where the considered course c is allowed to remove lectures
                # OrderedDict is used to remove duplicates
                allowed_periods_for_removal = OrderedDict((tuple(x), x) for x in [[i.day, i.period] for i in period_lecture_assignments]).values()

                # next we need to evaluate each position in the allowed_periods_for_removal list

                for position in allowed_periods_for_removal:
                    # get list of courses/lectures that are scheduled during repair phase on this certain position
                    potential_replacement_lectures = [i.course for i in period_lecture_assignments if i.day == position[0] and i.period == position[1]]
                    lectures_to_remove = []
                    # evaluate position by checking if lectures assigned to that position are conflicting the current course
                    # check conflicts for curriculum and teacher
                    for r in range(instance_data.rooms_count):
                        conflicted = False
                        l = schedule[position[0]][position[1][r]]
                        for q in course_curricula:
                            if l in q.courses:
                                conflicted = True
                                break
                        temp_course - next(i for i in instance_data.courses if i.id == l)
                        if temp_course.techer_id == course.teacher_id:
                            conflicted = True
                        # if the lecture is not part of fixed schedule then we add it to an array which use for comparison purposes in later stage
                        if conflicted and l in potential_replacement_lectures:
                            lectures_to_remove.append(l)
                        # if the lecture that is conflicting is one of the fixed schedule lectures, that means that we cannot remove it
                        # hence we will break and move to the next allowed position (it means this is not allowed
                        # although we initially consider every position where we scheduled lectures during repair period as allowed
                        # as those position contain the lectured which we are able to remove
                        elif conflicted and l not in potential_replacement_lectures:
                            break





                    for l in potential_replacement_lectures:



                print(allowed_periods_for_removal)

        return available_periods

    def is_period_available(schedule, instance_data, course, course_curricula, period_lecture_assignments, d, p):

        assigned_lectures_to_period = [x.course for x in period_lecture_assignments if x.day == d and x.period == p]

        is_available = True
        period_constrained_course = next(
            (i for i in instance_data.period_constraints if i.course == course.id), None)

        rooms_available = 0
        if period_constrained_course is not None and [d, p] in period_constrained_course.timeslots:
            return False
        else:
            for r in range(instance_data.rooms_count):
                scheduled_course = next(
                    (i for i in instance_data.courses if i.id == schedule[d][p][r]), None)

                if scheduled_course is None:
                    rooms_available += 1
                else:
                    for q in course_curricula:
                        if scheduled_course.id in q.courses:
                            is_available = False
                            break
                    if not is_available:
                        break
                    else:
                        if scheduled_course.teacher_id == course.teacher_id:
                            is_available = False
                            break
        # even if after checking the feasibility in the fixed schedule regarding scheduling students of same curriculum at the same time
        # we need to check also againt lectures that are assigned to this period in previous steps
        # during repair operators
        if is_available:
            for q in course_curricula:
                for l in assigned_lectures_to_period:
                    if l in q.courses:
                        is_available = False
                        break
                if not is_available:
                    break
        # even if after checking the feasibility in the fixed schedule regarding scheduling courses with same teacher at the same time
        # we need to check also against lectures that are assigned to this period in previous steps
        # during repair operators
        if is_available:
            for l in assigned_lectures_to_period:
                current_lecture = next(
                    (i for i in instance_data.courses if i.id == l), None)
                if course.teacher_id == current_lecture.teacher_id:
                    is_available = False

        # if there are rooms available from the fixed schedule, check how many lectures are assigned to this period in previous stages
        # so we make sure we don't assign more lectures than rooms in any period
        if is_available and (rooms_available - len(assigned_lectures_to_period)) > 0:
            return True
        else: return False

    def check_periods_conflicts(schedule, instance_data, course):
        print('check course conflicts')
        course_conflicts = {}
        current_course = next(
            (i for i in instance_data.courses if i.id == course), None)
        course_curricula = [i for i in instance_data.curricula if course in i.courses]

        for d in range(instance_data.days):
            for p in range(instance_data.periods_per_day):
                for r in range(instance_data.rooms_count):
                    scheduled_course = next(
                        (i for i in instance_data.courses if i.id == schedule[d][p][r]), None)

                    if scheduled_course is not None and scheduled_course.id != course:
                        for q in course_curricula:
                            if scheduled_course.id in q.courses:
                                course_conflicts[scheduled_course.id] = [d,p]

                        if scheduled_course.teacher_id == current_course.teacher_id:
                                course_conflicts[scheduled_course.id] = [d,p]

        return course_conflicts


        
    def assign_lecture_to_period(schedule, unscheduled_lectures, instance_data):
        # vector of lectures that we fail to insert during the process
        Uc = []
        # remove duplicates so we can retrieve unique courses from the lectures list
        unscheduled_courses = list(dict.fromkeys(unscheduled_lectures))
        # List of period-course assignments
        period_lecture_assignments = []
        # sort unscheduled courses according to chosen priority rule
        sorted_courses = repair_operators.saturation_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments)
        # keep track of periods from which we remove once a course, so we avoid cycles
        forbidden_periods = {}

        while unscheduled_courses is not None and len(unscheduled_courses) > 0:

            # find first course to assign based on chosen priority rule
            course_to_assign = sorted_courses[0]

            course = next(
                (i for i in instance_data.courses if i.id == course_to_assign), None)

            # compute potential insertion positions (periods)
            Pc = repair_operators.check_periods_available(schedule, instance_data, course, period_lecture_assignments)
            # if we are not able to assign course to any period, we apply Backtracking
            # Backtracking will consider to remove only the lectures that are assigned during the repairing phase
            if len(Pc) == 0:
                i = len(period_lecture_assignments) - 1
                while i >= 0:
                    pc = period_course(i.day, i.period, course_to_assign)
                    if (period_lecture_assignments[i] == pc):
                        continue
                    is_period_available = is_period_available(schedule, instance_data, course, course_curricula, period_lecture_assignments,
                                        i.day, i.period)
                    # remove the course from the assigned period temporarily until we check for other availabilities
                    period_lecture_assignments.pop(period_lecture_assignments.index(i))
                    if (is_period_available):
                        # append the removed lecture to unscheduled_list so we try to find it another available position
                        unscheduled_lectures.append(period_lecture_assignments[i].course)
                        period_lecture_assignments.append(pc)
                        # insert new course to the found available position
                        fpc = period_course(i.day, i.period, i.course)
                        forbidden_periods[course_to_assign] = fpc

                    i -= 1

            # initialize list of periods from which course c can remove lectures Rc = Pc
            Rc = Pc

            # create dictionary with keys representing courses,
            # and values representing how many lectures should we assign per each course
            unscheduled_counter = unscheduled_lectures.count(course_to_assign)

            while unscheduled_counter > 0:
                if Pc is not None and len(Pc) > 0:
                    # evaluate all periods of Pc; return best;
                    P_best = Pc[repair_operators.evaluate_2stage(schedule, instance_data, unscheduled_lectures, unscheduled_courses, course_to_assign, Pc, 2)]
                    # insert the lecture to the best position in the schedule
                    pc = period_course(P_best[0], P_best[1], course_to_assign)
                    period_lecture_assignments.append(pc)
                    Rc.pop(Rc.index(P_best))
                elif Rc is not None and len(Rc) > 0:
                    # evaluate all periods of Rc; return best;
                    P_best = Rc[repair_operators.evaluate_2stage(schedule, instance_data, course_to_assign, Rc, unscheduled_courses, 2)]

                    # find conflicting courses for best position
                    conflict_courses = []

                    # remove conflicting courses from the schedule in best found position
                    for c in conflict_courses:
                        for r in range(instance_data.rooms_count):
                            schedule[P_best[0]][P_best[1]][r] = ''
                            # add removed lecture to other unscheduled lectures
                            unscheduled_lectures.append(c)
                            # append conflicting course in the beginning of the unscheduled courses
                            if c in unscheduled_courses:
                                unscheduled_courses.pop(c)
                                unscheduled_courses.insert(0,c)

                    # insert current course to best found position
                    pc = period_course(P_best[0], P_best[1], course_to_assign)
                    period_lecture_assignments.append(pc)
                    Rc.pop(Rc.index(P_best))

                else:
                    Uc.append(course_to_assign)

                unscheduled_counter = unscheduled_counter - 1

            unscheduled_courses.pop(unscheduled_courses.index(course_to_assign))
            # sort unscheduled courses according to chosen priority rule
            sorted_courses = repair_operators.saturation_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments)

        print('unscheduled lectures: ', unscheduled_lectures)
        return period_lecture_assignments

    def two_stage_repair_operator(schedule, unscheduled_lectures, instance_data):
        period_lecture_assignments = repair_operators.assign_lecture_to_period(schedule, unscheduled_lectures, instance_data)
        schedule = repair_operators.assign_lecture_to_room(schedule, unscheduled_lectures, instance_data, period_lecture_assignments, 1)
        return schedule
        print('FINAL SCHEDULE: ', schedule)

    def assign_lecture_to_room(schedule, unscheduled_lectures, instance_data, period_lecture_assignments, type):

        print('SCHEDULE: ', schedule)
        print('UNSCHEDULED LECTURES: ', unscheduled_lectures)
        print('PERIODS LECTURES LIST: ', [(i.day, i.period, i.course) for i in period_lecture_assignments])

        # select periods only from periods_lectures list and remove duplicates
        periods = set(map(tuple, [[x.day, x.period] for x in period_lecture_assignments]))
        # shuffle the periods list so we take the random approach in placing the lectures in rooms
        random.shuffle(list(periods))
        print('SHUFFLED PERIODS: ', periods)

        for p in periods:
            print('PERIOD: ', p)
            day = p[0]
            period = p[1]
            available_rooms = []
            for r in range(instance_data.rooms_count):
                if schedule[day][period][r] is '':
                    available_rooms.append(r)

            print('AVAILABLE ROOMS: ', available_rooms)

            lectures = [x.course for x in period_lecture_assignments if x.day == day and x.period == period]
            print('LECTURES: ', lectures)
            courses_to_schedule = [i for i in instance_data.courses if i.id in lectures]
            # type 1: greatest heuristic
            # sort courses in ascending order by number of students
            if type == 1:
                courses_to_schedule.sort(key=lambda x : int(x.students),reverse=True)
            # type 2: match heuristic
            # sort courses randomly
            else:
                random.shuffle(courses_to_schedule)

            print('COURSES TO SCHEDULE: ', [i.id for i in courses_to_schedule])

            for c in courses_to_schedule:
                print('COURSE: ', c.id)
                min_cost = 999999
                selected_room = None
                for r in available_rooms:
                    cost = repair_operators.calculate_room_stability_cost(schedule, instance_data, day, period, c.id, r)
                    room = instance_data.rooms[r]
                    if int(c.students) > int(room.size):
                        cost += int(c.students) - int(room.size)
                    # ties are broken by preferring the room with largest capacity
                    # the rationale behind this is to keep smaller rooms for courses with less students,
                    # which might be beneficial with regard to the room stability
                    if type == 1 and cost == min_cost and int(room.size) > int(instance_data.rooms[selected_room].size):
                            selected_room = r
                    # ties are broken by preferring the room with smallest capacity
                    # the reason is that since lectures are schedules in a random order,
                    # there might be lectures that are processed later and require large rooms
                    elif type == 2 and cost == min_cost and int(room.size) < int(instance_data.rooms[selected_room].size):
                            selected_room = r
                    elif cost < min_cost:
                        selected_room = r
                print('SELECTED ROOM: ', selected_room)
                schedule[day][period][selected_room] = c.id
                available_rooms.pop(available_rooms.index(selected_room))

        print('SCHEDULE FINAL: ', schedule)
        fname = '/tmp/comp01' + str(uuid.uuid4())
        with open(fname, 'a+') as f:
            # print solution  to console
            for i in range(instance_data.days):
                for j in range(instance_data.periods_per_day):
                    for k in range(len(instance_data.rooms)):
                        if schedule[i][j][k] != "":
                            line = schedule[i][j][k] + " " + instance_data.rooms[k].id + " " + str(i) + " " + str(j) + '\n'
                            f.write(line)

        obj_func_instance = objective_function("UD2", instance_data)

        # Calculate cost/objective function of current solution
        current_cost, course_penalties, curriculum_penalties = obj_func_instance.cost(schedule)

        print('FILENAME: ', fname)
        print('COST: ', current_cost)

        return schedule

    def lecture_to_room_greatest_heuristic(self):
        print('')

    def lecture_to_room_match_heuristic(self):
        print('')


    def evaluate_2stage(schedule, instance_data, unscheduled_lectures, unscheduled_courses, c, available_periods, type):

        course_period_cost = {}

        course = next((i for i in instance_data.courses if i.id == c), None)

        index = 0
        for p in available_periods:
            cost = 0
            day = p[0]
            period = p[1]

            ####### check compactness #######

            cost += repair_operators.calculate_compactness_cost(schedule, instance_data, day, period, c)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check spread in days #######

            cost += repair_operators.calculate_spread_days_cost(schedule, instance_data, day, c, course)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check room stability #######

            cost += repair_operators.calculate_room_stability_cost(schedule, instance_data, day, period, c, None)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check room capacity #######

            cost += repair_operators.calculate_room_capacity_cost(schedule, instance_data, unscheduled_lectures, day, period, course, type)

            ####### ####### ####### ####### ####### ####### ####### #######


            course_period_cost[index] = cost
            index += 1

        # sort in ascending order periods based on cost evaluated by 4 previous step
        # and return the first period as the best period to insert the course
        course_period_cost = {k: v for k, v in sorted(course_period_cost.items(), key=lambda item: item[1])}
        return list(course_period_cost.keys())[0]



    def calculate_compactness_cost(schedule, instance_data, day, period, c):

        penalty_instance = penalty(configs.cbctt_type)
        cost = 0
        if period == 0:
            isolated = repair_operators.calculate_comp_cost(schedule, instance_data, c, day, period + 1)
            if isolated:
                cost += penalty_instance.get_isolated_lectures_penalty()
            else:
                cost -= penalty_instance.get_isolated_lectures_penalty()

        elif period == instance_data.periods_per_day - 1:
            isolated = repair_operators.calculate_comp_cost(schedule, instance_data, c, day, period - 1)
            if isolated:
                cost += penalty_instance.get_isolated_lectures_penalty()
            else:
                cost -= penalty_instance.get_isolated_lectures_penalty()

        else:
            left_isolated = repair_operators.calculate_comp_cost(schedule, instance_data, c, day, period - 1)
            right_isolated = repair_operators.calculate_comp_cost(schedule, instance_data, c, day, period + 1)
            if left_isolated and right_isolated:
                cost += penalty_instance.get_isolated_lectures_penalty()
            elif not left_isolated or not right_isolated:
                cost -= penalty_instance.get_isolated_lectures_penalty()

        return cost

    def calculate_comp_cost(schedule, instance_data, c, day, period):

        course_curricula = [i for i in instance_data.curricula if c in i.courses]

        isolated = True
        for r in range(instance_data.rooms_count):
            course = schedule[day][period][r]
            for q in course_curricula:
                if course in q.courses:
                    isolated = False
                    break
            if not isolated:
                break

        return isolated

    def calculate_spread_days_cost(schedule, instance_data, day, c, course):

        penalty_instance = penalty(configs.cbctt_type)
        spread = 0
        cost = 0
        course_in_existing_day = False
        for d in range(instance_data.days):
            course_scheduled_in_day = False
            for p in range(instance_data.periods_per_day):
                for r in range(instance_data.rooms_count):
                    if schedule[d][p][r] == c:
                        course_scheduled_in_day = True
                        spread += 1
                        if d == day:
                            course_in_existing_day = True
                        break
                if course_scheduled_in_day:
                    break

        if int(course.min_days) > spread and not course_in_existing_day:
            cost -= penalty_instance.get_min_wdays_penalty()

        return cost

    def calculate_room_stability_cost(schedule, instance_data, day, period, c, room):

        penalty_instance = penalty(configs.cbctt_type)
        scheduled_rooms = []
        cost = 0
        for d in range(instance_data.days):
            for p in range(instance_data.periods_per_day):
                for r in range(instance_data.rooms_count):
                    if schedule[d][p][r] == c and not r in scheduled_rooms:
                        scheduled_rooms.append(r)
                        break

        available_room = False
        # if we want to calculate the cost for a certain room
        if room is not None and room in scheduled_rooms:
            available_room = True
        # if we want to calculate the cost comparing all rooms
        else:
            for r in range(instance_data.rooms_count):
                if r in scheduled_rooms and schedule[day][period][r] == '':
                    available_room = True
                    break

        if not available_room:
            cost += penalty_instance.get_room_stability_penalty()

        return cost

    def calculate_room_capacity_cost(schedule, instance_data, unscheduled_lectures, day, period, course, type):

        penalty_instance = penalty(configs.cbctt_type)
        cost = 0
        # if 2stage best heuristic applies
        if type == 1:
            min_difference = 99999
            for r in range(instance_data.rooms_count):
                if schedule[day][period][r] is not '':
                    continue
                else:
                    size = int(instance_data.rooms[r].size)
                    if int(course.students) > size and int(course.students) - size < min_difference:
                        min_difference = int(course.students) - size

            if min_difference < 99999:
                cost += min_difference * penalty_instance.get_room_capacity_penalty()
        # if 2stage mean heuristic applies
        else:
            rooms_capacity = 0
            period_rooms_capacity = 0
            period_students = 0
            for d in range(instance_data.days):
                for p in range(instance_data.periods_per_day):
                    for r in range(instance_data.rooms_count):
                        if schedule[d][p][r] is '':
                            rooms_capacity += int(instance_data.rooms[r].size)
                            if d == day and p == period:
                                period_rooms_capacity += int(instance_data.rooms[r].size)
                        else:
                            if d == day and p == period:
                                l = next((i for i in instance_data.courses if i.id == schedule[d][p][r]), None)
                                period_students += int(l.students)

            lectures_capacity = 0
            for l in unscheduled_lectures:
                uc = next((i for i in instance_data.courses if i.id == l), None)
                lectures_capacity += int(uc.students)

            # an extra of 40% more than average of capacity "utilization";
            # if more students are assigned, there will be penalty
            eta_param = 1.3;

            # allowed percentage of covered capacity (without being penalized)
            cap_utilization = float(lectures_capacity) / rooms_capacity * eta_param

            capacity_limit = cap_utilization * period_rooms_capacity

            cost += max(float(0), min(period_students + int(course.students) - capacity_limit,
                                      float(course.students)) * penalty_instance.get_room_capacity_penalty())

        return cost

    def saturation_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        # The Saturation Degree rule arranges courses in ascending order
        # with respect to their number of available periods for scheduling
        # print('saturation degree')
        c_periods_count = {}
        for c in unscheduled_courses:
            course = next(
                (i for i in instance_data.courses if i.id == c), None)
            c_available_periods = repair_operators.check_periods_available(schedule, instance_data, course, period_lecture_assignments)
            c_periods_count[c] = len(c_available_periods)

        c_sorted = {k: v for k, v in sorted(c_periods_count.items(), key = lambda item:item[1])}
        # print(c_sorted)
        return list(c_sorted.keys())

    def largest_degree_order(schedule, instance_data, unscheduled_courses):
        # The Largest Degree rule prioritizes courses with the largest number of conflicts with other courses
        print('largest degree')
        c_conflicts_count = {}
        for c in unscheduled_courses:
            c_conflicts = repair_operators.check_periods_conflicts(schedule, instance_data, c)
            c_conflicts_count[c] = len(c_conflicts)

        c_sorted = {k: v for k, v in sorted(c_conflicts_count.items(), key = lambda item:item[1], reverse=True)}
        print(c_sorted)
        list(c_sorted.keys())

    def random_order(schedule, instance_data, unscheduled_courses):
        # The Random rule orders courses randomly
        print('random')
        shuffle(unscheduled_courses)
        unscheduled_courses


    ###################### End of Repair operators #############################################
