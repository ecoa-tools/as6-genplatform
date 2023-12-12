/**
* @file ldp_comp_util.c
* @brief ECOA component functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <assert.h>
#include <apr.h>
#include <apr_thread_cond.h>

#include "ldp_thread.h"
#include "ldp_trigger.h"
#include "ldp_mod_container_util.h"
#include "ldp_structures.h"
#include "ldp_fifo.h"
#include "ldp_request_response.h"
#include "ldp_comp_util.h"
#include "ldp_dynamic_trigger.h"
#include "ldp_status_error.h"
#include "ldp_fifo_manager.h"


uint32_t ldp_max(uint32_t a, uint32_t b){
	return ((a > b) ? a : b);
}

bool all_module_ready(ldp_PDomain_ctx* ctx){
	for (int i=0; i< ctx->nb_module; i++){
		if ( ctx->worker_context[i].state != READY){
			return false;
		}
	}
	for (int i=0; i< ctx->nb_trigger; i++){
		if ( ctx->trigger_context[i].state != READY){
			return false;
		}
	}
	for (int i=0; i< ctx->nb_dyn_trigger; i++){
		if ( ctx->dyn_trigger_context[i].state != READY){
			return false;
		}
	}
	return true;
}

void ldp_wait_modules(const ldp_PDomain_ctx* ctx, apr_thread_t** module_thread, apr_thread_t** dyn_trig_thread, apr_thread_t** trig_thread){

	ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF, "[%s] join modules threads ...", ctx->name);
	apr_status_t retval;

	// wait normal modules
	for(int i=0; i<ctx->nb_module;i++){
		        apr_thread_join(&retval, module_thread[i]);
	}

	//wait trigger
	for(int i=0; i<ctx->nb_trigger;i++){
		apr_thread_join(&retval, trig_thread[i]);
	}

	// wait dynamic trigger
	for(int i=0; i<ctx->nb_dyn_trigger;i++){
		apr_thread_join(&retval, dyn_trig_thread[i]);
	}
}

void ldp_init_VD_repositories(ldp_PDomain_ctx* ctx){
	for(int i=0; i<ctx->num_VD_repo; i++){
		ldp_init_repository(&ctx->VD_repo_array[i]);
	}
}


void ldp_init_mod_VD_managers(ldp_module_context* ctx){
	for (int i=0; i<ctx->num_reader_mng; i++){
		ldp_init_reader_mng(&ctx->VD_reader_managers[i]);
	}
	for (int i=0; i<ctx->num_writter_mng; i++){
		ldp_init_writter_mng(&ctx->VD_writter_managers[i]);
	}
}

// TODO rename function
void ldp_comp_init_state(ldp_PDomain_ctx* ctx){
	//init mutex
	ctx->state = PDomain_IDLE;
    apr_thread_mutex_create(&ctx->state_mutex, APR_THREAD_MUTEX_UNNESTED,ctx->mem_pool);
    ctx->msg_buffer = calloc(ctx->msg_buffer_size, sizeof(char));
    apr_thread_mutex_create(&ctx->external_mutex, APR_THREAD_MUTEX_UNNESTED,ctx->mem_pool);
	ctx->external_msg_buffer = calloc(ctx->msg_buffer_size, sizeof(char));
}

void ldp_comp_prepare_module_threads(ldp_PDomain_ctx* ctx, apr_threadattr_t** mod_attr, apr_threadattr_t** dyn_trigger_attr, apr_threadattr_t** trigger_attr){
	int ret;

	// start module trigger threads
	for(int i=0; i<ctx->nb_trigger;i++){
		ctx->trigger_context[i].component_ctx = ctx;
		ctx->trigger_context[i].mem_pool = ctx->mem_pool;
		ctx->trigger_context[i].state = IDLE;

		ctx->trigger_context[i].msg_buffer_size = LDP_HEADER_TCP_SIZE;
		ctx->trigger_context[i].msg_buffer = calloc(ctx->trigger_context[i].msg_buffer_size, sizeof(char));

		ldp_fifo_manager_create(ctx->trigger_context[i].fifo_manager, ctx->mem_pool);
		ret=apr_threadattr_create(&trigger_attr[i],ctx->mem_pool);
		assert(ret==APR_SUCCESS);

	}

	// fill module dynamic trigger ctx
	for(int i=0; i<ctx->nb_dyn_trigger;i++){
		ctx->dyn_trigger_context[i].component_ctx = ctx;
		ctx->dyn_trigger_context[i].mem_pool = ctx->mem_pool;
		ctx->dyn_trigger_context[i].state = IDLE;

		ctx->dyn_trigger_context[i].msg_buffer_size = ctx->dyn_trigger_context[i].params_size + LDP_HEADER_TCP_SIZE;
		ctx->dyn_trigger_context[i].msg_buffer = calloc(ctx->dyn_trigger_context[i].msg_buffer_size, sizeof(char));

		ldp_fifo_manager_create(ctx->dyn_trigger_context[i].fifo_manager, ctx->mem_pool);
		ret=apr_threadattr_create(&dyn_trigger_attr[i],ctx->mem_pool);
		assert(ret==APR_SUCCESS);
	}

	// Fill module threads ctx
	for(int i=0; i<ctx->nb_module;i++){
		ctx->worker_context[i].component_ctx = ctx;
		ctx->worker_context[i].mem_pool = ctx->mem_pool;
		ctx->worker_context[i].state = IDLE;

		ctx->worker_context[i].msg_buffer = calloc(ctx->worker_context[i].msg_buffer_size, sizeof(char));

		apr_thread_mutex_create(&ctx->worker_context[i].wait_response, APR_THREAD_MUTEX_UNNESTED,ctx->mem_pool);
		apr_thread_cond_create( &ctx->worker_context[i].condition_response, ctx->mem_pool);

		ldp_fifo_manager_create(ctx->worker_context[i].fifo_manager, ctx->mem_pool);
		ret=apr_threadattr_create(&mod_attr[i],ctx->mem_pool);
		assert(ret==APR_SUCCESS);
	}

	UNUSED(ret);
}

static int comp_check_module_state(ldp_PDomain_ctx* ctx, ldp_module_context* mod_ctx){
	if(mod_ctx->state != RUNNING){
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF,"[%s] %s : not in RUNNING state. Erase msg", ctx->name, mod_ctx->name);
		return -1;
	}
	return 0;
}


void ldp_comp_received_event (ldp_PDomain_ctx* ctx,
								bool copy_msg,
								char* read_msg,
								int msg_size,
								ldp_module_context* mod_ctx,
								int op_link_index,
								bool activating_op,
								uint32_t op_id){
    UNUSED(copy_msg);

	if(mod_ctx->state != RUNNING){
		// TODO : erase message if it is not a life cycle message
		if(op_id != LDP_ID_INITIALIZE_life
			&& op_id != LDP_ID_START_life
			&& op_id != LDP_ID_STOP_life
			&& op_id != LDP_ID_SHUTDOWN_life){
			ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF,"[%s] %s : not in RUNNING state. Erase event msg", ctx->name, mod_ctx->name);

			return;
		}
	}

	if (ldp_fifo_manager_push(mod_ctx->fifo_manager,
							  op_link_index,
							  op_id,
							  EVENT,
							  activating_op,
							  msg_size,
							  read_msg,
                                                          mod_ctx->mod_id) != 0){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,"[%s] %s : fifo full. Erase event msg on link %i", ctx->name, mod_ctx->name, op_link_index);
        ldp_send_fault_error_to_father(ctx, mod_ctx->mod_id, ECOA__asset_type_COMPONENT, ECOA__error_type_OVERFLOW, 1);
	}
}


void ldp_comp_received_request (ldp_PDomain_ctx* ctx,
									char* parameters,
									uint32_t parameter_size,
									ldp_module_context* mod_ctx,
									ldp_interface_ctx* socket_sender,
									uint32_t ELI_sequence_num,
									uint32_t response_op_id,
									int op_link_index,
									bool activating_op,
									uint32_t op_id){

	if(comp_check_module_state(ctx, mod_ctx) != 0){
		return;
	}
	ECOA__uint32 ID=-1;
	ECOA__uint32 req_ID=-1;
	ldp_req_connection_type connect_type;
	if(socket_sender->type == LDP_ELI_MCAST){
		connect_type = LDP_REQUEST_EXTERNAL;
	}else{
		connect_type = LDP_REQUEST_LOCAL_SOCKET;
	}


	memcpy(&req_ID, &parameters[0], sizeof(ECOA__uint32));
	int ret=ldp_add_req_received(&mod_ctx->req_resp, &ID, connect_type, ELI_sequence_num, socket_sender,response_op_id, req_ID, false);
    if (ret != 0) {
        ldp_send_fault_error_to_father(ctx, mod_ctx->mod_id, ECOA__asset_type_COMPONENT,
                                         ECOA__error_type_UNAVAILABLE, 1);
    }
	assert(ret == 0);

	// write local RR ID (received RR ID has been saved in a received_request structure):
	memcpy(&parameters[0],&ID ,sizeof(ECOA__uint32));

	if(ldp_fifo_manager_push(mod_ctx->fifo_manager,
							 op_link_index,
							 op_id,
							 RR_RECEIVED,
							 activating_op,
							 parameter_size, /* size = parameters + request ID */
							 parameters,
                                                         mod_ctx->mod_id) != 0){ /* push without ELI_sequence_num*/
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s] %s : fifo full. Erase received request", ctx->name, mod_ctx->name);
        ldp_send_fault_error_to_father(ctx, mod_ctx->mod_id, ECOA__asset_type_COMPONENT, ECOA__error_type_OVERFLOW, 2);
		// free structures
		// comp_free_buffer(ctx, buffer);
		ldp_node * req_to_remove;
		ldp_find_req_received(&mod_ctx->req_resp, ID, &req_to_remove);
		ldp_free_req_received(&mod_ctx->req_resp,req_to_remove);
	}

	UNUSED(ret);
}


