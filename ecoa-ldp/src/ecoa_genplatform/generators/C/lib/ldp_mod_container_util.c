/**
* @file ldp_mod_container_util.c
* @brief ECOA module container functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <assert.h>

#include "ldp_mod_container_util.h"

#include "ldp_structures.h"
#include "ldp_fifo.h"
#include "ldp_network.h"
#include <limits.h>
#include "ldp_request_response.h"
#include "ldp_log_platform.h"
#include "ldp_dynamic_trigger.h"
#include <pthread.h>
#include "ldp_fifo_manager.h"
#include "ldp_comp_util.h"

#include "ldp_thread.h"
#include "ldp_fine_grain_deployment.h"

#include "ldp_ELI.h"
#include "ldp_ELI_udp.h"
#include "ldp_ELI_msg_management.h"
#include "ECOA_simple_types_serialization.h"

void ldp_kill_platform(ldp_module_context* ctx){
    int msg = LDP_ID_KILL;
    net_data_w data_w;
#if USE_UDP_PROTO
    data_w.module_id = 0x01;
    data_w.msg_id = 0x01;
#endif
    if(ldp_IP_write(&ctx->component_ctx->interface_ctx_array[ctx->component_ctx->nb_client],
	   (char*)&msg,sizeof(int), &data_w) == APR_SUCCESS){
        ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF,"[%s] kill sent", ctx->name);
    }
}

void ldp_mod_init_notify(ldp_module_context* ctx){
    apr_thread_mutex_lock(ctx->component_ctx->state_mutex);
     if( (ctx->component_ctx->state == PDomain_INIT) && (all_module_ready(ctx->component_ctx)) ){
		ctx->component_ctx->state = PDomain_READY;
		// send ready to father
		int msg = LDP_ID_CLIENT_READY;
		net_data_w data_w;
#if USE_UDP_PROTO
		data_w.module_id = 0x01;
		data_w.msg_id = 0x01;
#endif
		if(ldp_IP_write(&ctx->component_ctx->interface_ctx_array[ctx->component_ctx->nb_client],
		   (char*)&msg,sizeof(char), &data_w) != APR_SUCCESS){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
			                     "Module %s fails to notify father that all modules are READY", ctx->name);
			ctx->component_ctx->state = PDomain_INIT;
		}
    }
    apr_thread_mutex_unlock(ctx->component_ctx->state_mutex);
}


/**
 * @brief      check if the module receiver is in RUNNING state
 *
 * @return     MOD_CONTAINER_OK, MOD_CONTAINER_KO
 */
static int mod_check_receiver_state(ldp_module_context* ctx, ldp_module_context* receiver_ctx){
    if(receiver_ctx->state != RUNNING){
        if (ctx->component_ctx->state == PDomain_RUNNING) {
            ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF,
		                     "[%s] module %s is not in running state", ctx->name, receiver_ctx->name);
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 1);
        }
        return MOD_CONTAINER_KO;
    }
    return MOD_CONTAINER_OK;
}

/**
 * @brief      Set a trigger in case of asynchonous RR
 *
 * @param      mod_ctx      The module context
 * @param[in]  req_sent_ID  The ID of the request sent
 * @param[in]  timeout      The timeout
 *
 * @return     MOD_CONTAINER_ERROR, MOD_CONTAINER_OK
 */
static int ldp_asynchronous_RR_set_trigger(ldp_module_context* mod_ctx,
                                             ECOA__uint32 req_sent_ID, const ldp__timestamp* timeout){
    if(mod_ctx->req_resp.trig_ctx == NULL){
        return MOD_CONTAINER_ERROR;
    }
    ldp_dyn_trigger_RR_param arg = (ldp_dyn_trigger_RR_param){req_sent_ID, mod_ctx};
    mod_ctx->req_resp.trig_ctx->mod_id = mod_ctx->mod_id;
    if (ldp_set_dynamic_trigger(mod_ctx->req_resp.trig_ctx, (ECOA__duration*) timeout,
	    &arg, ldp_handler_dynamic_trigger_RR_async) == 0){
        return MOD_CONTAINER_OK;
    }else{
        ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", mod_ctx->logger_PF,
		                     "[%s] cannot set dynamic trigger for asynchronous RR", mod_ctx->name);
        return MOD_CONTAINER_ERROR;
    }
}

