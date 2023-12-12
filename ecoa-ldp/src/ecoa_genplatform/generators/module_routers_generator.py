# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from .C.driver_api_generator import generate_external_c, generate_external_h
from .Cpp.driver_api_generator import generate_external_cpp, generate_external_hpp

from .C.component_generator import generate_component_h, generate_component_c, generate_properties_API
from .Cpp.component_generator import generate_component_hpp, generate_component_cpp
from ecoa.utilities.logs import debug, error, info
from .version_header_generator import generate_ldp_version_header_cmake
from .force_generation import file_need_generation


def generate_all_module_routers(output_dir, protection_domains, components, component_types, component_implementations, wires,
                            libraries, force_flag):
    """Generate all routers of module instances:

        * cmake
        * module router functions
        * module files
        * driver API
        * properties API
    """
    for comp_impl, _ in sorted(component_implementations.values()):
        comp_list = [c for c in components.values() if c.get_component_implementation() == comp_impl.name]
        if len(comp_list) == 0:
            info(" # Skip generation of component implementation '"+comp_impl.name+"' because it is not used in a component")
            continue

        info(" # Generate component implementation "+comp_impl.name+" for components "+str([c.name for c in comp_list]))

        cimpl_outdir = os.path.join(output_dir, comp_impl.get_name())
        comp_type, _ = component_types[comp_list[0].component_type]

        os.makedirs(cimpl_outdir, exist_ok=True)

        if comp_impl.has_cpp_module():
            generate_component_hpp(cimpl_outdir, comp_list, comp_impl, force_flag)
            generate_component_cpp(cimpl_outdir, comp_list, comp_type, comp_impl, wires, force_flag, libraries,
                                   protection_domains,
                                   components, component_implementations)
        else:
            generate_component_h(cimpl_outdir, comp_list, comp_impl, force_flag)
            generate_component_c(cimpl_outdir, comp_list, comp_type, comp_impl, wires, force_flag, libraries)

        generate_external_h(cimpl_outdir, comp_impl, force_flag, libraries)
        generate_external_c(cimpl_outdir, protection_domains, comp_impl, comp_list, force_flag)
        generate_external_hpp(cimpl_outdir, comp_impl, force_flag, libraries)
        generate_external_cpp(cimpl_outdir, protection_domains, comp_impl, comp_list, force_flag)
        generate_cmake(cimpl_outdir, comp_impl, libraries, force_flag)
        generate_properties_API(cimpl_outdir, comp_list, comp_type, comp_impl, libraries, force_flag)

def generate_cmake(output_dir, component_impl, libraries, force_flag):
    """Generate cmake file for this component implementation

    Attributes:
        output_dir  (str): The compnent implementation directory
        component_impl            (:class:`~ecoa.models.component_implementation.Component_Implementation`): The component implementation
        libraries                 (dict): dictionary of libraries
    """
    cmake_file = output_dir + os.sep + "CMakeLists.txt"
    comp_impl_dir = os.path.relpath(os.path.abspath(component_impl.impl_directory), start=output_dir)

    if not file_need_generation(cmake_file,
                            force_flag,
                            "CMakeLists.txt already exists for " + component_impl.get_name()):
        return

    fd = open(cmake_file, 'w')
    text = generate_ldp_version_header_cmake()
    text += "cmake_minimum_required(VERSION 3.4)\n\n"

    if component_impl.has_cpp_module():
        text += "set(SRC component_" + component_impl.get_name() + ".cpp \n"
    else:
        text += "set(SRC component_" + component_impl.get_name() + ".c \n"

    for module_impl in component_impl.module_implementations.values():
        if module_impl.language == "C++":
            text += os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir, module_impl.name, "src-gen", module_impl.name + "_container.cpp") + "\n"
        elif module_impl.language == "C":
            text += os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir, module_impl.name, "src-gen", module_impl.name + "_container.c") + "\n"
            text += os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir, module_impl.name, "src-gen", "*_"+module_impl.name + ".c") + "\n"
        else:
            error("language "+ module_impl.language+" is not supported ["+component_impl.name+" "+ module_impl.name+"]")

    if component_impl.has_external_c_links():
        text += component_impl.get_name() + "_External_Interface.c \n"
    if component_impl.has_external_cpp_links():
        text += component_impl.get_name() + "_External_Interface.cpp \n"
    text += ")\n\n"

    text += "file(GLOB SRC ${SRC} "

    for module_impl in component_impl.module_implementations.values():
        if not module_impl.is_binary_module():
            if module_impl.language=="C++":
                text += os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir, module_impl.name, "src", "*.cpp") + "\n"
            elif module_impl.language=="C":
                text += os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir, module_impl.name, "src", "*.c") + "\n"
            else:
                error("language is not supported")
        else:
            text += module_impl.binary_desc.object_file+ "\n"
    text += ")\n\n"

    if component_impl.has_cpp_module():
        text += "set(HEADER component_" + component_impl.get_name() + ".hpp)\n"
    else:
        text += "set(HEADER component_" + component_impl.get_name() + ".h)\n"


    text += "include_directories(${CMAKE_CURRENT_SOURCE_DIR})\n"
    for module_name, module_impl in component_impl.module_implementations.items():
        if not module_impl.is_binary_module():
            text += "include_directories("+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir,module_name,"inc")+")\n"
        text += "include_directories("+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir,module_name,"inc-gen")+")\n"
    text += "include_directories("+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}","..","platform")+")\n"

    text += "###########\n"
    text += "add_library(lib_" + component_impl.get_name() + " ${SRC} ${HEADER})\n"
    text += "target_include_directories(lib_" + component_impl.get_name() + " PRIVATE ${APR_INCLUDE_DIR})\n"
    text += "target_link_libraries(lib_" + component_impl.get_name() + " PRIVATE ecoa)\n"
    text += "if(${LDP_LOG_USE} STREQUAL \"lttng\")\n"
    text += "    target_link_libraries(lib_" + component_impl.get_name() + " PRIVATE lttng-ust)\n"
    text += "elseif(${LDP_LOG_USE} STREQUAL \"log4cplus\")\n"
    text += "    target_link_libraries(lib_" + component_impl.get_name() + " PRIVATE log4cplus::log4cplus)\n"
    text += "elseif(${LDP_LOG_USE} STREQUAL \"zlog\")\n"
    text += "    target_link_libraries(lib_" + component_impl.get_name() + " PRIVATE zlog)\n"
    text += "endif()\n"

    text +="if (EXISTS "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir,"local.cmake")+" )\n"
    text +="	include("+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir,"local.cmake")+" )\n"
    text +="endif (EXISTS "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",comp_impl_dir,"local.cmake")+" )\n"

    print(text, file=fd)
    fd.close()
