
class xml_instance:

    def __init__(self, days,
                 periods,
                 min_daily_lectures,
                 max_daily_lectures,
                 courses,
                 rooms,
                 curricula,
                 period_constraints,
                 room_contraints):

        self.days = days
        self.periods = periods
        self.min_daily_lecture = min_daily_lectures
        self.max_daily_lectures = max_daily_lectures
        self.courses = courses
        self.rooms = rooms
        self.curricula = curricula
        self.period_constraints = period_constraints
        self.room_constraints = room_contraints
