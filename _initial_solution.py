from random import randint
from _two_stage_repair_operator import two_stage_repair_operator
from _ga_steady_state_repair_operator import ga_steady_state_repair_operator
from _operators_lookup import operators_lookup

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
        schedule = [[[-1 for k in range(len(self.instance_data.rooms))] for j in range(self.instance_data.periods_per_day)] for i in range(self.instance_data.days)]

        unscheduled_lectures = []
        for i in range(self.instance_data.courses_count):
            for l in range(self.instance_data.courses_lectures[i]):
                unscheduled_lectures.append(i)

        initial_solution, Uc = two_stage_repair_operator.execute(schedule, self.instance_data, unscheduled_lectures, "best", "greatest", operators_lookup.priority_rules[0])

        # ga_operator = ga_steady_state_repair_operator()
        # initial_solution = ga_operator.execute(schedule, self.instance_data, unscheduled_lectures)
        # Uc = []
        # rows = []
        #
        # for i in range(self.instance_data.days):
        #     for j in range(self.instance_data.periods_per_day):
        #         for k in range(self.instance_data.rooms_count):
        #             if initial_solution[i][j][k] != -1:
        #                 row = self.instance_data.courses_ids[initial_solution[i][j][k]] + " " + self.instance_data.rooms[
        #                     k].id + " " + str(i) + " " + str(
        #                     j) + '\n'
        #                 rows.append(row)
        #
        # # write formatted input to a file to be used by the next process (max-SAT)
        # partial_temp_filename = 'C:/Users/vlere/qq/sol'
        #
        # with open(partial_temp_filename, 'w+') as f:
        #     for row in rows:
        #         f.write(row)

        # initial_solution, Uc = maxSAT.solve(schedule, self.instance_data, unscheduled_lectures)
        print("Initial Solution: ", initial_solution)
        return initial_solution, Uc



























