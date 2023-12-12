/*
* @file ldp_udp_comp_server.c
* @brief ECOA component server (protected domain)
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>

#include <apr_poll.h>
#include <apr_errno.h>
#include <apr_time.h>

#include "ldp_structures.h"
#include "ldp_network.h"
#include "ldp_log_platform.h"
#include "ldp_udp.h"

#include "ldp_multicast.h"
#include "ldp_ELI.h"
#include "ldp_ELI_msg_management.h"
#include "ldp_ELI_udp.h"

#include "assert.h"
/**
 * @brief      send message to main process
 *
 * @param      ctx   The component context
 * @param      op_ID  ID message to send
 *
 * @return     ldp status
 */
static ldp_status_t sent_msg_to_father(ldp_PDomain_ctx* ctx, uint8_t op_ID){
	net_data_w data_w;
	data_w.module_id = 0x01;
	apr_status_t ret=ldp_IP_write(&ctx->interface_ctx_array[ctx->nb_client],(char*) &op_ID, sizeof(uint8_t), &data_w);
	if(ret != APR_SUCCESS){
		return ret;
	}
	return LDP_SUCCESS;
}


void ldp_start_comp_server(ldp_PDomain_ctx* ctx){
	apr_pool_t* mem_pool = ctx->mem_pool;
	apr_pollset_t *pollset;
	ldp_status_t retval;
	apr_pollset_create_ex(&pollset, ctx->nb_client+ctx->nb_server + ctx->mcast_read_interface_num, mem_pool, 0,APR_POLLSET_EPOLL);
	ldp_interface_ctx* interface_ctx_array = ctx->interface_ctx_array;

	// set UDP interface structures:
	for (int i=0; i<ctx->nb_client; i++){
		if (interface_ctx_array[i].type == LDP_ELI_MCAST){
			// nothing to do: not possible
		}else{
			interface_ctx_array[i].inter.local.info_r = &interface_ctx_array[i].info_r;
			interface_ctx_array[i].inter.local.info_w = malloc(sizeof(ldp_tcp_info));
			memcpy(interface_ctx_array[i].inter.local.info_w, interface_ctx_array[i].inter.local.info_r, sizeof(ldp_tcp_info));
			interface_ctx_array[i].inter.local.info_w->port +=5000;
		}
	}

	for (int i=0; i<ctx->nb_server; i++){
		if (interface_ctx_array[ctx->nb_client+i].type == LDP_ELI_MCAST){
			// nothing to do:
		}else{
			interface_ctx_array[ctx->nb_client+i].inter.local.info_w = &interface_ctx_array[ctx->nb_client+i].info_r;
			interface_ctx_array[ctx->nb_client+i].inter.local.info_r = malloc(sizeof(ldp_tcp_info));
			memcpy(interface_ctx_array[ctx->nb_client+i].inter.local.info_r, interface_ctx_array[ctx->nb_client+i].inter.local.info_w, sizeof(ldp_tcp_info));
			interface_ctx_array[ctx->nb_client+i].inter.local.info_r->port +=5000;
		}
	}

	// set create interfaces (UDP or multicast):
	for (int i=0; i<ctx->nb_client+ctx->nb_server; i++){
		if (interface_ctx_array[i].type == LDP_ELI_MCAST){
			retval = ldp_create_sent_multicast_interface(&interface_ctx_array[i].inter.mcast,
														&interface_ctx_array[i].info_r,
														ctx->logger_PF, ctx->mem_pool);
			if( retval != LDP_SUCCESS){
				ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
								"Impossilbe to create sent multicast interface (%s:%i)",
									interface_ctx_array[i].info_r.addr,
									interface_ctx_array[i].info_r.port);
			}
		}else{
			retval = ldp_create_interface_udp(&interface_ctx_array[i].inter.local, ctx->msg_buffer_size + LDP_HEADER_TCP_SIZE, mem_pool);
			if (retval != LDP_SUCCESS){
				ldp_error_status_log(ctx->logger_PF, retval, "[%s] Can't create UDP interface %s:%i. ",
					ctx->name, interface_ctx_array[i].info_r.addr, interface_ctx_array[i].info_r.port);
			}

			ldp_add_pollset(pollset, &interface_ctx_array[i], interface_ctx_array[i].inter.local.read_sock_ctx->socket, ctx->mem_pool);
		}
	}

	// ELI multicast read sockets:
	for(int i=0; i<ctx->mcast_read_interface_num; i++){
		retval = ldp_create_read_multicast_interface(&ctx->mcast_read_interface[i].inter.mcast,
													&ctx->mcast_read_interface[i].info_r,
													ctx->logger_PF,
													ctx->mem_pool);
		if( retval == LDP_SUCCESS){
			ldp_add_pollset(pollset, &ctx->mcast_read_interface[i], ctx->mcast_read_interface[i].inter.mcast.socket, ctx->mem_pool);
		}else{
			ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
								"Impossilbe to create read multicast interface (%s:%i)",
								ctx->mcast_read_interface[i].info_r.addr, ctx->mcast_read_interface[i].info_r.port);
		}
	}

	ctx->state = PDomain_IDLE;
	retval = sent_msg_to_father(ctx, LDP_ID_CLIENT_INIT);
	if (retval != APR_SUCCESS){
		ldp_error_status_log(ctx->logger_PF, retval, "[%s] Cannot send CLIENT_INIT to father process. ", ctx->name);
	}else{
		ctx->state = PDomain_INIT;
	}



	const apr_pollfd_t *ret_pfd;
	bool server_is_running = true;
	apr_size_t len = 0;
	apr_int32_t num;

	int ELI_buffer_size = ctx->msg_buffer_size + LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE;
	char* ELI_read_buffer = malloc(ELI_buffer_size);
	while(server_is_running){
		retval=apr_pollset_poll(pollset, -1, &num, &ret_pfd);
		if (retval != LDP_SUCCESS && num <0){
			ldp_error_status_log(ctx->logger_PF, retval, "[%s] error in pollset %i. ", ctx->name, num);
		}

		for(int i=0; i<num;i++){
			ldp_interface_ctx* interface_ctx = ret_pfd[i].client_data;
			char* msg_buffer = NULL;
			if(interface_ctx->type == LDP_ELI_MCAST){
				// ELI message from a multicast socket
				ldp_ELI_UDP_PD_read_msg(ctx, interface_ctx, ELI_read_buffer, ELI_buffer_size);
			}else{
				assert(interface_ctx->type == LDP_LOCAL_IP);
				// local platform msg from an UDP socket
				ldp_IP_read(interface_ctx, NULL, &len);
				if(len > 0){
					// PUSH MSG
					ldp_udp_read_message* udp_msg = get_first_read_message(&interface_ctx->inter.local);

					if (udp_msg != NULL) {
						msg_buffer = udp_msg->read_msg;

						uint32_t op_ID ;
						uint32_t param_size;
						ldp_read_IP_header(ctx, msg_buffer, &op_ID,&param_size);
						len = 0;

						retval = domain_proc_consume_msg(ctx, msg_buffer, param_size, op_ID, interface_ctx);
						if (retval != LDP_SUCCESS){
							server_is_running = false;
							break;
						}
					}
				}
			}
		}
	}

	free(ELI_read_buffer);
    apr_pollset_destroy(pollset);

	// clean all socket properly
	for(int i=0; i<ctx->nb_client; i++){
		ldp_destroy_interface_udp(&interface_ctx_array[i].inter.local);
		free(interface_ctx_array[i].inter.local.info_w);
	}
	for(int i=0; i<ctx->nb_server; i++){
		ldp_destroy_interface_udp(&interface_ctx_array[ctx->nb_client+i].inter.local);
		free(interface_ctx_array[ctx->nb_client+i].inter.local.info_r);
	}
}
