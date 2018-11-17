import XMLtoOD
from Entities.Penalties import Penalties


class ObjectveFunction:

    def __init__(self, type):
        self.type = type
        # Get data from XML File
        xmldata = XMLtoOD.XMLData()

        # Number of available days (working days of University)
        self.days = xmldata.Days

        # Number of available periods per day (related to working hours of University)
        self.periods_per_day = xmldata.PeriodsPerDay

        # Number of minimum lectures that should be lectured per day (related to number of scheduled periods per day)
        self.daily_min_lectures = xmldata.MinDailyLectures

        # Number of maximum lectures that can be lectured per day (related to number of scheduled periods per day)
        self.daily_max_lectures = xmldata.MaxDailyLectures

        # List of all courses taught at the University
        self.courses = xmldata.Courses

        # List of rooms available for lectures at University
        self.rooms = xmldata.Rooms

        # List of curricula (programs) at University
        self.curricula = xmldata.Curricula

        # List of unavailable time slots per courses
        # teachers can pre-arrange periods when they're not available for lecturing their courses
        self.period_constraints = xmldata.PeriodConstraints

        # List of highly recommended rooms per courses
        self.room_constraints = xmldata.RoomConstraints

        # Penalty scores
        self.penalties = Penalties(type)

        self.rooms_count = len(self.rooms)

    # Objective function is sum of all penalties (which penalties is )
    def objective_function(self, current_solution):
        if self.type == 'UD4':
            return (self.room_capacity_penalties(current_solution) + self.min_wdays_penalties(current_solution)
                    + self.windows_penalties(current_solution) + self.minmax_load_penalties(current_solution)
                    + self.double_lectures_penalties(current_solution))
        elif self.type == 'UD2':
            return (self.room_capacity_penalties(current_solution) + self.min_wdays_penalties(current_solution)
                    + self.isolated_lectures_penalties(current_solution) + self.room_stability_penalties(current_solution))


    # For each lecture, the number of students that attend the course must be less
    # than or equal the number of seats of all the rooms that host its lectures.
    # Each student above the capacity counts as 1 point of penalty.
    def room_capacity_penalties(self, current_solution):
        penalty = 0
        for i in range(self.days):
            for j in range(self.periods_per_day):
                for k in range(self.rooms_count):
                    if current_solution[i][j][k] != 0:
                        course_id = current_solution[i][j][k][1]
                        course = next(x for x in self.courses if x.Id == course_id)
                        students = int(course.Students)
                        room_size = int(self.rooms[k].Size)
                        if students - room_size > 0:
                            penalty += (students - room_size)
        return penalty

    # The lectures of each course must be spread into a given minimum number of days.
    # Each day below the minimum counts as 1 violation.
    def min_wdays_penalties(self, current_solution):
        penalty = 0
        for course in self.courses:
            min_days = int(course.MinDays)
            course_days = 0
            for i in range(self.days):
                course_in_day = False
                for j in range(self.periods_per_day):
                    for k in range(self.rooms_count):
                        if current_solution[i][j][k] != 0 and course.Id == current_solution[i][j][k][1]:
                            course_in_day = True
                            break
                    if course_in_day:
                        break
                if course_in_day:
                    course_days += 1

            if course_days < min_days:
                penalty += (min_days - course_days) * self.penalties.min_wdays_penalty

        return penalty


    # Lectures belonging to a curriculum should not have time windows
    # (i.e., periods without teaching) between them. For a given curriculum we account for
    # a violation every time there is one windows between two lectures within the same day.
    # Each time window in a curriculum counts as many violation as its length (in periods).
    def windows_penalties(self, current_solution):
        penalty = 0
        for curriculum in self.curricula:
            for i in range(self.days):
                check_for_windows = False
                curriculum_windows = 0
                for j in range(self.periods_per_day):
                    if check_for_windows:
                        curriculum_windows += 1
                    for k in range(self.rooms_count):
                        if current_solution[i][j][k] != 0 and curriculum.Id == current_solution[i][j][k][0]:
                            if check_for_windows:
                                penalty += curriculum_windows - 1
                                curriculum_windows = 0
                                break
                            else:
                                check_for_windows = True
                                break
        return penalty


    # For each curriculum the number of daily lectures should be within a given range.
    # Each lecture below the minimum or above the maximum counts as 1 violation.
    def minmax_load_penalties(self, current_solution):
        penalty = 0
        for curriculum in self.curricula:
            for i in range(self.days):
                daily_lectures = 0
                for j in range(self.periods_per_day):
                    for k in range(self.rooms_count):
                        if current_solution[i][j][k] != 0 and curriculum.Id == current_solution[i][j][k][0]:
                            daily_lectures += 1
                            break

                if daily_lectures > self.daily_max_lectures:
                    penalty += daily_lectures - self.daily_max_lectures
                elif daily_lectures < self.daily_min_lectures:
                    penalty += self.daily_min_lectures - daily_lectures

        return penalty


    # Some courses require that lectures in the same day are grouped together
    # (double lectures). For a course that requires grouped lectures, every time there is more than
    # one lecture in one day, a lecture non-grouped to another is not allowed. Two lectures are
    # grouped if they are adjacent and in the same room. Each non-grouped lecture counts as 1
    # violation.
    def double_lectures_penalties(self, current_solution):
        penalty = 0
        for course in self.courses:
            if course.DoubleLectures == 'yes':
                for i in range(self.days):
                    course_periods = []
                    for j in range(self.periods_per_day):
                        course_in_day = False
                        for k in range(self.rooms_count):
                            if current_solution[i][j][k] != 0 and course.Id == current_solution[i][j][k][1]:
                                course_in_day = True
                                break

                        if course_in_day:
                            course_periods.append(1)
                        else:
                            course_periods.append(0)

                    for l in range(self.periods_per_day):
                        if course_periods[l] == 1:
                            if l == 0 and course_periods[l+1] == 0:
                                penalty += 1
                            elif l == self.periods_per_day - 1 and course_periods[l-1] == 0:
                                penalty += 1
                            elif course_periods[l-1] == 0 and course_periods[l+1] == 0:
                                penalty += 1

        return penalty


    # Lectures belonging to a curriculum should be adjacent to each other
    # (i.e., in consecutive periods). For a given curriculum we account for a
    # violation every time there is one lecture not adjacent to any other lecture within the same day.
    # Each isolated lecture in a curriculum counts as 1 violation.
    def isolated_lectures_penalties(self, current_solution):
        penalty = 0
        for curriculum in self.curricula:
                for i in range(self.days):
                    curriculum_periods = []
                    for j in range(self.periods_per_day):
                        curriculum_in_day = False
                        for k in range(self.rooms_count):
                            if current_solution[i][j][k] != 0 and curriculum.Id == current_solution[i][j][k][0]:
                                curriculum_in_day = True
                                break

                        if curriculum_in_day:
                            curriculum_periods.append(1)
                        else:
                            curriculum_periods.append(0)

                    for l in range(self.periods_per_day):
                        if curriculum_periods[l] == 1:
                            if l == 0 and curriculum_periods[l+1] == 0:
                                penalty += 1
                            elif l == self.periods_per_day - 1 and curriculum_periods[l-1] == 0:
                                penalty += self.penalties.isolated_lectures_penalty
                            elif curriculum_periods[l-1] == 0 and curriculum_periods[l+1] == 0:
                                penalty += self.penalties.isolated_lectures_penalty

        return penalty


    # All lectures of a course should be given in the same room. Each distinct
    # room used for the lectures of a course, but the first, counts as 1 violation.
    def room_stability_penalties(self, current_solution):
        penalty = 0
        for course in self.courses:
                course_room = None
                course_rooms = []
                for i in range(self.days):
                    for j in range(self.periods_per_day):
                        for k in range(self.rooms_count):
                            if current_solution[i][j][k] != 0 and current_solution[i][j][k][1] == course.Id:
                                room = self.rooms[k].Id
                                if course_room is None:
                                    course_room = room
                                    break
                                elif course_room != room and room not in course_rooms:
                                    course_rooms.append(room)
                                    penalty += self.penalties.room_stability_penalty

        return penalty

