/*
* @file ldp_log-lttng.c
* @brief ECOA lttng logger 
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#define TRACEPOINT_PROVIDER ldp_lttng_log
#define TRACEPOINT_DEFINE
#define TRACEPOINT_CREATE_PROBES
#include "ldp_log-lttng-tracef.h"
#define TRACEPOINT_INCLUDE "ldp_log-lttng-tracef.h"
#include <lttng/tracepoint-event.h>

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
	logger->initializer = NULL;
	logger->name = name;
	return 0;
}


void ldp_log_deinitialize(ldp_logger* logger){
	// nothing
}

void ldp_log_shutdown(void){
	//	nothing;
}


int ldp_log_log(ldp_log_priority_level level, const char* level_str, 
                  ldp_logger* logger,const char* msg, ldp__timestamp* tp){
	if(level & logger->level_mask){
		char buf[2*ECOA__LOG_MAXSIZE];
		snprintf(buf, sizeof(buf), "\"%u,%09u\":1:\"%s\":\"%s\":\"%s\":\"%s\"",
				tp->seconds, tp->nanoseconds,level_str, logger->component_inst, logger->module_inst, msg);

		switch(level){
			case ECOA_LOG_FATAL:
				tracepoint(ldp_lttng_log, ldp_log_fatal, logger->name, buf);
				break;
			case ECOA_LOG_ERROR:
				tracepoint(ldp_lttng_log, ldp_log_error, logger->name, buf);
				break;
			case ECOA_LOG_WARN:
				tracepoint(ldp_lttng_log, ldp_log_warn, logger->name, buf);
				break;
			case ECOA_LOG_INFO:
				tracepoint(ldp_lttng_log, ldp_log_info, logger->name, buf);
				break;
			case ECOA_LOG_DEBUG:
				tracepoint(ldp_lttng_log, ldp_log_debug, logger->name, buf);
				break;
			case ECOA_LOG_TRACE:
			default:
				tracepoint(ldp_lttng_log, ldp_log_trace, logger->name, buf);
				break;
		}
	}
	return 0;
}

