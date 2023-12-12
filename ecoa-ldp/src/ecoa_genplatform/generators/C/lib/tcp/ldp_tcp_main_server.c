/**
* @file ldp_tcp_main_server.c
* @brief ECOA platform server
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include <assert.h>

#include <apr.h>
#include <apr_poll.h>
#include <apr_errno.h>
#include <apr_thread_cond.h>

#include "ldp_thread.h"
#include "ldp_structures.h"
#include "ldp_network.h"
#include "ldp_log_platform.h"
#include "ldp_status_error.h"
#include "ldp_tcp.h"
#include <unistd.h>
#include "ldp_ELI.h"
#include "ldp_ELI_msg_management.h"


/**
 * @brief      read the buffer from socket in the file descriptor and process the buffer.
 *
 * @param      ctx                  The Main process context
 * @param      pollset              The pollset
 * @param[in]  fd                   File descriptor
 * @param      read_inter_ctx       Context of the read interface
 * @param      interface_ctx_array  Array of interface context
 *
 * @return     apr_status_t
 */
static ldp_status_t read_and_parse_buffer(ldp_Main_ctx* ctx,
											apr_pollset_t *pollset,
											const apr_pollfd_t* fd,
											ldp_interface_ctx* read_inter_ctx,
											ldp_interface_ctx* interface_ctx_array)
{
	char buf[128];
	apr_size_t len=1;
	ldp_status_t ret=LDP_SUCCESS;

	if (read_inter_ctx->type == LDP_LOCAL_IP){
		ret = ldp_IP_read(fd->client_data, buf, &len);
		if(ret == APR_EOF){
			ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[MAIN] Socket closed %i? Allow reconnection", read_inter_ctx->info_r.port);

			// accept new connection
			read_inter_ctx->inter.local.is_listening=true;
			int ret_assert=apr_pollset_remove (pollset, fd);
			assert(ret_assert == APR_SUCCESS);
			ret_assert=apr_socket_close( read_inter_ctx->inter.local.communication_sock);
			assert(ret_assert == APR_SUCCESS);UNUSED(ret_assert);
			read_inter_ctx->inter.local.communication_sock = NULL;
			ret = LDP_SUCCESS;
		}else{
			// process message
			ret = main_proc_consume_msg(ctx,
									buf,
									fd,
									read_inter_ctx,
									interface_ctx_array);
		}
	}else{
		ldp_ELI_UDP_main_read_msg(ctx, read_inter_ctx);
	}
	return ret;
}

