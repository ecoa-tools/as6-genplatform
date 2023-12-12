/**
* @file ldp_log-console.c
* @brief ECOA console logger
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_log.h"
#include <ECOA.h>
#include "ldp_time_manager.h"
#include "ldp_status_error.h"
#include <stdio.h>

int ldp_log_init(ldp_logger* logger) {
    UNUSED(logger);
    // nothing
    return 0;
}

int ldp_log_initialize(ldp_logger* logger,char * name){
    UNUSED(logger);
    UNUSED(name);
    // nothing
	return 0;
}


void ldp_log_deinitialize(ldp_logger* logger){
    UNUSED(logger);
	// nothing
}

void ldp_log_shutdown(void){
	//	nothing;
}


int ldp_log_log(ldp_log_priority_level level, const char* level_str, 
                  ldp_logger* logger,const char* msg, ldp__timestamp* tp){
	if(level & logger->level_mask){
		printf("\"%u,%09u\":1:\"%s\":\"%s\":\"%s\":\"%s\"\n",
									tp->seconds,
									tp->nanoseconds,
									level_str,
									logger->component_inst,
									logger->module_inst,
									msg);
	}
	return 0;
}

