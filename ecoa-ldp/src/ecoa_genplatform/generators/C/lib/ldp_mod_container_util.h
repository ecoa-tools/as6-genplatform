/**
* @file ldp_mod_container_util.h
* @brief ECOA module container functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_MOD_CONTAINER_UTIL_H
#define _LDP_MOD_CONTAINER_UTIL_H
#include <apr_thread_proc.h>
#include "ldp_network.h"
#include "ldp_request_response.h"
#include "ldp_structures.h"

#define MOD_CONTAINER_ERROR -4  //!< return code
#define MOD_CONTAINER_NO_BUFFER -3 //!< return code
#define MOD_CONTAINER_FIFO_FULL -2 //!< return code
#define MOD_CONTAINER_KO -1 //!< return code
#define MOD_CONTAINER_OK 0 //!< return code

typedef struct ldp_module_context_t ldp_module_context;
typedef struct ldp_req_received_t ldp_req_received;
typedef struct ldp_interface_ctx ldp_interface_ctx;

//! operation to send to a module FIFO
typedef struct ldp_mod_operation{
    ldp_module_context* mod_ctx;//!< context of the receiving module
    uint32_t op_id;               //!< operation ID in the receiving module
    uint32_t op_index;                 //!< operation index in the receiving module
    bool op_activating;    //!< True if this operation is activating in the receiving module
    bool RR_answer_activating;    //!< [only for RR answer] True if this operation is activating in the receiving module
    uint32_t RR_answer_op_index;      //!< [only for RR answer] index of the answer of request
}ldp_mod_operation;

//! operation to send on a socket
typedef struct ldp_socket_operation{
    ldp_interface_ctx* interface;   //!< socket information
    uint32_t op_id;                   //!< operation ID in the receiving module
    uint32_t RR_answer_op_index;      //!< operation index in the receiving module
    bool     RR_answer_op_activating; //!< [only for RR answer] operation activating or not
}ldp_socket_operation;

//! save information for an operation. Contains all informations to send messages to modules or sockets
typedef struct ldp_mod_operation_map{
    char* op_name; //!< sent name operation
    int nb_module; //!< number of module that receive this oepration
    int nb_local_socket; //!< number of local socket (in same node/ PF)
    int nb_ext_socket; //!< number of external socket (outside platform)

    ldp_mod_operation* module_operations;            //!< operation with modules inside the Protection Domain
    ldp_socket_operation* local_socket_operations;   //!< operation with components in other Protection Domains but on the same Platform (and node)
    ldp_socket_operation* external_socket_operations;//!< operation with other platforms
}ldp_mod_operation_map;

/**
 * @brief      hack function to terminate a test platform
 *
 * Send a message to the main process to ask for stopping all protection domains
 *
 * @param      context  The context module
 */
void ldp_kill_platform(ldp_module_context* context);

/**
 * @brief      if all Modules/triggers/dynamic triggers are READY, change the component state in READY and notify father process
 *
 * @param      ctx   The module context that try to send message
 */
void ldp_mod_init_notify(ldp_module_context* ctx);

/**
 * @brief      send an event to all connected modules and all sockets in the same protection domain (broadcast)
 *
 * @param      ctx            sender module
 * @param      param_msg      bytes array that contains parameters TODO
 * @param[in]  param_size     size of param_msg
 * @param[in]  operation_map  operation informations (all modules and sockets, operation IDs, ...)
 * @param      free_buffer    True if param_msg buffer need to be released
 *
 * @return     MOD_CONTAINER_OK or an error code
 */
int ldp_mod_event_send_local(ldp_module_context* ctx,
                               char* param_msg,
                               int param_size,
                               ldp_mod_operation_map operation_map,
                               bool free_buffer);
/**
 * @brief      send an event to sockets connected to other platforms
 */
int ldp_mod_event_send_external(ldp_module_context* ctx,
                                  char* param_msg,
                                  int param_size,
                                  ldp_mod_operation_map operation_map);

