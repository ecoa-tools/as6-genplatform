/**
* @file ldp_tcp_comp_server.c
* @brief ECOA component server (protected domain)
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
#include <apr_time.h>

#include "ldp_structures.h"
#include "ldp_network.h"
#include "ldp_log_platform.h"
#include "ldp_list.h"
#include "ldp_tcp.h"
#include "ldp_multicast.h"
#include "ldp_ELI.h"
#include "ldp_ELI_msg_management.h"
#include "ldp_ELI_udp.h"

// /**
//  * only to debug. Print apr error status
//  */
// static void ldp_IP_print_err(apr_status_t err, ldp_logger_platform* logger_PF){
// 	char buf[128];
// 	apr_strerror(err,buf,128);
// 	ldp_log_PF_log(ECOA_LOG_ERROR,"ERROR", logger_PF, buf);
// }

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
	apr_status_t ret=ldp_IP_write(&ctx->interface_ctx_array[ctx->nb_client],(char*) &op_ID, sizeof(uint8_t), &data_w);
	if(ret != APR_SUCCESS){
		return ret;
	}
	return LDP_SUCCESS;
}

/**
 * @brief      Try to connect with server all unconnected interface in the list
 *
 * @param      ctx        The component context
 * @param      pollset    The pollset
 * @param      list       The list of unconnected interface
 * @param      apr_time_t the time before the next reconnection
 */
static void reconnect_all_interfaces(ldp_PDomain_ctx* ctx, apr_pollset_t *pollset, ldp_list* list, apr_time_t* next_reconnection)
{
	if(list->current_size > 0){
		apr_time_t current_time = apr_time_now();
		if (current_time > *next_reconnection){
			// compute next reconnection time
			*next_reconnection = current_time + apr_time_usec(LDP_TIME_RECONNECTION);

			ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,"[%s], try reconnection with %i server(s)", ctx->name, list->current_size);
			ldp_interface_ctx* interface_to_recon;
			int num_of_inter = list->current_size;
			for(int i=0; i < num_of_inter; i++){
				if(ldp_remove_first_node(list, (void**)&interface_to_recon) != APR_SUCCESS){
					ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,"[%s], failed to remove first node in unconnected interface list", ctx->name);
					continue;
				}

				if(ldp_connect_server(ctx->logger_PF,
									ctx->mem_pool,
									pollset,
									interface_to_recon) != LDP_SUCCESS){

					// add interface in list if connect failed
					ldp_node* node;
					node = ldp_add_last(list);
					node->data = interface_to_recon;

				}else{
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,"[%s], connect port %i", ctx->name, interface_to_recon->info_r.port );
				}
			}
		}
	}
}

/**
 * @brief      in case of a closed socket, this function enable a reconnection and remove file descriptor from the pollset
 *
 * @param      ctx                   The component context
 * @param      pollset               The pollset
 * @param[in]  fd                    The file descriptor
 * @param      interf_ctx            The interface context
 * @param      l_interface_to_recon  The list of interface to reconnect with a sever
 */
static void enable_reconnection(ldp_PDomain_ctx* ctx,
								apr_pollset_t *pollset,
								const apr_pollfd_t* fd,
								ldp_interface_ctx* interf_ctx,
								ldp_list* l_interface_to_recon)
{
	//clean
	int ret=apr_pollset_remove (pollset, fd);
	assert(ret == APR_SUCCESS);
	ret = apr_socket_close( interf_ctx->inter.local.communication_sock);
	assert(ret == APR_SUCCESS);
	interf_ctx->inter.local.communication_sock = NULL;

	if(interf_ctx->inter.local.is_server){
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,"[%s], allow client reconnection (%s:%i)", ctx->name,
								interf_ctx->info_r.addr, interf_ctx->info_r.port);
		interf_ctx->inter.local.is_listening=true; // accept new connection

	}else{
		ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,"[%s], add reconnection in list (%s:%i)", ctx->name,
								interf_ctx->info_r.addr, interf_ctx->info_r.port);

		// add interface context in list
		ldp_node* node;
		node = ldp_add_last(l_interface_to_recon);
		node->data = interf_ctx;
	}

	UNUSED(ret);
}

/**
 * @brief      read tcp buffer on a file descriptor. Parse this buffer. could read more than one message
 *
 * @param      ctx            The component context
 * @param      read_buffer    The buffer that is filled by a read on the socket
 * @param      interface_ctx  The interface context
 * @param[in]  bytes_read     The size of the read_buffer
 *
 *
 * @return     { description_of_the_return_value }
 */
