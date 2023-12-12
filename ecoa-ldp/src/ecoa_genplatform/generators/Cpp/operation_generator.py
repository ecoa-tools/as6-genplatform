# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

from ..fix_names import fix_Cpp_data_type
import math

def generate_param_fct_call_cpp(op_type,  with_input=False, with_output=False, is_first_arg=False):
    """Generate parameters string for a function call in C.

        :param op_type:
        :param bool with_input: include input parameter. False by default.
        :param bool with_output: include output parameter. False by default.
    """
    string = ""
    for param in op_type.params:
        if (param.direction == 'input' and with_input) or (param.direction == 'output' and with_output):
            if param.is_complex:
                string += ",*" + param.name
            else:
                string += "," + param.name

    if is_first_arg:
        string=string.replace(",", " ", 1)
    return string


def generate_params_variable_cpp(op_type, start_read_index, with_input=False, with_output=False):
    string =""
    read_index = start_read_index
    for param in op_type.params:
        if (param.direction == 'input' and with_input) or (param.direction == 'output' and with_output):
            if param.is_complex:
                string += fix_Cpp_data_type(param.type) + "* " + param.name + " = "
                string += "(("+ fix_Cpp_data_type(param.type) +"*) &elt->parameters[" + read_index + "]);\n"
            else:
                string += fix_Cpp_data_type(param.type) + " " + param.name + ";\n"
                string += "memcpy(&" + param.name + ", &elt->parameters[" + read_index + "], sizeof("+ fix_Cpp_data_type(param.type) +"));\n"


            read_index += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"
    return string

def generate_header_fct_cpp(op_type, with_input=False, with_output=False,
                        is_output_const=False, output_mode=True, is_first_arg = False):
    """Generate parameters string for a function declaration header in C.

        :param op_type:
        :param bool with_input: include input parameter. False by default.
        :param bool with_output: include output parameter. False by default.
        :param bool is_output_const: add 'const' for output parameters. False by default.
        :param bool output_mode: output parameters could be generated as input (without * for simple type).
        True by default.
        :param bool is_first_arg: remove first character wich is a comma
        :return:string
   """
    header_string = ""

    for param in op_type.params:
        if param.direction == 'input' and with_input:
            header_string += ", const " + fix_Cpp_data_type(param.type)
            if param.is_complex:
                header_string += '&'
            header_string +=' '+param.name

        elif param.direction == 'output' and with_output:
            header_string += ", "
            if is_output_const:
                header_string += "const "
            header_string += fix_Cpp_data_type(param.type)

            if param.is_complex or output_mode:
                header_string += '&'
            header_string +=' '+param.name

    #remove first ',' if necessary
    if is_first_arg:
         header_string=header_string.replace(", ", "",1)
    return header_string


def generate_memcpy_parameters_cpp(op_type, start_index_str, with_input=False, with_output=False):
    """Generate parameters string to fill message with parameter values (using memcpy) in Cpp.

		:param op_type:
		:return:
		:param str start_index_str: index of message memory space where write parameter value.
		:param bool with_input: include input parameters values. False by default
		:param bool with_output: include output parameters values. False by default
	"""
    string_memcpy_parameters = ""
    start_write_index = start_index_str
    for param in op_type.params:  # or op[0].outputs:
        if param.direction == 'input' and with_input:
            string_memcpy_parameters += "memcpy(&param_msg[" + start_write_index + "], "
            #if not param.is_complex:

            # if is not a complexe parameter (freshly added)
            # if param.is_complex:
            #     string_memcpy_parameters += "&"
            # else:
            #     pass

            string_memcpy_parameters += "&"
            string_memcpy_parameters += param.name + ",sizeof(" + fix_Cpp_data_type(param.type) + "));\n"
            start_write_index += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"

        if param.direction == 'output' and with_output:
            string_memcpy_parameters += "memcpy(&param_msg[" + start_write_index + "], "
            string_memcpy_parameters += "&"
            string_memcpy_parameters += param.name + ",sizeof(" + fix_Cpp_data_type(param.type) + "));\n"
            start_write_index += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"

    return string_memcpy_parameters

def generate_serialization_parameters_cpp(op_type, start_index_str, with_input=False, with_output=False):
    """Generate parameters string to serialize message in Cpp.

        :param op_type:
        :return:
        :param str start_index_str: index of message memory space where write parameter value.
        :param bool with_input: include input parameters values. False by default
        :param bool with_output: include output parameters values. False by default
    """

    string = ""
    start_write_index = start_index_str
    for param in op_type.params:
        if (param.direction == 'input' and not with_input) or \
           (param.direction == 'output' and not with_output) :
           continue

        string += "        //serialize_"+ fix_Cpp_data_type(param.type).replace("::","__") +"("
        string += param.name + ", &param_msg[total_added_size], max_size ,&added_size);\n"
        string += "        //max_size -= added_size;\n"
        string += "        //total_added_size += added_size;\n"

    return string

