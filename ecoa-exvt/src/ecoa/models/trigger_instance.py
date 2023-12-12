# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .generic_module_instance import Gen_Module_Instance
from collections import OrderedDict


class Trigger_Instance(Gen_Module_Instance):
    """Class based on :class:`.Gen_Module_Instance` to describe trigger module instances

    Attributes:
        id                      (int) : unique number
        out_points_dict         (dict): dictionary of periods for this trigger. Each period
                                        is associated to a list of links.
                                        Period (str) -> list of :class:`.Module_Link`
                                        (the name of operation is the period as string)
    """
    id_counter = 0

    def __init__(self, name, trigger_index, behaviour="", deadline=0, wcet=0):
        super().__init__(name, trigger_index, behaviour, deadline, wcet)
        self.id = Trigger_Instance.id_counter

        Trigger_Instance.id_counter = Trigger_Instance.id_counter + 1

    def get_id(self):
        return self.id

    def get_implementation(self):
        return "trigger"

    def fill_in_out_points_dicts(self, component_impl):
        """Fill `entry_points_dict` and `out_points_dict` dictionaries

        Args:
            component_impl (:class:`.Component_Implementation`): component implementation
                                that contains this module instance
        """
        self.out_points_dict = OrderedDict()
        self.entry_points_dict = OrderedDict()

        super().fill_in_out_points_dicts(component_impl)
