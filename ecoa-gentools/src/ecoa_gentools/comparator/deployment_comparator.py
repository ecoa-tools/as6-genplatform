# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
Comparaison functions for Deployment
"""

from ecoa.utilities.logs import warning
from .utils_comparator import compare_set


def _pd_comparator(pd_1, pd_2):
    """Compare 2 Protection Domains"""
    # platform
    if pd_1.platform != pd_2.platform:
        warning(("[DIFF] in protection domain '%s', "+\
                 "platforms are different (%s != %s)") %
                (pd_1.name, pd_1.platform, pd_2.platform))

    # node
    if pd_1.node != pd_2.node:
        warning(("[DIFF] in protection domain '%s', "+\
                 "nodes are different (%s != %s)") %
                (pd_1.name, pd_1.node, pd_2.node))

    # deployed module
    # TODO


def deployment_comparator(model_1_name, model_2_name, dep_1, dep_2):
    """Compare 2 Deployments
    """
    # assembly name
    if dep_1.assembly_name != dep_2.assembly_name:
        warning("[DIFF] in deployment, assembly name (%s != %s)"%
                (dep_1.assembly_name, dep_2.assembly_name))

    # logical_system name
    if dep_1.logical_sys_name != dep_2.logical_sys_name:
        warning("[DIFF] in deployment, logical system (%s != %s)"%
                (dep_1.logical_sys_name, dep_2.logical_sys_name))

    # protection domains
    intersection_pd = compare_set("in deployment",
                                  model_1_name,
                                  model_2_name,
                                  set(dep_1.protection_domains.keys()),
                                  set(dep_2.protection_domains.keys()))

    # for protection domains defined in both model: check consistency
    for pd_name in intersection_pd:
        _pd_comparator(dep_1.protection_domains[pd_name],
                       dep_2.protection_domains[pd_name])

    # wire mapping
    # TODO: Not necessary ?

    # platform config
    # TODO: Not necessary ?
