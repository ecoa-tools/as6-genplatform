# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
import sys
import logging
from collections import OrderedDict

from .utilities.logs import init_logs, info, logger_resume, error, warning
from ecoa.utilities.process import execute

from .parsers.project_parser import ECOAProject
from .parsers.composite_parser import check_final_composite, check_upper_composite, parse_composite, \
    check_intial_composite
from .parsers.library_parser import parse_all_libraries
from .parsers.logicalsystem_parser import parse_all_logicalsystem
from .parsers.euid_parser import parse_all_EUID
from .parsers.cross_PF_view_parser import parse_cross_PF_view, check_cross_PF_view

from .parsers.component_implementation_parser import parse_component_implementations, \
    check_all_component_implementations
from .parsers.component_type_parser import parse_component_types, check_component_types
from .parsers.service_parser import parse_service_definitions
from .parsers.deployment_parser import parse_deployment_files, check_wire_mapping, check_deployment
from .parsers.bin_desc_parser import parse_all_binary_desc
from .parsers.fine_grain_deployment_parser import parse_fine_grain_deployment, \
    check_file_grain_deployment
from .parsers.ip_address_deployment_parser import parse_ip_address_deployment, check_ip_deployment
from .parsers.nodes_deployment_parser import parse_nodes_deployment, check_nodes_deployment
from .models.composite import Composite

from .utilities.euid_generator import find_IDs, generate_IDs, generate_EUID_keys, \
    check_cross_PF_IDs_consistency


