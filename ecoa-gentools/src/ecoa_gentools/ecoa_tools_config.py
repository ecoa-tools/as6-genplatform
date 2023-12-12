# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ecoa_genplatform.generators.module_skeleton_generator import generate_all_modules
from ecoa_genplatform.generators.types_generator import generate_types
from .generators.Module_bin_desc.binary_desc_generator import binary_desc_generator

from ecoa.ecoa_global_config import ECOA_Global_Config
from ecoa.utilities.logs import info, error
from ecoa.models.route import route


class ECOA_Gentools_Config(ECOA_Global_Config):
    """
    @brief      main class that extend all configuration information to generate a platform
    """

    def generate(self, force_flag, gen_bin_desc_info):
        if len(self.deployment.protection_domains) > 0:
            current_PF = self.logical_system.platforms[self.current_PF_name]
        else:
            error("No platform to generate. Any platform has a protection domain to deploye")
            error("Nothing to generate")
            return

        info("=============== GENERATE platform {}".format( current_PF.name))
        # info("File info route")
        # ROUTE_INFO = route(self.final_assembly_composite.wires,
        #                    self.final_assembly_composite.components, self.component_types,
        #                    self.service_definitions, self.component_implementations, self.IDs)

        info(" == Generate libraries")
        generate_types(self.PF_output_dir, self.types_output_dir, self.libraries, force_flag)

        info(" == Generate all modules")
        generate_all_modules(self.ECOAProject.output_dir,
                             self.component_implementations,
                             self.libraries,
                             force_flag)

        # Generate module binary descriptors files. It requires that types are generated
        info("=============== generate bin-desc files\n")
        c_compiler, cpp_compiler, c_flags, cpp_flags = gen_bin_desc_info
        binary_desc_generator(self.component_implementations, self.types_output_dir,
                              c_compiler, cpp_compiler, c_flags, cpp_flags)

        info("=============== Completed\n\n")

        return True
