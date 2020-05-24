
class parameters:

    # After applying the operators to the incumbent
    # solution the corresponding scores are updated by adding a value σ depending on the solution
    # quality. This scheme encourages operators that find solutions having not been accepted before, in
    # order to direct the algorithm towards unvisited regions of the search space.
    w1 = 30  # score for new global best
    w2 = 15  # score for accepted
    w3 = 18  # score for better than current solution

    time_limit = 960 # execution time for ALNS
    iteration_limit = 500000 # iteraions limit for ALNS

    # time_limit = 25 # execution time for ALNS
    # iteration_limit = 100 # iteraions limit for ALNS

    # SA: initially accept 4% worse solution than the initial solution with a probability of 50%

    init_deterioriation = 0.04 # deterioriation SA temp
    initial_acceptance = 0.5 # acceptance SA probability

    temperature_min = 0.1 # min temperature limit

    #  The reference destroy limit nmax 0 is set to d percent of the total number of lectures.
    #  It turns out that the usage of different percentages depending on the instance size is beneficial,
    #  i.e., ds is used for small instances with less than 280 lectures and dl for larger instances.
    ds = 0.30 # Destroy limit: small instances
    dl = 0.25 # Destroy limit: large instances

    # Decreasing the destroy limit considerably increases the number of iterations within a given
    # time limit, since repairing smaller parts of a solution typically requires less computation time.
    # On the other hand, by destroying less lectures one could potentially lose diversification which
    # in turn could outweigh the gain in performance resulting from the larger number of iterations.
    # Consequently, when setting the decreasing parameter δ, this trade-off has to be taken into
    # account
    destroy_decrease_parameter = 3

    # The probability of selecting
    # very related lectures is controlled by the parameter κ.
    # If κ is large it is likely to select the most
    # related lecture. On the other hand, if κ = 1 each lecture has the same selection probability
    selection_probability = 5