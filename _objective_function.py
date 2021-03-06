import xml_to_od
from Models.penalty import penalty
from Experiments.statistics import statistics


class objective_function:

    def __init__(self, type, instance_data):

        self.instance_data = instance_data
        self.type = type

        # Penalty scores
        self.penalties = penalty(type)

    # Objective function is sum of all penalties (which penalties is )
    def cost(self, current_solution):

        # initialize a dictionary that will help to keep track of courses penalties
        course_penalties = dict()
        for i in range(self.instance_data.courses_count):
            course_penalties[i] = 0

        # initialize a dictionary that will help to keep track of curricula penalties
        curriculum_penalties = dict()
        for curriculum in self.instance_data.curricula:
            curriculum_penalties[curriculum.id] = 0

        if self.type == 'UD4':

            room_capacity_penalty, course_penalties = self.room_capacity_penalties(current_solution, course_penalties)
            min_wdays_penalty, course_penalties = self.min_wdays_penalties(current_solution, course_penalties)
            windows_penalty, curriculum_penalties = self.windows_penalties(current_solution, curriculum_penalties)
            minmax_load_penalty = self.minmax_load_penalties(current_solution)
            double_lectures_penalty = self.double_lectures_penalties(current_solution)

            cost = room_capacity_penalty + min_wdays_penalty + windows_penalty + minmax_load_penalty + double_lectures_penalty

            return cost, course_penalties, curriculum_penalties

        elif self.type == 'UD2':
            room_capacity_penalty, course_penalties = self.room_capacity_penalties(current_solution, course_penalties)
            min_wdays_penalty, course_penalties = self.min_wdays_penalties(current_solution, course_penalties)
            isolated_lectures_penalty, curriculum_penalties = self.isolated_lectures_penalties(current_solution, curriculum_penalties)
            room_stability_penalty, course_penalties = self.room_stability_penalties(current_solution, course_penalties)

            cost = room_capacity_penalty + min_wdays_penalty + isolated_lectures_penalty + room_stability_penalty

            return cost, course_penalties, curriculum_penalties

    # For each lecture, the number of students that attend the course must be less
    # than or equal the number of seats of all the rooms that host its lectures.
    # Each student above the capacity counts as 1 point of penalty.
    def room_capacity_penalties(self, current_solution, course_penalties):

        penalty = 0

        for i in range(self.instance_data.days):
            for j in range(self.instance_data.periods_per_day):
                for k in range(self.instance_data.rooms_count):
                    if current_solution[i][j][k] != -1:
                        course_index = current_solution[i][j][k]
                        students = self.instance_data.courses_students[course_index]
                        room_size = int(self.instance_data.rooms[k].size)
                        if students - room_size > 0:
                            extra_students = students - room_size
                            penalty += extra_students
                            course_penalties[course_index] += extra_students

        return penalty, course_penalties

    # The lectures of each course must be spread into a given minimum number of days.
    # Each day below the minimum counts as 1 violation.
    def min_wdays_penalties(self, current_solution, course_penalties):

        penalty = 0

        for course in range(self.instance_data.courses_count):
            min_days = self.instance_data.courses_wdays[course]
            course_days = 0
            for i in range(self.instance_data.days):
                course_in_day = False
                for j in range(self.instance_data.periods_per_day):
                    for k in range(self.instance_data.rooms_count):
                        if course == current_solution[i][j][k]:
                            course_in_day = True
                            break
                    if course_in_day:
                        break
                if course_in_day:
                    course_days += 1

            if course_days < min_days:
                cost = (min_days - course_days) * self.penalties.P_DAYS
                penalty += cost
                course_penalties[course] += cost

        return penalty, course_penalties


    # Lectures belonging to a curriculum should not have time windows
    # (i.e., periods without teaching) between them. For a given curriculum we account for
    # a violation every time there is one windows between two lectures within the same day.
    # Each time window in a curriculum counts as many violation as its length (in periods).
    def windows_penalties(self, current_solution, curriculum_penalties):

        penalty = 0

        for curriculum in self.instance_data.curricula:
            for i in range(self.instance_data.days):
                check_for_windows = False
                curriculum_windows = 0
                for j in range(self.instance_data.periods_per_day):
                    if check_for_windows:
                        curriculum_windows += 1
                    for k in range(self.instance_data.rooms_count):
                        course = current_solution[i][j][k]
                        if course != -1:
                            if check_for_windows and curriculum in self.instance_data.courses_curricula[course]:
                                penalty += curriculum_windows - 1
                                curriculum_penalties[curriculum.id] += curriculum_windows - 1
                                curriculum_windows = 0
                                break
                            else:
                                check_for_windows = True
                                break

        return penalty, curriculum_penalties


    # For each curriculum the number of daily lectures should be within a given range.
    # Each lecture below the minimum or above the maximum counts as 1 violation.
    def minmax_load_penalties(self, current_solution):

        penalty = 0

        for curriculum in self.instance_data.curricula:
            for i in range(self.instance_data.days):
                daily_lectures = 0
                for j in range(self.instance_data.periods_per_day):
                    for k in range(self.instance_data.rooms_count):
                        if current_solution[i][j][k] != -1 and curriculum in self.instance_data.courses_curricula[current_solution[i][j][k]]:
                            daily_lectures += 1
                            break

                if daily_lectures > self.instance_data.daily_max_lectures:
                    penalty += daily_lectures - self.instance_data.daily_max_lectures
                elif daily_lectures < self.instance_data.daily_min_lectures:
                    penalty += self.instance_data.daily_min_lectures - daily_lectures

        return penalty


    # Some courses require that lectures in the same day are grouped together
    # (double lectures). For a course that requires grouped lectures, every time there is more than
    # one lecture in one day, a lecture non-grouped to another is not allowed. Two lectures are
    # grouped if they are adjacent and in the same room. Each non-grouped lecture counts as 1
    # violation.
    def double_lectures_penalties(self, current_solution):

        penalty = 0

        for course in range(self.instance_data.courses_count):
            if course.double_lectures == 'yes':
                for i in range(self.instance_data.days):
                    course_periods = []
                    for j in range(self.instance_data.periods_per_day):
                        course_in_day = False
                        for k in range(self.instance_data.rooms_count):
                            if course == current_solution[i][j][k]:
                                course_in_day = True
                                break

                        if course_in_day:
                            course_periods.append(1)
                        else:
                            course_periods.append(0)

                    for l in range(self.instance_data.periods_per_day):
                        if course_periods[l] == 1:
                            if l == 0 and course_periods[l+1] == 0:
                                penalty += 1
                            elif l == self.instance_data.periods_per_day - 1 and course_periods[l-1] == 0:
                                penalty += 1
                            elif course_periods[l-1] == 0 and course_periods[l+1] == 0:
                                penalty += 1

        return penalty


    # Lectures belonging to a curriculum should be adjacent to each other
    # (i.e., in consecutive periods). For a given curriculum we account for a
    # violation every time there is one lecture not adjacent to any other lecture within the same day.
    # Each isolated lecture in a curriculum counts as 1 violation.
    def isolated_lectures_penalties(self, current_solution, curriculum_penalties):

        penalty = 0

        for curriculum in self.instance_data.curricula:
            for i in range(self.instance_data.days):
                curriculum_periods = []
                for j in range(self.instance_data.periods_per_day):
                    curriculum_in_day = False
                    for k in range(self.instance_data.rooms_count):
                        course = current_solution[i][j][k]
                        if course != -1 and curriculum.id in self.instance_data.courses_curricula[course]:
                            curriculum_in_day = True
                            break
                    if curriculum_in_day:
                        curriculum_periods.append(1)
                    else:
                        curriculum_periods.append(0)

                for l in range(self.instance_data.periods_per_day):
                    if curriculum_periods[l] == 1:
                        if l == 0 and curriculum_periods[l+1] == 0:
                            penalty += self.penalties.P_COMP
                            curriculum_penalties[curriculum.id] += self.penalties.P_COMP
                        elif l == self.instance_data.periods_per_day - 1 and curriculum_periods[l-1] == 0:
                            penalty += self.penalties.P_COMP
                            curriculum_penalties[curriculum.id] += self.penalties.P_COMP
                        elif curriculum_periods[l-1] == 0 and curriculum_periods[l+1] == 0:
                            curriculum_penalties[curriculum.id] += self.penalties.P_COMP
                            penalty += self.penalties.P_COMP

        return penalty, curriculum_penalties

    # All lectures of a course should be given in the same room. Each distinct
    # room used for the lectures of a course, but the first, counts as 1 violation.
    def room_stability_penalties(self, current_solution, course_penalties):

        penalty = 0

        for course in range(self.instance_data.courses_count):
                course_room = None
                course_rooms = []
                for i in range(self.instance_data.days):
                    for j in range(self.instance_data.periods_per_day):
                        for k in range(self.instance_data.rooms_count):
                            if current_solution[i][j][k] == course:
                                room = self.instance_data.rooms[k].id
                                if course_room is None:
                                    course_room = room
                                    break
                                elif course_room != room and room not in course_rooms:
                                    course_rooms.append(room)
                                    penalty += self.penalties.P_STAB
                                    course_penalties[course] += self.penalties.P_STAB

        return penalty, course_penalties