def generate_params_request_cpp(op_type, start_index_str):
    text=""
    for param in op_type.params:
        if param.direction == "output":
            text+="        memcpy(&" + param.name + ",&elt_answer->parameters[" + start_index_str +"],sizeof("+ fix_Cpp_data_type(param.type)+"));\n"
            start_index_str = start_index_str + "+sizeof(" + fix_Cpp_data_type(param.type) + ")"
    return text

def generate_broadcast_event_send_cpp(op_type, operation_index):
    """Generate C code for event sending function. (broadcast event)

    Args:
        op_type (:class:`~ecoa.models.operation_type.Module_Operation_Type`): operation type
        operation_index (int): index of this operation in the operation_map of this module type
    """
    template = "\
    ldp_module_context* ctx=(ldp_module_context*) this->hook;\n"

    template += "    uint32_t params_size = 0#PARAMS_SIZE#;\n\
    char* param_msg = ctx->msg_buffer;\n\
    if (ctx->operation_map[#OP_INDEX#].nb_ext_socket > 0){\n\
        //uint32_t added_size = 0;\n\
        uint32_t total_added_size = LDP_HEADER_TCP_SIZE;\n\
        //uint32_t max_size = params_size;\n\
#PARAMS_SERIAL#\
        ldp_mod_event_send_external(ctx, param_msg, total_added_size, ctx->operation_map[#OP_INDEX#]);\n\n\
    }\n\
    if ((ctx->operation_map[#OP_INDEX#].nb_module > 0) ||\n\
        (ctx->operation_map[#OP_INDEX#].nb_local_socket > 0)){\n\
#PARAMS_MEMCPY#\
       ldp_mod_event_send_local(ctx, param_msg, params_size, ctx->operation_map[#OP_INDEX#], true);\n\
   }\n\
\n"

    #PARAMS_SIZE#
    params_size = ""
    for param in op_type.params:
        params_size += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"

    #PARAMS_MEMCPY#
    params_memcpy = generate_memcpy_parameters_cpp(op_type, "LDP_HEADER_TCP_SIZE", with_input=True)

    #PARAMS_SERIAL#
    params_serial = generate_serialization_parameters_cpp(op_type, "LDP_HEADER_TCP_SIZE", with_input=True)


    return template.replace("#OP_INDEX#", str(operation_index))\
                   .replace("#PARAMS_SIZE#", params_size)\
                   .replace("#PARAMS_SERIAL#", params_serial)\
                   .replace("#PARAMS_MEMCPY#", params_memcpy)


