/**
* @file ldp_fifo_manager.h
* @brief ECOA fifo manager functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_FIFO_MANAGER_H
#define _LDP_FIFO_MANAGER_H

#include <apr_thread_mutex.h>
#include "ldp_fifo.h"
#include "ldp_fifo_elt_pool.h"
#include "ldp_status_error.h"
#include "ldp_request_response.h"
#include "ldp_state.h"

  //! Manager of a module FIFO. Contains pending module operations
  typedef struct ldp_fifo_manager_t{
    ldp_fifo* fifo;                  //!< module fifo
    apr_thread_cond_t* activating_cond;//!< to block module waiting for new operation in fifo
    apr_thread_mutex_t* mutex; //!< to protect activating operation number
                               // and activation condition
    uint32_t activating_op_num;//!< current number of activating operation in fifo

    uint32_t op_pool_num;      //!< [static] number of pool
    ldp_element_pool* op_element_pools; //!< array of pool
  }ldp_fifo_manager;


  /**
   * @brief  Initialize fifo manager structure: FIFO, mutex, thread condition, pools
   *
   * @param fifo_manager  fifo manage to initialize
   * @param mp            APR memory pool
   *
   * @return  LDP_ERROR if initialisation failed
   **/
  ldp_status_t ldp_fifo_manager_create(ldp_fifo_manager* fifo_manager,
                                           apr_pool_t* mp);

  /**
   * @brief  Destroy fifo manager and clean memory used by this structure
   *
   * @param  fifo_manager
   *
   */
  void ldp_fifo_manager_destroy(ldp_fifo_manager* fifo_manager);

  /**
   * @brief  Push an operation in fifo
   *
   * @param op_index   index of operation. Correspond to the index of pool
   * @param op_ID      module ID of operation
   * @param op_type    type of operation (RR, event, ...)
   * @param activating_op  True if this operation is activating
   * @param parameter_size Size of parameters
   * @param op_parameter   Operation parameters
   * @param mod_ID         ID of the module
   **/
  ldp_status_t ldp_fifo_manager_push(ldp_fifo_manager* fifo_manager,
                                         int op_index,
                                         uint32_t op_ID,
                                         ldp_op_type op_type,
                                         bool activating_op,
                                         uint32_t parameter_size,
                                         char* op_parameter,
                                         ECOA__uint16 mod_ID);
  /**
   * @brief  Push an operation in fifo in fisrt place (used for response of synchronous RR)
   *
   * @param op_index   index of operation. Correspond to the index of pool
   * @param op_ID      module ID of operation
   * @param op_type    type of operation (RR, event, ...)
   * @param activating_op  True if this operation is activating
   * @param parameter_size Size of parameters
   * @param op_parameter   Operation parameters
   * @param mod_ID         ID of the module
   **/
  ldp_status_t ldp_fifo_manager_push_first(ldp_fifo_manager* fifo_manager,
                                               int op_index,
                                               uint32_t op_ID,
                                               ldp_op_type op_type,
                                               bool activating_op,
                                               uint32_t parameter_size,
                                               char* op_parameter,
                                               ECOA__uint16 mod_ID);

  /**
   * @brief  Pop the first element of FIFO.
   *         if FIFO is empty, thread stops on a pthread_condition
   *
   * @param fifo_manager  Fifo manage which contains the FIFO
   * @param elt           pointer to the element which will be popped
   *
   * @return
   */
  ldp_status_t ldp_fifo_manager_pop_elt(ldp_fifo_manager* fifo_manager,
                                            ldp_element** elt);

  /**
   * @brief  After a pop operation, this function releases the element by
   *         repushing it in the right pool.
   *
   * @param  fifo_manager  fifo manager which contains pools
   * @param  elt           element to release
   *
   * @return
   **/
  ldp_status_t ldp_fifo_manager_release_elt(ldp_fifo_manager* fifo_manager,
                                                ldp_element* elt);

  /**
   * @brief  Clean FIFO regarding module state.
   *         Clean also req_resp structure if FIFO contains RR answer
   *
   * @param  fifo_manager  fifo manager to clean
   * @param  mod_state     state of the module
   * @param  req_resp      req_resp to clean. could be NULL if any RR is handle by the module
   */
  void ldp_fifo_manager_clean(ldp_fifo_manager* fifo_manager,
                                ldp_module_state mod_state,
                                ldp_request_response* req_resp);

#endif /* _LDP_FIFO_MANAGER_H */

#ifdef __cplusplus
}
#endif
