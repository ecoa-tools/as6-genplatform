/**
* @file ldp_fifo_elt_pool.c
* @brief ECOA fifo pool functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include "apr.h"
#include "apr_thread_mutex.h"
#include "apr_thread_cond.h"
#include "ECOA.h"
#include "ldp_status_error.h"
#include "ldp_fifo_elt_pool.h"
#include "ldp_structures.h" //for UNUSED macro



ldp_status_t ldp_element_pool_create(ldp_element_pool* element_pool,
                                         apr_pool_t* mp){
  element_pool->element_available = element_pool->element_num;
  ldp_status_t ret = LDP_SUCCESS;
  if (apr_thread_mutex_create(&element_pool->mutex, 0, mp) != APR_SUCCESS){
    ret = LDP_ERROR;
  }

  element_pool->element_array = calloc(element_pool->element_num,
                                       sizeof(ldp_element));
  for(int i=0; i<element_pool->element_num; i++){
    element_pool->element_array[i].parameters = calloc(element_pool->parameter_size,
                                                       sizeof(char));
    element_pool->element_array[i].state = LDP_ELT_FREE;
    element_pool->element_array[i].parameter_size = element_pool->parameter_size;
    element_pool->element_array[i].pool = element_pool;

  }
  return ret;
}


ldp_status_t ldp_element_pool_destroy(ldp_element_pool* element_pool){
  element_pool->element_available = 0;
  apr_status_t ret = LDP_SUCCESS;
  if (apr_thread_mutex_destroy(element_pool->mutex) != APR_SUCCESS){
    ret = LDP_ERROR;
  }

  // free memory
  for(int i=0; i<element_pool->element_num; i++){
    free(element_pool->element_array[i].parameters);
  }
  free(element_pool->element_array);
  UNUSED(ret);
  return LDP_SUCCESS;
}


ldp_element* ldp_element_pool_get(ldp_element_pool* element_pool){
  // get a free element of the pool

  if (element_pool->element_available == 0){
    // no buffer available
    return NULL;
  }

  // find a buffer available in the pool
  ldp_element* free_element = NULL;
  apr_thread_mutex_lock(element_pool->mutex);
  // TODO improve it y replacing array with 2 lists of used and unused element
  for (int i=0; i < element_pool->element_num; i++){
    if (element_pool->element_array[i].state == LDP_ELT_FREE){
      free_element = &element_pool->element_array[i];
      free_element->state = LDP_ELT_USED;
      element_pool->element_available--;
      break;
    }
  }
  apr_thread_mutex_unlock(element_pool->mutex);

  return free_element;
}


void ldp_element_pool_release(ldp_element* elt){
  // release this element
  // no need to take mutex
  elt->state = LDP_ELT_FREE;

  // update pool
  apr_thread_mutex_lock(elt->pool->mutex);
  elt->pool->element_available++;
  apr_thread_mutex_unlock(elt->pool->mutex);
}
