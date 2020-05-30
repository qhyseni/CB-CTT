
from alns_destroy_operators import destroy_operators
from alns_repair_operators import repair_operators
from maxSAT_repair_operator import maxSAT
from priority_rules import priority_rules
from Experiments.statistics import statistics

class operators_lookup:

    # Initial weights of removal operators set to 1
    removal_operators_weights = {
        "0": 1,
        "1": 1,
        "2": 1,
        "3": 1,
        "4": 1,
        "5": 1
        # "6": 1
    }

    # array of removal operators methods with tuple of position (key) and value (method name)
    removal_operators = {
        0: destroy_operators.worst_courses_removal,
        1: destroy_operators.worst_curricula_removal,
        2: destroy_operators.random_lecture_removal,
        3: destroy_operators.random_dayperiod_removal,
        4: destroy_operators.random_roomday_removal,
        5: destroy_operators.random_teacher_removal
        # 6: destroy_operators.restricted_roomcourse_removal
    }

    # Initial weights of repair operators set to 1
    repair_operators_weights = {
        "0": 1,
        "1": 1}

    # array of repair operators methods with tuple of position (key) and value (method name)
    repair_operators = {
        0: repair_operators.two_stage_repair_operator,
        1: maxSAT.solve
    }

    # Initial weights of lecture-room assignment operators set to 1
    lecture_period_operators_weights = {
        "0": 1,
        "1": 1}

    # array of lecture-period operators methods with tuple of position (key) and value (method name)
    lecture_period_operators = {
        0: "best",
        1: "mean"
    }

    # Initial weights of lecture-room assignment operators set to 1
    lecture_room_operators_weights = {
        "0": 1,
        "1": 1}

    # array of lecture-room operators methods with tuple of position (key) and value (method name)
    lecture_room_operators = {
        0: "greatest",
        1: "match"
    }

    # Initial weights of lecture-room assignment operators set to 1
    priority_rules_weights = {
        "0": 1,
        "1": 1,
        "2": 1}

    # array of priority rule methods with tuple of position (key) and value (method name)
    priority_rules = {
        0: priority_rules.saturation_degree_order,
        1: priority_rules.largest_degree_order,
        2: priority_rules.random_order
    }