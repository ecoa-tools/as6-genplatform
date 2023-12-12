/**
* @file ldp_tcp.h
* @brief Contains specific functions and structures for TCP protocol
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef _LDP_TCP_H
#define _LDP_TCP_H

#include "ldp_network.h"
#include "ldp_structures.h"

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

#define LDP_TIME_RECONNECTION 1000*1000 //!< time between 2 reconnections (in micro-seconds)

typedef struct ldp_tcp_info ldp_tcp_info;//!< define in ldp_structures.h
typedef struct ldp_interface_ctx ldp_interface_ctx; //!< define in ldp_network.h

//! contains information about an interface of a protection domain
typedef struct ldp_interface_tcp{
	bool is_server; //!< is server side
	bool is_listening; //!< if server, is waiting for a new connection
	apr_socket_t* communication_sock; //!< communication socket (read/write with other process)
	apr_socket_t* connection_sock;  //!< to connect with new client ( used only for a server interface)
}ldp_interface_tcp;

//! Unused in TCP
typedef struct net_data_w {
 char packet_buffer[1]; //!< unused
 ECOA__uint16 module_id; //!< unused
 ECOA__uint16 msg_id; //!< unused
} net_data_w;

/**
 * @brief      In case of incomplete message, make read on socket and write
 *             completed message at the begining of the buffer In other case, do
 *             nothing
 *
 * @param      interface_ctx  The interface context
 * @param      buffer         The buffer that contains partial or completed
 *                            message
 * @param      offset         The start of the message in buffer. Is update in
 *                            case of incompleted message
 * @param      bytes_read     The number of bytes in buffer that have been
 *                            written during a read on a socket. Is update in
 *                            case of incompleted message
 * @param[in]  msg_size       The message size
 */
void ldp_complete_msg(ldp_interface_tcp* interface_ctx, char* buffer, uint32_t* offset, uint32_t* bytes_read, uint32_t msg_size);


/**
 * @brief      Create a tcp socket. This socket is waiting for new connection
 *
 * @param      new_socket  The new socket
 * @param      mp          APR memory pool
 * @param[in]  tcp_info    The tcp information to create new socket
 *
 * @return     ldp_status_t
 */
ldp_status_t ldp_create_listen_sock(apr_socket_t** new_socket, apr_pool_t *mp, ldp_tcp_info tcp_info);





/**
 * @brief      accept connection and add a new file descriptor in the poll for
 *             this socket
 *
 * @param      logger_PF      The component logger
 * @param      mp             APR memory pool
 * @param      pollset        The pollset
 * @param      interface_ctx  Context of the interface to connect
 *
 * @return     ldp_status_t
 */
apr_status_t ldp_accept_connection(ldp_logger_platform* logger_PF,
									apr_pool_t *mp,
									apr_pollset_t *pollset,
									ldp_interface_ctx* interface_ctx);

/**
 * @brief      create a soket, connect it with server and add the file
 *             descriptor of this socket to the poll
 *
 * @param      logger_PF      The logger pf
 * @param      mp             APR memory pool
 * @param      pollset        The pollset
 * @param      interface_ctx  Context of the interface to connect
 *
 * @return     ldp_status_t
 */
apr_status_t ldp_connect_server(ldp_logger_platform* logger_PF,
								apr_pool_t *mp,
								apr_pollset_t *pollset,
								ldp_interface_ctx* interface_ctx);

#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* _LDP_TCP_H */
