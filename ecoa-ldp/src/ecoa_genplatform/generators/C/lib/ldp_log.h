/**
* @file ldp_log.h
* @brief Implementation of a logger for ECOA Module
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_LOG_H
#define _LDP_LOG_H

#include "ldp_time_manager.h"

//! structure of logger
typedef struct ldp_logger
{
	void* initializer; //!< used only by componenent
	char* config_filename; //!< used only by componenent

	char* name; //!< logger name
	char* component_inst; //!< name of the component instance
	char* module_inst; //!< name of the deployed module instance
	unsigned int level_mask; //!< module specific
}ldp_logger;

//! log level structure
typedef enum{
	ECOA_LOG_FATAL = 1,
	ECOA_LOG_ERROR = 2,
	ECOA_LOG_WARN = 4,
	ECOA_LOG_INFO = 8,
	ECOA_LOG_DEBUG = 16,
	ECOA_LOG_TRACE = 32
}ldp_log_priority_level;


/**
 * @brief      Initialize logger librairy
 *
 * @param      logger  The logger structure
 *
 * @return     error number
 */
int ldp_log_init(ldp_logger* logger);

/**
 * @brief      Initialize logger structure
 *
 * @param      logger  The logger structure
 * @param      name    The name of logger
 *
 * @return     error number
 */
int ldp_log_initialize(ldp_logger* logger,char * name);

/**
 * @brief      shutdown a logger
 *
 * @param      logger  The logger
 */
void ldp_log_deinitialize(ldp_logger* logger);

/**
 * @brief      log a message
 *
 * @param[in]  level      The level
 * @param      level_str  The level string
 * @param      logger     The logger
 * @param[in]  msg        The message
 * @param      tp         timestamp of the message
 *
 * @return     error number
 */
int ldp_log_log(ldp_log_priority_level level,const char* level_str, ldp_logger* logger,const char* msg, ldp__timestamp* tp);



/**
 * @brief      shutdown log4cplus threads
 */
void ldp_log_shutdown(void);


#endif /* _LDP_LOG_H */
#ifdef __cplusplus
}
#endif
