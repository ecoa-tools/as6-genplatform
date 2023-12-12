# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
Component Implementation comparaison functions
"""

from ecoa.utilities.logs import warning
from .utils_comparator import compare_set, compare_ordered_list, compare_parameters_list

def _list_to_set_name(mylist):
    """From a list of object (with a 'name' attribute), return set of names
    """
    return set([o.name for o in mylist])

def _compare_mod_type(model_1_name, model_2_name,
                      comp_name, mtype_1, mtype_2):
    """Compare 2 modules types
    """
    error_str = "in component '%s', in module type '%s'"%\
                 (comp_name, mtype_1.name)

    # user context and warm context
    if mtype_1.user_context != mtype_2.user_context or\
       mtype_1.warm_start_context != mtype_2.warm_start_context:
        warning("[DIFF] %s, different conxtext setting"%error_str)

    # operations
    intersection_op = compare_set(error_str+\
                                  ", following operations are not defined",
                                  model_1_name,
                                  model_2_name,
                                  set(mtype_1.operations.keys()),
                                  set(mtype_2.operations.keys()))

    for op_name in intersection_op:
        op_1 = mtype_1.operations[op_name]
        op_2 = mtype_2.operations[op_name]

        # type
        if op_1.type != op_2.type:
            warning(error_str+", in operation '%s', different type (%s!=%s)"%
                    (op_name, op_1.type, op_2.type))

        # params
        compare_parameters_list(error_str+", in operation '%s', "%op_name,
                                model_1_name,
                                model_2_name,
                                op_1.params,
                                op_2.params)

    # pinfo
    # TODO: Not necessary ?

    # properties
    # TODO: Not necessary ?

def _compare_mod_impl(comp_name, mod_1, mod_2):
    """Compare 2 module implementations"""
    # type
    if mod_1.type != mod_2.type:
        warning(("[DIFF] in component '%s', in module impl, "+
                 "type different (%s != %s)") %
                (comp_name, mod_1.name, mod_1.type, mod_2.type))

    # language
    if mod_1.language != mod_2.language:
        warning(("[DIFF] in component '%s', in module impl, "+
                 "language different (%s != %s)") %
                (comp_name, mod_1.name, mod_1.language, mod_2.language))

def _compare_mod_inst(comp_name, mod_name, mod_1, mod_2):
    """Compare 2 module instances"""
    #implementation
    if mod_1.implementation != mod_2.implementation:
        warning(("[DIFF] in component '%s', in module instance, "+
                 "implementations different (%s != %s)") %
                (comp_name, mod_1.name, mod_1.implementation, mod_2.implemention))

    # Properties
    # TODO: Not necessary ?

def _compare_dyn_trig(model_1_name, model_2_name,
                      comp_name, dyn_1, dyn_2):
    """Compare 2 dynamic trigger instances"""
    error_str = "in component '%s', in dynamic trigger '%s', " %\
        (comp_name, dyn_1.name)

    # event size. number of event that dynamic trigger can handle
    if dyn_1.size != dyn_2.size:
        warning("[DIFF] %s, nb of handle event different: %s!=%s"%
                (error_str, dyn_1.size, dyn_2.size))

    # parameters
    intersection = compare_ordered_list(error_str+\
                                        "following parameters are not defined",
                                        error_str+"parameters",
                                        model_1_name,
                                        model_2_name,
                                        [p.name for p in dyn_1.params],
                                        [p.name for p in dyn_2.params])

    # same named parameters must be equals
    for param_name in intersection:
        param_1 = next(p for p in dyn_1.params if p.name == param_name)
        param_2 = next(p for p in dyn_2.params if p.name == param_name)

        if param_1.type != param_2.type or\
           param_1.direction != param_2.direction:
            warning(("[DIFF] %s parameter '%s': different type or direction "+
                    "((%s, %s) != (%s, %s))") %
                    (error_str, param_name,
                     param_1.type, param_1.direction,
                     param_2.type, param_2.direction))


def comp_impl_comparator(model_1_name, model_2_name, comp_impl_1, comp_impl_2):
    """Compare 2 component implementations"""
    # module types
    intersection_mod_t = compare_set("in component %s, "%comp_impl_1.name +
                                     "following module types are not defined",
                                     model_1_name,
                                     model_2_name,
                                     set(comp_impl_1.module_types.keys()),
                                     set(comp_impl_2.module_types.keys()))
    for mod_name in intersection_mod_t:
        _compare_mod_type(model_1_name,
                          model_2_name,
                          comp_impl_1.name,
                          comp_impl_1.module_types[mod_name],
                          comp_impl_2.module_types[mod_name])


    # module implementations
    intersection_mod_impl = compare_set("in component %s, "%comp_impl_1.name +
                                     "following module impl are not defined",
                                     model_1_name,
                                     model_2_name,
                                     set(comp_impl_1.module_implementations.keys()),
                                     set(comp_impl_2.module_implementations.keys()))
    for mod_name in intersection_mod_impl:
        _compare_mod_impl(comp_impl_1.name,
                          comp_impl_1.module_implementations[mod_name],
                          comp_impl_2.module_implementations[mod_name])

    # module instances
    intersection_mod_inst = compare_set("in component %s, "%comp_impl_1.name +
                                "following module inst are not defined",
                                model_1_name,
                                model_2_name,
                                _list_to_set_name(comp_impl_1.module_instances),
                                _list_to_set_name(comp_impl_2.module_instances))
    for mod_name in intersection_mod_inst:
        _compare_mod_inst(comp_impl_1.name,
                          mod_name,
                          comp_impl_1.get_instance(mod_name),
                          comp_impl_2.get_instance(mod_name))


    # trigger instances
    compare_set("in component %s, "%comp_impl_1.name +
                "following trigger inst are not defined",
                model_1_name,
                model_2_name,
                _list_to_set_name(comp_impl_1.trigger_instances),
                _list_to_set_name(comp_impl_2.trigger_instances))


    # dynamic triggers instances
    intersection_dyn_t_inst = compare_set("in component %s, "%comp_impl_1.name +
                        "following dynamic trigger inst are not defined",
                        model_1_name,
                        model_2_name,
                        _list_to_set_name(comp_impl_1.dynamic_trigger_instances),
                        _list_to_set_name(comp_impl_2.dynamic_trigger_instances))
    for dyn_trig_name in intersection_dyn_t_inst:
        _compare_dyn_trig(model_1_name,
                          model_2_name,
                          comp_impl_1.name,
                          comp_impl_1.get_instance(dyn_trig_name),
                          comp_impl_2.get_instance(dyn_trig_name))

    # links
    # TODO
