import xlwt
from datetime import datetime
from configs import configs
from parameters import parameters
from alns import alns
import random

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
IL = [6000, 8000, 12000, 20000]

# ------------ w1 parameter tuning ------------- #

configs.instance_name = "comp01.ectt"

wb = xlwt.Workbook()

ws = wb.add_sheet('IL_' + configs.instance_name)

ws.write(0, 0, "W1")
ws.write(0, 1, "Cost")
ws.write(0, 2, "Time")

row = 0
for param_value in IL:

    print("\nIL: ", param_value)

    parameters.iteration_limit = param_value

    print('INSTANCE' + configs.instance_name +'\n')

    for i in range(0, 10):
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

    wb.save('experiments_IL' + configs.instance_name + '.xls')