/**
 * @brief      Writes data for request-response: the sent request_ID, the module ctx of the sender.
 *
 * @param      buffer          The buffer that will be written
 * @param[in]  req_ID          The request id
 * @param      sender_mod_ctx  The sender context
 * @param[in]  offset          The offset where to start writting in buffer
 */
static void write_RR_params(char* buffer, ECOA__uint32 req_ID, ECOA__uint32 client_sequence_num, int offset){
        memcpy(&buffer[offset], &client_sequence_num, sizeof(ECOA__uint32)); // not use for direct module link
        memcpy(&buffer[offset+sizeof(ECOA__uint32)], &req_ID, sizeof(ECOA__uint32));
}

/**
 * @brief      Clean request structures in case of failure
 *              - clean sent request on client side
 *              - clean received request on server side
 *
 * @param      client_ctx     The client module context
 * @param[in]  mod_operation  The operation op
 * @param[in]  request_ID     The request id (server side)
 * @param[in]  response_ID    The response id (client side)
 */
static void RR_failure_clean(ldp_module_context* client_ctx, ldp_mod_operation mod_operation,
                             ECOA__uint32 request_ID, ECOA__uint32 response_ID ){
    ldp_node* req_to_remove;
    ldp_find_req_received(&mod_operation.mod_ctx->req_resp, response_ID, &req_to_remove);
    ldp_free_req_received(&mod_operation.mod_ctx->req_resp, req_to_remove);
    ldp_find_req_sent(&client_ctx->req_resp, request_ID, &req_to_remove);
    ldp_free_req_sent(&client_ctx->req_resp, req_to_remove);

}

static int push_fifo_msg(ldp_module_context* ctx,
                         ldp_mod_operation* mod_op,
                         ECOA__uint32 msg_size,
                         char* msg){
    if( ldp_fifo_manager_push(mod_op->mod_ctx->fifo_manager,
                                mod_op->op_index,
                                mod_op->op_id,
                                EVENT,
                                mod_op->op_activating,
                                msg_size,
                                msg,
                                mod_op->mod_ctx->mod_id) != 0){
        ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
		                     "[%s] %s : fifo full. Impossible to send message ID: %i",
                            ctx->name, mod_op->mod_ctx->name, mod_op->op_id);
        return MOD_CONTAINER_FIFO_FULL;
    }
    return MOD_CONTAINER_OK;
}

static int send_external_msg(ldp_module_context* ctx,
                             ldp_ELI_header* ELI_header,
                             unsigned char* msg_buffer,
                             ldp_interface_ctx* interface,
                             uint32_t params_size){


    ECOA__uint32 written_bytes;
    ldp_write_ELI_header(ELI_header, msg_buffer, LDP_ELI_UDP_HEADER_SIZE, &written_bytes);

    ECOA__uint16 channel_counter=12; /* TODO */
    ldp_sending_fct_ctx ctx_fct = {&interface->inter.mcast, ctx->logger_PF};
    ldp_ELI_udp_msg_fragment_and_send(&ctx_fct, ldp_ELI_UDP_sending_fct, &msg_buffer[LDP_ELI_UDP_HEADER_SIZE],
                                                     params_size+LDP_ELI_HEADER_SIZE,
                                                     interface->inter.mcast.UDP_current_PF_ID,
                                                     ctx->mod_id,
                                                     &channel_counter);

    return MOD_CONTAINER_OK;
}