void ldp_start_father_server(ldp_Main_ctx* ctx, ldp_interface_ctx* interface_ctx_array, uint32_t PF_links_num){
    UNUSED(PF_links_num);
	apr_pollset_t *pollset;
	apr_status_t ret;
	apr_pollset_create(&pollset, 2*ctx->PD_number + ctx->mcast_reader_interface_num, ctx->mem_pool, 0);

	for(int i=0;i<ctx->PD_number;i++){
		// create connection socket
		interface_ctx_array[i].type = LDP_LOCAL_IP;
		interface_ctx_array[i].inter.local.is_listening=true;
		interface_ctx_array[i].inter.local.is_server=true;
		ret = ldp_create_listen_sock(&interface_ctx_array[i].inter.local.connection_sock, ctx->mem_pool, interface_ctx_array[i].info_r);
		if (ret != LDP_SUCCESS){
			ldp_error_status_log(ctx->logger_PF, ret, "[MAIN] cannot create socket %i %s. ",
					interface_ctx_array[i].info_r.port, interface_ctx_array[i].info_r.addr );
            ldp_fault_error_notification(ctx,
                                           ctx->pd_processes_array[i].proc.pid,
                                           ECOA__asset_type_COMPONENT,
                                           ECOA__error_type_COMMUNICATION_ERROR,
                                           1);
		}

		interface_ctx_array[i].inter.local.communication_sock = NULL;

		// add new file descriptor
		ldp_add_pollset(pollset, &interface_ctx_array[i], interface_ctx_array[i].inter.local.connection_sock, ctx->mem_pool);
	}

	// ELI read sockets
	for (int i=0; i<ctx->mcast_reader_interface_num; i++){
		ret = ldp_create_read_multicast_interface(&ctx->mcast_reader_interface[i].inter.mcast,
													&ctx->mcast_reader_interface[i].info_r,
													ctx->logger_PF,
													ctx->mem_pool);
		if( ret == LDP_SUCCESS){
			ldp_add_pollset(pollset, &ctx->mcast_reader_interface[i], ctx->mcast_reader_interface[i].inter.mcast.socket, ctx->mem_pool);
		}else{
			ldp_error_status_log(ctx->logger_PF, ret, "[MAIN] Impossible to create read multicast interface (%s:%i)",
								ctx->mcast_reader_interface[i].info_r.addr, ctx->mcast_reader_interface[i].info_r.port);
		}
	}

	// ELI sender sockets
	for(int i=0; i<ctx->mcast_sender_interface_num; i++){
		ret = ldp_create_sent_multicast_interface(&ctx->mcast_sender_interface[i].inter.mcast,
													&ctx->mcast_sender_interface[i].info_r,
													ctx->logger_PF,
													ctx->mem_pool);
		if( ret != LDP_SUCCESS){
			ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
							"[MAIN] Impossible to create sent multicast interface (%s:%i)",
							ctx->mcast_sender_interface[i].info_r.addr, ctx->mcast_sender_interface[i].info_r.port);
		}
	}

	// start server
	bool is_running=true;
	apr_int32_t num;
	const apr_pollfd_t *ret_pfd;

	while(is_running){
		ret = apr_pollset_poll(pollset, 1000000, &num, &ret_pfd);
		if(ret != APR_SUCCESS && num <0){
			ldp_warning_status_log(ctx->logger_PF, ret, "[MAIN] ERROR IN POLL");
		}

		for(int i=0; i<num; i++){
			ldp_interface_ctx* interface_ctx = ret_pfd[i].client_data;

			if( interface_ctx->type == LDP_LOCAL_IP && interface_ctx->inter.local.is_listening){
				// accept connection
				ldp_log_PF_log_var(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF,"[MAIN] accept new connection %i", interface_ctx->info_r.port);
				ret=ldp_accept_connection(ctx->logger_PF,
								ctx->mem_pool,
								pollset,
								interface_ctx);
				if (ret != LDP_SUCCESS){
					ldp_error_status_log(ctx->logger_PF, ret, "[MAIN] cant accept connection on %s:%i. ",
					 interface_ctx->info_r.addr, interface_ctx->info_r.port);
				}
			}else{
				// new message
				if(read_and_parse_buffer(ctx,
											pollset,
											&ret_pfd[i],
											interface_ctx,
											interface_ctx_array) != LDP_SUCCESS){
					is_running=false;
					break;
				}
			}
		}
	}

	// Join thread of launcher if existing
	FILE *userlaunch_stream_check3;
	if(( userlaunch_stream_check3 = fopen (ctx->superv_tools->path_to_launcher_t,"r")) != NULL){ // there is a launchig file
			apr_status_t status;
			apr_thread_join(&status, ctx->superv_tools->launch_thread_ptr);
			fclose(userlaunch_stream_check3);
	}

	// clean sockets
	for(int i=0; i<ctx->PD_number; i++){
		if (interface_ctx_array[i].type == LDP_LOCAL_IP){
			if( interface_ctx_array[i].inter.local.connection_sock != NULL){
				apr_socket_close(interface_ctx_array[i].inter.local.connection_sock);
			}
			if( interface_ctx_array[i].inter.local.communication_sock != NULL){
				apr_socket_close(interface_ctx_array[i].inter.local.communication_sock);
			}
		}else{
			// TODO
		}
	}

	ret=apr_pollset_destroy(pollset);
	assert(ret == APR_SUCCESS);
}
