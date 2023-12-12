/**
* @file ldp_network.c
* @brief ECOA ldp network function
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_network.h"
#include "ldp_log_platform.h"
#include <inttypes.h>
#include <assert.h>
#include <unistd.h> //for sleep
#include <apr_poll.h>
#include "ldp_ELI_msg_management.h"
#include "ldp_structures.h" //for UNUSED macro

void ldp_written_IP_header(char* buffer, uint32_t param_size, uint32_t op_ID){
	buffer[0]=0xE;
	buffer[1]=0xC;
	buffer[2]=0x0;
	buffer[3]=0xA;

	memcpy(&buffer[4], &param_size, sizeof(uint32_t));
	memcpy(&buffer[8], &op_ID, LDP_OP_ID_SIZE);
}

void ldp_written_IP_op_ID(char* buffer, uint32_t op_ID){
	memcpy(&buffer[8], &op_ID, LDP_OP_ID_SIZE);
}

void ldp_written_IP_fault_error(char* buffer, 
                                  ECOA__asset_id asset_id,
                                  ECOA__asset_type asset_type,
                                  ECOA__error_type error_type,
                                  ECOA__uint32 error_code){
    ECOA__uint32 l_offset = 0;
    buffer[l_offset] = LDP_ID_CLIENT_FAULT_ERROR;
    l_offset += sizeof(uint8_t);
	memcpy(&buffer[l_offset], &asset_id, sizeof(ECOA__asset_id));
	l_offset += sizeof(ECOA__asset_id);
	memcpy(&buffer[l_offset], &asset_type, sizeof(ECOA__asset_type));
	l_offset += sizeof(ECOA__asset_type);
	memcpy(&buffer[l_offset], &error_type, sizeof(ECOA__error_type));
	l_offset += sizeof(ECOA__error_type);
	memcpy(&buffer[l_offset], &error_code, sizeof(ECOA__uint32));
	l_offset += sizeof(ECOA__uint32);
}

void ldp_read_IP_fault_error(char* buffer, 
                               ECOA__asset_id* asset_id,
                               ECOA__asset_type* asset_type,
                               ECOA__error_type* error_type,
                               ECOA__uint32* error_code){
	ECOA__uint32 l_offset = 0;
	*asset_id   = *((ECOA__asset_id*) &(buffer[l_offset]));
	l_offset += sizeof(ECOA__asset_id);
	*asset_type = *((ECOA__asset_type*) &(buffer[l_offset]));
	l_offset += sizeof(ECOA__asset_type);
	*error_type = *((ECOA__error_type*) &(buffer[l_offset]));
	l_offset += sizeof(ECOA__error_type);
	*error_code = *((ECOA__uint32*) &(buffer[l_offset]));
}

bool ldp_read_IP_header(ldp_PDomain_ctx* ctx, char* buffer, uint32_t* op_ID, uint32_t* param_size){
	// check begining
	if (buffer[0] == 0xE &&
		buffer[1] == 0xC &&
		buffer[2] == 0x0 &&
		buffer[3] == 0xA){

		// read parameters size and operation ID
		memcpy(param_size, &buffer[4], sizeof(uint32_t));
		memcpy(op_ID, &buffer[8], LDP_OP_ID_SIZE);

		// TODO : done, READ PARAMS

		// check param_size
		if (*param_size <= ctx->msg_buffer_size){
			return true;
		}else{
			ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
								 "invalid parameters size %"PRIu32" (max = %"PRIu32")", *param_size, ctx->msg_buffer_size);
		}

	}
	ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
						 "invalid header %02X:%02X:%02X:%02X params_size: %"PRIu32" op_ID: %"PRIu16"",
						 buffer[0], buffer[1], buffer[2], buffer[3], *param_size, *op_ID);
	return false;
}


void ldp_IP_print_err(apr_status_t err, ldp_logger_platform* logger_PF, ldp_tcp_info* ip_info){
	char buf[128];
	apr_strerror(err,buf,128);
	ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", logger_PF, "tcp error (%s:%i) : %s", ip_info->addr, ip_info->port, buf);
}

void ldp_fault_error_notification(ldp_Main_ctx* ctx,
                                    ECOA__asset_id asset_id,
                                    ECOA__asset_type asset_type,
                                    ECOA__error_type error_type,
                                    ECOA__uint32 error_code){
    ECOA__global_time l_timestamp  = {0,0};
    ldp_get_ecoa_utc_time((ldp__timestamp*)&l_timestamp);
    ctx->fault_handler_function_ptr(ctx->fault_handler_context,
                                    ctx->fault_handler_error_id++,
                                    l_timestamp,
                                    asset_id,
                                    asset_type,
                                    error_type,
                                    error_code);
}

ldp_status_t ldp_send_fault_error_to_father(ldp_PDomain_ctx* ctx,
                                                ECOA__asset_id asset_id,
                                                ECOA__asset_type asset_type,
                                                ECOA__error_type error_type,
                                                ECOA__uint32 error_code){
	net_data_w data_w;
#if USE_UDP_PROTO
	data_w.module_id = 0x01;
#endif
    char msg[LDP_FAULT_ERROR_MSG_SIZE];
    ldp_written_IP_fault_error(msg, asset_id, asset_type, error_type, error_code);
	apr_status_t ret=ldp_IP_write(&ctx->interface_ctx_array[ctx->nb_client], msg, LDP_FAULT_ERROR_MSG_SIZE, &data_w);
	if(ret != APR_SUCCESS){
		return ret;
	}
	return LDP_SUCCESS;
}

ldp_status_t write_msg(ldp_logger_platform* logger_PF,
									ldp_interface_ctx* interface_ctx,
									uint32_t msg_ID)
{
	char msg[LDP_HEADER_TCP_SIZE];
	ldp_written_IP_header(msg, 0, msg_ID);

	net_data_w data_w;
#if USE_UDP_PROTO
	data_w.module_id = 0x01;
#endif
	ldp_status_t ret=ldp_IP_write(interface_ctx,(char*) &msg, LDP_HEADER_TCP_SIZE, &data_w);
	if(ret != LDP_SUCCESS){
		ldp_error_status_log(logger_PF, ret, "[MAIN] cannot send message to client (%s:%i). msg = %i. ",
			interface_ctx->info_r.addr, interface_ctx->info_r.port, msg_ID);
	}
	return ret;
}


static ldp_status_t broadcast_to_client(ldp_logger_platform* logger_PF,
										ldp_interface_ctx* interface_ctx_array,
										int client_num,
										uint16_t msg_ID)
{
	ldp_status_t ret= LDP_SUCCESS;
	for(int i=0;i<client_num;i++){
		if(write_msg(logger_PF, &interface_ctx_array[i],msg_ID) != LDP_SUCCESS){
			ret = LDP_ERROR;
		}
	}
	return ret;
}

ldp_status_t main_proc_consume_msg(ldp_Main_ctx* ctx,
							char* buf,
                            const apr_pollfd_t* fd,
							ldp_interface_ctx* read_interface_ctx,
							ldp_interface_ctx* interface_ctx_array){

	assert(read_interface_ctx->type == LDP_LOCAL_IP);
	switch((uint8_t) buf[0]){
		case LDP_ID_KILL :
			ldp_log_PF_log(ECOA_LOG_INFO_PF, "INFO",
							 ctx->logger_PF, "*************** Send shutdown to children");
			broadcast_to_client(ctx->logger_PF, interface_ctx_array, ctx->PD_number, LDP_ID_KILL);
			return LDP_ERROR;

		case LDP_ID_CLIENT_INIT:
			ctx->nb_init_clients++;
			ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF, "[MAIN] received client_init: %i",ctx->nb_init_clients);

			if(ctx->nb_init_clients == ctx->PD_number){

				FILE *userlaunch_stream_check;

				ldp_log_PF_log(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF, "************** all components are connected");

				if(( userlaunch_stream_check = fopen (ctx->superv_tools->path_to_launcher_t,"r")) != NULL){ // there is a launchig file
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF, "***Launch following launcher.txt");
					fclose(userlaunch_stream_check);
					launching_thread_params the_params = {ctx->logger_PF,
															interface_ctx_array,
															ctx->PD_number,
															ctx->superv_tools->path_to_launcher_t,
															ctx->superv_tools->ldp_id_identifier,
															&ctx->superv_tools->launch_thread_ptr,
                                                            "launching_thread"};
					ldp_create_launching_thread(ctx->mem_pool, &the_params);

				}
				else{ // launch it automatically
					ldp_log_PF_log(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF, "***Automatic Launch");
					broadcast_to_client(ctx->logger_PF, interface_ctx_array, ctx->PD_number, LDP_ID_INIT_MOD);
				}

			}else if(ctx->nb_init_clients> ctx->PD_number){
				// restart lost client
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF,
									 "************** send init module on port %i", read_interface_ctx->info_r.port );
				write_msg(ctx->logger_PF, read_interface_ctx, LDP_ID_INIT_MOD);
			}
			break;

		case LDP_ID_CLIENT_READY:
			ctx->nb_ready_clients++;
			ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF,
								 "[MAIN] received client_ready: %i",ctx->nb_ready_clients);

			FILE *userlaunch_stream_check2;

			if ((userlaunch_stream_check2 = fopen (ctx->superv_tools->path_to_launcher_t,"r")) != NULL) {
                fclose(userlaunch_stream_check2);
                if(ctx->nb_ready_clients> ctx->PD_number){
                    // restart lost client
                    ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF,
                                         "************** send start module on port %i", read_interface_ctx->info_r.port );
                    write_msg(ctx->logger_PF, read_interface_ctx, LDP_ID_START_MOD);
                }
                break;
			} // if there is a launching file, there is no automatic
			if(ctx->nb_ready_clients == ctx->PD_number){
				// when all components are READY (only the first time)
				ldp_log_PF_log(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF, "************** everybody is ready");
				broadcast_to_client(ctx->logger_PF, interface_ctx_array, ctx->PD_number, LDP_ID_START_MOD);

				// initialized ELI starting sequence
				ldp_ELI_status ret = ldp_ELI_UDP_startup_sequence(ctx);

				if( ret != ELI_STATUS__OK){
						ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
										"[MAIN] Error during initialization of ELI startup sequence");
				}
			}else if(ctx->nb_ready_clients> ctx->PD_number){
				// restart lost client
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF,
									 "************** send start module on port %i", read_interface_ctx->info_r.port );
				write_msg(ctx->logger_PF, read_interface_ctx, LDP_ID_START_MOD);
			}
			break;
		case LDP_ID_CLIENT_FAULT_ERROR:
			{
				ECOA__asset_id    l_asset_id   = 0;
				ECOA__asset_type  l_asset_type = 0;
				ECOA__error_type  l_error_type = 0;
				ECOA__uint32      l_error_code = 0;
				char l_buffer[128];
				apr_size_t l_length = LDP_FAULT_ERROR_MSG_SIZE-1;
				ldp_status_t ret = ldp_IP_read(fd->client_data, l_buffer, &l_length);
                                UNUSED(ret);
				ldp_read_IP_fault_error(l_buffer, &l_asset_id, &l_asset_type, &l_error_type, &l_error_code);
                ldp_fault_error_notification(ctx, l_asset_id, l_asset_type, l_error_type, l_error_code);
			}
			break;
		default:
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF, "ERROR", ctx->logger_PF, "[MAIN] ERROR wrong msg \"%i\"", (uint8_t) buf[0]);

			return LDP_ERROR;
	}
	return LDP_SUCCESS;
}

ldp_status_t domain_proc_consume_msg(ldp_PDomain_ctx* ctx,
							char* read_buffer,
							uint32_t param_size,
							uint32_t op_ID,
							ldp_interface_ctx* interface_ctx){
	ldp_status_t retval = LDP_SUCCESS;
	switch(op_ID){
		case LDP_ID_INIT_MOD:
			if(ctx->state != PDomain_INIT){
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
									 "[%s]LDP_ID_INIT_MOD received but component is not in INIT state",ctx->name);
			}else{
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
									 "[%s]LDP_ID_INIT_MOD received",ctx->name);
				// INIT modules, triggers and dynamic triggers
				comp_server_broadcast(ctx, LDP_ID_INITIALIZE_life);
			}
			break;

		case LDP_ID_START_MOD:
			if(ctx->state != PDomain_READY){
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
									 "[%s]LDP_ID_START_MOD received but component is not in READY state",ctx->name);
			}else{
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]LDP_ID_START_MOD received",ctx->name);
				// START modules, triggers and dynamic triggers
				comp_server_broadcast(ctx, LDP_ID_START_life);
			}
			ctx->state = PDomain_RUNNING;
			break;

		case LDP_ID_KILL:
			// KILL all thread
			ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]KILL received",ctx->name);
			comp_server_broadcast(ctx, LDP_ID_KILL_life);
			ctx->state = PDomain_IDLE;

			// stop server loop
			retval = LDP_ERROR;
			break;

		case LDP_ID_SHUTDOWN:
			// SHUTDOWN all thread
			ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s]SHUTDOWN received",ctx->name);
			comp_server_broadcast(ctx, LDP_ID_SHUTDOWN_life);
			ctx->state = PDomain_INIT;
			break;

		case LDP_ID_SYNC:
			{
			// extract the ID of module destination and the ID of operation
			uint32_t ID_mod = (uint32_t)read_buffer[LDP_HEADER_TCP_SIZE];
			uint32_t operation_ID = (uint32_t)read_buffer[LDP_HEADER_TCP_SIZE+2];

			//find the module or trigger to which this operation should be applied, actually get its context
			find_dest_mod_and_send(ctx, ID_mod, operation_ID);

			break;
			}

		default:
			// message to route to modules
			(ctx->route_function_ptr)(ctx, op_ID, &read_buffer[LDP_HEADER_TCP_SIZE],
										param_size, interface_ctx, interface_ctx->info_r.port, 0, 0);
			break;
	}
	return retval;
}


/**
 * @brief      push a message for module life cycle in a module's fifo
 *
 * @param      comp_ctx  The component context
 * @param[in]  op_ID     The operation id (life cycle operation)
 * @param      mod_fifo_m  The module fifo
 * @param      mod_name  The module name
 * @param      mod_ID    The module ID
 *
 * @return     LDP_ERROR in case of error or LDP_SUCCESS
 */
