/**
* @file ldp_fifo.c
* @brief ECOA fifo functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdlib.h>
#include <stdio.h>
#include "ldp_fifo.h"
#include <assert.h>

#include <apr_thread_mutex.h>
#include <apr_thread_cond.h>

#include "ldp_status_error.h"

void ldp_init_fifo(ldp_fifo* f, apr_pool_t* mp){
  assert(f->size > 0 );
  f->tail = 0;
  f->head = 0;
  f->current_size = 0;
  f->mp = mp;
  apr_thread_mutex_create( &f->mutex,0,mp);
  f->queue= calloc(f->size,sizeof(node));
}


ldp_status_t ldp_push_fifo(ldp_fifo* f, node new_element){
	apr_thread_mutex_lock(f->mutex);
  // if full
  if(f->current_size >= f->size){
	apr_thread_mutex_unlock(f->mutex);
    return LDP_ERROR;
  }

  //memcpy(&f->queue[f->head], &new_element, sizeof(ldp_element));
  f->queue[f->head] = new_element;
  f->current_size ++;

  // if first elt
  if(f->current_size == 1 ){
    f->tail = f->head ;
  }

  f->head++;

  // if end of array
  if(f->head >= f->size){
    f->head = 0;
  }

  apr_thread_mutex_unlock(f->mutex);
  return LDP_SUCCESS;
}


ldp_status_t ldp_push_first_fifo(ldp_fifo* f, node new_element){
    apr_thread_mutex_lock(f->mutex);
  // if full
  if(f->current_size >= f->size){
    apr_thread_mutex_unlock(f->mutex);
    return LDP_ERROR;
  }

  // if first elt
  if(f->current_size == 0 ){
    apr_thread_mutex_unlock(f->mutex);
    ldp_push_fifo(f, new_element);
    return LDP_SUCCESS;
  }

  f->current_size ++;
  f->tail--;

  // if end of array
  if(f->tail < 0){
    f->tail = f->size-1;
  }

  //memcpy(&f->queue[f->tail], &new_element, sizeof(ldp_element));
  f->queue[f->tail] = new_element;

  apr_thread_mutex_unlock(f->mutex);
  return LDP_SUCCESS;
}


ldp_status_t ldp_pop_fifo(ldp_fifo* f, node* elt){
  apr_thread_mutex_lock(f->mutex);

  // if empty
  if(f->current_size <= 0)  {
   apr_thread_mutex_unlock(f->mutex);
   return LDP_ERROR;
  }

  /* memcpy(elt, &f->queue[f->tail], sizeof(ldp_element)); */
  *elt = f->queue[f->tail];

  f->current_size--;
  f->tail++;

  if(f->tail >= f->size ){
    f->tail = 0;
  }

  apr_thread_mutex_unlock(f->mutex);
  return LDP_SUCCESS;
}


//! NOT IMPLEMENTED
void ldp_destroy_fifo(ldp_fifo* f){
  apr_thread_mutex_destroy(f->mutex);
  free(f->queue);
}