static ldp_status_t TCP_read_and_parse_buffer(ldp_PDomain_ctx* ctx,
									char* read_buffer,
									ldp_interface_ctx* interface_ctx,
									uint32_t bytes_read)
{
	// parse buffer (could contains more than one message)
	uint32_t offset=0;
	apr_status_t retval = APR_SUCCESS;
    uint32_t l_bytes_read = bytes_read;

	while(offset < l_bytes_read){
		uint32_t param_size;
		uint32_t op_ID;

		// complete header if necessary
		ldp_complete_msg(&interface_ctx->inter.local, read_buffer, &offset, &l_bytes_read, LDP_HEADER_TCP_SIZE);

		// read header
		if(!ldp_read_IP_header(ctx,&read_buffer[offset], &op_ID, &param_size)){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"INFO", ctx->logger_PF, "[%s] ERROR in TCP message header",ctx->name);
			// TODO do something to find the next correct message
			assert(0);
		}

		// complete message if necessary
		ldp_complete_msg(&interface_ctx->inter.local, read_buffer, &offset, &l_bytes_read, param_size+LDP_HEADER_TCP_SIZE);

		// consume message
		retval = domain_proc_consume_msg(ctx, &read_buffer[offset], param_size, op_ID, interface_ctx);
		if (retval != LDP_SUCCESS){
			break;
		}

		offset += param_size;
		offset += LDP_HEADER_TCP_SIZE;
	}

	return retval;
}

/**
 * @brief      component loop that wait and read events on file descriptor in popllset
 *
 * @param      ctx                   The component context
 * @param      l_interface_to_recon  The list of interface to (re)connect with a server
 * @param      pollset               The pollset
 */
static void run_comp_server(ldp_PDomain_ctx* ctx, ldp_list* l_interface_to_recon, apr_pollset_t *pollset)
{
	apr_int32_t num;
	const apr_pollfd_t *ret_pfd;
	apr_status_t ret;

	int buffer_size = ctx->msg_buffer_size;
	char ldp_IP_read_buf[buffer_size];
	int retval;

	bool server_is_running = true;
	apr_time_t next_reconnection = 0;
	while(server_is_running){
		ret=apr_pollset_poll(pollset, LDP_TIME_RECONNECTION, &num, &ret_pfd);
		if (ret != LDP_SUCCESS && num <0){
			ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,"[%s] error in pollset %i", ctx->name, num);
			//continue;
		}

		// do reconnection if necessary
		reconnect_all_interfaces(ctx, pollset, l_interface_to_recon, &next_reconnection);

		// send init to father when all connections are done
		if (ctx->state == PDomain_IDLE){
			if(l_interface_to_recon->current_size == 0){
				if(sent_msg_to_father(ctx, LDP_ID_CLIENT_INIT) != APR_SUCCESS){
					ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s] Cannot send CLIENT_INIT to father process", ctx->name);
				}else{
					ctx->state = PDomain_INIT;
				}
			}
		}

		// read all awake file descriptors
		for(int i=0; i<num;i++){
			ldp_interface_ctx* interface_ctx = ret_pfd[i].client_data;

			if(interface_ctx->type == LDP_ELI_MCAST){
				// ELI message from a multicast socket
				ldp_ELI_UDP_PD_read_msg(ctx, interface_ctx, &ldp_IP_read_buf[0], buffer_size);
			}else{
				// internal Platform message
				if(interface_ctx->inter.local.is_listening){
					// accept connection
					ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "[%s] accept new connection on port %i", ctx->name, interface_ctx->info_r.port);
					retval = ldp_accept_connection(ctx->logger_PF,
									ctx->mem_pool,
									pollset,
									interface_ctx);
					if (retval != LDP_SUCCESS){
						ldp_warning_status_log(ctx->logger_PF, retval,"[%s] can not accept new connection on port %i : ", ctx->name, interface_ctx->info_r.port );
						assert(retval == APR_SUCCESS);
					}
				}else{
					//read data on TCP socket
					apr_size_t bytes_read = buffer_size;
					retval = ldp_IP_read(interface_ctx, &ldp_IP_read_buf[0],&bytes_read);
					if (retval == APR_EOF){
						// reconnection
						ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF, "[%s], socket closed on port %i ?", ctx->name, interface_ctx->info_r.port);
						enable_reconnection(ctx,
								pollset,
								&ret_pfd[i],
								interface_ctx,
								l_interface_to_recon);
					}else{
						// normal case
						if(TCP_read_and_parse_buffer(ctx,
									&ldp_IP_read_buf[0],
									interface_ctx,
									(uint32_t)bytes_read) != APR_SUCCESS){
							ldp_log_PF_log_var(ECOA_LOG_WARN_PF,"WARNING", ctx->logger_PF, "[%s] STOP SERVER", ctx->name);
							// break server loop to shut down Protection Domain
							server_is_running=false;
							break;
						}
					}
				}
			}
		}
	}
}

/**
 * @brief      close opened socket
 *
 * @param      ctx                  The component context
 * @param      interface_ctx_array  The array of interface
 */
static void sockets_cleanup(ldp_PDomain_ctx* ctx, ldp_interface_ctx* interface_ctx_array){
	// server sockets
	for(int i=0; i<ctx->nb_client; i++){
		if (interface_ctx_array[i].type == LDP_LOCAL_IP){
			if( interface_ctx_array[i].inter.local.connection_sock != NULL){
				apr_socket_close(interface_ctx_array[i].inter.local.connection_sock);
			}
			if( interface_ctx_array[i].inter.local.communication_sock != NULL){
				apr_socket_close(interface_ctx_array[i].inter.local.communication_sock);
			}
		}
	}

	// client sockets
	for(int i=ctx->nb_client; i<ctx->nb_client+ctx->nb_server; i++){
		if (interface_ctx_array[i].type == LDP_LOCAL_IP){
			if( interface_ctx_array[i].inter.local.communication_sock != NULL){
				apr_socket_close(interface_ctx_array[i].inter.local.communication_sock);
			}
		}
	}
}


