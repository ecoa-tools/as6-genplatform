# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .generators.module_skeleton_generator import generate_all_modules
from .generators.platform_skeleton_generator import generate_platform
from .generators.module_routers_generator import generate_all_module_routers
from .generators.types_generator import generate_types
from .generators.C.protection_domain_generator import generate_all_protection_domains
from .generators.C.svc_deserialization_generator import generate_svc_deserialized
from .generators.C.route_generator import generate_route
from .generators.C.multi_nodes_generator import generate_multi_nodes_file
from ecoa.ecoa_global_config import ECOA_Global_Config
from ecoa.utilities.logs import info, error
from ecoa.models.route import route


class ECOA_Generate_Config(ECOA_Global_Config):
    """
    @brief      main class that extend all configuration information to generate a platform
    """

    def generate(self, file_log_dir, force_flag, debug_flag, coverage_flag,
                 gen_bin_desc_info=None):
        if len(self.deployment.protection_domains) > 0:
            current_PF = self.logical_system.platforms[self.current_PF_name]
        else:
            error("No platform to generate. Any platform has a protection domain to deploye")
            error("Nothing to generate")
            return

        info("=============== GENERATE platform {}".format(current_PF.name))
        info("File info route")
        ROUTE_INFO = route(self.final_assembly_composite.wires,
                           self.final_assembly_composite.components, self.component_types,
                           self.service_definitions, self.component_implementations, self.IDs)

        info(" == Generate libraries")
        generate_types(self.PF_output_dir, self.types_output_dir, self.libraries, force_flag)

        info(" == Generate all modules")
        generate_all_modules(self.ECOAProject.output_dir,
                             self.component_implementations,
                             self.libraries,
                             force_flag)

        info(" == Generate platform")
        generate_platform(self.deployment.multi_node,
                          self.PF_output_dir,
                          self.final_assembly_composite.components,
                          self.component_implementations,
                          self.libraries, force_flag,
                          file_log_dir,
                          self.deployment.protection_domains,
                          self.fine_grain_deployment,
                          self.logical_system.platform_links,
                          current_PF,
                          debug_flag,
                          coverage_flag,
                          self.integration_directory)
        generate_svc_deserialized(self.service_definitions,
                                  self.PF_output_dir,
                                  self.libraries)

        generate_route(self.deployment.multi_node, ROUTE_INFO, self.PF_output_dir, force_flag, self.instance_index,
                       self.deployment.protection_domains, self.final_assembly_composite.components,
                       self.logical_system.platform_links, current_PF,
                       self.logical_system.platforms,
                       self.integration_directory,
                       self.ECOAProject.project_name,
                       self.nodes_deployment)

        info(" == Generate all module routers")
        generate_all_module_routers(self.ECOAProject.output_dir,
                                    self.deployment.protection_domains,
                                    self.final_assembly_composite.components,
                                    self.component_types,
                                    self.component_implementations,
                                    self.final_assembly_composite.wires,
                                    self.libraries,
                                    force_flag)

        info(" == Generate protection domains")
        generate_all_protection_domains(self.PF_output_dir,
                                        self.deployment.protection_domains,
                                        self.final_assembly_composite.components,
                                        self.component_implementations,
                                        self.final_assembly_composite.wires,
                                        self.component_types,
                                        self.service_definitions,
                                        self.libraries,
                                        self.logical_system.platform_links,
                                        current_PF,
                                        force_flag)

        if self.deployment.multi_node:
            info(" == Generate multi-nodes file")
            generate_multi_nodes_file(self.PF_output_dir,
                                      self.deployment.protection_domains,
                                      self.nodes_deployment,
                                      force_flag)

        info("=============== Completed\n\n")

        return True
