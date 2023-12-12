/**
* @file ldp_log-log4cplus.c
* @brief ECOA log4cplus logger
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <log4cplus/clogger.h>
#include "ldp_log.h"
#include <ECOA.h>
#include "ldp_time_manager.h"
#include "ldp_status_error.h"

int ldp_log_init(ldp_logger* logger) {
    UNUSED(logger);
    // nothing
    return 0;
}

int ldp_log_initialize(ldp_logger* logger,char * name){
	logger->initializer = log4cplus_initialize();
	logger->name = name;
	return log4cplus_file_configure(logger->config_filename);
}


void ldp_log_deinitialize(ldp_logger* logger){
	log4cplus_deinitialize(logger->initializer);
}

void ldp_log_shutdown(void){
	log4cplus_shutdown();
}

static loglevel_t ecoa_log_ll_to_log4c_ll(ldp_log_priority_level level){
	switch(level){
		case ECOA_LOG_FATAL:
			return L4CP_FATAL_LOG_LEVEL;
		case ECOA_LOG_ERROR:
			return L4CP_ERROR_LOG_LEVEL;
		case ECOA_LOG_WARN:
			return L4CP_WARN_LOG_LEVEL;
		case ECOA_LOG_INFO:
			return L4CP_INFO_LOG_LEVEL;
		case ECOA_LOG_DEBUG:
			return L4CP_DEBUG_LOG_LEVEL;
		case ECOA_LOG_TRACE:
			return L4CP_TRACE_LOG_LEVEL;
		default:
			return 0;
	}
}


int ldp_log_log(ldp_log_priority_level level, const char* level_str,
                  ldp_logger* logger,const char* msg, ldp__timestamp* tp){
	if(level & logger->level_mask){
		return log4cplus_logger_log(logger->name, ecoa_log_ll_to_log4c_ll(level) ,
									"\"%u,%09u\":1:\"%s\":\"%s\":\"%s\":\"%s\"",
									tp->seconds,
									tp->nanoseconds,
									level_str,
									logger->component_inst,
									logger->module_inst,
									msg);
	}
	return 0;
}
