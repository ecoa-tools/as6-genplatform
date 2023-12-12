/**
* @file ldp_ELI_udp.h
* @brief ECOA ELI UDP functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef LDP_ELI_UDP_H_
#define LDP_ELI_UDP_H_

#include "ECOA.h"
#include "ldp_ELI.h"
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */


#define LDP_ELI_UDP_HEADER_SIZE (4) //!< size of UDP message header
#define LDP_ELI_UDP_version     (2) //!< version
#define LDP_ELI_UDP_MSG_MAXSIZE (65507) //!< sizeof(UDP datagram) - sizeof(IP header) - sizeof(UDP header), 65535-20-8

//! part of an UDP message
typedef enum ldp_msg_part_type{
    LDP_ELI_BEGIN  = 0x0, //!< first part of an ELI message
    LDP_ELI_MIDDLE = 0x1, //!< middle part of an ELI message
    LDP_ELI_END    = 0x2, //!< end of an ELI message
    LDP_ELI_FULL   = 0x3, //!< full ELI message
}ldp_msg_part_type;

//! contains fields of an UDP message header
typedef struct ldp_ELI_UDP_header{
    ECOA__uint8 UDP_version;      //!< version
    ldp_msg_part_type msg_part; //!< indicate which part of the whole message this datagramme is associate with
    ECOA__uint8 platform_ID;      //!< ID of the sender logical plaform
    ECOA__uint8 channel_ID;       //!< channel ID
    ECOA__uint16 channel_counter; //!< message counter of the channel
}ldp_ELI_UDP_header;

//! context of an ELI UDP channel
typedef struct ldp_ELI_UDP_channel{
    bool is_used;            //!< false if this channel can be used. Channel ID is invalid.
    uint16_t channel_ID;     //!< ID of this channel
    uint16_t channel_counter;//!< counter of this channel
    uint32_t offset;         //!< (only used by reader) bytes already written in buffer
    unsigned char* buffer;   //!< (only used by reader) buffer that handle payload of datagrams to rebuild incomplete message
}ldp_ELI_UDP_channel;

//! context of a PF link
typedef struct ldp_PF_link_ctx{
    uint32_t ELI_connected_PF_ID;//!< ELI ID of the connected PF (defines in logical_system.xml)
    uint8_t UDP_connected_PF_ID; //!< UDP ID of the connected PF that is described in the binding file for this link
    uint16_t channel_num;        //!< number of channel
    uint32_t buffer_size; //!< (only used by reader) size of buffer that handle payload of datagrams to rebuild incomplete message (on each channel)
    ldp_ELI_UDP_channel* channels;       //!< channels contexts
}ldp_PF_link_ctx;


/**
 * function pointer type to define function that send UDP datagram:
 *    - sock_context : abstract structure
 *    - payload : datagram to send
 *    - payload size : size of datagram
 */
typedef void (*ldp_ELI_sending_fct)(void* sock_context, const unsigned char* payload, uint32_t payload_size);

/**
 * @brief      Initialize a link context and allocate memory for channel buffers
 *
 * @param      link_ctx  The link context
 */
void ldp_initialized_PF_link(ldp_PF_link_ctx* link_ctx);

/**
 * @brief      free memory. free channel buffers
 *
 * @param      link_ctx  The link context
 */
void ldp_free_PF_link(ldp_PF_link_ctx* link_ctx);

/**
 * @brief      Read UDP header of message from a cross platform link
 *
 * @param      header     The read UDP header
 * @param      buffer     The read datagramme
 * @param      offset     Index in buffer where start the read
 * @param      read_bytes Number of read bytes
 *
 * @return     return status
 */
ldp_ELI_status ldp_read_ELI_UDP_header(ldp_ELI_UDP_header* header,
                                           ECOA__uint8* buffer,
                                           ECOA__uint32 offset,
                                           ECOA__uint32* read_bytes);

/**
 * @brief      Write UDP header
 *
 * @param      header        The UDP header to write
 * @param      buffer        Buffer in which header is written
 * @param      offset        Index in message where start the written
 * @param      written_bytes Number of written bytes
 *
 * @return     return status
 */
