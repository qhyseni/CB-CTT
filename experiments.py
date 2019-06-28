import xlwt
from datetime import datetime
from configs import configs
from parameters import parameters
from alns import alns
import random


instances = [
    # 'comp01', 'comp02', 'comp03', 'comp04', 'comp05',
    #          'comp06', 'comp07', 'comp08', 'comp09',
             'comp10',
             'comp11', 'comp12',
             # 'comp13', 'comp14', 'comp15',
             # 'comp16', 'comp17', 'comp18', 'comp19', 'comp20',
             'comp21']


# ------------ w1 parameter tuning ------------- #

wb = xlwt.Workbook()
ws = wb.add_sheet('w1')

counter = 2
row = 0
while counter > 1:
    column = 0
    value = random.randrange(10, 100)
    parameters.w1 = value
    ws.write(row, column, value)
    for instance in instances:

        configs.instance_name = instance + '.ectt'
        print('INSTANCE' + configs.instance_name +'\n')
        alns_instance = alns()
        schedule, cost = alns_instance.execute()
        column += 1
        ws.write(row, column, cost)
    counter -= 1
    row += 1

wb.save('experiments.xls')