/**
* @file ldp_core_udp.c
* @brief ECOA core UDP functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "apr_network_io.h"
#include "ldp_network.h"
#include <assert.h>
#include "apr_strings.h"
#include "apr_thread_mutex.h"

static ldp_status_t udp_write(apr_socket_t* s, apr_sockaddr_t* addr,char* msg, size_t len){
	apr_size_t written_bits = len;
	apr_status_t ret = apr_socket_sendto(s, addr, 0, msg, &written_bits);
	if(ret != APR_SUCCESS){
		return ret;
    }

	assert(written_bits==len);
	return APR_SUCCESS;
}

static ldp_status_t ldp_create_server_udp_socket(ldp_r_socket_ctx* socket_ctx, apr_pool_t *mp, ldp_tcp_info* tcp_info){

	apr_status_t ret;
#if USE_AF_UNIX
    char* l_addr = apr_psprintf(mp, "/tmp/%s_%d", tcp_info->addr, tcp_info->port);
	ret=apr_sockaddr_info_get(&socket_ctx->socket_addr, l_addr, APR_UNIX, tcp_info->port, 0, mp);
    socket_ctx->socket_addr->sa.unx.sun_path[0]= '\0';
    apr_cpystrn(&(socket_ctx->socket_addr->sa.unx.sun_path[1]), l_addr, sizeof(socket_ctx->socket_addr->sa.unx.sun_path));
#else
    ret=apr_sockaddr_info_get(&socket_ctx->socket_addr, APR_ANYADDR, APR_INET, tcp_info->port, 0, mp);
#endif
	if (ret != APR_SUCCESS){
		return ret;
    }

	ret=apr_socket_create(&socket_ctx->socket, socket_ctx->socket_addr->family, SOCK_DGRAM, APR_PROTO_UDP, mp);
	if (ret != APR_SUCCESS){
		return ret;
    }

	ret=apr_socket_opt_set(socket_ctx->socket, APR_SO_REUSEADDR, 1);
	if (ret != APR_SUCCESS){
		return ret;
    }

	ret=apr_socket_bind(socket_ctx->socket, socket_ctx->socket_addr);
	if(ret != APR_SUCCESS){
		return ret;
	}

	return LDP_SUCCESS;
}

static ldp_status_t ldp_create_client_udp_socket(ldp_w_socket_ctx* socket_ctx, apr_pool_t *mp, ldp_tcp_info* tcp_info){
	apr_status_t ret;
#if USE_AF_UNIX
    char* l_addr = apr_psprintf(mp, "/tmp/%s_%d", tcp_info->addr, tcp_info->port);
	ret=apr_sockaddr_info_get(&socket_ctx->socket_addr, l_addr, APR_UNIX, tcp_info->port, 0, mp);
    socket_ctx->socket_addr->sa.unx.sun_path[0]= '\0';
    apr_cpystrn(&(socket_ctx->socket_addr->sa.unx.sun_path[1]), l_addr, sizeof(socket_ctx->socket_addr->sa.unx.sun_path));
#else
    ret=apr_sockaddr_info_get(&socket_ctx->socket_addr, tcp_info->addr, APR_INET, tcp_info->port, 0, mp);
#endif
	if (ret != APR_SUCCESS){
		return ret;
    }

	ret=apr_socket_create(&socket_ctx->socket,socket_ctx->socket_addr->family, SOCK_DGRAM, APR_PROTO_UDP, mp);
	if (ret != APR_SUCCESS){
		return ret;
    }

	// apr_socket_opt_set(socket_ctx->socket, APR_SO_NONBLOCK, 1);
	// apr_socket_timeout_set(socket_ctx->socket, 0);
	ret=apr_socket_opt_set(socket_ctx->socket, APR_SO_REUSEADDR, 1);
	if (ret != APR_SUCCESS){
		return ret;
    }

	return LDP_SUCCESS;
}


static void write_header(char* msg, uint32_t data_size, uint32_t msg_ID, uint32_t seq_start, uint16_t num_of_packet, uint16_t module_id){
	uint32_t offset=0;
	memcpy(&msg[offset], &msg_ID, sizeof(msg_ID));
	offset+=sizeof(msg_ID);
	memcpy(&msg[offset], &seq_start, sizeof(seq_start));
	offset+=sizeof(seq_start);
	memcpy(&msg[offset], &data_size, sizeof(data_size));
	offset+=sizeof(data_size);
	memcpy(&msg[offset], &num_of_packet, sizeof(num_of_packet));
	offset+=sizeof(num_of_packet);
	memcpy(&msg[offset], &module_id, sizeof(module_id));
}

/**
 * Initialize a new buffer
 * allocate an array of buf_size containing the uncompleted received message
 */
