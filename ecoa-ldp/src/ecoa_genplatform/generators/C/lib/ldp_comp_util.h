/**
* @file ldp_comp_util.h
* @brief File containing functions for component server thread
*
* This module contains functions to manage componenent server thread like :
* - component initialisation function,
* - functions to process received messages
* - ...
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_COMP_UTIL_H
#define _LDP_COMP_UTIL_H


#include <apr.h>
#include <apr_thread_proc.h>

#include "ldp_structures.h"

/**
 * @brief      Wait (join) all module threads (normal modules, triggers or dynamic triggers).
 * @note       Could never finish if a module never stops
 *
 * @param      ctx              component context
 * @param      module_thread    The array of module thread
 * @param      dyn_trig_thread  The array of dynamic trig thread
 * @param      trig_thread      The array of trig thread
 *
 */
void ldp_wait_modules(const ldp_PDomain_ctx* ctx, apr_thread_t** module_thread, apr_thread_t** dyn_trig_thread, apr_thread_t** trig_thread);

/**
 * @brief      compute the maximum of 2 numbers
 *
 * @param[in]  a
 * @param[in]  b
 *
 * @return
 */
uint32_t ldp_max(uint32_t a, uint32_t b);

/**
 * @brief      test if all modules/triggers/dynamic triggers are in READY state
 *
 * @param      ctx   The component context
 *
 * @return     True or False
 */
bool all_module_ready(ldp_PDomain_ctx* ctx);

/**
 * @brief      initialize all VD repositories of Protection Domains
 *
 * @param      ctx   The Protection Domain context
 */
void ldp_init_VD_repositories(ldp_PDomain_ctx* ctx);

/**
 * @brief      Initialize VD Managers (reader and writer) of Modules
 *
 * @param      ctx   The module context
 */
void ldp_init_mod_VD_managers(ldp_module_context* ctx);

/**
 * @brief      Initialize component state mutex and state
 *
 * @param      ctx               The component context
 */
void ldp_comp_init_state(ldp_PDomain_ctx* ctx);

/**
 * @brief      Initialize component threads attributes and completed contexts
 *
 * @param      ctx               The component context
 * @param      mod_attr          The module thread attributes
 * @param      dyn_trigger_attr  The dynamic trigger thread attributes
 * @param      trigger_attr      The trigger thread attributes
 */
void ldp_comp_prepare_module_threads(ldp_PDomain_ctx* ctx, apr_threadattr_t** mod_attr, apr_threadattr_t** dyn_trigger_attr, apr_threadattr_t** trigger_attr);

/**
 * @brief      route a received answer request to sender module
 * Push a RR response message in fifo of module :
 * 	- find the client module by reading message
 * 	- check if RR message id corresponds to a RR send by the target module
 * 	- then push message in target module fifo
 *
 * @param      ctx       The component context
 * @param      read_msg  The read message
 * @param      client_mod_ID ID of the module client
 * @param      req_id     ID of the curretn request
 * @param      op_id     The operation ID of the incoming answer
 */
void ldp_comp_received_answer_request(ldp_PDomain_ctx* ctx,
										char* parameters,
										uint32_t parameter_size,
										uint32_t client_mod_ID,
										uint32_t op_id);
/**
 * @brief      Route received request to one module fifo
 * Create a request_received object, add this request_received in module req_resp structure and push RR message to module fifo
 *
 * @param      ctx            The component context
 * @param      read_msg       The read message
 * @param[in]  msg_size       The read message size
 * @param      mod_ctx        The target module context that will received the request
 * @param      socket_sender  The socket sender to send answer with the same socket
 * @param      ELI_sequence_num
 * @param[in]  response_op_id   The operation identifier to write answer with the same ID
 * @param      op_link_index  The operation link index, used to retrived the current number of this operation that are already in module FIFO
 * @param      activating_op  Boolean that shows if operation is activating
 * @param      op_id          The operation ID of the incoming request
 */
void ldp_comp_received_request (ldp_PDomain_ctx* ctx,
									char* read_msg,
									uint32_t msg_size,
									ldp_module_context* mod_ctx,
									ldp_interface_ctx* socket_sender,
									uint32_t ELI_sequence_num,
									uint32_t response_op_id,
									int op_link_index,
									bool activating_op,
									uint32_t op_id);

/**
 * @brief      Route event message to modules fifos.
 * Copy read message in a buffer and push this buffer in module fifo
 *
 * @param      ctx       Component context
 * @param      copy_msg  if True, read_msg need to be copied in a new buffer.
 * @param      read_msg  The read message
 * @param[in]  msg_size  The read message size
 * @param      mod_ctx   Module context
 * @param      op_link_index  The operation link index, used to retrived the current number of this operation that are already in module FIFO
 * @param      activating_op  Boolean that shows if operation is activating
 * @param      op_id          Operation ID of the incoming event
 */
void ldp_comp_received_event (ldp_PDomain_ctx* ctx,
								bool copy_msg,
								char* read_msg,
								int msg_size,
								ldp_module_context* mod_ctx,
								int op_link_index,
								bool activating_op,
								uint32_t op_id);

/**
 * @brief      Notify module when Versioned Data has been updated by pushing a message in FIFOs.
 *
 * @param      PD_ctx         The Protection Domain context
 * @param      mod_ctx        The module context to notify
 * @param[in]  op_link_index  The operation link index to use
 * @param[in]  activating_op  True if the notifying operation is an activated operation
 * @param[in]  op_id          The notifying operation identifier to use
 */
void ldp_comp_notify_mod_VD(ldp_PDomain_ctx* PD_ctx, ldp_module_context* mod_ctx, int op_link_index, bool activating_op, uint32_t op_id);

/**
 * @brief      destroy all APR and ldp structures and free memory for a protection domain.
 *
 * @param      ctx   The context of the protection domain
 */
void ldp_destroy_component(ldp_PDomain_ctx* ctx);

/**
 * @brief      find module context with the module ID
 *
 * @param      ctx        The ontext of the Protection Domain
 * @param[in]  module_id  The module identifier
 *
 * @return     a module context or NULL
 */
ldp_module_context* find_module_context(ldp_PDomain_ctx* ctx, uint16_t module_id);

/**
 * @brief      destroy module context
 *
 * @param      ctx        The ontext of the Protection Domain
 */
void ldp_destroy_module(ldp_module_context* ctx);

#endif /*_LDP_COMP_UTIL_H */
#ifdef __cplusplus
}
#endif
