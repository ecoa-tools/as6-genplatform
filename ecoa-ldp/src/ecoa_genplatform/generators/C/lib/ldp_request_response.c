/**
* @file ldp_request_response.c
* @brief ECOA request/response functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_request_response.h"
#include <stdlib.h>
#include <stdint.h>
#include <apr_thread_mutex.h>
#include <apr.h>
#include "ECOA.h"
#include "ldp_list.h"
#include <stdbool.h>
#include <assert.h>
#include "ldp_time_manager.h"
#include "ldp_structures.h"
#include "ldp_dynamic_trigger.h"
#include <stdint.h>
#include "ldp_status_error.h"

/**
 * generate a request ID. This ID is unique only in module instance context
 */
static ECOA__uint32 generate_ID(ldp_request_response* req_resp){
	req_resp->ID_generator++;//SonarQube -> misra norm
	return req_resp->ID_generator;
}

static void compute_date_of_expiration(ldp__timestamp* expiration_date , ldp__timestamp* timeout_duration){
	// if second number is negatif, itmeans that timeout is infinite
	if (timeout_duration->seconds == UINT32_MAX){
		expiration_date->seconds = -1;
	}else{
		ldp_get_time(expiration_date);
		ldp_add_time(expiration_date, timeout_duration);
	}
}

void ldp_init_request_response(ldp_request_response* req_resp,
                                 int req_recv_size, int req_sent_size, int num_of_RR_op, apr_pool_t* mp){
	req_resp->ID_generator = 0x64;
	req_resp->num_of_RR_op = num_of_RR_op;
	req_resp->current_RR_number = calloc(num_of_RR_op, sizeof(int));
    int new_req_recv_size = req_recv_size;
    int new_req_sent_size = req_sent_size;

	if (req_recv_size < 2){
		new_req_recv_size = 2;
	}
	if (req_sent_size < 2){
		new_req_sent_size = 2;
	}
	ldp_init_list(&req_resp->req_received_list, new_req_recv_size, sizeof(ldp_req_received));
	ldp_init_list(&req_resp->req_sent_list, new_req_sent_size, sizeof(ldp_req_sent));
  	apr_thread_mutex_create( &req_resp->mutex,0,mp);
}

/**
 * - add request information in structure and add it in received request list
 * - generate an ID an return it in ID_ptr
 *
 * @return LDP_ERROR in case of error (most of time : if list is full) or LDP_SUCCESS
 */
ldp_status_t ldp_add_req_received(ldp_request_response* req_resp,
									  ECOA__uint32* ID_ptr,
									  ldp_req_connection_type connection_type,
									  uint32_t client_sequence_num,
									  void* client_ptr,
									  uint32_t op_id,
									  ECOA__uint32 req_ID,
									  bool is_synchrone){
	// lock mutext
	apr_thread_mutex_lock(req_resp->mutex);

	// create new object in list tail (and find memory space for this object)
	ldp_node* new_node;
	new_node = ldp_add_last(&req_resp->req_received_list);
	if(new_node == NULL){
		apr_thread_mutex_unlock(req_resp->mutex);
		return LDP_ERROR;
	}

	// fill request information
	ldp_req_received* req = (ldp_req_received*) new_node->data;

	req->ID = generate_ID(req_resp);
	req->connection_type = connection_type;
	req->client_sequence_num = client_sequence_num;
	req->client_ptr = client_ptr;
	req->client_op_id = op_id;
	req->client_req_ID=req_ID;
	req->is_synchrone=is_synchrone;

	*ID_ptr = req->ID;
	apr_thread_mutex_unlock(req_resp->mutex);
	return LDP_SUCCESS;
}

/**
 * same function that ldp_add_req_received but for sent request list
 */
ldp_status_t ldp_add_req_sent(ldp_request_response* req_resp,
								  ldp_req_connection_type connection_type,
								  uint32_t op_id,
								  uint32_t op_index,
								  ECOA__uint32* ID_ptr,
								  bool is_synchrone,
								  bool activating_op,
								  ldp__timestamp* timeout_duration){
	// compute date of expiration
	ldp__timestamp timeout;
	compute_date_of_expiration(&timeout, timeout_duration);

	// create request
	apr_thread_mutex_lock(req_resp->mutex);

	ldp_node* new_node;
	new_node = ldp_add_last(&req_resp->req_sent_list);
	if(new_node == NULL){

	apr_thread_mutex_unlock(req_resp->mutex);
		return LDP_ERROR;}

	ldp_req_sent* req = (ldp_req_sent*) new_node->data;

	req->ID = generate_ID(req_resp);
	req->connection_type = connection_type;
	req->resp_op_id = op_id;
	req->resp_op_index = op_index;
	req->is_synchrone = is_synchrone;
	req->resp_op_activating = activating_op;
	req->timeout = timeout;

	*ID_ptr = req->ID;
	apr_thread_mutex_unlock(req_resp->mutex);

	return LDP_SUCCESS;
}

