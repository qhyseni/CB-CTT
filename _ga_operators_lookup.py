
from _ga_mutate_operators import ga_mutate_operators


class mutation_operators:

    # array of GA mutation operators
    operators = {
        0: ga_mutate_operators.swap_periods_mutation,
        1: ga_mutate_operators.swap_days_mutation,
        2: ga_mutate_operators.swap_rooms_mutation
    }
