# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa_genplatform.generators.C.operation_generator import generate_header_fct
from ecoa_genplatform.generators.fix_names import fix_C_data_type

_template_H_ES_function="void #PREFIXE#_#MODULE_IMPL_NAME#__send__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context #PARAMETERS_IN#);\n"

_template_H_DW_function="// #OPERATION_NAME#\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_write_access__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #MODULE_IMPL_NAME#_container__#OPERATION_NAME#_handle* data_handle);\n\
\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__cancel_write_access__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #MODULE_IMPL_NAME#_container__#OPERATION_NAME#_handle* data_handle);\n\
\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__publish_write_access__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #MODULE_IMPL_NAME#_container__#OPERATION_NAME#_handle* data_handle);\n\
\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__write__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #TYPE_NAME# *data);\n\n"

_template_H_DR_function="// #OPERATION_NAME#\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__get_read_access__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #MODULE_IMPL_NAME#_container__#OPERATION_NAME#_handle* data_handle);\n\
\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__release_read_access__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #MODULE_IMPL_NAME#_container__#OPERATION_NAME#_handle* data_handle);\n\
\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__read__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #TYPE_NAME# *data);\n\n"

_template_H_RR_function="ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__response_send__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        const ECOA__uint32 ID #PARAMETERS_OUT#);\n"
_template_H_SRS_function="ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__request_sync__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context #PARAMETERS#);\n"
_template_H_ARS_function="ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__request_async__#OPERATION_NAME#(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        ECOA__uint32 *ID #PARAMETERS_OUT#);\n"

_template_H_PROPERTY_function="void #PREFIXE#_#MODULE_IMPL_NAME#__get_#PROPERTY_NAME#_value(\n\
        #MODULE_IMPL_NAME#__context *context,\n\
        #PROPERTY_TYPE_NAME# *value);\n"

_template_H_PINFO_function="ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__read_#PINFO_NAME#(\n\
        #MODULE_IMPL_NAME#__context* context,\n\
        ECOA__byte *memory_address,\n\
        ECOA__uint32 in_size,\n\
        ECOA__uint32 *out_size);\n\
ECOA__return_status #PREFIXE#_#MODULE_IMPL_NAME#__seek_#PINFO_NAME#(\n\
        #MODULE_IMPL_NAME#__context* context,\n\
        ECOA__int32 offset,\n\
        ECOA__seek_whence_type whence,\n\
ECOA__uint32 *new_position);\n"

_template_H_user_code = "void #PREFIXE#_#MODULE_IMPL_NAME#__concat(#MODULE_IMPL_NAME#__context *context,ECOA__log *log, char *str);\n"

def generate_C_encaps_h(module_impl, module_type, prefix, pattern_dict):
    text = ""
    current_file_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_file_dir,"templates","C_header_template.h")) as file:
        text = file.read()

    functions_ES =""
    functions_DW =""
    functions_DR =""
    functions_RR =""
    functions_SRS =""
    functions_ARS =""
    functions_user_code=""
    functions_PROPERTY = ""
    functions_PINFO = ""

    # operations
    for op in module_type.operations.values():
        if op.type == 'ES':
            parameters_str = generate_header_fct(op, with_input=True)
            functions_ES += _template_H_ES_function.replace('#PARAMETERS_IN#', parameters_str)\
                                                   .replace('#OPERATION_NAME#', op.name)
        elif op.type == 'DW':
            functions_DW += _template_H_DW_function.replace('#TYPE_NAME#', fix_C_data_type(op.params[0].type))\
                                                   .replace('#OPERATION_NAME#', op.name)
        elif op.type == 'DR' or op.type == 'DRN':
            functions_DR += _template_H_DR_function.replace('#TYPE_NAME#', fix_C_data_type(op.params[0].type))\
                                                   .replace('#OPERATION_NAME#', op.name)
        elif op.type == 'RR':
            parameters_str = generate_header_fct(op, with_output=True, is_output_const=True, output_mode=False)
            functions_RR += _template_H_RR_function.replace("#PARAMETERS_OUT#", parameters_str)\
                                                   .replace('#OPERATION_NAME#', op.name)
        elif op.type == 'ARS':
            parameters_str = generate_header_fct(op, with_input=True)
            functions_ARS +=_template_H_ARS_function.replace("#PARAMETERS_OUT#", parameters_str)\
                                                    .replace('#OPERATION_NAME#', op.name)
        elif op.type == 'SRS':
            parameters_str = generate_header_fct(op, with_input=True, with_output=True)
            functions_SRS +=_template_H_SRS_function.replace("#PARAMETERS#", parameters_str)\
                                                    .replace('#OPERATION_NAME#', op.name)
        else:
            pass

    # properties
    for pty in module_type.properties.values():
       pty_type =  fix_C_data_type(pty.get_type())
       functions_PROPERTY += _template_H_PROPERTY_function.replace('#PROPERTY_NAME#', pty.name)\
                                                          .replace("#PROPERTY_TYPE_NAME#", pty_type)

    # PINFO
    for pinfo in module_type.private_pinfo + module_type.public_pinfo :
        functions_PINFO += _template_H_PINFO_function.replace('#PINFO_NAME#', pinfo)


    # user code
    if "USER CODE HEADER" in pattern_dict:
        functions_user_code = pattern_dict["USER CODE HEADER"]
    else:
        functions_user_code = _template_H_user_code

    # replace
    text=text.replace('#EVENTSENT_FUNCTIONS#', functions_ES)\
             .replace('#WRITTEN_VD_FUNCTIONS#', functions_DW)\
             .replace('#READ_VD_FUNCTIONS#', functions_DR)\
             .replace('#RR_FUNCTIONS#', functions_RR)\
             .replace('#SRS_FUNCTIONS#', functions_SRS)\
             .replace('#ARS_FUNCTIONS#', functions_ARS)\
             .replace('#USER_CODE#', functions_user_code)\
             .replace('#PROPERTY_FUNCTIONS#', functions_PROPERTY)\
             .replace('#PINFO_FUNCTIONS#', functions_PINFO)

    text=text.replace("#MODULE_IMPL_NAME#", module_impl.name)\
             .replace("#PREFIXE#", prefix)

    return text
