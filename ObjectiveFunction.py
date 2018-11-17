import XMLtoOD
from random import randint

# Get data from XML File
xmldata = XMLtoOD.XMLData()
xmldata2 = XMLtoOD.XMLData()

# Number of available days (working days of University)
days = xmldata.Days
print("days", days)

# Number of available periods per day (related to working hours of University)
periods_per_day = xmldata.PeriodsPerDay
print("periods_per_day", periods_per_day)

# Number of minimum lectures that should be lectured per day (related to number of scheduled periods per day)
daily_min_lectures = xmldata.MinDailyLectures
print("daily_min_lectures", daily_min_lectures)

# Number of maximum lectures that can be lectured per day (related to number of scheduled periods per day)
daily_max_lectures = xmldata.MaxDailyLectures
print("daily_max_lectures", daily_max_lectures)

# List of all courses taught at the University
courses = xmldata.Courses
print("courses", len(courses))

# List of rooms available for lectures at University
rooms = xmldata.Rooms
print("rooms", len(rooms))

# List of curricula (programs) at University
curricula = xmldata.Curricula
print("curricula", len(curricula))

# List of unavailable time slots per courses
# teachers can pre-arrange periods when they're not available for lecturing their courses
period_constraints = xmldata.PeriodConstraints
print("period_constraints", len(period_constraints))

# List of highly recommended rooms per courses
room_constraints = xmldata.RoomConstraints
print("room_constraints", len(room_constraints))

room_capacity_penalty = 1
min_wdays_penalty = 1
windows_penalty = 1
minmax_load_penalty = 1
double_lectures_penalty = 1

rooms_count = len(rooms)


# For each lecture, the number of students that attend the course must be less
# than or equal the number of seats of all the rooms that host its lectures.
# Each student above the capacity counts as 1 point of penalty.
def room_capacity_penalties(current_solution):
    penalty = 0
    for i in range(days):
        for j in range(periods_per_day):
            for k in range(rooms_count):
                if current_solution[i][j][k] != 0:
                    course_id = current_solution[i][j][k][1]
                    course = next(x for x in courses if x.Id == course_id)
                    students = int(course.Students)
                    room_size = int(rooms[k].Size)
                    if students - room_size > 0:
                        penalty += (students - room_size)
    return penalty


# The lectures of each course must be spread into a given minimum number of days.
# Each day below the minimum counts as 1 violation.
def min_wdays_penalties(current_solution):
    penalty = 0
    for course in courses:
        min_days = int(course.MinDays)
        course_days = 0
        for i in range(days):
            course_in_day = False
            for j in range(periods_per_day):
                for k in range(rooms_count):
                    if current_solution[i][j][k] != 0 and course.Id == current_solution[i][j][k][1]:
                        course_in_day = True
                        break
                if course_in_day:
                    break
            if course_in_day:
                course_days += 1

        if course_days < min_days:
            penalty += (min_days - course_days)

    return penalty


# Lectures belonging to a curriculum should not have time windows
# (i.e., periods without teaching) between them. For a given curriculum we account for
# a violation every time there is one windows between two lectures within the same day.
# Each time window in a curriculum counts as many violation as its length (in periods).
def windows_penalties(current_solution):
    penalty = 0
    for curriculum in curricula:
        for i in range(days):
            check_for_windows = False
            curriculum_windows = 0
            for j in range(periods_per_day):
                if check_for_windows:
                    curriculum_windows += 1
                for k in range(rooms_count):
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
def minmax_load_penalties(current_solution):
    penalty = 0
    for curriculum in curricula:
        for i in range(days):
            daily_lectures = 0
            for j in range(periods_per_day):
                for k in range(rooms_count):
                    if current_solution[i][j][k] != 0 and curriculum.Id == current_solution[i][j][k][0]:
                        daily_lectures += 1
                        break

            if daily_lectures > daily_max_lectures:
                penalty += daily_lectures - daily_max_lectures
            elif daily_lectures < daily_min_lectures:
                penalty += daily_min_lectures - daily_lectures

    return penalty


# Some courses require that lectures in the same day are grouped together
# (double lectures). For a course that requires grouped lectures, every time there is more than
# one lecture in one day, a lecture non-grouped to another is not allowed. Two lectures are
# grouped if they are adjacent and in the same room. Each non-grouped lecture counts as 1
# violation.
def double_lectures_penalties(current_solution):
    penalty = 0
    for course in courses:
        if course.DoubleLectures == 'yes':
            for i in range(days):
                course_periods = []
                for j in range(periods_per_day):
                    course_in_day = False
                    for k in range(rooms_count):
                        if current_solution[i][j][k] != 0 and course.Id == current_solution[i][j][k][1]:
                            course_in_day = True
                            break

                    if course_in_day:
                        course_periods.append(1)
                    else:
                        course_periods.append(0)

                for l in range(periods_per_day):
                    if course_periods[l] == 1:
                        if l == 0 and course_periods[l+1] == 0:
                            penalty += 1
                        elif l == periods_per_day - 1 and course_periods[l-1] == 0:
                            penalty += 1
                        elif course_periods[l-1] == 0 and course_periods[l+1] == 0:
                            penalty += 1

    return penalty


# Lectures belonging to a curriculum should be adjacent to each other
# (i.e., in consecutive periods). For a given curriculum we account for a
# violation every time there is one lecture not adjacent to any other lecture within the same day.
# Each isolated lecture in a curriculum counts as 1 violation.
def isolated_lectures_penalties(current_solution):
    penalty = 0
    for curriculum in curricula:
            for i in range(days):
                curriculum_periods = []
                for j in range(periods_per_day):
                    curriculum_in_day = False
                    for k in range(rooms_count):
                        if current_solution[i][j][k] != 0 and curriculum.Id == current_solution[i][j][k][0]:
                            curriculum_in_day = True
                            break

                    if curriculum_in_day:
                        curriculum_periods.append(1)
                    else:
                        curriculum_periods.append(0)

                for l in range(periods_per_day):
                    if curriculum_periods[l] == 1:
                        if l == 0 and curriculum_periods[l+1] == 0:
                            penalty += 1
                        elif l == periods_per_day - 1 and curriculum_periods[l-1] == 0:
                            penalty += 1
                        elif curriculum_periods[l-1] == 0 and curriculum_periods[l+1] == 0:
                            penalty += 1

    return penalty


# All lectures of a course should be given in the same room. Each distinct
# room used for the lectures of a course, but the first, counts as 1 violation.
def room_stability_penalties(current_solution):
    penalty = 0
    for course in courses:
            course_room = None
            course_rooms = []
            for i in range(days):
                for j in range(periods_per_day):
                    for k in range(rooms_count):
                        if current_solution[i][j][k] != 0 and current_solution[i][j][k][1] == course.Id:
                            room = rooms[k].Id
                            if course_room is None:
                                course_room = room
                                break
                            elif course_room != room and room not in course_rooms:
                                course_rooms.append(room)
                                penalty += 1

    return penalty