int ldp_mod_event_send_local(ldp_module_context* ctx,
                               char* msg_buffer,
                               int params_size,
                               ldp_mod_operation_map operation_map,
                               bool free_buffer){
    // msg_ buffer contains parameters from the index HEADER_TCP_SIZE
    // by this way, it is possible to write IP header
    UNUSED(free_buffer);

    int retval = MOD_CONTAINER_OK;

    // Send message to local sockets
    ldp_written_IP_header(msg_buffer, params_size, 0);
    for(int i=0; i < operation_map.nb_local_socket; i++){
        ldp_written_IP_op_ID(msg_buffer, operation_map.local_socket_operations[i].op_id);
        ldp_IP_write(operation_map.local_socket_operations[i].interface,msg_buffer,
                       LDP_HEADER_TCP_SIZE + params_size, ctx->network_write_data);
    }

    // Send message to local modules
    for(int i=0; i < operation_map.nb_module; i++){

        if (mod_check_receiver_state(ctx, operation_map.module_operations[i].mod_ctx)){
            continue;
        }

        retval = push_fifo_msg(ctx, &operation_map.module_operations[i], params_size,
                               &msg_buffer[LDP_HEADER_TCP_SIZE] /*dont need header */);
    }
    return retval;
}

int ldp_mod_event_send_external(ldp_module_context* ctx,
                               char* msg,
                               int params_size,
                               ldp_mod_operation_map operation_map){
    int retval = MOD_CONTAINER_OK;

    for(int i=0; i < operation_map.nb_ext_socket; i++){
        ldp_ELI_header ELI_header = {LDP_ELI_VERSION,
                                    LDP_ELI_SERVICE_OP,
                                    ctx->component_ctx->ELI_platform_ID,
                                    operation_map.external_socket_operations[i].op_id,
                                    params_size, /* payload size*/
                                    0x0};

        send_external_msg(ctx, &ELI_header, (unsigned char*) msg,
                         operation_map.external_socket_operations[i].interface, params_size);
    }

    return retval;
}

static int ldp_mod_request_async_send_mod(ldp_module_context* ctx,
                                     ECOA__uint32* ID,
                                     char* msg_buffer,
                                     int param_size,
                                     ldp_mod_operation* mod_operation,
                                     ldp__timestamp* timeout_duration){
    ldp_status_t ret;
    ret = mod_check_receiver_state(ctx, mod_operation->mod_ctx);
    if (ret != MOD_CONTAINER_OK){
        return ret;
    }

    // create the request to save information about this request
    // ceate an unique ID (for this module)

    ret=ldp_add_req_sent(&ctx->req_resp, LDP_REQUEST_MODULE,
                           mod_operation->op_id,
                           mod_operation->RR_answer_op_index,
                           ID, false, /* asynchronous RR */
                            mod_operation->RR_answer_activating,
                            timeout_duration);
    if (ret != 0) {
        ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                         ECOA__error_type_RESOURCE_NOT_AVAILABLE, 2);
    }
    assert(ret == 0);

    if ((int)timeout_duration->seconds >= 0){
        // set a trigger if possible to inform module in case of timeout
        ldp_asynchronous_RR_set_trigger(ctx, *ID, timeout_duration);
    }

    // create the request directly in the target module
    // create an unique ID (for the target module)
    ECOA__uint32 response_ID;
    ret=ldp_add_req_received(&mod_operation->mod_ctx->req_resp, &response_ID, LDP_REQUEST_MODULE,
                                ctx->mod_id, ctx, mod_operation->op_id, *ID, false);
    if (ret != 0) {
        ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                         ECOA__error_type_RESOURCE_NOT_AVAILABLE, 3);
    }
    assert(ret == 0);

    write_RR_params(msg_buffer, response_ID, ctx->mod_id, LDP_HEADER_TCP_SIZE);


    // push message in target module fifo: don't send tcp header and client info
    ret = push_fifo_msg(ctx, mod_operation, param_size, &msg_buffer[LDP_HEADER_TCP_SIZE+sizeof(ECOA__uint32)]);
    if (ret != MOD_CONTAINER_OK){
        RR_failure_clean(ctx, *mod_operation, *ID, response_ID);
    }

    return ret;
}
static int ldp_mod_request_async_send_local_sock(ldp_module_context* ctx,
                                     ECOA__uint32* ID,
                                     char* msg_buffer,
                                     int param_size,
                                     ldp_socket_operation* sock_operation,
                                     ldp__timestamp* timeout_duration){
    ldp_status_t ret;

    // create the request to save information about this request
    // ceate an unique ID (for this module)
    ret=ldp_add_req_sent(&ctx->req_resp, true,
                           sock_operation->op_id,
                           sock_operation->RR_answer_op_index,
                           ID,
                           false, /* asynchronous RR*/
                           sock_operation->RR_answer_op_activating,
                           timeout_duration);
    if (ret != 0) {
        ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                         ECOA__error_type_RESOURCE_NOT_AVAILABLE, 4);
    }
    assert(ret == 0);
    if ((int)timeout_duration->seconds >= 0){
        // set a trigger if possible to inform module in case of timeout
        ldp_asynchronous_RR_set_trigger(ctx, *ID, timeout_duration);
    }

    // write TCP msg
    ldp_written_IP_header(msg_buffer, param_size, sock_operation->op_id);
    write_RR_params(msg_buffer, *ID, ctx->mod_id, LDP_HEADER_TCP_SIZE);


    // send TCP msg
    ldp_IP_write(sock_operation->interface,msg_buffer,
                    param_size + LDP_HEADER_TCP_SIZE, ctx->network_write_data);

    return MOD_CONTAINER_OK;
}

