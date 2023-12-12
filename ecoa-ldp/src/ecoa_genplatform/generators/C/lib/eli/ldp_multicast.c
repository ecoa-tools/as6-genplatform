/**
* @file ldp_multicast.c
* @brief ECOA multicast functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <apr_network_io.h>
#include <apr_poll.h>
#include "ldp_network.h"
#include <assert.h>
#include "ldp_ELI_udp.h"

apr_status_t ldp_create_read_multicast_interface(ldp_inter_mcast* interface,
                                              ldp_tcp_info* ip_info,
                                              ldp_logger_platform* logger_PF,
                                              apr_pool_t *mp){
    apr_status_t ret;
    apr_sockaddr_t *socket_addr_tmp;
    interface->ip_info = ip_info;

    // read socket
    ret=apr_sockaddr_info_get(&interface->socket_addr,
                              APR_ANYADDR, APR_INET,
                              interface->ip_info->port, 0, mp);
    if (ret != APR_SUCCESS){
        return ret;
    }

    ret=apr_socket_create(&interface->socket, APR_INET, SOCK_DGRAM, APR_PROTO_UDP, mp);
    if (ret != APR_SUCCESS){
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
        return ret;
    }
    apr_socket_opt_set(interface->socket, APR_SO_REUSEADDR, 1);

    ret=apr_socket_bind(interface->socket, interface->socket_addr);
    if (ret != APR_SUCCESS){
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
        return ret;
    }

    apr_sockaddr_info_get(&socket_addr_tmp,
                              interface->ip_info->addr,
                              APR_INET,
                              interface->ip_info->port, 0, mp);
    ret = apr_mcast_join(interface->socket, socket_addr_tmp, NULL, NULL);
    if (ret != APR_SUCCESS){
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
        return ret;
    }

    ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", logger_PF, "create read multicast interface (%s:%i)",
                         ip_info->addr, ip_info->port);
    return APR_SUCCESS;
}
apr_status_t ldp_create_sent_multicast_interface(ldp_inter_mcast* interface,
                                              ldp_tcp_info* ip_info,
                                              ldp_logger_platform* logger_PF,
                                              apr_pool_t *mp){
    apr_status_t ret;
    apr_sockaddr_t *socket_addr_tmp;
    interface->ip_info = ip_info;

    ret=apr_sockaddr_info_get(&interface->socket_addr,
                              interface->ip_info->addr,
                              APR_INET,
                              interface->ip_info->port, 0, mp);

    ret=apr_socket_create(&interface->socket, APR_INET, SOCK_DGRAM, APR_PROTO_UDP, mp);
    if (ret != APR_SUCCESS){
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
        return ret;
    }
    apr_socket_opt_set(interface->socket, APR_SO_REUSEADDR, 1);

    apr_sockaddr_info_get(&socket_addr_tmp,
                              APR_ANYADDR,
                              APR_INET,
                              interface->ip_info->port, 0, mp);
    ret = apr_mcast_interface(interface->socket, socket_addr_tmp ); // enable multicast sending
    if (ret != APR_SUCCESS){
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
        return ret;
    }
    apr_mcast_loopback(interface->socket,1); // enable loop back to received local msg
    // TODO: disable it to avoid to received sending message

    ldp_log_PF_log_var(ECOA_LOG_INFO,"INFO", logger_PF,"create sent multicast interface (%s:%i)",
                         ip_info->addr, ip_info->port);
    return APR_SUCCESS;
}

apr_status_t ldp_mcast_send(ldp_inter_mcast* interface,
                      char* msg,
                      uint64_t* msg_size,
                      ldp_logger_platform* logger_PF){
    if (interface->socket == NULL){
      ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", logger_PF,
                           "multicast error (%s:%i) : socket doesn't exist",
                           interface->ip_info->addr, interface->ip_info->port);
      *msg_size = 0;
      return LDP_ERROR;
    }

    apr_status_t ret = apr_socket_sendto(interface->socket, interface->socket_addr, 0, msg, msg_size);
    if (ret != APR_SUCCESS){
        ldp_log_PF_log_var(ECOA_LOG_ERROR,"ERROR", logger_PF,"cannot send on multicast interface (%s:%i)",
                         interface->ip_info->addr, interface->ip_info->port);
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
    }
    return ret;
}

apr_status_t ldp_mcast_read(ldp_inter_mcast* interface,
                              char* msg,
                              uint64_t* msg_size,
                              ldp_logger_platform* logger_PF){

    apr_status_t ret =  apr_socket_recv (interface->socket, msg, msg_size);
    if (ret != APR_SUCCESS){
        ldp_IP_print_err(ret, logger_PF, interface->ip_info);
    }

    // TODO do something for UDP message : packets re-ordering, packet check, ELI? , ... Maybe not here
    return ret;
}


ldp_PF_link* ldp_mcast_find_PF_link(ldp_interface_ctx* interface_ctx, ECOA__uint8 UDP_connected_PF_ID){
    for(int i=0; i < interface_ctx->inter.mcast.link_num; i++){
        if (interface_ctx->inter.mcast.PF_links_ctx[i].link_ctx.UDP_connected_PF_ID == UDP_connected_PF_ID){
            return &interface_ctx->inter.mcast.PF_links_ctx[i];
        }
    }

    // no link found
    return NULL;
}
