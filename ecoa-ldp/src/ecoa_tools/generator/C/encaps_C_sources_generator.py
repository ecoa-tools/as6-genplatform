# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ecoa_genplatform.generators.C.operation_generator import generate_header_fct, generate_param_fct_call2
from .templates.C_templates import C_Templates
from ecoa_genplatform.generators.fix_names import fix_C_data_type

def _generate_RR_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__response_send__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        parameters_header = generate_header_fct(operation, with_output=True, is_output_const=True, output_mode=False)
        parameters_names = generate_param_fct_call2(operation, with_output=True)
        return C_templates.template_C_RR_response.replace('#PARAMETERS_OUT#', parameters_header)\
                                      .replace('#PARAMETERS_OUT_NAMES#', parameters_names)\
                                      .replace('#OPERATION_NAME#', operation.name)

def _generate_SRS_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__request_sync__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        parameters_headers = generate_header_fct(operation, with_input=True, with_output=True, is_output_const=False, output_mode=True)
        parameters_names = generate_param_fct_call2(operation, with_input=True, with_output=True)
        return C_templates.template_C_RR_synchrone.replace('#PARAMETERS_INOUT#', parameters_headers) \
                                       .replace('#PARAMETERS_INOUT_NAMES#', parameters_names)\
                                       .replace('#OPERATION_NAME#', operation.name)

def _generate_ARS_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__request_async__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        parameters_headers = generate_header_fct(operation, with_input=True)
        parameters_names = generate_param_fct_call2(operation, with_input=True)
        return C_templates.template_C_RR_asynchrone.replace('#PARAMETERS_IN#', parameters_headers)\
                                        .replace('#PARAMETERS_IN_NAMES#', parameters_names)\
                                        .replace('#OPERATION_NAME#', operation.name)

def _generate_ES_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__send__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        parameters_header = generate_header_fct(operation, with_input=True)
        parameters_names = generate_param_fct_call2(operation, with_input=True)
        return C_templates.template_C_ES_functions.replace('#PARAMETERS_IN#', parameters_header)\
                                   .replace('#PARAMETERS_IN_NAMES#', parameters_names)\
                                   .replace('#OPERATION_NAME#', operation.name)

def _generate_DW_write_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__write__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        return C_templates.template_C_DW_write.replace('#OPERATION_NAME#', operation.name)\
                                   .replace('#DATA_TYPE#', fix_C_data_type(operation.params[0].type))

def _generate_DW_get_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__get_write_access__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        return C_templates.template_C_DW_get.replace('#OPERATION_NAME#', operation.name)

def _generate_DW_publish_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__publish_write_access__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[ macro_name]
    else:
        return C_templates.template_C_DW_publish.replace('#OPERATION_NAME#', operation.name)

def _generate_DW_cancel_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__cancel_write_access__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        return C_templates.template_C_DW_cancel.replace('#OPERATION_NAME#', operation.name)

def _generate_DR_get_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__get_read_access__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        return C_templates.template_C_DR_get.replace('#OPERATION_NAME#', operation.name)

def _generate_DR_read_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__read__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        return C_templates.template_C_DR_read.replace('#OPERATION_NAME#', operation.name)\
                                  .replace('#DATA_TYPE#', fix_C_data_type(operation.params[0].type))

def _generate_DR_release_function(operation, pattern_dict, C_templates, macro_prefix):
    macro_name = macro_prefix +"__release_read_access__"+operation.name
    if macro_name in pattern_dict:
        return pattern_dict[macro_name]
    else:
        return C_templates.template_C_DR_release.replace('#OPERATION_NAME#', operation.name)

def _generate_header(pattern_dict, C_templates):
    if "HEADER" in pattern_dict:
        return pattern_dict["HEADER"]
    else:
        return C_templates.template_C_HEADER

def _generate_include(pattern_dict, C_templates):
    if "INCLUDE" in pattern_dict:
        return pattern_dict["INCLUDE"]
    else:
        return C_templates.template_C_INCLUDE

def _generate_log_API(pattern_dict):
    string=""
    if "LOG RELATED API" in pattern_dict:
        string = pattern_dict["LOG RELATED API"]
    else:
        current_file_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_file_dir,"templates","C_log_API_template.c")) as file:
            string = file.read()
    return string

def _generate_time_API(pattern_dict):
    string=""
    if "TIME RELATED API" in pattern_dict:
        string = pattern_dict["TIME RELATED API"]
    else:
        current_file_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_file_dir,"templates","C_time_API_template.c")) as file:
            string = file.read()
    return string

def _generate_user_code(pattern_dict):
    string=""
    if "USER CODE" in pattern_dict:
        string = pattern_dict["USER CODE"]
    else:
        current_file_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(current_file_dir,"templates","C_User_Code_template.c")) as file:
            string = file.read()
    return string

