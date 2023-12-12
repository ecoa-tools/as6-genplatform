# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ecoa.utilities.logs import warning
from .utils_comparator import compare_set, compare_parameters_list

def __operations_comparator(model_1_name, model_2_name, service_name,
                            operation_1, operation_2):
    """Compare 2 operations
    """
    error_main_str = "in service '%s', in operation '%s'," % \
                      (service_name, operation_1.name)
    # operation nature
    if operation_1.nature != operation_2.nature:
        warning("[DIFF] %s nature different (%s != %s)" %
                (error_main_str,
                 operation_1.nature, operation_2.nature))

    # check missing parameters, invalid order, parameters concistency
    compare_parameters_list(error_main_str,
                            model_1_name,
                            model_2_name,
                            operation_1.params,
                            operation_2.params)

def services_comparator(model_1_name, model_2_name, service_1, service_2):
    """Compare 2 Service Defintions"""
    # find missing operations
    op_names_1 = set([op.name for op in service_1.operations])
    op_names_2 = set([op.name for op in service_2.operations])

    intersection_op = compare_set("in service '%s', "%service_1.name +
                                  "following operations are not defined",
                                  model_1_name,
                                  model_2_name,
                                  op_names_1,
                                  op_names_2)

    # for operations defined in both side: check consistency
    for op_name in intersection_op:
        __operations_comparator(model_1_name,
                                model_2_name,
                                service_1.name,
                                service_1.find_operation(op_name),
                                service_2.find_operation(op_name))
