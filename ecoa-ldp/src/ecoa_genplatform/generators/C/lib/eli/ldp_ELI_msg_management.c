/**
* @file ldp_ELI_msg_management.c
* @brief ECOA ELI management functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ECOA.h"
#include "ECOA_simple_types_serialization.h"
#include "ldp_network.h"
#include "ldp_ELI_msg_management.h"
#include "ldp_ELI_udp.h"
#include <assert.h>
#include "ldp_structures.h"
#include "ldp_VD.h"

#define LDP_ELI_MAIN_SERVER_CHANNEL_ID (0)
static ldp_platform_info* find_connected_platform(ldp_Main_ctx* ctx, uint32_t platform_ID){
    ldp_platform_info* connected_PF = NULL;
    for(int i=0; i< ctx->connected_platform_num;i++){
        if(ctx->connected_platforms[i].ELI_platform_ID == platform_ID){
            connected_PF = &ctx->connected_platforms[i];
            break;
        }
    }
    return connected_PF;
}

ldp_ELI_status ldp_ELI_UDP_startup_sequence(ldp_Main_ctx* ctx){
    ldp_ELI_status ret = ELI_STATUS__OK;
    unsigned char msg[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE + 4];

    // send UP to every platforms in DOWN state
    uint64_t msg_size = LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE + 4;
    int i = 0;
    for (i=0; i<ctx->connected_platform_num; i++){
        if (ctx->connected_platforms[i].state == ELI_PF_DOWN){
            ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", ctx->logger_PF,
                  "[MAIN] Platform ID '%i' is down. Send LDP_ELI_PLATFORM_STATUS\n",
                  ctx->connected_platforms[i].ELI_platform_ID);

            write_ELI_UDP_platform_message(ctx->ELI_platform_ID,
                                           ctx->connected_platforms[i].sending_interface->inter.mcast.UDP_current_PF_ID,
                                           LDP_ELI_MAIN_SERVER_CHANNEL_ID,
                                           msg, LDP_ELI_PLATFORM_STATUS, ELI_PF_UP, true);

            ret = ldp_mcast_send(&ctx->connected_platforms[i].sending_interface->inter.mcast, (char*)msg,
                             &msg_size, ctx->logger_PF);
            if (ret != APR_SUCCESS){
                ret = ELI_STATUS__ERROR;
                assert(0);
            }
        }else{
            // nothing to do
        }
    }

    return ELI_STATUS__OK;
}


static ldp_ELI_status received_platform_status_msg(ldp_Main_ctx* ctx,
                                                     ldp_ELI_header* ELI_header,
                                                     char* msg_payload){
    ldp_ELI_status ret = ELI_STATUS__OK;
    //check msg size
    if (ELI_header->payload_size < 4){
        // too little msg
        ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
                            "[MAIN] Received PLATFORM_STATUS: msg too little");
        ret = ELI_STATUS__ERROR;
    }else{
        // read new status
        ldp_platform_state new_connected_PF_state = ELI_PF_UNKNOWN;
        deserialize_ECOA__uint32(&new_connected_PF_state, msg_payload, 4);

        // find connected PF status
        ldp_platform_info* connected_PF = find_connected_platform(ctx, ELI_header->platform_ID);

        if(connected_PF == NULL ){
            // PF not connected
            ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", ctx->logger_PF,
                            "[MAIN] Platform ID '%i' is not connected", ELI_header->platform_ID);
        }else{
            if(connected_PF->state == ELI_PF_DOWN && new_connected_PF_state == ELI_PF_UP){
                // down to up
                connected_PF->state = new_connected_PF_state;
                ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", ctx->logger_PF,
                            "[MAIN] Connection of Platform ID '%i'", ELI_header->platform_ID);

                unsigned char buffer[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE + 4];
                uint64_t msg_size = LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE + 4;

                // send PF_state
                write_ELI_UDP_platform_message(ctx->ELI_platform_ID,
                                                connected_PF->sending_interface->inter.mcast.UDP_current_PF_ID,
                                                LDP_ELI_MAIN_SERVER_CHANNEL_ID,
                                                buffer, LDP_ELI_PLATFORM_STATUS, ELI_PF_UP, true);
                ldp_mcast_send(&connected_PF->sending_interface->inter.mcast, (char*)buffer,
                             &msg_size, ctx->logger_PF);

                // send VD_PULL
                write_ELI_UDP_platform_message(ctx->ELI_platform_ID,
                                                connected_PF->sending_interface->inter.mcast.UDP_current_PF_ID,
                                                LDP_ELI_MAIN_SERVER_CHANNEL_ID,
                                                buffer, LDP_ELI_VERSIONED_DATA_PULL, 0xFFFFFFFFU, true);

                ldp_mcast_send(&connected_PF->sending_interface->inter.mcast, (char*)buffer,
                             &msg_size, ctx->logger_PF);

            }else if(connected_PF->state == ELI_PF_UP && new_connected_PF_state == ELI_PF_DOWN){
                // up to down
                connected_PF->state = new_connected_PF_state;
                ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", ctx->logger_PF,
                            "[MAIN] Platform ID '%i' is unconnected", ELI_header->platform_ID);
            }else if(connected_PF->state == new_connected_PF_state){
                // no changement : nothing to do
            }else{
                // invalid state
                ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", ctx->logger_PF,
                                    "[MAIN] Received an invalid state from PF '%i'", ELI_header->platform_ID);
            }
        }
    }

    return ret;
}

static ldp_ELI_status received_platform_status_request_msg(ldp_Main_ctx* ctx,
                                         ldp_ELI_header* ELI_header){
    ldp_platform_info* connected_PF = find_connected_platform(ctx, ELI_header->platform_ID);
    if(connected_PF == NULL ){
        // PF not connected
        ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", ctx->logger_PF,
                        "[MAIN] Platform ID '%i' is not connected", ELI_header->platform_ID);
    }else{
        unsigned char buffer[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE];
        uint64_t msg_size = LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE;

        // send PF_state
        write_ELI_UDP_platform_message(ctx->ELI_platform_ID,
                                       connected_PF->sending_interface->inter.mcast.UDP_current_PF_ID,
                                       LDP_ELI_MAIN_SERVER_CHANNEL_ID,
                                       buffer, LDP_ELI_PLATFORM_STATUS, ELI_PF_UP, true);
        ldp_mcast_send(&connected_PF->sending_interface->inter.mcast, (char*)buffer,
                     &msg_size, ctx->logger_PF);
    }

    return ELI_STATUS__OK;
}

ldp_ELI_status ldp_ELI_UDP_main_read_msg(ldp_Main_ctx* ctx, ldp_interface_ctx* read_interface_ctx){
    char buffer[128];
    uint64_t buffer_size = 128;
    ldp_status_t ret;
    ECOA__uint32 read_bytes;
    ret = ldp_mcast_read(&read_interface_ctx->inter.mcast,
                              buffer,
                              &buffer_size,
                              ctx->logger_PF);

    // read UDP header
    ldp_ELI_UDP_header UDP_header;
    ldp_read_ELI_UDP_header(&UDP_header, (unsigned char*) buffer, 0, &read_bytes);

    // TODO call ldp_ELI_udp_msg_defragment

    // main never need partial message
    if( UDP_header.msg_part != LDP_ELI_FULL){
      return ELI_STATUS__INCOMPLETE_MSG;
    }

    /////////////////////////////////////////
    // if message is completed
    ldp_ELI_header ELI_header;

    // read ELI HEADER
    ret = ldp_read_ELI_header(&ELI_header, (unsigned char*) buffer, LDP_ELI_UDP_HEADER_SIZE, &read_bytes);
    if (ret != ELI_STATUS__OK){
        ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
            "[MAIN] invalid ELI header message on (%s:%i)",
            read_interface_ctx->info_r.addr, read_interface_ctx->info_r.port);

        return ret;
    }
    read_bytes += LDP_ELI_UDP_HEADER_SIZE;

    // Check domain:
    if (ELI_header.domain == LDP_ELI_PLATFORM_MNG){
        switch (ELI_header.msg_ID){
        case LDP_ELI_PLATFORM_STATUS:
            ret = received_platform_status_msg(ctx, &ELI_header, &buffer[read_bytes]);
            break;
        case LDP_ELI_PLATFORM_STATUS_REQUEST:
            ret = received_platform_status_request_msg(ctx, &ELI_header);
            break;
        case LDP_ELI_VERSIONED_DATA_PULL:
            // nothing to do in main processus
            break;
        case LDP_ELI_UNKNOWN_OPERATION:
            ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
                "[MAIN] Platform error with an unknown operation (%s:%i)",
                read_interface_ctx->info_r.addr, read_interface_ctx->info_r.port);
            ret = ELI_STATUS__ERROR;
            // nothing to do ?
            break;
        case LDP_ELI_RESERVED:
        default:
            //error
            ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
                "[MAIN] Platform message error : used of a reserved message ID '%i' on (%s:%i)",
                ELI_header.msg_ID, read_interface_ctx->info_r.addr, read_interface_ctx->info_r.port);
            ret = ELI_STATUS__ERROR;
            break;
        }
    }else if(ELI_header.domain == LDP_ELI_SERVICE_OP){
        // do nothing
    }else{
        //error
        ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
            "[MAIN] domain message is neither a platform message nor a service operation: '%i' on (%s:%i)",
            ELI_header.domain, read_interface_ctx->info_r.addr, read_interface_ctx->info_r.port);
        ret = ELI_STATUS__ERROR;
    }

    return ret;
}


///////////// Protection Domain functions

static ldp_ELI_status PD_proc_ELI_management_msg(ldp_PDomain_ctx* ctx, ldp_interface_ctx* read_interface_ctx,
                                            ldp_ELI_header* ELI_header, unsigned char* payload){
    ldp_status_t ret = ELI_STATUS__OK;
    switch (ELI_header->msg_ID){
        case LDP_ELI_PLATFORM_STATUS:
        case LDP_ELI_PLATFORM_STATUS_REQUEST:
            // nothing to do in protection domain processus
            break;
        case LDP_ELI_VERSIONED_DATA_PULL:
            // TODO received DATA PULL
          {
            ECOA__uint32 VD_ID = 0x0;
            deserialize_ECOA__uint32(&VD_ID, payload, 4);
            ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "VD data pull recevied. ID=%i", VD_ID);

            ECOA__boolean8 push_something = ECOA__FALSE;

            for (int i=0; i<ctx->num_VD_repo; i++){
              push_something |= ldp_push_VD_ELI(ctx,  &ctx->VD_repo_array[i], ELI_header->platform_ID, VD_ID);
            }

            if(push_something == ECOA__FALSE){
              ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF, "Nothing to push after VD PULL ID=%i", VD_ID);
              // nothing to psuh (no VD or invalid ID)
              // ldp_interface_ctx* response_interface = read_interface_ctx->inter.mcast.
              // unsigned char buffer[LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE + 4];
              // uint64_t msg_size = LDP_ELI_UDP_HEADER_SIZE + LDP_ELI_HEADER_SIZE + 4;
              // write_ELI_UDP_platform_message(ctx->ELI_platform_ID,
              //                                response_interface->inter.mcast.PF_links_ctx[0].UDP_current_PF_ID,
              //                                buffer, LDP_ELI_UNKNOWN_OPERATION, VD_ID, true);
              // ldp_mcast_send(&response_interface->inter.mcast, (char*)buffer, &msg_size, ctx->logger_PF);
            }

            break;
          }
        case LDP_ELI_UNKNOWN_OPERATION:
            // log ?
            // nothing to do ?
            break;
        case LDP_ELI_RESERVED:
        default:
            //error
            ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
                "Platform message error : used of a reserved message ID '%i' on (%s:%i)",
                ELI_header->msg_ID, read_interface_ctx->info_r.addr, read_interface_ctx->info_r.port);
            ret = ELI_STATUS__ERROR;
            break;
    }
    return ret;
}


apr_status_t ldp_ELI_UDP_PD_read_msg(ldp_PDomain_ctx* ctx,
                                         ldp_interface_ctx* interface_ctx,
                                         char* msg_buffer,
                                         uint32_t buffer_size){
  uint64_t received_bytes = buffer_size;
  apr_status_t ret;
  ret = ldp_mcast_read(&interface_ctx->inter.mcast,
              msg_buffer,
              &received_bytes,
              ctx->logger_PF);
  assert(ret == LDP_SUCCESS);

  // read UDP header
  ECOA__uint32 read_bytes;
  ldp_ELI_UDP_header UDP_header;
  ldp_read_ELI_UDP_header(&UDP_header, (unsigned char*) msg_buffer, 0, &read_bytes);
  ldp_PF_link* PF_link = ldp_mcast_find_PF_link(interface_ctx, UDP_header.platform_ID);
  if(PF_link == NULL){
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
      "No PF link found. useless message. sender_pf_udp : %i \n", UDP_header.platform_ID);
    return ELI_STATUS__OK;
  }

  ldp_ELI_UDP_channel* channel;
  ret = ldp_ELI_udp_msg_defragment(&PF_link->link_ctx,
                 &UDP_header,
                 (unsigned char*) &msg_buffer[read_bytes],
                 received_bytes - read_bytes,
                 &channel);

  if (ret == ELI_STATUS__INCOMPLETE_MSG){
    // wait next datagram
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", ctx->logger_PF,
      "message uncomplete or useless message sender_pf_udp : %i \n", UDP_header.platform_ID);
    return ELI_STATUS__OK;
  }else if(ret == ELI_STATUS__OK){
    // message FULL
    assert(channel != NULL);
  }else{
    //error
    return ret;
  }

  // if message is completed in PF_link_ctx:
  ldp_ELI_header ELI_header;

  // read ELI HEADER
  // TODO: check msg size >= ELI_HEADER_SIZE
  ret = ldp_read_ELI_header(&ELI_header,channel->buffer, 0, &read_bytes);
  assert(ret == ELI_STATUS__OK);

  // check payload message
  if (ELI_header.payload_size != channel->offset - read_bytes){
    ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
      "ELI message erro: size of payload is different than received bytes (%i/%i)(%s:%i)",
      ELI_header.payload_size, (channel->offset - read_bytes),
      interface_ctx->info_r.addr, interface_ctx->info_r.port);
    return ELI_STATUS__ERROR;
  }

  // check domain
  if (ELI_header.domain == LDP_ELI_PLATFORM_MNG){
    // process a platform-level message
    PD_proc_ELI_management_msg(ctx, interface_ctx,  &ELI_header, (unsigned char*)&channel->buffer[read_bytes]);
  }else if(ELI_header.domain == LDP_ELI_SERVICE_OP) {
    // route message to FIFO module
    ldp_interface_ctx* sender_interface = PF_link->sender_interface;
    (ctx->route_function_ptr)(ctx, ELI_header.msg_ID, (char*) &channel->buffer[read_bytes],
              ELI_header.payload_size, sender_interface, interface_ctx->info_r.port, ELI_header.sequence_num,  UDP_header.platform_ID);
  }else{
    // Error
    ldp_log_PF_log_var(ECOA_LOG_ERROR_PF,"ERROR", ctx->logger_PF,
      "domain message is neither a platform message nor a service operation: '%i' on (%s:%i)",
      ELI_header.domain, interface_ctx->info_r.addr, interface_ctx->info_r.port);
  }

  return ELI_STATUS__OK;
}


void ldp_ELI_UDP_sending_fct(void* sock_context, const unsigned char* payload, uint32_t payload_size){
  ldp_sending_fct_ctx* ctx = (ldp_sending_fct_ctx*) sock_context;
  uint64_t bytes_num = payload_size;
  ldp_mcast_send(ctx->interface,
                      (char*) payload,
                      &bytes_num,
                      ctx->logger);
}
