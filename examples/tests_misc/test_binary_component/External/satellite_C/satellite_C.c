/* Generated by PARSEC */
/* Module Implementation satellite_C */

#include "ECOA.h"
#include "satellite_C.h"

#include "ECOA.h"
#include "myLib.h"
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>

static void print_log(satellite_C__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  satellite_C_container__log_trace(context, log);
}

/* Entry points for lifecycle operations */
void satellite_C__INITIALIZE__received(satellite_C__context* context)
{
  /* @TODO TODO - To be implemented */
}

void satellite_C__START__received(satellite_C__context* context)
{
    ECOA__uint32 sat_num;
    satellite_C_container__get_satellite_num_value(context, &sat_num);

    context->user.position.x=sat_num;
    context->user.position.y=1;
    context->user.position.z=2;

    for(int i=0; i<myLib__array_data_MAXSIZE; i++){
        context->user.data[i] = sat_num+i;
    }

    print_log(context, "user ctx : %i", sizeof(context->user));

}

void satellite_C__STOP__received(satellite_C__context* context)
{
  /* @TODO TODO - To be implemented */
}

void satellite_C__SHUTDOWN__received(satellite_C__context* context)
{
  /* @TODO TODO - To be implemented */
}

void satellite_C__satellite_position__request_received(satellite_C__context* context, const ECOA__uint32 ID)
{
    ECOA__uint32 sat_num;
    satellite_C_container__get_satellite_num_value(context, &sat_num);

    print_log(context, "satellite %i received a position request", sat_num);

    assert(satellite_C_container__satellite_position__response_send(context,
                                                                    ID,
                                                                    &context->user.position,
                                                                    sat_num) == ECOA__return_status_OK);

    satellite_C_container__send_data__send(context, &context->user.data, sat_num);
}