ldp_req_received* ldp_find_req_received_no_MT(ldp_request_response* req_resp,
                                                  ECOA__uint32 ID, ldp_node** node_found){
	ldp_node* current_node = req_resp->req_received_list.used_list_tail;
	ldp_req_received* req = NULL;
	*node_found=NULL;

	// find ID in req_received_list
	while(current_node != NULL){
		if(((ldp_req_received*)current_node->data)->ID == ID){
			req = (ldp_req_received*)current_node->data;
			*node_found = current_node;
			break;
		}
		current_node = current_node->prev;
	}

	return req;
}
/**
 * find the received request with the good ID and return it
 * node_found : contains address of node used by the request
 * @return NULL if failed or found request.
 */
ldp_req_received* ldp_find_req_received(ldp_request_response* req_resp, int ID, ldp_node** node_found){
	apr_thread_mutex_lock(req_resp->mutex);
	ldp_req_received* req = ldp_find_req_received_no_MT(req_resp, ID, node_found);
	apr_thread_mutex_unlock(req_resp->mutex);

	return req;
}


static ldp_req_sent* ldp_find_req_sent_no_MT(ldp_request_response* req_resp,
                                                 ECOA__uint32 ID, ldp_node** node_found){
	ldp_node* current_node = req_resp->req_sent_list.used_list_tail;
	ldp_req_sent* req = NULL;
	*node_found=NULL;
	// find ID in req_sent_list
	while(current_node != NULL){
		if(((ldp_req_sent*)current_node->data)->ID == ID){
			req = (ldp_req_sent*)current_node->data;
			*node_found = current_node;
			break;
		}
		current_node = current_node->prev;
	}

	return req;
}
/**
 * same function that ldp_find_req_received but for sent request
 */
ldp_req_sent* ldp_find_req_sent(ldp_request_response* req_resp, int ID, ldp_node** node_found){
	apr_thread_mutex_lock(req_resp->mutex);
	ldp_req_sent* req = ldp_find_req_sent_no_MT(req_resp, ID, node_found);
	apr_thread_mutex_unlock(req_resp->mutex);

	return req;
}


int ldp_is_request_timeout(ldp__timestamp* timeout){
	// if timout is negatif (no timeout)
	if((int)timeout->seconds < 0){
		return 0;
    }
	ldp__timestamp timenow;
	ldp_get_time(&timenow);

	if(ldp_time_cmp(timeout,&timenow) == 1){
		return 0;
	}else{
		return 1;
	}
}

/**
 * free node. after this call, node is put in unused_list to be reused.
 */
void ldp_free_req_received(ldp_request_response* req_resp, ldp_node* node){
	apr_thread_mutex_lock(req_resp->mutex);
	ldp_status_t ret=ldp_remove_node(&req_resp->req_received_list, node);
	assert(ret==0);
	UNUSED(ret);
	apr_thread_mutex_unlock(req_resp->mutex);
}

/**
 * free node. after this call, node is put in unused_list to be reused.
 */
void ldp_free_req_sent(ldp_request_response* req_resp, ldp_node* node){
	apr_thread_mutex_lock(req_resp->mutex);
	ldp_status_t ret=ldp_remove_node(&req_resp->req_sent_list, node);
	assert(ret==0);
	UNUSED(ret);
	apr_thread_mutex_unlock(req_resp->mutex);
}

void ldp_request_response_clean(ldp_request_response* req_resp){
	if(req_resp != NULL){
		apr_thread_mutex_lock(req_resp->mutex);
		// clean req_received_list
		ldp_clean_list(&req_resp->req_received_list);

		// clean rreq_received_list
		ldp_clean_list(&req_resp->req_sent_list);

		// current_RR_number =0
		for (int i=0; i<req_resp->num_of_RR_op; i++){
			req_resp->current_RR_number[i]=0;
		}

		apr_thread_mutex_unlock(req_resp->mutex);
	}
}


void ldp_find_and_clean(ldp_request_response* req_resp, int ID, bool is_req_sent){
	apr_thread_mutex_lock(req_resp->mutex);
	ldp_node* node;
	if (is_req_sent){
		if(ldp_find_req_sent_no_MT(req_resp, ID, &node) != NULL){
			ldp_remove_node(&req_resp->req_sent_list, node);
		}
	}else{
		if(ldp_find_req_received_no_MT(req_resp, ID, &node) != NULL){
			ldp_remove_node(&req_resp->req_received_list, node);
		}
	}
	apr_thread_mutex_unlock(req_resp->mutex);
}

void ldp_request_response_destroy(ldp_request_response* req_resp){
	free(req_resp->current_RR_number);
	ldp_destroy_list(&req_resp->req_received_list);
	ldp_destroy_list(&req_resp->req_sent_list);
}
