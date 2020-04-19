import random
from random import randint, shuffle
import math
import os
import uuid
from itertools import groupby
import collections
from collections import OrderedDict
from configs import configs
from parameters import parameters
from objective_function import objective_function
from Entities.penalty import penalty
from Entities.period_course import period_course
from Entities.period_conflict_courses import period_conflict_courses

class repair_operators:

    ###################### Repair operators #############################################

    def two_stage_repair_operator(schedule, instance_data, unscheduled_lectures, lecture_period_heuristic, lecture_room_heuristic, priority_rule_operator):
        period_lecture_assignments = repair_operators.assign_lecture_to_period(schedule, unscheduled_lectures, instance_data, lecture_period_heuristic, priority_rule_operator)
        schedule = repair_operators.assign_lecture_to_room(schedule, unscheduled_lectures, instance_data, period_lecture_assignments, lecture_room_heuristic)
        print('FINAL SCHEDULE: ', schedule)
        return schedule

    def check_periods_available(schedule, instance_data, course, period_lecture_assignments, forbidden_period):
        # print('check period is available')
        available_periods = []

        for d in range(instance_data.days):
            for p in range(instance_data.periods_per_day):
                if forbidden_period is not None and forbidden_period[0] == d and forbidden_period[p] == p:
                    continue
                else:
                    is_available = repair_operators.is_period_available(schedule, instance_data, course,
                                                                        period_lecture_assignments, d, p)
                    if is_available:
                        available_periods.append([d, p])

        return available_periods

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
                                course_conflicts[scheduled_course.id] = [d, p]

                        if scheduled_course.teacher_id == current_course.teacher_id:
                            course_conflicts[scheduled_course.id] = [d, p]

        return course_conflicts

    def is_period_available(schedule, instance_data, course, period_lecture_assignments, d, p):

        course_curricula = [i for i in instance_data.curricula if course.id in i.courses]

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
        # we need to check also against lectures that are assigned to this period in previous steps
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
        else:
            return False

    def assign_lecture_to_period(schedule, unscheduled_lectures, instance_data, lecture_period_heuristic, priority_rule_operator):

        # vector of lectures that we fail to insert during the process
        Uc = []
        # remove duplicates so we can retrieve unique courses from the lectures list
        unscheduled_courses = list(dict.fromkeys(unscheduled_lectures))
        # List of period-course assignments
        period_lecture_assignments = []
        # sort unscheduled courses according to chosen priority rule
        sorted_courses = priority_rule_operator(schedule, instance_data, unscheduled_courses, period_lecture_assignments)
        # keep track of removed courses so we avoid cycles (this is needed during backtracking process, if applicable)
        forbidden_lectures = {}

        # compute potential insertion positions (periods) for each course to be scheduled
        Pc = available_periods_per_courses(schedule, instance_data, period_lecture_assignments)

        # initialize list of periods from which course c can
        # remove lectures R c = P c
        Rc = Pc.copy()

        while unscheduled_courses is not None and len(unscheduled_courses) > 0:

            removed_lectures = []
            # find first course to assign based on chosen priority rule
            course_to_assign = sorted_courses[0]

            course = next(
                (i for i in instance_data.courses if i.id == course_to_assign), None)

            Pc1 = Pc[course_to_assign]
            Rc1 = Rc[course_to_assign]
            # how many lectures should we assign per each course
            unscheduled_counter = unscheduled_lectures.count(course_to_assign)

            while unscheduled_counter > 0:
                if Pc1 is not None and len(Pc1) > 0:
                    # evaluate all periods of Pc; return best;
                    best_position_index = \
                        repair_operators.evaluate_insertion_positions(schedule, instance_data, unscheduled_lectures, unscheduled_courses, course, Pc1, lecture_period_heuristic)

                    P_best = Pc1[best_position_index]

                    # insert the lecture to the best position in the schedule
                    pc = period_course(P_best[0], P_best[1], course_to_assign)
                    period_lecture_assignments.append(pc)

                    Rc1.pop(Rc1.index(P_best))
                    Pc = available_periods_per_courses(schedule, instance_data, period_lecture_assignments)

                elif Rc1 is not None and len(Rc1) > 0:

                    course_curricula = [i for i in instance_data.curricula if course.id in i.courses]

                    # if we are not able to assign course to any period, we apply Backtracking
                    # Backtracking will consider to remove only the lectures that are assigned during the repairing phase

                    periods_conflict_courses = []
                    # evaluate all periods of Rc; return best;
                    for position in Rc1:

                        # evaluate position by checking if lectures assigned to that position are conflicting the current course
                        # check conflicts for curriculum and teacher
                        # find conflicting courses for best position
                        conflict_courses = []
                        conflict_courses_wcfa = []

                        # evaluate position by checking if lectures assigned to that position are conflicting the current course
                        # check conflicts for curriculum and teacher
                        for r in range(instance_data.rooms_count):
                            conflicted = False
                            assigned_course = schedule[position[0]][position[1]][r]
                            if assigned_course != '':
                                for q in course_curricula:
                                    if assigned_course in q.courses:
                                        conflicted = True
                                        break
                                assigned_course_details = next((i for i in instance_data.courses if i.id == assigned_course), None)
                                if assigned_course_details.teacher_id == course.teacher_id:
                                    conflicted = True

                                # if the lecture is not part of fixed schedule then we add it to an array which use for comparison purposes in later stage
                                if conflicted:
                                    conflict_courses.append(assigned_course)
                                    if len(Pc[assigned_course]) == 0:
                                        # conflict_courses_wcfa - indicates removable lectures (lectures that classify as removable from current course),
                                        # but don't have other conflicting free alternative positions if they get removed from this one.
                                        conflict_courses_wcfa.append(assigned_course)

                        if len(conflict_courses) > 0:
                            obj = period_conflict_courses(position[0], position[1], conflict_courses, conflict_courses_wcfa)
                            periods_conflict_courses.append(obj)

                    # the first criterion for the insertion period selection is preferring the period with the smallest
                    # number of lectures to remove that do not have any alternative conflict-free insertion positions left
                    # the reason behind this is that removing these lectures will lead to large disruptions
                    # ties are broken by choosing the period with the smallest number of lectures that have to be removed in total
                    # hence the list is sorted first by removable_lectures_wcfa_count, then by removable_lectures_count
                    periods_conflict_courses.sort(key=lambda x: (x.conflict_courses_wcfa_count, x.conflict_courses_count))
                    P_best = periods_conflict_courses[0]

                    # add the new period-course assignment to the list that contains all assignments during repairing operator
                    pc = period_course(P_best.day, P_best.period, course_to_assign)
                    period_lecture_assignments.append(pc)

                    # remove conflicting lectures
                    for conflict_course in P_best.conflict_courses:
                        pcc = period_course(P_best.day, P_best.period, conflict_course)
                        period_lecture_assignments = list(filter(lambda a: a != pcc, period_lecture_assignments))
                        unscheduled_lectures.append(conflict_course)

                    Rc.pop(Rc.index(P_best))
                    Pc = repair_operators.check_periods_available(schedule, instance_data, course, period_lecture_assignments, None)

                else:
                    Uc.append(course_to_assign)

                unscheduled_counter = unscheduled_counter - 1

            unscheduled_lectures = list(filter(lambda a: a != course_to_assign, unscheduled_lectures))
            unscheduled_courses = list(dict.fromkeys(unscheduled_lectures))

            # sort unscheduled courses according to chosen priority rule
            sorted_courses = priority_rule_operator(schedule, instance_data, unscheduled_courses, period_lecture_assignments)

        print('unscheduled lectures: ', unscheduled_lectures)
        return period_lecture_assignments

    def available_periods_per_courses(schedule, instance_data, period_lecture_assignments):
        Pc = {}

        for c in unscheduled_courses:
            course = next(
                (i for i in instance_data.courses if i.id == c), None)
            available_periods = repair_operators.check_periods_available(schedule, instance_data, course, period_lecture_assignments, None)
            Pc[uc] = available_periods

        return Pc

    def assign_lecture_to_room(schedule, unscheduled_lectures, instance_data, period_lecture_assignments, lecture_room_heuristic):

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
            if lecture_room_heuristic == "greatest":
                courses_to_schedule.sort(key=lambda x : int(x.students),reverse=True)
            # type 2: match heuristic
            # sort courses randomly
            elif lecture_room_heuristic == "match" or lecture_room_heuristic is None:
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
                    if lecture_room_heuristic == "greatest" and cost == min_cost and int(room.size) > int(instance_data.rooms[selected_room].size):
                            selected_room = r
                    # ties are broken by preferring the room with smallest capacity
                    # the reason is that since lectures are schedules in a random order,
                    # there might be lectures that are processed later and require large rooms
                    elif lecture_room_heuristic == "match" and cost == min_cost and int(room.size) < int(instance_data.rooms[selected_room].size):
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

    def evaluate_insertion_positions(schedule, instance_data, unscheduled_lectures, unscheduled_courses, course, available_periods, lecture_period_heuristic):

        course_period_cost = {}

        index = 0
        for p in available_periods:
            cost = 0
            day = p[0]
            period = p[1]

            ####### check compactness #######

            cost += repair_operators.calculate_compactness_cost(schedule, instance_data, day, period, course.id)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check spread in days #######

            cost += repair_operators.calculate_spread_days_cost(schedule, instance_data, day, course)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check room stability #######

            cost += repair_operators.calculate_room_stability_cost(schedule, instance_data, day, period, course.id, None)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check room capacity #######

            cost += repair_operators.calculate_room_capacity_cost(schedule, instance_data, unscheduled_lectures, day, period, course, lecture_period_heuristic)

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
        # if there is no adjacent slot that has scheduled any course from the same curriculum
        # means that if we place the lecture in the current slot it will be isolated
        # and hence it will increase the cost of curriculim compactness
        #
        # if there is a course from same curriculum in the neighbor period (adjacent slot)
        # means that if we place this current lecture at this slot, and if the course from same curricula in the adjacent slot
        # was isolated before, will no longer be so, and we will reduce the cost of curriculum compactness
        # line below checks if same curriculum course in the adjacent period is isolated or not
        is_lecture_isolated = repair_operators.is_lecture_isolated(schedule, instance_data, c, day, period)
        if is_lecture_isolated:
            cost += penalty_instance.get_isolated_lectures_penalty()
        else:
            if period == 0:
                is_neighbor_isolated = repair_operators.is_lecture_isolated(schedule, instance_data, c, day, period + 1)
                if is_neighbor_isolated:
                    cost -= penalty_instance.get_isolated_lectures_penalty()

            elif period == instance_data.periods_per_day - 1:
                is_neighbor_isolated = repair_operators.is_lecture_isolated(schedule, instance_data, c, day, period - 1)
                if is_neighbor_isolated:
                    cost -= penalty_instance.get_isolated_lectures_penalty()

            else:
                is_left_neighbor_isolated = repair_operators.is_lecture_isolated(schedule, instance_data, c, day, period - 1)
                if is_left_neighbor_isolated:
                    cost -= penalty_instance.get_isolated_lectures_penalty()

                is_right_neighbor_isolated = repair_operators.is_lecture_isolated(schedule, instance_data, c, day, period + 1)
                if is_right_neighbor_isolated:
                    cost -= penalty_instance.get_isolated_lectures_penalty()

        return cost

    def is_lecture_isolated(schedule, instance_data, c, day, period):

        if period == 0:
            has_curriculum_neighbor = repair_operators.has_curriculum_neighbor(schedule, instance_data, c, day, period + 1)
            return not has_curriculum_neighbor

        elif period == instance_data.periods_per_day - 1:
            has_curriculum_neighbor = repair_operators.has_curriculum_neighbor(schedule, instance_data, c, day, period - 1)
            return not has_curriculum_neighbor

        else:
            has_left_curriculum_neighbor = repair_operators.has_curriculum_neighbor(schedule, instance_data, c, day, period - 1)
            has_right_curriculum_neighbor = repair_operators.has_curriculum_neighbor(schedule, instance_data, c, day, period + 1)
            return not (has_left_curriculum_neighbor or has_right_curriculum_neighbor)

    def has_curriculum_neighbor(schedule, instance_data, c, day, neighbor_period):

        course_curricula = [i for i in instance_data.curricula if c in i.courses]

        has_neighbor = False
        for r in range(instance_data.rooms_count):
            neighbor_course = schedule[day][neighbor_period][r]
            if neighbor_course != "":
                for q in course_curricula:
                    if neighbor_course in q.courses:
                        has_neighbor = True
                        break
                if has_neighbor:
                    break

        return has_neighbor

    def calculate_spread_days_cost(schedule, instance_data, day, course):

        penalty_instance = penalty(configs.cbctt_type)
        spread = 0
        cost = 0
        # Whenever the required spread over days of the course is not reached and
        # no other lecture of the same course has been scheduled on the considered day,
        # the respective penalty is subtracted, since the solution will be improved.
        course_exists_in_considered_day = False
        for d in range(instance_data.days):
            course_scheduled_in_day = False
            for p in range(instance_data.periods_per_day):
                for r in range(instance_data.rooms_count):
                    if schedule[d][p][r] == course.id:
                        course_scheduled_in_day = True
                        spread += 1
                        if d == day:
                            course_exists_in_considered_day = True
                        break
                if course_scheduled_in_day:
                    break

        if int(course.min_days) > spread and not course_exists_in_considered_day:
            cost -= penalty_instance.get_min_wdays_penalty()

        return cost

    def calculate_room_stability_cost(schedule, instance_data, day, period, c, room):

        penalty_instance = penalty(configs.cbctt_type)
        scheduled_rooms = []
        cost = 0
        # If some lectures of the course have already been scheduled and none of the
        # rooms where these lectures take place are available in the considered period,
        # the penalty for violating the room stability is added.
        for d in range(instance_data.days):
            for p in range(instance_data.periods_per_day):
                for r in range(instance_data.rooms_count):
                    if schedule[d][p][r] == c and not r in scheduled_rooms:
                        scheduled_rooms.append(r)
                        break

        available_room = False
        # if we want to calculate the cost for a certain room
        if room is not None:
            if room in scheduled_rooms:
                available_room = True
            else:
                available_room = False
        # if we want to calculate the cost comparing all rooms
        else:
            for r in range(instance_data.rooms_count):
                if r in scheduled_rooms and schedule[day][period][r] == '':
                    available_room = True
                    break

        if not available_room:
            cost += penalty_instance.get_room_stability_penalty()

        return cost

    def calculate_room_capacity_cost(schedule, instance_data, unscheduled_lectures, day, period, course, lecture_period_heuristic):

        penalty_instance = penalty(configs.cbctt_type)
        cost = 0

        # if 2stage "best" heuristic applies
        # the capacity penalty is roughly estimated by assuming that
        # if the lecture has the xth most students of all courses that are assigned to the period in the part of the schedule that is under construction,
        # it will get the xth largest available room in the second stage.
        # The capacity penalty then corresponds to the excess number of students.

        if lecture_period_heuristic == "best":
            min_difference = 99999
            for r in range(instance_data.rooms_count):
                if schedule[day][period][r] is not '':
                    continue
                else:
                    room_capacity = int(instance_data.rooms[r].size)
                    if int(course.students) > room_capacity and int(course.students) - room_capacity < min_difference:
                        min_difference = int(course.students) - room_capacity

            if min_difference < 99999:
                cost += min_difference * penalty_instance.get_room_capacity_penalty()

        # if 2stage "mean" heuristic applies
        # A reference utilization of the room capacities u is computed by dividing the sum of the number of students
        # of all lectures that have to be scheduled Σl by the sum of the capacities of all available rooms
        # Σr, i.e., u = Σl / Σr . Then a capacity limit is computed for each period individually as η · u ·Σp,
        # where Σp denotes the sum of the capacities of the available rooms in period p and η denotes
        # a parameter that controls the penalty-free number of students. The capacity penalty added to
        # the insertion cost corresponds to the number of students of the assigned lectures exceeding
        # the capacity limit of the considered period.
        elif lecture_period_heuristic == "mean":

            available_capacity = 0
            required_capacity = 0
            period_available_capacity = 0
            period_required_capacity = 0

            for l in unscheduled_lectures:
                lecture = next((i for i in instance_data.courses if i.id == l), None)
                required_capacity += int(lecture.students)

            for d in range(instance_data.days):
                for p in range(instance_data.periods_per_day):
                    for r in range(instance_data.rooms_count):
                        if schedule[d][p][r] is '':
                            available_capacity += int(instance_data.rooms[r].size)
                            if d == day and p == period:
                                period_available_capacity += int(instance_data.rooms[r].size)
                        else:
                            if d == day and p == period:
                                lecture = next((i for i in instance_data.courses if i.id == schedule[d][p][r]), None)
                                period_required_capacity += int(lecture.students)

            # an extra of 40% more than average of capacity "utilization";
            # if more students are assigned, there will be penalty
            eta_param = 1.3;

            # allowed percentage of covered capacity (without being penalized)
            cap_utilization = float(required_capacity) / available_capacity * eta_param

            capacity_limit = cap_utilization * period_available_capacity

            cost += max(float(0), min(period_required_capacity + int(course.students) - capacity_limit,
                                      float(course.students)) * penalty_instance.get_room_capacity_penalty())

        return cost

    ###################### End of Repair operators #############################################
