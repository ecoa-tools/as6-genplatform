/**
* @file ldp_trigger.c
* @brief ECOA trigger functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#define _GNU_SOURCE /* Needed for syscall */
#include <time.h>
#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <pthread.h>
#include <assert.h>
#include <apr.h>
#include <apr_thread_proc.h>


#include "ldp_trigger.h"
#include "ldp_network.h"
#include "ldp_structures.h"
#include "ldp_mod_container_util.h" // to send message to modules and sockets
#include "ldp_status_error.h"

ldp_status_t ldp_create_timer(timer_t* timer, pid_t thread_id){
	// create sigevent
	struct sigevent sigev;
	sigev.sigev_notify = SIG;
	sigev.sigev_signo = SIG;
	sigev.sigev_value.sival_ptr = timer;
	sigev.sigev_notify =  SIGEV_THREAD_ID;
	sigev._sigev_un._tid = thread_id; // signal will be sent to this thread

	// create timer
	if (timer_create(CLOCKID, &sigev, timer) != 0){
		return LDP_ERROR;
	}
	return LDP_SUCCESS;
}


ldp_status_t ldp_start_timer(timer_t timer, float period){

	struct itimerspec its;
	its.it_value.tv_sec = (int)(period);
	its.it_value.tv_nsec = (int)((period - (float)its.it_value.tv_sec)*1000000000.0);
	its.it_interval.tv_sec = its.it_value.tv_sec;
	its.it_interval.tv_nsec = its.it_value.tv_nsec;

	//start timer
	if (timer_settime( timer, 0, &its, NULL) == -1){
		return LDP_ERROR;
	}
	return LDP_SUCCESS;
}


ldp_status_t ldp_stop_timer(timer_t timer){
	struct itimerspec its;
	its.it_value.tv_sec = 0;
	its.it_value.tv_nsec = 0;
	its.it_interval.tv_sec = its.it_value.tv_sec;
	its.it_interval.tv_nsec = its.it_value.tv_nsec;

	//stop timer
	if (timer_settime( timer, 0, &its, NULL) == -1){
		return LDP_ERROR;
	}
	return LDP_SUCCESS;

}


void* ldp_event_thread_timer(void* args){

	ldp_trigger_context* ctx = ((ldp_event_thread_timer_attr*)args)->ctx;
	int event_index = ((ldp_event_thread_timer_attr*)args)->trigger_event_index;

	// save PID in memory structure
	ctx->trigger_events[event_index].thread_trigger_id = syscall(SYS_gettid);
	pthread_barrier_wait(&ctx->barr);

	// create a sigset
	sigset_t sigset;
	sigemptyset(&sigset);
	sigaddset(&sigset, SIG);
	sigprocmask(SIG_BLOCK, &sigset,NULL);
	char msg[LDP_HEADER_TCP_SIZE];


	int signum = SIG;
	while(ctx->state != IDLE){
		// wait signal
		sigwait(&sigset, &signum);

		if( signum == SIG){
			for(int i=0; i< ctx->trigger_events[event_index].nb_operations;i++){
				int op_index = ctx->trigger_events[event_index].operation_indexes[i];
				if(ctx->state != IDLE){
					ldp_mod_event_send_local((ldp_module_context*)ctx, msg,0, ctx->operation_map[op_index], false);
					// TODO: add external function
				}else{
					// stopping thread
					break;
				}
			}
		}else{
			break;
		}
	}
	return NULL;
}

/**
 * @brief      Initialize trigger module : start trigger threads and timers threads
 *
 * @param      ctx     The trigger module context
 * @param      timers  The timer threads
 * @param      tids    The trigger threads
 * @param      attrs   The attributes of trigger threads
 *
 * @return     LDP_ERROR or LDP_SUCCESS
 */
static ldp_status_t initialize_trigger(ldp_trigger_context* ctx, timer_t* timers,
                                         pthread_t* tids, pthread_attr_t* attrs){
	ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
                         "[%s]:[%li] START threads and create timers",ctx->name, apr_time_now());

	ctx->state = READY;
	// create all event_timer_threads
	ldp_event_thread_timer_attr thread_attr[ctx->nb_trigger_event];
	for(int i=0; i< ctx->nb_trigger_event;i++){
		thread_attr[i].ctx = ctx;
		thread_attr[i].trigger_event_index = i;
		if(pthread_create(&tids[i] , &attrs[i], &ldp_event_thread_timer, &thread_attr[i]) != 0){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s]: pthread_create failed", ctx->name);
			return LDP_ERROR;
		}
	}

	// wait that all event_thread_triggers have saved PID in memory structure
	pthread_barrier_wait(&ctx->barr);
	//  create all timers (one per periods)
	for(int i=0; i< ctx->nb_trigger_event;i++){
		if(ldp_create_timer(&timers[i],ctx->trigger_events[i].thread_trigger_id) != LDP_SUCCESS){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s]: timer_create error", ctx->name);
			return LDP_ERROR;
		}
	}

	return LDP_SUCCESS;
}

