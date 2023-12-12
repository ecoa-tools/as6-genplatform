# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .logical_process import Logical_Processors
from ..utilities.logs import warning

class Node:
    """Describes a node instance within a :class:`.Platform`

    Attributes:
        id
        name
        logical_processors
        module_switch_time
    """

    id_counter = 0

    def __init__(self, name):
        self.name = name
        self.id = Node.id_counter
        self.logical_processors = set()
        self.module_switch_time = 0
        Node.id_counter = Node.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_logical_processors(self, number, ptype, step_duration):
        logical_processors = Logical_Processors(number, ptype, step_duration)
        self.logical_processors.add(logical_processors)
        return True

    def get_processors_number(self):
        nb = 0
        for lp in self.logical_processors:
            nb = nb + lp.get_number()
        return nb

    def get_mean_step_duration(self):
        mean = 0
        nb = 0
        for lp in self.logical_processors:
            mean = mean + lp.get_step_duration() * lp.get_number()
            nb = nb + lp.get_number()
        mean = mean / nb
        return int(mean)

    def set_module_switch_time(self, mst):
        if self.module_switch_time != 0:
            warning("Enforce new module switch time %d for node %s" % (mst, self.name))
        self.module_switch_time = mst
        return True

    def get_module_switch_time(self):
        return self.module_switch_time
