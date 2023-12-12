# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
Usefull comparaison functions
"""

from ecoa.utilities.logs import warning

def compare_set(error_str, model_1_name, model_2_name, set_1, set_2):
    """Compare 2 set of name.

    Attributes:
        error_str (str): error message to print
        module_1_name (str): name of model 1
        module_2_name (str): name of model 2
        set_1         (set): set of name in model_1
        set_2         (set): set of name in model_2

    Return:
        (set): intersection of these set
    """
    missing_1 = set_2 - set_1
    missing_2 = set_1 - set_2
    intersection = set_1.intersection(set_2)

    if len(missing_1) > 0:
        warning("[DIFF] in model '%s', %s: %s" %
                (model_1_name, error_str, missing_1))

    if len(missing_2) > 0:
        warning("[DIFF] in model '%s', %s: %s" %
                (model_2_name, error_str, missing_2))

    return intersection

def compare_ordered_list(error_str, order_error_str,
                         model_1_name, model_2_name, list_1, list_2):
    """Compare 2 list of name. Order is also checked

    Attributes:
        error_str (str): error message to print
        module_1_name (str): name of model 1
        module_2_name (str): name of model 2
        list_1       (list): list of name in model_1
        list_2       (list): list of name in model_2

    Return:
        (set): intersection of these list
    """

    # find missing element
    intersection = compare_set(error_str, model_1_name, model_2_name,
                               set(list_1), set(list_2))

    # check order (if no error before)
    if len(intersection) == len(list_1):
        for name_1, name_2 in zip(list_1, list_2):
            if name_1 != name_2:
                warning("[DIFF] %s: order don't match"%order_error_str)

    return intersection

def compare_parameters_list(error_str, model_1_name, model_2_name,
                            params_list_1, params_list_2):
    """Compare 2 list of :class:`.Parameter`.
    Find missing, check order, check type and direction

    Attributes:
        error_str      (str): error message to print
        module_1_name  (str): name of model 1
        module_2_name  (str): name of model 2
        params_list_1 (list): list of :class:`.Parameter` in model_1
        params_list_2 (list): list of :class:`.Parameter` in model_2
    """

    # missing parameters. invalid order
    intersection_params = compare_ordered_list(error_str +\
                         "following parameters are not defined",
                         error_str+ " parameters",
                         model_1_name,
                         model_2_name,
                         [op.name for op in params_list_1],
                         [op.name for op in params_list_2])

    # parameter must be equals
    for param_name in intersection_params:
        param_1 = next(p for p in params_list_1 if p.name == param_name)
        param_2 = next(p for p in params_list_2 if p.name == param_name)

        if param_1.type != param_2.type or\
           param_1.direction != param_2.direction:
            warning(("[DIFF] %s parameter '%s': different type or direction "+
                    "((%s, %s) != (%s, %s))") %
                    (error_str, param_name,
                     param_1.type, param_1.direction,
                     param_2.type, param_2.direction))
