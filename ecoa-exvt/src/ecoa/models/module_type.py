# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

from .property_type import Property_Type
from .operation_type import Module_Event_Operation, Module_RR_Operation, Module_VD_Operation
from ..utilities.logs import warning


class Module_Type:
    """Describe a module type

    Attributes:
        name             (str) : module type name
        fault_handler    (bool): NOT USED
        user_context     (bool): Flag in order to generate user context
        warm_start_context    (bool): Flag in order to generate warm start context
        id               (int) : unique number of module type. NOT USED
        operations       (dict): dictionary of :class:`~.Module_Operation_Type` retrieved by
                                 operation name
        input_operations (list): list of name of input :class:`~.Module_Operation_Type`
        output operations(list): list of name of output :class:`~.Module_Operation_Type`
        properties       (dict): dictionary of :class:`.Property_Type` retrieved by property name
    """
    id_counter = 0

    def __init__(self, name, fault_handler_flag=False, user_context_flag=True, warm_start_context_flag=True):
        self.name = name
        self.fault_handler = fault_handler_flag
        self.user_context = user_context_flag
        self.warm_start_context = warm_start_context_flag
        self.id = Module_Type.id_counter
        self.operations = OrderedDict()
        self.input_operations = []
        self.output_operations = []

        self.properties = OrderedDict()
        self.private_pinfo = []
        self.public_pinfo = []

        Module_Type.id_counter = Module_Type.id_counter + 1

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_operation(self, op_name, op_type, op_params, timeout=-1, maxVersions=0, writeOnly=False):
        if op_name in self.operations:
            warning("Module operation %s already defined for module type %s" % (op_name, self.name))
            return False
        else:
            if op_type in ['ES', 'ER']:
                self.operations[op_name] = Module_Event_Operation(op_name, op_type, op_params)
                if op_type == 'ES':
                    self.output_operations.append(op_name)
                else:
                    self.input_operations.append(op_name)

            elif op_type in ['RR', 'ARS', 'SRS']:
                self.operations[op_name] = Module_RR_Operation(op_name, op_type, op_params,
                                                               timeout, maxVersions)
                self.output_operations.append(op_name)
                self.input_operations.append(op_name)
                # set an index
                # self.set_RR_index(op_name)
            elif op_type in ['DW', 'DR', 'DRN']:
                self.operations[op_name] = Module_VD_Operation(op_name, op_type, op_params,
                                                               maxVersions, write_only=writeOnly)
                if op_type == 'DRN':
                    self.input_operations.append(op_name)

            if op_type != 'ER':
                self.operations[op_name].op_output_index = max([op.op_output_index for op
                                                                in self.operations.values()]) + 1
            if op_type in ['ER', 'DRN', 'RR', 'ARS', 'SRS']:
                self.operations[op_name].op_input_index = max([op.op_input_index for op
                                                               in self.operations.values()]) + 1

            return True

    def add_property(self, prop_name, prop_type, libraries):
        if prop_name in self.properties:
            warning("Module operation %s already defined for module type %s" % (prop_name, self.name))
            return False
        else:
            self.properties[prop_name] = Property_Type(prop_name, prop_type, libraries)
            return True

    def add_private_pinfo(self, pinfo_name):
        if pinfo_name in self.private_pinfo:
            warning("Module private pinfo "+ pinfo_name+ " alrready defined for module type "+ self. name)
            return False
        else:
            self.private_pinfo.append(pinfo_name)
            return True

    def add_public_pinfo(self, pinfo_name):
        if pinfo_name in self.public_pinfo:
            warning("Module public pinfo "+ pinfo_name+ " alrready defined for module type "+ self. name)
            return False
        else:
            self.public_pinfo.append(pinfo_name)
            return True

    def get_properties(self):
        return self.properties

    def get_operations(self):
        return self.operations

    def get_operation(self, op_name):
        return self.operations[op_name]

    def is_fault_handler(self):
        return self.fault_handler

    def has_user_context(self):
        return self.user_context

    def has_warm_start_context(self):
        return self.warm_start_context

    def set_vd_indexes(self):
        """For each :class:`.Module_VD_Operation`, give an unique index in this module by
        setting `module_op_index` and set vd_index array
        """
        index_VD_read = 0
        index_VD_write = 0
        for op in self.operations.values():
            if op.type in ['DRN', 'DR']:
                op.module_VD_op_index = index_VD_read
                # self.vd_index[op.name] = index_VD
                index_VD_read += 1
            elif op.type == 'DW':
                op.module_VD_op_index = index_VD_write
                index_VD_write += 1

    def find_VD_op(self):
        """Find all operations for Versioned Data within this module

        return:
            list of :class:`.Module_VD_Operation`
        """
        list_VD_op = []
        for op in self.operations.values():
            if op.type in ['DRN', 'DR', 'DW']:
                list_VD_op.append(op)
        return list_VD_op

    def set_rr_indexes(self):
        index_RR = 0
        for op in self.operations.values():
            if op.type in ['RR', 'ARS', 'SRS']:
                op.RR_op_index = index_RR
                index_RR += 1

    def has_RR_operations(self):
        for op in self.operations.values():
            if op.type in ['RR', 'ARS', 'SRS']:
                return True
        return False

