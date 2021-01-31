import random
from random import randrange

class ga_mutate_operators:

    ###################### Repair operators #############################################

    # init method or constructor
    def __init__(self):
        print()

    def swap_rooms_mutation(instance_data, best_member, mutation_rate):

        counter = mutation_rate
        while counter > 0:

            rand_day = randrange(instance_data.days)
            rand_period = randrange(instance_data.periods_per_day)

            rand_room1 = random.choice([i for i in range(instance_data.rooms_count)])
            rand_room2 = random.choice([i for i in range(instance_data.rooms_count) if i != rand_room1])

            temp = best_member[rand_day][rand_period][rand_room1]
            best_member[rand_day][rand_period][rand_room1] = best_member[rand_day][rand_period][rand_room2]
            best_member[rand_day][rand_period][rand_room2] = temp

            counter -= 1

        return best_member

    def swap_periods_mutation(instance_data, best_member, mutation_rate):

        counter = mutation_rate
        while counter > 0:

            # choose one random day
            rand_day = randrange(instance_data.days)

            # choose two different (since they belong to the same day) random periods
            rand_period1 = random.choice([i for i in range(instance_data.periods_per_day)])
            rand_period2 = random.choice([i for i in range(instance_data.periods_per_day) if i != rand_period1])

            # we need to make sure that all lcetures of one are period ar feasibile in the other period if swapped
            if not ga_mutate_operators.is_swap_feasible(instance_data, best_member, rand_day, rand_period1, rand_day, rand_period2):
                continue

            best_member = ga_mutate_operators.swap_days_periods(instance_data, best_member, rand_day, rand_period1, rand_day, rand_period2)

            counter -= 1

        return best_member
    
    def swap_days_mutation(instance_data, best_member, mutation_rate):

        counter = mutation_rate
        while counter > 0:

            # choose one random period
            rand_period = randrange(instance_data.periods_per_day)

            # choose two different random days
            rand_day1 = random.choice([i for i in range(instance_data.days)])
            rand_day2 = random.choice([i for i in range(instance_data.days) if i != rand_day1])

            # we need to make sure that all lcetures of one are period ar feasibile in the other period if swapped
            if not ga_mutate_operators.is_swap_feasible(instance_data, best_member, rand_day1, rand_period, rand_day2, rand_period):
                continue

            best_member = ga_mutate_operators.swap_days_periods(instance_data, best_member, rand_day1, rand_period, rand_day2, rand_period)

            counter -= 1

        return best_member

    def is_swap_feasible(instance_data, best_member, d1, p1, d2, p2):

        # we need to make sure that all lcetures of one are period ar feasibile in the other period if swapped
        for r in range(instance_data.rooms_count):
            # check if lecture in current room from the first period is not constrained in the second one
            scheduled_lecture = best_member[d1][p1][r]
            if scheduled_lecture != -1 and [d2, p2] in instance_data.courses_periods_constraints[scheduled_lecture]:
                return False

            # check if lecture in current room from the second period is not constrained in the first one
            scheduled_lecture = best_member[d2][p2][r]
            if scheduled_lecture != -1 and [d1, p1] in instance_data.courses_periods_constraints[scheduled_lecture]:
                return False

        return True

    def swap_days_periods(instance_data, best_member, d1, p1, d2, p2):

        for r in range(instance_data.rooms_count):
            temp = best_member[d1][p1][r]
            best_member[d1][p1][r] = best_member[d2][p2][r]
            best_member[d2][p2][r] = temp

        return best_member
    ###################### End of Repair operators ############################################