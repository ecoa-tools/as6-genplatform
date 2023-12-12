# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .module_instance import Module_Instance
from .dynamic_trigger_instance import Dynamic_Trigger_Instance
from .trigger_instance import Trigger_Instance
from .component_VD import component_VD
from .module_link import Module_Link
from .module_type import Module_Type
from .module_implementation import Module_Implementation
from ..utilities.logs import debug, error, warning
from collections import OrderedDict

class Component_Implementation:
    """Describes an implementation of component referred by a component instance within
        an assembly schema

    Attributes:
        id                  (int) : unique number
        name                (str) : component implementation name
        module_types        (dict): dictionary of :class:`.Module_Type` retrieved by name
        module_implementations (dict): dictionary of  :class:`.Module_Implementation` retrieved
                                                                by name
        module_instances    (list): list of :class:`.Module_Instance`
        trigger_instances   (list): list of :class:`.Trigger_Instance`
        dynamic_trigger_instances (list): list of :class:`.Dynamic_Trigger_Instance`
        links               (list): list of :class:`.Module_Link`
        component_VDs           (list): list of :class:`.component_VD` (in read or written access)
        buffer_pool_size    (int) : size of buffer pool
    """
    id_counter = 0

    def __init__(self, name, impl_dir):
        self.name = name
        self.id = Component_Implementation.id_counter
        self.impl_directory = impl_dir
        self.libraries = ['ECOA']
        self.module_types = OrderedDict()
        self.module_implementations = OrderedDict()
        self.module_instances = []

        self.trigger_instances = []
        self.dynamic_trigger_instances = []
        self.links = []

        self.component_VDs = []

        self.buffer_pool_size = -1

        Component_Implementation.id_counter += 1

    def __lt__(self, other):
        return self.name < other.name

    def has_cpp_module(self):
        """Returns True if there is at least one module which has c++ type, False if no one"""
        for mimpl in self.module_implementations.values():
            if mimpl.language == "C++":
                return True
        return False

    def fill_module_inst_info(self):
        """Fill normal module instance information :
            - compute VD index
            - fill in and out points dictionary
        """
        for m_Inst in self.module_instances:
            m_type = self.module_types[self.module_implementations[m_Inst.implementation].type]
            m_type.set_vd_indexes()
            m_type.set_rr_indexes()

            m_Inst.fill_in_out_points_dicts(self, m_type)
            m_Inst.fill_entry_links_index(self)

            # support of unconnected Data in written access
            self.add_vd_unconnected_DW(m_Inst, m_type)

        self.map_mod_VD_operations()


        for vd in self.component_VDs:
            vd.find_data_type(self, self.module_instances, self.module_types, self.module_implementations)
            vd.fill_notify_reader_module(self.module_instances, self.module_types,
                                         self.module_implementations)
            vd.compute_local_maxVersions(self)

    def fill_trigger_info(self):
        """Fill trigger module instance information :
            - fill in and out points dictionary
        """
        for m_trig in self.trigger_instances:
            m_trig.fill_in_out_points_dicts(self)
            m_trig.fill_entry_links_index(self)

    def fill_dynamic_trigger_info(self):
        """Fill dynamic trigger module instance information :
            - fill in and out points dictionary
        """
        for m_dtrig in self.dynamic_trigger_instances:
            m_dtrig.fill_in_out_points_dicts(self)
            m_dtrig.fill_entry_links_index(self)


    def add_vd_repository(self, accessControl):
        vd_index = len(self.component_VDs)
        vd = component_VD(vd_index, accessControl)
        self.component_VDs.append(vd)
        return vd


    def add_vd_unconnected_DW(self, m_inst, m_type):
        """detect if a module instance has a not connected written data operation.
        Create a new VD for this operation
        """

        # for data write operation of this module:
        for data_op in [ o for o in m_type.operations.values() if o.type == 'DW']:
            data_op_connected = False

            # check if operation is connected to a VD
            for vd in self.component_VDs:
                if m_inst.name in vd.writters_dict:
                    op_name_list = [op.op_name for op in  vd.writters_dict[m_inst.name]]
                    if data_op.name in op_name_list:
                        data_op_connected = True
                        break

            if not data_op_connected:
                # create a VD only for this data write operation
                print(data_op.name)
                print(m_inst.name)
                vd_index = len(self.component_VDs)
                new_vd = component_VD(vd_index, True)
                new_vd.data_type = data_op.params[0].type
                new_vd.add_writer(m_inst.name, data_op.name)
                self.component_VDs.append(new_vd)



    def set_mod_fifo_sizes(self):
        """Set the size of each module FIFO
        """
        for m in self.module_instances + self.dynamic_trigger_instances + self.trigger_instances:
            new_fifo_size = 2  # minimum size
            for _, l in m.entry_links_index.values():
                assert l.fifoSize > 0
                if l.source == m.name and l.type == "RR":
                    # answers of RR
                    # add all other links connected to this operation
                    mod_type = self.find_module_type(l.source)
                    for l2 in [x for x in self.links if x.get_op_id() == l.get_op_id()]:
                        op = mod_type.get_operation(l2.source_operation)
                        assert op.maxVersions > 0
                        new_fifo_size += op.maxVersions
                else:
                    # other operations
                    new_fifo_size += l.fifoSize

            m.set_fifo_size(new_fifo_size)

    def compute_buffer_pool_size(self):
        """Compute the size of the buffer pool with the size of each module FIFOs.
        """
        self.buffer_pool_size = 2  # add 2 more buffers
        for m in self.module_instances + self.dynamic_trigger_instances + self.trigger_instances:
            if m.fifo_size < 0:
                error("Fifo size is not set for module instance " + m.name)
            self.buffer_pool_size += m.fifo_size

    def is_generic_module_instance(self, name):
        """Check if a name matches with a generic module instance

        Attributes:
            name  (str): name of the module instance

        return:
            bool: True if name matches with a generic module instance, False otherwise.
        """
        if self.is_module_instance(name):
            return True
        if self.is_dynamic_trigger_instance(name):
            return True
        if self.is_trigger_instance(name):
            return True
        return False

    def is_trigger_instance(self, name):
        for m_trig in self.trigger_instances:
            if m_trig.name == name:
                return True
        return False

    def is_module_instance(self, name):
        for m_inst in self.module_instances:
            if m_inst.name == name:
                return True
        return False

    def is_dynamic_trigger_instance(self, name):
        for d_trig in self.dynamic_trigger_instances:
            if d_trig.name == name:
                return True
        return False

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_library(self, name):
        """Enforce only one instance of one given library"""
        if name in self.libraries:
            warning("Library %s already defined for %s" % (name, self.name))
            return False
        else:
            self.libraries.append(name)
            return True

    def add_module_type(self, name, fault_handler_flag, user_context_flag,
                        warm_start_context_flag):
        """Enforce only one instance of one given type"""
        if name in self.module_types:
            warning("Module type %s already defined for %s" % (name, self.name))
            return False
        else:
            mt = Module_Type(name, fault_handler_flag, user_context_flag, warm_start_context_flag)
            self.module_types[name] = mt
            return True

    def add_module_type_operation(self, module_name, op_name, op_type, op_params, timeout=-1,
                                  maxVersions=0, writeOnly=False):
        """Enforce only one instance of one given type"""
        if module_name not in self.module_types:
            error("Module type %s doesn't exist for %s" % (module_name, self.name))
            return False
        else:
            self.module_types[module_name].add_operation(op_name, op_type, op_params,
                                                         timeout=timeout, maxVersions=maxVersions, writeOnly=writeOnly)
            return True

    def add_module_type_property(self, module_name, prop_name, prop_type, libraries):
        """Enforce only one instance of one given type"""
        if module_name not in self.module_types:
            error("Module type %s doesn't exist for %s" % (module_name, self.name))
            return False
        else:
            self.module_types[module_name].add_property(prop_name, prop_type, libraries)
            return True

    def add_module_type_pinfo(self, module_name, pinfo_name, is_private):
        if module_name in self.module_types:
            if is_private:
                return self.module_types[module_name].add_private_pinfo(pinfo_name)
            else:
                return self.module_types[module_name].add_public_pinfo(pinfo_name)
        else:
            error("Module type %s doesn't exist for %s" % (module_name, self.name))
            return False

    def add_module_implementation(self, name, mtype, mlanguage):
        """Enforce only one instance of one given implementation"""
        if name in self.module_implementations:
            warning("Module implementation %s already defined for %s" % (name, self.name))
            return False
        else:
            mi = Module_Implementation(name, mtype, mlanguage)
            self.module_implementations[name] = mi
            return True

    def add_module_instance(self, name, module_index, implementation, behaviour, relative_priority,
                            deadline, wcet):
        """Enforce only one instance of one given instance"""
        if name in self.module_instances:
            warning("Module instance %s already defined for %s" % (name, self.name))
            return False
        else:
            mi = Module_Instance(name, module_index, implementation, behaviour, relative_priority,
                                 deadline, wcet)
            self.module_instances.append(mi)
            return True

    def add_module_inst_pinfo_value(self, mod_name, mod_type, pinfo_name, pinfo_value, is_private):
        mod_inst = self.get_instance(mod_name)
        if is_private:
            if pinfo_name in mod_type.private_pinfo:
                pinfo_index = len(mod_type.public_pinfo) + mod_type.private_pinfo.index(pinfo_name)
                return mod_inst.add_private_pinfo_value(pinfo_name, pinfo_value, pinfo_index)
            else:
                error("Private pinfo "+pinfo_name+" is not defined in module type "+ mod_type.name)
        else:
            if pinfo_name in mod_type.public_pinfo:
                pinfo_index = mod_type.public_pinfo.index(pinfo_name)
                return mod_inst.add_public_pinfo_value(pinfo_name, pinfo_value, pinfo_index)
            else:
                error("Public pinfo "+pinfo_name+" is not defined in module type "+ mod_type.name)
        return False

    def add_trigger_instance(self, name, trigger_index, behaviour, deadline, wcet):
        """Enforce only one instance of one given instance"""
        if name in self.trigger_instances:
            warning("Trigger instance %s already defined for %s" % (name, self.name))
            return False
        else:
            mi = Trigger_Instance(name, trigger_index, deadline)
            self.trigger_instances.append(mi)
            return True

    def add_dynamic_trigger_instance(self, name, dynamic_trigger_index, behaviour, deadline, wcet,
                                     size):
        """Enforce only one instance of one given instance"""
        if name in self.dynamic_trigger_instances:
            warning("Dynamic trigger instance %s already defined for %s" % (name, self.name))
            return False
        else:
            mi = Dynamic_Trigger_Instance(name, dynamic_trigger_index, deadline, size=size)
            self.dynamic_trigger_instances.append(mi)
            return True

    def get_module_implementation_wcet(self, name):
        return self.module_implementations[name].get_wcet()

    def get_module_instance_wcet(self, mname):
        for m in self.module_instances:
            if m.name == mname:
                debug("WCET for %s" % (m.name))
                return self.get_module_implementation_wcet(m.implementation)
        return 0

    def get_module_instance(self, mname):
        for m in self.module_instances:
            if m.name == mname:
                return m
        return None

    def get_module_instance_deadline(self, mname):
        for m in self.module_instances:
            if m.name == mname:
                debug("deadline for %s" % (m.name))
                return m.deadline
        return 0

    def get_module_instances(self):
        return self.module_instances

    def get_all_instance_names(self):
        return self.module_instances + self.trigger_instances + self.dynamic_trigger_instances

    def get_module_implementations(self):
        return self.module_implementations

    def get_module_type(self, mtype):
        return self.module_types[mtype]

    def get_module_implementation(self, mimpl):
        return self.module_implementations[mimpl]

    def add_module_link(self, source, source_op, source_xml, target, target_op, target_xml, link_type):
        ml = Module_Link(source, source_op, source_xml, target, target_op, target_xml, link_type)
        self.links.append(ml)
        return ml

    def get_links(self):
        return self.links

    def get_libraries(self):
        return self.libraries

    def get_instance(self, instance_name):

        for instance in self.module_instances:
            if instance.get_name() == instance_name:
                return instance

        for instance in self.trigger_instances:
            if instance.get_name() == instance_name:
                return instance

        for instance in self.dynamic_trigger_instances:
            if instance.get_name() == instance_name:
                return instance
        return None

    def check_fill_mod_properties(self, libraries, component_type):
        """Check and fill module properties using component properties  and data types
        that have been declared in libraries

        Attributes:
            libraries              (dict): dictionary of class:`.Library`
            component_type (:class:`.Component_Type`): type of the component
        """
        for m_inst in self.module_instances:
            m_type = self.module_types[self.module_implementations[m_inst.implementation].type]
            m_inst.check_and_fill_properties(m_type, libraries, component_type)

    def find_module_type(self, mod_instance):
        """From a module instance name  find module type

        Attributes:
            mod_instance  (str): module instance name

        return:
            :class:`.Module_Type`
        """
        mod_inst = next(m for m in self.module_instances if m.name == mod_instance)
        mod_impl = self.module_implementations[mod_inst.implementation]
        return self.module_types[mod_impl.type]

    def find_module_operations(self, comp_op_name):
        """From a service or reference operation name find list of module operation names

        Attributes:
            comp_op_name  (str): name of the operation from a service or a reference

        Return:
            list of module operation names

        Note:
            Not used
        """

        mod_op_list = []
        for l in self.links:
            # find operation name and module name
            op_name = ""
            mod_name = ""
            if l.target_operation == comp_op_name and self.is_module_instance(l.source):
                op_name = l.source_operation
                mod_name = l.source
            elif l.source_operation == comp_op_name and self.is_module_instance(l.target):
                op_name = l.target_operation
                mod_name = l.target

            # find operation
            if op_name != "":
                operation = self.find_module_type(mod_name).operations[op_name]
                mod_op_list.append(operation)
        return mod_op_list

    def find_module_operations_from_name(self, mod_op_name):
        """From a module operation name find module operation

        Attributes:
            mod_op_name  (str): name of the operation from a module

        Return:
            module operation

        Note:
            Not used
        """
        for l in self.links:
            # find operation name and module name
            op_name = ""
            mod_name = ""
            if l.source_operation == mod_op_name and self.is_module_instance(l.source):
                op_name = l.source_operation
                mod_name = l.source
            elif l.target_operation == mod_op_name and self.is_module_instance(l.target):
                op_name = l.target_operation
                mod_name = l.target

            # find operation
            if op_name != "":
                return self.find_module_type(mod_name).operations[op_name]
        return None

    def has_external_c_links(self):
        """Check if component has a link with an external C driver

        Return:
            bool: True or False
        """
        has_external = False
        for link in self.links:
            has_external = has_external or link.is_external_c()
        return has_external

    def has_external_cpp_links(self):
        """Check if component has a link with an external C++ driver

        Return:
            bool: True or False
        """
        has_external = False
        for link in self.links:
            has_external = has_external or link.is_external_cpp()
        return has_external

    def has_external_links(self):
        """Check if component has a link with an external driver

        Return:
            bool: True or False
        """
        has_external = False
        for link in self.links:
            has_external = has_external or link.is_external()
        return has_external

    def to_string(self):
        string = ""
        string += "Component implementation: " + self.name + "\n"
        string += "  module types: " + str(
            [m_type.name for m_type in self.module_types.values()]) + "\n"
        string += "  module implementations: " + str(
            [m_impl.name for m_impl in self.module_implementations.values()]) + "\n"
        string += "  module instances: " + str(
            [m_inst.name for m_inst in self.module_instances]) + "\n"
        string += "  module trigger: " + str(
            [m_trig.name for m_trig in self.trigger_instances]) + "\n"
        string += "  module dyn trigger: " + str(
            [m_inst.name for m_inst in self.dynamic_trigger_instances]) + "\n"
        string += ""

        for m_type in self.module_types.values():
            string += "  Module type: " + str(m_type.name) + "\n"
            string += "   properties: " + str([p.name for p in m_type.properties.values()]) + "\n"
            string += "   operations: " + str([op.name for op in m_type.operations.values()]) + "\n"
        string += "\n"
        for m_inst in self.module_instances:
            string += "  Module inst: " + str(m_inst.name) + "\n"
            string += "   properties: " + str(
                [str(p) for p in m_inst.property_values.values()]) + "\n"
            string += "   in operations: "+str([str(op) for op in m_inst.entry_points_dict.values()]) + "\n"
            string += "   out operations: "+str([str(op) for op in m_inst.out_points_dict.values()]) + "\n"
        string += "VD: "+str(len(self.component_VDs))+"\n"

        return string

    def fill_pinfo_directory(self, integration_directory):
        """Fill pinfo directory of all pinfo modules

        Attributes:
            integration_directory     (str): The integration directory
        """
        for mod in self.module_instances:
            mod.fill_pinfo_directory(integration_directory, self.impl_directory, self.name)

    def find_connected_links(self, service_reference_name):
        """Find links that are connected with service/reference

        Attributes:
            service_reference_name (str): name of the service/reference

        Returns:
            list : list of connected :class:`.Link`
        """
        connected_links = []

        for l in self.links:
            if l.target == service_reference_name:
                connected_links.append(l)
            elif l.source == service_reference_name:
                connected_links.append(l)

        return connected_links

    def find_connected_links2(self, service_reference_name, service_op_name):
        """Find links that are connected with service/reference and the right operation

        Attributes:
            service_reference_name (str): name of the service/reference
            service_op_name        (str): name of the service/reference operation

        Returns:
            list : list of connected :class:`.Link`
        """
        connected_links = []

        for l in self.links:
            if l.target == service_reference_name and l.target_operation == service_op_name:
                connected_links.append(l)
            elif l.source == service_reference_name and l.source_operation == service_op_name:
                connected_links.append(l)

        # TODO add corner case: data update with no reader module
        return connected_links



    def find_VD_repository(self, op_name, mod_inst_name):
        for vd_repo in self.component_VDs:
            if mod_inst_name in vd_repo.readers_dict:
                for reader_op in vd_repo.readers_dict[mod_inst_name]:
                    if op_name == reader_op.op_name:
                        return vd_repo
            elif mod_inst_name in vd_repo.writters_dict:
                for writter_op in vd_repo.writters_dict[mod_inst_name]:
                    if op_name == writter_op.op_name:
                        return vd_repo
        return None


    def map_mod_VD_operations(self):
        # map VD operation of a module instance to the VD repository
        for mod_inst in self.module_instances:
            mod_type = self.find_module_type(mod_inst.name)
            for op in mod_type.operations.values():
                if op.type in ['DRN', 'DR']:
                    mod_inst.VD_read_op_map[op] = self.find_VD_repository(op.name, mod_inst.name)
                elif op.type == 'DW':
                    mod_inst.VD_written_op_map[op] = self.find_VD_repository(op.name, mod_inst.name)
