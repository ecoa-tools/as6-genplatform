/**
* @file ldp_dynamic_trigger.h
* @brief ECOA dynamic trigger functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef _LDP_DYNAMIC_TRIGGER_H
#define _LDP_DYNAMIC_TRIGGER_H

#ifdef __cplusplus
extern "C" {
#endif

#define TIME_INFINITY ECOA__UINT32_MAX //!< maximum time

#include "ldp_structures.h"
#include "ECOA.h"
#include "ldp_time_manager.h"
#include <apr_thread_proc.h>
#include "ldp_status_error.h"

#define ID_dynamic_trigger_in 500 //!< event ID
#define ID_dynamic_trigger_reset 501 //!< event ID

//! parameters for a RR timeout event
typedef struct ldp_dyn_trigger_RR_param_t{
	ECOA__uint32 request_ID; //!< ID of the oudated RR
	ldp_module_context* mod_ctx; //!< ctx of the module that send this outdated RR
}ldp_dyn_trigger_RR_param;

//! function type to handle a event: normale dynamiq trigger or RR dynamic triggger
typedef void (*ldp_handler_dynamic_trigger)(ldp_dyn_trigger_context* ctx, void* parameters);

//! structure for a dynamic trigger event. Set during execution.
typedef struct ldp_dyn_trigger_event_t{
	int is_set; //!< equals to 1 if this event is set. 0 in other case.
	ldp__timestamp expiration_date; //!< expiration date for this event
	ldp_handler_dynamic_trigger handler; //!< function pointer to do something after expiration date
	void* parameters;//!< pointer to parameters memory space
}ldp_dyn_trigger_event;

/**
 * @brief      Start main thread of a dynamic trigger module
 * This thread is like a normal module thread : it is listening new message on module fifo
 *
 * @param      t     apr thread structure
 * @param      args  Contains pointer to the dynamic trigger context
 *
 * @note       should never return
 */
void* ldp_start_module_dynamic_trigger(apr_thread_t* t, void* args);

/**
 * @brief      start the dynamic trigger thread
 * this thread wait an expiration date and send messages
 *
 * @param      t     apr thread structure
 * @param      args  contains pointer to the dynamic trigger context and handle function pointer
 * @note       Should never return
 */
void* ldp_start_dynamic_trigger(apr_thread_t* t, void* args);

/**
 * @brief      Initialize a dynamic trigger structure memory
 *
 * @param      ctx   The context of the dynamic trigger
 */
void ldp_init_dynamic_trigger(ldp_dyn_trigger_context* ctx);

/**
 * @brief      reset dynamic trigger by removing waitting events
 *
 * @param      ctx   The context of the dynamic trigger
 */
void ldp_reset_dynamic_trigger(ldp_dyn_trigger_context* ctx);

/**
 * @brief      set a dynamic trigger by adding a new event date
 *
 * @param      ctx            The dynamic trigger context
 * @param[in]  delayDuration  The delay duration to wait before sending event
 * @param      parameters     The bytes array that contains parameters values
 * @param[in]  handler_fct    The handler fct to use to send event after delay
 *
 * @return     LDP_ERROR in case of failure (wrong delayDuration or no more free trigger_event structure) or LDP_SUCCESS
 */
ldp_status_t ldp_set_dynamic_trigger(ldp_dyn_trigger_context* ctx, const ECOA__duration *delayDuration, void* parameters, ldp_handler_dynamic_trigger handler_fct);

/**
 * @brief      handle of a dynamic trigger used by normal module
 * Send events to modules
 *
 * @param      ctx         The contextof the dynamic trigger
 * @param      parameters  The parameters that should be included in events that are sent to modules
 */
void ldp_handler_dynamic_trigger_module(ldp_dyn_trigger_context* ctx, void* parameters);

/**
 * @brief      handle of a dynamic trigger used for asynchronous request response.
 * When a RR is out of date and if the RR existed still : inform the module by sending an answer with an error code
 *
 * @param      ctx         The contextof the dynamic trigger
 * @param      parameters  The parameters : a pointer to a ldp_dyn_trigger_RR_param structure. Used to send answer to the right module
 */
void ldp_handler_dynamic_trigger_RR_async(ldp_dyn_trigger_context* ctx, void* parameters);

/**
 * Free memory area of a dynamic trigger before end of thread
 */
void ldp_destroy_dynamic_trigger(ldp_dyn_trigger_context* ctx);

/**
 * @brief      initialize dynamic trigger
 *
 * @param      ctx   The context of the dynamic trigger
 */
void initialize_life(ldp_dyn_trigger_context* ctx);

/**
 * @brief      start dynamic trigger
 *
 * @param      ctx          The context of the dynamic trigger
 * @param      tid0         apr thread handle
 * @param      attr0        Handle to apr thread attribute
 * @param      thread_pool  Pool of thread
 */
void start_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0, apr_threadattr_t** attr0, apr_pool_t* thread_pool);

/**
 * @brief      stop dynamic trigger
 *
 * @param      ctx   The context of the dynamic trigger
 * @param      tid0  apr thread handle
 */
void stop_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0);

/**
 * @brief      shutdown dynamic trigger
 *
 * @param      ctx   The context of the dynamic trigger
 * @param      tid0  apr thread handle
 */
void shutdown_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0);

/**
 * @brief      kill dynamic trigger
 *
 * @param      ctx   The context of the dynamic trigger
 * @param      tid0  apr thread handle
 */
void kill_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0);

#ifdef __cplusplus
}
#endif
#endif /* _LDP_DYNAMIC_TRIGGER_H */
