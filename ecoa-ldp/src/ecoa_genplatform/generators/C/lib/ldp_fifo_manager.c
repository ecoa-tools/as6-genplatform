/**
* @file ldp_fifo_manager.c
* @brief ECOA fifo manager functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_fifo_manager.h"
#include "ldp_fifo_elt_pool.h"
#include "ldp_status_error.h"
#include "ldp_fifo.h"
#include "ldp_request_response.h"
#include "ldp_structures.h"

#define LDP_ID_INITIALIZE_life   10
#define LDP_ID_KILL_life         11
#define LDP_ID_START_life        12
#define LDP_ID_STOP_life         13
#define LDP_ID_SHUTDOWN_life     14

ldp_status_t ldp_fifo_manager_create(ldp_fifo_manager* fifo_manager,
                                         apr_pool_t* mp)
{
  apr_status_t apr_val;
  ldp_status_t ldp_val = LDP_SUCCESS;

  // Initialisze FIFO:
  ldp_init_fifo(fifo_manager->fifo, mp);

  // create mutex and condition:
  apr_val = apr_thread_mutex_create(&fifo_manager->mutex, 0, mp);
  if (apr_val != APR_SUCCESS){
    ldp_val = LDP_ERROR;
  }

  apr_val = apr_thread_cond_create(&fifo_manager->activating_cond, mp);
  if (apr_val != APR_SUCCESS){
    ldp_val = LDP_ERROR;
  }

  //
  fifo_manager->activating_op_num = 0;

  // create pools:
  for(int i=0; i<fifo_manager->op_pool_num; i++){
    ldp_element_pool_create(&fifo_manager->op_element_pools[i], mp);
  }

  return ldp_val;
}

void ldp_fifo_manager_destroy(ldp_fifo_manager* fifo_manager)
{
  ldp_destroy_fifo(fifo_manager->fifo);
  free(fifo_manager->fifo);

  apr_thread_mutex_destroy(fifo_manager->mutex);
  fifo_manager->mutex = NULL;

  apr_thread_cond_destroy(fifo_manager->activating_cond);
  fifo_manager->activating_cond = NULL;

  for (int i=0; i<fifo_manager->op_pool_num; i++){
    ldp_element_pool_destroy(&fifo_manager->op_element_pools[i]);
  }
  free(fifo_manager->op_element_pools);
  fifo_manager->op_element_pools = NULL;
}


static ldp_status_t _ldp_fifo_manager_push_local(
                                              ldp_fifo_manager* fifo_manager,
                                              int op_index,
                                              uint32_t op_ID,
                                              ldp_op_type op_type,
                                              bool activating_op,
                                              uint32_t parameter_size,
                                              char* op_parameter,
                                              ECOA__uint16 mod_ID,
                                              bool push_first)
{
  //TODO check op_index ??

  ldp_status_t retval = LDP_SUCCESS;
  ldp_element* new_element = NULL;
  uint32_t new_parameter_size = parameter_size;

  // check op_index:
  if (op_index >= fifo_manager->op_pool_num){
    // invalid op_index: cannot find an element pool
    return LDP_ERROR;
  }

  // get a free element
  new_element = ldp_element_pool_get(&fifo_manager->op_element_pools[op_index]);
  if (new_element == NULL){
    // no buffer available
    return LDP_ERROR;
  }

  // fill element
  new_element->op_ID = op_ID;
  new_element->op_type = op_type;
  new_element->activating_op = activating_op;
  new_element->mod_ID = mod_ID;

  // check parameters size
  if (new_parameter_size > fifo_manager->op_element_pools[op_index].parameter_size){
    // Cannot copy all parameters in fifo elements: paramaters are too large
    retval =  LDP_ERROR; // TODO create error code
    new_parameter_size = fifo_manager->op_element_pools[op_index].parameter_size;
  }

  // copy parameters size
  if (new_parameter_size > 0 && op_parameter != NULL){
    memcpy(new_element->parameters, op_parameter, new_parameter_size);
  }
  new_element->parameter_size = new_parameter_size;

  // push element in fifo
  if (push_first){
    retval = ldp_push_first_fifo(fifo_manager->fifo, (void*)new_element);
  }else{
    retval = ldp_push_fifo(fifo_manager->fifo, (void*)new_element);
  }
  if (retval != LDP_SUCCESS){
    // fifo full
    return LDP_ERROR;
  }

  //activating operation
  if (activating_op){
    apr_thread_mutex_lock(fifo_manager->mutex);
    fifo_manager->activating_op_num++;
		apr_thread_cond_signal(fifo_manager->activating_cond);
    apr_thread_mutex_unlock(fifo_manager->mutex);
  }

  return retval;
}

ldp_status_t ldp_fifo_manager_push(ldp_fifo_manager* fifo_manager,
                                       int op_index,
                                       uint32_t op_ID,
                                       ldp_op_type op_type,
                                       bool activating_op,
                                       uint32_t parameter_size,
                                       char* op_parameter,
                                       ECOA__uint16 mod_ID){
  return _ldp_fifo_manager_push_local(fifo_manager,
                                        op_index,
                                        op_ID,
                                        op_type,
                                        activating_op,
                                        parameter_size,
                                        op_parameter,
                                        mod_ID,
                                        false);
}

ldp_status_t ldp_fifo_manager_push_first(ldp_fifo_manager* fifo_manager,
                                             int op_index,
                                             uint32_t op_ID,
                                             ldp_op_type op_type,
                                             bool activating_op,
                                             uint32_t parameter_size,
                                             char* op_parameter,
                                             ECOA__uint16 mod_ID){
  return _ldp_fifo_manager_push_local(fifo_manager,
                                        op_index,
                                        op_ID,
                                        op_type,
                                        activating_op,
                                        parameter_size,
                                        op_parameter,
                                        mod_ID,
                                        true);
}

ldp_status_t ldp_fifo_manager_pop_elt(ldp_fifo_manager* fifo_manager,
                                          ldp_element** elt){

  apr_thread_mutex_lock(fifo_manager->mutex);
  // if any activating operation in fifo: wait new operations
  if (fifo_manager->activating_op_num == 0){
    apr_thread_cond_wait(fifo_manager->activating_cond, fifo_manager->mutex);
  }

  // try to pop from fifo:
  ldp_status_t retval = ldp_pop_fifo(fifo_manager->fifo, (node*)elt);


  // update activating operation number:
  if (retval == LDP_SUCCESS){
    if((*elt)->activating_op){
      fifo_manager->activating_op_num--;
    }
  }

  // release mutex which has been lock by apr_thread_cond_wait
  apr_thread_mutex_unlock(fifo_manager->mutex);

  return retval;
}

ldp_status_t ldp_fifo_manager_release_elt(ldp_fifo_manager* fifo_manager,
                                              ldp_element* elt){
  UNUSED(fifo_manager);
  ldp_element_pool_release(elt);
  return LDP_SUCCESS;
}

static bool allowed_operation(bool start_op, ldp_element* elt, int mod_state){
	return (start_op ||
				(elt->op_ID == LDP_ID_KILL_life) || /* operation hard shutdown */
				((elt->op_ID == LDP_ID_SHUTDOWN_life) && (mod_state != IDLE))|| /* operation shutdown */
				(elt->op_ID == LDP_ID_INITIALIZE_life && mod_state == IDLE)/* operation initialisation */
			);
}

