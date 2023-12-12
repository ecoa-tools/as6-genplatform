/**
* @file ldp_tcp.c
* @brief ECOA ldp TCP functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include <string.h>
#include <apr_strings.h>
#include <apr_time.h>
#include <inttypes.h>

#include "ldp_structures.h"
#include "ldp_network.h"
#include "ldp_log_platform.h"
#include "ldp_status_error.h"
#include "ldp_tcp.h"

static ldp_status_t ldp_IP_read_exactly(ldp_interface_tcp* interface_ctx, char* msg, apr_size_t len);


void ldp_complete_msg(ldp_interface_tcp* interface_ctx, char* buffer, uint32_t* offset, uint32_t* bytes_read, uint32_t msg_size){
	uint32_t remaining_bytes = *bytes_read - *offset;
	if (remaining_bytes < msg_size ){
		memmove(&buffer[0], &buffer[*offset], remaining_bytes); // copy the partial message to the begining of the buffer
		ldp_IP_read_exactly(interface_ctx, (char*) &buffer[remaining_bytes], msg_size - remaining_bytes); // complete msg
		*offset = 0;
		*bytes_read = msg_size;
	}
}

ldp_status_t ldp_IP_write(ldp_interface_ctx* sock_interface, char* msg, int length, net_data_w* data_w/*unused*/){
	UNUSED(data_w);
	apr_size_t written_bits = 0;
	apr_size_t missing_bits = length;
	apr_size_t  len;
	apr_status_t ret;
	if(sock_interface->inter.local.communication_sock == NULL){
		return LDP_ERROR;
	}
	while(missing_bits > 0){
		len = missing_bits;
		ret = apr_socket_send(sock_interface->inter.local.communication_sock, &(msg[written_bits]),&len);
		if(ret != APR_SUCCESS){
			if(ret != APR_EAGAIN){
				return LDP_ERROR;
			}else{
				// if ressource is not avalaible : do again
				// TODO : something to avoid deadlock (if socket is never free) ???
				continue;
			}
		}
		written_bits += len;
		missing_bits -= len;
	}

	return LDP_SUCCESS;
}

static ldp_status_t ldp_TCP_read(ldp_interface_tcp* sock_interface, char* msg, apr_size_t* len){
    int ret=apr_socket_recv(sock_interface->communication_sock,msg,len);
	if (ret != APR_SUCCESS){
		// apr_socket_close(s);
		return ret;
	}

	return LDP_SUCCESS;
}
ldp_status_t ldp_IP_read(ldp_interface_ctx* sock_interface, char* msg, apr_size_t* len){
	return ldp_TCP_read(&sock_interface->inter.local,msg,len);
}

/**
 * @brief      read exactly the number of bytes
 * @note       COULD BLOCK INDEFINITLY
 *
 * @param      s     Socket to read
 * @param      msg   The message
 * @param[in]  len   The length to read
 *
 * @return     ldp_status_t
 */
static ldp_status_t ldp_IP_read_exactly(ldp_interface_tcp* interface_ctx, char* msg, apr_size_t len){
	apr_size_t nb_missing_bytes = len;
	apr_status_t ret;
	while(nb_missing_bytes != 0){
		apr_size_t bytes_to_read = nb_missing_bytes;
		ret = ldp_TCP_read(interface_ctx, &msg[len-bytes_to_read] ,&bytes_to_read);
		if(ret != APR_SUCCESS){
			if (ret != APR_EAGAIN){
				return LDP_ERROR; // Exit because of error
			}else{
				// if ressource is not avalaible : do again
				// TODO : something to avoid deadlock (if socket is never free) ???
				continue;
			}
		}
		nb_missing_bytes -= bytes_to_read;
	}
	return LDP_SUCCESS;
}

ldp_status_t ldp_create_listen_sock(apr_socket_t** new_socket, apr_pool_t *mp, ldp_tcp_info tcp_info){
    apr_sockaddr_t *socket_addr;
	apr_status_t ret;
#if USE_AF_UNIX
    char* l_addr = apr_psprintf(mp, "/tmp/%s_%d", tcp_info.addr, tcp_info.port);
	ret=apr_sockaddr_info_get(&socket_addr, l_addr, APR_UNIX, tcp_info.port, 0, mp);
    socket_addr->sa.unx.sun_path[0]= '\0';
    apr_cpystrn(&(socket_addr->sa.unx.sun_path[1]), l_addr, sizeof(socket_addr->sa.unx.sun_path));
#else
    ret=apr_sockaddr_info_get(&socket_addr, APR_ANYADDR, APR_INET, tcp_info.port, 0, mp);
#endif
	if (ret != APR_SUCCESS){
		return ret;
    }

	ret=apr_socket_create(new_socket,socket_addr->family, SOCK_STREAM, APR_PROTO_TCP, mp);
	if (ret != APR_SUCCESS){
		return ret;
    }

	/* non-blocking socket */
	apr_socket_opt_set(*new_socket, APR_SO_NONBLOCK, 1);
	apr_socket_timeout_set(*new_socket, 0);
	apr_socket_opt_set(*new_socket, APR_SO_REUSEADDR, 1);
	apr_socket_opt_set(*new_socket, APR_TCP_NODELAY, 1);

	ret=apr_socket_bind(*new_socket,socket_addr);
	if (ret != APR_SUCCESS){
		return ret;
    }

	ret=apr_socket_listen(*new_socket, 16);
	if (ret != APR_SUCCESS){
		return ret;
    }

	return LDP_SUCCESS;
}

