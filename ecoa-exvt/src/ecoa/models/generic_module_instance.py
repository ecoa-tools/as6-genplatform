# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

class Gen_Module_Instance:
    """ Generic module instance class

    Attributes:
        name              (str) : module name
        behaviour         (int) : NOT USED
        deadline          (int) : NOT USED
        wcet              (int) : NOT USED
        module_index      (int) : index of the module (to retrieve module context in generated code)
        fifo_size         (int) : size of the module FIFO
        entry_points_dict (dict): dictionary of entry points. module_op_name -> list of links
                                 (target == this trigger)
        entry_links_index (dict): dictionary of operation name to retrieved index of
                                  this operation and a link connected to this operation
        out_points_dict   (dict): dictionary of out points. module_op_name -> list of links
                                  (source == this trigger)
    """

    def __init__(self, name, module_index, behaviour="", deadline=0, wcet=0):
        self.name = name
        self.behaviour = behaviour
        self.deadline = deadline
        self.wcet = wcet
        self.module_index = module_index

        self.fifo_size = -1
        self.entry_points_dict = OrderedDict()
        self.entry_links_index = OrderedDict()
        self.out_points_dict = OrderedDict()

    def get_mod_index(self):
        """Gets the module index.
        In C code, this index is specific to a component context and allow to retrieve
        module context at runtime.

        Returns:
            int: module index
        """
        return self.module_index

    def set_fifo_size(self, new_fifo_size):
        """set module fifo size

        Args:
            new_fifo_size (int): new size of FIFO
        """
        self.fifo_size = new_fifo_size

    def fill_in_out_points_dicts(self, component_impl):
        """Fill entry_points_dict and out_points_dict dictionaries
        key : name of :class:`.Module_Operation_Type`
        value : list of :class:`.Module_Link`

        Args:
            component_impl (:class:`.Component_Implementation`): component implementation that contains this module
        """

        for l in component_impl.links:

            if l.source == self.name:
                if l.type == 'data':
                    # data message are sent by VD_writer_manager
                    continue

                if l.source_operation not in self.out_points_dict:
                    self.out_points_dict[l.source_operation] = []
                self.out_points_dict[l.source_operation].append(l)

            elif l.target == self.name:
                if l.target_operation not in self.entry_points_dict:
                    self.entry_points_dict[l.target_operation] = []
                self.entry_points_dict[l.target_operation].append(l)


    def fill_entry_links_index(self, component_impl):
        """Fill entry_links_index dictionary
            * key : module operation name of :class:`.Module_Link`
            * value : tuple of (the new link index , :class:`.Module_Link`)

        Note:
            In case of multiple links connected to the same operation type, only the first one
            is used in the tuple
            There is no consequences in the generated code.

        Args:
            component_impl  (:class:`.Component_Implementation`): The component implementation
        """
        l_index = 1 # start at one because first index is reserved for lifecycle operations
        for l in component_impl.links:
            if l.target == self.name:
                if l.target_operation not in self.entry_links_index:
                    self.entry_links_index[l.target_operation] = (l_index, l)
                    l_index += 1
            elif l.source == self.name and l.type == 'RR':
                ## add input for RR answer
                if l.target_operation not in self.entry_links_index:
                    self.entry_links_index[l.source_operation] = (l_index, l)
                    l_index += 1

    def offset_entry_links_index(self, index_offset):
        """set entry_links_index dictionary by adding an offset to the link index
        
        Args:
            new_index  (int): The new index
        """
        for op_name, (l_index, l) in sorted(self.entry_links_index.items(), key=lambda x: x[1][0]):
            self.entry_links_index[op_name] = (l_index + index_offset, l)



    ## useless ??
    def get_behaviour(self):
        return self.behaviour

    def get_wcet(self):
        return self.wcet

    def get_deadline(self):
        return self.deadline

    def get_name(self):
        return self.name
