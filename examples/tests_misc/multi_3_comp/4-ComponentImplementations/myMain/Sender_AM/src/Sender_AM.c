/* @file "Sender_AM.c"
 * This is the user code for Module Sender_AM
 */

#include "../inc-gen/Sender_AM.h"
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <stdarg.h>

static void print_log(Sender_AM__context* context, const char *format, ...){
    va_list vl;
    ECOA__log log;

    va_start(vl, format);
    vsnprintf(log.data, ECOA__LOG_MAXSIZE, format, vl);
    va_end( vl);

  Sender_AM_container__log_trace(context, log);
}
/* The following functions must be implemented by this module: */

/* Entrypoints for lifecycle events */
void Sender_AM__INITIALIZE__received(Sender_AM__context* context)
{
   /* One-shot initialisation activities: */
   /* @TODO TODO - To be implemented */

   /* Call REINITIALIZE entry-point: */
}

void Sender_AM__START__received(Sender_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void Sender_AM__STOP__received(Sender_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}

void Sender_AM__SHUTDOWN__received(Sender_AM__context* context)
{
   /* @TODO TODO - To be implemented */
}



/* Entrypoints for module operations */
void
Sender_AM__Run__received (
  Sender_AM__context* context
  ,
  const pingpong__T_Target_Position *position
 )
{
   /* @TODO TODO - To be implemented */
	print_log(context, "RUN");
	assert(position->Is_Valid);
	assert(fabs(position->Location.Longitude-6.022) < 0.0001);
	assert(fabs(position->Location.Latitude-3.1415) < 0.0001);
	Sender_AM_container__Ping__send(context,position->Tactical_Item_ID);
}



