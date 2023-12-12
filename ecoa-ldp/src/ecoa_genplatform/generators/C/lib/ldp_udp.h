/**
* @file ldp_udp.h
* @brief ECOA ldp UPD functions and structures
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef _LDP_UDP_H
#define _LDP_UDP_H

#include "ldp_network.h"
#include "ldp_structures.h"

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

#define LDP_UDP_DATA_SIZE (512) //!< size of data in an UDP packet. The UDP packet size will be LDP_UDP_DATA_SIZE+LDP_UDP_HEADER_SIZE
#define LDP_UDP_HEADER_SIZE (3*sizeof(uint32_t) + 2*sizeof(uint16_t)) //!< size of the header of an UDP packet: Start_seq_index | Data_size | num_packets | Msg_id | module_id

typedef struct ldp_tcp_info ldp_tcp_info; //! define in ldp_network.h
#if USE_UDP_PROTO
typedef struct ldp_interface_ctx ldp_interface_ctx; //!< define in ldp_network.h
#endif

//! socket context for written socket
typedef struct ldp_w_socket_ctx{
	apr_socket_t* socket; //!< the written socket
	apr_sockaddr_t* socket_addr; //!< the written socket address
}ldp_w_socket_ctx;

//! contains message info from a specific senders
typedef struct ldp_udp_read_message{
	char* read_msg;  //!< buffer that contains the uncompleted message
	uint32_t read_msg_ID; //!< current ID of the uncompleted message
	uint32_t recieved_packets; //!< number of received packet for the uncompleted message
	uint16_t msg_packet_number; //!< number of packet to recieve
	uint16_t module_id; //!< unique identifier of the module sender
	bool is_free; //!< is the buffer available? message completed = is_free=true | message uncompleted is_free=false or uninitialized buffer
}ldp_udp_read_message;

//! context for a read socket
typedef struct ldp_r_socket_ctx{
	apr_socket_t* socket; //!< the read socket
	apr_sockaddr_t* socket_addr; //!< the read socket address

	char* read_buf; //!< buffer that contains the currently read packet
	int read_msgs_buffer_count; //!< Total number of read_msgs buffer available
	ldp_udp_read_message* read_msgs; //!< buffer that contains the uncompleted message
}ldp_r_socket_ctx;

//! context for an interface(read and written sockets)
typedef struct ldp_interface_udp{
	ldp_tcp_info* info_r;//!< info for the read socket
	ldp_tcp_info* info_w;//!< info fot the written socket

	ldp_r_socket_ctx* read_sock_ctx;//!< the read socket context
	ldp_w_socket_ctx* write_sock_ctx;//!< the written socket context
}ldp_interface_udp;

//! data created for each module 1module contains 1net_data_w containing header informations
typedef struct net_data_w_udp {
 char packet_buffer[LDP_UDP_DATA_SIZE+LDP_UDP_HEADER_SIZE]; //!< The write buffer module
 ECOA__uint16 module_id; //!< The module unique identifier
 ECOA__uint16 msg_id; //!< The current value of incremented msg_id
} net_data_w_udp;

/**
 * @brief      create an UDP interface
 *              - allocate buffer and socket context
 *              - create written and read sockets
 *
 * @param      interface      The interface to create
 * @param[in]  read_buf_size  The read buffer size
 * @param      mp             APR memory pool
 *
 * @return     LDP_SUCCESS or an apr error code
 */
ldp_status_t ldp_create_interface_udp(ldp_interface_udp* interface, int read_buf_size, apr_pool_t *mp);

/**
 * @brief      Get the first completed udp message received from network using the underlying UDP buffer management.
 *								Commonly used after ldp_IP_read return a value > 0.
 *
 * @param      interface      The interface containing the buffer manager
 *
 * @return     The completed message or NULL if no message completed has been found inside the buffer manager.
 */
ldp_udp_read_message* get_first_read_message(ldp_interface_udp* interface);

/**
 * @brief      Destroy an UDP interface. CLose sockets and clean memory
 *
 * @param      interface  The interface
 */
void ldp_destroy_interface_udp(ldp_interface_udp* interface);

/**
 * @brief      Read on a socket
 *              - In TCP : read the socket
 *              - In UDP : read a packet on the socket and update the interface
 *                context
 * @note       define in udp/ or in tcp/
 *
 * @param      sock_interface  The socket interface to read
 * @param      len             On entry : the number of bytes to read. On exit :
 *                             the number of bytes read
 *
 * @return     LDP_SUCCESS if success or an APR error code
 */
ldp_status_t ldp_UDP_read(ldp_interface_udp* sock_interface, apr_size_t* len);

/**
 * Write a packet to the network.
 *
 * @param ctx the network socket context
 * @param msg            the complete message data to write to the network
 *                       data is fragmented using the sequence_start information.
 *
 * @param written_buf    the temporarily buffer used to write data to network (thread safe)
 * @param msg_id				 the message ID unique for each module_id
 * @param data_size      the packet data size
 * @param packet_number  the total number of packet sent from this message
 * @param sequence_start The message offset to be written from
 * @param module_id      The unique module identifier
 */
ldp_status_t ldp_udp_write_packet(ldp_w_socket_ctx* ctx, char* msg,
											char* written_buf, uint32_t msg_id, uint32_t data_size, uint16_t packet_number,
																					uint32_t sequence_start, uint16_t module_id);

/**
 * @brief      Write message on socket.
 * @note       IN TCP : COULD BLOCK INDEFINITLY
 * @note       define in udp/ or in tcp/
 *
 * @param      sock_interface  The sock interface to write
 * @param      msg             The message to write
 * @param[in]  length          The number of byte that must be written
 * @param      data_w          [only used for udp] contains information to write udp packet header
 *
 * @return     APR status
 */
ldp_status_t ldp_UDP_write(ldp_interface_udp* sock_interface, char* msg, int length, net_data_w_udp* data_w);

#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* _LDP_UDP_H */
