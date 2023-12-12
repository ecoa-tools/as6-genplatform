/**
* @file ldp_ELI.h
* @brief ECOA ELI functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef LDP_ELI_H_
#define LDP_ELI_H_

#include "ECOA.h"
#include <stdint.h>
#include <stdbool.h>


#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */

#define LDP_ELI_HEADER_SIZE (20) //!< size of ELI message header
#define LDP_ELI_VERSION     (2)  //!< version of ELI protocol

#define LDP_ELI_PLATFORM_MNG (0) //!< Domain value : Platform-level Manager operation
#define LDP_ELI_SERVICE_OP   (1) //!< Domain value : Service operations

//! return status for ELI functions
typedef enum ldp_ELI_status{
    ELI_STATUS__OK,                   //!<
    ELI_STATUS__INCOMPLETE_MSG,       //!< message is not yet complete (not an error)
    ELI_STATUS__ERROR,                //!<
    ELI_STATUS__INVALID_HEADER,       //!<
    ELI_STATUS__LOST_PACKET,          //!< packets have been lost. The message will never been complete
    ELI_STATUS__MEMORY_BUFFER_ERROR,  //!< memory buffer is not large enougth to handle the message
    ELI_STATUS__NO_CHANNEL_AVAILABLE, //!< no free channel context available
}ldp_ELI_status;

//! platform-level ELI message IDs:
typedef enum{
    LDP_ELI_RESERVED                = 0x0,
    LDP_ELI_PLATFORM_STATUS         = 0x1,
    LDP_ELI_PLATFORM_STATUS_REQUEST = 0x2,
    LDP_ELI_UNKNOWN_OPERATION       = 0x3,
    LDP_ELI_VERSIONED_DATA_PULL     = 0x4,
}ldp_ELI_mng_msg_type;

//! contains fields of a generic ELI message header
typedef struct ldp_ELI_header{
    ECOA__uint8 ELI_version;   //!< version
    ECOA__uint8 domain;        //!< ELI functional domaine of this message
    ECOA__uint32 platform_ID;  //!< ID of the sender logical plaform
    ECOA__uint32 msg_ID;       //!< message ID in the context of the domain
    ECOA__uint32 payload_size; //!< size of the payload
    ECOA__uint32 sequence_num; //!< sequence number
} ldp_ELI_header;

/**
 * @brief      Read generic ELI header
 *
 * @param      header     The read ELI header
 * @param      message    Message that contains ELI header
 * @param      offset     Index in message where start the read
 * @param      read_bytes Number of read bytes
 *
 * @return     return status
 */
ldp_ELI_status ldp_read_ELI_header(ldp_ELI_header* header,
                                       ECOA__uint8* message,
                                       ECOA__uint32 offset,
                                       ECOA__uint32* read_bytes);

/**
 * @brief      Write generic ELI header in a message
 *
 * @param      header        The ELI header to write
 * @param      message       Message in which header is written
 * @param      offset        Index in message where start the written
 * @param      written_bytes Number of written bytes
 *
 * @return     return status
 */
ldp_ELI_status ldp_write_ELI_header(ldp_ELI_header* header,
                                        ECOA__uint8* message,
                                        ECOA__uint32 offset,
                                        ECOA__uint32* written_bytes);



/**
 * @brief      Write an ELI platform message (ELI header + field)
 *
 * @param[in]  ELI_platform_ID  The ELI platform id
 * @param      buffer           The buffer to be written
 * @param      offset           The offset in buffer wher to start the writting
 * @param[in]  pf_msg_type      The PF message type
 * @param[in]  field            The field of the message (optional)
 * @param[in]  has_field        Indicates if the message has a field
 */
void write_ELI_platform_msg(uint32_t ELI_platform_ID,
                            unsigned char* buffer,
                            uint32_t offset,
                            uint32_t pf_msg_type,
                            uint32_t field,
                            bool has_field);

#if defined(__cplusplus)
}
#endif /* __cplusplus */

#endif /* LDP_ELI_H_ */

