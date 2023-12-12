/**
* @file ldp_mod_lifecycle.h
* @brief ECOA lifecycle functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#ifdef __cplusplus
extern "C" {
#endif

#ifndef _LDP_MOD_LIFECYCLE_H
#define _LDP_MOD_LIFECYCLE_H

void ldp_mod_lifecycle_initialize(ldp_module_context* mod_ctx);
void ldp_mod_lifecycle_start(ldp_module_context* mod_mod_ctx);
void ldp_mod_lifecycle_stop(ldp_module_context* mod_mod_ctx);
void ldp_mod_lifecycle_shutdown(ldp_module_context* mod_mod_ctx, apr_thread_t* RR_dyn_trigger_thread);
void ldp_mod_lifecycle_kill(ldp_module_context* mod_mod_ctx, apr_thread_t* RR_dyn_trigger_thread);

#endif/* _LDP_MOD_LIFECYCLE_H */
#ifdef __cplusplus
}
#endif
