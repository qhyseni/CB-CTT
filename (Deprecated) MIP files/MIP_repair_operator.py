from itertools import product
from sys import stdout as out
from mip import *
from Entities import course, room, curriculum, constraints
from Entities.penalty import penalty
from configs import configs

class mip_operator:

    def __init__(self, instance_data):

        self.instance_data = instance_data
        # set of periods
        self.P = int(instance_data.periods_per_day)
        # set of days
        self.D = instance_data.days
        # set of rooms
        self.R = instance_data.rooms_count
        # set of courses
        self.C = len(instance_data.courses)
        # set of curricula
        self.CU = len(instance_data.curricula)
        self.T = len(instance_data.teachers)

        penalty_instance = penalty(configs.cbctt_type)
        self.p_CAP = penalty_instance.get_room_capacity_penalty()
        self.p_STAB = penalty_instance.get_room_stability_penalty()
        self.p_DAYS = penalty_instance.get_min_wdays_penalty()
        self.p_COMP = penalty_instance.get_isolated_lectures_penalty()

    def available_courses(self,d,p):
        available = []
        for c in range(self.C):
            pc = next((i for i in self.instance_data.period_constraints if i.course == self.instance_data.courses[c].id), None)
            if pc is None:
                available.append(c)
            else:
                if not [d,p] in pc.timeslots:
                    available.append(self.instance_data.courses.index(next(i for i in self.instance_data.courses if i.id == pc.course)))

        return available

    def unavailable_slots(self, c):
        pc = next((i for i in self.instance_data.period_constraints if i.course == self.instance_data.courses[c].id), None)
        if pc is not None:
            return pc.timeslots

        return []

    def teacher_courses(self,t):
        return [self.instance_data.courses.index(cc) for cc in self.instance_data.courses if cc.teacher_id == self.instance_data.teachers[t]]

    def curriculum_courses(self,cu):
        return [self.instance_data.courses.index(cc) for cc in self.instance_data.courses if cc.id in self.instance_data.curricula[cu].courses]

    def capacity_shortage(self,c,r):
        students_capacity_diff = int(self.instance_data.courses[c].students) - int(self.instance_data.rooms[r].size)
        if students_capacity_diff > 0:
            return students_capacity_diff
        else:
            return 0


    def repair(self):
        d = 0
        p = 0
        aaa = range(self.C)
        uuu = self.unavailable_slots(2)
        ttt = self.teacher_courses(0)
        qqq = self.curriculum_courses(1)




        esa = [0,1,2,3,4,5]

        esa1 = xsum(esa[i] for i in range(len(esa))) * 3
        esa2 = xsum(esa[i] * 3 for i in range(len(esa)))

        print('esa1: ',esa1)
        print('esa2: ',esa2)


        m = Model("cbctt")
        # m = Model("cbctt", solver_name=GRB)

        print('MEOW')
        print(self.C)
        print(self.D)
        print(self.P)
        print(self.R)
        print(self.CU)

        # ####################################################################### #
        # variables #
        # ####################################################################### #



        x_cdpr = [[[[m.add_var('x({},{},{},{})'.format(c,d,p,r), var_type=BINARY)
                     for r in range(self.R)] for p in range(self.P)] for d in range(self.D)] for c in range(self.C)]
        print('\nx_cdpr:',x_cdpr)

        v_cupd = [[[m.add_var('v({},{},{})'.format(cu,p,d),var_type=BINARY)
                    for d in range(self.D)] for p in range(self.P)] for cu in range(self.CU)]
        print('\nv_cupd:',v_cupd)

        y_cr = [[m.add_var('y({},{})'.format(c,r),var_type=BINARY)
                 for r in range(self.R)] for c in range(self.C)]
        print('\ny_cr:',y_cr)

        z_cd = [[m.add_var('z({},{})'.format(c,d),var_type=BINARY)
                 for d in range(self.D)] for c in range(self.C)]
        print('\nz_cd:',z_cd)

        w_c = [m.add_var('w({})'.format(c), lb=0, var_type=INTEGER)
               for c in range(self.C)]
        print('\nw_c:',w_c)

        # objective function

        # !!!!!!!!!!!!!!! gabimi: c_students[c] - r_capacity[r] !!!!!!!!!!!

        m.objective = minimize(
            xsum(x_cdpr[c][d][p][r] * self.capacity_shortage(c,r) * self.p_CAP
                 for c in range(self.C) for d in range(self.D) for p in range(self.P) for r in range(self.R))
            + xsum((xsum(y_cr[c][r] for r in range(self.R)) - 1) * self.p_STAB
                   for c in range(self.C))
            + xsum(w_c[c] * self.p_DAYS for c in range(self.C))
            + xsum(v_cupd[cu][p][d] * self.p_COMP
                   for cu in range(self.CU) for p in range(self.P) for d in range(self.D))
        )

        # ####################################################################### #
        # hard constraints #
        # ####################################################################### #


        # fixed courses
        # m += x_cdpr[2][0][0][0] == 1
        # m += x_cdpr[9][0][0][1] == 1
        # m += x_cdpr[2][2][0][0] == 1
        # m += x_cdpr[3][3][0][0] == 1


        for c, d, p,r in product(range(self.C),range(self.D),range(self.P),range(self.R)):
            if [d,p] in self.unavailable_slots(c):
                # print('gotcha ',c,d,p)
                m += x_cdpr[c][d][p][r] == 0

        for c in range(self.C):
            m += xsum(x_cdpr[c][d][p][r]
                      for d in range(self.D) for p in range(self.P) for r in range(self.R)) == int(self.instance_data.courses[c].lectures)

        for p,d,t in product(range(self.P), range(self.D), range(self.T)):
            m += xsum(x_cdpr[c][d][p][r]
                      for r in range(self.R) for c in [ct for ct in range(self.C) if ct in self.teacher_courses(t)]) <= 1

        for p,d,cu in product(range(self.P), range(self.D), range(self.CU)):
            m += xsum(x_cdpr[c][d][p][r]
                      for r in range(self.R) for c in [ccu for ccu in range(self.C) if ccu in self.curriculum_courses(cu)]) <= 1

        for r, p, d in product(range(self.R), range(self.P), range(self.D)):
            m += xsum(x_cdpr[c][d][p][r]
                      for c in range(self.C)) <= 1


        # ####################################################################### #
        # soft constraints #
        # ####################################################################### #

        for c,d in product(range(self.C), range(self.D)):
            m += xsum(x_cdpr[c][d][p][r]
                      for r in range(self.R) for p in range(self.P)) - z_cd[c][d] >= 0

        for c in range(self.C):
            m += xsum(z_cd[c][d]
                      for d in range(self.D)) + w_c[c] >= int(self.instance_data.courses[c].min_days)

        for cu,p,d in product(range(self.CU), range(self.P), range(self.D)):
            temp_xcdpr = xsum(x_cdpr[c][d][p][r]
                              for c in [ccu for ccu in self.available_courses(d, p) if ccu in self.curriculum_courses(cu)] for r in range(self.R))
            if p != 0:
                temp_xcdpr = temp_xcdpr - xsum(x_cdpr[c][d][p-1][r]
                    for r in range(self.R) for c in [ccu for ccu in range(self.C) if ccu in self.curriculum_courses(cu)])
            if p != self.P-1:
                temp_xcdpr = temp_xcdpr - xsum(x_cdpr[c][d][p+1][r]
                      for r in range(self.R) for c in [ccu for ccu in range(self.C) if ccu in self.curriculum_courses(cu)])
            m += temp_xcdpr - v_cupd[cu][p][d] <= 0

        for c,r in product(range(self.C),range(self.R)):
            m += xsum(x_cdpr[c][d][p][r] for d in range(self.D) for p in range(self.P)) - 10000*y_cr[c][r] <= 0

        m.optimize(max_seconds=120)


        if m.num_solutions:
            for c,d,p,r in product(range(self.C),range(self.D),range(self.P),range(self.R)):
                if x_cdpr[c][d][p][r].x > 0.99:
                    print('Is scheduled: {}  --  [{}] -- [{}][{}][{}]'.format(x_cdpr[c][d][p][r].x > 0.99 , c,d,p,r ))

            print('DONE =)')

            return x_cdpr

        else:
            print("Infeasible")
            return []