int ldp_mod_request_async_send_local(ldp_module_context* ctx,
                                     ECOA__uint32* ID,
                                     char* msg_buffer,
                                     int param_size,
                                     ldp_mod_operation_map* operation_map,
                                     ldp__timestamp* timeout_duration){
    int new_param_size = param_size + sizeof(ECOA__uint32); // 4bytes for module ID in local-platform message
    int retval = MOD_CONTAINER_KO;
    // TODO ???? y
    if (operation_map->nb_module > 0){
        retval = ldp_mod_request_async_send_mod(ctx, ID, msg_buffer, new_param_size,
                                              &operation_map->module_operations[0],
                                              timeout_duration);
    }else if (operation_map->nb_local_socket > 0){
        retval = ldp_mod_request_async_send_local_sock(ctx, ID, msg_buffer, new_param_size,
                                              &operation_map->local_socket_operations[0],
                                              timeout_duration);
    }

    return retval;
}

int ldp_mod_request_async_send_external(ldp_module_context* ctx,
                                        ECOA__uint32* ID_ptr,
                                        char* buffer_msg,
                                        int params_size,
                                        ldp_mod_operation_map* operation_map,
                                        ldp__timestamp* timeout_duration){
    ldp_status_t ret;

    if( operation_map->nb_ext_socket > 0){
        ret=ldp_add_req_sent(&ctx->req_resp, LDP_REQUEST_EXTERNAL,
                               operation_map->external_socket_operations[0].op_id,
                               operation_map->external_socket_operations[0].RR_answer_op_index,
                               ID_ptr,
                               false, /*Asynchrounous*/
                                operation_map->external_socket_operations[0].RR_answer_op_activating,
                                timeout_duration);
        if (ret != 0) {
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 5);
        }
        assert(ret == 0);

        // write request ID:
        memcpy(&buffer_msg[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE], ID_ptr, sizeof(ECOA__uint32));

        ldp_ELI_header ELI_header = {LDP_ELI_VERSION,
                                       LDP_ELI_SERVICE_OP,
                                       ctx->component_ctx->ELI_platform_ID,
                                       operation_map->external_socket_operations[0].op_id,
                                       params_size,
                                       ctx->mod_id};

        if ((int)timeout_duration->seconds >= 0){
            // set a trigger if possible to inform module in case of timeout
            ldp_asynchronous_RR_set_trigger(ctx, *ID_ptr, timeout_duration);
        }

        ret = send_external_msg(ctx, &ELI_header, (unsigned char*) buffer_msg,
                         operation_map->external_socket_operations[0].interface, params_size);

    }else{
        ret = MOD_CONTAINER_KO;
    }

    return ret;
}


