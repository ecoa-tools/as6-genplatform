/**
* @file ldp_time_manager.c
* @brief ECOA time manager functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <time.h>
#include "ldp_time_manager.h"
#include <stdint.h>
#include <stdio.h>


void ldp_get_time(ldp__timestamp *tp){
#if _POSIX_C_SOURCE >= 199309L
	struct timespec tp2;
    clock_gettime(CLOCK_MONOTONIC,&tp2);
    tp->seconds = (uint32_t) tp2.tv_sec;
    tp->nanoseconds = (uint32_t) tp2.tv_nsec;
#else
#	error  "time manager is not available"
#endif
}

void ldp_get_ecoa_utc_time(ldp__timestamp *utc_time){
#if _POSIX_C_SOURCE >= 199309L
	struct timespec tp;
    clock_gettime(CLOCK_REALTIME,&tp);
    utc_time->seconds = (uint32_t) tp.tv_sec;
    utc_time->nanoseconds = (uint32_t) tp.tv_nsec;
#else
#	error  "time manager is not available"
#endif
}

void ldp_get_ecoa_absolute_time(ldp__timestamp *absolute_time){
#if _POSIX_C_SOURCE >= 199309L
	struct timespec tp;
    clock_gettime(CLOCK_REALTIME,&tp);
    absolute_time->seconds = (uint32_t) tp.tv_sec;
    absolute_time->nanoseconds = (uint32_t) tp.tv_nsec;
#else
#	error  "time manager is not available"
#endif
}


void ldp_get_ecoa_relative_time(const ldp__timestamp* time_reference, ldp__timestamp *relative_time){
	ldp_get_time(relative_time);
	if(NULL!= time_reference) {
		ldp_subs_time(relative_time, time_reference);
	}
}


void ldp_get_ecoa_utc_timeres(ldp__timestamp *utc_timeres){
#if _POSIX_C_SOURCE >= 199309L
	struct timespec res;
	clock_getres(CLOCK_REALTIME, &res);
	utc_timeres->seconds = (uint32_t) res.tv_sec;
	utc_timeres->nanoseconds = (uint32_t) res.tv_nsec;
#else
#	error  "time manager is not available"
#endif
}

void ldp_get_ecoa_absolute_timeres(ldp__timestamp *absolute_timeres){
#if _POSIX_C_SOURCE >= 199309L
	struct timespec res;
	clock_getres(CLOCK_REALTIME, &res);
	absolute_timeres->seconds = (uint32_t) res.tv_sec;
	absolute_timeres->nanoseconds = (uint32_t) res.tv_nsec;
#else
#	error  "time manager is not available"
#endif
}

void ldp_get_ecoa_relative_timeres(ldp__timestamp *relative_timeres){
#if _POSIX_C_SOURCE >= 199309L
	struct timespec res;
	clock_getres(CLOCK_MONOTONIC, &res);
	relative_timeres->seconds = (uint32_t) res.tv_sec;
	relative_timeres->nanoseconds = (uint32_t) res.tv_nsec;
#else
#	error  "time manager is not available"
#endif
}