def generate_async_request_send_cpp(op_type, operation_index, op_rr_index):

    template = "\n\
    ldp_module_context* ctx=(ldp_module_context*) this->hook;\n"

    template += "    if (ldp_check_concurrent_RR_num(ctx,#OP_RR_INDEX# , #MAX_OP_NUM#) != MOD_CONTAINER_OK){\n\
        return ECOA::return_status::RESOURCE_NOT_AVAILABLE;\n\
    }\n\
    uint32_t params_size = sizeof(ECOA::uint32)+sizeof(ECOA::uint32)#PARAMS_SIZE#;\n\
    ldp__timestamp timeout_duration = {#TIMEOUT#};\n\
    \n\
    char* param_msg = ctx->msg_buffer;\n\
    int retval;\n\
\n\
    if ((ctx->operation_map[#OP_INDEX#].nb_module > 0) ||\n\
        (ctx->operation_map[#OP_INDEX#].nb_local_socket > 0)){\n\
#PARAMS_MEMCPY#\
        retval = ldp_mod_request_async_send_local(ctx, &ID, param_msg, params_size,\n\
                                                  &ctx->operation_map[#OP_INDEX#],\n\
                                                  &timeout_duration);\n\
    }else if(ctx->operation_map[#OP_INDEX#].nb_ext_socket > 0){\n\
        //uint32_t added_size = 0;\n\
        //uint32_t total_added_size = LDP_HEADER_TCP_SIZE + sizeof(ECOA__uint32)+sizeof(ldp_module_context*);\n\
        //uint32_t max_size = params_size - sizeof(ECOA__uint32) - sizeof(ldp_module_context*);\n\
#PARAMS_SERIAL#\
#PARAMS_SERIAL#\
        // TODO ldp_mod_request_async_send_extern\n\
        retval = ECOA__return_status_NO_RESPONSE;\n\
    }else{\n\
        retval = ECOA__return_status_NO_RESPONSE;\n\
    }\n\
\n\
    ECOA::return_status toreturn = ECOA::return_status::OK;\n\
    if(retval == MOD_CONTAINER_OK){\n\
        ctx->req_resp.current_RR_number[#OP_RR_INDEX#]++;\n\
        toreturn = ECOA::return_status::OK;\n\
    }else if (retval == MOD_CONTAINER_FIFO_FULL){\n\
        toreturn = ECOA::return_status::RESOURCE_NOT_AVAILABLE;\n\
    }else{\n\
        toreturn = ECOA::return_status::NO_RESPONSE;\n\
    }\n\
    return toreturn;\n"


    if op_type.timeout > 0:
        seconds = int(op_type.timeout)
        nanoseconds = int((op_type.timeout * 1000000000) % 1000000000)
        timeout_str = "{0}, {1}".format(seconds, nanoseconds)
    else:
        timeout_str = "ECOA__UINT32_MAX, ECOA__UINT32_MAX"

    params_size = ""
    for param in op_type.params:
        if param.direction == 'input':
            params_size += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"

    params_memcpy = generate_memcpy_parameters_cpp(op_type,
                                            "LDP_HEADER_TCP_SIZE+sizeof(ECOA::uint32)+"
                                            "sizeof(ECOA::uint32)", with_input=True)


    params_serial = generate_serialization_parameters_cpp(op_type, "LDP_HEADER_TCP_SIZE+sizeof(ECOA::uint32)+"
                                            , with_input=True)

    return template.replace("#OP_RR_INDEX#", str(op_rr_index)) \
                   .replace("#MAX_OP_NUM#", str(op_type.maxVersions))\
                   .replace("#TIMEOUT#", timeout_str)\
                   .replace("#OP_INDEX#", str(operation_index))\
                   .replace("#PARAMS_SIZE#", params_size)\
                   .replace("#PARAMS_MEMCPY#", params_memcpy)\
                   .replace("#PARAMS_SERIAL#", params_serial)



def generate_sync_request_send_cpp(op_type, operation_index):
    template = "\
    ldp_module_context* ctx=(ldp_module_context*) this->hook;\n"

    template += "    uint32_t params_size = sizeof(ECOA::uint32)#PARAMS_SIZE#;\n\
    ldp__timestamp timeout_duration = {#TIMEOUT#};\n\
    char* param_msg = ctx->msg_buffer;\n\
    int retval;\n\
    \n\
    if ((ctx->operation_map[#OP_INDEX#].nb_module > 0) ||\n\
        (ctx->operation_map[#OP_INDEX#].nb_local_socket > 0)){\n\
#PARAMS_MEMCPY_REQ#\
        retval = ldp_mod_request_sync_send_local(ctx, param_msg, params_size,\n\
                                                   &ctx->operation_map[#OP_INDEX#],\n\
                                                   &timeout_duration);\n\
    }else if(ctx->operation_map[#OP_INDEX#].nb_ext_socket > 0){\n\
        //uint32_t added_size = 0;\n\
        //uint32_t total_added_size = LDP_HEADER_TCP_SIZE + sizeof(ECOA__uint32)+sizeof(ldp_module_context*);\n\
        //uint32_t max_size = params_size - sizeof(ECOA__uint32) - sizeof(ldp_module_context*);\n\
#PARAMS_SERIAL_REQ#\
        // TODO ldp_mod_request_sync_send_extern\n\
        retval = ECOA__return_status_NO_RESPONSE;\n\
    }else{\n\
        retval = ECOA__return_status_NO_RESPONSE;\n\
    }\n\
    \n\
    ECOA::return_status toreturn = ECOA::return_status::OK;\n\
    if (retval == 0){\n\
        ldp_element* elt_answer;\n\
        ldp_status_t ret=ldp_fifo_manager_pop_elt(ctx->fifo_manager, &elt_answer);\n\
        assert(ret !=-1);UNUSED(ret);\n"
    template += "\
#PARAMS_MEMCPY_ANSWER#\
        ldp_fifo_manager_release_elt(ctx->fifo_manager, elt_answer);\n\
        toreturn = ECOA::return_status::OK;\n\
    }else if (retval == MOD_CONTAINER_FIFO_FULL){\n\
        toreturn = ECOA::return_status::RESOURCE_NOT_AVAILABLE;\n\
    }else{\n\
        toreturn = ECOA::return_status::NO_RESPONSE;\n\
    }\n\
    return toreturn;\n"

    if op_type.timeout > 0:
        seconds = int(op_type.timeout)
        nanoseconds = int((op_type.timeout * 1000000000) % 1000000000)
        timeout_str = "{0}, {1}".format(seconds, nanoseconds)
    else:
        timeout_str = "ECOA__UINT32_MAX, ECOA__UINT32_MAX"


    params_size = ""
    for param in op_type.params:
        if param.direction == 'input':
            params_size += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"

    params_memcpy_req = generate_memcpy_parameters_cpp(op_type,
                                            "LDP_HEADER_TCP_SIZE+sizeof(ECOA::uint32)+"
                                            "sizeof(ECOA__uint32)", with_input=True)
    params_memcpy_answer = ""
    params_memcpy_answer =generate_params_request_cpp(op_type,
                                            "sizeof(ECOA::uint32)")

    params_serial_req = generate_serialization_parameters_cpp(op_type,
                                            "LDP_HEADER_TCP_SIZE+sizeof(ECOA::uint32)", with_input=True)

    return template.replace("#TIMEOUT#",timeout_str)\
                   .replace("#OP_INDEX#",str(operation_index))\
                   .replace("#PARAMS_MEMCPY_REQ#", params_memcpy_req)\
                   .replace("#PARAMS_MEMCPY_ANSWER#", params_memcpy_answer)\
                   .replace("#PARAMS_SIZE#", params_size)\
                   .replace("#PARAMS_SERIAL_REQ#", params_serial_req)

