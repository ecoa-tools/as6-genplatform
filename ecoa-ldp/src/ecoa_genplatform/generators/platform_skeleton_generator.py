# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import shutil
import sys
import os

from ..generators.C.platform_generator import generate_main, generate_main_tools,\
    generate_platform_cmake, generate_id_identifying_struct
from ..generators.C.cmake_generator import generate_main_cmake
from ..generators.C.fault_handler_container_generator import generate_C_fault_handler_container,\
    generate_H_fault_handler_container
from ..generators.C.fault_handler_generator import generate_C_fault_handler,\
    generate_H_fault_handler, generate_H_fault_handler_user_context
from ..generators.C.log_properties_generator import generate_log_properties
from ecoa.utilities.logs import debug


# OD BEGIN
def generate_platform(multi_node, platform_output_dir, components, component_implementations, libraries, force_flags,
                      file_log_path, protection_domains, fine_grain_deployment, PF_links, current_PF,
                      debug_flag, coverage_flag, integration_directory):
    """Generate code for main and route.c file and a makefile. Copy some files from /lib directory to platform/lib directory

    :param str multi_node: multi node activation 
    :param str platform_output_dir: path to component implementations directory
    :param dict component_implementations: dictionary of component_implementation objects retrieved by name
    :param set wires: set of wires
    :param dict libraries: dictionary of libraries retrieved by name
    :param bool force_flags: overwrite files
    :param str integration_directory: integration directory path"""

    # Fault handler paths
    l_fault_handler_dir = os.path.realpath(integration_directory)
    l_fh_src_gen = os.path.join(l_fault_handler_dir, "src-gen")
    l_fh_inc_gen = os.path.join(l_fault_handler_dir, "inc-gen")
    l_fh_src = os.path.join(l_fault_handler_dir, "src")
    l_fh_inc = os.path.join(l_fault_handler_dir, "inc")

    # create dir
    os.makedirs(platform_output_dir, exist_ok=True)
    os.makedirs(l_fh_src_gen, exist_ok=True)
    os.makedirs(l_fh_inc_gen, exist_ok=True)
    os.makedirs(l_fh_src, exist_ok=True)
    os.makedirs(l_fh_inc, exist_ok=True)

    # generate
    generate_main(multi_node, platform_output_dir,libraries, force_flags,
                  protection_domains, fine_grain_deployment, PF_links, current_PF)
    generate_main_tools(platform_output_dir, component_implementations, libraries, force_flags,
                  protection_domains)

    generate_C_fault_handler_container(l_fh_src_gen, current_PF, force_flags)
    generate_H_fault_handler_container(l_fh_inc_gen, current_PF, force_flags)
    
    generate_C_fault_handler(l_fh_src, current_PF, force_flags)
    generate_H_fault_handler(l_fh_inc, current_PF, force_flags)
    generate_H_fault_handler_user_context(l_fh_inc, current_PF, force_flags)

    # OD BEGIN
    generate_main_cmake(platform_output_dir, components, protection_domains, debug_flag, coverage_flag, force_flags)
    generate_platform_cmake(multi_node, platform_output_dir, component_implementations, components,
                            protection_domains,
                            integration_directory, current_PF, force_flags)
    generate_id_identifying_struct(platform_output_dir, protection_domains)

    log_properties_dir = os.path.join(platform_output_dir, 'log_properties')
    if os.path.exists(log_properties_dir):
        debug(log_properties_dir + " exists (override)")
    else:
        os.mkdir(log_properties_dir)

    for pd_name in protection_domains:
        generate_log_properties(log_properties_dir, pd_name, file_log_path, force_flags)
        generate_log_properties(log_properties_dir, pd_name + "_PF", file_log_path, force_flags)
    generate_log_properties(log_properties_dir, "main_PF", file_log_path, force_flags)

    # copy ecoa libraries in /lib directory
    cmodule = sys.modules['ecoa_genplatform.generators.C.types_generator']
    path = os.path.dirname(cmodule.__file__)
    lib_path = platform_output_dir + os.sep + "lib"

    # create directory
    if os.path.exists(lib_path) is False:
        os.mkdir(lib_path)

    # copy
    for item in os.listdir(path + os.sep + 'lib'):
        if item == 'html':
            # avoid to copy doxygen docs
            continue
        s = os.path.join(path + os.sep + 'lib', item)
        d = os.path.join(lib_path, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
