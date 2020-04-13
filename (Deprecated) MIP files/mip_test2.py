from itertools import product
from sys import stdout as out
from mip import Model, xsum, minimize, BINARY, INTEGER



c_teachers = [0,0,2,3,4,5,6,7,8,9]
c_lectures = [3,3,5,5,2,3,3,2,2,5]
c_min_days = [3,2,4,4,1,3,3,2,1,2]
c_students = [30,42,40,18,30,30,15,25,25, 30]
c_double_lectures = [1,0,1,1,0,0,1,1,1,1]


c_unavailability = [
                    [0,0,0,0],
                    [0,0,0,0],
                    [2,2,0,0],
                    [0,0,2,2],
                    [1,1,1,1]
                    ]

curricula = ['Cur1','Cur2']
cu_courses = [[0, 1, 2],[2, 3], [4,5,6], [4,7],[8,9],[0,6,9]]

teachers = ['t01','t02','t03','t04','t05','t06','t07','t08','t09','t10']

rooms = ['rA', 'rB', 'rC']
r_capacity = [32,50,40]


# set of periods
P = 3
# set of days
D = 5
# set of rooms
R = 3
# set of courses
C = 10
# set of curricula
CU = 6
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

print('\nx_cdpr:',x_cdpr[0][0][0][0].x)
print('\nx_cdpr:',x_cdpr[1][1][0][0].x)
print('\nx_cdpr:',x_cdpr[2][2][0][0].x)
print('\nx_cdpr:',x_cdpr[3][3][0][0].x)


v_cupd = [[[m.add_var('v({},{},{})'.format(cu,p,d),var_type=BINARY)
            for d in range(D)] for p in range(P)] for cu in range(CU)]
print('\nv_cupd:',v_cupd)
y_cr = [[m.add_var('y({},{})'.format(c,r),var_type=BINARY)
         for r in range(R)] for c in range(C)]
print('\ny_cr:',y_cr)
z_cd = [[m.add_var('z({},{})'.format(c,d),var_type=BINARY)
         for d in range(D)] for c in range(C)]
print('\nz_cd:',z_cd)
w_c = [m.add_var('w({})'.format(c), lb=0, ub= c_min_days[c], var_type=INTEGER)
       for c in range(C)]
print('\nw_c:',w_c)

# objective function

# !!!!!!!!!!!!!!! gabimi: c_students[c] - r_capacity[r] !!!!!!!!!!!

m.objective = minimize(
    xsum(x_cdpr[c][d][p][r] * (1) * p_CAP
         for c in range(C) for d in range(D) for p in range(P) for r in range(R))
    + xsum((xsum(y_cr[c][r] for r in range(R)) - 1) * p_STAB
           for c in range(C))
    + xsum(w_c[c] * p_DAYS for c in range(C))
    + xsum(v_cupd[cu][p][d] * p_COMP
           for cu in range(CU) for p in range(P) for d in range(D))

)

# hard constraints

# fixed courses
# m += x_cdpr[2][0][0][0] == 1
# m += x_cdpr[9][0][0][1] == 1
# m += x_cdpr[2][2][0][0] == 1
# m += x_cdpr[3][3][0][0] == 1


for c in range(C):
    m += xsum(x_cdpr[c][d][p][r]
              for d in range(D) for p in range(P) for r in range(R)) == c_lectures[c]

for p,d,t in product(range(P), range(D), range(T)):
    m += xsum(x_cdpr[c][d][p][r]
              for r in range(R) for c in [i for i, q in enumerate(c_teachers) if q == t]) <= 1

for p,d,cu in product(range(P), range(D), range(CU)):
    m += xsum(x_cdpr[c][d][p][r]
              for r in range(R) for c in cu_courses[cu]) <= 1

for r, p, d in product(range(R), range(P), range(D)):
    m += xsum(x_cdpr[c][d][p][r]
              for c in range(C)) <= 1

# soft constraints

for c,d in product(range(C), range(D)):
    m += xsum(x_cdpr[c][d][p][r]
              for r in range(R) for p in range(P)) - z_cd[c][d] >= 0

for c in range(C):
    m += xsum(z_cd[c][d]
              for d in range(D)) + w_c[c] >= c_min_days[c]

for cu,p,d in product(range(CU), range(P), range(D)):
    temp_xcdpr = xsum(x_cdpr[c][d][p][r]
              for c in cu_courses[cu] for r in range(R))
    if p != 0:
        temp_xcdpr = temp_xcdpr - xsum(x_cdpr[c][d][p-1][r]
            for r in range(R) for c in cu_courses[cu])
    if p != P-1:
        temp_xcdpr = temp_xcdpr - xsum(x_cdpr[c][d][p+1][r]
              for r in range(R) for c in cu_courses[cu])
    m += temp_xcdpr - v_cupd[cu][p][d] <= 0

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

else:
    print("Infeasible")