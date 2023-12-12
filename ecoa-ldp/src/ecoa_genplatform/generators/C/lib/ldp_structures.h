/**
* @file ldp_structures.h
* @brief ECOA main data structures
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_STRUCTURE_H
#define _LDP_STRUCTURE_H

#include "ECOA.h"
#include "ldp_fifo.h"
#include <apr_thread_mutex.h>
#include <apr_thread_cond.h>
#include <apr_poll.h>
#include "ldp_VD.h"
#include "ldp_log.h"
#include "ldp_log_platform.h"
#include "ldp_pinfo.h"
#include "ldp_network.h"
#include "ldp_request_response.h"
#include "ldp_fifo_manager.h"
#include "ldp_state.h"

#define UNUSED(x) (void)(x)

//! for life cycle
#define LDP_ID_INITIALIZE_life   10
#define LDP_ID_KILL_life         11
#define LDP_ID_START_life        12
#define LDP_ID_STOP_life         13
#define LDP_ID_SHUTDOWN_life     14



//! struct that associates a module to its component, protection domain and id.
typedef struct ldp_id_descriptor_t {
   char* pd_name; //!< protection domain name
   char* comp_name; //!< component name
   char* mod_name; //!< module name
   uint16_t id; //!< ID of the module
} ldp_id_descriptor;

//! struct which contains the matrix of modules and their characteristics and its size
typedef struct ldp_id_identifier_struct_t {
	uint16_t size; //<! Size of the description array (number of modules)
	ldp_id_descriptor** descriptors_array; //!< matrix descripting the platform
} ldp_id_identifier_struct;

//! struct with elements to provide to the server for launching
typedef struct supervision_struct_t {
	ldp_id_identifier_struct* ldp_id_identifier; //<! Struct with all elements about the platform
	char* path_to_launcher_t; //<! Path from root to the file launcher.txt
	apr_thread_t* launch_thread_ptr; //<! Pointer to the thread for the launcher
} supervision_struct;



//typedef struct ldp_PDomain_ctx_t ldp_PDomain_ctx; //!<
typedef struct ldp_trigger_event_context_t ldp_trigger_event_context; //!<
typedef struct ldp_dyn_trigger_event_t ldp_dyn_trigger_event; //!<
  //typedef struct ldp_request_response_t ldp_request_response; //!<

typedef void* ldp_properties;//!<

typedef struct ldp_VD_reader_mng ldp_VD_reader_mng; //!<
typedef struct ldp_VD_writter_mng ldp_VD_writter_mng; //!<
typedef struct ldp_repository_VD ldp_repository_VD; //!<

//! socket information structure
typedef struct ldp_tcp_info ldp_tcp_info; //! define in ldp_network.h
//! contains information about an interface of a protection domain
typedef struct ldp_interface_ctx ldp_interface_ctx; //! define in ldp_network.h

#if USE_UDP_PROTO
typedef struct net_data_w_udp net_data_w; //!< define in ldp_udp.h
#else
typedef struct net_data_w net_data_w; //!< define in ldp_udp.h or in ldp_tcp.h
#endif

typedef struct ldp_mod_operation_map ldp_mod_operation_map; //!< define in ldp_module_container.c

//! structure for normal module
typedef struct ldp_module_context_t{
	// ----- Common part with other module type context ---- //
	char* name; //!< module instance name
	ECOA__uint16 mod_id; //!< module thread ID (unique on ECOA platform)
	net_data_w* network_write_data; //!< used by udp network to reserve a packet buffer for each component
	char* component_name; //!< component instance name
	apr_pool_t* mem_pool;//!< apr memory pool
	uint32_t msg_buffer_size; //!< size of msg buffer
	char* msg_buffer; //!< buffer which contains a message to send

	ldp_module_state state; //!< module current state (NOT USED)
	ldp_PDomain_ctx* component_ctx; //!< component context
	int operation_num; //!< size of operation_map array
	ldp_mod_operation_map* operation_map; //!< contains information about all module_container output operations (like RR and output events).

	ldp_fifo_manager* fifo_manager;//!< Manager of FIFO module
	ldp_logger_platform* logger_PF;//!< logger for platform messages

	int priority; //!< module thread priority
	cpu_mask cpu_affinity_mask; //!< cpu affinity mask of this thread
	// --------------------------------------------------- //

    // ---- specific for normal module ---- //
	ldp_logger* logger; //!< Logger for ECOA messages
	int num_reader_mng;                        //!< number of read VD manager
	ldp_VD_reader_mng* VD_reader_managers;   //!< array of read VD manager
	int num_writter_mng;                       //!< number of write VD manager
	ldp_VD_writter_mng* VD_writter_managers; //!< array of write VD manager

	ldp_request_response req_resp; //!< structure that will save information about RR sent and RR received
	apr_thread_mutex_t* wait_response; //!< mutex used to stop module thread in case of synchronous RR
	apr_thread_cond_t* condition_response; //!< condition to stop module thread in case of synchronous RR

	ldp_properties properties;//!< Structure that handles properties values for this module
	ldp_pinfo_manager pinfo_manager;//!< Strcuture that manages pinfo files
}ldp_module_context;

//! structure for trigger module
typedef struct ldp_trigger_context{
	// ---- Common part with other module type context ---- //
	char* name; //!< trigger instance name
	ECOA__uint16 mod_id; //!< module thread ID (unique on ECOA platform)
	net_data_w* network_write_data; //!< used by udp network to reserve a packet buffer for each component
	char* component_name; //!< component instance name
	apr_pool_t* mem_pool; //!< apr memory pool

	uint32_t msg_buffer_size; //!< size of msg buffer
	char* msg_buffer; //!< buffer which contains a message to send

	ldp_module_state state;//!< module current state (NOT USED)
	ldp_PDomain_ctx* component_ctx; //!< component context
	int operation_num; //!< size of operation_map array
	ldp_mod_operation_map* operation_map;//!< contains information about all output operations.

	ldp_fifo_manager* fifo_manager;//!< manager of FIFO module
	ldp_logger_platform* logger_PF;//!< logger for platform messages

	int priority; //!< module thread priority
	cpu_mask cpu_affinity_mask; //!< cpu affinity mask of this thread
	// --------------------------------------------------- //

	// ----specific for trigger module ---- //
	ldp_logger* logger;//!< Logger for ECOA messages
	pthread_barrier_t barr; //!< used during initialization to synchronized timer creations and timer startings
	int nb_trigger_event; //!< number of trigger events in trigger_events array
	ldp_trigger_event_context* trigger_events; //!< array of trigger events

}ldp_trigger_context;

//! structure for dynamic trigger module
typedef struct ldp_dyn_trigger_context_t{
	// ---- Common part with other module type context ---- //
	char* name;//!< dynamin trigger instance name
	ECOA__uint16 mod_id; //!< module thread ID (unique on ECOA platform)
	net_data_w* network_write_data; //!< used by udp network to reserve a packet buffer for each component
	char* component_name; //!< component instance name
	apr_pool_t* mem_pool; //!< apr memory pool

	uint32_t msg_buffer_size; //!< size of msg buffer
	char* msg_buffer; //!< buffer which contains a message to send

	ldp_module_state state; //!< module current state (NOT USED)
	ldp_PDomain_ctx* component_ctx; //!< component context
	int operation_num; //!< size of operation_map array
	ldp_mod_operation_map* operation_map; //!< contains only one ldp_mod_operation_map for 'out' operation

	ldp_fifo_manager* fifo_manager;//!< manager of FIFO module
	ldp_logger_platform* logger_PF;//!< logger for platform messages

	int priority; //!< module thread priority
	cpu_mask cpu_affinity_mask; //!< cpu affinity mask of this thread
	// --------------------------------------------------- //

	// ---- specific for dynamic trigger module ---- //
	int max_event_nb; //!< maximal number of waiting events
	ldp_dyn_trigger_event* trigger_event_tab; //!< array of ldp_dyn_trigger_event
	pthread_cond_t cond; //!< pthread condition to wakup trigger thread (to check expired event or to add a new one)
	pthread_mutex_t mutex; //!< mutex of the pthread condition
	int params_size; //!< size of parameters


}ldp_dyn_trigger_context;

//! type of function to route messages to modules
typedef void (*PDomain_router_fct)(ldp_PDomain_ctx* ctx, uint32_t operation_id, char* msg, int size_msg,
									ldp_interface_ctx* socket_sender, int port_nb, uint32_t ELI_sequence_num, ECOA__uint32 sender_PF_ID);

//! context of protection domains
typedef struct ldp_PDomain_ctx_t{
	char* name; //!< protection domain instance name
	apr_pool_t* mem_pool;//!< apr memory pool
	int sched_policy; //!< schedular policy of module threads (not technical threads)
	cpu_mask technical_cpu_mask; //!< cpu affinity mask for every technical threads (not module threads)
	uint32_t ELI_platform_ID;    //!< ELI logical ID of the current platform

    // tcp information
	int nb_server; //!< number of services in protection domain
	int nb_client; //!< number of references in protection domain
	int nb_client_ready; //!< used during initialization
	ldp_interface_ctx* interface_ctx_array; //!< array of interfaces ctx

	int mcast_read_interface_num; //!< number of multicast socket to listen (for ELI)
	ldp_interface_ctx* mcast_read_interface;//!< interface of multicast socket to listen (for ELI)

    // module contexts
	int nb_module;//!< number of normal modules
	ldp_module_context* worker_context; //!< array of module contexts

    // module trigger contexts
	int nb_trigger; //!< number of trigger modules
	ldp_trigger_context* trigger_context; //!< array of module trigger contexts

    // module dynamic trigger contexts
	int nb_dyn_trigger;//!< number of dynamic trigger modules
	ldp_dyn_trigger_context* dyn_trigger_context; //!< array of module dynamic trigger contexts

    //
	PDomain_router_fct route_function_ptr; //!< function pointer to a specific function to route new tcp messages read on sockets
	uint32_t msg_buffer_size; //!< size of the biggest message that the PD can handle
	char* msg_buffer;         //!< buffer which contains message to deserialized or to send (for VD push)

	// Version data struct
	int num_VD_repo; //!< number of versioned data in c
	ldp_repository_VD* VD_repo_array; //!< versioned managers array

	ldp_logger* logger;//!< Logger for ECOA messages
	ldp_logger_platform* logger_PF;//!< logger for platform messages

	apr_thread_mutex_t* state_mutex;//!< protect PD state. Can be updated by module threads
	ldp_PD_state state;//!< current PD state. Used for synchronisation with main process

	char* external_msg_buffer;         //!< buffer which contains message use by driver components
	apr_thread_mutex_t* external_mutex;//!< protect driver components buffer. Can be updated from several threads

}ldp_PDomain_ctx;


#endif /* _LDP_STRUCTURE_H */
#ifdef __cplusplus
}
#endif
