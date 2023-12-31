/* Module Helpers Implementation for myCadet_Main_impl */

/* @file myCadet_Main_impl_helpers.c
 * This is the Module Test Container for Module myCadet_Main_impl
 * This file is generated by the ECOA tools and shall not be modified
 */

/* Generated by PARSEC */

#include <stdio.h>
#include <string.h>
#include <stdarg.h>

#include "ECOA.h"
#include "myCadet_Main_impl_container.h"
#include "myCadet_Main_impl_helpers.h"

#include "ECOA.h"
#include "libmarx.h"


const char* MYCADET_MAIN_IMPL = "MYCADET_MAIN_IMPL: ";

void myCadet_Main_impl_log_info(myCadet_Main_impl__context* context, char *msg, ...) {
    ECOA__log log;
    strncpy(log.data, MYCADET_MAIN_IMPL, ECOA__LOG_MAXSIZE);
    va_list argp;
    va_start(argp, msg);
    vsnprintf((char *) log.data + strnlen(MYCADET_MAIN_IMPL, ECOA__LOG_MAXSIZE),
    ECOA__LOG_MAXSIZE, msg, argp);
    va_end(argp);
    log.current_size = strnlen((char *) &log.data, ECOA__LOG_MAXSIZE);
    myCadet_Main_impl_container__log_info(context, log);
}

void myCadet_Main_impl_log(myCadet_Main_impl__context* context, char *msg, ...) {
    ECOA__log log;
    strncpy(log.data, MYCADET_MAIN_IMPL, ECOA__LOG_MAXSIZE);
    va_list argp;
    va_start(argp, msg);
    vsnprintf((char *) log.data + strnlen(MYCADET_MAIN_IMPL, ECOA__LOG_MAXSIZE),
    ECOA__LOG_MAXSIZE, msg, argp);
    va_end(argp);
    log.current_size = strnlen((char *) &log.data, ECOA__LOG_MAXSIZE);
    myCadet_Main_impl_container__log_debug(context, log);
}



void myCadet_Main_impl__set_older_information(myCadet_Main_impl__context *context,
        libmarx__T_Data* data) {
    myCadet_Main_impl_container__older_information_handle handle;

    ECOA__return_status return_status;

    return_status =
            myCadet_Main_impl_container__older_information__get_write_access(
                    context, &handle);

    if (return_status == ECOA__return_status_OK
            || return_status == ECOA__return_status_DATA_NOT_INITIALIZED) {

        *(handle.data) = *data;

        return_status =
                myCadet_Main_impl_container__older_information__publish_write_access(
                        context, &handle);

        if (return_status != ECOA__return_status_OK) {
            myCadet_Main_impl_log(context,
                    "older_information: publish_write_access FAILED / error = %d", return_status);
        }
    } else {
        myCadet_Main_impl_log(context,
                "older_information: get_write_access FAILED / error = %d", return_status);
    }
}



void myCadet_Main_impl__get_younger_information(myCadet_Main_impl__context* context,
        libmarx__T_Data* data) {
    /* assert: data != NULL */

    myCadet_Main_impl_container__younger_information_handle handle;
    ECOA__return_status return_status = !ECOA__return_status_OK;

    return_status = myCadet_Main_impl_container__younger_information__get_read_access(context,
            &handle);
    if (return_status == ECOA__return_status_OK) {

        *data = *(handle.data);

        return_status = myCadet_Main_impl_container__younger_information__release_read_access(context,
                &handle);
        if (return_status != ECOA__return_status_OK) {
            myCadet_Main_impl_log(context, "younger_information: Fail on release_read_access / error = %d",
                    return_status);
        }
    } else {
        if (return_status != ECOA__return_status_NO_DATA) {
            myCadet_Main_impl_log(context, "younger_information: Fail on get_read_access / error = %d",
                    return_status);
        }
    }
}



