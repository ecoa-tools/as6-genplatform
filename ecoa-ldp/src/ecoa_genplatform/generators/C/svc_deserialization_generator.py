# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ..fix_names import fix_C_data_type, fix_C_libname
from ..version_header_generator import generate_ldp_version_header_cmake, generate_ldp_version_header_warning

def generate_svc_deserialized(service_definitions, directory,libraries):

    directory_svc = os.path.join(directory, "svc_deserial")
    os.makedirs(directory_svc, exist_ok=True)
    for service_dnf,_ in service_definitions.values():
        filename_h = os.path.join(directory_svc, "svc_"+service_dnf.name+"_deserial.h")
        filename_c = os.path.join(directory_svc, "svc_"+service_dnf.name+"_deserial.c")
        generate_svc_deserialized_h(service_dnf, filename_h)
        generate_svc_deserialized_c(service_dnf, filename_c, libraries)
    filename_h = os.path.join(directory_svc, "CMakeLists.txt")
    generate_cmake(service_definitions, filename_h)

template_header="uint32_t deserialized_#SERVICE_NAME#_#OP_NAME#(char* dest, char* src)"
template_header_data_serial="uint32_t serialized_#SERVICE_NAME#_#OP_NAME#(char* dest, char* src)"
template_header_param_size="uint32_t params_size_#SERVICE_NAME#_#OP_NAME#(void);"

def generate_svc_deserialized_h(service, filename):

    text = generate_ldp_version_header_warning()
    text +="#include \"ECOA.h\"\n"
    for libname in service.libraries:
        text += "#include \""+fix_C_libname(libname)+".h\"\n"

    for operation in service.operations:
        if operation.nature in ['CMD', 'NOTIFY']:
            text +=template_header.replace("#SERVICE_NAME#", service.name)\
                                         .replace("#OP_NAME#",operation.name)+";\n"
            text += template_header_param_size.replace("#SERVICE_NAME#", service.name)\
                                              .replace("#OP_NAME#",operation.name)+"\n"
        elif operation.nature == 'RR':
            text +=template_header.replace("#SERVICE_NAME#", service.name)\
                                         .replace("#OP_NAME#",operation.name+"_answer")+";\n"
            text +=template_header.replace("#SERVICE_NAME#", service.name)\
                                         .replace("#OP_NAME#",operation.name+"_request")+";\n"
            text += template_header_param_size.replace("#SERVICE_NAME#", service.name)\
                                              .replace("#OP_NAME#",operation.name+"_answer")+"\n"
            text += template_header_param_size.replace("#SERVICE_NAME#", service.name)\
                                              .replace("#OP_NAME#",operation.name+"_request")+"\n"
        elif operation.nature == 'DATA':
            text +=template_header.replace("#SERVICE_NAME#", service.name)\
                                         .replace("#OP_NAME#",operation.name)+";\n"
            text +=template_header_data_serial.replace("#SERVICE_NAME#", service.name)\
                                         .replace("#OP_NAME#",operation.name)+";\n"
            text += template_header_param_size.replace("#SERVICE_NAME#", service.name)\
                                              .replace("#OP_NAME#",operation.name)+"\n"

    text += "uint32_t min_buffer_size_"+service.name+"(void);\n"

    file = open(filename, 'w')
    print(text, file=file)
    file.close()


template_deserial="\
    deserialize_#DATA_TYPE_NAME#((void*) &dest[index_dest], &src[index_src], dest_length);\n\
    index_src += #DATA_SIZE#;\n\
    dest_length -= #DATA_SIZE#;\n\
    index_dest += sizeof(#DATA_TYPE_NAME#);\n"

def _current_size_of_datatype(datatype_name, datatype_category):
    if datatype_category in ['SIMPLE', 'CONSTANT', 'ENUM']:
        return "sizeof(" + datatype_name + ")"
    elif datatype_category in ["ARRAY", "VARIANT_RECORD"]:
        return "current_size_of_"+datatype_name +"(("+datatype_name+"*)&dest[index_dest])"
    else:
        return "size_of_" + datatype_name + "()"

def _generate_parameters_string(parameters, offset_string_dest, offset_string_src, libraries):
    params_str_tmp= ""
    params_str= ""
    for param in parameters:
        parameter = libraries[param.get_libname()][0].datatypes2[param.get_typename()]

        data_size_str = _current_size_of_datatype(fix_C_data_type(param.type), parameter.data_category)
        params_str_tmp += template_deserial.replace("#DATA_TYPE_NAME#", fix_C_data_type(param.type))\
                                      .replace("#DATA_SIZE#", data_size_str)
    if params_str_tmp != "":
        params_str +="    uint32_t index_dest = "+offset_string_dest+";\n"
        params_str +="    uint32_t index_src = "+offset_string_src+";\n"
        params_str +="    uint32_t dest_length = ECOA__UINT32_MAX; // max buffer size\n"
        params_str += params_str_tmp;
        params_str += "    return index_dest; \n"
    else:
        params_str += "    return " + offset_string_dest +";\n"
    return params_str;