def generate_response_send_cpp(op_type, operation_index, op_rr_index):
    """Generate C code for response sending function.

    Args:
        op_type (:class:`~ecoa.models.operation_type.Module_Operation_Type`): operation type
        operation_index (int): index of this operation in the operation_map of this module type
        op_rr_index     (int): index of this rr operation  for this module type
    """

    template="\
    ldp_module_context* ctx=(ldp_module_context*) this->hook;\n"

    template += "    ctx->req_resp.current_RR_number[#OP_RR_INDEX#]--;\n\
    int params_size = sizeof(ECOA::uint32)#PARAMS_SIZE#;\n\
    ldp_node* node;\n\
    ldp_req_received* req=ldp_find_req_received(&ctx->req_resp,ID, &node);\n\
    if (req != NULL){\n\
        char* param_msg = ctx->msg_buffer;\n\
        if(req->connection_type == LDP_REQUEST_EXTERNAL){\n\
#PARAMS_SERIAL#\n\
            ldp_mod_request_answer_send_external(ctx, param_msg,params_size, req);\n\
        }else{\n\
#PARAMS_MEMCPY#\
            ldp_mod_request_answer_send_local(ctx, param_msg,params_size, req);\n\
        }\n\
        ldp_free_req_received(&ctx->req_resp,node);\n\
    }else{\n\
        ldp_log_PF_log(ECOA_LOG_ERROR_PF,\"ERROR\", ctx->logger_PF,\"cant send RR answer: no client found\");\n\
        return ECOA::return_status::INVALID_IDENTIFIER;\n\
    }\n\
    return ECOA::return_status::OK;\n"

    params_size = ""
    for param in op_type.params:
        if param.direction == 'output':
            params_size += "+sizeof(" + fix_Cpp_data_type(param.type) + ")"
    params_memcpy_str =  generate_memcpy_parameters_cpp(op_type,
                                    'LDP_HEADER_TCP_SIZE+sizeof(ECOA::uint32)+sizeof(ECOA::uint32)'
                                    , with_output=True)

    params_serial = generate_serialization_parameters_cpp(op_type,
                                            "LDP_HEADER_TCP_SIZE+sizeof(ECOA__uint32)", with_output=True)
    if params_serial != "":
        string_tmp = "\
            //uint32_t added_size = 0;\n\
            //uint32_t total_added_size = LDP_HEADER_TCP_SIZE + sizeof(ECOA__uint32)+sizeof(ldp_module_context*);\n\
            //uint32_t max_size = params_size - sizeof(ECOA__uint32) - sizeof(ldp_module_context*);\n"
        params_serial = string_tmp + params_serial

    return template.replace("#OP_RR_INDEX#", str(op_rr_index))\
                   .replace("#PARAMS_SIZE#", params_size)\
                   .replace("#PARAMS_MEMCPY#", params_memcpy_str)\
                   .replace("#PARAMS_SERIAL#", params_serial)


