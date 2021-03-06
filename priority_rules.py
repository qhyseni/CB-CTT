
from random import shuffle
from alns_repair_operators import repair_operators
from Experiments.statistics import statistics

class priority_rules:

    def saturation_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        print("Saturation Degree Priority Rule")
        # The Saturation Degree rule arranges courses in ascending order
        # with respect to their number of available periods for scheduling
        c_periods_count = {}
        for c in unscheduled_courses:
            course = next(
                (i for i in instance_data.courses if i.id == c), None)
            c_available_periods = repair_operators.check_periods_available(schedule, instance_data, course, period_lecture_assignments)
            c_periods_count[c] = len(c_available_periods)

        c_sorted = {k: v for k, v in sorted(c_periods_count.items(), key = lambda item:item[1])}

        return list(c_sorted.keys())

    def largest_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        print("Largest Degree Priority Rule")
        # The Largest Degree rule prioritizes courses with the largest number of conflicts with other courses
        c_conflicts_count = {}
        for c in unscheduled_courses:
            c_conflicts_count[c] = repair_operators.check_course_conflicts(schedule, instance_data, c)

        c_sorted = {k: v for k, v in sorted(c_conflicts_count.items(), key = lambda item:item[1], reverse=True)}

        return list(c_sorted.keys())

    def random_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        print("Random Order Priority Rule")
        # The Random rule orders courses randomly
        shuffle(unscheduled_courses)
        return unscheduled_courses

