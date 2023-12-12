/*
* @file ldp_udp.c
* @brief ECOA ldp UPD functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "apr_network_io.h"
#include "ldp_network.h"
#include <assert.h>
#include "apr_thread_mutex.h"

ldp_status_t ldp_IP_write(ldp_interface_ctx* interface, char* msg, int length, net_data_w* data_w){
	ldp_w_socket_ctx* socket_ctx = interface->inter.local.write_sock_ctx;

	uint16_t packet_number = ((length / LDP_UDP_DATA_SIZE) + (length % LDP_UDP_DATA_SIZE != 0));
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

	} while(sent_count != packet_number && retVal==LDP_SUCCESS);

	return retVal;
}

ldp_status_t ldp_IP_read(ldp_interface_ctx* interface, char* read_completed_buffer, apr_size_t* len){
    return ldp_UDP_read(&interface->inter.local, len);
}