void ldp_start_comp_server(ldp_PDomain_ctx* ctx){
	// create a poll of file descriptors
	apr_pool_t* mem_pool = ctx->mem_pool;
	apr_pollset_t *pollset;
	apr_pollset_create_ex(&pollset, 2*ctx->nb_client+ctx->nb_server + ctx->mcast_read_interface_num, mem_pool, 0,APR_POLLSET_EPOLL);
	ldp_interface_ctx* interface_ctx_array = ctx->interface_ctx_array;
	ldp_list interface_to_recon;
	apr_status_t ret;

	// server interface
	for(int i=0; i<ctx->nb_client; i++){
		if (interface_ctx_array[i].type == LDP_ELI_MCAST){
			// nothing to do: not possible
		}else{
			// create connection socket
			interface_ctx_array[i].inter.local.is_listening=true;
			interface_ctx_array[i].inter.local.is_server=true;
			interface_ctx_array[i].inter.local.communication_sock = NULL;
			apr_status_t ret=ldp_create_listen_sock(&interface_ctx_array[i].inter.local.connection_sock, mem_pool, interface_ctx_array[i].info_r);
			if (ret != LDP_SUCCESS){
				ldp_error_status_log(ctx->logger_PF, ret, "[%s] Can't create listening socket %s:%i. ",
					ctx->name, interface_ctx_array[i].info_r.addr, interface_ctx_array[i].info_r.port);
				assert(ret == APR_SUCCESS);
			}
			// add new file desciptor
			ldp_add_pollset(pollset, &interface_ctx_array[i], interface_ctx_array[i].inter.local.connection_sock, ctx->mem_pool);
		}
	}

	// client interface
	for(int i=ctx->nb_client; i<ctx->nb_client+ctx->nb_server; i++){
		if (interface_ctx_array[i].type == LDP_ELI_MCAST){
			ret = ldp_create_sent_multicast_interface(&interface_ctx_array[i].inter.mcast,
														&interface_ctx_array[i].info_r,
														ctx->logger_PF, ctx->mem_pool);
			if( ret != LDP_SUCCESS){
				ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
								"Impossilbe to create sent multicast interface (%s:%i)",
									interface_ctx_array[i].info_r.addr, interface_ctx_array[i].info_r.port);
			}
		}else{
			// initialize TCP client socket
			interface_ctx_array[i].inter.local.is_listening=false;
			interface_ctx_array[i].inter.local.is_server=false;
			interface_ctx_array[i].inter.local.communication_sock = NULL;
			interface_ctx_array[i].inter.local.connection_sock = NULL;
		}
	}

	// ELI multicast read socket
	for(int i=0; i<ctx->mcast_read_interface_num; i++){
		ret = ldp_create_read_multicast_interface(&ctx->mcast_read_interface[i].inter.mcast,
													&ctx->mcast_read_interface[i].info_r,
													ctx->logger_PF,
													ctx->mem_pool);
		if( ret == LDP_SUCCESS){
			ldp_add_pollset(pollset, &ctx->mcast_read_interface[i], ctx->mcast_read_interface[i].inter.mcast.socket, ctx->mem_pool);
		}else{
			ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
								"Impossilbe to create read multicast interface (%s:%i)",
								ctx->mcast_read_interface[i].info_r.addr, ctx->mcast_read_interface[i].info_r.port);
		}
	}

	// connect with main process
	while(ldp_connect_server(ctx->logger_PF,
								ctx->mem_pool,
								pollset,
								&interface_ctx_array[ctx->nb_client]) != LDP_SUCCESS){
		ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF, "[%s], cant connect with main %i", ctx->name, interface_ctx_array[ctx->nb_client].info_r.port);
		apr_sleep(LDP_TIME_RECONNECTION);
	}
	interface_ctx_array[ctx->nb_client].inter.local.is_listening = false;

	// create list for reconnexion without the connection with the main process
	ldp_init_list(&interface_to_recon, ctx->nb_server, 0);
	for(int i=ctx->nb_client+1;  i<ctx->nb_client+ctx->nb_server; i++){
		if (interface_ctx_array[i].type == LDP_LOCAL_IP){
			ldp_node* node;
			node = ldp_add_last(&interface_to_recon);
			node->data = &interface_ctx_array[i];
		}
	}

	////////////////////////////////////////////
	// run server
	////////////////////////////////////////////
	ctx->state = PDomain_IDLE;
	run_comp_server(ctx, &interface_to_recon, pollset);
	apr_pollset_destroy(pollset);

	// clean all socket properly
	sockets_cleanup(ctx, interface_ctx_array);


	free(interface_to_recon.node_array);

}
