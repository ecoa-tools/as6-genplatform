/**
* @file ldp_fifo_elt_pool.h
* @brief ECOA fifo pool functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_FIFO_ELT_POOL_H
#define _LDP_FIFO_ELT_POOL_H

#include "ECOA.h"
#include <stdint.h>
#include <stdbool.h>
#include "ldp_status_error.h"
#include "apr_thread_mutex.h"

  //! state of a pool element
  typedef enum{
               LDP_ELT_FREE,
               LDP_ELT_USED
  }ldp_element_state;

  //! operation type of an element
  typedef enum{
               EVENT,
               VERSIONED_DATA,
               RR_ANSWER,
               RR_RECEIVED
  }ldp_op_type;

  //! Incomplete declaration of pool of elements
  typedef struct ldp_element_pool ldp_element_pool;

  //! element of a pool
  typedef struct{
    ldp_element_state state; //!< useless if elements are in list (used/available list)
    ldp_op_type op_type;     //!< type of operation
    bool activating_op;        //!< true if operation is activating

    ldp_element_pool* pool; //!< [static] pool of the element
                              //    (to release it in the right pool)

    uint32_t op_ID;     //!< ID of the modle operation
    int parameter_size; //!< Useful size of parameters
                        //   (not the size of memory area)
    char* parameters;   //!< array of byte which contains oepration parameters
    
    ECOA__uint16 mod_ID;    //!< ID of the module
  }ldp_element;

  //! pool of elements
  struct ldp_element_pool{
    uint16_t op_id; // [static] Useless? Operation ID of this pool
    uint32_t element_num;    //!< [static] number of element in pool
    uint32_t parameter_size; //!< [static] maximum size of parameters which
                             //   element can handle

    apr_thread_mutex_t* mutex;    //!< mutex to protect write operation
    uint32_t element_available;   //!< available element number in pool
    ldp_element* element_array; //!< TODO: used list instead of array
  };


  /**
   * @brief Create pool of elements: init mutex, create eand init elements array (calloc)
   *
   * @param element_pool  pool to create
   * @param mp            APR memory pool (for mutex init)
   **/
  ldp_status_t ldp_element_pool_create(ldp_element_pool* element_pool,
                                           apr_pool_t* mp);

  /**
   * @brief destroy a pool : clean memory of element array, and destroy mutex
   *
   * @param  pool to destroy
   **/
  ldp_status_t ldp_element_pool_destroy(ldp_element_pool* element_pool);

  /**
   * @brief Get a free element from the pool (threadsafe)
   *
   * @param element_pool pool of elements
   *
   * @return a free element (now used), or NULL (if no element available)
   **/
  ldp_element* ldp_element_pool_get(ldp_element_pool* element_pool);

  /**
   * @brief release used element
   *
   * @param element to release
   **/
  void ldp_element_pool_release(ldp_element* elt);

#endif /* _LDP_FIFO_ELT_POOL_H */

#ifdef __cplusplus
}
#endif