ldp_status_t comp_server_push_fifo(ldp_PDomain_ctx* comp_ctx,int op_ID, ldp_fifo_manager* mod_fifo_m, char* mod_name, ECOA__uint16 mod_ID){

	ldp_status_t ret = ldp_fifo_manager_push(mod_fifo_m,
												0, /* pool index for lifecycle operation*/
												op_ID, EVENT,
												true, /* activating op*/
												0, /* no parameter */
												NULL, /* no parameter */
                                                mod_ID /* ID of the module*/);
	if (ret!= 0){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", comp_ctx->logger_PF,
							 "[%s] %s : fifo full. Enable to init server", comp_ctx->name, mod_name);
	return LDP_ERROR;
	}

	return LDP_SUCCESS;
}

/**
 * @brief      Broadcast a life cycle message to all modules of a component (module, trigger, dynamic trigger)
 *
 * @param      comp_ctx  The component context
 * @param[in]  msg_ID    The message id (life cycle operation)
 */
void comp_server_broadcast(ldp_PDomain_ctx* comp_ctx, uint32_t msg_ID){
	for(int i=0; i<comp_ctx->nb_trigger;i++){
		comp_server_push_fifo(comp_ctx, msg_ID,
							  comp_ctx->trigger_context[i].fifo_manager, comp_ctx->trigger_context[i].name, comp_ctx->trigger_context[i].mod_id);
	}
	for(int i=0; i<comp_ctx->nb_dyn_trigger;i++){
		comp_server_push_fifo(comp_ctx, msg_ID, comp_ctx->dyn_trigger_context[i].fifo_manager,comp_ctx->dyn_trigger_context[i].name, comp_ctx->dyn_trigger_context[i].mod_id);
	}

    if (msg_ID == LDP_ID_START_life) {
        bool l_triggers_all_started = true;
        uint32_t l_nb_try = 5;
        while(l_nb_try){
            l_triggers_all_started = true;
	        for(int i=0; i<comp_ctx->nb_trigger;i++){
                if (comp_ctx->trigger_context[i].state != RUNNING) {
                  l_triggers_all_started = false;
                }
	        }
	        for(int i=0; i<comp_ctx->nb_dyn_trigger;i++){
                if (comp_ctx->dyn_trigger_context[i].state != RUNNING) {
                  l_triggers_all_started = false;
                }
	        }
            if (true == l_triggers_all_started) {
		        for(int i=0; i<comp_ctx->nb_module;i++){
			        comp_server_push_fifo(comp_ctx, msg_ID, comp_ctx->worker_context[i].fifo_manager, comp_ctx->worker_context[i].name, comp_ctx->worker_context[i].mod_id);
		        }
                break;
            }
            l_nb_try--;
            ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", comp_ctx->logger_PF,
		    					 "[%s] : waiting for Triggers to start remaining try %d", comp_ctx->name, l_nb_try);
            sleep(1);
        }
    }else{
	    for(int i=0; i<comp_ctx->nb_module;i++){
		    comp_server_push_fifo(comp_ctx, msg_ID, comp_ctx->worker_context[i].fifo_manager, comp_ctx->worker_context[i].name, comp_ctx->worker_context[i].mod_id);
	    }
    }
}

