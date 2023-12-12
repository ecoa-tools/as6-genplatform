# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from .utilities import expand_data_type
from ..force_generation import file_need_generation


spaces = "	"


log_entries_header = """
extern const char* $MODULE_SHORT_NAME$;

void $module_name$_log_info($module_name$__context* context, char *msg, ...);
void $module_name$_log($module_name$__context* context, char *msg, ...);
"""

log_entries = """
const char* $MODULE_SHORT_NAME$ = "$MODULE_SHORT_NAME$: ";

void $module_name$_log_info($module_name$__context* context, char *msg, ...) {
    ECOA__log log;
    strncpy(log.data, $MODULE_SHORT_NAME$, ECOA__LOG_MAXSIZE);
    va_list argp;
    va_start(argp, msg);
    vsnprintf((char *) log.data + strnlen($MODULE_SHORT_NAME$, ECOA__LOG_MAXSIZE),
    ECOA__LOG_MAXSIZE, msg, argp);
    va_end(argp);
    log.current_size = strnlen((char *) &log.data, ECOA__LOG_MAXSIZE);
    $module_name$_container__log_info(context, log);
}

void $module_name$_log($module_name$__context* context, char *msg, ...) {
    ECOA__log log;
    strncpy(log.data, $MODULE_SHORT_NAME$, ECOA__LOG_MAXSIZE);
    va_list argp;
    va_start(argp, msg);
    vsnprintf((char *) log.data + strnlen($MODULE_SHORT_NAME$, ECOA__LOG_MAXSIZE),
    ECOA__LOG_MAXSIZE, msg, argp);
    va_end(argp);
    log.current_size = strnlen((char *) &log.data, ECOA__LOG_MAXSIZE);
    $module_name$_container__log_debug(context, log);
}
"""

setter = """
void $module_name$__set_$data_name$($module_name$__context *context,
        $data_declaration$) {
    $module_name$_container__$data_name$_handle handle;

    ECOA__return_status return_status;

    return_status =
            $module_name$_container__$data_name$__get_write_access(
                    context, &handle);

    if (return_status == ECOA__return_status_OK
            || return_status == ECOA__return_status_DATA_NOT_INITIALIZED) {

        *(handle.data) = $data_access$;

        return_status =
                $module_name$_container__$data_name$__publish_write_access(
                        context, &handle);

        if (return_status != ECOA__return_status_OK) {
            $module_name$_log(context,
                    "$data_name$: publish_write_access FAILED / error = %d", return_status);
        }
    } else {
        $module_name$_log(context,
                "$data_name$: get_write_access FAILED / error = %d", return_status);
    }
}
"""

getter = """
void $module_name$__get_$data_name$($module_name$__context* context,
        $data_declaration$) {
    /* assert: data != NULL */

    $module_name$_container__$data_name$_handle handle;
    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = $module_name$_container__$data_name$__get_read_access(context,
            &handle);
    if (return_status == ECOA__return_status_OK) {

        *data = *(handle.data);

        return_status = $module_name$_container__$data_name$__release_read_access(context,
                &handle);
        if (return_status != ECOA__return_status_OK) {
            $module_name$_log(context, "$data_name$: Fail on release_read_access / error = %d",
                    return_status);
        }
    } else {
        if (return_status != ECOA__return_status_NO_DATA) {
            $module_name$_log(context, "$data_name$: Fail on get_read_access / error = %d",
                    return_status);
        }
    }
}
"""

sync_requester = """
void $module_name$__request_$operation_name$($module_name$__context* context
        $data_declaration$) {
    /* assert: data != NULL */

    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = $module_name$_container__$operation_name$__request_sync(context
            $data$);
    if (return_status != ECOA__return_status_OK) {
        $module_name$_log(context, "$operation_name$: Fail on request_sync / error = %d",
                    return_status);
    }
}
"""

