import xlwt
from datetime import datetime
from configs import configs
from parameters import parameters
from alns import alns
import random


instances = [
            'comp01', 'comp02',
            'comp03', 'comp04', 'comp05',
             'comp06', 'comp07', 'comp08', 'comp09','comp10',
             'comp11', 'comp12','comp13', 'comp14', 'comp15',
             'comp16', 'comp17', 'comp18', 'comp19', 'comp20','comp21']

# ------------ w1 parameter tuning ------------- #

wb = xlwt.Workbook()

counter = 10
last_row = 0
while counter > 0:
    column = 0
    row = last_row + 1
    value = random.randrange(10, 100)
    parameters.w1 = value
    fill_first_column = True
    for instance in instances:

        row = last_row + 1
        column += 1
        configs.instance_name = instance + '.ectt'
        ws = wb.add_sheet('w1' + configs.instance_name)
        print('\nINSTANCE' + configs.instance_name +'\n')
        ws.write(row, column, configs.instance_name)
        for i in range(0, 10):
            print(i)
            row += 1
            alns_instance = alns()
            schedule, cost = alns_instance.execute()
            ws.write(row, column, cost)
            if fill_first_column:
                ws.write(row, 0, value)
        fill_first_column = False
        wb.save('experiments.xls')
    last_row = row
    counter -= 1
