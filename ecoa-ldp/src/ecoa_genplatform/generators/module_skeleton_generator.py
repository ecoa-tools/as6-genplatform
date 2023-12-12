# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from .C.module_generator import generate_C_module, generate_H_user_context, generate_H_module
from .C.mod_container_generator import generate_H_container, generate_C_container
from .C.test_module_generator import generate_C_module_test, generate_C_test_makefile, generate_C_test_container
from .C.module_helpers_generator import generate_C_module_helpers_test, generate_H_module_helpers,\
    generate_C_helpers_makefile, generate_C_module_helpers

from .Cpp.module_generator import generate_Cpp_module, generate_Hpp_user_context, generate_Hpp_module
from .Cpp.mod_container_generator import generate_Hpp_container, generate_Hpp_container_types, generate_Cpp_container
import os, sys, shutil
from collections import OrderedDict
from ecoa.utilities.logs import debug, error, info

def generate_all_modules(output_dir,
                         component_implementations,
                         libraries,
                         force_flag):

    sorted_component_keys = list(component_implementations.keys())
    sorted_component_keys.sort()

    for cimpl in iter(sorted_component_keys):
        info(" # Generate module implementation in component implementation %s" % cimpl)
        for (mimpl_k, mimpl_v) in component_implementations[cimpl][0].get_module_implementations().items():
            mimpl_dir = component_implementations[cimpl][0].impl_directory + os.sep + mimpl_k
            info("    mod: %s, type: %s, language: %s" % (mimpl_k, mimpl_v.get_type(), mimpl_v.get_language()))

            if os.path.exists(mimpl_dir):
                info("    Module implementation already exists for %s" % mimpl_k)

                if force_flag:
                    info("    Erase existing module implementation")
                    for root, dirs, files in os.walk(mimpl_dir, topdown=False):
                        if not (root.endswith("src")) and not (root.endswith("inc")):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                if name != "src" and name != "inc" and name != "test":
                                    debug(os.path.join(root, name))
                                    os.rmdir(os.path.join(root, name))
            else:
                pass
                # if force_flag == True:
            mimpl_src     = os.path.join(mimpl_dir, "src")
            mimpl_src_gen = os.path.join(mimpl_dir, "src-gen")
            mimpl_inc     = os.path.join(mimpl_dir, "inc")
            mimpl_inc_gen = os.path.join(mimpl_dir, "inc-gen")
            mimpl_test    = os.path.join(mimpl_dir, "test")

            os.makedirs(mimpl_dir, exist_ok = True)
            os.makedirs(mimpl_test, exist_ok = True)
            os.makedirs(mimpl_src_gen, exist_ok = True)
            os.makedirs(mimpl_inc_gen, exist_ok = True)
            if not mimpl_v.is_binary_module():
              os.makedirs(mimpl_src, exist_ok = True)
              os.makedirs(mimpl_inc, exist_ok = True)

            if mimpl_v.get_language() == 'C':
                mimpl_libraries = OrderedDict()
                for lib_name, lib in libraries.items():
                    if lib_name in component_implementations[cimpl][0].get_libraries():
                        mimpl_libraries[lib_name] = lib[0]

                if not mimpl_v.is_binary_module():
                  generate_C_module(mimpl_src, mimpl_v,
                                    component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                    component_implementations[cimpl][0].get_libraries(),
                                    force_flag)
                  generate_C_module_test(mimpl_test, mimpl_v,
                                         component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                         component_implementations[cimpl][0].get_libraries(),
                                         force_flag)
                  generate_C_test_makefile(mimpl_test, mimpl_v,
                                           force_flag)

                  generate_H_user_context(mimpl_inc, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)

                # always generated
                generate_H_module(mimpl_inc_gen, mimpl_v,
                                    component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                    mimpl_libraries,
                                    force_flag)

                generate_H_container(mimpl_inc_gen, mimpl_v,
                                     component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                     mimpl_libraries,
                                     force_flag)
                generate_C_container(mimpl_src_gen, mimpl_v,
                                     component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                     mimpl_libraries,
                                     cimpl,
                                     force_flag)
                generate_C_test_container(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)
                generate_C_module_helpers_test(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)
                generate_H_module_helpers(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)
                generate_C_helpers_makefile(mimpl_test, mimpl_v,
                                            force_flag)
                generate_C_module_helpers(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)


            elif mimpl_v.get_language() == 'C++':
                mimpl_libraries = OrderedDict()
                for lib_name, lib in libraries.items():
                    if lib_name in component_implementations[cimpl][0].get_libraries():
                        mimpl_libraries[lib_name] = lib[0]

                if not mimpl_v.is_binary_module():
                  generate_Cpp_module(mimpl_src, mimpl_v,
                                    component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                    component_implementations[cimpl][0].get_libraries(),
                                    force_flag)
                  generate_C_module_test(mimpl_test, mimpl_v,
                                         component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                         component_implementations[cimpl][0].get_libraries(),
                                         force_flag)
                  generate_C_test_makefile(mimpl_test, mimpl_v,
                                           force_flag)
                  generate_Hpp_user_context(mimpl_inc, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),

                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)

                # always generated
                generate_Hpp_module(mimpl_inc_gen, mimpl_v,
                                    component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                    mimpl_libraries,
                                    force_flag)
                generate_Hpp_container(mimpl_inc_gen, mimpl_v,
                                     component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                     mimpl_libraries,
                                     force_flag)
                generate_Hpp_container_types(mimpl_inc_gen, mimpl_v,
                                     component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                     mimpl_libraries,
                                     force_flag)
                generate_Cpp_container(mimpl_src_gen, mimpl_v,
                                     component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                     mimpl_libraries,
                                     cimpl,
                                     force_flag)
                generate_C_test_container(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)
                generate_C_module_helpers_test(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)
                generate_H_module_helpers(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)
                generate_C_helpers_makefile(mimpl_test, mimpl_v,
                                            force_flag)
                generate_C_module_helpers(mimpl_test, mimpl_v,
                                          component_implementations[cimpl][0].get_module_type(mimpl_v.get_type()),
                                          component_implementations[cimpl][0].get_libraries(),
                                          force_flag)

            else:
                error("language not supported")
