/* Module Test Container Implementation Skeleton for myElder_Main_impl */

/* @file myElder_Main_impl_test_container.c
 * This is the Module Test Container for Module myElder_Main_impl
 * This file is generated by the ECOA tools and shall not be modified
 */

/* Generated by PARSEC */

#include <stdlib.h>

#include "ECOA.h"
#include "myElder_Main_impl_container.h"

#include "ECOA.h"
#include "libmarx.h"

void myElder_Main_impl_container__command__send(myElder_Main_impl__context* context, const libmarx__T_Data* param)
{
  /* @TODO TODO - To be implemented */
}

ECOA__return_status myElder_Main_impl_container__transaction_1__request_sync(myElder_Main_impl__context* context, const libmarx__T_Data* input, libmarx__T_Data* output)
{
  /* @TODO TODO - To be implemented */
  ECOA__return_status return_status = ECOA__return_status_OK;
  return return_status;
}

ECOA__return_status myElder_Main_impl_container__transaction_2__request_sync(myElder_Main_impl__context* context, const libmarx__T_Data* input, libmarx__T_Data* output)
{
  /* @TODO TODO - To be implemented */
  ECOA__return_status return_status = ECOA__return_status_OK;
  return return_status;
}

ECOA__return_status myElder_Main_impl_container__information__get_read_access(myElder_Main_impl__context* context, myElder_Main_impl_container__information_handle* data_handle)
{
  /* @TODO TODO - To be implemented */
  ECOA__return_status return_status = ECOA__return_status_INVALID_HANDLE;
  return return_status;
}

ECOA__return_status myElder_Main_impl_container__information__release_read_access(myElder_Main_impl__context* context, myElder_Main_impl_container__information_handle* data_handle)
{
  /* @TODO TODO - To be implemented */
  ECOA__return_status return_status = ECOA__return_status_INVALID_HANDLE;
  return return_status;
}


/* Properties API */
void myElder_Main_impl__get_ID_value(myElder_Main_impl__context* context, ECOA:uint32* value)
{
  /* @TODO TODO - To be implemented */
}


/* Logging services API call specifications */
void myElder_Main_impl_container__log_trace(myElder_Main_impl__context* context, const ECOA__log log)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__log_debug(myElder_Main_impl__context* context, const ECOA__log log)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__log_info(myElder_Main_impl__context* context, const ECOA__log log)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__log_warning(myElder_Main_impl__context* context, const ECOA__log log)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__raise_error(myElder_Main_impl__context* context, const ECOA__log log)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__raise_fatal_error(myElder_Main_impl__context* context, const ECOA__log log)
{
  /* @TODO TODO - To be implemented */
}


/* Recovery action service API call specification if the module is a Fault Handler */

/* Time Services API call specifications */
void myElder_Main_impl_container__get_relative_local_time(myElder_Main_impl__context* context, ECOA__hr_time *relative_local_time)
{
  /* @TODO TODO - To be implemented */
}

ECOA__return_status myElder_Main_impl_container__get_UTC_time(myElder_Main_impl__context* context, ECOA__global_time *utc_time)
{
  /* @TODO TODO - To be implemented */
  ECOA__return_status return_status = ECOA__return_status_OK;
  return return_status;
}

ECOA__return_status myElder_Main_impl_container__get_absolute_system_time(myElder_Main_impl__context* context, ECOA__global_time *absolute_system_time)
{
  /* @TODO TODO - To be implemented */
  ECOA__return_status return_status = ECOA__return_status_OK;
  return return_status;
}

void myElder_Main_impl_container__get_relative_local_time_resolution(myElder_Main_impl__context* context, ECOA__duration *relative_local_time_resolution)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__get_UTC_time_resolution(myElder_Main_impl__context* context, ECOA__duration *utc_time_resolution)
{
  /* @TODO TODO - To be implemented */
}

void myElder_Main_impl_container__get_absolute_system_time_resolution(myElder_Main_impl__context* context, ECOA__duration *absolute_system_time_resolution)
{
  /* @TODO TODO - To be implemented */
}