ldp_ELI_status ldp_write_ELI_UDP_header(ldp_ELI_UDP_header* header,
                                            ECOA__uint8* buffer,
                                            ECOA__uint32 offset,
                                            ECOA__uint32* written_bytes);

/**
 * @brief      Writes an ELI UDP platform-level message
 *
 * @param[in]  ELI_platform_ID  The ELI platform id
 * @param[in]  UDP_platform_ID  The UDP platform id
 * @param      channel_ID       The ID of the channel to use
 * @param      buffer           The message buffer that is written
 * @param[in]  pf_msg_type      The platform-level message type
 * @param[in]  field            The field of the message (optional)
 * @param[in]  has_field        Indicates if the message has a field
 */
void write_ELI_UDP_platform_message(uint32_t ELI_platform_ID,
                                    uint8_t UDP_platform_ID,
                                    uint8_t channel_ID,
                                    unsigned char* buffer,
                                    uint32_t pf_msg_type,
                                    uint32_t field,
                                    bool has_field);

/**
 * @brief      Writes an ELI UDP header platform.
 *
 * @param[in]  UDP_platform_ID  The udp platform id
 * @param[in]  channel_ID       The channel id
 * @param      buffer           The buffer
 */
void write_ELI_UDP_header_platform_message(uint8_t UDP_platform_ID,
                                           uint8_t channel_ID,
                                           unsigned char* buffer);

/**
 * @brief      Defragment UDP datagrams. Complete ELI-message if necessary. Check channel counter. Fill channel context
 *
 * @param      link_ctx      The Platform Link connected to the read socket
 * @param      header        The UDP header of the received datagram
 * @param      payload       The datagram payload
 * @param[in]  payload_size  The datagram payload size (may be different from the header->payload_size in case of error)
 * @param      channel_to_return   channel ptr that contains a complete message. NULL if message is incomplete or in case of error
 *
 * @return     ELI_STATUS__OK if a message is complete on channel_to_return,
 *    or ELI_STATUS__NO_CHANNEL_AVAILABLE, ELI_STATUS__LOST_PACKET, ELI_STATUS__INCOMPLETE_MSG, ELI_STATUS__ERROR
 */
ldp_ELI_status ldp_ELI_udp_msg_defragment(ldp_PF_link_ctx* link_ctx,
                                              ldp_ELI_UDP_header* header,
                                              unsigned char* payload,
                                              uint32_t payload_size,
                                              ldp_ELI_UDP_channel** channel_to_return);

/**
 * @brief      Compute the number and the size of fragment to send if the message is too big for one UDP datagram
 *
 * @param[in]  msg_size            The size of the message to send
 * @param      number_fragment     The number fragment to send
 * @param      frgament_size       The size of each fragment (exept the last one)
 * @param      last_frgament_size  The size of the last frgament
 */
void ldp_ELI_udp_compute_fragment(uint32_t msg_size,
                                  uint32_t* number_fragment,
                                  uint32_t* frgament_size,
                                  uint32_t* last_frgament_size);

/**
 * @brief      fragment and send message.
 *
 * @param      sock_context     abstract structure. Contains the context of the sending function
 * @param[in]  sending_fct      pointer to the sending function.
 * @param[in]  msg              The message to send
 * @param[in]  msg_size         The message size
 * @param[in]  platform_ID      The platform ID
 * @param[in]  channel_ID       The channel ID
 * @param      channel_counter  The channel counter to update
 *
 * @return     ELI_STATUS__OK
 */
ldp_ELI_status ldp_ELI_udp_msg_fragment_and_send(void* sock_context,
                                                     const ldp_ELI_sending_fct sending_fct,
                                                     const unsigned char* msg,
                                                     uint32_t msg_size,
                                                     ECOA__uint8 platform_ID,
                                                     ECOA__uint8 channel_ID,
                                                     ECOA__uint16* channel_counter);

#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* LDP_ELI_UDP_H_ */
