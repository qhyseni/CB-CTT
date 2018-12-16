import xml.etree.ElementTree as ET
from Entities import Course, Room, Curriculum, Constraints


# Convert data from XML instances to object properties
# The XML format should be validated against http://tabu.diegm.uniud.it/ctt/cb_ctt.dtd

class XMLData:

    def __init__(self):
        tree = ET.parse('Files/comp01.xml')
        self.root = tree.getroot()

    def getDays(self):

        for elem in self.root.findall("./descriptor/days"):
            days = elem.attrib['value']
        return int(days)

    Days = property(getDays)

    def getPeriods(self):

        for elem in self.root.findall("./descriptor/periods_per_day"):
            periods_per_day = elem.attrib['value']
        return int(periods_per_day)

    PeriodsPerDay = property(getPeriods)

    def getMinDailyLectures(self):
        for elem in self.root.findall("./descriptor/daily_lectures"):
            daily_lectures_min = elem.attrib['min']
        return int(daily_lectures_min)

    MinDailyLectures = property(getMinDailyLectures)

    def getMaxDailyLectures(self):

        for elem in self.root.findall("./descriptor/daily_lectures"):
            daily_lectures_max = elem.attrib['max']
        return int(daily_lectures_max)

    MaxDailyLectures = property(getMaxDailyLectures)

    def getCourses(self):

        courses = []
        for elem in self.root.findall("./courses/course"):
            course = Course.Course(elem.attrib['id'], elem.attrib['teacher'], elem.attrib['lectures'],
                                   elem.attrib['min_days'], elem.attrib['students'], elem.attrib['double_lectures'])
            courses.append(course)
        return courses

    Courses = property(getCourses)

    def getRooms(self):

        rooms = []
        for elem in self.root.findall("./rooms/room"):
            room = Room.Room(elem.attrib['id'], elem.attrib['size'], elem.attrib['building'])
            rooms.append(room)
        return rooms

    Rooms = property(getRooms)

    def getCurricula(self):

        curricula = []
        for elem in self.root.findall("./curricula/curriculum"):
            q_courses = []
            for c in self.root.findall(f"./curricula/curriculum[@id='{elem.attrib['id']}']/course"):
                q_courses.append(c.attrib['ref'])
            curriculum = Curriculum.Curriculum(elem.attrib['id'], q_courses)
            curricula.append(curriculum)
        return curricula

    Curricula = property(getCurricula)

    def getPeriodConstraints(self):

        period_constraints = []
        for elem in self.root.findall("./constraints/constraint[@type='period']"):
            timeslots = []
            for t in self.root.findall(f"./constraints/constraint[@course='{elem.attrib['course']}']/timeslot"):
                timeslot = [int(t.attrib['day']), int(t.attrib['period'])]
                timeslots.append(timeslot)
            pc = Constraints.PeriodConstraint(elem.attrib['course'], timeslots)
            period_constraints.append(pc)
        return period_constraints

    PeriodConstraints = property(getPeriodConstraints)

    def getRoomConstraints(self):

        room_constraints = []
        for elem in self.root.findall("./constraints/constraint[@type='room']"):
            crooms = []
            for t in self.root.findall(f"./constraints/constraint[@course='{elem.attrib['course']}']/room"):
                crooms.append(t.attrib['ref'])
            rc = Constraints.RoomConstraint(elem.attrib['course'], crooms)
            room_constraints.append(rc)
        return room_constraints

    RoomConstraints = property(getRoomConstraints)
