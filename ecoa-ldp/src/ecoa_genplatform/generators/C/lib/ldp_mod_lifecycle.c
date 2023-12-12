/**
* @file ldp_mod_lifecycle.c
* @brief ECOA lifecycle functions
*
* Copyright (c) 2023 Dassault Aviation
*
* SPDX-License-Identifier: MIT
*
*/

#include "ldp_mod_container_util.h"
#include "ldp_log_platform.h"
#include "ldp_fifo_manager.h"
#include "ldp_request_response.h"
#include "ldp_mod_lifecycle.h"


void ldp_mod_lifecycle_initialize(ldp_module_context* mod_ctx){
    mod_ctx->state = READY;
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", mod_ctx->logger_PF,"[%s]: INIT", mod_ctx->name);
    ldp_mod_init_notify(mod_ctx);
}

void ldp_mod_lifecycle_start(ldp_module_context* mod_ctx){
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", mod_ctx->logger_PF,"[%s]: START", mod_ctx->name);
    mod_ctx->state = RUNNING;
}

void ldp_mod_lifecycle_stop(ldp_module_context* mod_ctx){
    mod_ctx->state = READY;
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", mod_ctx->logger_PF,"[%s]: STOP", mod_ctx->name);

    ldp_fifo_manager_clean(mod_ctx->fifo_manager,
                             mod_ctx->state,
                             &mod_ctx->req_resp);
}

void ldp_mod_lifecycle_shutdown(ldp_module_context* mod_ctx, apr_thread_t* RR_dyn_trigger_thread){
    UNUSED(RR_dyn_trigger_thread);
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", mod_ctx->logger_PF,"[%s]: SHUTDOWN", mod_ctx->name);
    mod_ctx->state = IDLE;

    // clean RR
    ldp_request_response_clean(&mod_ctx->req_resp);

    // clean VD
    // release_all_handle(mod_ctx->VD_manager);

    // clean FIFO sauf INITIALIZE et KILL
    ldp_fifo_manager_clean(mod_ctx->fifo_manager,
                             mod_ctx->state, NULL);
}

void ldp_mod_lifecycle_kill(ldp_module_context* mod_ctx, apr_thread_t* RR_dyn_trigger_thread){
    ldp_log_PF_log_var(ECOA_LOG_INFO_PF,"INFO", mod_ctx->logger_PF,"[%s]: KILL", mod_ctx->name);
    mod_ctx->state = IDLE;

    // stop thread RR
    if (RR_dyn_trigger_thread != NULL){
        ldp_mod_stop_RR_trigger(mod_ctx, RR_dyn_trigger_thread);
    }

    // clean RR
    ldp_request_response_clean(&mod_ctx->req_resp);

    // clean VD
    // release_all_handle(mod_ctx->VD_manager);

    // clean FIFO sauf INITIALIZE et KILL
    ldp_fifo_manager_clean(mod_ctx->fifo_manager,
                             mod_ctx->state, NULL);

    // every thing will be destroy when the thread will end
}
