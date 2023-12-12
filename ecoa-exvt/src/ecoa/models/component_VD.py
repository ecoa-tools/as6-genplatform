# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

class vd_reader:
    """Module or service reader of a Versioned Data

    Attributes:
        name    (str): name of reader
        op_name (str): operation name for this VD
    """
    def __init__(self, reader_name, op_name):
        self.name = reader_name
        self.op_name = op_name

class vd_reader_module(vd_reader):
    """Class based on :class:`.vd_reader` for module reader of Versioned Data

    Attributes:
        fifo_size      (int) : number of notified operation that module FIFO can handle
        activating_op  (bool): notified operations are activating
        to_be_notified (bool): this reader need to be notified after a VD publication
    """
    def __init__(self, mod_name, op_name, fifo_size, activating_op):
        super().__init__(mod_name, op_name)
        self.fifo_size = fifo_size
        self.activating_op = activating_op
        self.to_be_notified = False

    def set_notifying(self, mod_type):
        op_type = mod_type.operations[self.op_name]
        if op_type.type == 'DRN':
            self.to_be_notified = True
        else:
            self.to_be_notified = False

class vd_writter:
    """Module or service writter of a Versioned Data

    Attributes:
        name    (str): name of writter
        op_name (str): operation name for this VD
    """
    def __init__(self, writter_name, op_name):
        self.name = writter_name
        self.op_name = op_name


class component_VD:
    """Versioned Data that is described in a component implementation by a dataLink

    Attributes:
        readers_dict      (dict): dictionary of :class:`.vd_reader`
        writters_dict     (dict): dictionary of :class:`.vd_writter`
        data_type          (str): type of data in the VD
        num_written_copies (int): number of copy in written access
        accessControl     (bool): true if access to this VD is controlled
    """
    def __init__(self, index, accessControl):
        self.readers_dict = OrderedDict()
        self.writters_dict = OrderedDict()
        self.data_type = ""
        self.num_written_copies = 0
        self.accessControl = accessControl

    def add_writer(self, writer_name, op_name):
        new_writter = vd_writter(writer_name, op_name)
        if writer_name not in self.writters_dict:
            self.writters_dict[writer_name] = []
        self.writters_dict[writer_name].append(new_writter)

    def add_reader_module(self, mod_name, op_name, fifo_size, activating_op):
        new_reader = vd_reader_module(mod_name, op_name, fifo_size, activating_op)
        if mod_name not in self.readers_dict:
            self.readers_dict[mod_name] = []
        self.readers_dict[mod_name].append(new_reader)

    def add_reader_service(self, serv_name, op_name):
        new_reader = vd_reader(serv_name, op_name)
        if serv_name not in self.readers_dict:
            self.readers_dict[serv_name] = []
        self.readers_dict[serv_name].append(new_reader)

    def set_data_type(self, type):
        self.data_type = type

    def get_VD_access_mode(self):
        if self.accessControl:
            return "CONTROLLED"
        else:
            return "UNCONTROLLED"

    def get_readers(self):
        """get the list of readers

        Return:
            (list): list of :class:`vd_reader` (module or service)
        """
        readers_list=[]
        for readers in self.readers_dict.values():
            readers_list+=readers

        return readers_list

    def find_data_type(self, comp_impl, module_instances, module_types, module_implementations):
        """Fill data_type attribute. Find the first operation type of a module (reader or writer)
        """
        op_name = ""
        mod_inst = ""
        for writter_name, writters in self.writters_dict.items():
            if comp_impl.is_module_instance(writter_name):
                mod_inst = comp_impl.get_instance(writter_name)
                op_name = writters[0].op_name
                break

        if mod_inst == "":
            # no writer module found
            for reader_name, readers in self.readers_dict.items():
                if comp_impl.is_module_instance(reader_name):
                    mod_inst = comp_impl.get_instance(reader_name)
                    op_name = readers[0].op_name
                    break

        if  mod_inst == "":
            # strange VD with no reader or writer modules. only service or reference.
            # An empty repository will be created
            self.set_data_type("1")
        else:
            # a module and a operation have been found.
            mod_type_name = module_implementations[mod_inst.implementation].type
            op = module_types[mod_type_name].operations[op_name]
            self.set_data_type(op.params[0].type)

    def fill_notify_reader_module(self, module_instances, module_types, module_implementations):
        """fill fill notify property of reader modules
        """
        for reader in self.get_readers():
            if type(reader) == vd_reader_module:
                module_inst = next(m for m in module_instances if m.name == reader.name)
                module_type = module_types[module_implementations[module_inst.implementation].type]
                reader.set_notifying(module_type)

    def compute_local_maxVersions(self, component_implementation):
        """compute the number of Version in written access that this VD requieres

        Note:
            number of written access for each writtern modules
            + number of module writer
            + number of module reader
        """
        self.num_written_copies = 0
        for writter in self.writters_dict.keys():
            if component_implementation.is_module_instance(writter):
                module_type = component_implementation.find_module_type(writter)
                for writter_op in self.writters_dict[writter]:
                    op = module_type.operations[writter_op.op_name]
                    self.num_written_copies += op.maxVersions
                    self.num_written_copies += 1

        for reader in self.readers_dict.keys():
            if component_implementation.is_module_instance(reader):
                self.num_written_copies += 1

    def __str__(self):
        string = ""
        string = "W : "
        # for w in self.writers_name:
        #     string += " ("+w+", "+self.writers_op_name[w]+")"

        # string += "\nR : "
        # for r in self.readers_name:
        #     string += " ("+r+", "+self.readers_op_name[r]+")"

        return string