int ldp_mod_request_sync_send_external(ldp_module_context* ctx,
                                        char* buffer_msg,
                                        int params_size,
                                        ldp_mod_operation_map* operation_map,
                                        ldp__timestamp* timeout_duration){
    ldp_status_t ret;
    ECOA__uint32 ID;

    if( operation_map->nb_ext_socket > 0){
        ret=ldp_add_req_sent(&ctx->req_resp, true,
                                operation_map->external_socket_operations[0].op_id,
                                operation_map->external_socket_operations[0].RR_answer_op_index,
                                &ID, true,
                                true, /* synchronous RR: force answer to be an activating operation */
                                timeout_duration);
        if (ret != 0) {
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 6);
        }
        assert(ret == 0);

        // write request ID:
        memcpy(&buffer_msg[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE], &ID, sizeof(ECOA__uint32));

        ldp_ELI_header ELI_header = {LDP_ELI_VERSION,
                                       LDP_ELI_SERVICE_OP,
                                       ctx->component_ctx->ELI_platform_ID,
                                       operation_map->external_socket_operations[0].op_id,
                                       params_size,
                                       ctx->mod_id};

        // lock mutex to wait for answer after
        apr_thread_mutex_lock(ctx->wait_response);
        ret = send_external_msg(ctx, &ELI_header, (unsigned char*) buffer_msg,
                         operation_map->external_socket_operations[0].interface, params_size);

        if(ret != MOD_CONTAINER_OK){
            ldp_node* req_to_remove;
            ldp_find_req_sent(&ctx->req_resp, ID, &req_to_remove);
            ldp_free_req_sent(&ctx->req_resp, req_to_remove);
            // TODO reset request ??
            ret = MOD_CONTAINER_KO;
        }else{
            // TODO : duplication
            // wait response and continue
            apr_int64_t delay = apr_time_from_sec(timeout_duration->seconds) + (timeout_duration->nanoseconds*1e-3);
            ret = MOD_CONTAINER_OK;
            if( APR_TIMEUP == apr_thread_cond_timedwait(ctx->condition_response, ctx->wait_response, delay)){
                ldp_node* req_to_remove = NULL;
                ldp_log_PF_log(ECOA_LOG_WARN_PF, "WARN", ctx->logger_PF, "RR timeout");
                if(ldp_find_req_sent(&ctx->req_resp, ID, &req_to_remove) != NULL){
                    ldp_free_req_sent(&ctx->req_resp, req_to_remove);
                }
                ret = MOD_CONTAINER_KO;
            }

        }


        apr_thread_mutex_unlock(ctx->wait_response);

    }else{
        ret = MOD_CONTAINER_KO;
    }

    return ret;
}

