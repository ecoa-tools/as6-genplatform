/**
* @file ldp_udp_main_server.c
* @brief ECOA platform server
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include <assert.h>

#include <apr_poll.h>
#include <apr_errno.h>

#include "ldp_structures.h"
#include "ldp_network.h"
#include "ldp_log_platform.h"
#include "ldp_status_error.h"

#include "ldp_udp.h"
#include "ldp_ELI.h"
#include "ldp_ELI_msg_management.h"


// void ldp_start_father_server(ldp_Main_ctx* ctx, ldp_tcp_info* comp_tcp_info){
void ldp_start_father_server(ldp_Main_ctx* ctx, ldp_interface_ctx* interface_ctx_array, uint32_t PF_links_num){
	apr_pollset_t *pollset;
	apr_status_t ret;
	apr_pollset_create(&pollset, ctx->PD_number + ctx->mcast_reader_interface_num, ctx->mem_pool, 0);

	for (int i=0; i<ctx->PD_number; i++){
		interface_ctx_array[i].type = LDP_LOCAL_IP;
		interface_ctx_array[i].inter.local.info_r = &interface_ctx_array[i].info_r;
		interface_ctx_array[i].inter.local.info_w = malloc(sizeof(ldp_tcp_info));
		memcpy(interface_ctx_array[i].inter.local.info_w, interface_ctx_array[i].inter.local.info_r, sizeof(ldp_tcp_info));
		interface_ctx_array[i].inter.local.info_w->port +=5000;

// OD BEGIN
//		assert(ldp_create_interface_udp(&interface_ctx_array[i].inter.local, 128 + LDP_HEADER_TCP_SIZE, ctx->mem_pool) == APR_SUCCESS);
		ldp_create_interface_udp(&interface_ctx_array[i].inter.local, 128 + LDP_HEADER_TCP_SIZE, ctx->mem_pool);
// OD END

		ldp_add_pollset(pollset, &interface_ctx_array[i], interface_ctx_array[i].inter.local.read_sock_ctx->socket, ctx->mem_pool);
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

	bool is_running=true;
	apr_int32_t num;
	apr_size_t len=0;
	const apr_pollfd_t *ret_pfd;

	while(is_running){
		ret = apr_pollset_poll(pollset, 1000000, &num, &ret_pfd);
		if(ret != APR_SUCCESS && num <0){
			ldp_log_PF_log(ECOA_LOG_INFO_PF, "INFO", ctx->logger_PF, "[MAIN] ERROR IN POLL");
		}

		for(int i=0; i<num; i++){
			ldp_interface_ctx* interface_ctx = ret_pfd[i].client_data;

			char* msg_buffer = NULL;
			if (interface_ctx->type == LDP_LOCAL_IP){
				ldp_IP_read(interface_ctx, msg_buffer, &len);
				if(len > 0){

					ldp_udp_read_message* udp_msg=get_first_read_message(&interface_ctx->inter.local);

					if (udp_msg!=NULL) {
						if(main_proc_consume_msg(ctx,
										udp_msg->read_msg,
                                        &ret_pfd[i],
										interface_ctx,
										interface_ctx_array) != APR_SUCCESS){
							is_running = false;
						}
					}
				}
			}else{
				assert(interface_ctx->type == LDP_ELI_MCAST);
				ldp_ELI_UDP_main_read_msg(ctx, interface_ctx);
			}
		}
	}

	// clean sockets
	for(int i=0; i<ctx->PD_number; i++){
		ldp_destroy_interface_udp(&interface_ctx_array[i].inter.local);
		free(interface_ctx_array[i].inter.local.info_w);
	}
	// TODO: clean ELI socket

    ret=apr_pollset_destroy(pollset);
    assert(ret == APR_SUCCESS);
}
