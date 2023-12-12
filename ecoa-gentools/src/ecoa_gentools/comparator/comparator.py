# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ecoa.utilities.logs import warning, info
from .libraries_comparator import libraries_comparator
from .services_comparator import services_comparator
from .comp_type_comparator import comp_type_comparator
from .comp_impl_comparator import comp_impl_comparator
from .deployment_comparator import deployment_comparator
from .wires_comparator import wires_comparator
from .utils_comparator import compare_set

def models_comparator(model_1, model_2):
    """ make comparaison between 2 ECOA models.
    Differences are display as warning message

    Attributes:
        model_1 (:class:`.ECOA_Global_Config`): ECOA project
        model_2 (:class:`.ECOA_Global_Config`): ECOA project
    """
    model_1_name = model_1.platform_config_file
    model_2_name = model_2.platform_config_file

    # libraries
    info("[DIFF] ======== Compare librarie")
    intersection_lib = compare_set("following libraries are not defined",
                                   model_1_name,
                                   model_2_name,
                                   set(model_1.libraries.keys()),
                                   set(model_2.libraries.keys()))

    for lib_name in intersection_lib:
        info("[DIFF] == Process on library "+lib_name)
        libraries_comparator(model_1_name,
                             model_2_name,
                             model_1.libraries[lib_name][0],
                             model_2.libraries[lib_name][0])

    # services
    info("[DIFF] ======== Compare services")
    intersection_serv = compare_set("following services are not defined",
                                    model_1_name,
                                    model_2_name,
                                    set(model_1.service_definitions.keys()),
                                    set(model_2.service_definitions.keys()))

    for service_name in intersection_serv:
        services_comparator(model_1_name,
                            model_2_name,
                            model_1.service_definitions[service_name][0],
                            model_2.service_definitions[service_name][0])

    #component types
    info("[DIFF] ======== Compare component types")
    intersection_comp_type = compare_set("following component types are not defined",
                                         model_1_name,
                                         model_2_name,
                                         set(model_1.component_types.keys()),
                                         set(model_2.component_types.keys()))

    for comp_type_name in intersection_comp_type:
        comp_type_comparator(model_1_name,
                             model_2_name,
                             model_1.component_types[comp_type_name][0],
                             model_2.component_types[comp_type_name][0])

    # component implementations
    info("[DIFF] ======== Component implementations")
    intersection_comp_impl = compare_set("following component implementation "+
                                         "are not defined",
                                         model_1_name,
                                         model_2_name,
                                         set(model_1.component_implementations.keys()),
                                         set(model_2.component_implementations.keys()))

    for comp_impl_name in intersection_comp_impl:
        comp_impl_comparator(model_1_name,
                             model_2_name,
                             model_1.component_implementations[comp_impl_name][0],
                             model_2.component_implementations[comp_impl_name][0])

    info("[DIFF] ======== Wires")
    wires_comparator(model_1_name, model_2_name,
                     model_1.final_assembly_composite.wires,
                     model_2.final_assembly_composite.wires)

    # deployment
    info("[DIFF] ======== Deployment")
    deployment_comparator(model_1_name, model_2_name,
                          model_1.deployment,
                          model_2.deployment)
