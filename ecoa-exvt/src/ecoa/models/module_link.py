# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

class Module_Link:
    """Class for an operation link within an ECOA Component

        Attributes:
            source     (str): source name (module or service/reference)
            source_op  (str): source operation name
            source_xml (str): source operation xml ('service', 'reference')
            target     (str): target name (module or service/reference)
            target_op  (str): target operation name
            target_xml (str): target operation xml ('service', 'reference')
            type  (str): operation type ('event, 'RR', 'data)
            fifoSize   (int): maximum number of pending operation in FIFO
            activating_op (bool): activating or non-activating operation (for target, if it is a modul)           
            activating_RR_answer (bool): RR answer activating or non-activating
    """
    id_counter = 0  #: unique module_link number

    def __init__(self, source, source_op, source_xml, target, target_op, target_xml, link_type):
        self.name = link_type + "_" + source_op
        self.id = Module_Link.id_counter
        self.source = source
        self.source_operation = source_op
        self.source_xml = source_xml
        self.target = target
        self.target_operation = target_op
        self.target_xml = target_xml
        self.type = link_type
        self.fifoSize = -1
        self.activating_op = True
        self.activating_RR_answer = True
        Module_Link.id_counter = Module_Link.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def set_fifoSize(self, size):
        self.fifoSize = size

    def __repr__(self):
        if self.source is None:
            return self.name + ':EXTERNAL_' + self.target + '_' \
                   + self.target_operation
        else:
            return self.name + ':' + self.source + '_' + self.target + '_' \
                   + self.target_operation

    def get_op_id(self):
        """Create ID string of this link

        Return:
            str: the ID
        """
        if self.source is None:
            return "ID_External_" + self.target + "_" + self.target_operation
        else:
            return "ID_" + self.source + "_" + self.target + "_" + self.target_operation

    def is_external(self):
        """
        Return:
            (bool) True if this link connects a Module and a Non-ECOA Module
        """
        return self.source is None

    def is_external_c(self):
        """
        Return:
            (bool) True if this link connects a Module and a Non-ECOA C Module
        """
        return self.is_external() and self.source_xml == "external_C"

    def is_external_cpp(self):
        """
        Return:
            (bool) True if this link connects a Module and a Non-ECOA C++ Module
        """
        return self.is_external() and self.source_xml == "external_C++"

    def is_between_modules(self, comp_impl):
        """Determines if link is between 2 module instances or not

        Args:
            comp_impl  (:class:`.Component_Implementation`): component implementation that contains this link

        Return:
            True if link is between modules, False otherwise.
        """
        if not comp_impl.is_generic_module_instance(self.source):
            return False
        if not comp_impl.is_generic_module_instance(self.target):
            return False
        return True

    def find_connected_wires_link(self, component_name, wires):
        """Find connected :class:`.Wire` for this link in a component

        Args:
            component_name  (str) : Component name
            wires           (dict): Dictionary of all :class:`.Wire`

        Return:
            list: list of connected :class:`.Wire`
        """
        connected_wires = []
        for w in wires:
            if w.source_component == component_name and w.source_service \
                    in [self.target, self.source]:
                connected_wires.append(w)
            elif w.target_component == component_name and w.target_service \
                    in [self.target, self.source]:
                connected_wires.append(w)
        return connected_wires
