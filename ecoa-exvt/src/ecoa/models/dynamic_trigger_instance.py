# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .generic_module_instance import Gen_Module_Instance
from .operation_type import Module_Event_Operation, Parameter
from ..utilities.logs import error



class Dynamic_Trigger_Instance(Gen_Module_Instance):
    """Class based on :class:`.Gen_Module_Instance` to describe dynamic trigger module instance

    Attributes:
        id        (int) :
        size      (int) : number of trigger that module can handle at the same time
        params    (list): list of :class:`.Parameter` for event sent by this module
        event_in  (:class:`.Module_Event_Operation`) : event sent by this module
    """
    id_counter = 0

    def __init__(self, name, dynamic_trigger_index, behaviour="", deadline=0, wcet=0, size=1):
        super().__init__(name, dynamic_trigger_index, behaviour, deadline, wcet)
        self.id = Dynamic_Trigger_Instance.id_counter
        self.size = size
        self.params = []
        self.event_in = None

        Dynamic_Trigger_Instance.id_counter = Dynamic_Trigger_Instance.id_counter + 1

    def set_params(self, parameters):
        """Set `params` list and set  `event_in`

        Attributes:
            parameters (list): new list of :class:`.Parameter`
        """
        self.params.append(Parameter("delayDuration", "ECOA:duration", "input", is_complex=True))
        self.params += parameters
        self.event_in = Module_Event_Operation("out", "ES", self.params)

    def fill_entry_links_index(self, component_impl):
        """Create dictionary specific for dynamic trigger module

        Args:
            component_impl (:class:`.Component_Implementation`): component implementation of the module instance
        """
        # for dynamic trigger, operations and index:
        # ------------+-------
        #  lifecycle  |  0
        #  in         |  1
        #  reset      |  2

        for l in component_impl.links:
            if l.target == self.name:
                if l.target_operation == "in":
                    self.entry_links_index["in"] = (1, l)
                elif l.target_operation == "reset":
                    self.entry_links_index["reset"] = (2, l)
                else:
                    error("entry operation for dynamic trigger not allowed " + l.__repr__())

    def get_id(self):
        return self.id

    def get_implementation(self):
        return "dynamic_trigger"
