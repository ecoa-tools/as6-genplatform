/**
* @file ldp_trigger.h
* @brief ECOA trigger functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_TRIGGER_H
#define _LDP_TRIGGER_H

#include <time.h>
#include <signal.h>
#include <sys/syscall.h>
#include <apr.h>
#include <apr_thread_proc.h>


#include "ldp_structures.h"
#include "ldp_status_error.h"

#define CLOCKID CLOCK_REALTIME //!< clock used to measure time
#define SIG SIGRTMIN //!< signal raised by a trigger to wake up a thread

//! structure for event of an trigger module. Handle all periods, operations,...
typedef struct ldp_trigger_event_context_t{
	long int thread_trigger_id; //!< tid of thread that will consume this event
	float period; //!< period of this event
	int nb_operations; //!< nb of operations for this event
	int* operation_indexes; //!< indexes in operation_map that must be sent
}ldp_trigger_event_context;

//! attribute for a timer thread
typedef struct ldp_event_thread_timer_attr_t{
	ldp_trigger_context* ctx; //!< context of the trigger module
	int trigger_event_index; //!< index of trigger event to find ldp_trigger_event_context in ctx
}ldp_event_thread_timer_attr;

/**
 * @brief create a timer : create a pthread_timer that will send a signal to the specific thread_id
 * @param timer will contains timer created
 * @param thread_id tid of thread to be wakeup by timer
 * @return LDP_ERROR in case of failure or LDP_SUCCESS
 */
ldp_status_t ldp_create_timer(timer_t* timer, pid_t thread_id);
/**
 * @brief start timer by setting period
 * @param timer
 * @param period new period of timer
 * @return LDP_ERROR in case of failure or LDP_SUCCESS
 */
ldp_status_t ldp_start_timer(timer_t timer, float period);

/**
 * @brief stop timer by setting period to zero
 * @param timer
 * @return LDP_ERROR in case of failure or LDP_SUCCESS
 */
ldp_status_t ldp_stop_timer(timer_t timer);

/**
 * @brief thread function that will consume a timer event by sending message to connected modules or sockets
 * In this function the thread is blocked by a sigwait. The thread is unblock when a timer send signal to its
 * @param args contains a pointer to the trigger context
 * @note should never return
 */
void* ldp_event_thread_timer(void* args);

/**
 * @brief start module trigger thread
 *  - this is an ECOA module (with a lifecycle, a fifo, ...)
 *  - create timers
 *  - create one ldp_event_thread_timer by period. Those threads will be wake up by timers trigger.
 *		   Then they will send messages to connected modules or sockets
 * @param t
 * @param args contains a pointer to the trigger context
 * @note should never return
 */
void * ldp_start_module_trigger(apr_thread_t* t, void* args);

#endif /* _LDP_TRIGGER_H */

#ifdef __cplusplus
}
#endif