int ldp_mod_request_sync_send_local(ldp_module_context* ctx,
                                      char* buffer_msg,
                                      int param_size,
                                      ldp_mod_operation_map* operation_map,
                                  ldp__timestamp* timeout_duration){
    ECOA__uint32 ID;
    ldp_status_t ret;
    int new_param_size = param_size + sizeof(ECOA__uint32); // 4bytes for module ID in local-platform message

    // TODO change behaviour : choose a module first. if NOT: choose the first socket
    if( operation_map->nb_local_socket > 0){
        // choose the first socket

        // save request sent information and create an ID (client)
        ret=ldp_add_req_sent(&ctx->req_resp, LDP_REQUEST_LOCAL_SOCKET,
                               operation_map->local_socket_operations[0].op_id,
                               operation_map->local_socket_operations[0].RR_answer_op_index,
                               &ID, true,
                               true, /* synchronous RR: force answer to be an activating operation */
                               timeout_duration);
        if (ret != 0) {
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 7);
        }
        assert(ret == 0);

        // write TCP msg
        ldp_written_IP_header(buffer_msg, new_param_size, operation_map->local_socket_operations[0].op_id);
        write_RR_params(buffer_msg, ID, ctx->mod_id, LDP_HEADER_TCP_SIZE);

        // lock mutex to wait for answer after
        apr_thread_mutex_lock(ctx->wait_response);

        // send TCP msg
        ldp_IP_write(operation_map->local_socket_operations[0].interface, buffer_msg,
                        new_param_size + LDP_HEADER_TCP_SIZE, ctx->network_write_data);
    }else if (operation_map->nb_module>0){
        // check module state
        if (mod_check_receiver_state(ctx, operation_map->module_operations[0].mod_ctx)){
            return MOD_CONTAINER_KO;
        }

        // save request sent information and create an ID (client)
        ret=ldp_add_req_sent(&ctx->req_resp, LDP_REQUEST_MODULE,
                               operation_map->module_operations[0].op_id,
                               operation_map->module_operations[0].RR_answer_op_index,
                                &ID, true,
                                true, /* synchronous RR: force answer to be an activating operation */
                                timeout_duration);
        if (ret != 0) {
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 8);
        }
        assert(ret == 0);

        // save request received information and create ID (server)
        ECOA__uint32 response_ID;
        ret=ldp_add_req_received(&operation_map->module_operations[0].mod_ctx->req_resp, &response_ID,
                                    LDP_REQUEST_MODULE, ctx->mod_id,
                                    ctx, operation_map->module_operations[0].op_id, ID,true);
        if (ret != 0) {
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 9);
        }
        assert(ret == 0);

        // write module msg
        write_RR_params(buffer_msg, response_ID, ctx->mod_id, LDP_HEADER_TCP_SIZE);

        // lock mutex to wait for answer after
        apr_thread_mutex_lock(ctx->wait_response);

        //don't send tcp header and client info
        ret = push_fifo_msg(ctx, &operation_map->module_operations[0], new_param_size, &buffer_msg[LDP_HEADER_TCP_SIZE+sizeof(ECOA__uint32)]);
        if (ret != MOD_CONTAINER_OK){
            // free structure
            RR_failure_clean(ctx, operation_map->module_operations[0], ID, response_ID);

            apr_thread_mutex_unlock(ctx->wait_response);
            return MOD_CONTAINER_FIFO_FULL;
        }
    }else{
        // not connected operation
        return MOD_CONTAINER_KO;
    }

    // wait response and continue
    apr_int64_t delay = apr_time_from_sec(timeout_duration->seconds) + (timeout_duration->nanoseconds*1e-3);
    ret = MOD_CONTAINER_OK;
    if( APR_TIMEUP == apr_thread_cond_timedwait(ctx->condition_response, ctx->wait_response, delay)){
        ldp_node* req_to_remove = NULL;
        ldp_log_PF_log(ECOA_LOG_WARN_PF, "WARN", ctx->logger_PF, "RR timeout");
        if(ldp_find_req_sent(&ctx->req_resp, ID, &req_to_remove) != NULL){
            ldp_free_req_sent(&ctx->req_resp, req_to_remove);
        }
        ret = MOD_CONTAINER_KO;
    }
    apr_thread_mutex_unlock(ctx->wait_response);

    return ret;
}

int ldp_mod_request_answer_send_external(ldp_module_context* ctx,
                                        char* buffer_msg,
                                        int params_size,
                                        ldp_req_received* req){
    ldp_interface_ctx* client_interface = (ldp_interface_ctx*) req->client_ptr;

    ldp_ELI_header ELI_header = {LDP_ELI_VERSION,
                                LDP_ELI_SERVICE_OP,
                                ctx->component_ctx->ELI_platform_ID,
                                req->client_op_id,
                                params_size,
                                req->client_sequence_num};

    // write request ID:
    memcpy(&buffer_msg[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE], &req->client_req_ID, sizeof(ECOA__uint32));

    int retval = send_external_msg(ctx, &ELI_header, (unsigned char*) buffer_msg,
                     client_interface, params_size);
    return retval;
}