def generate_svc_deserialized_c(service, filename, libraries):
    text = generate_ldp_version_header_warning()
    text +="#include \"ldp_network.h\"\n"
    text +="#include \"ECOA.h\"\n"
    text +="#include \"ECOA_simple_types_serialization.h\"\n"
    for libname in service.libraries:
        text += "#include \""+fix_C_libname(libname)+".h\"\n"
        text += "#include \""+fix_C_libname(libname)+"_serialization.h\"\n"

    for operation in service.operations:
        params_str=""
        if operation.nature in ['CMD', 'NOTIFY']:
            text += template_header.replace("#SERVICE_NAME#", service.name)\
                                   .replace("#OP_NAME#",operation.name)+"{\n"
            text += _generate_parameters_string(operation.inputs, "0","0", libraries)

        elif operation.nature == 'RR':
            text += template_header.replace("#SERVICE_NAME#", service.name)\
                                   .replace("#OP_NAME#",operation.name+"_answer")+"{\n"
            text += "    memcpy(&dest[0], src, sizeof(ECOA__uint32)); // copie ID\n"
            text += _generate_parameters_string(operation.outputs, "sizeof(ECOA__uint32)","sizeof(ECOA__uint32)", libraries)
            text += "}\n"

            ###############
            text += template_header.replace("#SERVICE_NAME#", service.name)\
                                   .replace("#OP_NAME#",operation.name+"_request")+"{\n"
            text += "    memcpy(&dest[0], src, sizeof(ECOA__uint32)); // TODO: what to do for 32bit OS?\n"
            text += _generate_parameters_string(operation.inputs, "sizeof(ECOA__uint32)","sizeof(ECOA__uint32)", libraries)

        elif operation.nature == 'DATA':
            text += template_header.replace("#SERVICE_NAME#", service.name)\
                                   .replace("#OP_NAME#",operation.name)+"{\n"
            text += _generate_parameters_string(operation.inputs, "0","0", libraries)
            text += "}\n"

            text += template_header_data_serial.replace("#SERVICE_NAME#", service.name)\
                                   .replace("#OP_NAME#",operation.name)+"{\n"
            data_str = fix_C_data_type(operation.inputs[0].type)
            text+= "    uint32_t added_size;\n"
            text+= "    serialize_"+data_str+"("

            if not operation.inputs[0].is_complex:
                text+="*"
            text+="("+data_str+"*) &src[0], &dest[0], ECOA__UINT32_MAX, &added_size);\n"
            text+= "    return added_size;\n"
        text += "}\n"

    text += generate_op_buffer_size(service)
    text += generate_min_buffer_size(service)

        # print(text)
    file = open(filename, 'w')
    print(text, file=file)
    file.close()

def generate_cmake(service_definitions, filename):

    text = generate_ldp_version_header_cmake()
    text += "cmake_minimum_required(VERSION 3.4)\n"

    text += "project(ecoa)\n"

    text += "include_directories(${CMAKE_CURRENT_SOURCE_DIR}/.)\n"
    if len(service_definitions) >0:
        text += "target_sources(ecoa PRIVATE ${${PROJECT_NAME}_svc_serial_src}\n"
        for svc_name in sorted(service_definitions.keys()):
            text+="   ${CMAKE_CURRENT_SOURCE_DIR}/svc_"+svc_name+"_deserial.c\n"
        text += ")\n"
    text += "target_include_directories(ecoa PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/.)\n"

    file = open(filename, 'w')
    print(text, file=file)
    file.close()




def generate_op_buffer_size(service):

    template="\
uint32_t params_size_#SERVICE_NAME#_#OP_NAME#(void){\n\
    return #PARAMS_SIZE#;\n\
}\n"
    text=""

    for op in service.operations:

        param_size="0"
        if op.nature in ['CMD', 'NOTIFY','DATA']:
            for param in op.inputs:
                param_size += "+sizeof("+fix_C_data_type(param.type)+")"
            text += template.replace("#OP_NAME#", op.name)\
                            .replace("#PARAMS_SIZE#", param_size)
        elif op.nature == 'RR':
            for param in op.inputs:
                param_size += "+sizeof("+fix_C_data_type(param.type)+")"
            text += template.replace("#OP_NAME#", op.name+"_request")\
                           .replace("#PARAMS_SIZE#", param_size)

            param_size="0"
            for param in op.outputs:
                param_size += "+sizeof("+fix_C_data_type(param.type)+")"
            text += template.replace("#OP_NAME#", op.name+"_answer")\
                           .replace("#PARAMS_SIZE#", param_size)

    return text.replace("#SERVICE_NAME#", service.name)

def generate_min_buffer_size(service):
    text = "uint32_t min_buffer_size_"+service.name+"(void){\n"
    text+= "    uint32_t max = 0;\n"
    text+= "    uint32_t tmp = 0;\n"
    for op in service.operations:
        if op.nature in ['CMD', 'NOTIFY','DATA']:
            text+= "    tmp = params_size_"+service.name+"_"+op.name+"();\n"
        elif op.nature == 'RR':
            text+= "    tmp = params_size_"+service.name+"_"+op.name+"_request();\n"
            text+= "    max = ( tmp < max ) ? max : tmp;\n"
            text+= "    tmp = params_size_"+service.name+"_"+op.name+"_answer();\n"
        text+= "    max = ( tmp < max ) ? max : tmp;\n"
    text+="    return max+LDP_ELI_HEADER_SIZE+LDP_ELI_UDP_HEADER_SIZE;\n"
    text+="}\n"

    return text;
