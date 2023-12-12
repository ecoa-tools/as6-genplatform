/**
* @file ldp_dynamic_trigger.c
* @brief ECOA dynamic trigger functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>

#include <time.h>
#include <pthread.h> //???????????
#include <apr.h>
#include <apr_thread_proc.h>

#include "ldp_dynamic_trigger.h"
#include "ldp_structures.h"
#include "ldp_mod_container_util.h"
#include "ldp_time_manager.h"
#include "ldp_status_error.h"
#include "ldp_fifo_manager.h" // sonarQube might remove its error in the ldp_pop_fifo_manager function

/**
 * @brief      stop trigger thread
 *
 * @param      ctx             The module dynamic trigger context
 * @param      trigger_thread  The trigger thread
 *
 * @return     return value
 */
static apr_status_t stop_trigger_thread(ldp_dyn_trigger_context* ctx, apr_thread_t** trigger_thread){
	apr_status_t ret_val;

	// stop trigger thread
	ctx->state = IDLE;
	ldp_reset_dynamic_trigger(ctx);

	// wait thread
	apr_thread_join(&ret_val, *trigger_thread);
	return ret_val;
}

/*SonarQube : function for the first case of ldp_start_module_dynamic_trigger*/
void initialize_life(ldp_dyn_trigger_context* ctx) {
	if(ctx->state == IDLE){
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]: INITIALIZE", ctx->name);

		ldp_reset_dynamic_trigger(ctx);
		ctx->state = READY;
		ldp_mod_init_notify((ldp_module_context*)ctx);
	}else{
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF,"[%s]: received INITIALIZE. Invalid state", ctx->name);
        ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                         ECOA__error_type_INITIALISATION_PROBLEM, 9);
	}
}

/*SonarQube : function for the second case of ldp_start_module_dynamic_trigger*/
void start_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0, apr_threadattr_t** attr0, apr_pool_t* thread_pool) {
	int ret;

	if(ctx->state == READY){
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,"[%s]: START", ctx->name);
		ctx->state = RUNNING;

		// create thread
		ret=apr_threadattr_create(attr0, thread_pool);
		assert(ret==APR_SUCCESS);
		ret=apr_thread_create(tid0,*attr0, ldp_start_dynamic_trigger, (void*) ctx, thread_pool);
		assert(ret==APR_SUCCESS);
	}else{
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNNING", ctx->logger_PF,"[%s]: received START. Invalid state", ctx->name);
        ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                         ECOA__error_type_INITIALISATION_PROBLEM, 10);
	}
}

/*SonarQube : function for the third case of ldp_start_module_dynamic_trigger*/
void stop_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0) {
	if(ctx->state == RUNNING){
		ctx->state = READY;
		ldp_fifo_manager_clean(ctx->fifo_manager, ctx->state, NULL);
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]: STOP", ctx->name);
		stop_trigger_thread(ctx, tid0);
	}else{
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNNING", ctx->logger_PF,"[%s]: received STOP. Invalid state", ctx->name);
	}
}

/*SonarQube : function for the fourth case of ldp_start_module_dynamic_trigger*/
void shutdown_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0) {
	if(ctx->state != IDLE){
		ctx->state = IDLE;
		ldp_fifo_manager_clean(ctx->fifo_manager, ctx->state, NULL);
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]: SHUTDOWN", ctx->name);
		stop_trigger_thread(ctx, tid0);

		// reinit trigger_event_tab
		for(int i=0;i<ctx->max_event_nb;i++){
			ctx->trigger_event_tab[i].is_set=0;
			ctx->trigger_event_tab[i].expiration_date.seconds = TIME_INFINITY;
		}
	}else{
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNNING", ctx->logger_PF,"[%s]: received SHUTDOWN. Invalid state", ctx->name);
	}

}

/*SonarQube : function for the fifth case of ldp_start_module_dynamic_trigger*/
void kill_life(ldp_dyn_trigger_context* ctx, apr_thread_t** tid0) {
	if(ctx->state != IDLE) {
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]: KILL", ctx->name);
		stop_trigger_thread(ctx, tid0);
	}
	ctx->state = IDLE;
	ldp_fifo_manager_clean(ctx->fifo_manager, ctx->state, NULL);
}


