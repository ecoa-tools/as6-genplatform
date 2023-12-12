/**
* @file ldp_ELI_udp.c
* @brief ECOA ELI UDP functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <string.h>
#include <stdio.h>
#include "ECOA.h"
#include "ldp_ELI_udp.h"
#include "ECOA_simple_types_serialization.h"

void ldp_initialized_PF_link(ldp_PF_link_ctx* link_ctx){
    link_ctx->channels = calloc(link_ctx->channel_num, sizeof(ldp_ELI_UDP_channel));
    for(int i=0; i<link_ctx->channel_num; i++){
        link_ctx->channels[i].is_used = false;
        link_ctx->channels[i].channel_ID = 0;
        link_ctx->channels[i].channel_counter = 0;
        link_ctx->channels[i].offset = 0;
        link_ctx->channels[i].buffer = malloc(link_ctx->buffer_size);
    }
}

void ldp_free_PF_link(ldp_PF_link_ctx* link_ctx){
    for(int i=0; i<link_ctx->channel_num; i++){
        free(link_ctx->channels[i].buffer);
    }
    free(link_ctx->channels);
}

ldp_ELI_status ldp_read_ELI_UDP_header(ldp_ELI_UDP_header* header,
                                           ECOA__uint8* buffer,
                                           ECOA__uint32 offset,
                                           ECOA__uint32* read_bytes){


    header->UDP_version = buffer[offset] >> 6;       // read [xx......]
    header->msg_part = ( buffer[offset] >> 4) & 0x3; // read [..xx....]
    header->platform_ID = buffer[offset] & 0xF;      // read [....xxxx]

    header->channel_ID = buffer[offset+1];
    deserialize_ECOA__uint16(&header->channel_counter, &buffer[offset+2], 2);

    *read_bytes = 4;

    return ELI_STATUS__OK;
}

ldp_ELI_status ldp_write_ELI_UDP_header(ldp_ELI_UDP_header* header,
                                            ECOA__uint8* buffer,
                                            ECOA__uint32 offset,
                                            ECOA__uint32* written_bytes){

    buffer[offset] = 0;

    buffer[offset] += (ECOA__uint8)(header->UDP_version << 6);       // write 2 first bits in [xx......]
    buffer[offset] += (header->msg_part << 6) >> 2;   // write 2 first bits in [..xx....]
    buffer[offset] += (ECOA__uint8)(((ECOA__uint8)(header->platform_ID << 4)) >> 4);// write 4 first bits in [....xxxx]

    buffer[offset+1] = header->channel_ID;

    uint32_t added_bytes;
    serialize_ECOA__uint16(header->channel_counter, &buffer[offset+2], 2, &added_bytes);

    *written_bytes = 4;

    return ELI_STATUS__OK;
}

void write_ELI_UDP_header_platform_message(uint8_t UDP_platform_ID,
                                           uint8_t channel_ID,
                                           unsigned char* buffer){
    ECOA__uint32 written_bytes = 0;
    ldp_ELI_UDP_header UDP_header = {LDP_ELI_UDP_version,
                                       LDP_ELI_FULL,
                                       UDP_platform_ID,
                                       channel_ID,
                                       0};
    ldp_write_ELI_UDP_header(&UDP_header, buffer, 0, &written_bytes);
}
void write_ELI_UDP_platform_message(uint32_t ELI_platform_ID,
                                    uint8_t UDP_platform_ID,
                                    uint8_t channel_ID,
                                    unsigned char* buffer,
                                    uint32_t pf_msg_type,
                                    uint32_t field,
                                    bool has_field){

    write_ELI_UDP_header_platform_message(UDP_platform_ID, channel_ID, buffer);
    write_ELI_platform_msg(ELI_platform_ID, buffer, LDP_ELI_UDP_HEADER_SIZE,
                          pf_msg_type, field, has_field);
}

static inline ldp_ELI_status update_channel_buffer(ldp_ELI_UDP_channel* channel,
                                        unsigned char* payload,
                                        uint32_t payload_size,
                                        uint16_t channel_counter,
                                        uint32_t channel_buffer_maxsize){

    // ccheck buffer max size
    if (channel->offset + payload_size > channel_buffer_maxsize){
        // error
        // reset channel:
        channel->offset = 0;
        return ELI_STATUS__MEMORY_BUFFER_ERROR;
    }

    // update channel context
    memcpy(&channel->buffer[channel->offset], payload, payload_size);
    channel->offset += payload_size;
    channel->channel_counter = channel_counter;

    return ELI_STATUS__OK;
}

ldp_ELI_status ldp_ELI_udp_msg_defragment(ldp_PF_link_ctx* link_ctx,
                                                    ldp_ELI_UDP_header* header,
                                                    unsigned char* payload,
                                                    uint32_t payload_size,
                                                    ldp_ELI_UDP_channel** channel_to_return){

    // TODO check datagram payload size >= header payload

    // TODO : find the channel or set a new one
    ldp_ELI_UDP_channel* channel = NULL;
    *channel_to_return = NULL;
    ldp_ELI_status ret;
    for (int j=0; j<link_ctx->channel_num; j++){
        if (link_ctx->channels[j].is_used && link_ctx->channels[j].channel_ID == header->channel_ID){
            channel = &link_ctx->channels[j];
            break;
        }
    }
    if(channel == NULL)
    {
        // set a new channel
        // find free channel and set it
        for (int j=0; j<link_ctx->channel_num; j++){
            if (!link_ctx->channels[j].is_used){
                channel = &link_ctx->channels[j];
                link_ctx->channels[j].is_used = true;
                link_ctx->channels[j].channel_ID = header->channel_ID;
                link_ctx->channels[j].channel_counter = 0;
                break;
            }
        }

        if (channel == NULL){
            // no channel available
            return ELI_STATUS__NO_CHANNEL_AVAILABLE;
        }
    }

    // fill channel buffer:
    switch(header->msg_part){
        case LDP_ELI_FULL:
            channel->offset = 0;
            ret = update_channel_buffer(channel, payload, payload_size, header->channel_counter, link_ctx->buffer_size);
            if(ret == ELI_STATUS__OK){
                *channel_to_return = channel;
            }
            break;
        case LDP_ELI_BEGIN:
            channel->offset = 0;
            ret = update_channel_buffer(channel, payload, payload_size, header->channel_counter, link_ctx->buffer_size);
            if(ret == ELI_STATUS__OK){
                ret = ELI_STATUS__INCOMPLETE_MSG;
            }
            break;
        case LDP_ELI_MIDDLE:
            // check channel_counter to detect missing packets
            if(channel->channel_counter != header->channel_counter - 1){
                ret = ELI_STATUS__LOST_PACKET;
                // TODO : reset channel context ???
            }else{
                ret = update_channel_buffer(channel, payload, payload_size, header->channel_counter, link_ctx->buffer_size);
                if(ret == ELI_STATUS__OK){
                    ret = ELI_STATUS__INCOMPLETE_MSG;
                }
            }
            break;
        case LDP_ELI_END:
            // check channel_counter to detect missing packets
            if(channel->channel_counter != header->channel_counter - 1){
                ret = ELI_STATUS__LOST_PACKET;
                // TODO : reset channel context ???
            }else{
                ret = update_channel_buffer(channel, payload, payload_size, header->channel_counter, link_ctx->buffer_size);
                if(ret == ELI_STATUS__OK){
                   *channel_to_return = channel;
                }
            }
            break;
        default :
            ret = ELI_STATUS__ERROR;
            break;
    }

    return ret;
}

void ldp_ELI_udp_compute_fragment(uint32_t msg_size,
                                  uint32_t* number_fragment,
                                  uint32_t* fragment_size,
                                  uint32_t* last_fragment_size){

    if (msg_size < (LDP_ELI_UDP_MSG_MAXSIZE - LDP_ELI_UDP_HEADER_SIZE)){
        *fragment_size = 0;
        *number_fragment = 1;
        *last_fragment_size = msg_size;
    }else{
        *fragment_size = LDP_ELI_UDP_MSG_MAXSIZE - LDP_ELI_UDP_HEADER_SIZE;
        *number_fragment = msg_size / (*fragment_size);
        *last_fragment_size = msg_size % (*fragment_size);
        if(*last_fragment_size == 0){
            *last_fragment_size = *fragment_size;
        }else{
            (*number_fragment)++;
        }
    }
}

ldp_ELI_status ldp_ELI_udp_msg_fragment_and_send(void* sock_context,
                                                     const ldp_ELI_sending_fct sending_fct,
                                                     const unsigned char* msg,
                                                     uint32_t msg_size,
                                                     ECOA__uint8 platform_ID,
                                                     ECOA__uint8 channel_ID,
                                                     ECOA__uint16* channel_counter){

    uint32_t offset = 0; // offset of the next fragment to send in msg
	unsigned char buffer[LDP_ELI_UDP_MSG_MAXSIZE+LDP_ELI_UDP_HEADER_SIZE];
    ECOA__uint32 written_bytes;

    // compute fragments size
    uint32_t number_fragment = 0;
    uint32_t fragment_size = 0;
    uint32_t last_fragment_size = 0;
    ldp_ELI_udp_compute_fragment(msg_size, &number_fragment, &fragment_size, &last_fragment_size);

    // prepare UDP header
    ldp_ELI_UDP_header header = (ldp_ELI_UDP_header){LDP_ELI_UDP_version, 0, platform_ID, channel_ID, *channel_counter};

    // send every fragments with the right UDP header
    header.channel_counter++;
    if(number_fragment == 1){
        header.msg_part = LDP_ELI_FULL;
        ldp_write_ELI_UDP_header(&header, buffer, 0, &written_bytes);
        memcpy(&buffer[written_bytes], msg, last_fragment_size);
        sending_fct(sock_context, buffer, last_fragment_size + written_bytes);
    }else{
        // send first
        header.msg_part = LDP_ELI_BEGIN;
        ldp_write_ELI_UDP_header(&header, buffer, 0, &written_bytes);
        memcpy(&buffer[written_bytes], msg, fragment_size);
        sending_fct(sock_context, buffer, fragment_size + written_bytes);
        offset = fragment_size;

        // send middle fragments
        for(int i=1; i<number_fragment-1; i++){
            header.channel_counter++;
            header.msg_part = LDP_ELI_MIDDLE;
            ldp_write_ELI_UDP_header(&header, buffer, 0, &written_bytes);
            memcpy(&buffer[written_bytes], &msg[offset], fragment_size);
            sending_fct(sock_context, buffer, fragment_size + written_bytes);
            offset += fragment_size;
        }

        //send last
        header.channel_counter++;
        header.msg_part = LDP_ELI_END;
        ldp_write_ELI_UDP_header(&header, buffer, 0, &written_bytes);
        memcpy(&buffer[written_bytes], &msg[offset], last_fragment_size);
        sending_fct(sock_context, buffer, last_fragment_size + written_bytes);
    }

    // update channel counter
    *channel_counter += number_fragment;

    return ELI_STATUS__OK;
}
