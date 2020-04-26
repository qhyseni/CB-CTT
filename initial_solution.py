from random import randint
from alns_repair_operators import repair_operators
from operators_lookup import operators_lookup

class initial_solution:

    def __init__(self, instance_data):

        self.instance_data = instance_data
        # Lengths of arrays for future usage (-1 because we start counting by 0)
        self.rooms_max_range = self.instance_data.rooms_count - 1
        self.days_max_range = self.instance_data.days - 1
        self.periods_max_range = self.instance_data.periods_per_day - 1

        self.curricula_scheduled_timeslots = {}
        self.teachers_scheduled_timeslots = {}

    def generate_solution(self):

        # Declaration of INITIAL SOLUTION as a 3-dimensional array
        # The array contains days, each day contains periods, each period contains rooms
        # in which the courses can take place
        schedule = [[["" for k in range(len(self.instance_data.rooms))] for j in range(self.instance_data.periods_per_day)] for i in range(self.instance_data.days)]

        unscheduled_lectures = []
        for course in self.instance_data.courses:
            lectures_counter = int(course.lectures)
            # place course lectures into solution
            for lecture in range(lectures_counter):
                unscheduled_lectures.append(course.id)

        initial_solution = repair_operators.two_stage_repair_operator(schedule, self.instance_data, unscheduled_lectures, "best", "match", operators_lookup.priority_rules[0])

        return initial_solution



