void ldp_init_dynamic_trigger(ldp_dyn_trigger_context* ctx){
	ctx->trigger_event_tab = calloc(ctx->max_event_nb, sizeof(ldp_dyn_trigger_event));
	for(int i=0;i<ctx->max_event_nb;i++){
		ctx->trigger_event_tab[i].is_set=0;
		ctx->trigger_event_tab[i].expiration_date.seconds = TIME_INFINITY;
		ctx->trigger_event_tab[i].parameters = malloc(LDP_HEADER_TCP_SIZE + ctx->params_size);
		ldp_written_IP_header(ctx->trigger_event_tab[i].parameters, ctx->params_size, 0);
	}

	pthread_condattr_t attr;
	pthread_condattr_init(&attr);
	pthread_condattr_setclock(&attr, CLOCK_MONOTONIC); // or use ldp_get_ecoa_absolute_time instead of ldp_get_time
	int ret=pthread_cond_init(&ctx->cond, &attr);
	assert(ret == 0);
	ret=pthread_mutex_init(&ctx->mutex, NULL);
	assert(ret == 0);

	UNUSED(ret);
}

void ldp_destroy_dynamic_trigger(ldp_dyn_trigger_context* ctx){

	for(int i=0;i<ctx->max_event_nb;i++){
		free(ctx->trigger_event_tab[i].parameters);
	}
	free(ctx->trigger_event_tab);
	pthread_cond_destroy(&ctx->cond);
	pthread_mutex_destroy(&ctx->mutex);
}

void ldp_reset_dynamic_trigger(ldp_dyn_trigger_context* ctx){
	for(int i=0;i<ctx->max_event_nb;i++){
		ctx->trigger_event_tab[i].is_set=0;
		ctx->trigger_event_tab[i].expiration_date.seconds = TIME_INFINITY;
	}
	pthread_mutex_lock(&ctx->mutex);
	pthread_cond_signal(&ctx->cond);
	pthread_mutex_unlock(&ctx->mutex);
}

void* ldp_start_module_dynamic_trigger(apr_thread_t* t, void* args){
	ldp_dyn_trigger_context* ctx = (ldp_dyn_trigger_context*) args;
	ldp_element* elt;
	apr_thread_t* tid0 = NULL;
	apr_threadattr_t* attr0;
	ctx->state = IDLE;
	int ret;
	bool server_running = true;
	apr_pool_t* thread_pool = apr_thread_pool_get(t);
	ldp_init_dynamic_trigger(ctx);

	while(server_running){
		ldp_fifo_manager_pop_elt(ctx->fifo_manager, &elt);
		switch(elt->op_ID){
			case LDP_ID_INITIALIZE_life :
				initialize_life(ctx);
				break;
			case LDP_ID_START_life :
				start_life(ctx, &tid0, &attr0, thread_pool);
				break;

			case LDP_ID_STOP_life :
				stop_life(ctx, &tid0);
				break;

			case LDP_ID_SHUTDOWN_life :
				shutdown_life(ctx, &tid0);
				break;

			case LDP_ID_KILL_life :
				kill_life(ctx, &tid0);
				server_running = false;// to stop while loop
				break;

			default :
				if(ctx->state != RUNNING){
					ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF, "[%s]: dynamic trigger is not in RUNNING state", ctx->name);
				}else if(elt->op_ID == ID_dynamic_trigger_in){
					ECOA__duration delayDuration;
					memcpy(&delayDuration,&elt->parameters[0],sizeof(delayDuration)); // ttt
					void* parameters=&elt->parameters[sizeof(delayDuration)]; // ttt
					ldp_set_dynamic_trigger(ctx, &delayDuration, parameters, &ldp_handler_dynamic_trigger_module);
				}else if(elt->op_ID == ID_dynamic_trigger_reset){
					ldp_reset_dynamic_trigger(ctx);
				}else{
					ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF, "[%s]: unknow msg %i", ctx->name, elt->op_ID);
				}
		}
		//ret=ldp_free_buffer(ctx->buf_pool, &elt.data);
    ret = ldp_fifo_manager_release_elt(ctx->fifo_manager, elt);
 		assert(ret != -1);
	}
	ldp_destroy_dynamic_trigger(ctx);
	UNUSED(ret);
	return NULL;
}

