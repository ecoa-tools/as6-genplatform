/**
* @file ldp_log_platform.c
* @brief ECOA platform logger
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_log_platform.h"
#include "ldp_time_manager.h"
#include "ldp_log.h"

#include <stdarg.h>
#include <stdio.h>

int ldp_log_PF_initialize(ldp_logger_platform* logger,char * name){
	return ldp_log_initialize((ldp_logger*) logger,name);
}

void ldp_log_PF_deinitialize(ldp_logger_platform* logger){
	ldp_log_deinitialize((ldp_logger*)logger);
}

int ldp_log_PF_log(ldp_log_PF_priority_level level, const char* level_str, ldp_logger_platform* logger,const char* msg){
	if(logger == NULL){
		printf("%s\n",msg);
		return -1;
	}
    ldp__timestamp utc_time;
    ldp_get_ecoa_utc_time(&utc_time);

	return ldp_log_log((ldp_log_priority_level) level,level_str, (ldp_logger*) logger,msg, &utc_time);
}
