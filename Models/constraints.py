class period_contraint:

    def __init__(self, course, timeslots):
        self.course = course
        self.timeslots = timeslots

    # course = property()
    #
    # timeslots = property()


class room_constraint:

    def __init__(self, course, rooms):
        self.course = course
        self.rooms = rooms

    # course = property()
    #
    # rooms = property()
