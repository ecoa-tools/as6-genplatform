/**
* @file ldp_state.h
* @brief ECOA ldp state definitions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_STATE_H
#define _LDP_STATE_H

//! Module state
typedef enum ldp_module_state_t{
	IDLE,
	READY,
	RUNNING,
} ldp_module_state;

//! Protection domain state
typedef enum {
	PDomain_IDLE,
	PDomain_INIT,
	PDomain_READY,
	PDomain_RUNNING,
} ldp_PD_state ;

#endif /* _LDP_STATE_H */

#ifdef __cplusplus
}
#endif
