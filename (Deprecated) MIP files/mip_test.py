from itertools import product
from sys import stdout as out
from mip import Model, xsum, minimize, BINARY, INTEGER

# Name: Toy
# Courses: 4
# Rooms: 3
# Days: 5
# Periods_per_day: 4
# Curricula: 2
# Min_Max_Daily_Lectures: 2 3
# UnavailabilityConstraints: 8
# RoomConstraints: 3
#
# COURSES:
# SceCosC Ocra 3 3 30 1
# ArcTec Indaco 3 2 42 0
# TecCos Rosa 5 4 40 1
# Geotec Scarlatti 5 4 18 1
#
# ROOMS:
# rA 32 1
# rB 50 0
# rC 40 0
#
# CURRICULA:
# Cur1 3 SceCosC ArcTec TecCos
# Cur2 2 TecCos Geotec
#
# UNAVAILABILITY_CONSTRAINTS:
# TecCos 2 0
# TecCos 2 1
# TecCos 3 2
# TecCos 3 3
# ArcTec 4 0
# ArcTec 4 1
# ArcTec 4 2
# ArcTec 4 3
#
# ROOM_CONSTRAINTS:
# SceCosC rA
# Geotec rB
# TecCos rC

courses = ['SceCosC', 'ArcTec', 'TecCos', 'Geotec']

c_teachers = ['Ocra', 'Indaco', 'Rosa', 'Scarlatti']
c_lectures = [3,3,5,5]
c_min_days = [3,2,4,4]
c_students = [30,42,40,18]
c_double_lectures = [1,0,1,1]


c_unavailability = [
                    [0,0,0,0],
                    [0,0,0,0],
                    [2,2,0,0],
                    [0,0,2,2],
                    [1,1,1,1]
                    ]

curricula = ['Cur1','Cur2']
cu_courses = [[0, 1, 2],[2, 3]]

teachers = ['t01','t02','t03','t04']

rooms = ['rA', 'rB', 'rC']
r_capacity = [32,50,40]

# set of periods
P = 4
# set of days
D = 5
# set of rooms
R = 3
# set of courses
C = 4
# set of curricula
CU = 2
# techers
T = len(teachers)

p_CAP = 1
p_STAB = 1
p_DAYS = 1
p_COMP = 1
#
# ma = [[0,1,2],[3,4,5],[6,7,8],[6,7,8]]
# meow = 1 - (xsum(ma[i][j] for i in range(2) for j in range(3)) \
#        + xsum(ma[i][j] for i in range(2,4) for j in range(3)))

m = Model("cbctt")

x_cdpr = [[[[m.add_var('x({},{},{},{})'.format(c,d,p,r),var_type=BINARY)
             for r in range(R)] for p in range(P)] for d in range(D)] for c in range(C)]

print('\nx_cdpr:',x_cdpr[3][4][3][2])

v_cupd = [[[m.add_var('v({},{},{})'.format(cu,p,d),var_type=BINARY)
            for d in range(D)] for p in range(P)] for cu in range(CU)]
print('\nv_cupd:',v_cupd)
y_cr = [[m.add_var('y({},{})'.format(c,r),var_type=BINARY)
         for r in range(R)] for c in range(C)]
print('\ny_cr:',y_cr)
z_cd = [[m.add_var('y({},{})'.format(c,d),var_type=BINARY)
         for d in range(D)] for c in range(C)]
print('\nz_cd:',z_cd)
w_c = [m.add_var('w({}'.format(c), lb=0, ub= c_min_days[c])
       for c in range(C)]
print('\nw_c:',w_c)

# objective function

# !!!!!!!!!!!!!!! gabimi: c_students[c] - r_capacity[r] !!!!!!!!!!!

m.objective = minimize(
    xsum(x_cdpr[c][d][p][r] * (1) * p_CAP
         for c in range(C) for d in range(D) for p in range(P) for r in range(R))
    + xsum((xsum(y_cr[c][r] for c in range(C) for r in range(R)) - 1) * p_STAB
           for c in range(C))
    + xsum(w_c[c] * p_DAYS for c in range(C))
    + xsum(v_cupd[cu][p][d] * p_COMP
           for cu in range(CU) for p in range(P) for d in range(D))

)

# hard constraints
for c in range(C):
    m += xsum(x_cdpr[c][d][p][r]
              for d in range(D) for p in range(P) for r in range(R)) == c_lectures[c]

for c,p,d,r in product(range(C), range(P), range(D), range(T)):
    m += xsum(x_cdpr[c][d][p][r]
              for r in range(R)) <= 1

for p,d,cu in product(range(P), range(D), range(CU)):
    m += xsum(x_cdpr[c][d][p][r]
              for r in range(R) for c in range(C)) <= 1

for r, p, d in product(range(R), range(P), range(D)):
    m += xsum(x_cdpr[c][d][p][r]
              for c in range(C)) <= 1

# soft constraints

for c,d in product(range(C), range(D)):
    m += xsum(x_cdpr[c][d][p][r]
              for r in range(R) for p in range(P)) - z_cd[c][d] >= 0

for c in range(C):
    m += xsum(z_cd[c][d]
              for d in range(D)) + w_c[c] >= 0

for cu,p,d in product(range(CU), range(P), range(D)):
    temp_res = xsum(x_cdpr[c][d][p][r]
              for c in cu_courses[cu] for r in range(R))
    if p != 0:
        temp_res = temp_res - xsum(x_cdpr[c][d][p-1][r]
              for c in cu_courses[cu] for r in range(R))
    if p != P-1:
        temp_res = temp_res - xsum(x_cdpr[c][d][p+1][r]
              for c in cu_courses[cu] for r in range(R))
    m += temp_res - v_cupd[cu][p][d] <= 0

for c,r in product(range(C),range(R)):
    m += xsum(x_cdpr[c][d][p][r]
              for d in range(D) for p in range(P)) - 100 * y_cr[c][r] >= 0

m.optimize()

# if m.num_solutions:
#     for s in range(m.num_solutions):
#         print(s)

if m.num_solutions:
    for c,d,p,r in product(range(C),range(D),range(P),range(R)):
        if x_cdpr[c][d][p][r].x > 0.99:
            print('Is scheduled: {}  --  [{}] -- [{}][{}][{}]'.format(x_cdpr[c][d][p][r].x > 0.99 , c,d,p,r, ))

print('DONE =)')