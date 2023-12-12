/**
* @file ldp_log-lttng-tracef.h
* @brief lttng macro definitions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <features.h>
#include <stdarg.h>
#include <sys/types.h>
#include <lttng/tracepoint.h>

#define LDP_LTTNG_LOG_ARGS \
	TP_ARGS(const char *, logname_arg, \
	        const char *, msg_arg)

#define LDP_LTTNG_LOG_FIELDS \
		TP_FIELDS( \
			ctf_string(logname_field, logname_arg) \
			ctf_string(msg_field, msg_arg) \
		) \


TRACEPOINT_EVENT(ldp_lttng_log, ldp_log_fatal,
	LDP_LTTNG_LOG_ARGS,
	LDP_LTTNG_LOG_FIELDS
)
TRACEPOINT_LOGLEVEL(ldp_lttng_log, ldp_log_fatal, TRACE_CRIT)

TRACEPOINT_EVENT(ldp_lttng_log, ldp_log_error,
	LDP_LTTNG_LOG_ARGS,
	LDP_LTTNG_LOG_FIELDS
)
TRACEPOINT_LOGLEVEL(ldp_lttng_log, ldp_log_error, TRACE_ERR)

TRACEPOINT_EVENT(ldp_lttng_log, ldp_log_warn,
	LDP_LTTNG_LOG_ARGS,
	LDP_LTTNG_LOG_FIELDS
)
TRACEPOINT_LOGLEVEL(ldp_lttng_log, ldp_log_warn, TRACE_WARNING)

TRACEPOINT_EVENT(ldp_lttng_log, ldp_log_info,
	LDP_LTTNG_LOG_ARGS,
	LDP_LTTNG_LOG_FIELDS
)
TRACEPOINT_LOGLEVEL(ldp_lttng_log, ldp_log_info, TRACE_INFO)

TRACEPOINT_EVENT(ldp_lttng_log, ldp_log_debug,
	LDP_LTTNG_LOG_ARGS,
	LDP_LTTNG_LOG_FIELDS
)
TRACEPOINT_LOGLEVEL(ldp_lttng_log, ldp_log_debug, TRACE_DEBUG_PROGRAM)

TRACEPOINT_EVENT(ldp_lttng_log, ldp_log_trace,
	LDP_LTTNG_LOG_ARGS,
	LDP_LTTNG_LOG_FIELDS
)
TRACEPOINT_LOGLEVEL(ldp_lttng_log, ldp_log_trace, TRACE_DEBUG)