int ldp_mod_request_answer_send_local(ldp_module_context* ctx,
                                        char* buffer_msg,
                                        int param_size,
                                        ldp_req_received* req){
    int new_param_size = param_size + sizeof(ECOA__uint32); // 4bytes for module ID in local-platform message
    if (req->connection_type == LDP_REQUEST_LOCAL_SOCKET){
        // write TCP msg
        ldp_written_IP_header(buffer_msg, new_param_size, req->client_op_id);
        write_RR_params(buffer_msg, req->client_req_ID, req->client_sequence_num, LDP_HEADER_TCP_SIZE);
         // send TCP msg
        ldp_IP_write(req->client_ptr,buffer_msg,new_param_size+LDP_HEADER_TCP_SIZE, ctx->network_write_data);

    }else if(req->connection_type == LDP_REQUEST_MODULE){
        // find request sent in  reciever module ctx
        ldp_node* node;
        ldp_req_sent* req_sent=ldp_find_req_sent(&((ldp_module_context*)req->client_ptr)->req_resp,
                                                     req->client_req_ID,
		                                             &node);
        if(req_sent == NULL){
            ldp_log_PF_log_var(ECOA_LOG_WARN_PF, "WARN", ((ldp_module_context*)req->client_ptr)->logger_PF,
                                    "[%s] Request sent no found (maybe erase because of timeout)", ctx->name);
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 10);
            return MOD_CONTAINER_KO;
        }

        // check timeout
        if(ldp_is_request_timeout(&req_sent->timeout) == 1){
            ldp_log_PF_log_var(ECOA_LOG_WARN_PF, "WARN", ((ldp_module_context*)req->client_ptr)->logger_PF,
                                    "[%s] Request answer out of date : discard by module", ctx->name);
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_RESOURCE_NOT_AVAILABLE, 11);
            return MOD_CONTAINER_KO;
        }

        // check module state
        if (mod_check_receiver_state(ctx, (ldp_module_context*)req->client_ptr)){
            return MOD_CONTAINER_KO;
        }

        // write msg
        //
        ldp_status_t ret;
        write_RR_params(buffer_msg, req->client_req_ID, req->client_sequence_num, LDP_HEADER_TCP_SIZE);

        // push answer: don't send tcp header and client info
        if(req->is_synchrone){
            ret = ldp_fifo_manager_push_first(((ldp_module_context*)req->client_ptr)->fifo_manager,
                                                req_sent->resp_op_index,
                                                req_sent->resp_op_id,
                                                RR_ANSWER,
                                                true, /* sync RR answer to be activating */
                                                new_param_size - sizeof(ECOA__uint32),
                                                &buffer_msg[LDP_HEADER_TCP_SIZE+sizeof(ECOA__uint32)],
                                                ((ldp_module_context*)req->client_ptr)->mod_id);
        }else{
            ret = ldp_fifo_manager_push(((ldp_module_context*)req->client_ptr)->fifo_manager,
                                          req_sent->resp_op_index,
                                          req_sent->resp_op_id,
                                          RR_ANSWER,
                                          req_sent->resp_op_activating, /* async RR answer could be no activating*/
                                          new_param_size - sizeof(ECOA__uint32),
                                          &buffer_msg[LDP_HEADER_TCP_SIZE+sizeof(ECOA__uint32)],
                                          ((ldp_module_context*)req->client_ptr)->mod_id);
        }
        if (ret != 0){
            ldp_log_PF_log_var(ECOA_LOG_ERROR_PF, "ERROR", ((ldp_module_context*)req->client_ptr)->logger_PF,
                                    "[%s] fifo full in mod %s, pool %i. Impossible to send request answer",
                                    ctx->name, ((ldp_module_context*)req->client_ptr)->name,
                                    req_sent->resp_op_index);
            ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                             ECOA__error_type_OVERFLOW, 6);
        }

        if(req->is_synchrone){
            // remove request_sent for local synchrone RR only
            ldp_free_req_sent(&((ldp_module_context*)req->client_ptr)->req_resp, node);
            // unblock module in case of synchrone RR
            apr_thread_mutex_lock(((ldp_module_context*)req->client_ptr)->wait_response);
            apr_thread_cond_signal(((ldp_module_context*)req->client_ptr)->condition_response);
            apr_thread_mutex_unlock(((ldp_module_context*)req->client_ptr)->wait_response);
        }
    }else{
        return MOD_CONTAINER_KO;
    }
    return MOD_CONTAINER_OK;
}

