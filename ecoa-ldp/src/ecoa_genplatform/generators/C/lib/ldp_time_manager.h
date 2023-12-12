/**
* @file ldp_time_manager.h
* @brief ECOA time functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_TIME_MANAGER_H
#define _LDP_TIME_MANAGER_H

#include <stdlib.h>
#include <stdint.h>

//! time structure
typedef struct {
	uint32_t seconds;     //!< seconds
	uint32_t nanoseconds; //!< nanoseconds
} ldp__timestamp;

/**
 * @brief    file tp structure with current time (used CLOCK_REALTIME)
 */
void ldp_get_time(ldp__timestamp *tp);

/**
 * @return    ts1 + ts2
 */
void ldp_add_time(ldp__timestamp* ts1, const ldp__timestamp* ts2 );

/**
 * @return    ts1 - ts2
 */
void ldp_subs_time(ldp__timestamp* ts1, const ldp__timestamp* ts2 );

/**
 * @brief      Compare 2 timespec
 *
 * @param[in]  ts1   timsetamp 1
 * @param[in]  ts2   timsetamp 2
 *
 * @return     1 if ts1>=ts2 or 0
 */
int ldp_time_cmp(const ldp__timestamp* ts1, const ldp__timestamp* ts2 );


/**
 * @brief      Get UTC time
 *
 * @param[out] utc_time UTC time
 */
void ldp_get_ecoa_utc_time(ldp__timestamp *utc_time);

/**
 * @brief      Get Absolute system time
 *
 * @param[out] absolute_time Absolute system time
 */
void ldp_get_ecoa_absolute_time(ldp__timestamp *absolute_time);

/**
 * @brief      Get relative local time
 *
 * @param[in]  time_reference  The time reference
 * @param[out] relative_time Relative local time (high res)
 */
void ldp_get_ecoa_relative_time(const ldp__timestamp* time_reference, ldp__timestamp *relative_time);


/**
 * @brief      Get resolution of UTC clock
 *
 * @param[out] utc_timeres resolution
 */
void ldp_get_ecoa_utc_timeres(ldp__timestamp *utc_timeres);

/**
 * @brief      Get resolution of Absolute system clock
 *
 * @param[out] absolute_timeres resolution
 */
void ldp_get_ecoa_absolute_timeres(ldp__timestamp *absolute_timeres);

/**
 * @brief      Get resolution of the relative local clock
 *
 * @param[out] relative_timeres resolution
 */
void ldp_get_ecoa_relative_timeres(ldp__timestamp *relative_timeres);


#endif /* _LDP_TIME_MANAGER_H */

#ifdef __cplusplus
}
#endif
