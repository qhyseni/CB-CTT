
class parameters:

    # After applying the operators to the incumbent
    # solution the corresponding scores are updated by adding a value σ depending on the solution
    # quality. This scheme encourages operators that find solutions having not been accepted before, in
    # order to direct the algorithm towards unvisited regions of the search space.
    w1 = 30  # score for new global best
    w2 = 15  # score for accepted
    w3 = 18  # score for better than current solution

    time_limit = 480 # execution time for ALNS
    iteration_limit = 500 # iteraions limit for ALNS
    # iteration_limit = 200000 # iteraions limit for ALNS

    # time_limit = 25 # execution time for ALNS
    # iteration_limit = 100 # iteraions limit for ALNS

    # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

    init_deterioriation = 0.04 # deterioriation SA temp
    initial_acceptance = 0.5 # acceptance SA probability

    temperature_min = 0.1 # min temperature limit

    #  The reference destroy limit nmax 0 is set to d percent of the total number of lectures.
    #  It turns out that the usage of different percentages depending on the instance size is beneficial,
    #  i.e., ds is used for small instances with less than 280 lectures and dl for larger instances.
    ds = 0.30 # Destroy limit: small instances 30%
    dl = 0.25 # Destroy limit: large instances 25%

    # Decreasing the destroy limit considerably increases the number of iterations within a given
    # time limit, since repairing smaller parts of a solution typically requires less computation time.
    # On the other hand, by destroying less lectures one could potentially lose diversification which
    # in turn could outweigh the gain in performance resulting from the larger number of iterations.
    # Consequently, when setting the decreasing parameter δ, this trade-off has to be taken into
    # account
    destroy_decrease = 3

    # The probability of selecting
    # very related lectures is controlled by the parameter κ.
    # If κ is large it is likely to select the most
    # related lecture. On the other hand, if κ = 1 each lecture has the same selection probability
    selection_probability = 5

    # multiply or divide unassigned penalty/cost if solution is infeasible or feasible, respectively
    adjust_unscheduled_cost = 1.001

    # reheats limit
    reheat_limit = 50
    # reheat_limit = 60000
    # always remove at least 10 lectures
    min_destroy_lectures = 10


    # GA Steady State Algorithm

    pop_size = 100
    tournament_size = 15
    mutation_rate = 10
    alternation_frequency = 10
    max_generations = 1000