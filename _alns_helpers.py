from Experiments.configs import configs
from Models.penalty import penalty

class alns_helpers:

    def check_periods_available(schedule, instance_data, course, period_lecture_assignments):

        available_periods = []

        for d in range(instance_data.days):
            for p in range(instance_data.periods_per_day):
                is_available = alns_helpers.is_period_available(schedule, instance_data, course,
                                                                    period_lecture_assignments, d, p)
                if is_available:
                    available_periods.append([d, p])

        return available_periods

    def check_course_conflicts(schedule, instance_data, course):

        course_conflicts_count = 0

        for iteration_course in range(instance_data.courses_count):
            conflicted = False
            if iteration_course != course:

                if instance_data.courses_teachers[iteration_course] == instance_data.courses_teachers[course]:
                    conflicted = True

                # if courses have conflicting curricula
                if not set(instance_data.courses_curricula[iteration_course]).isdisjoint(
                        instance_data.courses_curricula[course]) and not conflicted:
                    conflicted = True

                if conflicted:
                    course_conflicts_count += instance_data.courses_lectures[iteration_course]

        return course_conflicts_count

    def is_period_available(schedule, instance_data, course, period_lecture_assignments, d, p):

        assigned_lectures_to_period = [x.course for x in period_lecture_assignments if x.day == d and x.period == p]

        if [d, p] in instance_data.courses_periods_constraints[course]:
            return False

        # even if checking the feasibility in the fixed schedule regarding scheduling students of same curriculum at the same time
        # we need to check also against lectures that are assigned to this period in previous steps
        # during repair operators
        for assigned_course in assigned_lectures_to_period:
            if instance_data.courses_teachers[assigned_course] == instance_data.courses_teachers[course]:
                return False

            if not set(instance_data.courses_curricula[assigned_course]).isdisjoint(
                    instance_data.courses_curricula[course]):
                return False

        # check against fixed schedule
        rooms_available = 0
        for r in range(instance_data.rooms_count):
            assigned_course = schedule[d][p][r]
            if assigned_course == -1:
                rooms_available += 1
            else:
                if instance_data.courses_teachers[assigned_course] == instance_data.courses_teachers[course]:
                    return False

                if not set(instance_data.courses_curricula[assigned_course]).isdisjoint(
                        instance_data.courses_curricula[course]):
                    return False

        # if there are rooms available from the fixed schedule, check how many lectures are assigned to this period in previous stages
        # so we make sure we don't assign more lectures than rooms in any period
        if (rooms_available - len(assigned_lectures_to_period)) > 0:
            return True
        else:
            return False

    def available_periods_per_courses(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        Pc = {}

        for c in unscheduled_courses:
            available_periods = alns_helpers.check_periods_available(schedule, instance_data, c, period_lecture_assignments)
            Pc[c] = available_periods

        return Pc

    def calculate_compactness_cost(schedule, instance_data, period_lecture_assignments, day, period, c):

        penalty_instance = penalty(configs.cbctt_type)
        cost = 0
        # if there is no adjacent slot that has scheduled any course from the same curriculum
        # means that if we place the lecture in the current slot it will be isolated
        # and hence it will increase the cost of curriculum compactness
        #
        # if there is a course from same curriculum in the neighbor period (adjacent slot)
        # means that if we place this current lecture at this slot,
        # and if the course from same curricula in the adjacent slot was isolated before,
        # will no longer be so, and we will reduce the cost of curriculum compactness
        # line below checks if same curriculum course in the adjacent period is isolated or not
        is_lecture_isolated = alns_helpers.is_lecture_isolated(schedule, instance_data, period_lecture_assignments, c, day, period)
        if is_lecture_isolated:
            cost += penalty_instance.get_isolated_lectures_penalty()
        else:
            if period == 0:
                is_neighbor_isolated = alns_helpers.is_lecture_isolated(schedule, instance_data, period_lecture_assignments, c, day, period + 1)
                if is_neighbor_isolated:
                    cost -= penalty_instance.get_isolated_lectures_penalty()

            elif period == instance_data.periods_per_day - 1:
                is_neighbor_isolated = alns_helpers.is_lecture_isolated(schedule, instance_data, period_lecture_assignments, c, day, period - 1)
                if is_neighbor_isolated:
                    cost -= penalty_instance.get_isolated_lectures_penalty()

            else:
                if alns_helpers.has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, period - 1):
                    is_left_neighbor_isolated = alns_helpers.is_lecture_isolated(schedule, instance_data, period_lecture_assignments, c, day, period - 1)
                    if is_left_neighbor_isolated:
                        cost -= penalty_instance.get_isolated_lectures_penalty()

                if alns_helpers.has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, period + 1):
                    is_right_neighbor_isolated = alns_helpers.is_lecture_isolated(schedule, instance_data, period_lecture_assignments, c, day, period + 1)
                    if is_right_neighbor_isolated:
                        cost -= penalty_instance.get_isolated_lectures_penalty()

        print("Compactness Cost for day {}, period {}, course{}".format(day, period, c))
        return cost

    def is_lecture_isolated(schedule, instance_data, period_lecture_assignments, c, day, period):

        if period == 0:
            has_curriculum_neighbor = alns_helpers.has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, period + 1)
            return not has_curriculum_neighbor

        elif period == instance_data.periods_per_day - 1:
            has_curriculum_neighbor = alns_helpers.has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, period - 1)
            return not has_curriculum_neighbor

        else:
            has_left_curriculum_neighbor = alns_helpers.has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, period - 1)
            has_right_curriculum_neighbor = alns_helpers.has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, period + 1)
            return not (has_left_curriculum_neighbor or has_right_curriculum_neighbor)

    def has_curriculum_neighbor(schedule, instance_data, period_lecture_assignments, c, day, neighbor_period):

        period_assigned_neighbor_courses = [x.course for x in period_lecture_assignments if
                                       x.day == day and x.period == neighbor_period]

        has_neighbor = False
        # let us check first if any course belonging to the same curricula as current course
        # is assigned to the neighbor period (adjacent slot)
        for neighbor_course in period_assigned_neighbor_courses:
            if neighbor_course == c:
                has_neighbor = True
                break

            if not set(instance_data.courses_curricula[neighbor_course]).isdisjoint(
                    instance_data.courses_curricula[c]):
                has_neighbor = True
                break

        # if no courses from same curricula found in adjacent slot
        # from those assigned to that slot during period-lecture assignment stage
        # then let's check if any course from the fixed schedule belongs to same curricula
        if not has_neighbor:
            for r in range(instance_data.rooms_count):
                neighbor_course = schedule[day][neighbor_period][r]
                if neighbor_course != -1:
                    if neighbor_course == c:
                        has_neighbor = True
                        break
                    if not set(instance_data.courses_curricula[neighbor_course]).isdisjoint(
                            instance_data.courses_curricula[c]):
                        has_neighbor = True
                        break

        return has_neighbor

    def course_exists_in_day(schedule, instance_data, period_lecture_assignments, day, course):

        period_assigned_courses = [x.course for x in period_lecture_assignments if
                                   x.day == day]

        # check if any lecture of this course is already assigned to this day
        # so we count it in the spread days cost
        if course in period_assigned_courses:
            return True

        # if no lecture of the course is scheduled to this day during the period-lecture assignment stage
        # we check if any lecture of the course is scheduled in this day in the fixed schedule
        for p in range(instance_data.periods_per_day):
            for r in range(instance_data.rooms_count):
                if schedule[day][p][r] == course:
                    return True

        return False

    def calculate_spread_days_cost(schedule, instance_data, period_lecture_assignments, day, course):

        penalty_instance = penalty(configs.cbctt_type)
        spread = 0
        cost = 0

        course_exists_in_day = alns_helpers.course_exists_in_day(schedule, instance_data, period_lecture_assignments, day, course)

        if not course_exists_in_day:
            # Whenever the required spread over days of the course is not reached and
            # no other lecture of the same course has been scheduled on the considered day,
            # the respective penalty is subtracted, since the solution will be improved.

            for d in range(instance_data.days):
                if d != day:

                    course_scheduled_in_day = alns_helpers.course_exists_in_day(schedule, instance_data,
                                                                             period_lecture_assignments, day, course)

                    if course_scheduled_in_day:
                        spread += 1

            if instance_data.courses_wdays[course] > spread:
                cost -= penalty_instance.get_min_wdays_penalty()

        print("Minimum Spread Days Cost for day {}, course {}: {}".format(day, course , cost))
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
                    if schedule[d][p][r] == c and r not in scheduled_rooms:
                        scheduled_rooms.append(r)
                        break

        available_room = False
        # if we want to calculate the cost for a certain room
        if room is not None and room in scheduled_rooms:
            available_room = True
        else:
            # if we want to calculate the cost comparing all rooms
            for r in range(instance_data.rooms_count):
                if r in scheduled_rooms and schedule[day][period][r] == -1:
                    available_room = True
                    break

        if not available_room:
            cost += penalty_instance.get_room_stability_penalty()

        print("Room Stability Cost for day {}, period {}, course {}: {}".format(day, period, c, cost))
        return cost

    def calculate_room_capacity_cost(schedule, instance_data, unscheduled_lectures, period_lecture_assignments, day, period, course, lecture_period_heuristic):

        penalty_instance = penalty(configs.cbctt_type)
        cost = 0

        # if 2stage "best" heuristic applies
        # the capacity penalty is roughly estimated by assuming that
        # if the lecture has the xth most students of all courses that are assigned to the period in the part of the schedule that is under construction,
        # it will get the xth largest available room in the second stage.
        # The capacity penalty then corresponds to the excess number of students.

        if lecture_period_heuristic == "best":
            print("2-stage Best Heuristic")

            courses_to_schedule = [x.course for x in period_lecture_assignments if x.day == day and x.period == period]
            courses_to_schedule.append(course)
            courses_to_schedule.sort(key=lambda x: instance_data.courses_students[x], reverse=True)

            available_rooms = []
            for r in range(instance_data.rooms_count):
                if schedule[day][period][r] == -1:
                    available_rooms.append(instance_data.rooms[r])

            available_rooms.sort(key=lambda x: int(x.size), reverse=True)

            courses_to_schedule_length = len(courses_to_schedule)
            available_rooms_length = len(available_rooms)
            try:
                # in cases of backtracking when the period is not available due to the fact that there are no more available rooms
                # we will be evaluating which period results in more conflicts so we decide from which to remove courses
                # namely, when we come at this step we will already be having more courses we want to assign to the period
                # because we havent decided yet from which to remove, and if we want to evaluate this we suppose that we will remove courses
                # from this period, and we calculate the cost only by the difference of the course we want to schedule and the available rooms
                if (courses_to_schedule_length > available_rooms_length):
                   cost += max(0, (instance_data.courses_students[course] - int(available_rooms[0].size)))
                else:
                    for i in range(courses_to_schedule_length):
                        cost += max(0, (instance_data.courses_students[courses_to_schedule[i]] - int(available_rooms[i].size)))
            except:
                print("Calculate room capacity failed...")

            cost = cost * penalty_instance.get_room_capacity_penalty()

        # if 2stage "mean" heuristic applies
        # A reference utilization of the room capacities u is computed by dividing the sum of the number of students
        # of all lectures that have to be scheduled Σl by the sum of the capacities of all available rooms
        # Σr, i.e., u = Σl / Σr . Then a capacity limit is computed for each period individually as η · u ·Σp,
        # where Σp denotes the sum of the capacities of the available rooms in period p and η denotes
        # a parameter that controls the penalty-free number of students. The capacity penalty added to
        # the insertion cost corresponds to the number of students of the assigned lectures exceeding
        # the capacity limit of the considered period.
        elif lecture_period_heuristic == "mean":
            print("2-stage Mean Heuristic")

            available_capacity = 0
            required_capacity = 0
            period_available_capacity = 0
            period_required_capacity = 0

            for l in unscheduled_lectures:
                required_capacity += instance_data.courses_students[l]

            for d in range(instance_data.days):
                for p in range(instance_data.periods_per_day):
                    for r in range(instance_data.rooms_count):
                        if schedule[d][p][r] == -1:
                            available_capacity += int(instance_data.rooms[r].size)
                            if d == day and p == period:
                                period_available_capacity += int(instance_data.rooms[r].size)
                        else:
                            if d == day and p == period:
                                period_required_capacity += instance_data.courses_students[schedule[d][p][r]]

            # an extra of 40% more than average of capacity "utilization";
            # if more students are assigned, there will be penalty
            eta_param = 1.3;

            # allowed percentage of covered capacity (without being penalized)
            cap_utilization = float(required_capacity) / available_capacity

            capacity_limit = cap_utilization * eta_param * period_available_capacity

            cost += max(float(0), min(period_required_capacity + instance_data.courses_students[course] - capacity_limit,
                                      float(instance_data.courses_students[course])) * penalty_instance.get_room_capacity_penalty())

        print("Room Capacity Cost for day {}, period {}, course {}: {}".format(day, period, course, cost))
        return cost

    ###################### End of Repair operators #############################################
