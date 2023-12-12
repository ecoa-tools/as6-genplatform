/**
* @file ldp_network.h
* @brief ECOA ldp network functions
*        This file contains functions for
* 	     - create and connect sockets
*        - send or read sockets
*        - launch component and father servers
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_NETWORK_H
#define _LDP_NETWORK_H

#include <stdbool.h>

#include <apr_poll.h>
#include "ldp_log_platform.h"
#include "ldp_status_error.h"
#include "apr_thread_mutex.h"
#include "ldp_launcher.h"
#include "ldp_fifo_manager.h"
#include "ldp_structures.h"

#include "ldp_udp.h"
#if !USE_UDP_PROTO
#include "ldp_tcp.h"
#endif
#include "ldp_multicast.h"


#define LDP_ID_START_MOD 0 //!< synchronisation message to make component start all modules
#define LDP_ID_INIT_MOD 1 //!< synchronisation message to make component initialize all modules
#define LDP_ID_CLIENT_READY 2 //!< synchronisation message to notify father that all components are ready
#define LDP_ID_CLIENT_INIT 3 //!< synchronisation message to notify father that all components are initialized
#define LDP_ID_KILL 4 //!< synchronisation message to kill all components
#define LDP_ID_MSG 5 //!< normal message to route to module
#define LDP_ID_SYNC 6 //!<message with further details
#define LDP_ID_CLIENT_FAULT_ERROR 7 //!< synchronisation message to notify father to call fault handler
#define LDP_ID_SHUTDOWN 8 //!< synchronisation message to shutdown all components

#define LDP_OP_ID_SIZE (4) //!< size of an operation ID
#define LDP_HEADER_TCP_SIZE (8 + LDP_OP_ID_SIZE) //!< size of an IP message header: 0xEC0A + param_size + op_ID
#define LDP_ELI_HEADER_SIZE (20) // TODO do it in multicast.h with the right size of an ELI HEADER
#define LDP_FAULT_ERROR_MSG_SIZE (17) // size of the msg used to notify fault error to father


//typedef struct ldp_fifo_manager_t ldp_fifo_manager; //!< define in ldp_fifo_manager.h
typedef struct supervision_struct_t supervision_struct; //!< define in ldp_structures.h
typedef struct ldp_id_descriptor_t ldp_id_descriptor; //!< define in ldp_structures.h
typedef struct ldp_id_identifier_struct_t ldp_id_identifier_struct; //!< define in ldp_structures.h
typedef struct ldp_fifo_manager_t ldp_fifo_manager; //!<

typedef enum {
	PROCESS_RUNNING,
	PROCESS_STOPPED
} ldp_process_state ;

typedef struct {
	int pid;
	apr_exit_why_e exitwhy;
	int exitcode;
} ldp_process_exit_infos;

typedef struct ldp_process_infos_t {
    apr_proc_t proc;
    char* prog_names;
    ldp_process_exit_infos proc_exit_infos; 
    apr_procattr_t* procattr;
    char** prog_argv;
    ldp_process_state state;
    bool pending_action;
} ldp_process_infos;

typedef enum{
	LDP_LOCAL_IP,//!< local socket. UDP or TCP (if macro USE_UDP_PROTO is defined or not)
	LDP_ELI_MCAST//!<  external socket. multical UD. Use for ELI connection
}ldp_interface_type;

//! socket information structure
typedef struct ldp_tcp_info{
	int port; //!< socket port
	char* addr; //!< socket address
	int msg_buffer_count; //!< only used in UDP, number of buffers used to read on socket
	// bool ELI_socket; //!< true if it is a ELI socket
	bool is_server2; //!< TODO remove ?
}ldp_tcp_info;

#if USE_UDP_PROTO
typedef struct ldp_interface_udp ldp_inter_local; //!< udp interface
#else
typedef struct ldp_interface_tcp ldp_inter_local; //!< tcp interface
#endif

//! network interface with other processes or platforms
typedef struct ldp_interface_ctx{
	ldp_interface_type type; //!< type of interface : local or multicast socket
	ldp_tcp_info info_r; //!< IP information of a read socket: address, port, ...
	ldp_tcp_info info_s; //!< IP information of a send socket: address, port, ... . Used by ELI only TODO: remove it -not used!!!
	union{
		ldp_inter_local local; //!< local platform socket : TCP or UDP (depends of compilation option).
		ldp_inter_mcast mcast; //!< external multicast socket with an other platform
	}inter; //!< interface: local(tcp or udp) or external (udp multicast)
}ldp_interface_ctx;

//! structure for launching modules thread of the main process
typedef struct launching_thread_params_t {
    ldp_logger_platform* logger_PF_t;
    ldp_interface_ctx* interface_ctx_array_t;
    int client_num_t;
    char* path_t;
    ldp_id_identifier_struct* ldp_id_identifier_t;
    apr_thread_t** launch_thread_ptr;
    char* name;
} launching_thread_params;


#if USE_UDP_PROTO
typedef struct net_data_w_udp net_data_w; //!< define in ldp_udp.h
#else
typedef struct net_data_w net_data_w; //!< define in ldp_udp.h or in ldp_tcp.h
#endif

typedef struct ldp_PDomain_ctx_t ldp_PDomain_ctx; //!< define in ldp_structures.h

typedef struct ldp_fault_handler_context_t ldp_fault_handler_context; //!< define in <platform_name>_fault_handler.h

//! type of function for fault handler error notification
typedef void (*fault_handler_fct)(ldp_fault_handler_context* context, ECOA__error_id error_id, const ECOA__global_time timestamp,
                      ECOA__asset_id asset_id, ECOA__asset_type asset_type, ECOA__error_type error_type, ECOA__uint32 error_code);
//! platform state
typedef enum ldp_platform_state{
    ELI_PF_DOWN    = 0,
    ELI_PF_UP      = 1,
    ELI_PF_UNKNOWN = 2,
}ldp_platform_state;

//! describe a connected platform
typedef struct ldp_platform_info{
	uint32_t ELI_platform_ID;              //!< logical platform ID
	ldp_platform_state state;			   //!< current state
	ldp_interface_ctx* sending_interface; //!< interface to begin ELI-startup sequence
}ldp_platform_info;

//! main process context
typedef struct ldp_Main_ctx_t{
	apr_pool_t* mem_pool; //!< apr memory pool
	int PD_number;//!< number of protection domains
	ldp_logger_platform* logger_PF; //!< logger
    ldp_fault_handler_context* fault_handler_context; //!< structure for fault handler
	fault_handler_fct fault_handler_function_ptr; //!< function pointer to a specific function to route new tcp messages read on sockets
	ECOA__error_id fault_handler_error_id; //!< Fault Handler error unique ID
    ldp_interface_ctx* interface_ctx_array; //!< array of interfaces ctx

	supervision_struct* superv_tools; //!< structure for supervisor tools
	int nb_init_clients;//!< current number of client that are in INITIALIZED state
	int nb_ready_clients;//!< current number of client that are in READY state

	// ELI
	uint32_t ELI_platform_ID;                    //!< ELI logical ID of the current Platform
	uint32_t mcast_reader_interface_num;         //!< number of read multicast interface
	ldp_interface_ctx* mcast_reader_interface; //!< array of read multicast interface

	uint32_t mcast_sender_interface_num;        //!< number of sending multicast interface
	ldp_interface_ctx* mcast_sender_interface;//!< array of sending multicast interface

	uint32_t connected_platform_num;         //!< number of connected platforms
	ldp_platform_info* connected_platforms;//!< array of information about connected platforms
    ldp_process_infos* pd_processes_array; //!< array of information about protected domain processes
}ldp_Main_ctx;

/**
 * @brief      writter header of a message in buffer
 *
 * @param      buffer      The buffer to write
 * @param[in]  param_size  The parameters size
 * @param[in]  op_ID       The operation ID
 */