def _generate_properties(pty, pattern_dict, C_templates, macro_prefix):
    string = ""
    macro_name = macro_prefix+"__get__"+pty.name+"_value"
    if macro_name in pattern_dict:
        string = pattern_dict[macro_name]
    else:
        pty_type =  fix_C_data_type(pty.get_type())
        string = C_templates.template_C_PTY_get.replace('#PROPERTY_NAME#', pty.name)\
                                               .replace('#PROPERTY_TYPE_NAME#', pty_type)
    return string

def _generate_Pinfo_seek(pinfo,  pattern_dict, C_templates, macro_prefix):
    string=""
    macro_name = macro_prefix+"__seek__"+pinfo
    if macro_name in pattern_dict:
        string=pattern_dict[macro_name]
    else:
        string = C_templates.template_C_PINFO_seek.replace('#PINFO_NAME#', pinfo)
    return string

def _generate_Pinfo_read(pinfo,  pattern_dict, C_templates, macro_prefix):
    string=""
    macro_name = macro_prefix+"__read__"+pinfo

    if macro_name in pattern_dict:
        string=pattern_dict[macro_name]
    else:
        string = C_templates.template_C_PINFO_read.replace('#PINFO_NAME#', pinfo)
    return string

def generate_C_encaps_c(module_impl, module_type, prefix, pattern_dict):
    """Generate source C file for encapsulation functions of module_impl

    Args:
        module_impl   (`.Module_Implementation`):The module implementation
        module_type   (`.Module_Type`):The module type
        prefix        (str):The prefix of function names
        pattern_dict  (dict):The pattern dictionary that contains code of some functions

    Return:
        (str): string to write in file
    """
    C_templates = C_Templates()
    text = ""

    text += _generate_header(pattern_dict, C_templates) +"\n"
    text += _generate_include(pattern_dict, C_templates) +"\n"
    text += _generate_user_code(pattern_dict) + "\n"
    text += _generate_log_API(pattern_dict) +"\n"
    text += _generate_time_API(pattern_dict) +"\n"

    # container operations
    functions_ES ="\n/************* EVENT SEND ****************/\n"
    functions_DW ="\n/************ DATA WRITTEN ***************/\n"
    functions_DR ="\n/************* DATA READ *****************/\n"
    functions_RR ="\n/************ RESPONSE SEND **************/\n"
    functions_SRS ="\n/************ REQUEST SYNC **************/\n"
    functions_ARS ="\n/*********** REQUEST ASYNC **************/\n"

    macro_prefix = module_impl.name
    for op in module_type.operations.values():
        if op.type == 'ES':
            functions_ES += _generate_ES_function(op, pattern_dict, C_templates, macro_prefix)
        elif op.type == 'DW':
            functions_DW += _generate_DW_get_function(op, pattern_dict, C_templates, macro_prefix)
            functions_DW += _generate_DW_publish_function(op, pattern_dict, C_templates, macro_prefix)
            functions_DW += _generate_DW_cancel_function(op, pattern_dict, C_templates, macro_prefix)
            functions_DW += _generate_DW_write_function(op, pattern_dict, C_templates, macro_prefix)
        elif op.type == 'DR' or op.type == 'DRN':
            functions_DR += _generate_DR_release_function(op, pattern_dict, C_templates, macro_prefix)
            functions_DR += _generate_DR_read_function(op, pattern_dict, C_templates, macro_prefix)
            functions_DR += _generate_DR_get_function(op, pattern_dict, C_templates, macro_prefix)
        elif op.type == 'RR':
            functions_RR += _generate_RR_function(op, pattern_dict, C_templates, macro_prefix)
        elif op.type == 'SRS':
            functions_SRS += _generate_SRS_function(op, pattern_dict, C_templates, macro_prefix)
        elif op.type == 'ARS':
            functions_ARS += _generate_ARS_function(op, pattern_dict, C_templates, macro_prefix)
        else:
            pass

    text += functions_ES +"\n"
    text += functions_DW +"\n"
    text += functions_DR +"\n"
    text += functions_RR +"\n"
    text += functions_SRS +"\n"
    text += functions_ARS +"\n"

    # properties
    for pty in module_type.properties.values():
        text += _generate_properties(pty, pattern_dict, C_templates, macro_prefix)

    #PINFO
    for pinfo in module_type.private_pinfo + module_type.public_pinfo:
        text += "// PINFO "+pinfo+"\n"
        text += _generate_Pinfo_seek(pinfo, pattern_dict, C_templates, macro_prefix)
        text += _generate_Pinfo_read(pinfo, pattern_dict, C_templates, macro_prefix)+"\n"

    text = text.replace("#MODULE_IMPL_NAME#", module_impl.name)\
               .replace("#PREFIXE#", prefix)

    return text
