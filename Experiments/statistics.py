
class statistics:

    test = 9999

    time = 0
    time_best = 0
    iterations = 0
    iteration_best = 0

    worst_courses_removal_count = 0
    worst_curricula_removal_count = 0
    random_lecture_removal_count = 0
    random_teacher_removal_count = 0
    random_dp_removal_count = 0
    random_rd_removal_count = 0
    restricted_rc_removal_count = 0

    two_stage_count = 0
    two_stage_best_count = 0
    two_stage_mean_count = 0
    two_stage_greatest_count = 0
    two_stage_match_count = 0
    backtrack_count = 0
    maxsat_count = 0

    saturation_degree_count = 0
    largest_degree_count = 0
    random_order_count = 0

    infeasible_count = 0
    accepted_count = 0
    better_count = 0
    worse_count = 0
    global_best_counts = 0
    reheats_count = 0

    def reset(self):

        statistics.test = 0

        statistics.time = 0
        statistics.time_best = 0
        statistics.iterations = 0
        statistics.iteration_best = 0

        statistics.worst_courses_removal_count = 0
        statistics.worst_curricula_removal_count = 0
        statistics.random_lecture_removal_count = 0
        statistics.random_teacher_removal_count = 0
        statistics.random_dp_removal_count = 0
        statistics.random_rd_removal_count = 0
        statistics.restricted_rc_removal_count = 0

        statistics.two_stage_count = 0
        statistics.two_stage_best_count = 0
        statistics.two_stage_mean_count = 0
        statistics.two_stage_greatest_count = 0
        statistics.two_stage_match_count = 0
        statistics.backtrack_count = 0
        statistics.maxsat_count = 0

        statistics.saturation_degree_count = 0
        statistics.largest_degree_count = 0
        statistics.random_order_count = 0

        statistics.infeasible_count = 0
        statistics.accepted_count = 0
        statistics.better_count = 0
        statistics. worse_count = 0
        statistics.global_best_counts = 0
        statistics.reheats_count = 0

    def print_statistics(self):

        print("Statistics - Time: ", statistics.time)
        print("Statistics - Time Best: ", statistics.time_best)
        print("Statistics - Iterations: ", statistics.iterations)
        print("Statistics - Iteration Best: ", statistics.iteration_best)

        print("Statistics - Destroy Operator - Worst Course Removal: ", statistics.worst_courses_removal_count)
        print("Statistics - Destroy Operator - Worst Curricula Removal: ", statistics.worst_curricula_removal_count)
        print("Statistics - Destroy Operator - Random Lecture Removal: ", statistics.random_lecture_removal_count)
        print("Statistics - Destroy Operator - Random Teacher Removal: ", statistics.random_teacher_removal_count)
        print("Statistics - Destroy Operator - Random Day/Period Removal: ", statistics.random_dp_removal_count)
        print("Statistics - Destroy Operator - Random Room/Day Removal: ", statistics.random_rd_removal_count)
        print("Statistics - Destroy Operator - Random Room/Course Removal: ", statistics.restricted_rc_removal_count)

        print("Statistics - Repair Operator - 2-Stage: ", statistics.two_stage_count)
        print("Statistics - Repair Operator - 2-Stage Best: ", statistics.two_stage_best_count)
        print("Statistics - Repair Operator - 2-Stage Mean: ", statistics.two_stage_mean_count)
        print("Statistics - Repair Operator - 2-Stage Greatest: ", statistics.two_stage_greatest_count)
        print("Statistics - Repair Operator - 2-Stage Match: ", statistics.two_stage_match_count)
        print("Statistics - Repair Operator - 2-Stage Backtracking: ", statistics.backtrack_count)

        print("Statistics - Repair Operator - Max-SAT: ", statistics.maxsat_count)

        print("Statistics - Priority Rule - Saturation Degree: ", statistics.saturation_degree_count)
        print("Statistics - Priority Rule - Largest Degree: ", statistics.largest_degree_count)
        print("Statistics - Priority Rule - Random Order: ", statistics.random_order_count)

        print("Statistics - Infeasible Solutions: ", statistics.infeasible_count)
        print("Statistics - Accepted Solutions: ", statistics.accepted_count)
        print("Statistics - Better Solutions: ", statistics.better_count)
        print("Statistics - Worse Solutions: ", statistics.worse_count)
        print("Statistics - Global Best Solutions: ", statistics.global_best_counts)
        print("Statistics - Number of Reheats: ", statistics.reheats_count)