async_requester = """
void $module_name$__async_request_$operation_name$($module_name$__context* context,
        $data_declaration$) {
    /* assert: data != NULL */

    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = $module_name$_container__$operation_name$__request_async(context
            $data$);
    if (return_status != ECOA__return_status_OK) {
        $module_name$_log(context, "$operation_name$: Fail on request_async / error = %d",
                    return_status);
    }
}
"""


def generate_helper_call_params(op_type, with_input=False, with_output=False):
    """Generate parameters string for a function call in C.

        :param op_type:
        :param bool with_input: include input parameter. False by default.
        :param bool with_output: include output parameter. False by default.
    """
    string = ""
    for param in op_type.params:
        if param.direction == 'input' and with_input:
            string += ", " + param.name
        elif param.direction == 'output' and with_output:
            string += ", " + param.name
    return string


def generate_helper_signature_params(op_type, with_input=False, with_output=False,
                                     is_input_const=False, is_output_const=False):
    """Generate parameters string for a function declaration header in C.

            :param op_type:
        :return:
        :param bool with_input: include input parameter. False by default.
        :param bool with_output: include output parameter. False by default.
        :param bool is_input_const: add 'const' for input parameters. False by default.
        :param bool is_output_const: add 'const' for output parameters. False by default.
    """
    header_string = ""

    for param in op_type.params:
        if param.direction == 'input' and with_input:
            if is_input_const:
                header_string += ", const "
            else:
                header_string += ", "

            if param.is_complex:
                header_string += param.type.replace(':', '__') + '* ' + param.name
            else:
                header_string += param.type.replace(':', '__') + ' ' + param.name

        elif param.direction == 'output' and with_output:
            if is_output_const:
                header_string += ", const "
            else:
                header_string += ", "
            header_string += param.type.replace(':', '__') + '* ' + param.name
    return header_string


def generate_C_module_helpers_test(directory, mimpl, mtype,
                                   libraries, force_flag):
    data_already_declared = []

    c_filename = os.path.join(directory, mimpl.get_name() + '_helpers_test.c')

    if file_need_generation(c_filename,
                            force_flag,
                            "    A module test already exists for " + mimpl.get_name()):

        fd = open(c_filename, 'w')

        mname = mimpl.get_name()

        print("/* Generated by LDP */", file=fd)
        print("/* Helpers for the Module Implementation %s */" % mname, file=fd)
        print("", file=fd)
        print("#include \"ECOA.h\"", file=fd)
        print("#include \"" + mname + ".h\"", file=fd)
        print("#include \"" + mname + "_helpers.h\"", file=fd)
        print("", file=fd)
        for lib in libraries:
            print("#include \"" + lib + ".h\"", file=fd)
        print("", file=fd)
        print("int main(int argc, char *argv[])", file=fd)
        print("{", file=fd)
        print(spaces + mname + "__context context;", file=fd)
        print("", file=fd)

        for (_, op) in mtype.get_operations().items():
            if op.get_type() == 'DW':

                data_type = op.get_params()[0].type
                is_data_complex = op.get_params()[0].is_complex

                data_type = expand_data_type(data_type)

                if data_type not in data_already_declared:
                    print(data_type + " " + data_type + "_data;", file=fd)
                    data_already_declared.append(data_type)

                signature = mname + "__set_" + op.get_name() + "(&context, "

                if is_data_complex:
                    signature += "&" + data_type + "_data);"
                else:
                    signature += data_type + "_data);"

                print(signature, file=fd)
                print("", file=fd)
            elif op.get_type() == 'DR':
                data_type = op.get_params()[0].type
                data_type = expand_data_type(data_type)

                if data_type not in data_already_declared:
                    print(data_type + " " + data_type + "_data;", file=fd)
                    data_already_declared.append(data_type)
                print(
                    mname + "__get_" + op.get_name() + "(&context, &" + data_type + "_data);",
                    file=fd)
                print("", file=fd)

        print("    return 0;", file=fd)
        print("}", file=fd)
        fd.close()


