class PeriodConstraint:

    def __init__(self, course, timeslots):
        self._course = course
        self._timeslots = timeslots

    def getCourse(self):
        return self._course

    def setCourse(self, value):
        self._course = value

    Course = property(getCourse, setCourse)

    def getTimeslots(self):
        return self._timeslots

    def setTimeslots(self, value):
        self._timeslots = value

    Timeslots = property(getTimeslots, setTimeslots)


class RoomConstraint:

    def __init__(self, course, rooms):
        self._course = course
        self._rooms = rooms

    def getCourse(self):
        return self._course

    def setCourse(self, value):
        self._course = value

    Course = property(getCourse, setCourse)

    def getRooms(self):
        return self._rooms

    def setRooms(self, value):
        self._rooms = value

    Rooms = property(getRooms, setRooms)