void ldp_fifo_manager_clean(ldp_fifo_manager* fifo_manager,
                              ldp_module_state mod_state,
                              ldp_request_response* req_resp){

  // need to freeze everything ??

  apr_thread_mutex_lock(fifo_manager->mutex);

	//clean fifo
	ldp_element* elt;
	ldp_status_t retval = LDP_SUCCESS;
	bool start_op = false; //boolean that indicate if a start operation is in fifo
	int current_op_num = fifo_manager->fifo->current_size;

	fifo_manager->activating_op_num = 0;
	for(int i=0; i<current_op_num; i++){
		retval = ldp_pop_fifo(fifo_manager->fifo, (node*) &elt);


		if(retval == LDP_SUCCESS){
			// remove operations if it is not an allowed operation
			if ((elt->op_ID == LDP_ID_START_life) && (mod_state == READY)){
				// re-push allowed operation
        ldp_push_fifo(fifo_manager->fifo, (void*) elt);
				start_op = true;
        fifo_manager->activating_op_num++;
			}
			else if (allowed_operation(start_op, elt, mod_state) ){
				// re-push allowed operation
        ldp_push_fifo(fifo_manager->fifo, (void*) elt);
        if (elt->activating_op){
          fifo_manager->activating_op_num++;
        }
			}else{
        // if RR_RECEIVED and req_resp != NULL
        if (elt->op_type == RR_RECEIVED){
          // RR received: remove request_received from structure req_resp
          ECOA__uint32 ID;
          memcpy(&ID, elt->parameters, sizeof(ECOA__uint32));
          ldp_find_and_clean(req_resp, ID, false);
        }

        // release element
        ldp_element_pool_release(elt);
			}
		}
	}

	apr_thread_mutex_unlock(fifo_manager->mutex);
}