class ECOA_Global_Config:
    """
    @brief      main class that contains all configuration information to generate a platform
    """

    def __init__(self, working_directory, platform_config_file, index=0,
                 verbosity=3, level=5):
        """

        :param working_directory:
        :type working_directory:
        :param platform_config_file:
        :type platform_config_file:
        """

        self.libraries = OrderedDict()
        self.component_types = OrderedDict()
        self.component_implementations = OrderedDict()
        self.service_definitions = OrderedDict()

        # composites
        # [TODO : add in a list of composite object for multi-composites support (= multi assembly files)]
        self.final_assembly_composite = None  # composite of the final assembly

        # protection domains
        # [TODO : add in a list of deployment object for multi-composites support]
        self.deployment = None

        # Platforms
        # [TODO : add in a list of logical system object for multi logical-system support]
        self.logical_system = None  # deployment file depends on a logical system
        # Actually only one deployment file is supported. Consequently ldp support only a unique
        # assembly schema (unique composite) and a unique logical system file

        self.IDs = OrderedDict()

        # project configuration
        self.working_directory = working_directory
        self.platform_config_file = platform_config_file
        self.instance_index = index

        # cross Platform view : not necessary to generate a PF
        self.platform_composites = OrderedDict()  # platforms composites defined in Initial Assembly
        self.cross_PF_view = None
        self.upper_composite = None

        # Multi nodes
        self.nodes_deployment = None

        # Validation level
        self.validation_level = level

        self.ECOAProject = ECOAProject(self.platform_config_file)

        init_logs(verbosity)

    def set_instance_index(self, new_index):
        self.instance_index = new_index

    def end(self):
        return logger_resume()

    def parse_output(self, output, xsd_directory=None):
        info("=============== OUTPUT DIRECTORY")

        info(" == Set Output directory")
        l_status = self.ECOAProject.parse_output(output, xsd_directory)

        info("=============== Completed\n\n")
        return l_status

    def do_external_validation(self, checker, project):
        code, output, _ = execute("{} -p {}".format(checker, project))
        print(output.decode("utf-8"))
        sys.stdout.flush()
        return code == 0

    def do_validation(self, xsd_directory, generate_ids_file=True):
        logging.disable(level=logging.CRITICAL)
        self.do_parsing(xsd_directory)
        self.build_model(generate_ids_file)
        logging.disable(level=logging.NOTSET)

    def __check_svc_and_ref_consistency(self):
        for n, c in self.final_assembly_composite.components.items():
            # in case of inconsistency in implementation files
            l_impl = c.get_component_implementation()
            if l_impl in self.component_implementations:
                for c_link in self.component_implementations[l_impl][0].links:
                    if c_link.type == "event":
                        l_message = "{0} '{1}:{2}' is not defined as {0} in the component definition"
                        if c_link.source_xml == "service" and c_link.source not in c.services:
                            error(l_message.format("service", c_link.source, c_link.source_operation))
                        if c_link.source_xml == "reference" and c_link.source not in c.references:
                            error(l_message.format("reference", c_link.source, c_link.source_operation))
                        if c_link.target_xml == "service" and c_link.target not in c.services:
                            error(l_message.format("service", c_link.target, c_link.target_operation))
                        if c_link.target_xml == "reference" and c_link.target not in c.references:
                            error(l_message.format("reference", c_link.target, c_link.target_operation))

    def __parse_assembly_and_deployment(self, xsd_directory):
        info(" == Parse Final Assembly composite files ")
        if len(self.ECOAProject.impl_assembly_files) == 0:
            error(" No final assembly file")
        else:
            self.final_assembly_composite = parse_composite(xsd_directory,
                                                            list(self.ECOAProject.impl_assembly_files)[0],
                                                            self.libraries)

        if not self.final_assembly_composite:
            error(" No final assembly composite")

            return False
        else:
            # Check EventLink service and reference consistency
            self.__check_svc_and_ref_consistency()

        info(" == Parse logical system")
        self.logical_system = parse_all_logicalsystem(xsd_directory,
                                                      self.ECOAProject.logical_system_files)
        if not self.logical_system:
            error(" No logical System")
            return False

        info(" == Parse deployment files")
        self.deployment = parse_deployment_files(xsd_directory,
                                                 self.ECOAProject.deployment_files,
                                                 self.final_assembly_composite,
                                                 self.logical_system)
        if not self.deployment:
            error(" No deployment files")
            return False

        return True

    def __check_assembly_and_deployment(self):
        check_deployment(self.deployment, self.final_assembly_composite,
                         self.component_implementations, self.logical_system)

        info(" == Check final assembly '%s'" % self.final_assembly_composite.name)
        check_final_composite(self.final_assembly_composite.components, self.component_types,
                              self.final_assembly_composite.wires,
                              self.final_assembly_composite.properties, self.libraries)

        # check consistency between component-component_type-component_implementation
        info(" == Check component-component_type-component_implementation consistency")
        check_all_component_implementations(self.final_assembly_composite.components,
                                            self.component_implementations,
                                            self.component_types,
                                            self.service_definitions,
                                            self.libraries)

        info(" == Check wire mapping of logical system '%s'"
             % self.logical_system.name)
        check_wire_mapping(self.deployment.wire_mapping, self.logical_system.platform_links,
                           self.final_assembly_composite.wires)

    def __parse_cross_platform(self, xsd_directory):
        info(" == Parse cross platforms view")
        self.cross_PF_view = parse_cross_PF_view(xsd_directory, self.ECOAProject.crossplatform_files)

        if len(self.ECOAProject.crossplatform_files) != 0:
            cross_PF_view_dir = os.path.dirname(list(self.ECOAProject.crossplatform_files)[0])
            upper_composite_file = os.path.join(cross_PF_view_dir, "upper.impl.composite")
            self.upper_composite = parse_composite(xsd_directory, upper_composite_file,
                                                   self.libraries)
            check_upper_composite(self.upper_composite, self.service_definitions, self.platform_composites)

        if not self.upper_composite:
            # create an empty upper composite (in case of error or in case of single platform)
            self.upper_composite = Composite("upper")

        check_cross_PF_view(self.cross_PF_view, self.logical_system.platform_links,
                            self.logical_system.platforms, self.upper_composite)

    def __parse_optional_integration(self, xsd_directory):
        self.integration_directory = os.path.dirname(list(self.ECOAProject.deployment_files)[0])
        self.fine_grain_deployment = parse_fine_grain_deployment(self.integration_directory, xsd_directory)
        if not check_file_grain_deployment(self.fine_grain_deployment, self.deployment.protection_domains):
            pass

        self.ip_address_directory = os.path.dirname(list(self.ECOAProject.deployment_files)[0])
        self.ip_address_deployment = parse_ip_address_deployment(self.ip_address_directory, xsd_directory)
        if not check_ip_deployment(self.ip_address_deployment, self.deployment.protection_domains):
            pass

        if self.deployment.multi_node:
            info(" == Parse Nodes deployment files")
            self.nodes_directory = os.path.dirname(list(self.ECOAProject.deployment_files)[0])
            self.nodes_deployment = parse_nodes_deployment(self.nodes_directory, xsd_directory)
            if not check_nodes_deployment(self.nodes_deployment, self.deployment.protection_domains):
                pass

    def __parse_integration(self, xsd_directory):
        # Parse assembly and deployment
        if not self.__parse_assembly_and_deployment(xsd_directory):
            return False

        # Check assembly and deployment
        self.__check_assembly_and_deployment()

        # Parse cross platform
        self.__parse_cross_platform(xsd_directory)

        info(" == Parse EUIDs")
        parse_all_EUID(xsd_directory,
                       self.ECOAProject.EUID_files,
                       self.IDs)

        # Parse optional files in 5-integration
        self.__parse_optional_integration(xsd_directory)

        # TODO : move in build_model ???
        if len(self.libraries) > 1:
            # if a library is defined, use the directory of this library to generated files for type
            # (ie: serialization, headers,...)
            lib = next(l for l, _ in self.libraries.values() if l.name != 'ECOA')
            self.types_output_dir = lib.libfile_directory
        else:
            # default path
            self.types_output_dir = os.path.join(self.ECOAProject.output_dir, "0-Types")
        self.PF_output_dir = os.path.join(self.ECOAProject.output_dir, "platform")

        return True

    def do_parsing(self, xsd_directory):
        info("=============== PARSER")
        l_status = True
        self.ECOAProject.parse_project(xsd_directory)

        info(" == Parse libraries")
        parse_all_libraries(xsd_directory,
                            self.ECOAProject.type_files,
                            self.libraries)

        if self.validation_level >= 1:
            info(" == Parse service definitions")
            parse_service_definitions(xsd_directory,
                                      self.ECOAProject.service_files,
                                      self.service_definitions,
                                      self.libraries)

        if self.validation_level >= 2:
            info(" == Parse component types in")
            parse_component_types(xsd_directory,
                                  self.ECOAProject.component_files,
                                  self.component_types,
                                  self.libraries)
            check_component_types(self.component_types, self.service_definitions,
                                  self.libraries)

        if self.validation_level >= 4:
            info(" == Parse component implementations")
            parse_component_implementations(xsd_directory,
                                            self.ECOAProject.comp_impl_files,
                                            self.component_implementations,
                                            self.libraries)

            info(" == Parse binary descriptions")
            parse_all_binary_desc(xsd_directory, self.component_implementations)

        if self.validation_level >= 3:
            info(" == Parse Initial Assembly files")
            for file in self.ECOAProject.init_assembly_files:
                new_composite = parse_composite(xsd_directory, file, self.libraries)
                if new_composite:
                    self.platform_composites[new_composite.name] = new_composite
                    check_intial_composite(new_composite, self.component_types, self.libraries)

        if self.validation_level >= 5:
            l_status = self.__parse_integration(xsd_directory)

        info("=============== Completed\n\n")
        return l_status

    def build_model(self, generate_ids_file=True):
        if self.validation_level < 5:
            return False

        if not self.deployment or not self.final_assembly_composite or not self.logical_system:
            return False

        info("=============== BUILD MODEL")
        self.current_PF_name = ""
        if len(self.deployment.protection_domains) > 0:
            self.current_PF_name = next(
                iter(self.deployment.protection_domains.values())).platform  # name of the PF of the first PD

        # Wires mapping
        for w in self.final_assembly_composite.wires:
            w.set_wire_mapping(self.deployment.wire_mapping)

        # find platform link for platform messages
        for pf in self.logical_system.platforms.values():
            if pf.name in self.deployment.platforms_config:
                pf.platform_message_link = self.deployment.platforms_config[pf.name].platform_message_link
            if pf.platform_message_link == "":
                # find default link for plaform messages
                pass

        # Platform link services
        for PF_link_id, PF_link in self.logical_system.platform_links.items():
            PF_link.find_services_wires(self.deployment.wire_mapping,
                                        self.final_assembly_composite.components,
                                        self.component_types,
                                        self.service_definitions)

        # build multi platforms model
        for pf in self.logical_system.platforms.values():
            pf.set_composite_name(self.cross_PF_view.find_composite_name(pf.name))
            pf.set_composite_impl_name(self.upper_composite)

        # generate Cross PF EUIDs (define in cross pf file):
        if not self.upper_composite.is_empty:
            missing_EUIDs = self.cross_PF_view.find_missing_EUIDs(self.upper_composite, self.service_definitions)

            # generate missing binding files
            for binding_file, ID_keys in missing_EUIDs.items():
                new_IDs = generate_EUID_keys(ID_keys)
                generate_IDs(new_IDs, binding_file)
                self.cross_PF_view.EUIDs[binding_file].update(new_IDs)

        # check consistency between cross PF ID and project IDs (define in project EUIDs files)
        new_IDs_to_generate = OrderedDict()
        for w in self.final_assembly_composite.wires:
            if w.is_map_on_PF_link():
                syntax = w.find_service_syntax(self.final_assembly_composite.components,
                                               self.component_types, self.service_definitions)
                other_pf_name = self.logical_system.platform_links[w.PF_link_id].get_other_platform(
                    self.current_PF_name)
                current_pf_composite_type = self.logical_system.platforms[self.current_PF_name].find_PF_composite_type(
                    self.cross_PF_view,
                    self.upper_composite, self.platform_composites)

                if current_pf_composite_type is None:
                    warning("Cannot check IDs of wire '%s' (PF composite type not found)" % w)
                    continue

                new_IDs_tmp = check_cross_PF_IDs_consistency(w, syntax, self.current_PF_name, other_pf_name,
                                                             current_pf_composite_type,
                                                             self.final_assembly_composite.components,
                                                             self.cross_PF_view, self.IDs)
                new_IDs_to_generate.update(new_IDs_tmp)
        self.IDs.update(new_IDs_to_generate)

        # Update project IDs (used in generated code):
        new_IDs_tmp = find_IDs(self.IDs,
                               self.final_assembly_composite.wires,
                               self.final_assembly_composite.components,
                               self.component_types, self.service_definitions)
        new_IDs_to_generate.update(new_IDs_tmp)

        if generate_ids_file:
            # generate local missing IDs
            if len(self.ECOAProject.EUID_files) > 0:
                default_ID_filename = list(self.ECOAProject.EUID_files)[0]
            else:
                default_ID_filename = os.path.join(self.integration_directory,
                                                   self.ECOAProject.project_name + ".ids.xml")
            generate_IDs(new_IDs_to_generate, default_ID_filename)
        self.IDs.update(new_IDs_to_generate)

        # fill information of component implementations
        for comp_impl, _ in self.component_implementations.values():
            comp_impl.fill_module_inst_info()
            comp_impl.fill_trigger_info()
            comp_impl.fill_dynamic_trigger_info()
            comp_impl.set_mod_fifo_sizes()
            comp_impl.compute_buffer_pool_size()

        # Priorities relocation:
        #  Aggregate all priorities in deployed modules
        node_priorities = dict()
        for dp in self.deployment.protection_domains.values():
            for dm in dp.deployed_modules:
                cn = self.final_assembly_composite.components[dm.component_name]
                priority = cn.mod_priority[dm.name]
                if dp.node not in node_priorities:
                    node_priorities[dp.node] = set()
                node_priorities[dp.node].add(priority)
        for n, s in node_priorities.items():
            node_priorities[n] = sorted(s)

        # compute relocated priority for each module
        for cn in self.final_assembly_composite.components.values():
            for m, p in cn.mod_priority.items():
                node = cn.mod_node[m]
                priorities_node = node_priorities[node]
                # let's the most priority for internal use
                relocated_priority = 1 + priorities_node.index(p)
                cn.mod_set_relocated_priority(m, relocated_priority)

        # Properties
        for comp_impl, _ in self.component_implementations.values():
            # do it only if component_impl is used in a component
            for comp_inst in self.final_assembly_composite.components.values():
                if comp_inst.component_implementation == comp_impl.name:
                    comp_type, _ = self.component_types[comp_inst.component_type]
                    comp_impl.check_fill_mod_properties(self.libraries, comp_type)

        # Pinfo
        for comp_impl, _ in self.component_implementations.values():
            comp_impl.fill_pinfo_directory(self.integration_directory)

        # PD
        for pd in self.deployment.protection_domains.values():
            pd.find_internal_external_wires(self.final_assembly_composite.wires,
                                            self.final_assembly_composite.components,
                                            self.component_implementations)

            pd.find_VD_repository(self.final_assembly_composite.components,
                                  self.component_implementations, self.component_types,
                                  self.final_assembly_composite.wires, self.deployment.wire_mapping)
            pd.reduce_vd_repo_number()

            pd.set_sockets_index(self.logical_system.platform_links, self.deployment.wire_mapping)
            pd.set_deployed_mod_index(self.final_assembly_composite.components, self.component_implementations)

            pd.set_fine_grain_deployment(self.fine_grain_deployment)
            pd.find_ELI_input_operation(self.logical_system.platform_links)

        info("=============== Completed\n\n")
        return True