/**
 * @brief      Stops trigger module and join threads
 *
 * @param      ctx     The context
 * @param      timers  The timers
 * @param      tids    The tids
 *
 * @return     LDP_SUCCESS or never return (block by a join)
 */
static apr_status_t stop_trigger(ldp_trigger_context* ctx, timer_t* timers, pthread_t* tids){
    UNUSED(tids);
	ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] STOP timers and threads",ctx->name);
	ctx->state = IDLE;

	// stop timer threads
	for(int i=0; i< ctx->nb_trigger_event;i++){
		if(ldp_stop_timer(timers[i]) != LDP_SUCCESS){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s]: fail to stop timer", ctx->name);
		}else{
			int ret=timer_delete(timers[i]);
			assert(ret == 0);
			UNUSED(ret);
		}
	}

	// stop trigger threads
	for(int i=0; i< ctx->nb_trigger_event;i++){
		pthread_kill(tids[i],SIG);
	}
	for(int i=0; i< ctx->nb_trigger_event;i++){
		pthread_join(tids[i],NULL);
	}
	return LDP_SUCCESS;
}


void * ldp_start_module_trigger(apr_thread_t* t, void* args){
	ldp_trigger_context* ctx = (ldp_trigger_context*) args;
	ctx->mem_pool = apr_thread_pool_get(t);

	pthread_t tids[ctx->nb_trigger_event];
    for(int i=0; i<ctx->nb_trigger_event; i++){
        tids[i] = 0;
    }
	pthread_attr_t attrs[ctx->nb_trigger_event];
	for(int i=0; i<ctx->nb_trigger_event;i++){
		pthread_attr_init(&attrs[i]);
    }
	pthread_barrier_init(&ctx->barr, NULL, ctx->nb_trigger_event+1);

	timer_t timers[ctx->nb_trigger_event];
    for(int i=0; i<ctx->nb_trigger_event; i++){
        timers[i] = 0;
    }

	ldp_element* elt;
	ctx->state = IDLE;
	bool is_running=true;
	while(is_running){
		ldp_fifo_manager_pop_elt(ctx->fifo_manager, &elt);

		switch (elt->op_ID){
			case LDP_ID_INITIALIZE_life :
				if(ctx->state == IDLE ){
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] INIT trigger",ctx->name);
					if (initialize_trigger(ctx, timers, tids, attrs) != LDP_SUCCESS){
						return NULL;
					}
					ldp_mod_init_notify((ldp_module_context*)ctx);
					ctx->state = READY;
				}else{
					ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF,
					                     "[%s]: received INITIALIZE. Invalid state", ctx->name);
                    ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                                     ECOA__error_type_INITIALISATION_PROBLEM, 7);
				}
				break;

			case LDP_ID_START_life :
				if(ctx->state == READY){
					ctx->state = RUNNING;
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] STAAART trigger",ctx->name);
					//start all timers (one per period)
					for(int i=0; i< ctx->nb_trigger_event;i++){
						if(ldp_start_timer(timers[i],ctx->trigger_events[i].period) != LDP_SUCCESS){
							ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s]: fail to start timer", ctx->name);
						}
					}
				}else{
					ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF,"[%s]: received START. Invalid state", ctx->name);
                    ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                                     ECOA__error_type_INITIALISATION_PROBLEM, 8);
				}
				break;

			case LDP_ID_STOP_life :
				if(ctx->state == RUNNING){
					ctx->state = READY;
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] STOOP trigger",ctx->name);
					ldp_fifo_manager_clean(ctx->fifo_manager, ctx->state, NULL);
					for(int i=0; i< ctx->nb_trigger_event;i++){
						if(ldp_stop_timer(timers[i]) != LDP_SUCCESS){
							ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s]: fail to stop timer", ctx->name);
						}
					}
				}else{
					ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF,"[%s]: received STOP. Invalid state", ctx->name);
				}
				break;

			case LDP_ID_SHUTDOWN_life :
				if(ctx->state != IDLE){
					ctx->state = IDLE;
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] SHUTDOWN trigger",ctx->name);
					ldp_fifo_manager_clean(ctx->fifo_manager, ctx->state, NULL);
					stop_trigger(ctx, timers, tids);
				}else{
					ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF,
					                     "[%s]: received SHUTDOWN. Invalid state", ctx->name);
				}
				break;

			case LDP_ID_KILL_life :
                if (ctx->state != IDLE){
                    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] KILL trigger",ctx->name);
                    stop_trigger(ctx, timers, tids);
                }
                ctx->state = IDLE;
                is_running = false;
				break;

			default:
				ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF, "[%s]: unknow msg %i", ctx->name, elt->op_ID);
		}

		apr_status_t ret = ldp_fifo_manager_release_elt(ctx->fifo_manager, elt);
		assert(ret != -1);
		UNUSED(ret);

	}

	return NULL;
}