void ldp_written_IP_header(char* buffer, uint32_t param_size, uint32_t op_ID);

/**
 * @brief      write the error in a message buffer
 *
 * @param      buffer      The buffer to write
 * @param      asset_id    The asset ID
 * @param      asset_type  The asset type
 * @param      error_type  The error type
 * @param      error_code  The error code
 */
void ldp_written_IP_fault_error(char* buffer, 
                                  ECOA__asset_id asset_id,
                                  ECOA__asset_type asset_type,
                                  ECOA__error_type error_type,
                                  ECOA__uint32 error_code);

/**
 * @brief      read the error in a message buffer
 *
 * @param      buffer      The buffer to write
 * @param      asset_id    The asset ID
 * @param      asset_type  The asset type
 * @param      error_type  The error type
 * @param      error_code  The error code
 */
void ldp_read_IP_fault_error(char* buffer, 
                               ECOA__asset_id* asset_id,
                               ECOA__asset_type* asset_type,
                               ECOA__error_type* error_type,
                               ECOA__uint32* error_code);

/**
 * @brief      write the operation ID in a message
 *
 * @param      buffer  The buffer that contains the message
 * @param[in]  op_ID   The operation ID
 */
void ldp_written_IP_op_ID(char* buffer, uint32_t op_ID);


/**
 * @brief      Read and check header of an IP message
 *     - check if message begin by 0xECOA
 *     - retrieve parameters size and check if this size is not too big
 *     - retrieve opeartion ID
 *
 * @param      ctx         The Protection Domain context
 * @param      buffer      The buffer to read
 * @param      op_ID       The operation id
 * @param      param_size  The parameter size
 *
 * @return     true if header is correct, or false in case of error
 */
bool ldp_read_IP_header(ldp_PDomain_ctx* ctx, char* buffer, uint32_t* op_ID, uint32_t* param_size);

/**
 * @brief      Send message to all clients (on all sockets in the poll of file
 *             descriptor)
 *
 * @param[in]  err        The error code
 * @param      logger_PF  The plateform logger
 * @param      ip_info   The ip information
 */
void ldp_IP_print_err(apr_status_t err, ldp_logger_platform* logger_PF, ldp_tcp_info* ip_info);