void ldp_comp_received_answer_request(ldp_PDomain_ctx* ctx,
										char* parameters,
										uint32_t parameter_size,
										uint32_t client_mod_ID,
										uint32_t op_id){

	// find client module context
	ldp_module_context* module_ctx = find_module_context(ctx, client_mod_ID);
	if(module_ctx==NULL){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF, "ERROR", ctx->logger_PF,
		 "[%s]: request req_sequence_num does not match with a module ID (%i)", ctx->name, client_mod_ID);
		return;
	}

	if( comp_check_module_state(ctx, module_ctx) != 0){
		return;
	}

	ldp_node* node;
	ECOA__uint32 req_id;
	memcpy(&req_id, parameters, sizeof(ECOA__uint32));
	ldp_req_sent* req=ldp_find_req_sent(&module_ctx->req_resp,req_id, &node);
	// TODO do someyhong if req = NULL : if request ID does not exist
	if (req == NULL){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF, "ERROR", module_ctx->logger_PF, "[%s] %s : request ID does not exist", ctx->name, module_ctx->name);
		return;
	}

	// discard request answer if out of date
	if(ldp_is_request_timeout(&req->timeout) == 1){
		ldp_log_PF_log_var(ECOA_LOG_WARN_PF, "WARN", module_ctx->logger_PF, "[%s] %s Request answer out of date : discard by component", ctx->name, module_ctx->name);
		ldp_free_req_sent(&module_ctx->req_resp,node);
		return;
	}

	if( !req->is_synchrone){
		// asynchrone
		if(ldp_fifo_manager_push(module_ctx->fifo_manager,
							   req->resp_op_index,
							   op_id,
							   RR_RECEIVED,
							   req->resp_op_activating,
							   parameter_size,
							   parameters,
                                                           module_ctx->mod_id) != 0){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s] %s : fifo full. Erase received request answer", ctx->name, module_ctx->name);
            ldp_send_fault_error_to_father(ctx, module_ctx->mod_id, ECOA__asset_type_COMPONENT, ECOA__error_type_OVERFLOW, 3);
			ldp_free_req_sent(&module_ctx->req_resp,node);
		}
	}else{
		if(ldp_fifo_manager_push_first(module_ctx->fifo_manager,
									 req->resp_op_index,
									 op_id,
									 RR_RECEIVED,
									 req->resp_op_activating,
									 parameter_size,
									 parameters,
                                                                         module_ctx->mod_id) != 0){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s] %s : fifo full. Erase received request answer", ctx->name, module_ctx->name);
            ldp_send_fault_error_to_father(ctx, module_ctx->mod_id, ECOA__asset_type_COMPONENT, ECOA__error_type_OVERFLOW, 4);
		}
	// unblock module
	apr_thread_mutex_lock(module_ctx->wait_response);
		apr_thread_cond_signal(module_ctx->condition_response);
		apr_thread_mutex_unlock(module_ctx->wait_response);

		ldp_free_req_sent(&module_ctx->req_resp,node);
	}

}


