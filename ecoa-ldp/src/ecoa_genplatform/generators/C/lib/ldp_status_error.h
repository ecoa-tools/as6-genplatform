/**
* @file ldp_status_error.h
* @brief ECOA ldp error types
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_STATUS_ERROR_H
#define _LDP_STATUS_ERROR_H
#include "apr_errno.h"
#define UNUSED(x) (void)(x)

typedef apr_status_t ldp_status_t;
#define LDP_SUCCESS APR_SUCCESS
#define LDP_ERROR APR_EGENERAL

#endif /* _LDP_STATUS_ERROR_H */
#ifdef __cplusplus
}
#endif