/**
 * @brief      Call fault handler notification hook
 *
 * @param      ctx   The main context
 * @param      asset_id    the id of the asset linked to the error
 * @param      asset_type  the type of the asset linked to the error
 * @param      error_type  the type of the error raised
 * @param      error_code  extra error code passed by the asset
 *
 */
void ldp_fault_error_notification(ldp_Main_ctx* ctx,
                                    ECOA__asset_id asset_id,
                                    ECOA__asset_type asset_type,
                                    ECOA__error_type error_type,
                                    ECOA__uint32 error_code);

/**
 * @brief      send fault error message to main process
 *
 * @param      ctx   The component context
 * @param      asset_id    the id of the asset linked to the error
 * @param      asset_type  the type of the asset linked to the error
 * @param      error_type  the type of the error raised
 * @param      error_code  extra error code passed by the asset
 *
 * @return     ldp status
 */
ldp_status_t ldp_send_fault_error_to_father(ldp_PDomain_ctx* ctx,
                                                ECOA__asset_id asset_id,
                                                ECOA__asset_type asset_type,
                                                ECOA__error_type error_type,
                                                ECOA__uint32 error_code);

ldp_status_t write_msg(ldp_logger_platform* logger_PF,
							ldp_interface_ctx* interface_ctx,
							uint32_t msg_ID);

/**
 * @brief      Consume a message in the main process
 *
 * @param      buf                  The buffer that contains the message
 * @param      ctx					main process context
 * @param      read_interface_ctx   The context of the read interface
 * @param      interface_ctx_array  The array of all interfaces of the process
 *
 * @return     LDP_ERROR if the main process should stop, or LDP_SUCCESS
 */
ldp_status_t main_proc_consume_msg(ldp_Main_ctx* ctx,
							char* buf,
                            const apr_pollfd_t* fd,
							ldp_interface_ctx* read_interface_ctx,
							ldp_interface_ctx* interface_ctx_array);

/**
 * @brief      Consume a message by a protection domain process
 *
 * @param      ctx                  Protection Domain context
 * @param      read_buffer          The buffer that contains the message
 * @param      param_size           main process context
 * @param      op_ID                operation ID of the message
 * @param      interface_ctx        The context of the read interface
 *
 * @return     LDP_ERROR if the process should stop, or LDP_SUCCESS
 */
ldp_status_t domain_proc_consume_msg(ldp_PDomain_ctx* ctx,
							char* read_buffer,
							uint32_t param_size,
							uint32_t op_ID,
							ldp_interface_ctx* interface_ctx);
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
ldp_status_t ldp_IP_write(ldp_interface_ctx* sock_interface, char* msg, int length, net_data_w* data_w);


/**
 * @brief      Read on a socket
 *              - In TCP : read the socket
 *              - In UDP : read a packet on the socket and update the interface
 *                context
 * @note       define in udp/ or in tcp/
 *
 * @param      sock_interface  The socket interface to read
 * @param      msg             The message that will be read (only use for TCP)
 * @param      len             On entry : the number of bytes to read. On exit :
 *                             the number of bytes read
 *
 * @return     LDP_SUCCESS if success or an APR error code
 */
ldp_status_t ldp_IP_read(ldp_interface_ctx* sock_interface, char* msg, apr_size_t* len);

/**
 * @brief      server for a Protection Domain
 * @note       define in udp/ or in tcp/
 *
 * @param      ctx   The Protection Domain context
 */
void ldp_start_comp_server(ldp_PDomain_ctx* ctx);

/**
 * @brief      server for the main process
 * @note       define in udp/ or in tcp/
 *
 * @param      ctx                  main process context
 * @param      interface_ctx_array  array of network interface interfaces between local Protections Domains or other platforms
 * @param      PF_links_num         number of PF links
 */
void ldp_start_father_server(ldp_Main_ctx* ctx, ldp_interface_ctx* interface_ctx_array, uint32_t PF_links_num);

ldp_status_t comp_server_push_fifo(ldp_PDomain_ctx* comp_ctx,int op_ID, ldp_fifo_manager* mod_fifo_m, char* mod_name, ECOA__uint16 mod_ID);
void comp_server_broadcast(ldp_PDomain_ctx* comp_ctx, uint32_t msg_ID);
void find_dest_mod_and_send(ldp_PDomain_ctx* ctx, uint16_t ID_mod, uint32_t operation_ID);
void find_dest_mod_by_comp_and_send(ldp_PDomain_ctx* ctx, char* component_name, uint32_t operation_ID);

/**
 * @brief add socket read to the poolset
 *
 * @param    pollset         poolset to complete
 * @param    sock_interface  interface of the read socket
 * @param    read_socket     read socket to add in the poolset
 * @param    mem_pool        APR memory pool
 **/
void ldp_add_pollset(apr_pollset_t *pollset,
					   ldp_interface_ctx* sock_interface,
					   apr_socket_t* read_socket,
					   apr_pool_t* mem_pool);

#endif /* _LDP_NETWORK_H */

#ifdef __cplusplus
}
#endif
