/* Module Helpers Implementation for myElder_Main_impl */

/* @file myElder_Main_impl_helpers.c
 * This is the Module Test Container for Module myElder_Main_impl
 * This file is generated by the ECOA tools and shall not be modified
 */

/* Generated by PARSEC */

#include <stdio.h>
#include <string.h>
#include <stdarg.h>

#include "ECOA.h"
#include "myElder_Main_impl_container.h"
#include "myElder_Main_impl_helpers.h"

#include "ECOA.h"
#include "libmarx.h"


const char* MYELDER_MAIN_IMPL = "MYELDER_MAIN_IMPL: ";

void myElder_Main_impl_log_info(myElder_Main_impl__context* context, char *msg, ...) {
    ECOA__log log;
    strncpy(log.data, MYELDER_MAIN_IMPL, ECOA__LOG_MAXSIZE);
    va_list argp;
    va_start(argp, msg);
    vsnprintf((char *) log.data + strnlen(MYELDER_MAIN_IMPL, ECOA__LOG_MAXSIZE),
    ECOA__LOG_MAXSIZE, msg, argp);
    va_end(argp);
    log.current_size = strnlen((char *) &log.data, ECOA__LOG_MAXSIZE);
    myElder_Main_impl_container__log_info(context, log);
}

void myElder_Main_impl_log(myElder_Main_impl__context* context, char *msg, ...) {
    ECOA__log log;
    strncpy(log.data, MYELDER_MAIN_IMPL, ECOA__LOG_MAXSIZE);
    va_list argp;
    va_start(argp, msg);
    vsnprintf((char *) log.data + strnlen(MYELDER_MAIN_IMPL, ECOA__LOG_MAXSIZE),
    ECOA__LOG_MAXSIZE, msg, argp);
    va_end(argp);
    log.current_size = strnlen((char *) &log.data, ECOA__LOG_MAXSIZE);
    myElder_Main_impl_container__log_debug(context, log);
}



void myElder_Main_impl__request_transaction_1(myElder_Main_impl__context* context
        , libmarx__T_Data* input) {
    /* assert: data != NULL */

    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = myElder_Main_impl_container__transaction_1__request_sync(context
            , input, output);
    if (return_status != ECOA__return_status_OK) {
        myElder_Main_impl_log(context, "transaction_1: Fail on request_sync / error = %d",
                    return_status);
    }
}



void myElder_Main_impl__request_transaction_2(myElder_Main_impl__context* context
        , libmarx__T_Data* input) {
    /* assert: data != NULL */

    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = myElder_Main_impl_container__transaction_2__request_sync(context
            , input, output);
    if (return_status != ECOA__return_status_OK) {
        myElder_Main_impl_log(context, "transaction_2: Fail on request_sync / error = %d",
                    return_status);
    }
}



void myElder_Main_impl__get_information(myElder_Main_impl__context* context,
        libmarx__T_Data* data) {
    /* assert: data != NULL */

    myElder_Main_impl_container__information_handle handle;
    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = myElder_Main_impl_container__information__get_read_access(context,
            &handle);
    if (return_status == ECOA__return_status_OK) {

        *data = *(handle.data);

        return_status = myElder_Main_impl_container__information__release_read_access(context,
                &handle);
        if (return_status != ECOA__return_status_OK) {
            myElder_Main_impl_log(context, "information: Fail on release_read_access / error = %d",
                    return_status);
        }
    } else {
        if (return_status != ECOA__return_status_NO_DATA) {
            myElder_Main_impl_log(context, "information: Fail on get_read_access / error = %d",
                    return_status);
        }
    }
}


