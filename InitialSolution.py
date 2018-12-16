import XMLtoOD
import ObjectiveFunction
from random import randint


class InitialSolution:

    def __init__(self,  xmldata):

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

        self.rooms_count = len(self.rooms)

    def generate_solution(self):

        # Declaration of INITIAL SOLUTION ad a 3-dimensional array
        # The array contains days, each day contains periods, each period contains rooms in which the courses can take place
        initial_solution = [[[0 for k in range(len(self.rooms))] for j in range(self.periods_per_day)] for i in range(self.days)]

        # Lengths of arrays for future usage (-1 because we start counting by 0)
        rooms_counter = len(self.rooms) - 1
        days_counter = self.days - 1
        periods_counter = self.periods_per_day - 1

        # This array will be used to store all time slots scheduled for teachers
        teachers_scheduled_timeslots = []

        # The scheduling of course lectures will be done by placing each course lecture of each curriculum
        # into time slot / room pair. Generation of Initial solution will be randomly
        for curriculum in self.curricula:

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
                course = next(i for i in self.courses if i.Id == c)
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
                        cc = next((i for i in self.period_constraints if i.Course == c), None)
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
        return initial_solution



































