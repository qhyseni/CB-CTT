from random import randint
from alns_repair_operators import repair_operators
from operators_lookup import operators_lookup
from maxSAT_repair_operator import maxSAT
from Experiments.statistics import statistics

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
        print("Generating Initial Solution...")
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

        initial_solution, Uc = repair_operators.two_stage_repair_operator(schedule, self.instance_data, unscheduled_lectures, "best", "greatest", operators_lookup.priority_rules[0])

        initial_solution[0][0][0] = 'c4'
        initial_solution[0][0][1] = 'c1'
        initial_solution[0][0][2] = ''

        initial_solution[0][1][0] = 'c9'
        initial_solution[0][1][1] = 'c2'
        initial_solution[0][1][2] = ''

        initial_solution[0][2][0] = 'c1'
        initial_solution[0][2][1] = 'c8'
        initial_solution[0][2][2] = ''

        initial_solution[0][3][0] = 'c3'
        initial_solution[0][3][1] = 'c10'
        initial_solution[0][3][2] = 'c1'

        initial_solution[1][0][0] = 'c8'
        initial_solution[1][0][1] = ''
        initial_solution[1][0][2] = ''

        initial_solution[1][1][0] = ''
        initial_solution[1][1][1] = 'c9'
        initial_solution[1][1][2] = ''

        initial_solution[1][2][0] = 'c2'
        initial_solution[1][2][1] = 'c10'
        initial_solution[1][2][2] = 'c5'

        initial_solution[1][3][0] = 'c5'
        initial_solution[1][3][1] = ''
        initial_solution[1][3][2] = ''

        initial_solution[2][0][0] = 'c6'
        initial_solution[2][0][1] = 'c10'
        initial_solution[2][0][2] = ''

        initial_solution[2][1][0] = 'c7'
        initial_solution[2][1][1] = 'c3'
        initial_solution[2][1][2] = 'c10'

        initial_solution[2][2][0] = 'c4'
        initial_solution[2][2][1] = ''
        initial_solution[2][2][2] = 'c5'

        initial_solution[2][3][0] = ''
        initial_solution[2][3][1] = ''
        initial_solution[2][3][2] = 'c5'

        initial_solution[3][0][0] = 'c8'
        initial_solution[3][0][1] = 'c6'
        initial_solution[3][0][2] = ''

        initial_solution[3][1][0] = 'c7'
        initial_solution[3][1][1] = 'c9'
        initial_solution[3][1][2] = ''

        initial_solution[3][2][0] = 'c3'
        initial_solution[3][2][1] = ''
        initial_solution[3][2][2] = ''

        initial_solution[3][3][0] = 'c2'
        initial_solution[3][3][1] = 'c3'
        initial_solution[3][3][2] = ''
        # initial_solution = maxSAT.solve(schedule, self.instance_data, unscheduled_lectures)
        print("Initial Solution: ", initial_solution)
        return initial_solution, Uc



























