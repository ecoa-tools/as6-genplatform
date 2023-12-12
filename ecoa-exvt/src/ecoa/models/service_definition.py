# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..utilities.logs import debug, warning

class Operation_Definition:
    """Operation_Definition

    Attributes:
        id         (int)  : unique number
        name       (str)  : service name
        nature     (str)  : nature of the operation : DATA, CMD, NOTIFY, RR
        inputs     (list) : list of input :class:`.Parameter`
                                only used for CMD, NOTIFY, RR
        outputs    (list) : list of output :class:`.Parameter`
                                only used for CMD, NOTIFY, RR
        params     (list) : list that contains both inputs and outputs
    """
    id_counter = 0 #: unique operation number

    def __init__(self, name, nature="", data_type="", inputs=[], outputs=[]):
        self.name = name
        self.id = Operation_Definition.id_counter
        self.nature = nature
        self.inputs = inputs
        self.outputs = outputs
        self.params = inputs + outputs
        Operation_Definition.id_counter = Operation_Definition.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_nature(self):
        return self.nature

    def get_data_type(self):
        return self.data_type


class Service_Definition:
    """Describes a definition of a service

    Attributes:
        id         (int)  : unique number
        name       (str)  : service syntax name
        libraries  (list) : list of libraries names used to defined operations parameters
                            within this service
        operations (list) : list of :class:`.Operation_Definition` within this service
    """
    id_counter = 0 #:unique service_definition ID

    def __init__(self, name):
        self.name = name
        self.id = Service_Definition.id_counter
        self.libraries = []
        self.operations = []
        Service_Definition.id_counter = Service_Definition.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_operation(self, name, nature, data_type, inputs, outputs):
        """Create an :class:`.Operation_Definition` and add it. Enforce that all operations
                have different names

        Args:
            name : operation name
            nature     (str) : operation nature ('DATA', 'CMD', 'NOTIFY' or 'RR')
            data_type  (str) : type of the DATA operation, only used for DATA
            inputs     (list): list of inputs parameters. list of tuples (name, type)
            outputs    (list): list of inputs parameters. list of tuples (name, type)

        Returns:
            True or False in case of failed
        """

        if name in self.operations:
            warning("Operation %s already defined in %s" % (name, self.name))
            return False
        else:
            o = Operation_Definition(name, nature, data_type, inputs, outputs)
            self.operations.append(o)
            return True

    def add_library(self, library_name):
        """Add a library name. Enforce only one instance of one given type

        Args:
            library_name  (str): name of the library

        Returns:
            True or False in case of failed
        """
        if library_name in self.libraries:
            print("Library %s already defined for %s" % (library_name, self.name))
            return False
        else:
            self.libraries.append(library_name)
            return True

    def find_input_operation(self, on_reference_side):
        input_ops = set()
        for op in self.operations:
            if on_reference_side:
                if op.nature in ['CMD', 'DATA', 'RR']:
                    debug("    + input operation "+ op.name)
                    input_ops.add(op.name)
                elif op.nature == 'NOTIFY':
                    debug("    - output operation "+ op.name)

            else:
                if op.nature in ['NOTIFY', 'DATA', 'RR']:
                    debug("    + input operation "+ op.name)
                    input_ops.add(op.name)
                elif op.nature == 'CMD':
                    debug("    - output operation "+ op.name)

        return sorted(input_ops)

    def find_operation(self, op_name):
        for op in self.operations:
            if op.name == op_name:
                return op
        return None
