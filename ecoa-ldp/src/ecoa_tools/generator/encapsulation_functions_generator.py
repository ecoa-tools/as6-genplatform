# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa.utilities.logs import debug, error
from .C.encaps_C_functions_generator import generate_C_encaps
from .pattern_files_parser import parse_component_pattern_file, parse_module_pattern_file

def check_existing_dir(dir_path):
    if not os.path.exists(dir_path):
        debug("    Directory does not existed : %s" % (dir_path))
        os.mkdir(dir_path)

def encaps_functions_generate(components_directory, component_implementations, force_flag):
    """Generate all encapsulation functions for all module implementations
        of all component_implementation.

    Args:
        components_directory       (str): The directory of component implementations
        component_implementations  (dict): dictionary of component implementation
        force_flag (bool): if True, files will be overwritten,
                           otherwise existing files will not be modifyed

    """

    # find 4-ComponentImplementations directory
    comp_implementations_dir= list(component_implementations.values())[0][0].impl_directory
    prefix = parse_component_pattern_file(os.path.join(comp_implementations_dir,".."))

    for comp_impl,_ in component_implementations.values():
        comp_directory = comp_impl.impl_directory
        if not os.path.exists(comp_directory):
            error("    Directory does not exist for %s" % (comp_directory))
            continue

        for mod_impl in comp_impl.module_implementations.values():
            mod_type = comp_impl.module_types[mod_impl.type]
            mod_impl_directory = os.path.join(comp_directory,mod_impl.name)
            check_existing_dir(mod_impl_directory)
            check_existing_dir(os.path.join(mod_impl_directory,"inc-gen"))
            check_existing_dir(os.path.join(mod_impl_directory,"src-gen"))

            # file pattern dictionary if possible
            pattern_dict = parse_module_pattern_file(mod_impl_directory, mod_impl, mod_type)
            generate_C_encaps(mod_impl, mod_type, mod_impl_directory, prefix, force_flag, pattern_dict)
            #@TODO generate_CPP_encaps...



