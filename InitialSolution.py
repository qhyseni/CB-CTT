import XMLtoOD
import ObjectiveFunction
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

# Declaration of INITIAL SOLUTION ad a 3-dimensional array
# The array contains days, each day contains periods, each period contains rooms in which the courses can take place
initial_solution = [[[0 for k in range(len(rooms))] for j in range(periods_per_day)] for i in range(days)]

# Lengths of arrays for future usage (-1 because we start counting by 0)
rooms_counter = len(rooms) - 1
days_counter = days - 1
periods_counter = periods_per_day - 1

# This array will be used to store all time slots scheduled for teachers
teachers_scheduled_timeslots = []

# The scheduling of course lectures will be done by placing each course lecture of each curriculum
# into time slot / room pair. Generation of Initial solution will be randomly
for curriculum in curricula:

    # This array will be used to store all time slots for one curriculum (group of students)
    curricula_scheduled_timeslots = []

    for c in curriculum.Courses:

        # Get one of the rooms from the room constraints, if any
        # course_rooms = next((i for i in room_constraints if i.Course == c), None)
        # if course_rooms is None:
        #     room = randint(0, len(rooms) - 1)
        # else:
        #     r = next(i for i in course_rooms.Rooms)
        #     room = [i for i, n in enumerate(rooms) if n.Id == r][0]

        # Get Course object data for the referenced course in the curriculum
        course = next(i for i in courses if i.Id == c)
        # Get number of course lectures (-1 because we start counting from 0)
        lectures_counter = int(course.Lectures)

        # Place course lectures into solution
        for lecture in range(lectures_counter):

            while True:
                # Generate random day/period/room based on respective ranges
                random_room = randint(0, rooms_counter)
                random_day = randint(0, days_counter)
                random_period = randint(0, periods_counter)

                timeslot = [random_day, random_period]
                teacher_timeslot = [course.TeacherId, timeslot]

                # Check if current course has restricted time slots
                cc = next((i for i in period_constraints if i.Course == c), None)
                # If yes and current time slot is one of the time slots declared unavailable for this course
                # Skip below steps and generate new random values
                # This to ensure meeting this as hard constraint
                if cc is not None and timeslot in cc.Timeslots:
                    continue

                # Ensure feasibility by checking hard constraints
                # Check if the room is not already scheduled for the time slot
                # Check if the teacher is not already scheduled for the time slot
                # Check if the group of students is not already scheduled for the time slot
                if initial_solution[random_day][random_period][random_room] == 0 \
                        and (teacher_timeslot not in teachers_scheduled_timeslots) \
                        and (timeslot not in curricula_scheduled_timeslots):
                    # If any of the conditions not met the loop won't break,
                    # it will repeat random value assignments until the conditions met and the loop breaks
                    break

            # Add scheduled lecture to the initial solution
            initial_solution[random_day][random_period][random_room] = [curriculum.Id, course.Id, course.TeacherId]

            # Add scheduled time slot to this array to mark unavailability of the teacher for this time slot for future scheduling
            teachers_scheduled_timeslots.append([course.TeacherId, timeslot])

            # Add scheduled time slot to this array to mark unavailability of the students of this curriculum
            # for this time slot for future scheduling
            curricula_scheduled_timeslots.append([random_day, random_period])

print("solution", initial_solution)

obj_func = ObjectiveFunction.ObjectveFunction('UD2')

score = obj_func.objective_function(initial_solution)

# obj_func.room_capacity_penalties(initial_solution)
# obj_func.min_wdays_penalties(initial_solution)
# obj_func.windows_penalties(initial_solution)
# obj_func.minmax_load_penalties(initial_solution)
# obj_func.double_lectures_penalties(initial_solution)
# obj_func.isolated_lectures_penalties(initial_solution)
# obj_func.room_stability_penalties(initial_solution)


print('done')
# Violations/Penalties


































