/**
* @file ldp_multicast.h
* @brief manage UDP multicast messages and sockets
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/
#ifndef LDP_MULTICAST_H_
#define LDP_MULTICAST_H_

#include <apr_network_io.h>
#include <apr_poll.h>
#include "ldp_ELI_udp.h"

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

//! Platform link structure
typedef struct ldp_PF_link{
  ldp_PF_link_ctx link_ctx; //!< ELI information about this platform link (counters, buffers, IDs)
  ldp_interface_ctx* sender_interface;//!< (only used by reader) sender interface to send response on the same logical PF link
}ldp_PF_link;

//! multicast interface
typedef struct ldp_inter_mcast{
    uint32_t UDP_current_PF_ID ; //!< UDP ID of the current PF on this PF_link
    apr_socket_t* socket;       //!< socket
    apr_sockaddr_t* socket_addr;//!< socket address
    ldp_tcp_info* ip_info;    //!< IP information

    uint32_t link_num; //!< number of PF link connected on this interface
    ldp_PF_link* PF_links_ctx; //!< array of link context for each PF link
}ldp_inter_mcast;

/**
 * @brief      create a read multicast interface (create socket).
 *
 * @param      interface  The interface
 * @param      ip_info    The ip information
 * @param      logger_PF  The logger
 * @param      mp         memory pool
 *
 */
apr_status_t ldp_create_read_multicast_interface(ldp_inter_mcast* interface,
                                              ldp_tcp_info* ip_info,
                                              ldp_logger_platform* logger_PF,
                                              apr_pool_t *mp);
/**
 * @brief      create a write multicast interface (create socket)
 *
 * @param      interface  The interface
 * @param      ip_info    The ip information
 * @param      logger_PF  The logger pf
 * @param      mp         memory pool
 */
apr_status_t ldp_create_sent_multicast_interface(ldp_inter_mcast* interface,
                                              ldp_tcp_info* ip_info,
                                              ldp_logger_platform* logger_PF,
                                              apr_pool_t *mp);

/**
 * @brief      write datagram on a multicast socket
 *
 * @param      interface  The interface
 * @param      msg        The message to send
 * @param      msg_size   The message size
 * @param      logger_PF  Platform logger
 *
 * @return
 */
apr_status_t ldp_mcast_send(ldp_inter_mcast* interface,
                      char* msg,
                      uint64_t* msg_size,
                      ldp_logger_platform* logger_PF);

/**
 * @brief      read a datagram on a multicast socket
 *
 * @param      interface  The interface to read
 * @param      msg        buffer that will contain the read datagram
 * @param      msg_size   the size of buffer
 * @param      logger_PF  Platform logger
 *
 * @return
 */
apr_status_t ldp_mcast_read(ldp_inter_mcast* interface,
                              char* msg,
                              uint64_t* msg_size,
                              ldp_logger_platform* logger_PF);

/**
 * @brief      find Platform link for this interface with the ID of the connected Platform
 *
 * @param      interface_ctx        The interface context
 * @param[in]  UDP_connected_PF_ID  The UDP ID of the connected
 *
 * @return     NULL if no link found
 */
ldp_PF_link* ldp_mcast_find_PF_link(ldp_interface_ctx* interface_ctx, ECOA__uint8 UDP_connected_PF_ID);

#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* LDP_MULTICAST_H_ */
