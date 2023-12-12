# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .component_VD import vd_reader, vd_reader_module

class PD_vd_repository:
    """Structure that describe a versioned data repository of a Protection Domain

    Attributes:
        component    (:class:`.Component`)   : component that belongs this repository
        comp_impl_VD (:class:`.component_VD`): component VD of this repository
        pd_vd_index              (int): index of this repository in PD
        num_written_copies       (int): number of requiered copies in written access
        notified_modules        (list): list of :class:`.vd_reader_module` that can read in this repository
        notified_local_sockets  (list): list of :class:`.vd_reader` that are socekts inside the same node
        notified_local_repo     (list): list of :class:`.vd_reader` that are an other repository inside the PD
        notified_ext_sockets    (list): list of :class:`.vd_reader` that are socekts outside the node
        num_notified_readers     (int): total number of reader


    """
    def __init__(self, component, comp_impl_VD, pd_vd_index):
        # self.component = component
        # self.comp_impl_VD = comp_impl_VD

        self.list_comp_impl_VD = [(component, comp_impl_VD)] # list of (component, comp_impl_VD)

        self.pd_vd_index = pd_vd_index
        self.num_written_copies = 0

        self.notified_modules = {component.name:[]}
        self.notified_local_sockets = {component.name:[]}
        self.notified_local_repo = []
        self.notified_ext_sockets = []

        self.num_notified_readers = 0

        self.serialisation_fct_name = "NULL"

    def get_vd_datatype(self):
        return self.list_comp_impl_VD[0][1].data_type

    def get_vd_access_mode(self):
        return self.list_comp_impl_VD[0][1].get_VD_access_mode()

    def compute_written_copies(self):
        self.num_written_copies = 0
        if self.list_comp_impl_VD[0][1].accessControl:
            self.num_written_copies = 1 # one copy for router thread access when a socket publishes
            for comp, comp_imp_vd in self.list_comp_impl_VD:
                self.num_written_copies += comp_imp_vd.num_written_copies
        else:
            # Without access control
            self.num_written_copies = 1

    def find_notified_modules(self):
        """Find modules that need to be notifyed
        """
        for comp, comp_impl_vd in self.list_comp_impl_VD:
            for reader in comp_impl_vd.get_readers():
                if type(reader) == vd_reader_module and reader.to_be_notified:
                    self.notified_modules[comp.name].append(reader)

    def find_readers(self, protection_domain, wires, components, component_types, wire_mapping):
        """Find readers that need to be notify. Reader can be a module, a local socket (in node) or an external socket.

        Attributes:
            protection_domain  (:class:`.Protection_Domain`): The Protection Domain of the VD repository
            wires              (list): list of all wires
            components         (dict): Dictionary of :class:`.Component`

        """

        # find modules to notify
        self.find_notified_modules()

        # find local and external sockets and local repo to notify
        for comp, comp_impl_vd in self.list_comp_impl_VD:
            service_readers_names = [r.name for r in comp_impl_vd.get_readers() if type(r) == vd_reader]
            connected_wires = [ w for w in wires if w.target_component == comp.name
                                                and w.target_service in service_readers_names]

            for w in connected_wires:
                for reader in [r for r in comp_impl_vd.get_readers() if r.name == w.target_service]:
                    if protection_domain.external_wires_connection[w] != []:
                        # external wire
                        # TODO check if it is an node external wire or not
                        # by default node internal wire:
                        self.notified_local_sockets[comp.name].append((w, reader))
                    elif w in protection_domain.external_PF_wires:
                        for pf_link_id_tmp in wire_mapping.keys():
                            if w in wire_mapping[pf_link_id_tmp]:
                                pf_link_id = pf_link_id_tmp
                                break;
                        self.notified_ext_sockets.append((w, reader,pf_link_id))

                        # find serialised function name
                        comp_t = component_types[comp.component_type][0]
                        svc_syntax = next(s.syntax for s in comp_t.services  if s.name == reader.name)
                        # all external PF readers have the same data type
                        # So it is possible to use the serialisation function of an arbitrary readers
                        self.serialisation_fct_name = "serialized_" + svc_syntax+"_"+reader.op_name

                    else:
                        #internal wire (internal PD)
                        reader_comp = components[w.source_component]
                        reader_service = w.source_service
                        reader_op_name = reader.op_name

                        # find connected PD_vd_repository
                        for pd_vd in protection_domain.VD_repositories:
                            if pd_vd.is_writter(reader_service, reader_op_name, reader_comp.name):

                                self.notified_local_repo.append((w,pd_vd))

    def compute_notified_reader(self):
        """Compute the number of reader to notify
        """
        self.num_notified_readers = 0
        self.num_notified_readers += len(self.notified_local_repo)
        self.num_notified_readers += len(self.notified_ext_sockets)

        for comp,module_list in self.notified_modules.items():
            self.num_notified_readers += len(module_list)
        for  comp,socket_list in self.notified_local_sockets.items():
            self.num_notified_readers += len(socket_list)

    def is_writter(self, writter_name, op_name, component_name):
        """ Check if a module/service instance is a writer in this VD repository for an operation

        Attributes:
            writter_name (str): The writter name
            op_name      (str): The operation name

        Return:
            (bool): True if it is writter, False otherwise.
        """
        for comp, comp_impl_vd in self.list_comp_impl_VD:
            # print("= "+component_name+" "+ writter_name+" = "+comp.name +" "+str(comp_impl_vd.writters_dict.keys()))
            if writter_name in comp_impl_vd.writters_dict and component_name == comp.name:
                for w_op in  comp_impl_vd.writters_dict[writter_name]:
                    if op_name == w_op.op_name:
                        return True
        return False

    def is_in_vd_repo(self, component, comp_impl_VD):
        for comp, c_impl_vd in self.list_comp_impl_VD:
            if comp == component and comp_impl_VD == c_impl_vd:
                return True

        return False

    def merge_VD(self, other_repo, other_wire):
        """Merge one VD repository in an other one

        Attributes:
            other_repo (:class:`.PD_vd_repository`): The repo to merge
            other_wire (:class:`.Wire`): The wire that connects the 2 repo
        """
        for other_repo_comp, other_comp_impl_VD in other_repo.list_comp_impl_VD:
            if (other_repo_comp, other_comp_impl_VD) in self.list_comp_impl_VD:
                # already merge
                continue

            self.list_comp_impl_VD.append((other_repo_comp, other_comp_impl_VD))

            # remove repo to notify
            self.notified_local_repo.remove((other_wire,other_repo))

            # merge module list
            if other_repo_comp.name not in self.notified_modules:
                self.notified_modules[other_repo_comp.name] = []
            self.notified_modules[other_repo_comp.name] += other_repo.notified_modules[other_repo_comp.name]

            # merge local socket list
            if other_repo_comp.name not in self.notified_local_sockets:
                self.notified_local_sockets[other_repo_comp.name] = []
            self.notified_local_sockets[other_repo_comp.name] += other_repo.notified_local_sockets[other_repo_comp.name]

            # merge local repo list
            self.notified_local_repo += other_repo.notified_local_repo

            # merge external repo list
            self.notified_ext_sockets += other_repo.notified_ext_sockets

    def __str__(self):
        string = "VD repo. index: %i, num_reader: %i\n" %(self.pd_vd_index, self.num_notified_readers)
        string += "  %i extern sockets  \n" %(len(self.notified_ext_sockets))
        string += "  %i local repo" %(len(self.notified_local_repo))
        string += " with index : "+str([vd.pd_vd_index for _,vd in self.notified_local_repo ])+"\n"
        string += "  %i comp impl VD :\n" % (len(self.list_comp_impl_VD))
        for comp, _ in self.list_comp_impl_VD:
            string += "   "+comp.name+"\n"
            string += "    notified mod: "+str([m.name for m in self.notified_modules[comp.name]])+"\n"
            string += "    local socket: "+str([m.name for _,m in self.notified_local_sockets[comp.name]])+"\n"
        return string+"\n"

