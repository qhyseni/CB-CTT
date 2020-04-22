
from random import shuffle
from alns_repair_operators import repair_operators

class priority_rules:

    def saturation_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        # The Saturation Degree rule arranges courses in ascending order
        # with respect to their number of available periods for scheduling
        # print('saturation degree')
        c_periods_count = {}
        for c in unscheduled_courses:
            course = next(
                (i for i in instance_data.courses if i.id == c), None)
            c_available_periods = repair_operators.check_periods_available(schedule, instance_data, course, period_lecture_assignments)
            c_periods_count[c] = len(c_available_periods)

        c_sorted = {k: v for k, v in sorted(c_periods_count.items(), key = lambda item:item[1])}
        # print(c_sorted)
        return list(c_sorted.keys())

    def largest_degree_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        # The Largest Degree rule prioritizes courses with the largest number of conflicts with other courses
        print('largest degree')
        c_conflicts_count = {}
        for c in unscheduled_courses:
            c_conflicts = repair_operators.check_periods_conflicts(schedule, instance_data, c)
            c_conflicts_count[c] = len(c_conflicts)

        c_sorted = {k: v for k, v in sorted(c_conflicts_count.items(), key = lambda item:item[1], reverse=True)}
        print(c_sorted)
        return list(c_sorted.keys())

    def random_order(schedule, instance_data, unscheduled_courses, period_lecture_assignments):
        # The Random rule orders courses randomly
        print('random')
        shuffle(unscheduled_courses)
        return unscheduled_courses

