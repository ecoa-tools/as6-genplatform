/**
* @file ldp_ELI.c
* @brief ECOA ELI functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_ELI.h"
#include <ECOA.h>
#include "ECOA_simple_types_serialization.h"

ldp_ELI_status ldp_read_ELI_header(ldp_ELI_header* header,
                                       ECOA__uint8* message,
                                       ECOA__uint32 offset,
                                       ECOA__uint32* read_bytes){
    ECOA__uint32 new_offset = offset;
    *read_bytes = new_offset;

    // check 0xECOA
    if ((message[new_offset] != 0xEC) ||
        (message[new_offset + 1] != 0x0A)){
        return ELI_STATUS__INVALID_HEADER;
    }
    new_offset += 2;

    // check ELI Version
    if (message[new_offset++] != LDP_ELI_VERSION){
        return ELI_STATUS__INVALID_HEADER;
    }
    header->ELI_version = LDP_ELI_VERSION;

    // message domain
    header->domain = message[new_offset++];

    // logical Platform ID
    deserialize_ECOA__uint32(&header->platform_ID, &message[new_offset], 4);
    new_offset += 4;

    // ID
    deserialize_ECOA__uint32(&header->msg_ID, &message[new_offset], 4);
    new_offset += 4;

    //size
    deserialize_ECOA__uint32(&header->payload_size, &message[new_offset], 4);
    new_offset += 4;

    // sequence number
    deserialize_ECOA__uint32(&header->sequence_num, &message[new_offset], 4);
    new_offset += 4;

    *read_bytes = new_offset - *read_bytes;
    return ELI_STATUS__OK;
}

ldp_ELI_status ldp_write_ELI_header(ldp_ELI_header* header,
                                        ECOA__uint8* message,
                                        ECOA__uint32 offset,
                                        ECOA__uint32* written_bytes){
    ECOA__uint32 new_offset = offset;
    *written_bytes = new_offset;

    // 0xECOA
    message[new_offset++] = 0xEC;
    message[new_offset++] = 0x0A;

    // ELI version number
    message[new_offset++] = LDP_ELI_VERSION;

    // message domain
    message[new_offset++] = header->domain;

    // logical Platform ID
    uint32_t added_bytes;
    serialize_ECOA__uint32(header->platform_ID, &message[new_offset], 4, &added_bytes);
    new_offset += added_bytes;

    // ID
    serialize_ECOA__uint32(header->msg_ID, &message[new_offset], 4, &added_bytes);
    new_offset += added_bytes;

    //size
    serialize_ECOA__uint32(header->payload_size, &message[new_offset], 4, &added_bytes);
    new_offset += added_bytes;

    //sequence number
    serialize_ECOA__uint32(header->sequence_num, &message[new_offset], 4, &added_bytes);
    new_offset += added_bytes;

    *written_bytes = new_offset - *written_bytes;

    return ELI_STATUS__OK;
}


void write_ELI_platform_msg(uint32_t ELI_platform_ID,
                            unsigned char* buffer,
                            uint32_t offset,
                            uint32_t pf_msg_type,
                            uint32_t field,
                            bool has_field){

    ECOA__uint32 written_bytes = 0;
    if (has_field){
        serialize_ECOA__uint32(field, &buffer[offset + LDP_ELI_HEADER_SIZE], 4, &written_bytes);
    }

    // write ELI header
    ldp_ELI_header header = {LDP_ELI_VERSION,
                               LDP_ELI_PLATFORM_MNG,
                               ELI_platform_ID,
                               pf_msg_type,
                               written_bytes,
                               0x0};

    ldp_write_ELI_header(&header, buffer, offset, &written_bytes);
}
