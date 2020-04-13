class assignment_cost:

    def __init__(self, day, period, room, course, cost):
        self.day = day
        self.period = period
        self.room = room
        self.course = course
        self.cost = cost

    def __eq__(self, other):
        if not isinstance(other, assignment_cost):
            return NotImplemented

        return self.day == other.day and self.period == other.period and self.room == other.room and self.course == other.course and self.cost == other.cost