import xml.etree.ElementTree as ET
from Entities import course, room, curriculum, constraints
from Experiments.configs import configs
from Experiments.statistics import statistics


# Convert data from XML instances to object properties
# The XML format should be validated against http://tabu.diegm.uniud.it/ctt/cb_ctt.dtd

class ectt_data:

    def __init__(self):

        self.raw_courses = []
        self.raw_rooms = []
        self.raw_curricula = []
        self.raw_period_constraints = []
        self.raw_room_contraints = []

        add_courses = False
        add_rooms = False
        add_curricula = False
        add_unavailability_constraints = False
        add_room_constraints = False

        with open(configs.datasets_dir+configs.instance_name, 'rU') as f:
            for line in f:
                line = line.rstrip("\n")

                if line.__contains__("Days"):
                    self.raw_days=line.split(" ")[1]
                elif line.__contains__("Periods_per_day"):
                    self.raw_periods=line.split(" ")[1]
                elif line.__contains__("Min_Max_Daily_Lectures"):
                    self.raw_min_daily_lectures=line.split(" ")[1]
                    self.raw_max_daily_lectures=line.split(" ")[2]
                elif line.__contains__("Min_Max_Daily_Lectures"):
                    self.raw_min_daily_lectures=line.split(" ")[1]

                elif add_courses:
                    if line == "":
                        add_courses = False
                        continue
                    else:
                        line_array = line.split(" ")

                        c = course.course(line_array[0],
                                          line_array[1],
                                          line_array[2],
                                          line_array[3],
                                          line_array[4],
                                          line_array[5],)

                        self.raw_courses.append(c)

                elif add_rooms:
                    if line == "":
                        add_rooms= False
                        continue
                    else:
                        line_array = line.split(" ")

                        r = room.room(line_array[0],line_array[1], line_array[2])
                        self.raw_rooms.append(r)

                elif add_curricula:
                    if line == "":
                        add_curricula= False
                        continue
                    else:
                        line_array = line.split(" ")

                        q_courses = []
                        i = 2
                        counter = 0
                        while (counter < int(line_array[1])):
                            q_courses.append(line_array[i])
                            i += 1
                            counter += 1;
                        q = curriculum.curriculum(line_array[0], q_courses)
                        self.raw_curricula.append(q)

                elif add_unavailability_constraints:
                    if line == "":
                        add_unavailability_constraints= False
                        continue
                    else:
                        line_array = line.split(" ")

                        timeslot = [int(line_array[1]), int(line_array[2])]
                        uc = [line_array[0], timeslot]

                        self.raw_period_constraints.append(uc)

                elif add_room_constraints:
                    if line == "":
                        add_room_constraints = False
                        continue
                    else:
                        line_array = line.split(" ")

                        rc = [line_array[0], line_array[1]]

                        self.raw_room_contraints.append(rc)

                elif line.__contains__("COURSES"):
                    add_courses = True
                elif line.__contains__("ROOMS"):
                    add_rooms= True
                elif line.__contains__("CURRICULA"):
                    add_curricula= True
                elif line.__contains__("UNAVAILABILITY_CONSTRAINTS"):
                    add_unavailability_constraints= True
                elif line.__contains__("ROOM_CONSTRAINTS"):
                    add_room_constraints= True

    def days(self):
        return int(self.raw_days)

    def periods(self):
        return int(self.raw_periods)

    def min_daily_lectures(self):
        return int(self.raw_min_daily_lectures)

    def max_daily_lectures(self):
        return int(self.raw_max_daily_lectures)

    def courses(self):
        return self.raw_courses

    def rooms(self):
        return self.raw_rooms

    def curricula(self):
        return self.raw_curricula

    def period_constraints(self):

        period_constraints = []

        for course in self.raw_courses:

            timeslots = [t[1] for t in self.raw_period_constraints if t[0] == course.id]
            if timeslots == []:
                continue
            else:
                pc = constraints.period_contraint(course.id, timeslots)
                period_constraints.append(pc)

        return period_constraints

    def room_contraints(self):

        room_constraints = []

        for course in self.raw_courses:

            rooms = [t[1] for t in self.raw_room_contraints if t[0] == course.id]
            if rooms == []:
                continue
            else:
                rc = constraints.room_constraint(course.id, rooms)
                room_constraints.append(rc)

        return room_constraints
