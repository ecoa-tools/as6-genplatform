# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..utilities.logs import debug, error, info, warning
from .PD_vd_repository import PD_vd_repository
from collections import OrderedDict


class Deployed_Module:
    """Instance of a deployed module in a protection domain

    Attributes:
        id              (int) : unique number. Use in UDP packet
        name            (str) : name of the deployed module
        component_name  (str) : name of component of the deployed module
        type            (str) : module type ('module' ou 'trigger')
    """
    id_counter = 0

    def __init__(self, name, component_name, mod_type):
        self.id = Deployed_Module.id_counter
        self.name = name
        self.component_name = component_name
        #self.index = -1 ??
        self.type = mod_type
        Deployed_Module.id_counter = Deployed_Module.id_counter + 1

    def __gt__(self, dep_mod):
        return self.id > dep_mod.id

    def get_name(self):
        return self.name

    def get_component_name(self):
        return self.component_name


class Protection_Domain:
    """Describes an instance of protection domain used within a deployment

    Attributes:
        id                (int) : unique number
        name              (str) : node identifier
        deployed_modules  (set) : set of :class:`.Deployed_Module` within the protection domain
        platform          (str) : name of the computing platform
        node              (str) : name of the computing node
        internal_wires_connection (dict) : :class:`.Wire` => [(link1, link2)],
                   tuple of 2 :class:`.Link` connected thanks to a Wire inside the Protection Domain
        external_wires_connection (dict) : :class:`.Wire` => [links], list of
                                                    :class:`.Link` not connected with a module in PD
        wire_server_socket_index  (dict) : :class:`.Wire` => socket index for this Wire
        wire_client_socket_index  (dict) : :class:`.Wire` => socket index for this Wire

        fine_grain_deployment (:class:`.Fine_Grain_Deployment`): fine grain deployment information.
            Could be None if protection domains are not deployed with this extention
        assembly_name       (str) : name of the final assembly composite which is deployed
        logical_system_name (str): name of the logical system which is used
    """
    id_counter = 0

    def __init__(self, name, platform, node, assembly_name, logical_system_name):
        self.name = name
        self.id = Protection_Domain.id_counter
        self.deployed_modules = set()
        self.assembly_name = assembly_name
        self.logical_system_name = logical_system_name
        self.platform = platform
        self.node = node
        self.fine_grain_deployment = None

        # wire => [(link1, link2)], tuple of links connected thanks to a wire inside PD
        self.internal_wires_connection = OrderedDict()
        # wire => [links], links not connected with a module in PD
        self.external_wires_connection = OrderedDict()

        self.external_PF_wires = OrderedDict() # wires connected with an other Platform
                                    # wire => [links], links not connected with a module in PD

        self.wire_server_socket_index = OrderedDict() # wire => socket index
        self.wire_client_socket_index = OrderedDict() # wire => socket index
        self.external_PF_sending_socket_index = OrderedDict() # PF_link_ID => socket index
        self.external_PF_reading_socket_index = OrderedDict() # binding_filename => (list(PF_link_id that are connected to this PD using the same binding))

        # PF_link_ID => dict of service syntax => dict of service operation name => list of wire
        self.ELI_input_operations = OrderedDict()

        Protection_Domain.id_counter = Protection_Domain.id_counter + 1

        self.VD_repositories = []

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def add_module(self, name, component_name, mod_type):
        md = Deployed_Module(name, component_name, mod_type)
        self.deployed_modules.add(md)
        return True

    def add_componentLog(self ,comp_name, log_levels):
        debug( "##########" + comp_name + " " +log_levels)

    def get_modules_number(self):
        return len(self.deployed_modules)

    def get_platform(self):
        return self.platform

    def get_node(self):
        return self.node

    def get_all_component_names(self):
        """Get the name of all components that are in this protection domain: get the name of
        component for each deployed modules.

        Returns:
            a set of component names.
        """
        comp_list = set()
        for m in self.deployed_modules:
            if m.component_name not in comp_list:
                comp_list.add(m.component_name)
        return sorted(comp_list)

    def get_all_component_implementations_name(self, components):
        """For each deployed modules, get the name of its component implementation.

        Args:
            components  (dict) : dictionary of :class:`.Component`

        Return:
            set of component implementation name
        """
        comp_impl_list = set()
        for m in self.deployed_modules:
            if components[m.component_name].get_component_implementation() not in comp_impl_list:
                comp_impl_list.add(components[m.component_name].get_component_implementation())
        return sorted(comp_impl_list)

    def check_protection_domain(self, components, component_implementations):
        """Check if the protection domain contains all modules of a components

        Note:
            All modules of a component should be deployed in the same protection domain

        Args:
            components                 (dict) : Dictionary of :class:`.Component` within the
                                                protection domain
            component_implementations  (dict) : Dictionary of :class:`.Component_Implementation`
                                                within the protection domain
        """
        ret_val = True
        comp_impl_list = self.get_all_component_implementations_name(components)
        deployed_mod_list = [m.name for m in self.deployed_modules]

        for comp_impl_name in comp_impl_list:
            for mod in component_implementations[comp_impl_name][0].module_instances \
                        + component_implementations[comp_impl_name][0].trigger_instances \
                        + component_implementations[comp_impl_name][0].dynamic_trigger_instances:
                if mod.name not in deployed_mod_list:
                    error("In module " +mod. name +" is not deployed in the right protection domain")
                    error("All modules of a component should be deployed in the same protection domain")
                    ret_val = False
        return ret_val

    def is_deployed_module(self, component_name, module_name):
        """Check if a Module Instance is deployed in this Protection Domaine

        Args:
            component_name  (str): component name
            module_name     (str): module instance name (belongs to the component)

        Return:
            True if module is deployed in this PD, False otherwise.
        """
        for d_mod in self.deployed_modules:
            if module_name == d_mod.name and component_name == d_mod.component_name:
                return True
        return False


    def set_fine_grain_deployment(self, fine_grain_deployment):
        self.fine_grain_deployment = fine_grain_deployment

    def get_scheduler_policy(self):
        policy = "OTHER" #default scheduler policy
        if self.fine_grain_deployment != None:
            policy = self.fine_grain_deployment.get_PD_sched_policy(self.name)
        return policy

    def set_deployed_mod_index(self, components, component_implementations):
        """Give an index to each normal deployed module, deployed trigger, deployed dynamic trigger
        For exemple: a deployed trigger and a deployed dynamic trigger could have the same index.
        But not 2 deployed triggers

        Args:
            components                (dict): dictionary of all :class:`.Component`
            component_implementations (dict): dictionary of all :class:`.Component_Implementation`
        """
        mod_index = 0
        trigger_index = 0
        dyn_trigger_index = 0
        for mod in sorted(self.deployed_modules):
            comp_impl = component_implementations[
                components[mod.component_name].component_implementation][0]
            if comp_impl.is_dynamic_trigger_instance(mod.name):
                mod.index = dyn_trigger_index
                dyn_trigger_index += 1
            elif comp_impl.is_trigger_instance(mod.name):
                mod.index = trigger_index
                trigger_index += 1
            elif comp_impl.is_module_instance(mod.name):
                mod.index = mod_index
                mod_index += 1

    def get_normal_deployed_module(self, components, component_implementations):
        """get all normal deployed module

        Args:
            components                (dict): dictionary of all :class:`.Component`
            component_implementations (dict): dictionary of all :class:`.Component_Implementation`
        """
        normal_deployed_mod = []
        for m in self.deployed_modules:
            comp_impl = component_implementations[
                components[m.component_name].component_implementation][0]
            if comp_impl.is_module_instance(m.name):
                normal_deployed_mod.append(m)
        return sorted(normal_deployed_mod)

    def get_dynamic_trigger_deployed_module(self, components, component_implementations):
        """get all deployed dynamic trigger

        Args:
            components                (dict): dictionary of all :class:`.Component`
            component_implementations (dict): dictionary of all :class:`.Component_Implementation`

        """
        dynamic_deployed_mod = []
        for m in self.deployed_modules:
            comp_impl = component_implementations[
                components[m.component_name].component_implementation][0]
            if comp_impl.is_dynamic_trigger_instance(m.name):
                dynamic_deployed_mod.append(m)
        return sorted(dynamic_deployed_mod)

    def get_trigger_deployed_module(self, components, component_implementations):
        """get all deployed trigger

        Args:
            components                (dict): dictionary of all :class:`.Component`
            component_implementations (dict): dictionary of all :class:`.Component_Implementation`
        """
        trigger_deployed_mod = []
        for m in self.deployed_modules:
            comp_impl = component_implementations[
                components[m.component_name].component_implementation][0]
            if comp_impl.is_trigger_instance(m.name):
                trigger_deployed_mod.append(m)
        return sorted(trigger_deployed_mod)

    def compute_buffer_pool_size(self, components, component_implementations):
        """Compute the size of the buffer pool

        Args:
            components                (dict): dictionary of all :class:`.Component`
            component_implementations (dict): dictionary of all :class:`.Component_Implementation`

        """
        buffer_pool_size = 2# minimal size
        for dep_mod in self.deployed_modules:
            comp_impl = component_implementations[
                components[dep_mod.component_name].component_implementation][0]
            buffer_pool_size += comp_impl.get_instance(dep_mod.name).fifo_size
        return buffer_pool_size

    def find_deployed_module(self, mod_instance_name, component_name):
        """Find a deployed modules

        Args:
            mod_instance_name (str): module instance name (belongs to the component)
            component_name    (str): component name

        returns:
            (:class:`Deployed_Module`): Found deployed module, or None if
            the module is not deployed here
        """
        for d_mod in self.deployed_modules:
            if d_mod.name == mod_instance_name and d_mod.component_name == component_name:
                return d_mod
        return None

    def _find_connected_links_wire(self, wire, comp_impl_source, comp_impl_target):
        # is internal if:
        #   * the source component has a link with a deployed module in this PD
        #   * and the target component has a link with a deployed module in this PD
        if comp_impl_source == None:
            connected_links_source = []
        else:
            connected_links_source = comp_impl_source.find_connected_links(wire.source_service)

        if comp_impl_target == None:
            connected_links_target = []
        else:
            connected_links_target = comp_impl_target.find_connected_links(wire.target_service)

        internal_connected_links = []
        external_connected_links = []
        for l in connected_links_source:
            if self.is_deployed_module(wire.source_component, l.target) \
                    or self.is_deployed_module(wire.source_component, l.source):
                internal_connected_links.append(l)
            else:
                external_connected_links.append(l)

        for l in connected_links_target:
            if self.is_deployed_module(wire.target_component, l.target) \
                    or self.is_deployed_module(wire.target_component, l.source):
                internal_connected_links.append(l)
            else:
                external_connected_links.append(l)

        return internal_connected_links, external_connected_links

    def find_internal_external_wires(self, wires, components, component_implementations):
        """for all wires, sort wires connected with components inside this protection
        domains and the other.
        Fill dictionaries:
        * internal_wires_connection
        * external_wires_connection

        Args:
            wires       (set): set of :class:`.Wire`
            components (dict): dictionary of :class:`.Component`
            component_implementations (dict): dictionary of :class:`.Component_Implementation`
        """
        for w in wires:
            # remove wire that are not connected with a component in the PD
            if w.target_component not in self.get_all_component_names() and\
               w.source_component not in self.get_all_component_names():
                   continue

            self.internal_wires_connection[w] = []
            self.external_wires_connection[w] = []

            if components[w.source_component].component_implementation == "":
                comp_impl_source = None
                #external plaform wire
            else:
                comp_impl_source = component_implementations[
                    components[w.source_component].component_implementation][0]

            if components[w.target_component].component_implementation == "":
                comp_impl_target = None
                #external plaform wire
            else:
                comp_impl_target = component_implementations[
                    components[w.target_component].component_implementation][0]

            internal_links, external_links = \
                self._find_connected_links_wire(w, comp_impl_source, comp_impl_target)

            # inside PD:
            for l in internal_links:
                # find 2 connected links with the same wire (inside the protection domaine)
                if l.target == w.source_service:
                    for l2 in internal_links:
                        if l2.source == w.target_service and l2 != l \
                                and l2.source_operation == l.target_operation:
                            self.internal_wires_connection[w].append((l, l2))
                elif l.target == w.target_service:
                    for l2 in internal_links:
                        if l2.source == w.source_service and l2 != l \
                                and l2.source_operation == l.target_operation:
                            self.internal_wires_connection[w].append((l, l2))

            # outside PD:
            if not w.is_map_on_PF_link():
                # In Platform:
                self.external_wires_connection[w] = external_links
                #detect connected wires but with no link in the connected component
                # (ie: if a side of a wire has no link)
                comp_list = self.get_all_component_names()
                if w.target_component not in comp_list or w.source_component not in comp_list:
                    if comp_impl_target.find_connected_links(w.target_service) == [] or\
                       comp_impl_source.find_connected_links(w.source_service) == []:
                        self.external_wires_connection[w] = []
                        warning("wire "+str(w)+" is connected to a service/reference with no link")
            else:
                # External PF wires
                self.external_PF_wires[w] = internal_links



    def set_sockets_index(self, PF_links, wire_mapping):
        """ Set socket indexes for each external wires of this protection domain
        Fill dictionaries:
        * wire_server_socket_index
        * wire_client_socket_index

        Warning:
            Only work if modules of component are deployed in the same PD
        """

        s_socket_index = 0
        c_socket_index = 0
        # for w, links in list(self.external_wires_connection.items())+list(self.external_PF_wires.items()):
        for w, links in self.external_wires_connection.items():
            if len(links) > 0:
                if w.source_component in self.get_all_component_names():
                    self.wire_server_socket_index[w] = s_socket_index
                    s_socket_index += 1
                elif w.target_component in self.get_all_component_names():
                    self.wire_client_socket_index[w] = c_socket_index
                    c_socket_index += 1
            else:
                #no link connected to this wire on one side or the other one
                pass

        # external wire
        for pf_link_id in PF_links.keys():
            # Check if a wire connected to the PD is mapped on this PF_link:
            if pf_link_id not in wire_mapping:
                continue
            for w in self.external_PF_wires.keys():
                if w in wire_mapping[pf_link_id]:
                    self.external_PF_sending_socket_index[pf_link_id] = s_socket_index
                    s_socket_index += 1
                    break

        self.external_PF_reading_socket_index = OrderedDict()
        for pf_link_id, pf_link in PF_links.items():
            # Check if a wire connected to the PD is mapped on this PF_link
            if pf_link_id not in self.external_PF_sending_socket_index:
                #pf link is connected to any wires with this PD
                continue

            binding_filename = pf_link.link_binding.filename
            if binding_filename not in self.external_PF_reading_socket_index:
                self.external_PF_reading_socket_index[binding_filename] = []
            self.external_PF_reading_socket_index[binding_filename].append(pf_link_id)


    def find_ELI_input_operation(self, PF_links):
        # PF_link_ID => dict of syntax => dict of service operation => list of wires
        # for every platform links that are connected
        for PF_link_id in self.external_PF_sending_socket_index.keys():
            if PF_link_id not in self.ELI_input_operations:
                self.ELI_input_operations[PF_link_id]=OrderedDict()

            pf_link= PF_links[PF_link_id]

            #for every service syntax in this PF _link
            for service_syntax, wires_tmp in pf_link.service_syntax.items():
                if service_syntax.name not in self.ELI_input_operations[PF_link_id]:
                    self.ELI_input_operations[PF_link_id][service_syntax.name] = OrderedDict()

                # select only wires that are connected to this PD:
                connected_wires = [w for w in wires_tmp if w in list(self.external_PF_wires.keys())]

                # sort wires for each operation by cross_PF_ID:
                # find cross PF id for every service operations:
                for w in connected_wires:
                    PD_is_client = (w.target_component in self.get_all_component_names())
                    for op_name in service_syntax.find_input_operation(PD_is_client):
                        if op_name not in self.ELI_input_operations[PF_link_id][service_syntax.name]:
                            self.ELI_input_operations[PF_link_id][service_syntax.name][op_name] = []

                        self.ELI_input_operations[PF_link_id][service_syntax.name][op_name].append(w)


    def find_links_inside_PD(self, components, component_implementations):
        """find internal links : links between 2 deployed modules or one deployed module and
        a reference/service

        Note:
            Currently not use
        """

        self.links_inside = []
        for comp in components.values():
            comp_impl, _ = component_implementations[comp.component_implementation]
            for l in comp_impl.links:
                source_is_mod = comp_impl.is_generic_module_instance(l.source)
                target_is_mod = comp_impl.is_generic_module_instance(l.target)

                if source_is_mod and target_is_mod \
                   and self.is_deployed_module(comp.name, l.source) \
                   and self.is_deployed_module(comp.name, l.target):
                   # both source and target are modules and are deployed
                    self.links_inside.append(l)
                elif source_is_mod and not target_is_mod \
                   and self.is_deployed_module(comp.name, l.source):
                   # both source is a module and is deployed
                    self.links_inside.append(l)
                elif target_is_mod and not source_is_mod \
                   and self.is_deployed_module(comp.name, l.target):
                   # both target is a module and is deployed
                    self.links_inside.append(l)

    def find_VD_repository(self, components, comp_implementations, component_types, wires, wire_mapping):
        """Find VD repository to create in this Protection Domain.

        Attributes:
            components           (dict): The dictionary of components
            comp_implementations (dict): The dictionary of component implementations
            wires                (lsit): The list of wires

        @return     { description_of_the_return_value }
        """
        pd_vd_index = 0
        for comp_name in self.get_all_component_names():
            comp = components[comp_name]
            comp_impl,_ = comp_implementations[comp.component_implementation]
            for vd in comp_impl.component_VDs:
                # for every component VD, create a VD repository in PD
                # (Can be optimized to reduce the number of VD repository :
                #  In some case, VD repository can be merged)
                new_PD_vd_repo = PD_vd_repository(comp, vd, pd_vd_index)

                self.VD_repositories.append(new_PD_vd_repo)
                pd_vd_index += 1

        for vd_repo in self.VD_repositories:
            vd_repo.compute_written_copies()
            # for every VD repository created, found readers to notify
            vd_repo.find_readers(self, wires, components, component_types, wire_mapping)

    def find_connected_vd_repo(self, comp, comp_impl_vd):
        for vd in self.VD_repositories:
            for c, c_impl_vd in vd.list_comp_impl_VD:
                if c == comp and c_impl_vd == comp_impl_vd:
                    return vd
        return None

    def reduce_vd_repo_number(self):
        """reduce number of repository when it is possible.
        Conditions to merge one repositoty  A in an other one B when A can publish in B:
        - B should have only one writters : the A repository
        - A and B should have the same mode (Controlled)
        """

        # find merge VD repo
        vd_index_to_removed = []
        already_merged=set()
        for vd_repo in self.VD_repositories[:]:
            if vd_repo in already_merged:
                continue

            already_merged.add(vd_repo)
            for index, (w,reader_repo) in enumerate(vd_repo.notified_local_repo[:]):
                # the other merged repos should complete the merged condition:
                reader_comp, comp_impl_VD = reader_repo.list_comp_impl_VD[0]

                # check condition:
                if len(comp_impl_VD.writters_dict) == 1 \
                   and comp_impl_VD.get_VD_access_mode() == vd_repo.get_vd_access_mode():
                    info("merge VD : index %i => %i" % (reader_repo.pd_vd_index, vd_repo.pd_vd_index))
                    vd_repo.merge_VD(reader_repo, w)
                    already_merged.add(reader_repo)
                    vd_index_to_removed.append(reader_repo.pd_vd_index)

        # recompute vd repository index and reader number
        self.VD_repositories = [x for x in self.VD_repositories if x.pd_vd_index not in vd_index_to_removed]

        info("[%s], reduce number of repository by %i" % (self.name, len(vd_index_to_removed)))
        for index,vd_repo in enumerate(self.VD_repositories):
            vd_repo.pd_vd_index = index
            vd_repo.compute_notified_reader()
            debug(str(vd_repo))

    ############################################################
    ### TO DEBUG
    def _find_external_link(self, components, component_implementations):
        ## find link connected directly with a module outside the PD (without wire)
        self.external_M_to_M_links = []
        for comp in components.values():
            comp_impl, _ = component_implementations[comp.component_implementation]
            for l in comp_impl.links:
                if comp_impl.is_generic_module_instance(l.source) \
                        and comp_impl.is_generic_module_instance(l.target):
                    source_is_deployed = self.is_deployed_module(comp.name, l.source)
                    target_is_deployed = self.is_deployed_module(comp.name, l.target)
                    if (source_is_deployed and not target_is_deployed) or (not source_is_deployed
                                                                           and target_is_deployed):
                        # if one module is deployed in this PD and the other is not
                        self.external_M_to_M_links.append(l)


    def display_info(self, wires, components, component_implementations):
        self._find_external_link(components, component_implementations)
        print("\n======================="+self.name)
        print("external connection:")
        for w, links in self.external_wires_connection.items():
            if len(links) > 0:
                print("   - "+str(w) + " => {"+ w.name() + "_port, " + w.name() + "_addr, NULL}")
            else:
                print("   - "+str(w) + " => no link connected on one side of this wire")
        for l in self.external_M_to_M_links:
            print("   -"+str(l)+" => create TCP")


        for d_mod in self.deployed_modules:
            comp = components[d_mod.component_name]
            comp_impl, _ = component_implementations[comp.component_implementation]
            mod_inst = comp_impl.get_instance(d_mod.name)

            if comp_impl.is_module_instance(mod_inst.name):
                mod_impl = comp_impl.module_implementations[mod_inst.implementation]
                mod_type = comp_impl.module_types[mod_impl.type]
                print(" ==  deployed module instance : "+mod_inst.name+" (type : "
                      +mod_type.name+", impl : "+mod_impl.name+")")

                for op_name in mod_inst.out_points_dict.keys():
                    op = mod_type.operations[op_name]
                    print("   -- out op : "+str(op))



                    for l in mod_inst.out_points_dict[op_name]:
                        print("          "+str(l))
                        ## find direct module in same comp and check if it is deployed
                        ## find connected wire
                        ##   - direct
                        ##   - not direct
                        if comp_impl.is_generic_module_instance(l.target):
                            if self.is_deployed_module(comp.name, l.target):
                                ## direct push
                                print("            direct : "+comp.name+" "+ l.target)
                            else:
                                ## not direct
                                print("not yet implemented ")
                                assert 0
                        else:
                            # find wires
                            connected_wires = l.find_connected_wires_link(comp.name, wires)
                            for w in connected_wires:
                                # for inside link
                                for l1, l2 in self.internal_wires_connection[w]:
                                    if l1 == l:
                                        print("            direct : "+w.target_component+" "
                                              + l2.target)
                                for l1 in self.external_wires_connection[w]:
                                    if w in self.wire_client_socket_index:
                                        print("            TCP index: "
                                              + str(self.wire_client_socket_index[w])+" on wire :"
                                              +str(w)+" to link:"+str(l1))
                                    elif w in self.wire_server_socket_index:
                                        print("            TCP index: "
                                              + str(self.wire_server_socket_index[w])+" on wire :"
                                              +str(w)+" to link:"+str(l1))
                                    else:
                                        print("            No index: wire not connected to link : "+str(w))

                            if len(connected_wires) == 0:
                                print("ERROR")

                for op_name in mod_inst.entry_points_dict.keys():
                    op = mod_type.operations[op_name]
                    print("   -- in op : "+str(op))
                    for l in mod_inst.entry_points_dict[op_name]:
                        print("          "+str(l))

        print("=======================\n")
