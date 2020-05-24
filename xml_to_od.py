import xml.etree.ElementTree as ET
from Entities import course, room, curriculum, constraints
from Experiments.statistics import statistics

# Convert data from XML instances to object properties
# The XML format should be validated against http://tabu.diegm.uniud.it/ctt/cb_ctt.dtd

class xml_data:

    def __init__(self):
        tree = ET.parse('Files/comp04.xml')
        self.root = tree.getroot()

    def days(self):

        for elem in self.root.findall("./descriptor/days"):
            days = elem.attrib['value']
        return int(days)

    def periods(self):

        for elem in self.root.findall("./descriptor/periods_per_day"):
            periods_per_day = elem.attrib['value']
        return int(periods_per_day)

    def min_daily_lectures(self):
        for elem in self.root.findall("./descriptor/daily_lectures"):
            daily_lectures_min = elem.attrib['min']
        return int(daily_lectures_min)

    def max_daily_lectures(self):

        for elem in self.root.findall("./descriptor/daily_lectures"):
            daily_lectures_max = elem.attrib['max']
        return int(daily_lectures_max)

    def courses(self):

        courses = []
        for elem in self.root.findall("./courses/course"):
            c = course.course(elem.attrib['id'],
                              elem.attrib['teacher'],
                              elem.attrib['lectures'],
                              elem.attrib['min_days'],
                              elem.attrib['students'],
                              elem.attrib['double_lectures'])
            courses.append(c)
        return courses

    def rooms(self):

        rooms = []
        for elem in self.root.findall("./rooms/room"):
            r = room.room(elem.attrib['id'], elem.attrib['size'], elem.attrib['building'])
            rooms.append(r)
        return rooms

    def curricula(self):

        curricula = []
        for elem in self.root.findall("./curricula/curriculum"):
            q_courses = []
            for c in self.root.findall(f"./curricula/curriculum[@id='{elem.attrib['id']}']/course"):
                q_courses.append(c.attrib['ref'])
            q = curriculum.curriculum(elem.attrib['id'], q_courses)
            curricula.append(q)
        return curricula

    def period_constraints(self):

        period_constraints = []
        for elem in self.root.findall("./constraints/constraint[@type='period']"):
            timeslots = []
            for t in self.root.findall(f"./constraints/constraint[@course='{elem.attrib['course']}']/timeslot"):
                timeslot = [int(t.attrib['day']), int(t.attrib['period'])]
                timeslots.append(timeslot)
            pc = constraints.period_contraint(elem.attrib['course'], timeslots)
            period_constraints.append(pc)
        return period_constraints

    def room_contraints(self):

        room_constraints = []
        for elem in self.root.findall("./constraints/constraint[@type='room']"):
            crooms = []
            for t in self.root.findall(f"./constraints/constraint[@course='{elem.attrib['course']}']/room"):
                crooms.append(t.attrib['ref'])
            rc = constraints.room_constraint(elem.attrib['course'], crooms)
            room_constraints.append(rc)
        return room_constraints

