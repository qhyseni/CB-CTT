from random import randint
from maxSAT_repair_operator import maxSAT

class initial_solution:

    def __init__(self, instance_data):

        self.instance_data = instance_data
        # Number of available days (working days of University)
        self.days = instance_data.days

        # Number of available periods per day (related to working hours of University)
        self.periods_per_day = instance_data.periods

        # Number of minimum lectures that should be lectured per day (related to number of scheduled periods per day)
        self.daily_min_lectures = instance_data.min_daily_lecture

        # Number of maximum lectures that can be lectured per day (related to number of scheduled periods per day)
        self.daily_max_lectures = instance_data.max_daily_lectures

        # List of all courses taught at the University
        self.courses = instance_data.courses

        # List of rooms available for lectures at University
        self.rooms = instance_data.rooms

        # List of curricula (programs) at University
        self.curricula = instance_data.curricula

        # List of unavailable time slots per courses
        # teachers can pre-arrange periods when they're not available for lecturing their courses
        self.period_constraints = instance_data.period_constraints

        # List of highly recommended rooms per courses
        self.room_constraints = instance_data.room_constraints

        self.rooms_count = len(self.rooms)

        # Lengths of arrays for future usage (-1 because we start counting by 0)
        self.rooms_max_range = self.rooms_count - 1
        self.days_max_range = self.days - 1
        self.periods_max_range = self.periods_per_day - 1

        self.curricula_scheduled_timeslots = []
        self.teachers_scheduled_timeslots = []

    def generate_solution(self):

        # Declaration of INITIAL SOLUTION ad a 3-dimensional array
        # The array contains days, each day contains periods, each period contains rooms
        # in which the courses can take place
        initial_solution = [[["" for k in range(len(self.rooms))] for j in range(self.periods_per_day)] for i in range(self.days)]

        # The scheduling of course lectures will be done by placing each course lecture of each curriculum
        # into time slot / room pair. Generation of Initial solution will be randomly

        courses_scores = []
        for c in self.courses:

            score = 0

            period_constrained_course = next((i for i in self.period_constraints if i.course == c.id), None)
            if period_constrained_course is not None:
                score += len(period_constrained_course.timeslots)

            room_constrained_course = next((i for i in self.room_constraints if i.course == c.id), None)
            if room_constrained_course is not None:
               score += len(room_constrained_course.rooms)

            course_curricula = []

            for curriculum in self.curricula:
                curriculum_course = next((i for i in curriculum.courses if i == c.id), None)
                if curriculum_course is not None:
                    course_curricula.append(curriculum.id)
                    score += (len(curriculum.courses) - 1)

            score += len(course_curricula)

            courses_scores.append([c, score])

        courses_scores = sorted(courses_scores , key=lambda c: c[1], reverse=True)
        for cs in courses_scores:
            pc = next((i for i in self.period_constraints if i.course == cs[0].id), None)
            if pc is not None:
                timeslots = pc.timeslots
            else:
                timeslots = None

            initial_solution, generate_with_maxsat = self.schedule_course(cs[0], initial_solution, timeslots)

            if generate_with_maxsat:
                break

        if generate_with_maxsat:
            lines = []
            for course in self.courses:
                lectures_counter = int(course.lectures)
                # place course lectures into solution
                for lecture in range(lectures_counter):
                    line = course.id + " " + "-1" + " " + "-1" + " " + "-1" + '\n'
                    lines.append(line)

            initial_solution = maxSAT.solve(self.instance_data, lines)

        print("solution", initial_solution)
        return initial_solution

    def schedule_course(self, course, initial_solution, constrained_timeslots):

        generate_with_maxsat = False

        course_curricula = []

        for curriculum in self.curricula:
            curriculum_course = next((i for i in curriculum.courses if i == course.id), None)
            if curriculum_course is not None:
                course_curricula.append(curriculum.id)

        lectures_counter = int(course.lectures)
        # place course lectures into solution
        for lecture in range(lectures_counter):
            counter = 0
            while True:

                if counter == 100:
                    generate_with_maxsat = True
                    break

                counter += 1

                # Generate random day/period/room based on respective ranges
                random_room = randint(0, self.rooms_max_range)
                random_day = randint(0, self.days_max_range)
                random_period = randint(0, self.periods_max_range)

                timeslot = [random_day, random_period]

                # If current course has restricted time slots and
                # current time slot is one of the time slots declared unavailable for this course
                # Skip below steps and generate new random values
                # This to ensure meeting this as hard constraint
                if constrained_timeslots is not None and timeslot in constrained_timeslots:
                    continue

                # # Check if current course has restricted rooms
                # room_constrained_course = next((i for i in self.room_constraints if i.course == course.id), None)
                # # If yes and current time slot is one of the time slots declared unavailable for this course
                # # Skip below steps and generate new random values
                # # This to ensure meeting this as hard constraint
                # if room_constrained_course is not None and self.rooms[random_room].id in room_constrained_course.rooms:
                #     continue

                teacher_timeslot = [course.teacher_id, timeslot]

                if teacher_timeslot in self.teachers_scheduled_timeslots:
                    continue

                next_iteration = False;
                for q in course_curricula:
                    curriculum_timeslot = [q, timeslot]
                    if curriculum_timeslot in self.curricula_scheduled_timeslots:
                        next_iteration = True
                        break

                if next_iteration:
                    continue

                # Ensure feasibility by checking hard constraints
                # Check if the room is not already scheduled for the time slot
                # check if the teacher is not already scheduled for the time slot
                # check if the group of students is not already scheduled for the time slot
                if initial_solution[random_day][random_period][random_room] == "":
                    # If any of the conditions not met the loop won't break,
                    # it will repeat random value assignments until the conditions met and the loop breaks
                    break

            if generate_with_maxsat:
                break

            # Add scheduled time slot to this array to mark unavailability of the teacher for this timeslot
            # for future scheduling
            self.teachers_scheduled_timeslots.append(teacher_timeslot)

            # # Add scheduled time slot to this array to mark unavailability of the students of this curriculum
            # # for this time slot for future scheduling
            for q in course_curricula:
                self.curricula_scheduled_timeslots.append([q, timeslot])

            # Add scheduled lecture to the initial solution
            initial_solution[random_day][random_period][random_room] = course.id

        return initial_solution, generate_with_maxsat




























