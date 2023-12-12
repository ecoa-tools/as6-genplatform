# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from .C.types_generator import generate_C_types
from .Cpp.types_generator import generate_Cpp_types
from ecoa.utilities.logs import debug
from .fix_names import fix_C_libname
from .version_header_generator import generate_ldp_version_header_cmake

def check_existing_dir(dir_path):
    if not os.path.exists(dir_path):
        debug("    Directory does not existed : %s" % (dir_path))
        os.makedirs(dir_path, exist_ok=True)

def generate_types(PF_directory, directory, libraries, force_flag):
    check_existing_dir(directory + os.sep + "inc")
    check_existing_dir(directory + os.sep + "inc-gen")
    check_existing_dir(directory + os.sep + "src-gen")
    check_existing_dir(os.path.join(PF_directory,"..","0-Types"))

    generate_C_types(directory, libraries, force_flag)
    generate_Cpp_types(directory, libraries, force_flag)
    generate_cmakelist(os.path.join(PF_directory,"..","0-Types"), libraries)

def generate_cmakelist(directory, libraries):

    text = generate_ldp_version_header_cmake()
    text+= "cmake_minimum_required(VERSION 3.4) \n\n\
project(ecoa)\n"
    lib_dir = set()
    lib_directories=set([lib.libfile_directory for lib,_ in libraries.values()])
    for lib_dir in lib_directories:
        if lib_dir != "":
            relpath = os.path.relpath( lib_dir, start=directory)
        else:
            relpath = directory
        text += "    include_directories("+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",relpath,"inc")+")\n"
        text += "    include_directories("+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",relpath,"inc-gen")+")\n"

    text+="target_sources(ecoa PRIVATE ${${PROJECT_NAME}_types_src}\n"
    for lib,_ in libraries.values():
        if(lib.libfile_directory !=""):
            relpath = os.path.relpath( lib.libfile_directory, start=directory)
        else:
            relpath = directory

        if lib.name != 'ECOA':
            text += "    "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",relpath,"src-gen",fix_C_libname(lib.name)+"_serialization.c \n")
            # text += "    ${CMAKE_CURRENT_SOURCE_DIR}"+relpath+"/src-gen/"+fix_C_libname(lib.name)+"_serialization.cpp \n"

        text += "    "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",relpath,"src-gen",lib.comp_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.comp_suffix+".c \n")
        text += "    "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",relpath,"src-gen",lib.zeroise_prefix+"__"+fix_C_libname(lib.name)+"_types_"+lib.zeroise_suffix+".c \n")
        #@TODO same with cpp
        #@TODO text += "    ${CMAKE_CURRENT_SOURCE_DIR}/src-gen/"+lib.comp_prefix+"__"+lib.name+"_types_"+lib.comp_suffix+".cpp \n"
        #@TODO text += "    ${CMAKE_CURRENT_SOURCE_DIR}/src-gen/"+lib.zeroise_prefix+"__"+lib.name+"_types_"+lib.zeroise_suffix+".cpp \n"

    text+= ") \n\n"

    text += "##################### \n"
    for lib_dir in lib_directories:
        if lib_dir != "":
            dir_tmp = os.path.relpath( lib_dir, start=directory)
            text += "    target_include_directories(${PROJECT_NAME} PUBLIC "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",dir_tmp,"inc")+")\n"
            text += "    target_include_directories(${PROJECT_NAME} PUBLIC "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",dir_tmp,"inc-gen")+")\n"

            local_cmake_file = os.path.join("${CMAKE_CURRENT_SOURCE_DIR}", dir_tmp,"local.cmake")
            text += "if (EXISTS "+ local_cmake_file+" )\n"
            text += "    include("+ local_cmake_file+" )\n"
            text += "endif (EXISTS "+ local_cmake_file+" )\n"
        else:
            text += "    target_include_directories(${PROJECT_NAME} PUBLIC "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",directory,"inc")+")\n"
            text += "    target_include_directories(${PROJECT_NAME} PUBLIC "+os.path.join("${CMAKE_CURRENT_SOURCE_DIR}",directory,"inc-gen")+")\n"


    if os.path.exists(directory) == False:
       os.makedirs(directory)

    cmakelist_path = os.path.join(directory, "CMakeLists.txt")
    cmakelist_file = open(cmakelist_path, 'w')

    print(text, file = cmakelist_file)
    cmakelist_file.close()