static ldp_udp_read_message generate_buffer(uint32_t buf_size) {
	ldp_udp_read_message udp_read_msg;
	udp_read_msg.read_msg=calloc(buf_size, sizeof(char));
	udp_read_msg.read_msg_ID=0x00;
	udp_read_msg.recieved_packets=0x00;
	udp_read_msg.msg_packet_number=0x00;
	udp_read_msg.module_id=0x00;
	udp_read_msg.is_free=true;

	return udp_read_msg;
}

ldp_status_t ldp_create_interface_udp(ldp_interface_udp* interface, int read_buf_size, apr_pool_t *mp){

	interface->read_sock_ctx = calloc(1, sizeof(ldp_r_socket_ctx));
	interface->read_sock_ctx->read_buf = malloc(LDP_UDP_DATA_SIZE+LDP_UDP_HEADER_SIZE);
	interface->read_sock_ctx->read_msgs_buffer_count = interface->info_r->msg_buffer_count;

	if (interface->read_sock_ctx->read_msgs_buffer_count == 0) {
		interface->read_sock_ctx->read_msgs_buffer_count=1; // set at least one buffer
	}

	interface->read_sock_ctx->read_msgs = calloc(interface->read_sock_ctx->read_msgs_buffer_count, sizeof(ldp_udp_read_message));

	for (size_t i = 0; i < interface->read_sock_ctx->read_msgs_buffer_count; i++) {
		interface->read_sock_ctx->read_msgs[i] = generate_buffer(read_buf_size);
	}

	interface->write_sock_ctx = calloc(1, sizeof(ldp_w_socket_ctx));

	apr_status_t ret = ldp_create_server_udp_socket(interface->read_sock_ctx, mp, interface->info_r);
	if (ret != APR_SUCCESS){
		return ret;
	}

	ret = ldp_create_client_udp_socket(interface->write_sock_ctx, mp, interface->info_w);
	if (ret != APR_SUCCESS){
		return ret;
	}

	return APR_SUCCESS;
}

ldp_status_t ldp_udp_write_packet(ldp_w_socket_ctx* ctx, char* msg,
											char* written_buf, uint32_t msg_id, uint32_t data_size, uint16_t packet_number,
																					uint32_t sequence_start, uint16_t module_id){

	write_header(written_buf, data_size, msg_id, sequence_start, packet_number, module_id);
	memcpy(&(written_buf)[LDP_UDP_HEADER_SIZE], &msg[sequence_start], data_size);
	return udp_write(ctx->socket, ctx->socket_addr, written_buf, data_size+LDP_UDP_HEADER_SIZE);
}

void ldp_destroy_interface_udp(ldp_interface_udp* interface){
	free(interface->read_sock_ctx->read_buf);
	for (size_t i = 0; i < interface->read_sock_ctx->read_msgs_buffer_count; i++) {
		free(interface->read_sock_ctx->read_msgs[i].read_msg);
	}

	free(interface->read_sock_ctx->read_msgs);

	apr_socket_close(interface->read_sock_ctx->socket);
	apr_socket_close(interface->write_sock_ctx->socket);

	free(interface->read_sock_ctx);
	free(interface->write_sock_ctx);
}

