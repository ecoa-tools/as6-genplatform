/* @file satellite_C_container.h
 * This is the Module Container header for Module satellite_C
 * This file is generated by the ECOA tools and shall not be modified
 */

/* Generated by PARSEC */

#if !defined(_SATELLITE_C_CONTAINER_H)
#define _SATELLITE_C_CONTAINER_H

#if defined(__cplusplus)
extern "C" {
#endif

#include "ECOA.h"
#include "ECOA.h"
#include "myLib.h"
#include "satellite_C_user_context.h"

#define ECOA_VERSIONED_DATA_HANDLE_PRIVATE_SIZE 32

/* Incomplete definition of the technical (platform-dependent) part of the context
 * (it will be defined privately by the container)
 */
struct satellite_C__platform_hook;


/* Module Context structure declaration */
typedef struct
{
  /*
   * Other container technical data will accessible through the pointer defined here
   */
  struct satellite_C__platform_hook *platform_hook;

  /* the type satellite_C_user_context shall be defined by the user
   * in the satellite_C_user_context.h file to carry the module
   * implementation private data
   */
  satellite_C_user_context user;

  /*
   * When the optional warm start context is used, the type
   * satellite_C_warm_start_context shall be defined by the
   * user in the satellite_C_user_context.h file to carry the module
   * implementation warm start private data and the attribute
   * satellite_C_warm_start_context user shall be declared as follows:
   */
  // satellite_C_warm_start_context warm_start;
} satellite_C__context;

void satellite_C_container__send_data__send(satellite_C__context* context, const myLib__array_data* data, const ECOA__uint32 satellite_num);

ECOA__return_status satellite_C_container__satellite_position__response_send(satellite_C__context* context, const ECOA__uint32 ID, const myLib__position* data, const ECOA__uint32 satellite_num);

/* Properties API */
void satellite_C_container__get_satellite_num_value(satellite_C__context* context, ECOA__uint32* value);

/* PINFO API */

/* Logging services API call specifications */
void satellite_C_container__log_trace(satellite_C__context* context, const ECOA__log log);
void satellite_C_container__log_debug(satellite_C__context* context, const ECOA__log log);
void satellite_C_container__log_info(satellite_C__context* context, const ECOA__log log);
void satellite_C_container__log_warning(satellite_C__context* context, const ECOA__log log);
void satellite_C_container__raise_error(satellite_C__context* context, const ECOA__log log);
void satellite_C_container__raise_fatal_error(satellite_C__context* context, const ECOA__log log);

/* Recovery action service API call specification if the module is a Fault Handler */

/* Time Services API call specifications */
void satellite_C_container__get_relative_local_time(satellite_C__context* context, ECOA__hr_time *relative_local_time);
ECOA__return_status satellite_C_container__get_UTC_time(satellite_C__context* context, ECOA__global_time *utc_time);
ECOA__return_status satellite_C_container__get_absolute_system_time(satellite_C__context* context, ECOA__global_time *absolute_system_time);
void satellite_C_container__get_relative_local_time_resolution(satellite_C__context* context, ECOA__duration *relative_local_time_resolution);
void satellite_C_container__get_UTC_time_resolution(satellite_C__context* context, ECOA__duration *utc_time_resolution);
void satellite_C_container__get_absolute_system_time_resolution(satellite_C__context* context, ECOA__duration *absolute_system_time_resolution);

#if defined(__cplusplus)
}
#endif

#endif  /* _SATELLITE_C_CONTAINER_H */