/**
 * @brief      send an asynchrone request-response to the first connected module or the first local socket
 *
 * @param      ctx               sender module
 * @param      ID                return the local ID of this request
 * @param      msg_buffer        bytes array that contains parameters
 * @param[in]  param_size        size of param_msg
 * @param[in]  operation_map     operation informations (all modules and sockets, operation IDs, ...)
 * @param      timeout_duration  maximum time before answer
 *
 * @return     MOD_CONTAINER_OK or an error code
 */
int ldp_mod_request_async_send_local(ldp_module_context* ctx,
                                     ECOA__uint32* ID,
                                     char* msg_buffer,
                                     int param_size,
                                     ldp_mod_operation_map* operation_map,
                                     ldp__timestamp* timeout_duration);
/**
 * @brief      send an asynchrone request-response to a socket connected to another platform
 */
int ldp_mod_request_async_send_external(ldp_module_context* ctx,
                                        ECOA__uint32* ID_ptr,
                                        char* buffer_msg,
                                        int params_size,
                                        ldp_mod_operation_map* operation_map,
                                        ldp__timestamp* timeout_duration);
/**
 * @brief      send an synchrone request-response to the first connected module or the first local socket
 *
 * @param      ctx               sender module
 * @param      buffer_msg        bytes array that contains parameters
 * @param[in]  param_size        size of param_msg
 * @param[in]  operation_map     operation informations (all modules and sockets, operation IDs, ...)
 * @param      timeout_duration  maximum time before answer
 *
 * @return     MOD_CONTAINER_OK or an error code
 */
int ldp_mod_request_sync_send_local(ldp_module_context* ctx,
                                      char* buffer_msg,
                                      int param_size,
                                      ldp_mod_operation_map* operation_map,
                                  ldp__timestamp* timeout_duration);
/**
 * @brief      send an synchrone request-response to a socket connected to another platform
 */
int ldp_mod_request_sync_send_external(ldp_module_context* ctx,
                                        char* buffer_msg,
                                        int param_size,
                                        ldp_mod_operation_map* operation_map,
                                        ldp__timestamp* timeout_duration);

/**
 * @brief      send answer of request-response to the local client (module or local socket).
 *
 * @param      ctx         sender module
 * @param      buffer_msg   bytes array that contains parameters TODO
 * @param[in]  param_size  size of param_msg
 * @param      req         structure that contains information about the request like the client and the ID to include in answer
 *
 * @return     MOD_CONTAINER_OK or an error code
 */
int ldp_mod_request_answer_send_local(ldp_module_context* ctx,
                                        char* buffer_msg,
                                        int param_size,
                                        ldp_req_received* req);
/**
 * @brief      send answer of request-response to the external client (client on antoher platform).
 **/
int ldp_mod_request_answer_send_external(ldp_module_context* ctx,
                                        char* buffer_msg,
                                        int param_size,
                                        ldp_req_received* req);

/**
 * @brief      Start a dynamic trigger to remove sent asynchronous RR after timeout
 *
 * @param      ctx                    The context
 * @param      RR_dyn_trigger_thread  The rr dynamic trigger thread
 */
void ldp_mod_start_RR_trigger(ldp_module_context* ctx, apr_thread_t** RR_dyn_trigger_thread);

/**
 * @brief      check concurrent RR number and log if error
 *
 * @param      ctx                The context
 * @param[in]  RR_index           The rr index
 * @param[in]  max_concurrent_RR  The maximum concurrent rr number
 *
 * @return     MOD_CONTAINER_OK, MOD_CONTAINER_KO
 */
int ldp_check_concurrent_RR_num(ldp_module_context* ctx,int RR_index,int max_concurrent_RR);

/**
 * @brief      Stop the RR trigger thread
 *
 * @param      ctx                    The module context
 * @param      RR_dyn_trigger_thread  The rr dynamic trigger thread to stop
 */
void ldp_mod_stop_RR_trigger(ldp_module_context* ctx, apr_thread_t* RR_dyn_trigger_thread);
#endif /* _LDP_MOD_CONTAINER_UTIL_H */

#ifdef __cplusplus
}
#endif