void find_dest_mod_and_send(ldp_PDomain_ctx* ctx, uint16_t ID_mod, uint32_t operation_ID){
	// loop in modules
	for (int i=0; i<ctx->nb_module; i++){
		if ((ctx->worker_context[i]).mod_id == ID_mod){
			comp_server_push_fifo(ctx, operation_ID, (ctx->worker_context[i]).fifo_manager, (ctx->worker_context[i]).name, (ctx->worker_context[i]).mod_id);
			return;
		}
	}
	// loop in triggers
	for (int i=0; i<ctx->nb_trigger; i++){
		if ((ctx->trigger_context[i]).mod_id == ID_mod){
			comp_server_push_fifo(ctx, operation_ID,
								  (ctx->trigger_context[i]).fifo_manager, (ctx->trigger_context[i]).name, (ctx->trigger_context[i]).mod_id);
			return;
		}
	}
	// loop in dynamic triggers
	for (int i=0; i<ctx->nb_dyn_trigger; i++){
		if ((ctx->dyn_trigger_context[i]).mod_id == ID_mod){
			comp_server_push_fifo(ctx, operation_ID,
								  (ctx->dyn_trigger_context[i]).fifo_manager, (ctx->dyn_trigger_context[i]).name, (ctx->dyn_trigger_context[i]).mod_id);
			return;
		}
	}
}

