# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
import sys
from shutil import copytree, rmtree
from ecoa.utilities.logs import debug
from ..version_header_generator import generate_ldp_version_header_cmake
from ..force_generation import file_need_generation


def generate_main_cmake(directory, components, protections_domains, debug_flag, coverage_flag, force_flag):
    """@TODO Function docstring"""
    cmake_dir = os.path.join(directory, "..")
    cmake_filename = os.path.join(cmake_dir, "CMakeLists.txt")

    if not file_need_generation(cmake_filename,
                            force_flag,
                            "    CMakeLists already exists"):
        return

    file = open(cmake_filename, 'w')

    text = generate_ldp_version_header_cmake()
    text += "cmake_minimum_required(VERSION 3.4)\n\n"

    text += "project(globalProject)\n\n "
    text += "set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} \"" + os.path.join(
        "${globalProject_SOURCE_DIR}", "CMakeModules") + "\")\n"
    text += "#################\n"
    text += "## binary directory\n"
    text += "set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY " + os.path.join("${CMAKE_BINARY_DIR}",
                                                                 "lib") + ")\n"
    text += "set(CMAKE_LIBRARY_OUTPUT_DIRECTORY " + os.path.join("${CMAKE_BINARY_DIR}",
                                                                 "lib") + ")\n"
    text += "set(CMAKE_RUNTIME_OUTPUT_DIRECTORY " + os.path.join("${CMAKE_BINARY_DIR}",
                                                                 "bin") + ")\n\n"

    text += "###################\n"
    text += "## set compiler flags\n"
    text += "set(CMAKE_C_FLAGS \"${CMAKE_C_FLAGS} -D_POSIX_C_SOURCE=200809L"
    if debug_flag:
        text += " -g"
    if coverage_flag:
        text += " --coverage"
    text += " ${USER_CMAKE_C_FLAGS}\")\n"
    text += "set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS}"
    if debug_flag:
        text += " -g"
    if coverage_flag:
        text += " --coverage"
    text += " ${USER_CMAKE_CXX_FLAGS}\")\n"
    text += "add_definitions(-D ECOA_64BIT_SUPPORT)\n\n"
    text += "if(NOT CMAKE_USE_UDP_PROTO)\n"
    text += "    set(CMAKE_USE_UDP_PROTO false)\n"
    text += "    message(\"-- Use TCP protocol\")\n"
    text += "else()\n"
    text += "    message(\"-- Use UDP protocol\")\n"
    text += "endif ()\n"
    text += "add_definitions(-D USE_UDP_PROTO=${CMAKE_USE_UDP_PROTO})\n\n"
    text += "if(NOT CMAKE_USE_AF_UNIX)\n"
    text += "    set(CMAKE_USE_AF_UNIX false)\n"
    text += "    message(\"-- Use AF_INET socket family\")\n"
    text += "else()\n"
    text += "    message(\"-- Use AF_UNIX socket family\")\n"
    text += "endif ()\n"
    text += "add_definitions(-D USE_AF_UNIX=${CMAKE_USE_AF_UNIX})\n"

    text += "find_package(PkgConfig)\n\n"

    text += "#############\n"
    text += "## APR\n"
    text += "find_package ( APR )\n"
    text += "if (APR_FOUND)\n"
    text += "    message(STATUS \"Find APR in ${APR_ROOT_PATH}\")\n"
    text += "    link_directories(${APR_LIB_DIR})\n"
    text += "else(APR_FOUND)\n"
    text += "    message(SEND_ERROR \"No APR found\")\n"
    text += "endif (APR_FOUND)\n\n"

    text += "if(${LDP_LOG_USE} STREQUAL \"lttng\")\n"
    text += "   pkg_check_modules(lttng-ust REQUIRED lttng-ust)\n"
    text += "elseif(${LDP_LOG_USE} STREQUAL \"log4cplus\")\n"
    text += "   #############\n"
    text += "   ## LOG4CPLUS\n"
    text += "   find_package ( log4cplus REQUIRED )\n"
    text += "elseif(${LDP_LOG_USE} STREQUAL \"zlog\")\n"
    text += "   #############\n"
    text += "   ## ZLOG\n"
    text += "   find_package ( zlog REQUIRED )\n"
    text += "endif()\n\n"

    text += "#############\n"
    text += "## PThread\n"
    text += "set(THREADS_PREFER_PTHREAD_FLAG ON)\n"
    text += "find_package(Threads REQUIRED)\n\n"

    text += "##########\n"
    text += "## libecoa\n"
    text += "add_subdirectory(" + os.path.join("platform", "lib") + ")\n"
    text += "add_subdirectory(" + os.path.join("platform", "svc_deserial") + ")\n"
    text += "add_subdirectory(" + os.path.join("0-Types") + ")\n\n"

    text += "#################\n"
    text += "## components and plarform executables\n"
    text += "add_subdirectory(platform)\n"
    comp_impl_names = set()
    # find component implementations that are used in every Protections Domains
    for pd in protections_domains.values():
        comp_impl_names |= set(pd.get_all_component_implementations_name(components))
    for comp_impl_name in sorted(comp_impl_names):
        text += "add_subdirectory(" + comp_impl_name + ")\n"

    text += "if(${LDP_LOG_USE} STREQUAL \"lttng\")\n"
    text += "add_custom_target(run\n"
    text += "    COMMAND lttng create Session_ECOA\\; "
    text += "lttng enable-event --userspace ldp_lttng_log:* \\; lttng start \\; "
    text += "./platform \\; STATUS_ECOA=$$? \\; lttng stop \\; lttng destroy Session_ECOA\\;"
    text += "exit $$STATUS_ECOA\n"
    text += "    DEPENDS platform"
    for pd_name in protections_domains.values():
        text += " PD_" + pd_name.get_name()
    text += "\n"
    text += "    WORKING_DIRECTORY " + os.path.join("${CMAKE_BINARY_DIR}", "bin") + "\n"
    text += ")\n"
    text += "else()\n"
    text += "add_custom_target(run\n"
    text += "    COMMAND ./platform \\; STATUS_ECOA=$$? \\; python -c \n"
    text += "\\\"import os, datetime\\;\n"
    text += "os.rename\\('" + os.path.join("${CMAKE_BINARY_DIR}", "bin", "logs") + "',\n"
    text += "            '" + os.path.join("${CMAKE_BINARY_DIR}", "bin",
                                           "logs") + "-'+datetime.datetime.now\\(\\).strftime\\(" \
                                                     "'%Y%m%d%H%M%S'\\)\\)\n "
    text += "\\\" \\; exit $$STATUS_ECOA\n"
    text += "    DEPENDS platform"
    for pd_name in protections_domains.values():
        text += " PD_" + pd_name.get_name()
    text += "\n"
    text += "    WORKING_DIRECTORY " + os.path.join("${CMAKE_BINARY_DIR}", "bin") + "\n"
    text += ")\n"
    text += "endif()\n\n"

    text += "if (EXISTS " + os.path.join("${CMAKE_CURRENT_SOURCE_DIR}", "local.cmake") + " )\n"
    text += "	include(" + os.path.join("${CMAKE_CURRENT_SOURCE_DIR}", "local.cmake") + ")\n"
    text += "endif (EXISTS " + os.path.join("${CMAKE_CURRENT_SOURCE_DIR}", "local.cmake") + " )\n"

    print(text, file=file)

    file.close()

    current_module = sys.modules['ecoa_genplatform.generators']
    current_module_path = os.path.dirname(current_module.__file__)
    rmtree(os.path.normpath(os.path.join(cmake_dir, "CMakeModules")), True)
    copytree(os.path.normpath(os.path.join(current_module_path, "C", "CMakeModules")),
             os.path.normpath(os.path.join(cmake_dir, "CMakeModules")))
