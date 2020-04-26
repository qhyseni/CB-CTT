from Entities.course import course


class period_course:

    def __init__(self, day, period, course):
        self.day = day
        self.period = period
        self.course = course

    def __eq__(self, other):
        if not isinstance(other, period_course):
            return NotImplemented

        return self.day == other.day and self.period == other.period and self.course.id == other.course.id