ldp_status_t ldp_UDP_write(ldp_interface_udp* sock_interface, char* msg, int length, net_data_w_udp* data_w){
	ldp_w_socket_ctx* socket_ctx = sock_interface->write_sock_ctx;

	uint16_t packet_number = ((length / LDP_UDP_DATA_SIZE) + ((length % LDP_UDP_DATA_SIZE != 0)?1:0));
	int data_size = (packet_number>1) ? LDP_UDP_DATA_SIZE : length;

	data_w->msg_id++;

	int seq_start=0;
	int sent_count=0;
	ldp_status_t retVal=LDP_SUCCESS;
	do {
		retVal=ldp_udp_write_packet(socket_ctx, msg, data_w->packet_buffer, data_w->msg_id, data_size, packet_number, seq_start, data_w->module_id);

		sent_count++;

		if (sent_count == packet_number-1 && length % LDP_UDP_DATA_SIZE != 0){
			data_size = length % LDP_UDP_DATA_SIZE;
		}
		else{
			data_size = LDP_UDP_DATA_SIZE;
		}

		seq_start=LDP_UDP_DATA_SIZE*sent_count;
		// usleep(1);

	} while(sent_count != packet_number && retVal==LDP_SUCCESS);

	return retVal;
}

/**
 * Pick a buffer according to the received module_id
 * Each time a new module_id is received a buffer should be picked for that particular module id
 * So each time a message with the already received module_id is received the reserved buffer will be picked.
 * If all the buffer are 'allowed' to a module_id there is no more free buffer available.
 */
static ldp_udp_read_message* pick_msg_buffer(ldp_interface_udp* interface, uint16_t module_id){
	ldp_udp_read_message* read_msg_buf=NULL;
	bool free_buffer=false;

	// Find the buffer associated with the module's sender id
	for (size_t i = 0; i < interface->read_sock_ctx->read_msgs_buffer_count; i++) {
		ldp_udp_read_message* current_msg_buf = &interface->read_sock_ctx->read_msgs[i];

		// If buffer found exit and return it
		if(current_msg_buf->module_id == module_id){
			return current_msg_buf;
		}

		// Find the first unused buffer (uninitialized)
		if(free_buffer==false && current_msg_buf->is_free == true && current_msg_buf->module_id == 0x00){
			free_buffer=true;
			read_msg_buf=current_msg_buf;
		}
	}

	// Associate the found empty buffer to the module id
	if (read_msg_buf!=NULL)
	{
		read_msg_buf->module_id = module_id;
		read_msg_buf->is_free   = false;
	}else{
		// error
		// no buffer found. No buffer available.
	}

	return read_msg_buf;
}

/*
 * Parse UDP raw header in order fill parameters.
 *
 * @param header         Packet header data to be parsed.
 * @param msg_ID         The message ID parsed from the header buffer.
 * @param msg_seq_       The message data offset parsed from the header buffer.
 * @param msg_data_size  Size of the received packet parsed from the header buffer.
 * @param msg_packet_num The total count of packet for this message parsed from the header buffer.
 * @param module_id      the unique module_id parsed from the header buffer.

 * @return read_size     The total read size (should be size of UDP header)
 */
static uint32_t parse_udp_header(char* header, uint32_t* msg_ID, uint32_t* msg_seq_start,
											uint32_t* msg_data_size, uint16_t* msg_packet_num, uint16_t* module_id) {
	uint32_t offset=0;
	*msg_ID         = *((uint32_t*) &(header[offset]));
	offset+=sizeof(*msg_ID);
	*msg_seq_start  = *((uint32_t*) &(header[offset]));
	offset+=sizeof(*msg_seq_start);
	*msg_data_size  = *((uint32_t*) &(header[offset]));
	offset+=sizeof(*msg_data_size);
	*msg_packet_num = *((uint16_t*) &(header[offset]));
	offset+=sizeof(*msg_packet_num);
	*module_id      = *((uint16_t*) &(header[offset]));
	offset+=sizeof(*module_id);

	return offset;
}