def generate_C_helpers_makefile(directory, mimpl, force_flag):
    c_filename = os.path.join(directory, mimpl.get_name() + '_helpers.mak')

    if file_need_generation(c_filename,
                            force_flag,
                            "    A module test makefile already exists for " + mimpl.get_name()):

        fd = open(c_filename, 'w')
        mname = mimpl.get_name()

        print("all: helpers", file=fd)
        print("", file=fd)
        print("helpers:", file=fd)
        print(
            "\tgcc -g -Wall -o helpers_test " + mname + "_helpers.c " + mname + "_test_container.c "
            + mname + "_helpers_test.c -I ../inc -I ../inc-gen/ -I ../../../../0-Types/inc-gen/ "
                      "-DECOA_64BIT_SUPPORT",
            file=fd)
        print("", file=fd)
        print("clean:", file=fd)
        print("\trm -f helpers_test", file=fd)
        fd.close()


def generate_H_module_helpers(directory, mimpl, mtype,
                              libraries, force_flag):
    c_filename = os.path.join(directory, mimpl.get_name() + '_helpers.h')

    if file_need_generation(c_filename,
                            force_flag,
                            "    A module test already exists for " + mimpl.get_name()):

        fd = open(c_filename, 'w')

        mname = mimpl.get_name()

        print("/* Generated by LDP */", file=fd)
        print("/* Helpers for the Module Implementation %s */" % mname, file=fd)
        print("", file=fd)
        print("#if !defined(" + mname.upper() + "_HELPERS)", file=fd)
        print("#define " + mname.upper() + "_HELPERS", file=fd)
        print("#include \"ECOA.h\"", file=fd)
        print("#include \"" + mname + ".h\"", file=fd)
        print("", file=fd)
        for lib in libraries:
            print("#include \"" + lib + ".h\"", file=fd)
        print("", file=fd)

        print("#if defined(__cplusplus)", file=fd)
        print("extern \"C\" {", file=fd)
        print("#endif", file=fd)

        signature = log_entries_header.replace("$MODULE_SHORT_NAME$", mname.upper())
        signature = signature.replace("$module_name$", mname)
        print(signature, file=fd)
        print("", file=fd)

        for (_, op) in mtype.get_operations().items():
            if op.get_type() == 'DW':

                data_type = op.get_params()[0].type
                data_type = expand_data_type(data_type)
                is_data_complex = op.get_params()[0].is_complex

                signature = "void " + mname + "__set_" + op.get_name() + "(" + mname \
                            + "__context* context, " + data_type
                if is_data_complex is True:
                    signature += "* data);"
                else:
                    signature += " data);"

                print(signature, file=fd)

            elif op.get_type() == 'DR' or op.get_type() == 'DRN':
                data_type = op.get_params()[0].type
                data_type = expand_data_type(data_type)

                print(
                    "void " + mname + "__get_" + op.get_name() + "(" + mname + "__context* context, "
                    + data_type + "* data);",
                    file=fd)

            elif op.get_type() == 'SRS':
                signature = "void " + mname + "__request_" + op.get_name() + "(" + mname \
                            + "__context* context"
                signature += generate_helper_signature_params(op, with_input=True, is_input_const=False,
                                                              with_output=True, is_output_const=False)
                signature += ");"
                print(signature, file=fd)
                print("", file=fd)

            elif op.get_type() == 'ARS':
                signature = "void " + mname + "__async_request_" + op.get_name() + "(" + mname \
                            + "__context* context"
                signature += ", const ECOA__uint32 ID"
                signature += generate_helper_signature_params(op, with_input=True, is_input_const=False,
                                                              with_output=False, is_output_const=False)
                signature += ");"
                print(signature, file=fd)
                print("", file=fd)

        print("", file=fd)
        print("#if defined(__cplusplus)", file=fd)
        print("}", file=fd)
        print("#endif", file=fd)

        print("#endif /* " + mname.upper() + "_HELPERS */", file=fd)
        fd.close()


