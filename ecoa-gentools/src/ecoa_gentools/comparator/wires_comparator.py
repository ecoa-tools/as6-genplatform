# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

"""
Comparaison functions for Wires
"""
from .utils_comparator import compare_set

def wires_comparator(model_1_name, model_2_name, wires_1, wires_2):
    #
    wires_description_set_1 = set([(w.source_component,
                                    w.source_service,
                                    w.target_component,
                                    w.target_service) for w in wires_1])

    wires_description_set_2 = set([(w.source_component,
                                    w.source_service,
                                    w.target_component,
                                    w.target_service) for w in wires_2])


    intersection_wires = compare_set("following wires are not defined",
                                       model_1_name,
                                       model_2_name,
                                       wires_description_set_1,
                                       wires_description_set_2)