/**
 *	Insert new packet into a retrieved buffer from "pick_msg_buffer"
 *
 *	Three cases are possible in order to insert the message:
 *  1 - Buffer is free => Message is inserted into the given buffer
 *  2 - Buffer is not free and msg_id is the same as the buffer => Message is completed
 *                                    with the new received packet.
 *  3 - Buffer is not free and msg_id is higher than the buffer one => Buffer is overriden
 *                                    with the new message information.
 */
static void insert_msg_into_buffer(ldp_udp_read_message* read_msg_buf, char* packet_data, uint32_t msg_ID,
									uint32_t msg_seq_start, uint32_t msg_data_size, uint16_t msg_packet_num) {
	bool override=false;

	if (read_msg_buf->is_free) {
		override=true;
	} else {
		if (read_msg_buf->read_msg_ID == msg_ID) {
			read_msg_buf->recieved_packets++;
			memcpy(&read_msg_buf->read_msg[msg_seq_start], packet_data, msg_data_size);
		} else if (read_msg_buf->read_msg_ID < msg_ID) {
			override=true;
		}
	}

	if (override) {
		read_msg_buf->read_msg_ID       = msg_ID;
		read_msg_buf->recieved_packets  = 0x01; // this packet
		read_msg_buf->msg_packet_number = msg_packet_num;
		read_msg_buf->is_free=false;

		memcpy(&read_msg_buf->read_msg[msg_seq_start], packet_data, msg_data_size);
	}
}

ldp_udp_read_message* get_first_read_message(ldp_interface_udp* interface){
	for (size_t i = 0; i < interface->read_sock_ctx->read_msgs_buffer_count; i++) {
		ldp_udp_read_message* current_msg_buf = &interface->read_sock_ctx->read_msgs[i];

		if (current_msg_buf->recieved_packets == current_msg_buf->msg_packet_number && current_msg_buf->is_free == false)
		{
			current_msg_buf->is_free=true; // The buffer is no freed and can be used by
			return current_msg_buf;
		}
	}
	return NULL; // No completed buffer found
}

ldp_status_t ldp_UDP_read(ldp_interface_udp* sock_interface, apr_size_t* len){

	ldp_r_socket_ctx* socket_ctx = sock_interface->read_sock_ctx;

	apr_size_t len_packet = LDP_UDP_DATA_SIZE+LDP_UDP_HEADER_SIZE;
	int ret=apr_socket_recv(socket_ctx->socket, socket_ctx->read_buf, &len_packet) ;
	if (ret != APR_SUCCESS){
		// apr_socket_close(s);
		return ret;
	}

	uint32_t msg_ID, msg_seq_start, msg_data_size = 0;
	uint16_t msg_packet_num, module_id = 0;

	// read header @TODO endianess
	uint32_t offset=parse_udp_header(socket_ctx->read_buf, &msg_ID, &msg_seq_start, &msg_data_size, &msg_packet_num, &module_id);

	if (offset!=LDP_UDP_HEADER_SIZE) {
		// WARNING should never happen
	}

	// Retrieve the buffer associated to the received module id
	ldp_udp_read_message* msg_buf=pick_msg_buffer(sock_interface, module_id);
	if (msg_buf!=NULL){
		insert_msg_into_buffer(msg_buf, &socket_ctx->read_buf[offset], msg_ID, msg_seq_start, msg_data_size, msg_packet_num);

		if (msg_buf->msg_packet_number == msg_buf->recieved_packets){
				*len = 1; // flag in order to say that full message has been recieved
		}
	} else {
		// No buffer available for this module id
		return LDP_ERROR;
	}

	return LDP_SUCCESS;
}