void find_dest_mod_by_comp_and_send(ldp_PDomain_ctx* ctx, char* component_name, uint32_t operation_ID){
	// loop in modules
	for (int i=0; i<ctx->nb_module; i++){
		if (strcmp((ctx->worker_context[i]).component_name, component_name) == 0){
			comp_server_push_fifo(ctx, operation_ID, (ctx->worker_context[i]).fifo_manager, (ctx->worker_context[i]).name, (ctx->worker_context[i]).mod_id);
		}
	}
	// loop in triggers
	for (int i=0; i<ctx->nb_trigger; i++){
		if (strcmp((ctx->trigger_context[i]).component_name, component_name) == 0){
			comp_server_push_fifo(ctx, operation_ID,
								  (ctx->trigger_context[i]).fifo_manager, (ctx->trigger_context[i]).name, (ctx->trigger_context[i]).mod_id);
		}
	}
	// loop in dynamic triggers
	for (int i=0; i<ctx->nb_dyn_trigger; i++){
		if (strcmp((ctx->dyn_trigger_context[i]).component_name, component_name) == 0){
			comp_server_push_fifo(ctx, operation_ID,
								  (ctx->dyn_trigger_context[i]).fifo_manager, (ctx->dyn_trigger_context[i]).name, (ctx->dyn_trigger_context[i]).mod_id);
		}
	}
}

void ldp_add_pollset(apr_pollset_t *pollset,
					   ldp_interface_ctx* sock_interface,
					   apr_socket_t* read_socket,
					   apr_pool_t* mem_pool){
	apr_pollfd_t new_fd = { mem_pool, APR_POLL_SOCKET, APR_POLLIN | APR_POLLERR | APR_POLLHUP , 0,
						   { NULL }, sock_interface};
	new_fd.desc.s = read_socket;
// OD BEGIN
//	assert(apr_pollset_add(pollset, &new_fd) == APR_SUCCESS);
	apr_pollset_add(pollset, &new_fd);
// OD END
}
