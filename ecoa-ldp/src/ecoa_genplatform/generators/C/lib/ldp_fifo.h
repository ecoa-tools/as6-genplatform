/**
* @file ldp_fifo.h
* @brief ECOA fifo functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_FIFO_H
#define _LDP_FIFO_H

#include <apr_thread_mutex.h>
#include <apr_thread_cond.h>
#include <apr.h>
#include "ldp_status_error.h"
#include <stdbool.h>

#include "ldp_fifo_elt_pool.h"


typedef void* node;

//! fifo object
//! fifo elements are ldp_elt_fifo and they are declared and store in an array 'queue' in structure 'ldp_fifo'
typedef struct ldp_fifo{
	apr_pool_t* mp; //!< apr memory pool
	int tail; //!<  index of the last element in the aray
	int head; //!< index the first element in the array
	node* queue; //!< array of used or unused elements
	int current_size; //!< current number of element in fifo
	int size; //!< maximum number of element in fifo
	apr_thread_mutex_t* mutex; //!< mutex
}ldp_fifo;

/**
 * @brief      Initialize a ldp_fifo structure and allocate memory space
 *
 * @param      f   fifo structure
 * @param      mp  APR memory pool
 */
void ldp_init_fifo(ldp_fifo* f, apr_pool_t* mp);

/**
 * @brief      Push a new element in fifo
 *
 * @param      f       fifo structure
 * @param[in]  new_element     new element to push in fifo
 *
 * @return     LDP_ERROR in case of failed (fifo full) or LDP_SUCCESS
 */
ldp_status_t ldp_push_fifo(ldp_fifo* f, node new_element);

/**
 * @brief      push a new element in the head of fifo
 *
 * @param      f       fifo structure
 * @param[in]  new_element     new element to push in fifo
 *
 * @return     LDP_ERROR in case of failed (fifo full) or LDP_SUCCESS
 */
ldp_status_t ldp_push_first_fifo(ldp_fifo* f, node new_element);

/**
 * @brief      take the first element of fifo.
 This function is blocked if they is no element in fifo.
 This function is unblock by an other thread after adding a new element in the fifo
 *
 * @param      f     fifo structure
 * @param      elt   The fifo element that will contains the first element
 *
 * @return     LDP_SUCCESS or never return
 */
ldp_status_t ldp_pop_fifo(ldp_fifo* f, node* elt);

/**
 * @brief      free memory and destroy mutex and condition
 *
 * @param      f     fifo to destroy
 */
void ldp_destroy_fifo(ldp_fifo* f);


#endif /* _LDP_FIFO_H */
#ifdef __cplusplus
}
#endif
