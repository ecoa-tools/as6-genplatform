/**
* @file ldp_ELI_msg_management.h
* @brief ECOA ELI management functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef LDP_ELI_MSG_MANAGEMENT_H_
#define LDP_ELI_MSG_MANAGEMENT_H_

#include "ECOA.h"
#include "ECOA_simple_types_serialization.h"
#include "ldp_network.h"
#include "ldp_ELI.h"
#include "ldp_structures.h"

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

/**
 * @brief      first step of ELI startup sequence: send PLATFORM_STATUS message to every DOWN platform
 *
 * @param      ctx   The context of the main process
 *
 * @return
 */
ldp_ELI_status ldp_ELI_UDP_startup_sequence(ldp_Main_ctx* ctx);

/**
 * @brief      Main process read datagram on an interface. Process message.
 *
 * @param      ctx                 The context of the main process
 * @param      read_interface_ctx  The interface context to read
 *
 * @return
 */
ldp_ELI_status ldp_ELI_UDP_main_read_msg(ldp_Main_ctx* ctx, ldp_interface_ctx* read_interface_ctx);

/**
 * @brief      Protection Domain read datagram on an interface. Process completed message and route it to a module FIFO
 *
 * @param      ctx            The protection domain context
 * @param      interface_ctx  The interface context to read
 * @param      msg_buffer     The message buffer to handle message
 * @param[in]  buffer_size    The buffer size
 *
 * @return
 */
apr_status_t ldp_ELI_UDP_PD_read_msg(ldp_PDomain_ctx* ctx,
                                         ldp_interface_ctx* interface_ctx,
                                         char* msg_buffer,
                                         uint32_t buffer_size);

//! structure of the context of ldp_ELI_UDP_sending_fct
typedef struct ldp_sending_fct_ctx{
	ldp_inter_mcast* interface;  //!< sending interface
	ldp_logger_platform* logger; //!< logger
}ldp_sending_fct_ctx;

//! function type to send ELI message on an UDP multicast socket
void ldp_ELI_UDP_sending_fct(void* sock_context, const unsigned char* payload, uint32_t payload_size);


#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* LDP_ELI_MSG_MANAGEMENT_H_ */