void* ldp_start_dynamic_trigger(apr_thread_t* t, void* args){
	ldp_dyn_trigger_context* ctx = (ldp_dyn_trigger_context*) args;
	ctx->mem_pool = apr_thread_pool_get(t);

	ldp__timestamp timeout = {0,0};
	ldp__timestamp current_time= {0,0};
	struct timespec timeout2= {0,0};
	int retval = 0;

	while(ctx->state == RUNNING){
		timeout.seconds = TIME_INFINITY;

		pthread_mutex_lock(&ctx->mutex);
		// compute next time_out
		for(int i= 0 ; i< ctx->max_event_nb;i++){
			if(ctx->trigger_event_tab[i].is_set == 1){
				retval = ldp_time_cmp(&ctx->trigger_event_tab[i].expiration_date,&timeout);
				if (retval == 0){
					timeout = ctx->trigger_event_tab[i].expiration_date;
				}
			}
		}

		timeout2.tv_sec = timeout.seconds;
		timeout2.tv_nsec = timeout.nanoseconds;

		// wait timeout or a wakeup
		pthread_cond_timedwait(&ctx->cond,&ctx->mutex,&timeout2);
		pthread_mutex_unlock(&ctx->mutex);

		// find events to send
		ldp_get_time(&current_time);
		for(int i= 0 ; i< ctx->max_event_nb;i++){
			if(ctx->trigger_event_tab[i].is_set == 1){
				retval = ldp_time_cmp(&ctx->trigger_event_tab[i].expiration_date, &current_time);
				if (retval == 0){
					(ctx->trigger_event_tab[i].handler)(ctx,ctx->trigger_event_tab[i].parameters);
					ctx->trigger_event_tab[i].expiration_date.seconds = TIME_INFINITY;
					ctx->trigger_event_tab[i].expiration_date.nanoseconds = TIME_INFINITY;
					ctx->trigger_event_tab[i].is_set = 0;
				}
			}
		}
	}

	return NULL;
}


ldp_status_t ldp_set_dynamic_trigger(ldp_dyn_trigger_context* ctx, const ECOA__duration *delayDuration, void* parameters, ldp_handler_dynamic_trigger handler_fct){
	// check duration
	ldp__timestamp current_time;

	ldp_get_time(&current_time);

	// find free trigger_event
	for(int i= 0 ; i< ctx->max_event_nb;i++){
		if(ctx->trigger_event_tab[i].is_set == 0){

			ldp_add_time(&current_time, (ldp__timestamp*) delayDuration);
			ctx->trigger_event_tab[i].expiration_date.seconds = current_time.seconds;
			ctx->trigger_event_tab[i].expiration_date.nanoseconds = current_time.nanoseconds;
			char* trigger_params = ctx->trigger_event_tab[i].parameters;
			memcpy(&trigger_params[LDP_HEADER_TCP_SIZE], parameters,ctx->params_size);
			ctx->trigger_event_tab[i].is_set=1; // now is set
			ctx->trigger_event_tab[i].handler = handler_fct;

			pthread_mutex_lock(&ctx->mutex);
			pthread_cond_signal(&ctx->cond);
			pthread_mutex_unlock(&ctx->mutex);
			return LDP_SUCCESS;
		}
	}
	ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF, "[%s]: cannot set dynamic trigger. max number of events reached", ctx->name);
    ldp_send_fault_error_to_father(ctx->component_ctx, ctx->mod_id, ECOA__asset_type_COMPONENT,
                                     ECOA__error_type_RESOURCE_NOT_AVAILABLE, 17);
	return LDP_ERROR;
}

void ldp_handler_dynamic_trigger_module(ldp_dyn_trigger_context* ctx, void* parameters){
	ldp_mod_event_send_local((ldp_module_context *) ctx,parameters , ctx->params_size, ctx->operation_map[0], false);
	// TODO send external
}

void ldp_handler_dynamic_trigger_RR_async(ldp_dyn_trigger_context* ctx, void* parameters){
	ldp_node* node;
	ldp_dyn_trigger_RR_param* RR_param = (ldp_dyn_trigger_RR_param*) &(((char *)parameters)[LDP_HEADER_TCP_SIZE]);
	ldp_req_sent* req = NULL;
	req = ldp_find_req_sent(&RR_param->mod_ctx->req_resp, RR_param->request_ID, &node);
	if (req != NULL){
		// free it if it exists and push in fifo to inform module of a out fo date RR
		ldp_free_req_sent(&RR_param->mod_ctx->req_resp, node);
		ldp_log_PF_log(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF, "Asynchronous RR timeout ");

		char msg[sizeof(ECOA__uint32)]; //minimal message of a RR answer
		ECOA__uint32 err = ECOA__UINT32_MAX;

		memcpy((char *)&msg[0], &err, sizeof(ECOA__uint32));
		if( ldp_fifo_manager_push(RR_param->mod_ctx->fifo_manager,
									req->resp_op_index,
									req->resp_op_id,
									RR_ANSWER,
									req->resp_op_activating,
									sizeof(ECOA__uint32),
									msg,
                                                                        RR_param->mod_ctx->mod_id) != MOD_CONTAINER_OK){
			ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF,
								 " [%s] cannot push in fifo %s", ctx->name, RR_param->mod_ctx->name);
		}
	}
	// else : nothing to do, the answer has arrived already
}
