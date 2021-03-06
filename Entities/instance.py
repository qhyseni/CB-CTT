from Entities.penalty import penalty

class instance:

    def __init__(self, raw_data):

        penalties = penalty("UD2")

        # Number of available days (working days of University)
        self.days = raw_data.days()

        # Number of available periods per day (related to working hours of University)
        self.periods_per_day = raw_data.periods()

        # Number of minimum lectures that should be lectured per day (related to number of scheduled periods per day)
        self.daily_min_lectures = raw_data.min_daily_lectures()

        # Number of maximum lectures that can be lectured per day (related to number of scheduled periods per day)
        self.daily_max_lectures = raw_data.max_daily_lectures()

        # List of all courses taught at the University
        self.courses = raw_data.courses()

        # List of rooms available for lectures at University
        self.rooms = raw_data.rooms()

        # self.sorted_rooms = self.rooms.sort(key=lambda x: int(x.size), reverse=True)

        # List of curricula (programs) at University
        self.curricula = raw_data.curricula()

        # List of unavailable time slots per courses
        # teachers can pre-arrange periods when they're not available for lecturing their courses
        self.period_constraints = raw_data.period_constraints()

        # List of highly recommended rooms per courses
        self.room_constraints = raw_data.room_contraints()

        self.rooms_count = len(self.rooms)

        self.teachers = self.get_teachers()

        self.total_lectures = 0
        self.max_cost = 0

        sorted_rooms = sorted(self.rooms, key=lambda x: int(x.size), reverse=True)
        smallest_room_size = int(sorted_rooms[self.rooms_count - 1].size)
        for course in self.courses:
            self.total_lectures += int(course.lectures)

            course_curricula = [q for q in self.curricula if course.id in q.courses]

            temp_max_cost = \
                max(0, int(course.students) - smallest_room_size) * penalties.P_CAP \
                + len(course_curricula) * penalties.P_COMP
            if temp_max_cost > self.max_cost:
                self.max_cost = temp_max_cost

        self.max_cost += penalties.P_STAB


    def get_teachers(self):
        teachers = []
        for c in self.courses:
            if c.teacher_id not in teachers:
                teachers.append(c.teacher_id)

        return teachers

