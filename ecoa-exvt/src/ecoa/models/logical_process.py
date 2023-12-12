# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Logical_Processors:
    """Logical Processors

    Attributes:
        id (int):
        processors_number (int):
        processor_type (str):
        step_duration (str):
    """
    id_counter = 0

    def __init__(self, number, ptype, stepDuration):
        self.id = Logical_Processors.id_counter
        self.processors_number = number
        self.processor_type = ptype
        self.step_duration = stepDuration
        Logical_Processors.id_counter = Logical_Processors.id_counter + 1

    def get_number(self):
        return self.processors_number

    def get_step_duration(self):
        return self.step_duration