/**
 * create a client socket and make a connection with server
 * @param new_socket : new client socket
 * @param mp : apr memory pool
 * @param  tcp_info : contains server informations (address and port)
 * @return apr status
 */
static ldp_status_t ldp_do_connect(apr_socket_t** new_socket, apr_pool_t *mp, ldp_tcp_info tcp_info){

	apr_sockaddr_t *socket_addr;
	apr_status_t ret;
#if USE_AF_UNIX
    char* l_addr = apr_psprintf(mp, "/tmp/%s_%d", tcp_info.addr, tcp_info.port);
	ret=apr_sockaddr_info_get(&socket_addr, l_addr, APR_UNIX, tcp_info.port, 0, mp);
    socket_addr->sa.unx.sun_path[0]= '\0';
    apr_cpystrn(&(socket_addr->sa.unx.sun_path[1]), l_addr, sizeof(socket_addr->sa.unx.sun_path));
#else
    ret=apr_sockaddr_info_get(&socket_addr, tcp_info.addr, APR_INET, tcp_info.port, 0, mp);
#endif
	if (ret != APR_SUCCESS){
		return ret;
    }
	ret=apr_socket_create(new_socket,socket_addr->family, SOCK_STREAM, APR_PROTO_TCP, mp);
	if (ret != APR_SUCCESS){
		return ret;
	}

	apr_socket_opt_set(*new_socket, APR_SO_NONBLOCK, 1);
	apr_socket_timeout_set(*new_socket, 30000000);

	ret = apr_socket_connect(*new_socket, socket_addr);
	if (ret != APR_SUCCESS){
		apr_socket_close(*new_socket);
		return ret;
	}

    apr_socket_opt_set(*new_socket, APR_SO_NONBLOCK, 0);
    apr_socket_timeout_set(*new_socket, 30000000);

	return LDP_SUCCESS;
}



apr_status_t ldp_accept_connection(ldp_logger_platform* logger_PF,
									apr_pool_t *mp,
									apr_pollset_t *pollset,
									ldp_interface_ctx* interface_ctx){

	apr_status_t ret;

	// accept socket
	ret=apr_socket_accept(&interface_ctx->inter.local.communication_sock, interface_ctx->inter.local.connection_sock, mp);
	if (ret != APR_SUCCESS){
		ldp_IP_print_err(ret, logger_PF, &interface_ctx->info_r);
		return ret;
	}

	// non-blocking socket
	apr_socket_opt_set(interface_ctx->inter.local.communication_sock, APR_SO_NONBLOCK, 1);
	apr_socket_timeout_set(interface_ctx->inter.local.communication_sock, 0);

	apr_pollfd_t new_fd = (apr_pollfd_t) { mp, APR_POLL_SOCKET, APR_POLLIN , APR_POLLERR | APR_POLLHUP, { NULL }, NULL };
	new_fd.desc.s = interface_ctx->inter.local.communication_sock;
	new_fd.client_data = interface_ctx;

	ret = apr_pollset_add(pollset, &new_fd);
	if (ret != APR_SUCCESS){
		ldp_IP_print_err(ret, logger_PF, &interface_ctx->info_r);
		return ret;
	}

	// stop listening
	interface_ctx->inter.local.is_listening = false;
	return ret;
}


apr_status_t ldp_connect_server(ldp_logger_platform* logger_PF,
								apr_pool_t *mp,
								apr_pollset_t *pollset,
								ldp_interface_ctx* interface_ctx)
{

	// make a connection with server socket
	ldp_status_t ret= ldp_do_connect(&interface_ctx->inter.local.communication_sock, mp, interface_ctx->info_r);
	if (ret != LDP_SUCCESS){
		ldp_IP_print_err(ret, logger_PF, &interface_ctx->info_r);
		return ret;
	}

	// init new file descriptor
	apr_pollfd_t new_fd = (apr_pollfd_t) { mp, APR_POLL_SOCKET, APR_POLLIN | APR_POLLERR | APR_POLLHUP, 0, { NULL }, NULL };
	new_fd.desc.s = interface_ctx->inter.local.communication_sock;
	new_fd.client_data = interface_ctx;

	// add this file descriptot to the poll
	ret = apr_pollset_add(pollset, &new_fd);
	if (ret != APR_SUCCESS){
		ldp_IP_print_err(ret, logger_PF, &interface_ctx->info_r);
	}

	return ret;
}
