from random import randint


class initial_solution2:

    def __init__(self,  xmldata):

        # Number of available days (working days of University)
        self.days = xmldata.days

        # Number of available periods per day (related to working hours of University)
        self.periods_per_day = xmldata.periods

        # Number of minimum lectures that should be lectured per day (related to number of scheduled periods per day)
        self.daily_min_lectures = xmldata.min_daily_lecture

        # Number of maximum lectures that can be lectured per day (related to number of scheduled periods per day)
        self.daily_max_lectures = xmldata.max_daily_lectures

        # List of all courses taught at the University
        self.courses = xmldata.courses

        # List of rooms available for lectures at University
        self.rooms = xmldata.rooms

        # List of curricula (programs) at University
        self.curricula = xmldata.curricula

        # List of unavailable time slots per courses
        # teachers can pre-arrange periods when they're not available for lecturing their courses
        self.period_constraints = xmldata.period_constraints

        # List of highly recommended rooms per courses
        self.room_constraints = xmldata.room_constraints

        self.rooms_count = len(self.rooms)

    def generate_solution(self):

        # Declaration of INITIAL SOLUTION ad a 3-dimensional array
        # The array contains days, each day contains periods, each period contains rooms in which the courses can take place
        initial_solution = [[["" for k in range(len(self.rooms))] for j in range(self.periods_per_day)] for i in range(self.days)]

        # Lengths of arrays for future usage (-1 because we start counting by 0)
        rooms_counter = len(self.rooms) - 1
        days_counter = self.days - 1
        periods_counter = self.periods_per_day - 1

        # This array will be used to store all time slots for one curriculum (group of students)
        curricula_scheduled_timeslots = []
        teachers_scheduled_timeslots = []
        # The scheduling of course lectures will be done by placing each course lecture of each curriculum
        # into time slot / room pair. Generation of Initial solution will be randomly

        for curriculum in self.curricula:

            day = 0;
            period = 0;

            for c in curriculum.courses:

                if c == "c0071":
                    esa = True

                # # Get one of the rooms from the room constraints, if any
                course = next((i for i in self.courses if i.id == c), None)
            # if course_rooms is not None:
            #     room = randint(0, len(rooms) - 1)
            # else:
            #     r = next(i for i in course_rooms.Rooms)
            #     room = [i for i, n in enumerate(rooms) if n.id == r][0]

            # Get Course object data for the referenced course in the curriculum
            # course = next(i for i in self.courses if i.id == c)
            # Get number of course lectures (-1 because we start counting from 0)

                lectures_counter = int(course.lectures)
                counter = 0
            # place course lectures into solution
                for lecture in range(lectures_counter):

                    while True:
                        counter +=1
                        print(counter)
                # Generate random day/period/room based on respective ranges
                        random_room = randint(0, rooms_counter)
                        period += 1

                        if period == self.periods_per_day:
                            period = 0
                            day += 1
                            if day == self.days:
                                day = 0

                        timeslot = [day, period]
                        teacher_timeslot = [course.teacher_id, timeslot]

                        if teacher_timeslot in teachers_scheduled_timeslots:
                            continue

                # Check if current course has restricted time slots
                        period_constrained_course = next((i for i in self.period_constraints if i.course == course.id), None)
                # If yes and current time slot is one of the time slots declared unavailable for this course
                # Skip below steps and generate new random values
                # This to ensure meeting this as hard constraint
                        if period_constrained_course is not None and timeslot in period_constrained_course.timeslots:
                            continue


                # Check if current course has restricted rooms
                        room_constrained_course = next((i for i in self.room_constraints if i.course == course.id), None)
                # If yes and current time slot is one of the time slots declared unavailable for this course
                # Skip below steps and generate new random values
                # This to ensure meeting this as hard constraint
                        if room_constrained_course is not None and self.rooms[random_room].id in room_constrained_course.rooms:
                            continue

                # Ensure feasibility by checking hard constraints
                # Check if the room is not already scheduled for the time slot
                # check if the teacher is not already scheduled for the time slot
                # check if the group of students is not already scheduled for the time slot
                        if initial_solution[day][period][random_room] == "":
                    # If any of the conditions not met the loop won't break,
                    # it will repeat random value assignments until the conditions met and the loop breaks
                            break

                # Add scheduled lecture to the initial solution
                    initial_solution[day][period][random_room] = course.id
                    print(day, period, random_room, course.id)

                # Add scheduled time slot to this array to mark unavailability of the teacher for this time slot for future scheduling
                    teachers_scheduled_timeslots.append(teacher_timeslot)

                # # Add scheduled time slot to this array to mark unavailability of the students of this curriculum
                # # for this time slot for future scheduling
                # curricula_scheduled_timeslots.append([random_day, random_period])

        print("solution", initial_solution)
        return initial_solution



