def generate_C_module_helpers(directory, mimpl, mtype,
                              libraries, force_flag):
    c_filename = os.path.join(directory, mimpl.get_name() + '_helpers.c')

    if file_need_generation(c_filename,
                            force_flag,
                            "    A module test container already exists for" + mimpl.get_name()):

        fd = open(c_filename, 'w')

        mname = mimpl.get_name()

        print("/* Module Helpers Implementation for %s */" % mname, file=fd)
        print("", file=fd)
        print("/* @file " + mname + "_helpers.c", file=fd)
        print(" * This is the Module Test Container for Module " + mname, file=fd)
        print(" * This file is generated by the ECOA tools and shall not be modified", file=fd)
        print(" */", file=fd)
        print("", file=fd)
        print("/* Generated by LDP */", file=fd)
        print("", file=fd)
        print("#include <stdio.h>", file=fd)
        print("#include <string.h>", file=fd)
        print("#include <stdarg.h>", file=fd)
        print("", file=fd)
        print("#include \"ECOA.h\"", file=fd)
        print("#include \"" + mname + "_container.h\"", file=fd)
        print("#include \"" + mname + "_helpers.h\"", file=fd)
        print("", file=fd)
        for lib in libraries:
            print("#include \"" + lib + ".h\"", file=fd)
        print("", file=fd)

        signature = log_entries.replace("$MODULE_SHORT_NAME$", mname.upper())
        signature = signature.replace("$module_name$", mname)
        print(signature, file=fd)
        print("", file=fd)

        for (opname, op) in mtype.get_operations().items():
            if op.get_type() == 'DW':
                data_type = op.get_params()[0].type
                data_type = expand_data_type(data_type)
                is_data_complex = op.get_params()[0].is_complex

                if is_data_complex:
                    data_declaration = data_type + "* data"
                    data_access = "*data"
                else:
                    data_declaration = data_type + " data"
                    data_access = "data"

                signature = setter.replace("$module_name$", mname)
                signature = signature.replace("$data_name$", opname)
                signature = signature.replace("$data_declaration$", data_declaration)
                signature = signature.replace("$data_access$", data_access)
                print(signature, file=fd)

                print("", file=fd)

            elif op.get_type() == 'DR' or op.get_type() == 'DRN':
                data_type = op.get_params()[0].type
                data_type = expand_data_type(data_type)

                data_declaration = data_type + "* data"

                signature = getter.replace("$module_name$", mname)
                signature = signature.replace("$data_name$", opname)
                signature = signature.replace("$data_declaration$", data_declaration)
                print(signature, file=fd)

                print("", file=fd)

            elif op.get_type() == 'SRS':
                signature = sync_requester.replace("$module_name$", mname)
                signature = signature.replace("$operation_name$", op.get_name())
                signature = signature.replace("$data_declaration$",
                                              generate_helper_signature_params(op, with_input=True,
                                                                               is_input_const=False,
                                                                               is_output_const=False))
                signature = signature.replace("$data$", generate_helper_call_params(op, with_input=True,
                                                                                    with_output=True))
                print(signature, file=fd)
                print("", file=fd)

            elif op.get_type == 'ARS':
                signature = async_requester.replace("$module_name$", mname)
                signature = signature.replace("$operation_name$", op.get_name())
                signature = signature.replace("$data_declaration$",
                                              generate_helper_signature_params(op, with_input=False,
                                                                               is_input_const=False,
                                                                               with_output=True,
                                                                               is_output_const=False))
                signature = signature.replace("$data$", generate_helper_call_params(op,
                                                                                    with_input=False,
                                                                                    with_output=True))
                print(signature, file=fd)
                print("", file=fd)

        print("", file=fd)

        fd.close()
