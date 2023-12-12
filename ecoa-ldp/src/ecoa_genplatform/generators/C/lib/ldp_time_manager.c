/**
* @file ldp_time_manager.c
* @brief ECOA time functions
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


int ldp_time_cmp(const ldp__timestamp* ts1, const ldp__timestamp* ts2 ){
	if (ts1->seconds > ts2->seconds){
		return 1;
	}else if (ts1->seconds == ts2->seconds && ts1->nanoseconds >= ts2->nanoseconds){
		return 1;
    }
	return 0;
}


void ldp_subs_time(ldp__timestamp* ts1, const ldp__timestamp* ts2  ){
	ts1->seconds -= ts2->seconds;
	uint32_t buf = ts1->nanoseconds - ts2->nanoseconds;
	if(ts1->nanoseconds < ts2->nanoseconds){
		ts1->nanoseconds = 1000000000 + buf;
		ts1->seconds -=1;
	}else{
		ts1->nanoseconds = buf;
	}
}

void ldp_add_time(ldp__timestamp* ts1,const ldp__timestamp* ts2  ){
	ts1->seconds += ts2->seconds;

	long long int buf = ts1->nanoseconds + ts2->nanoseconds;

	if(buf >= 1000000000){
		ts1->nanoseconds = buf -1000000000;
		ts1->seconds +=1;
	}else{
		ts1->nanoseconds = buf;
	}
}

