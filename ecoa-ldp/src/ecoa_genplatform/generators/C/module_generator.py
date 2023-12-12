# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from .operation_generator import generate_header_fct
from ecoa.utilities.logs import debug
from ..fix_names import fix_C_libname
from ..version_header_generator import generate_ldp_version_header, generate_ldp_version_header_warning
from ..force_generation import file_need_generation

def generate_C_module(directory, mimpl, mtype, libraries,
                      force_flag):
    default_generated_comment = "  /* @TODO TODO - To be implemented */"

    c_filename = os.path.join(directory, mimpl.get_name() + '.c')

    if file_need_generation(c_filename,
                            force_flag,
                            "    module C implementation already exists for " + mimpl.get_name()):

        fd = open(c_filename, 'w')

        mname = mimpl.get_name()

        print(generate_ldp_version_header(), file=fd)
        print("/* Module Implementation %s */" % (mname), file=fd)
        print("", file=fd)
        print("#include \"ECOA.h\"", file=fd)
        print("#include \"" + mname + ".h\"", file=fd)
        print("", file=fd)
        for lib in libraries:
            print("#include \"" + fix_C_libname(lib) + ".h\"", file=fd)
        print("", file=fd)
        print("/* Entry points for lifecycle operations */", file=fd)
        print("void " + mname + "__INITIALIZE__received(" + mname + "__context* context)", file=fd)
        print("{", file=fd)
        print(default_generated_comment, file=fd)
        print("}", file=fd)
        print("", file=fd)
        print("void " + mname + "__START__received(" + mname + "__context* context)", file=fd)
        print("{", file=fd)
        print(default_generated_comment, file=fd)
        print("}", file=fd)
        print("", file=fd)
        print("void " + mname + "__STOP__received(" + mname + "__context* context)", file=fd)
        print("{", file=fd)
        print(default_generated_comment, file=fd)
        print("}", file=fd)
        print("", file=fd)
        print("void " + mname + "__SHUTDOWN__received(" + mname + "__context* context)", file=fd)
        print("{", file=fd)
        print(default_generated_comment, file=fd)
        print("}", file=fd)
        print("", file=fd)

        for (opname, op) in mtype.get_operations().items():
            if op.get_type() == 'ER':

                signature = "void " + mname + "__" + op.get_name() + "__received(" + mname \
                            + "__context* context"
                signature += generate_header_fct(op, with_input=True)
                signature += ")"
                print(signature, file=fd)

                print("{", file=fd)
                print(default_generated_comment, file=fd)
                print("}", file=fd)
                print("", file=fd)
            elif op.get_type() == 'RR':
                signature = "void " + mname + "__" + op.get_name() + "__request_received(" \
                            + mname + "__context* context"
                signature += ", const ECOA__uint32 ID"
                signature += generate_header_fct(op, with_input=True)
                signature += ")"
                print(signature, file=fd)
                print("{", file=fd)
                print(default_generated_comment, file=fd)
                print("}", file=fd)
                print("", file=fd)

            elif op.get_type() == 'ARS':
                signature = "void " + mname + "__" + op.get_name() + "__response_received(" \
                            + mname + "__context* context"
                signature += ", const ECOA__uint32 ID"
                signature += ", const ECOA__return_status status"
                signature += generate_header_fct(op, with_output=True, is_output_const=True,
                                                 output_mode=False)
                signature += ")"
                print(signature, file=fd)
                print("{", file=fd)
                print(default_generated_comment, file=fd)
                print("}", file=fd)
                print("", file=fd)

            elif op.get_type() == 'DRN':
                signature = "void " + mname + "__" + op.get_name() + "__updated(" + mname \
                            + "__context* context){\n"
                signature += default_generated_comment+"\n"
                signature += "}\n"
                print(signature, file=fd)

        if mtype.is_fault_handler() is True:
            print("/* Fault Handling API */", file=fd)
            print("", file=fd)
            print("void " + mname + "__error_notification(", file=fd)
            print("    " + mname + "__context* context,", file=fd)
            print("    const ECOA__error_id error_id)", file=fd)
            print("{", file=fd)
            print(default_generated_comment, file=fd)
            print("}", file=fd)

        fd.close()


