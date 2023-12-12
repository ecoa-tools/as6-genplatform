# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
Comparaison functions of Component Types
"""

from ecoa.utilities.logs import warning
from .utils_comparator import compare_set

def _service_comparator(model_1_name, model_2_name, comp_name,
                              list_1, list_2, is_reference):
    """Compare 2list of services(or references) of 2 component types"""
    serv_names_1 = set([serv.name for serv in list_1])
    serv_names_2 = set([serv.name for serv in list_2])

    serv_str = "reference" if is_reference else "service"
    error_str="in comp type '%s', following %ss are not defined"%(comp_name, serv_str)

    # find missing service in both size:
    intersection_serv = compare_set(error_str,
                model_1_name,
                model_2_name,
                serv_names_1,
                serv_names_2)

    # for service defined in both component: check syntax consistency
    for serv_name in intersection_serv:
        serv_1 = next(serv for serv in list_1 if serv.name == serv_name)
        serv_2 = next(serv for serv in list_2 if serv.name == serv_name)
        if serv_1.syntax != serv_2.syntax:
            warning(("[DIFF] in comp type '%s', %s '%s', "+\
                 " syntax are different (%s != %s)") %
                    (comp_name, serv_str, serv_name,
                     serv_1.syntax, serv_2.syntax))


def comp_type_comparator(model_1_name, model_2_name, comp_type_1, comp_type_2):
    """Compare 2 Component Types"""
    # service
    _service_comparator(model_1_name, model_2_name, comp_type_1.name,
                       comp_type_1.services, comp_type_2.services, False)
    # reference
    _service_comparator(model_1_name, model_2_name, comp_type_1.name,
                       comp_type_1.references, comp_type_2.references, True)

    # property
    intersection_prop = compare_set("in comp type '%s', "%(comp_type_1.name)+
                                    "following properties are not defined",
                                    model_1_name,
                                    model_2_name,
                                    set(comp_type_1.properties.keys()),
                                    set(comp_type_2.properties.keys()))
    ## For properties defined in both component: check type consistency
    for prop_name in intersection_prop:
        if comp_type_1.properties[prop_name].type != \
           comp_type_2.properties[prop_name].type:
            warning("[DIFF] in comp type '%s', properties '%s' are different"%
                    (comp_type_1.name, prop_name))
