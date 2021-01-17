import random
import copy
from _alns_helpers import alns_helpers
from Experiments.statistics import statistics
from Models.period_course import period_course
from Models.period_conflict_courses import period_conflict_courses

class two_stage_repair_operator:

    ###################### Repair operators #############################################

    def two_stage_repair_operator(schedule, instance_data, unscheduled_lectures, lecture_period_heuristic, lecture_room_heuristic, priority_rule_operator):
        print("2-stage Repair Operator")
        statistics.two_stage_count += 1

        Uc = []

        period_lecture_assignments, Uc = two_stage_repair_operator.assign_lecture_to_period(schedule, unscheduled_lectures, instance_data, lecture_period_heuristic, priority_rule_operator)

        schedule = two_stage_repair_operator.assign_lecture_to_room(schedule, unscheduled_lectures, instance_data, period_lecture_assignments, lecture_room_heuristic)

        return schedule, Uc

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
        # we need to have unchanged list of courses that were unscheduled initially,
        # as we will need to update the actual list throughout the process, we are creating a copy of it to use where needed
        unscheduled_lectures_copy = copy.deepcopy(unscheduled_lectures)
        unscheduled_courses_copy = copy.deepcopy(unscheduled_courses)

        # compute potential insertion positions (periods) for each course to be scheduled
        Pc = alns_helpers.available_periods_per_courses(schedule, instance_data, unscheduled_courses_copy, period_lecture_assignments)

        # initialize list of periods from which course c can remove lectures R c = P c
        Rc = copy.deepcopy(Pc)

        while unscheduled_courses is not None and len(unscheduled_courses) > 0:

            removed_lectures = []
            # find first course to assign based on chosen priority rule
            course_to_assign = sorted_courses[0]
            print("Course to assign: ", course_to_assign)

            Rc1 = Rc[course_to_assign]
            print("Removable lectures: ", Rc1)
            # how many lectures should we assign per each course
            unscheduled_counter = unscheduled_lectures.count(course_to_assign)

            while unscheduled_counter > 0:
                Pc1 = copy.deepcopy(Pc[course_to_assign])
                print("Available Periods: ", Pc1)

                if Pc1 is not None and len(Pc1) > 0:
                    # evaluate all periods of Pc; return best;
                    best_position_index = \
                        two_stage_repair_operator.evaluate_insertion_positions(schedule, instance_data, unscheduled_lectures_copy, period_lecture_assignments, course_to_assign, Pc1, lecture_period_heuristic)

                    P_best = Pc1[best_position_index]
                    print("Best Period: ", P_best)

                    # insert the lecture to the best position in the schedule
                    pc = period_course(P_best[0], P_best[1], course_to_assign)
                    period_lecture_assignments.append(pc)

                    if P_best in Rc1:
                        Rc1.pop(Rc1.index(P_best))
                    Pc = alns_helpers.available_periods_per_courses(schedule, instance_data, unscheduled_courses_copy, period_lecture_assignments)

                elif Rc1 is not None and len(Rc1) > 0:
                    print("Backtracking")
                    print("Removable lectures: ", Rc1)
                    statistics.backtrack_count += 1

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

                        period_assigned_courses = [i.course for i in period_lecture_assignments if i.day == position[0] and i.period == position[1]]

                        for assigned_course in period_assigned_courses:
                            conflicted = False
                            # first check if we have curriculum related conflict
                            for q in instance_data.courses_curricula[course_to_assign]:
                                if q in instance_data.courses_curricula[assigned_course]:
                                    conflicted = True
                                    break
                            # check for teacher assignment conflict only if we didn't get any conflict in the curriculum check
                            # otherwise we already know that the course is confliced so no need to check for other conflicts
                            if not conflicted:
                                if instance_data.courses_teachers[assigned_course] == instance_data.courses_teachers[course_to_assign]:
                                    conflicted = True

                            if conflicted:
                                conflict_courses.append(assigned_course)
                                if len(Pc[assigned_course]) == 0:
                                    # conflict_courses_wcfa - indicates removable lectures (lectures that classify as removable from current course),
                                    # but don't have other conflicting free alternative positions if they get removed from this one.
                                    conflict_courses_wcfa.append(assigned_course)

                        if len(conflict_courses) > 0:
                            obj = period_conflict_courses(position[0], position[1], conflict_courses, conflict_courses_wcfa)
                            periods_conflict_courses.append(obj)

                    if len(periods_conflict_courses) > 0:

                        # the first criterion for the insertion period selection is preferring the period with the smallest
                        # number of lectures to remove that do not have any alternative conflict-free insertion positions left
                        # the reason behind this is that removing these lectures will lead to large disruptions
                        # ties are broken by choosing the period with the smallest number of lectures that have to be removed in total
                        # hence the list is sorted first by removable_lectures_wcfa_count, then by removable_lectures_count
                        periods_conflict_courses.sort(key=lambda x: (x.conflict_courses_wcfa_count, x.conflict_courses_count))
                        selected_for_removal = periods_conflict_courses[0]
                        P_best = [selected_for_removal.day, selected_for_removal.period]

                        # remove conflicting lectures
                        for conflict_course in selected_for_removal.conflict_courses:
                            pc = period_course(P_best[0], P_best[1], conflict_course)
                            period_lecture_assignments = list(filter(lambda a: a != pc, period_lecture_assignments))

                            unscheduled_lectures.append(conflict_course)

                    else:
                        # if we get a tie, that means none of the courses assigned to the periods during repair operation is a conflicting one
                        # but still the perios is unavailable means that the unavailability if coming from number of already assigned lectures
                        # is equal to the number of rooms hence there's no empty room in the periods that qualify as eligable to remove lectures from
                        # in this case of a tie we will choose the period with smallest number of conflicts and remove all lectured assigned during repair operation to it
                        # we will treat these lectures as "conflict courses" although technically they are not conflicting with the course we want to assign
                        best_position_index = \
                        two_stage_repair_operator.evaluate_insertion_positions(schedule, instance_data, unscheduled_lectures_copy, period_lecture_assignments, course_to_assign, Rc1, lecture_period_heuristic)
                        P_best = Rc1[best_position_index]

                        conflict_courses = [i for i in period_lecture_assignments if i.day == P_best[0] and i.period == P_best[1]]

                        for conflict_course in conflict_courses:
                            period_lecture_assignments = list(filter(lambda a: a != conflict_course, period_lecture_assignments))

                            unscheduled_lectures.append(conflict_course.course)

                    # add the new period-course assignment to the list that contains all assignments during repairing operator
                    pc = period_course(P_best[0], P_best[1], course_to_assign)
                    period_lecture_assignments.append(pc)
                    print("Best Period: ", [P_best[0], P_best[1]])

                    if P_best in Rc1:
                        Rc1.pop(Rc1.index(P_best))
                    Pc = alns_helpers.available_periods_per_courses(schedule, instance_data, unscheduled_courses_copy, period_lecture_assignments)

                else:
                    print("Lecture left unscheduled.")
                    Uc.append(course_to_assign)

                unscheduled_counter = unscheduled_counter - 1

            unscheduled_lectures = list(filter(lambda a: a != course_to_assign, unscheduled_lectures))
            unscheduled_courses = list(dict.fromkeys(unscheduled_lectures))

            # sort unscheduled courses according to chosen priority rule
            sorted_courses = priority_rule_operator(schedule, instance_data, unscheduled_courses, period_lecture_assignments)

        return period_lecture_assignments, Uc

    def assign_lecture_to_room(schedule, unscheduled_lectures, instance_data, period_lecture_assignments, lecture_room_heuristic):
        # select periods only from periods_lectures list and remove duplicates
        periods = set(map(tuple, [[x.day, x.period] for x in period_lecture_assignments]))
        # shuffle the periods list so we take the random approach in placing the lectures in rooms
        random.shuffle(list(periods))

        for p in periods:
            day = p[0]
            period = p[1]
            available_rooms = []
            for r in range(instance_data.rooms_count):
                if schedule[day][period][r] == -1:
                    available_rooms.append(r)

            courses_to_schedule = [x.course for x in period_lecture_assignments if x.day == day and x.period == period]

            # type 1: greatest heuristic
            # sort courses in ascending order by number of students
            if lecture_room_heuristic == "greatest":
                print("Greatest Heuristic")
                courses_to_schedule.sort(key=lambda x : instance_data.courses_students[x], reverse=True)
            # type 2: match heuristic
            # sort courses randomly
            elif lecture_room_heuristic == "match" or lecture_room_heuristic is None:
                print("Match Heuristic")
                random.shuffle(courses_to_schedule)

            for c in courses_to_schedule:
                min_cost = 999999
                selected_room = None
                for r in available_rooms:
                    cost = alns_helpers.calculate_room_stability_cost(schedule, instance_data, day, period, c, r)
                    room = instance_data.rooms[r]
                    if instance_data.courses_students[c] > int(room.size):
                        cost += instance_data.courses_students[c] - int(room.size)
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
                        min_cost = cost

                print('Selected Room {} for Lecture {}'.format(selected_room, c))
                if selected_room is not None:
                    schedule[day][period][selected_room] = c
                    available_rooms.pop(available_rooms.index(selected_room))

        return schedule

    def evaluate_insertion_positions(schedule, instance_data, unscheduled_lectures, period_lecture_assignments, course, available_periods, lecture_period_heuristic):

        course_period_cost = {}

        index = 0
        for p in available_periods:
            cost = 0
            day = p[0]
            period = p[1]

            ####### check compactness #######

            cost += alns_helpers.calculate_compactness_cost(schedule, instance_data, period_lecture_assignments, day, period, course)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check spread in days #######

            cost += alns_helpers.calculate_spread_days_cost(schedule, instance_data, period_lecture_assignments, day, course)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check room stability #######

            cost += alns_helpers.calculate_room_stability_cost(schedule, instance_data, day, period, course, None)

            ####### ####### ####### ####### ####### ####### ####### #######

            ####### check room capacity #######

            cost += alns_helpers.calculate_room_capacity_cost(schedule, instance_data, unscheduled_lectures, period_lecture_assignments, day, period, course, lecture_period_heuristic)

            ####### ####### ####### ####### ####### ####### ####### #######

            print("Total Cost for day {}, period {}, course {}: {}".format(day, period, course, cost))

            course_period_cost[index] = cost
            index += 1

        # sort in ascending order periods based on cost evaluated by 4 previous step
        # and return the first period as the best period to insert the course
        course_period_cost = {k: v for k, v in sorted(course_period_cost.items(), key=lambda item: item[1])}
        selected_position = 0
        selected_value = list(course_period_cost.values())[selected_position]
        count_same_with_selected = sum(value == selected_value for value in course_period_cost.values())
        if count_same_with_selected > 1:
            selected_position = random.randrange(count_same_with_selected)
        return list(course_period_cost.keys())[selected_position]

    ###################### End of Repair operators #############################################
