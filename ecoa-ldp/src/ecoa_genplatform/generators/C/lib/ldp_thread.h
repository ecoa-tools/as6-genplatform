/**
* @file ldp_thread.h
* @brief ECOA ldp thread functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_THREAD_H
#define _LDP_THREAD_H

#include <apr.h>
#include <apr_thread_proc.h>
#include "ldp_status_error.h"
#include "ldp_fine_grain_deployment.h"

/**
 * @brief      Wrap apr_thread_create to add support of RT scheduling and priority setting
 *
 * @param      new_element  The newly created thread handle.
 * @param      attr         The threadattr to use to determine how to create the thread.
 * @param[in]  func         The function to start the new thread in.
 * @param      data         Any data to be passed to the starting function.
 * @param      properties   The deployment properties of the thread.
 * @param      pool         The pool to use.
 *
 * @return     ldp status
 */
ldp_status_t ldp_thread_create(apr_thread_t **new_element,
                                apr_threadattr_t *attr,
                                apr_thread_start_t func,
                                void *data,
                                ldp_thread_properties* properties,
                                apr_pool_t *pool);


#endif /* _LDP_THREAD_H */

#ifdef __cplusplus
}
#endif
