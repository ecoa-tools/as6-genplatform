/**
* @file ldp_log_platform.h
* @brief ECOA platform logger
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef _LDP_LOG_PLATFORM_H
#define _LDP_LOG_PLATFORM_H

#ifdef __cplusplus
extern "C" {
#endif

#include "ldp_time_manager.h"
#include "ldp_log.h"


/**
 * ecoa logger platform
 */
typedef struct ldp_logger_platform
{
	void* initializer; //!< used only by componenent
	char* config_filename; //!< used only by componenent

	char* name; //!< logger name
    char* pd_name; //!< protection domain name
    char* node_name; //!< node name
	unsigned int level_mask; //!< module specific
}ldp_logger_platform;


/**
 * log level for platform logger
 */
typedef enum{
	ECOA_LOG_FATAL_PF = ECOA_LOG_FATAL, // 1
	ECOA_LOG_ERROR_PF = ECOA_LOG_ERROR, // 2
	ECOA_LOG_WARN_PF = ECOA_LOG_WARN, // 4
	ECOA_LOG_INFO_PF = ECOA_LOG_INFO, // 8
	ECOA_LOG_DEBUG_PF = ECOA_LOG_DEBUG, // 16
	ECOA_LOG_TRACE_PF = ECOA_LOG_TRACE // 32
}ldp_log_PF_priority_level;


/**
 * @brief      { initialize ldp_logger_platform structure }
 *
 * @param      logger  The logger to initialize
 * @param      name    name of the config filename for this logger
 *
 * @return     { description_of_the_return_value }
 */
int ldp_log_PF_initialize(ldp_logger_platform* logger,char * name);

/**
 * @brief      deinitialize logger
 *
 * @param      logger  The logger
 */
void ldp_log_PF_deinitialize(ldp_logger_platform* logger);

/**
 * @brief      { log a platform message }
 *
 * @param[in]  level      message level
 * @param      level_str  string level message
 * @param      logger     logger structure that will log message
 * @param[in]  msg        message to log
 *
 * @return     { return 0 }
 */
int ldp_log_PF_log(ldp_log_PF_priority_level level, const char* level_str, ldp_logger_platform* logger,const char* msg);

/**
 * @brief      Log platform message (variadic version)
 *
 * @param[in]  level      The level
 * @param      level_str  The level string
 * @param      logger     The logger
 * @param[in]  format     The format
 * @param      args       variadic arguments
 *
 */
#define ldp_log_PF_log_var(level, level_str, logger, format, args...)\
{char F00_err_msg[1024];\
int ret=0;\
ret = snprintf(F00_err_msg, 1024, format, ##args);\
if (ret < 0) {\
    abort();\
}\
ldp_log_PF_log(level,level_str, logger, F00_err_msg);}

#define ldp_warning_status_log(logger, status, msg_format, args...)\
{char F00_err_msg[1024];\
int ret = 0;\
ret = snprintf(F00_err_msg, 950, msg_format , ##args);\
if (ret < 0) {\
    abort();\
}\
apr_strerror(status, F00_err_msg+strlen(F00_err_msg), 74);\
ldp_log_PF_log(ECOA_LOG_WARN_PF, "WARNING", logger, F00_err_msg);}

#define ldp_error_status_log(logger, status, msg_format, args...)\
{char F00_err_msg[1024];\
int ret = 0;\
ret = snprintf(F00_err_msg, 950, msg_format , ##args);\
if (ret < 0) {\
    abort();\
}\
apr_strerror(status, F00_err_msg+strlen(F00_err_msg), 74);\
ldp_log_PF_log(ECOA_LOG_ERROR_PF, "ERROR", logger, F00_err_msg);}
#ifdef __cplusplus
}
#endif

#endif /* _LDP_LOG_PLATFORM_H */
