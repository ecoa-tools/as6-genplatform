/**
* @file ldp_log-zlog.c
* @brief ECOA zlog logger
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <zlog.h>
#include "ldp_log.h"
#include <ECOA.h>
#include "ldp_time_manager.h"
#include "ldp_status_error.h"

int ldp_log_init(ldp_logger* logger) {
    struct stat st = {0};
    if (stat("logs", &st) == -1) {
        mkdir("logs", 0700);
    }
    return zlog_init(logger->config_filename);
}

int ldp_log_initialize(ldp_logger* logger,char * name){
    logger->name = name;
    logger->initializer = zlog_get_category(logger->name);
    char log_filename[2048];
    snprintf(log_filename, strlen(logger->name)+14, "logs/log_%s.log", logger->name);
    FILE* fd = fopen(log_filename, "w");
    fclose(fd);
	return 0;
}


void ldp_log_deinitialize(ldp_logger* logger){
    UNUSED(logger);
    //	nothing;
}

void ldp_log_shutdown(void){
    zlog_fini();
}


int ldp_log_log(ldp_log_priority_level level, const char* level_str,
                ldp_logger* logger,const char* msg, ldp__timestamp* tp){
    if(level & logger->level_mask){
        char buf[2*ECOA__LOG_MAXSIZE];
        snprintf(buf, sizeof(buf), "\"%u,%09u\":1:\"%s\":\"%s\":\"%s\":\"%s\"",
                 tp->seconds, tp->nanoseconds,level_str, logger->component_inst, logger->module_inst, msg);

        switch(level){
            case ECOA_LOG_FATAL:
                zlog_fatal(logger->initializer, buf);
                break;
            case ECOA_LOG_ERROR:
                zlog_error(logger->initializer, buf);
                break;
            case ECOA_LOG_WARN:
                zlog_warn(logger->initializer, buf);
                break;
            case ECOA_LOG_INFO:
                zlog_info(logger->initializer, buf);
                break;
            case ECOA_LOG_DEBUG:
                zlog_debug(logger->initializer, buf);
                break;
            case ECOA_LOG_TRACE:
            default:
                zlog_notice(logger->initializer, buf);
                break;
        }
    }
    return 0;
}
