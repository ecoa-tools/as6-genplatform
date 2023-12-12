/**
* @file ldp_launcher.h
* @brief ECOA launcher
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_LAUNCHER_H
#define _LDP_LAUNCHER_H

#include <apr.h>
#include <apr_thread_cond.h>
#include <apr_poll.h>
#include <apr_errno.h>

#include "ldp_thread.h"

typedef struct launching_thread_params_t launching_thread_params;

/**
 * @brief      Creates launcher attribute and create the thread
 *
 * @param      mem_pool  The memory pool
 * @param      params    The parameters that contains among other the script file
 */
void ldp_create_launching_thread(apr_pool_t* mem_pool, launching_thread_params* params);

/**
 * @brief      Parses the file launcher.txt and realises requested operations.
 *
 *
 * @param   t      apr_thread_t*
 * @param   args   pointer to struct of type "launching_thread_params" (needed information)

 * @return  Nothing
 */
void * launch_func(apr_thread_t* t, void* args);

#endif /* _LDP_LAUNCHER_H */
#ifdef __cplusplus
}
#endif