def generate_H_user_context(directory, mimpl, mtype, libraries, force_flag):
    h_filename = os.path.join(directory, mimpl.get_name() + '_user_context.h')

    if file_need_generation(h_filename,
                            force_flag,
                            "    A module header user_context already exists for " + mimpl.get_name()):

        fd = open(h_filename, 'w')

        mname = mimpl.get_name()

        print(generate_ldp_version_header(), file=fd)
        print("/* Module User Context Header for module %s */" % (mname), file=fd)
        print("#if !defined(" + str.upper(mname) + "_USER_CONTEXT_H)", file=fd)
        print("#define " + str.upper(mname) + "_USER_CONTEXT_H", file=fd)
        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("extern \"C\" {", file=fd)
        print("#endif /* __cplusplus */", file=fd)
        print("", file=fd)
        print("/*", file=fd)
        print(" * @file " + mname + "_user_context.h", file=fd)
        print(" */", file=fd)
        print("", file=fd)
        for lib in libraries:
            print("#include \"" + fix_C_libname(lib) + ".h\"", file=fd)

        if mtype.has_user_context():
            print("/* Module User Context Structure */", file=fd)
            print("typedef struct", file=fd)
            print("{", file=fd)
            print("    /*********** START USER-WRITTEN USER ***********/", file=fd)
            print("", file=fd)
            print("    /*********** END USER-WRITTEN USER ***********/", file=fd)
            print("} " + mname + "_user_context;", file=fd)

        if mtype.has_warm_start_context():
            print("\n", file=fd)
            print("/* Warm start Module Context structure */", file=fd)
            print("typedef struct", file=fd)
            print("{", file=fd)
            print("    /************* START USER-WRITTEN CODE *************/", file=fd)
            print("", file=fd)
            print("    /*************** END USER-WRITTEN CODE *************/", file=fd)
            print("} " + mname + "_warm_start_context;", file=fd)

        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("} ", file=fd)
        print("#endif /* __cplusplus */", file=fd)
        print("", file=fd)
        print("#endif  /* " + str.upper(mname) + "_USER_CONTEXT_H */", file=fd)

        fd.close()


def generate_H_module(directory, mimpl, mtype, libraries,
                      force_flag):
    h_filename = os.path.join(directory, mimpl.get_name() + '.h')

    if not file_need_generation(h_filename,
                            force_flag,
                            "    A module H file already exists for " + mimpl.get_name()):
        return

    fd = open(h_filename, 'w')

    mname = mimpl.get_name()

    print(generate_ldp_version_header_warning(), file=fd)
    print("/* Module Header %s */" % (mname), file=fd)
    print("", file=fd)
    print("#if !defined(_" + str.upper(mname) + "_H)", file=fd)
    print("#define _" + str.upper(mname) + "_H", file=fd)
    print("", file=fd)
    print("#if defined(__cplusplus)", file=fd)
    print("extern \"C\" {", file=fd)
    print("#endif", file=fd)
    print("", file=fd)
    print("#include \"ECOA.h\"", file=fd)
    for lib in libraries.keys():
        print("#include \"" + fix_C_libname(lib) + ".h\"", file=fd)
    print("#include \"%s_container.h\"" % (mname), file=fd)

    print("", file=fd)
    print("/* Entry points for lifecycle operations */", file=fd)
    print("void " + mname + "__INITIALIZE__received(" + mname + "__context* context);", file=fd)
    print("", file=fd)
    print("void " + mname + "__START__received(" + mname + "__context* context);", file=fd)
    print("", file=fd)
    print("void " + mname + "__STOP__received(" + mname + "__context* context);", file=fd)
    print("", file=fd)
    print("void " + mname + "__SHUTDOWN__received(" + mname + "__context* context);", file=fd)
    print("", file=fd)

    for (opname, op) in mtype.get_operations().items():
        if op.get_type() == 'ER':

            signature = "void " + mname + "__" + op.get_name() + "__received(" + mname \
                        + "__context* context"
            signature += generate_header_fct(op, with_input=True)
            signature += ");"
            print(signature, file=fd)
            print("", file=fd)
        elif op.get_type() == 'RR':
            signature = "void " + mname + "__" + op.get_name() + "__request_received(" + mname \
                        + "__context* context"
            signature += ", const ECOA__uint32 ID"
            signature += generate_header_fct(op, with_input=True)
            signature += ");"
            print(signature, file=fd)
            print("", file=fd)

        elif op.get_type() == 'ARS':
            signature = "void " + mname + "__" + op.get_name() + "__response_received(" + mname \
                        + "__context* context"
            signature += ", const ECOA__uint32 ID"
            signature += ", const ECOA__return_status status"
            signature += generate_header_fct(op, with_output=True, is_output_const=True,
                                             output_mode=False)
            signature += ");"
            print(signature, file=fd)
            print("", file=fd)

        elif op.get_type() == 'DRN':
            signature = "void " + mname + "__" + op.get_name() + "__updated(" + mname \
                        + "__context* context);"
            print(signature, file=fd)
            print("", file=fd)

    if mtype.is_fault_handler():
        print("/* Fault Handling API */", file=fd)
        print("", file=fd)
        print("void " + mname + "__error_notification(", file=fd)
        print("    " + mname + "__context* context,", file=fd)
        print("    const ECOA__error_id error_id);", file=fd)

    print("", file=fd)
    print("#if defined(__cplusplus)", file=fd)
    print("} ", file=fd)
    print("#endif", file=fd)
    print("", file=fd)
    print("#endif  /* _" + str.upper(mname) + "_H */", file=fd)

    fd.close()