void ldp_comp_notify_mod_VD(ldp_PDomain_ctx* PD_ctx, ldp_module_context* mod_ctx, int op_link_index, bool activating_op, uint32_t op_id){

	if(comp_check_module_state(PD_ctx, mod_ctx) != 0){
		return;
	}

	if (ldp_fifo_manager_push(mod_ctx->fifo_manager,
							  op_link_index,
							  op_id,
							  VERSIONED_DATA,
							  activating_op,
							  0, /* no parameter in VD notification*/
							  NULL,
                                                          mod_ctx->mod_id) != 0){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", PD_ctx->logger_PF,
			"comp %s, mod %s : fifo full. Impossible to send notify msg", PD_ctx->name, mod_ctx->name);
        ldp_send_fault_error_to_father(PD_ctx, mod_ctx->mod_id, ECOA__asset_type_COMPONENT, ECOA__error_type_OVERFLOW, 5);
	}

}


void ldp_destroy_module(ldp_module_context* ctx){
	ldp_fifo_manager_destroy(ctx->fifo_manager);
	free(ctx->fifo_manager);
	free(ctx->network_write_data);

	for(int j = 0; j < ctx->operation_num; j++){
		free(ctx->operation_map[j].module_operations);
		free(ctx->operation_map[j].local_socket_operations);
		free(ctx->operation_map[j].external_socket_operations);
	}
	free(ctx->operation_map);
	free(ctx->msg_buffer);
}
void ldp_destroy_component(ldp_PDomain_ctx* ctx){
	ldp_log_PF_log_var(ECOA_LOG_TRACE_PF,"TRACE", ctx->logger_PF, "comp %s: will be destroyed", ctx->name);

	// module contexts
	for (int i=0; i<ctx->nb_module; i++){
		ldp_destroy_module(&ctx->worker_context[i]);
		free(ctx->worker_context[i].logger);
		ldp_request_response_destroy(&ctx->worker_context[i].req_resp);
		free(ctx->worker_context[i].properties);

		for(int j=0; j<ctx->worker_context[i].num_reader_mng ;j++){
			ldp_destroy_reader_mng(&ctx->worker_context[i].VD_reader_managers[j]);
		}
		free(ctx->worker_context[i].VD_reader_managers);
		for(int j=0; j<ctx->worker_context[i].num_writter_mng ;j++){
			ldp_destroy_writter_mng(&ctx->worker_context[i].VD_writter_managers[j]);
		}
		free(ctx->worker_context[i].VD_writter_managers);
	}
	free(ctx->worker_context);

	// trigger contests
	for (int i=0; i<ctx->nb_trigger; i++){
		ldp_destroy_module((ldp_module_context*) &ctx->trigger_context[i]);
		for(int j=0; j< ctx->trigger_context[i].nb_trigger_event; j++){
			free(ctx->trigger_context[i].trigger_events[j].operation_indexes);
		}
		free(ctx->trigger_context[i].trigger_events);
	}
	if(ctx->nb_trigger > 0){
		free(ctx->trigger_context);
	}

	// dynamic triggers contexts
	for (int i=0; i<ctx->nb_dyn_trigger; i++){
		ldp_destroy_module((ldp_module_context*) &ctx->dyn_trigger_context[i]);
	}
	if(ctx->nb_dyn_trigger > 0){
		free(ctx->dyn_trigger_context);
	}

	// buffer pool
	free(ctx->msg_buffer);

	apr_thread_mutex_destroy (ctx->state_mutex);
	apr_thread_mutex_destroy (ctx->external_mutex);

	// ports info array
	free(ctx->interface_ctx_array);

	for(int i=0; i<ctx->mcast_read_interface_num; i++){
		for (int j=0; j< ctx->mcast_read_interface[i].inter.mcast.link_num; j++){
			ldp_free_PF_link(&ctx->mcast_read_interface[i].inter.mcast.PF_links_ctx[j].link_ctx);
		}
	}

	// VD_manager_array
	for(int i=0; i<ctx->num_VD_repo; i++){
		ldp_destroy_repository(&ctx->VD_repo_array[i],ctx->mem_pool);
	}
	free(ctx->VD_repo_array);

	// logger
	ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARN", ctx->logger_PF, "comp %s: destroyed", ctx->name);
	ldp_log_deinitialize(ctx->logger);
	ldp_log_PF_deinitialize(ctx->logger_PF);
	free(ctx->logger);
	ctx->logger=NULL;
	free(ctx->logger_PF);
	ctx->logger_PF=NULL;
	free(ctx);
}

ldp_module_context* find_module_context(ldp_PDomain_ctx* ctx, uint16_t module_id){
	for(int i=0; i<ctx->nb_module; i++){
		if(ctx->worker_context[i].mod_id == module_id){
			return &ctx->worker_context[i];
		}
	}
	return NULL;
}

