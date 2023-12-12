# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from collections import OrderedDict

import os
from .generic_module_instance import Gen_Module_Instance
from .property_classes import Module_Property
from .pinfo import Pinfo
from ..utilities.logs import error, warning

class Module_Instance(Gen_Module_Instance):
    """Class based on :class:`.Gen_Module_Instance` to describe normal module instance

    Attributes:
        id                (int): unique module instance number
        implementation    (str): name of the implementation module
        relative_priority (int):
        property_values   (dict): dictionary of :class:`.Module_Property`
        pinfo             (dict): dictionary of :class:`.Pinfo`
    """

    id_counter = 0  #: unique module instance number

    def __init__(self, name, module_index, implementation="", behaviour="", relative_priority=0,
                 deadline=0, wcet=0):
        super().__init__(name, module_index, behaviour, deadline, wcet)
        self.id = Module_Instance.id_counter
        self.implementation = implementation  #: (str) module implementation name
        self.relative_priority = relative_priority  #: (int)
        self.property_values = OrderedDict()
        self.pinfo = OrderedDict()

        self.VD_read_op_map = OrderedDict() #! (dict): map VD operations of module_type to a VD repository in Component: op_name -> VD_repo
        self.VD_written_op_map = OrderedDict()

        Module_Instance.id_counter = Module_Instance.id_counter + 1

    def get_id(self):
        return self.id

    def get_implementation(self):
        return self.implementation

    def add_property_value(self, mod_type, p_name, value):
        if p_name in self.property_values:
            error("Property value "+ p_name +"is already define in module " + self.name)
            return

        if p_name not in mod_type.properties:
            error("Property value "+ p_name + " in module " + self.name + " is not define in module type "+ mod_type.name)
            return

        self.property_values[p_name] = Module_Property(p_name, value)

    def add_private_pinfo_value(self, pinfo_name, pinfo_value, pinfo_index):
        if pinfo_name in self.pinfo:
            error("Private pinfo "+ pinfo_name + "is already define in module "+self.name)
            return False
        else:
            self.pinfo[pinfo_name] = Pinfo(pinfo_name, pinfo_value, True, pinfo_index)
            return True

    def add_public_pinfo_value(self, pinfo_name, pinfo_value, pinfo_index):
        if pinfo_name in self.pinfo:
            error("Public pinfo "+ pinfo_name + "is already define in module "+self.name)
            return False
        else:
            self.pinfo[pinfo_name] = Pinfo(pinfo_name, pinfo_value, False, pinfo_index)
            return True

    def fill_in_out_points_dicts(self, component_impl, mod_type):
        """Fill `entry_points_dict` and `out_points_dict` dictionaries

        Args:
            component_impl (:class:`.Component_Implementation`): component implementation that
                contains this module instance
            mod_type       (:class:`.Module_Type`):
        """

        # init out-operations dictionary
        self.out_points_dict = OrderedDict()
        for out_op_name in mod_type.output_operations:
            self.out_points_dict[out_op_name] = []

        # init entry-operations dictionary
        self.entry_points_dict = OrderedDict()
        for in_op_name in mod_type.input_operations:
            self.entry_points_dict[in_op_name] = []

        # Fill dictionaries
        super().fill_in_out_points_dicts(component_impl)

        for l in component_impl.links:
            if l.type == 'RR':
                if l.source == self.name:
                    # in case of RR, we have to add a event in entry_point_dict for the answer
                    op_name = l.source_operation
                    if op_name not in self.entry_points_dict:
                        error("Operation "+op_name+" is not an in-operation for module "+self.name)
                    else:
                        self.entry_points_dict[op_name].append(l)

                if l.target == self.name:
                    # in case of RR, we have to add a event in out_points_dict to send the answer
                    op_name = l.target_operation
                    if op_name not in self.out_points_dict:
                        error("Operation "+op_name+" is not an out-operation for module "+self.name)
                    else:
                        self.out_points_dict[op_name].append(l)

            elif l.type == 'data' and l.target == self.name:
                # for a data notification, add a event in entry_points_dict
                op = mod_type.operations[l.target_operation]
                if op.type == 'DRN':
                    self.entry_points_dict[l.target_operation] = [l]



    def check_and_fill_properties(self, m_type, libraries, component_type):
        """Check properties that refer to a component property and fill property_type of
        each properties

        Attributes:
            component_properties  (dict)  : the component dictionary of :class:`.Component_Property`
            m_type                (:class:`.Module_Type`): The module type
            libraries             (dict)  : The dictionary of :class:`.Library`
            component_type (:class:`.Component_Type`): type of the component
        """
        for prop in self.property_values.values():
            # check reference value
            if not prop.check_reference(component_type.properties):
                error("Invalide reference : "+str(prop))
                continue

            # check if property type exists in module type
            if prop.name not in m_type.properties:
                error("Property "+prop.name + " is not declared in module type "+m_type.name)
                continue

            # if value is a refence, check type consistency betwenn type reference and property value type
            if prop.value[0] == '$':
                prop_type = m_type.properties[prop.name]
                comp_prop = component_type.properties[prop.value[1:]]
                if comp_prop.type != prop_type.type:
                    warning("[%s] property type consistency for property '%s': '%s' != '%s'"\
                        %(self.name,prop.name, comp_prop.type, prop_type.type))

            prop.property_type = m_type.properties[prop.name]


    def fill_pinfo_directory(self, integration_directory, implementation_directory, comp_impl_name):
        """Fill pinfo directory

        Attributes:
            integration_directory     (str): The integration directory
            implementation_directory  (str): The implementation directory
            comp_impl_name            (str): The component implementation name
        """
        for p in self.pinfo.values():
            if not p.is_private:
                p.directory = os.path.join(integration_directory, "Pinfo")
            else:
                p.directory = os.path.join(implementation_directory, "Pinfo")


