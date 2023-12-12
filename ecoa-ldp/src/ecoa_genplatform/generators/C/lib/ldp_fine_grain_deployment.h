/**
* @file ldp_fine_grain_deployment.h
* @brief Contains portable header function to set deployment properties
* @note  Currently only linux OS are supported
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_FINE_GRAIN_DEPLOYMENT_H
#define _LDP_FINE_GRAIN_DEPLOYMENT_H


#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "ldp_status_error.h"
#include "ldp_log_platform.h"

#if defined(__linux__)

#include <stdio.h>
#include <sched.h>

#define LDP_SCHED_OTHER SCHED_OTHER
#define LDP_SCHED_IDLE SCHED_IDLE
#define LDP_SCHED_BATCH SCHED_BATCH
#define LDP_SCHED_FIFO SCHED_FIFO
#define LDP_SCHED_RR SCHED_RR
//#define LDP_SCHED_DEADLINE SCHED_DEADLINE

typedef cpu_set_t cpu_mask; //!< redefinition of a CPU mask

#else
#error Only linux platform is supported
#endif

//! strcuture to describe deployment properties of a thread
typedef struct ldp_thread_properties{
	int priority; //!< ECOA property. WIll be translate in linux priority or niceness
	int policy; //!< scheduler policy
	cpu_mask cpu_affinity_mask; //!< CPU mask
	ldp_logger_platform* logger; //!< logger to save error message during thread creation
	const char* thread_name; //!< thread name. Will be restrict to 15 bytes due to pthread library
}ldp_thread_properties;

/**
 * @brief      create a cpu_mask to defined cpu affinity of a thread
 *
 * @param[in]  nb_cpu   The number of cpu
 * @param      cpu_ids  The cpu identifiers on which the thread could run
 *
 * @return     create CPU mask
 */
cpu_mask ldp_create_cpu_mask(int nb_cpu, int* cpu_ids);

/**
 * @brief      Create a CPU with all CPUs activated
 *
 * @return     create CPU mask
 */
cpu_mask ldp_create_cpu_mask_full(void);

/**
 * @brief      set CPU affinity of the main thread of a processus
 *
 * @param[in]  mask  The CPU mask
 *
 * @return     ldp status
 */
ldp_status_t ldp_set_proc_affinty(cpu_set_t mask);

/**
 * @brief      Print current thread deployment properties
 *
 * @param      logger  The logger
 */
void log_thread_deployment_properties(ldp_logger_platform* logger);

#endif /* _LDP_FINE_GRAIN_DEPLOYMENT_H */

#ifdef __cplusplus
}
#endif
