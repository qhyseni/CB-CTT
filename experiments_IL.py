import xlwt
from datetime import datetime
from Experiments.configs import configs
from Experiments.parameters import parameters
from _alns import alns
import random
from Experiments.statistics import statistics

import time
# instances = [
#             'comp01', 'comp02',
#             'comp03', 'comp04', 'comp05',
#              'comp06', 'comp07', 'comp08', 'comp09','comp10',
#              'comp11', 'comp12','comp13', 'comp14', 'comp15',
#              'comp16', 'comp17', 'comp18', 'comp19', 'comp20','comp21']
#

instances = ['comp01']
# IL = [50, 100, 500, 1000, 2000, 4000, 6000, 8000, 10000, 12000]
IL = [8000]
# IL = [100, 500, 1000, 5000, 8000, 10000]

# ------------ w1 parameter tuning ------------- #

configs.instance_name = "comp01.ectt"

wb = xlwt.Workbook()

ws = wb.add_sheet('IL_' + configs.instance_name)

ws.write(0, 0, "W1")
ws.write(0, 1, "Cost")
ws.write(0, 2, "Time")
ws.write(0, 3, "Time")
ws.write(0, 4, "Time Best")
ws.write(0, 5, "Iterations")
ws.write(0, 6, "Iteration Best")
ws.write(0, 7, "DO_WCR")
ws.write(0, 8, "DO_WQR")
ws.write(0, 9, "DO_RLR")
ws.write(0, 10, "DO_RTR")
ws.write(0, 11, "DO_DPR")
ws.write(0, 12, "DO_RDR")
ws.write(0, 13, "DO_RCR")
ws.write(0, 14, "RO_2STG")
ws.write(0, 15, "RO_2STGB")
ws.write(0, 16, "RO_2STGME")
ws.write(0, 17, "RO_2STGG")
ws.write(0, 18, "RO_2STGMA")
ws.write(0, 19, "RO_2STGBTR")
ws.write(0, 20, "RO_MAXSAT")
ws.write(0, 21, "PR_SD")
ws.write(0, 22, "PR_LD")
ws.write(0, 23, "PR_RAND")
ws.write(0, 24, "Infeasible")
ws.write(0, 25, "Accepted")
ws.write(0, 26, "Better")
ws.write(0, 27, "Worse")
ws.write(0, 28, "GB")
ws.write(0, 29, "Reheats")
ws.write(0, 30, "UnSAT")

row = 0
for param_value in IL:

    print("\nIL: ", param_value)

    parameters.iteration_limit = param_value

    print('INSTANCE' + configs.instance_name +'\n')

    for i in range(1):
        row = row + 1
        print(i)
        alns_instance = alns()
        start_time = time.time()
        schedule, cost = alns_instance.execute()
        end_time = time.time()
        exec_time = end_time - start_time

        ws.write(row, 0, param_value)
        ws.write(row, 1, cost)
        ws.write(row, 2, exec_time)
        ws.write(row, 3, statistics.time)
        ws.write(row, 4, statistics.time_best)
        ws.write(row, 5, statistics.iterations)
        ws.write(row, 6, statistics.iteration_best)
        ws.write(row, 7, statistics.worst_courses_removal_count)
        ws.write(row, 8, statistics.worst_curricula_removal_count)
        ws.write(row, 9, statistics.random_lecture_removal_count)
        ws.write(row, 10, statistics.random_teacher_removal_count)
        ws.write(row, 11, statistics.random_dp_removal_count)
        ws.write(row, 12, statistics.random_rd_removal_count)
        ws.write(row, 13, statistics.restricted_rc_removal_count)
        ws.write(row, 14, statistics.two_stage_count)
        ws.write(row, 15, statistics.two_stage_best_count)
        ws.write(row, 16, statistics.two_stage_mean_count)
        ws.write(row, 17, statistics.two_stage_greatest_count)
        ws.write(row, 18, statistics.two_stage_match_count)
        ws.write(row, 19, statistics.backtrack_count)
        ws.write(row, 20, statistics.maxsat_count)
        ws.write(row, 21, statistics.saturation_degree_count)
        ws.write(row, 22, statistics.largest_degree_count)
        ws.write(row, 23, statistics.random_order_count)
        ws.write(row, 24, statistics.infeasible_count)
        ws.write(row, 25, statistics.accepted_count)
        ws.write(row, 26, statistics.better_count)
        ws.write(row, 27, statistics.worse_count)
        ws.write(row, 28, statistics.global_best_counts)
        ws.write(row, 29, statistics.reheats_count)
        ws.write(row, 30, statistics.unsat)

    wb.save('experiments_IL' + configs.instance_name + '.xls')