int ldp_check_concurrent_RR_num(ldp_module_context* ctx,int RR_index,int max_concurrent_RR){
    if(ctx->req_resp.current_RR_number[RR_index] >= max_concurrent_RR){
        ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF,
		                     "[%s] maximum number of concurrent request", ctx->name);
        ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id,
                                         ECOA__asset_type_COMPONENT, ECOA__error_type_OVERFLOW, 7);
        return MOD_CONTAINER_KO;
    }
    return MOD_CONTAINER_OK;
}

void ldp_mod_start_RR_trigger(ldp_module_context* ctx, apr_thread_t** RR_dyn_trigger_thread){
    ctx->req_resp.trig_ctx = malloc(sizeof(ldp_dyn_trigger_context));
    ctx->req_resp.trig_ctx->name = "RR_dyn_trig";
    ctx->req_resp.trig_ctx->max_event_nb = 16;
    ctx->req_resp.trig_ctx->params_size = sizeof(ldp_dyn_trigger_RR_param);
    ctx->req_resp.trig_ctx->state = RUNNING;
    ctx->req_resp.trig_ctx->logger_PF = ctx->logger_PF;
    ctx->req_resp.trig_ctx->component_ctx = ctx->component_ctx;

    ldp_init_dynamic_trigger(ctx->req_resp.trig_ctx);
    apr_threadattr_t* attr;
    int ret=apr_threadattr_create(&attr,ctx->mem_pool);
    assert(ret==APR_SUCCESS);

    // use same affinity and scheduler than technical ressources
    ldp_thread_properties prop = {.priority=-20,
                                    .policy=LDP_SCHED_OTHER,
                                    .cpu_affinity_mask=ctx->component_ctx->technical_cpu_mask,
                                    .thread_name=ctx->req_resp.trig_ctx->name,
                                    .logger=ctx->logger_PF};

    ret = ldp_thread_create(RR_dyn_trigger_thread,
                                attr,
                                ldp_start_dynamic_trigger,
                                (void*) ctx->req_resp.trig_ctx,
                                &prop,
                                ctx->mem_pool);
    assert(ret==APR_SUCCESS);

    pthread_mutex_lock(&ctx->req_resp.trig_ctx->mutex);
    pthread_cond_signal(&ctx->req_resp.trig_ctx->cond);
    pthread_mutex_unlock(&ctx->req_resp.trig_ctx->mutex);

    UNUSED(ret);
}

void ldp_mod_stop_RR_trigger(ldp_module_context* ctx, apr_thread_t* RR_dyn_trigger_thread){
    ctx->req_resp.trig_ctx->state = IDLE;// invalid loop condition of thread

    // unlock thread
    pthread_mutex_lock(&ctx->req_resp.trig_ctx->mutex);
    pthread_cond_signal(&ctx->req_resp.trig_ctx->cond);
    pthread_mutex_unlock(&ctx->req_resp.trig_ctx->mutex);
    apr_status_t ret_val;

    // wait thread
    apr_thread_join(&ret_val,RR_dyn_trigger_thread);

    ldp_destroy_dynamic_trigger(ctx->req_resp.trig_ctx);
    free(ctx->req_resp.trig_ctx);
}
