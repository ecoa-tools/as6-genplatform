/**
* @file ldp_request_response.h
* @brief ECOA request/response functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_REQUEST_RESPONSE_H
#define _LDP_REQUEST_RESPONSE_H
#include <stdbool.h>
#include <stdint.h>
#include <apr_thread_mutex.h>
#include <apr.h>

#include "ldp_list.h"
#include "ECOA.h"
#include "ldp_time_manager.h"
#include "ldp_status_error.h"
 //#include "ldp_mod_container_util.h"
//#include "ldp_structures.h"

typedef struct ldp_dyn_trigger_context_t ldp_dyn_trigger_context; //!< define in structures.h
// typedef struct ldp_mod_operation ldp_mod_operation;

//! type client or server of a request
typedef enum ldp_req_connection_type{
	LDP_REQUEST_MODULE,
	LDP_REQUEST_LOCAL_SOCKET,
	LDP_REQUEST_EXTERNAL
}ldp_req_connection_type;

//! structure for received RR which the answer must be sent
typedef struct ldp_req_received_t{
	ldp_req_connection_type connection_type; //!< nature of the client ptr: module FIFO, local socket or ELI socket
	ECOA__uint32 ID; //!< unique ID of the request received
	ECOA__uint32 client_req_ID; //!< unique ID send by client
	uint32_t client_op_id; //!< operation id of the request_response to send
	uint32_t client_sequence_num; //!< sequence number from client (for ELI message). For ldp, it is the client module ID.
	void* client_ptr; //!< pointer to client: module context pointer or socket interface (depends on the connection type)
	bool is_synchrone;//!< the server module can unlock mutex client when the response is sent
	bool is_free; //!< True if this strcuture is not used
}ldp_req_received;

//! structure for sent RR which the answer is on standby
typedef struct ldp_req_sent{
	ECOA__uint32 ID; //!< unique ID of the request sent
	ldp_req_connection_type connection_type; //!< nature of the server ptr: module FIFO, local socket or ELI socket
	ldp__timestamp timeout;//!< response should arrived BEFORE this timestamp
	uint32_t resp_op_id; //!< ID of this operation
	uint32_t resp_op_index; //!< operation index in sender. (ie: pool index in FIFO manager)
	bool resp_op_activating; //!< True if response is an activating operation. (False for synchronous RR to avoid deadlock)
	bool is_synchrone;//!< tcp router can unlock mutex client when the response is received
	bool is_free; //!< True if this strcuture is not used
}ldp_req_sent;

//! struture for sent and received RR
typedef struct ldp_request_response{
	int num_of_RR_op; //!< number of RR operation. size of the array current_RR_number
	int* current_RR_number; //!< current number of concurrent request, retrieved by index

	ldp_list req_received_list; //!< list of received requests that are requiered to send a response
	ldp_list req_sent_list; //!< list of sent requests that are waitting for a response
	ECOA__uint32 ID_generator; //!< to generate an unique ID
	apr_thread_mutex_t* mutex; //!< protect this structure
	ldp_dyn_trigger_context* trig_ctx; //!< context of the RR dynamic trigger context thread (used for RR timeout)
}ldp_request_response;


/**
 * @brief      Initialize request_response structure : allocate memory, initialize lists and mutex
 *
 * @param      req_resp       The request_response structure to init
 * @param[in]  req_recv_size  The maximum number of received request that can be managed by module
 * @param[in]  req_sent_size  The maximum number of sent request that can be managed by module
 * @param[in]  num_of_RR_op   The number of different RR operations
 * @param      mp             APR memory pool
 */
void ldp_init_request_response(ldp_request_response* req_resp, int req_recv_size, int req_sent_size, int num_of_RR_op, apr_pool_t* mp);

ldp_status_t ldp_add_req_received(ldp_request_response* req_resp,
									  ECOA__uint32* ID_ptr,
									  ldp_req_connection_type connection_type,
									  uint32_t client_sequence_num,
									  void* client_ptr,
									  uint32_t op_id,
									  ECOA__uint32 req_ID,
									  bool is_synchrone);

ldp_status_t ldp_add_req_sent(ldp_request_response* req_resp,
								  ldp_req_connection_type connection_type,
								  uint32_t op_id,
								  uint32_t op_index,
								  ECOA__uint32* ID_ptr,
								  bool is_synchrone,
								  bool activating_op,
								  ldp__timestamp* timeout);

ldp_req_received* ldp_find_req_received_no_MT(ldp_request_response* req_resp,
                                                  ECOA__uint32 ID, ldp_node** node_found);
ldp_req_received* ldp_find_req_received(ldp_request_response* req_resp, int ID, ldp_node** node_found);
ldp_req_sent* ldp_find_req_sent(ldp_request_response* req_resp, int ID, ldp_node** node_found);

/**
 * @brief      Determines if a request is out of date
 *
 * @param      timeout  The timeout of the request
 *
 * @return     True if request is out of date, False otherwise.
 */
int ldp_is_request_timeout(ldp__timestamp* timeout);

void ldp_free_req_received(ldp_request_response* req_resp, ldp_node* node);
void ldp_free_req_sent(ldp_request_response* req_resp, ldp_node* node);

/**
 * @brief      Clean request response structure: cclean lists and reinitialize current_RR_number array
 *
 * @param      req_resp  The request response structure
 */
void ldp_request_response_clean(ldp_request_response* req_resp);

/**
 * @brief      find a request response and remove it from the list
 *
 * @param      req_resp     The request response structure
 * @param[in]  ID           The ID of the request
 * @param[in]  is_req_sent  Indicates if it is a request sent or a request received
 */
void ldp_find_and_clean(ldp_request_response* req_resp,  int ID, bool is_req_sent);

/**
 * @brief      destroye and free memory
 *
 * @param      req_resp  The request response structure
 */
void ldp_request_response_destroy(ldp_request_response* req_resp);


#endif /* _LDP_REQUEST_RESPONSE_H */

#ifdef __cplusplus
}
#endif
