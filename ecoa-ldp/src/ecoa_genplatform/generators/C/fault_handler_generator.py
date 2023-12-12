# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ..version_header_generator import generate_ldp_version_header
from ..force_generation import file_need_generation


def generate_C_fault_handler(fault_handler_dir, current_PF, force_flag):
    c_filename = os.path.join(fault_handler_dir, current_PF.name + '_fault_handler.c')

    if file_need_generation(c_filename,
                            force_flag,
                            "    A fault handler already exists for " + current_PF.name):

        fd = open(c_filename, 'w')

        print(generate_ldp_version_header(), file=fd)
        print("/* Fault Handler Implementation for %s */" % current_PF.name, file=fd)
        print("#include \"ldp_network.h\"", file=fd)
        print("#include \"" + current_PF.name + "_fault_handler.h\"", file=fd)
        print("", file=fd)
        print("void " + current_PF.name + "__initialize_user_context(%s_user_context * context) {" % current_PF.name,
              file=fd)
        print("  /* @TODO TODO - To be implemented */", file=fd)
        print("}", file=fd)
        print("", file=fd)
        print("void " + current_PF.name + "__error_notification (", file=fd)
        print("  ldp_fault_handler_context* context, ", file=fd)
        print("  ECOA__error_id error_id,", file=fd)
        print("  ECOA__global_time timestamp,", file=fd)
        print("  ECOA__asset_id asset_id,", file=fd)
        print("  ECOA__asset_type asset_type,", file=fd)
        print("  ECOA__error_type error_type,", file=fd)
        print("  ECOA__error_code error_code)", file=fd)
        print("{", file=fd)
        print("  /* @TODO TODO - To be implemented */", file=fd)
        print("}", file=fd)

        fd.close()


def generate_H_fault_handler_user_context(fault_handler_dir, current_PF, force_flag):
    h_filename = os.path.join(fault_handler_dir, current_PF.name + '_user_context.h')

    if file_need_generation(h_filename,
                            force_flag,
                            "    A fault handler header user_context already exists for " + current_PF.name):

        fd = open(h_filename, 'w')

        print(generate_ldp_version_header(), file=fd)
        print("/* Fault Handler User Context Header for %s */" % current_PF.name, file=fd)
        print("#if !defined(" + str.upper(current_PF.name) + "_USER_CONTEXT_H)", file=fd)
        print("#define " + str.upper(current_PF.name) + "_USER_CONTEXT_H", file=fd)
        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("extern \"C\" {", file=fd)
        print("#endif /* __cplusplus */", file=fd)
        print("", file=fd)

        print("/*", file=fd)
        print(" * @file " + str.upper(current_PF.name) + "_user_context.h", file=fd)
        print(" */", file=fd)
        print("/* Fault Handler User Context Structure */", file=fd)
        print("typedef struct", file=fd)
        print("{", file=fd)
        print("    /*********** START USER-WRITTEN USER ***********/", file=fd)
        print("    /*********** START USER-WRITTEN USER ***********/", file=fd)
        print("} " + current_PF.name + "_user_context;", file=fd)

        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("} ", file=fd)
        print("#endif /* __cplusplus */", file=fd)
        print("", file=fd)
        print("#endif  /* " + str.upper(current_PF.name) + "_USER_CONTEXT_H */", file=fd)

        fd.close()


def generate_H_fault_handler(fault_handler_dir, current_PF, force_flag):
    h_filename = os.path.join(fault_handler_dir, current_PF.name + '_fault_handler.h')

    if file_need_generation(h_filename,
                            force_flag,
                            "    A fault handler header already exists for " + current_PF.name):

        fd = open(h_filename, 'w')

        print(generate_ldp_version_header(), file=fd)
        print("/* Fault Handler Header for %s */" % current_PF.name, file=fd)
        print("#if !defined(_" + str.upper(current_PF.name) + "_H)", file=fd)
        print("#define _" + str.upper(current_PF.name) + "_H", file=fd)
        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("extern \"C\" {", file=fd)
        print("#endif", file=fd)
        print("", file=fd)

        print("#include \"" + current_PF.name + "_container.h\"", file=fd)
        print("", file=fd)
        print("void " + current_PF.name + "__initialize_user_context(" + current_PF.name + "_user_context * context);",
              file=fd)
        print("", file=fd)
        print("void " + current_PF.name + "__error_notification (", file=fd)
        print("  ldp_fault_handler_context* context, ", file=fd)
        print("  ECOA__error_id error_id,", file=fd)
        print("  ECOA__global_time timestamp,", file=fd)
        print("  ECOA__asset_id asset_id,", file=fd)
        print("  ECOA__asset_type asset_type,", file=fd)
        print("  ECOA__error_type error_type,", file=fd)
        print("  ECOA__error_code error_code);", file=fd)

        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("} ", file=fd)
        print("#endif", file=fd)
        print("", file=fd)
        print("#endif  /* _" + str.upper(current_PF.name) + "_H */", file=fd)

        fd.close()
